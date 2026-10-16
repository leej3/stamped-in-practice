#!/usr/bin/env python3
"""Group inference for supplied NARPS AO86 gain-effect maps."""
from __future__ import annotations
import hashlib, json, os, platform, sys
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats, ndimage
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'input'
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
N_PERM = 9999
SEED = 20261016
ALPHA = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
    participants = pd.read_csv(INPUT / 'participants.tsv', sep='\t')
    sources = json.loads((INPUT / 'sources.json').read_text())
    files = sources['files']
    ids = participants.participant_id.tolist()
    assert len(ids) == 54 and len(set(ids)) == 54
    assert all(p.group == 'equalIndifference' for p in participants.itertuples())
    assert sum(k.endswith('_hypo1_cope.nii.gz') for k in files) == len(ids)

    images, arrays, qc = [], [], []
    for pid in ids:
        rel = f'data/{pid}_hypo1_cope.nii.gz'
        path = INPUT / rel
        meta = files[f'input/{rel}'] if f'input/{rel}' in files else files[rel]
        assert meta['participant_id'] == pid
        digest = sha256(path)
        assert digest == meta['sha256'], f'checksum mismatch: {pid}'
        img = nib.load(str(path)); data = img.get_fdata(dtype=np.float32)
        assert np.isfinite(data).all()
        if images:
            assert data.shape == images[0].shape
            assert np.allclose(img.affine, images[0].affine, atol=1e-5)
        images.append(img); arrays.append(data)
        nz = data != 0
        qc.append({'participant_id': pid, 'sha256': digest, 'nonzero_voxels': int(nz.sum()),
                   'mean_nonzero': float(data[nz].mean()), 'sd_nonzero': float(data[nz].std()),
                   'finite_fraction': float(np.isfinite(data).mean())})

    data = np.stack(arrays, axis=0)
    mask = np.all(data != 0, axis=0)
    assert mask.sum() > 10000
    X = data[:, mask].astype(np.float64)
    n, v = X.shape
    assert n == 54
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = stats.t.sf(t_obs, df=n-1)

    # Random sign flips are at the participant level; sum of squares stays fixed.
    rng = np.random.default_rng(SEED)
    sumsq = np.sum(X * X, axis=0)
    maxima = np.empty(N_PERM, dtype=np.float32)
    batch = 64
    for start in range(0, N_PERM, batch):
        stop = min(start + batch, N_PERM)
        signs = rng.choice(np.array([-1., 1.]), size=(stop-start, n))
        sums = signs @ X
        denom2 = np.maximum(n * sumsq[None, :] - sums * sums, np.finfo(float).tiny)
        t_perm = sums * np.sqrt(n-1) / np.sqrt(denom2)
        maxima[start:stop] = np.max(t_perm, axis=1)
    max_thr = float(np.quantile(maxima, 1-ALPHA, method='higher'))
    sorted_maxima = np.sort(maxima)
    p_fwer = (1 + N_PERM - np.searchsorted(sorted_maxima, t_obs, side='left')) / (N_PERM + 1)

    # Convert voxel coordinates from image affine into MNI coordinates.
    ijk = np.array(np.where(mask)).T
    xyz = nib.affines.apply_affine(images[0].affine, ijk)
    vm = ((xyz[:, 0] >= -15) & (xyz[:, 0] <= 15) & (xyz[:, 1] >= 20) &
          (xyz[:, 1] <= 60) & (xyz[:, 2] >= -20) & (xyz[:, 2] <= 10))
    assert vm.sum() > 0
    roi_idx = np.flatnonzero(vm)
    best = roi_idx[np.argmax(t_obs[roi_idx])]
    best_xyz = xyz[best]
    roi_participant = X[:, roi_idx].mean(axis=1)
    roi_t = stats.ttest_1samp(roi_participant, 0, alternative='greater')
    roi_mean = roi_participant.mean(); roi_se = stats.sem(roi_participant)
    roi_ci = stats.t.interval(.95, n-1, loc=roi_mean, scale=roi_se)

    # Independent reference calculation for selected voxels.
    selected = np.unique([0, v//3, 2*v//3, best, int(np.argmax(t_obs))])
    ref = []
    for j in selected:
        z = stats.ttest_1samp(X[:, j], 0, alternative='greater')
        assert np.isclose(z.statistic, t_obs[j], rtol=1e-10, atol=1e-10)
        assert np.isclose(z.pvalue, p_unc[j], rtol=1e-10, atol=1e-14)
        ref.append({'voxel_index_in_mask': int(j), 'scipy_t': float(z.statistic), 'scipy_p_one_sided': float(z.pvalue)})

    # Reconstruct 3D maps, NaN outside common coverage.
    t_img = np.full(mask.shape, np.nan, np.float32); t_img[mask] = t_obs
    p_img = np.full(mask.shape, np.nan, np.float32); p_img[mask] = p_fwer
    mean_img = np.full(mask.shape, np.nan, np.float32); mean_img[mask] = mean
    for name, values in [('group_t.nii.gz', t_img), ('fwer_p.nii.gz', p_img), ('group_mean.nii.gz', mean_img)]:
        nib.save(nib.Nifti1Image(values, images[0].affine, images[0].header), OUT / name)

    significant = np.flatnonzero(p_fwer < ALPHA)
    sig_mask = np.zeros(mask.shape, dtype=bool); sig_mask[mask] = p_fwer < ALPHA
    labels, n_clusters = ndimage.label(sig_mask, structure=np.ones((3, 3, 3), dtype=int))
    cluster_summaries = []
    for label in range(1, n_clusters + 1):
        loc = np.array(np.where(labels == label)).T
        coords = nib.affines.apply_affine(images[0].affine, loc)
        vals = t_img[labels == label]
        peak = coords[int(np.argmax(vals))]
        cluster_summaries.append({'voxels_26_connected': int(len(loc)), 'center_mni_mm': [float(x) for x in coords.mean(axis=0)], 'peak_mni_mm': [float(x) for x in peak], 'peak_t': float(vals.max())})
    sig_in_vm = [j for j in significant if vm[j]]
    top = int(np.argmax(t_obs))
    result = {
      'runtime': {'python': sys.version.split()[0], 'platform': platform.platform(), 'numpy': np.__version__, 'scipy': __import__('scipy').__version__, 'pandas': pd.__version__, 'matplotlib': __import__('matplotlib').__version__, 'nibabel': nib.__version__},
      'n_participants': n, 'n_excluded': 0, 'mask_voxels': int(v), 'voxel_size_mm': list(map(float, images[0].header.get_zooms()[:3])),
      'n_permutations': N_PERM, 'seed': SEED, 'alpha': ALPHA, 'max_t_fwe_critical': max_thr,
      'n_fwer_significant_voxels': int(len(significant)), 'n_26_connected_fwer_clusters': int(n_clusters), 'fwer_cluster_summaries': cluster_summaries, 'n_fwer_significant_in_vmPFC_mask': len(sig_in_vm),
      'whole_brain_decision': 'support' if sig_in_vm else 'no corrected support',
      'vmPFC_mask_definition_mni_mm': {'x':[-15,15], 'y':[20,60], 'z':[-20,10]}, 'vmPFC_mask_voxels':int(vm.sum()),
      'vmPFC_roi_mean_estimate':float(roi_mean), 'vmPFC_roi_mean_se':float(roi_se), 'vmPFC_roi_mean_t':float(roi_t.statistic),
      'vmPFC_roi_mean_p_one_sided_uncorrected':float(roi_t.pvalue), 'vmPFC_roi_mean_ci95_two_sided':[float(roi_ci[0]),float(roi_ci[1])],
      'best_vmPFC_voxel': {'mni_x_mm':float(best_xyz[0]),'mni_y_mm':float(best_xyz[1]),'mni_z_mm':float(best_xyz[2]),'mean_estimate':float(mean[best]),'t':float(t_obs[best]),'p_one_sided_uncorrected':float(p_unc[best]),'p_fwer_maxT':float(p_fwer[best])},
      'strongest_whole_brain_voxel': {'mni_x_mm':float(xyz[top,0]),'mni_y_mm':float(xyz[top,1]),'mni_z_mm':float(xyz[top,2]),'mean_estimate':float(mean[top]),'t':float(t_obs[top]),'p_one_sided_uncorrected':float(p_unc[top]),'p_fwer_maxT':float(p_fwer[top])},
      'independent_scipy_reference':ref,
      'permutation_mc_resolution':1/(N_PERM+1), 'input_map_qc':qc
    }
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    pd.DataFrame(qc).to_csv(OUT/'participant_qc.tsv',sep='\t',index=False)
    np.savetxt(OUT/'max_t_null.tsv', maxima, fmt='%.7g', header='max_positive_t_signflip')

    # Figure: group estimate with uncertainty in vmPFC ROI and spatial view of t statistics.
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.2), constrained_layout=True)
    rng2 = np.random.default_rng(SEED)
    jitter = rng2.normal(0, .035, size=n)
    ax[0].scatter(roi_participant, jitter, s=22, alpha=.72, color='#315b7d', edgecolor='none')
    ax[0].axvline(0, color='black', lw=1)
    ax[0].axvline(roi_mean, color='#bf4b32', lw=2, label='mean')
    ax[0].axvspan(roi_ci[0], roi_ci[1], color='#bf4b32', alpha=.16, label='95% CI')
    ax[0].set(yticks=[], xlabel='Participant mean gain-effect estimate', title='vmPFC ROI values (n = 54)')
    ax[0].legend(frameon=False, loc='upper left')
    # Coronal section at voxel with maximum vmPFC t; map with Nilearn-free Matplotlib.
    k = int(np.argmin(abs(np.arange(mask.shape[2]) * images[0].header.get_zooms()[2] + images[0].affine[2,3] - best_xyz[2])))
    section = t_img[:, :, k].T
    ax[1].imshow(section, origin='lower', cmap='RdBu_r', vmin=-7, vmax=7,
                 extent=[-96,96,-132,98], interpolation='nearest', aspect='equal')
    cb = fig.colorbar(ax[1].images[0], ax=ax[1], fraction=.046, pad=.04)
    cb.set_label('One-sample t statistic')
    ax[1].set(xlim=(-40,40), ylim=(-20,70), xlabel='MNI x (mm)', ylabel='MNI y (mm)',
              title=f'Group t map, z = {best_xyz[2]:.1f} mm')
    ax[1].add_patch(plt.Rectangle((-15,20),30,40,fill=False,edgecolor='black',lw=1.2,linestyle='--'))
    fig.suptitle('Potential gain effect: group estimates and vmPFC location')
    fig.savefig(FIG/'group_effects.png',dpi=180)
    plt.close(fig)
    # Null distribution figure.
    fig, ax = plt.subplots(figsize=(6.5,4), constrained_layout=True)
    ax.hist(maxima,bins=45,color='#809bb0',edgecolor='white')
    ax.axvline(max_thr,color='#bf4b32',lw=2,label=f'95th percentile = {max_thr:.2f}')
    ax.axvline(float(t_obs.max()),color='black',lw=1.5,linestyle='--',label=f'observed max t = {t_obs.max():.2f}')
    ax.set(xlabel='Maximum positive t over 198,029 voxels',ylabel='Permutations',title='Whole-brain sign-flip maximum-t null')
    ax.legend(frameon=False)
    fig.savefig(FIG/'max_t_null.png',dpi=180)
    plt.close(fig)

if __name__ == '__main__': main()
