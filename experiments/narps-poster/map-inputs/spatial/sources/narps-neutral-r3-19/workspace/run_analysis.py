#!/usr/bin/env python3
"""Group analysis of supplied NARPS equal-indifference gain-effect maps."""
from __future__ import annotations
import hashlib, json, platform, sys, time, os
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
from scipy.stats import t as t_dist, ttest_1samp
from scipy import ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from nilearn import plotting

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'input'
OUT = ROOT / os.environ.get('OUTPUT_DIR', 'results')
FIG = ROOT / os.environ.get('FIGURE_DIR', 'figures')
B = int(os.environ.get('N_PERM', '9999'))
SEED = 20261016
ALPHA = 0.05
ROI_CENTER = np.array([0., 40., -10.])
ROI_RADIUS_MM = 10.


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    started = time.time()
    OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
    sources = json.loads((INPUT / 'sources.json').read_text())
    participant_table = pd.read_csv(INPUT / 'participants.tsv', sep='\t', dtype={'participant_id': str})
    paths = sorted((INPUT / 'data').glob('*_hypo1_cope.nii.gz'))
    ids = [p.name.split('_')[0] for p in paths]
    assert len(paths) == 54 and len(set(ids)) == len(ids)
    assert set(ids) == set(participant_table.participant_id)
    assert set(ids) == {v['participant_id'] for k,v in sources['files'].items() if k.endswith('.nii.gz')}
    participant_table = participant_table.set_index('participant_id').loc[ids].reset_index()
    assert participant_table['group'].eq('equalIndifference').all()

    imgs = []
    qc_rows = []
    ref_shape = ref_affine = None
    for path, sid in zip(paths, ids):
        expected = sources['files'][f'data/{path.name}']
        digest = sha256(path)
        img = nib.load(str(path))
        data = img.get_fdata(dtype=np.float32)
        if ref_shape is None:
            ref_shape, ref_affine = img.shape, img.affine
        same_grid = img.shape == ref_shape and np.allclose(img.affine, ref_affine, atol=1e-5)
        finite = np.isfinite(data)
        nonzero = finite & (data != 0)
        qc_rows.append({'participant_id':sid, 'sha256_expected':expected['sha256'], 'sha256_observed':digest,
                        'checksum_match':digest == expected['sha256'], 'bytes_match':path.stat().st_size == expected['bytes'],
                        'shape':str(img.shape), 'same_grid':same_grid, 'finite_voxels':int(finite.sum()),
                        'nonzero_voxels':int(nonzero.sum()), 'minimum':float(np.nanmin(data)), 'maximum':float(np.nanmax(data)),
                        'mean_nonzero':float(data[nonzero].mean()), 'sd_nonzero':float(data[nonzero].std())})
        assert digest == expected['sha256'] and path.stat().st_size == expected['bytes']
        assert same_grid and finite.all()
        imgs.append(data)
    qc = pd.DataFrame(qc_rows)
    qc.to_csv(OUT/'input_qc.tsv', sep='\t', index=False)
    Xall = np.stack(imgs, axis=0)
    # A common supported analysis mask, derived without looking at effect direction/magnitude.
    mask = np.all(np.isfinite(Xall) & (Xall != 0), axis=0)
    assert mask.any()
    affine = nib.load(str(paths[0])).affine
    ijk = np.array(np.where(mask)).T
    xyz = nib.affines.apply_affine(affine, ijk)
    roi_mask = mask & (np.linalg.norm(nib.affines.apply_affine(affine, np.indices(mask.shape).reshape(3,-1).T).reshape(*mask.shape,3) - ROI_CENTER, axis=-1) <= ROI_RADIUS_MM)
    # Group voxel arrays; rows are independent participants.
    X = Xall[:, mask].astype(np.float64)
    n, v = X.shape
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = t_dist.sf(t_obs, df=n-1)
    check_idx = np.unique(np.linspace(0, v-1, 7, dtype=int))
    scipy_t = np.array([ttest_1samp(X[:, j], 0).statistic for j in check_idx])
    assert np.allclose(scipy_t, t_obs[check_idx], rtol=1e-10, atol=1e-10)
    # Sign flips at the participant level; the max over all tested voxels controls one-sided whole-brain FWE.
    rng = np.random.default_rng(SEED)
    null_max = np.empty(B, dtype=np.float32)
    sumsq = np.sum(X*X, axis=0)
    # Small batches keep memory bounded; matrix multiplication is the heavy operation.
    batch = 64
    for lo in range(0, B, batch):
        hi = min(B, lo+batch)
        signs = rng.choice(np.array([-1.,1.]), size=(hi-lo,n))
        sums = signs @ X
        denom = np.sqrt(np.maximum((sumsq[None,:] - sums*sums/n)/(n-1), 0) / n)
        t_perm = np.divide(sums/n, denom, out=np.zeros_like(sums), where=denom>0)
        null_max[lo:hi] = np.max(t_perm, axis=1)
    null_sorted = np.sort(null_max)
    fwe_p = (B + 1 - np.searchsorted(null_sorted, t_obs, side='left'))/(B+1)
    threshold = float(np.quantile(null_max, 1-ALPHA, method='higher'))
    significant = t_obs >= threshold

    def volume(vec, fill=np.nan):
        arr = np.full(mask.shape, fill, dtype=np.float32)
        arr[mask] = np.asarray(vec, dtype=np.float32)
        return arr
    header = nib.load(str(paths[0])).header.copy()
    for name, values in [('mean_effect',mean),('t_stat',t_obs),('p_uncorrected',p_unc),('p_fwe',fwe_p)]:
        nib.save(nib.Nifti1Image(volume(values), affine, header), OUT/f'{name}.nii.gz')
    nib.save(nib.Nifti1Image(mask.astype(np.uint8), affine, header), OUT/'analysis_mask.nii.gz')
    np.save(OUT/'null_max_t.npy', null_max)

    # Subject-level ROI means; report estimate and t-based CI as descriptive uncertainty.
    roi_vox = np.where(roi_mask)
    subj_roi = Xall[(slice(None),)+roi_vox].mean(axis=1)
    roi_mean, roi_sd = float(subj_roi.mean()), float(subj_roi.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    ci_half = float(t_dist.ppf(.975,n-1)*roi_se)
    roi_t = roi_mean/roi_se
    max_i = int(np.argmax(t_obs))
    max_ijk = ijk[max_i]
    max_xyz = nib.affines.apply_affine(affine, max_ijk)
    roi_significant = bool(np.any(significant & (np.linalg.norm(xyz-ROI_CENTER,axis=1) <= ROI_RADIUS_MM)))
    sig_vol = np.zeros(mask.shape, dtype=bool); sig_vol[mask] = significant
    t_vol = np.zeros(mask.shape, dtype=np.float32); t_vol[mask] = t_obs.astype(np.float32)
    labels, n_clusters = ndimage.label(sig_vol, structure=np.ones((3,3,3)))
    clusters = []
    for cluster_id in range(1, n_clusters + 1):
        cijk = np.array(np.where(labels == cluster_id)).T
        cstat = t_vol[labels == cluster_id]
        peak_xyz = nib.affines.apply_affine(affine, cijk[int(np.argmax(cstat))])
        clusters.append({'cluster_26conn':cluster_id,'voxels':int(len(cijk)),'peak_t':float(cstat.max()),'peak_mni_mm':[float(q) for q in peak_xyz]})
    summary = {
      'n_participants':n,'n_voxels_mask':v,'roi_voxels':int(roi_mask.sum()),
      'mask_nonzero_subjects_rule':'finite and nonzero in all 54 participant maps',
      'roi_definition':{'center_mni_mm':ROI_CENTER.tolist(),'radius_mm':ROI_RADIUS_MM},
      'inference':{'model':'one-sample group t test of participant contrast estimates against zero',
        'alternative':'positive','permutation':'participant-level sign flips; maximum positive t across whole mask',
        'n_random_sign_patterns':B,'seed':SEED,'alpha':ALPHA,'fwe_t_threshold':threshold,
        'max_stat_fwe_p_at_peak':float(fwe_p[max_i]),'min_resolvable_empirical_p':1/(B+1),
        'peak_t':float(t_obs[max_i]),'peak_uncorrected_p':float(p_unc[max_i]),'peak_mni_mm':[float(x) for x in max_xyz],
        'whole_brain_fwe_significant_voxels':int(significant.sum()),'vmPFC_roi_has_fwe_significant_voxel':roi_significant,'descriptive_26_connected_clusters':clusters},
      'vmPFC_roi_summary':{'mean_effect_estimate':roi_mean,'sd_between_participants':roi_sd,
        'ci95_t_based':[roi_mean-ci_half,roi_mean+ci_half],'one_sample_t_descriptive':float(roi_t),
        'uncorrected_one_sided_p_descriptive':float(t_dist.sf(roi_t,n-1))},
      'qc':{'all_checksums_match':bool(qc.checksum_match.all()),'all_bytes_match':bool(qc.bytes_match.all()),
        'all_same_grid':bool(qc.same_grid.all()),'all_finite':bool((qc.finite_voxels == np.prod(ref_shape)).all()),
        'excluded_participants':[],'independent_scipy_t_spotcheck_max_abs_difference':float(np.max(np.abs(scipy_t-t_obs[check_idx])))},
      'runtime':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'nibabel':nib.__version__,
        'pandas':pd.__version__,'scipy':__import__('scipy').__version__,'matplotlib':matplotlib.__version__,'nilearn':__import__('nilearn').__version__,'elapsed_seconds':round(time.time()-started,2)}
    }
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    pd.DataFrame({'participant_id':ids,'vmPFC_roi_mean_effect':subj_roi}).to_csv(OUT/'vmPFC_participant_effects.tsv',sep='\t',index=False)
    pd.DataFrame({'max_t_null':null_max}).to_csv(OUT/'max_t_null.tsv.gz',sep='\t',index=False,compression='gzip')

    # Figure: the primary corrected statistical map plus the individual ROI distribution.
    stat_img = nib.Nifti1Image(volume(t_obs, fill=0), affine, header)
    display = plotting.plot_stat_map(stat_img, threshold=threshold, display_mode='ortho', cut_coords=max_xyz.tolist(),
        cmap='hot', colorbar=True, title=f'Whole-brain FWE-positive map; cuts at peak (t ≥ {threshold:.2f})',
        annotate=True, black_bg=False, draw_cross=True, dim=0)
    display.savefig(FIG/'group_t_map.png', dpi=180)
    display.close()
    fig, ax = plt.subplots(figsize=(5.8,4.3), constrained_layout=True)
    rng2 = np.random.default_rng(SEED)
    ax.scatter(rng2.normal(1,0.035,n),subj_roi,s=28,alpha=.75,color='#355c7d',edgecolor='white',linewidth=.35,zorder=2)
    ax.errorbar([1],[roi_mean],yerr=[[ci_half],[ci_half]],fmt='D',color='#c44e52',capsize=5,markersize=7,zorder=3,label='Mean and 95% t CI')
    ax.axhline(0,color='0.35',lw=1,ls='--')
    ax.set(xlim=(.75,1.25),xticks=[1],xticklabels=['vmPFC sphere'],ylabel='Participant contrast estimate (upstream units)',title='Participant vmPFC estimates (10-mm sphere)')
    ax.legend(frameon=False,loc='best')
    fig.savefig(FIG/'vmPFC_participant_effects.png',dpi=180)
    plt.close(fig)
    print(json.dumps(summary,indent=2))

if __name__ == '__main__':
    main()
