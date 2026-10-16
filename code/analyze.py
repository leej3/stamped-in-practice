#!/usr/bin/env python3
"""Group analysis of fixed NARPS AO86 gain-effect maps."""
from __future__ import annotations
import argparse, glob, hashlib, json, platform, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats, ndimage
from scipy.stats import false_discovery_control
import matplotlib.pyplot as plt
from nilearn import datasets, image, plotting

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'; FIG = ROOT / 'figures'

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--permutations',type=int,default=9999)
    ap.add_argument('--seed',type=int,default=240519)
    ap.add_argument('--skip-atlas',action='store_true',help='Skip secondary AAL atlas annotation')
    ap.add_argument('--output-dir',type=Path,default=ROOT/'results')
    ap.add_argument('--figure-dir',type=Path,default=ROOT/'figures')
    args=ap.parse_args()
    OUT=args.output_dir if args.output_dir.is_absolute() else ROOT/args.output_dir
    FIG=args.figure_dir if args.figure_dir.is_absolute() else ROOT/args.figure_dir
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'input/sources.json').read_text())
    participants_path=ROOT/'input/participants.tsv'
    if sha256(participants_path)!=manifest['files']['participants.tsv']['sha256']:
        raise ValueError('Participant table differs from source manifest')
    participants=pd.read_csv(participants_path,sep='\t')
    ids=participants.participant_id.tolist()
    assert participants.participant_id.is_unique and len(ids)==54
    assert set(participants.group)=={'equalIndifference'}
    files=[ROOT/'input/data'/f'{pid}_hypo1_cope.nii.gz' for pid in ids]
    missing=[str(f) for f in files if not f.is_file()]
    if missing: raise FileNotFoundError(missing)
    all_hashes={'input/participants.tsv':manifest['files']['participants.tsv']['sha256']}
    exp=manifest['files']
    for pid,f in zip(ids,files):
        key=f'data/{f.name}'; rec=exp[key]
        if f.stat().st_size != rec['bytes'] or sha256(f)!=rec['sha256']:
            raise ValueError(f'Input differs from manifest: {f}')
        all_hashes[str(f.relative_to(ROOT))]=rec['sha256']
    imgs=[nib.load(str(f)) for f in files]
    ref=imgs[0]
    shape=ref.shape; affine=ref.affine
    for pid,im in zip(ids,imgs):
        if im.shape!=shape or not np.allclose(im.affine,affine,atol=1e-5):
            raise ValueError(f'Geometry mismatch: {pid}')
    data=np.stack([im.get_fdata(dtype=np.float32) for im in imgs])
    finite=np.isfinite(data).all(axis=(1,2,3))
    if not finite.all(): raise ValueError('Non-finite voxels in one or more maps')
    # Common supported domain: voxels nonzero in every participant image.
    mask=np.all(data!=0,axis=0)
    if mask.sum()<10000: raise ValueError('Unexpectedly small common support mask')
    Y=data[:,mask].astype(np.float64)
    n=Y.shape[0]; df=n-1
    mu=Y.mean(0); sd=Y.std(0,ddof=1); se=sd/np.sqrt(n)
    t_obs=mu/se
    p_unc=stats.t.sf(t_obs,df)
    # Independent formula check through scipy's one-sample t implementation at a sampled set.
    sample=np.linspace(0,Y.shape[1]-1,min(1000,Y.shape[1]),dtype=int)
    t_ref,p_ref=stats.ttest_1samp(Y[:,sample],0,axis=0,alternative='greater')
    if not np.allclose(t_obs[sample],t_ref,rtol=1e-10,atol=1e-10):
        raise AssertionError('Independent t statistic check failed')
    # Sign-flip max-T; recompute the one-sample denominator for each flipped sample.
    sum_sq=np.sum(Y*Y,axis=0)
    # Formula for t of any sign-flipped sample: signed sum / sqrt((n*sum(x^2)-sum(x)^2)/(n-1)).
    check_signs=rng_check=np.random.default_rng(args.seed).choice(np.array([-1.,1.]),size=n)
    signed_check=check_signs[:,None]*Y[:,sample]
    sums_check=signed_check.sum(axis=0)
    t_check=sums_check/np.sqrt((n*(signed_check*signed_check).sum(axis=0)-sums_check**2)/(n-1))
    scipy_check=stats.ttest_1samp(signed_check,0,axis=0,alternative='greater').statistic
    if not np.allclose(t_check,scipy_check,rtol=1e-10,atol=1e-10):
        raise AssertionError('Independent permuted t statistic check failed')
    rng=np.random.default_rng(args.seed)
    max_t=np.empty(args.permutations,dtype=np.float32)
    # Save full maxima for exact reproducibility and audit.
    for b in range(args.permutations):
        signs=rng.choice(np.array([-1.,1.]),size=n)
        tsum=signs @ Y
        t_perm=tsum/np.sqrt((n*sum_sq-tsum**2)/(n-1))
        max_t[b]=np.max(t_perm)
    sorted_max=np.sort(max_t)
    # Right-tail counts without allocating permutations × voxels.
    p_fwe=(1+args.permutations-np.searchsorted(sorted_max,t_obs,side='left'))/(args.permutations+1)
    # FDR is a secondary whole-brain sensitivity.
    p_fdr=false_discovery_control(p_unc,method='bh')
    # Reconstruct maps in original grid, keeping outside-common-support voxels zero.
    def ni(data_vec,dtype=np.float32):
        arr=np.zeros(shape,dtype=dtype); arr[mask]=data_vec
        return nib.Nifti1Image(arr,affine,ref.header)
    stat_paths={}
    for name,vec in [('mean_effect',mu),('t_one_sided',t_obs),('p_uncorrected',p_unc),('p_fwe_maxT',p_fwe),('p_fdr_bh',p_fdr)]:
        path=OUT/f'{name}.nii.gz'; nib.save(ni(vec),path); stat_paths[name]=str(path.relative_to(ROOT))
    nib.save(nib.Nifti1Image(mask.astype(np.uint8),affine,ref.header),OUT/'common_support_mask.nii.gz')
    np.save(OUT/'permutation_max_t.npy',max_t)
    # Secondary, independent AAL anatomical definition of broad ventromedial prefrontal coverage.
    roi_data=None; roi_label=[]
    if not args.skip_atlas:
        atlas=datasets.fetch_atlas_aal(version='3v2')
        atlas_img=image.resample_to_img(atlas.maps,ref,interpolation='nearest')
        labels=list(atlas.labels)
        # AAL medial orbital frontal and rectus labels; bilateral, intentionally broad approximation.
        roi_codes=[]
        for i,label in enumerate(labels):
            if any(term in str(label).lower() for term in ['frontal_med_orb','rectus']):
                roi_codes.append(i)
                roi_label.append(str(label))
        atlas_arr=atlas_img.get_fdata().astype(int)
        roi=np.isin(atlas_arr,roi_codes)&mask
        if roi.sum()==0: raise ValueError('AAL vmPFC proxy does not overlap common support')
        roi_data=data[:,roi].mean(axis=1)
        roi_table=pd.DataFrame({'participant_id':ids,'mean_AAL_medial_orbitofrontal_rectus_effect':roi_data})
        roi_table.to_csv(OUT/'vmPFC_proxy_subject_values.tsv',sep='\t',index=False)
        roi_t,roi_p=stats.ttest_1samp(roi_data,0,alternative='greater')
        roi_mean=float(roi_data.mean()); roi_sd=float(roi_data.std(ddof=1)); roi_se=roi_sd/np.sqrt(n)
        roi_ci=stats.t.interval(.95,df,loc=roi_mean,scale=roi_se)
        # Leave-one-out estimates describe sensitivity of the ROI average, not formal inferential tests.
        loo=np.array([np.delete(roi_data,j).mean() for j in range(n)])
        roi_summary={'definition':'AAL3v2 bilateral Frontal_Med_Orb and Rectus labels intersected with common support; broad anatomical proxy, secondary only',
                     'labels':roi_label,'voxels':int(roi.sum()),'mean':roi_mean,'sd_between_participants':roi_sd,
                     'ci95_t':list(map(float,roi_ci)),'t':float(roi_t),'p_one_sided_uncorrected':float(roi_p),
                     'loo_mean_min':float(loo.min()),'loo_mean_max':float(loo.max()),'loo_all_positive':bool((loo>0).all()),
                     'voxelwise_maxT_FWE_p_min_in_proxy':float(p_fwe[roi[mask]].min()),
                     'voxelwise_FWE_q05_voxels_in_proxy':int((p_fwe[roi[mask]]<=.05).sum()),
                     'voxelwise_BH_q05_voxels_in_proxy':int((p_fdr[roi[mask]]<=.05).sum()),
                     'voxelwise_BH_min_q_in_proxy':float(p_fdr[roi[mask]].min()),
                     'max_t_in_proxy':float(t_obs[roi[mask]].max())}
        (OUT/'vmPFC_proxy_summary.json').write_text(json.dumps(roi_summary,indent=2)+'\n')
        # Atlas labels at highest whole-brain t voxel and positive corrected voxels.
        peak_idx=np.unravel_index(np.argmax(ni(t_obs).get_fdata()),shape)
        peak_xyz=nib.affines.apply_affine(affine,peak_idx).tolist()
        peak_label=[]
        peak_code=int(atlas_arr[peak_idx])
        if 0<=peak_code<len(labels): peak_label=[str(labels[peak_code])]
    else:
        roi_summary=None; peak_idx=np.unravel_index(np.argmax(ni(t_obs).get_fdata()),shape)
        peak_xyz=nib.affines.apply_affine(affine,peak_idx).tolist(); peak_label=[]
    # significant voxels/clusters from the strict max-T FWE map
    sig=p_fwe<=.05
    sig_img=ni(sig.astype(np.uint8),np.uint8)
    labs,ncl=ndimage.label(sig_img.get_fdata()>0)
    clusters=[]
    for c in range(1,ncl+1):
        vox=np.argwhere(labs==c); vals=ni(t_obs).get_fdata()[labs==c]
        peak=vox[np.argmax(vals)]; xyz=nib.affines.apply_affine(affine,peak).tolist()
        clusters.append({'cluster':c,'voxels':int(len(vox)),'peak_t':float(vals.max()),'peak_mni_mm':xyz})
    # Descriptive whole-brain empirical summaries; no inferential exclusions.
    subj_summary=pd.DataFrame({'participant_id':ids,'map_mean_common_support':Y.mean(axis=1),
                               'map_sd_common_support':Y.std(axis=1),'map_absmax_common_support':np.abs(Y).max(axis=1)})
    subj_summary.to_csv(OUT/'participant_qc.tsv',sep='\t',index=False)
    # Simple estimates for the peak voxel (post-selection; descriptive only).
    peakval=data[:,peak_idx[0],peak_idx[1],peak_idx[2]]
    peak_stats={'mean':float(peakval.mean()),'sd':float(peakval.std(ddof=1)),'t':float(ni(t_obs).get_fdata()[peak_idx]),
                'uncorrected_p':float(ni(p_unc).get_fdata()[peak_idx]),'maxT_fwe_p':float(ni(p_fwe).get_fdata()[peak_idx])}
    # Figures
    plt.figure(figsize=(8,4.5)); plt.hist(subj_summary.map_mean_common_support,bins=12,color='#3478a8',edgecolor='white')
    plt.axvline(0,color='black',lw=1); plt.xlabel('Participant mean gain contrast (common support)'); plt.ylabel('Participants')
    plt.title('Participant-level contrast distribution'); plt.tight_layout(); plt.savefig(FIG/'participant_qc.png',dpi=180); plt.close()
    if roi_data is not None:
        plt.figure(figsize=(7,4.5)); x=np.arange(n); plt.scatter(x,roi_data,color='#245a79',s=30)
        plt.axhline(0,color='black',lw=1); plt.axhline(roi_mean,color='#c44e52',lw=2,label=f'Mean {roi_mean:.3g}')
        plt.axhspan(roi_ci[0],roi_ci[1],color='#c44e52',alpha=.15,label='95% CI for mean')
        plt.xlabel('Participant (source order)'); plt.ylabel('Mean contrast in AAL vmPFC proxy')
        plt.title('Secondary anatomical summary (not whole-brain corrected)'); plt.legend(frameon=False); plt.tight_layout()
        plt.savefig(FIG/'vmPFC_proxy_distribution.png',dpi=180); plt.close()
    plotting.plot_stat_map(ni(np.where(p_fwe<=.05,t_obs,0)),bg_img=datasets.load_mni152_template(resolution=2),
                           display_mode='ortho',cut_coords=(0,40,-10),threshold=0,
                           title='vmPFC-centered slices: no max-T-FWE voxels (p ≤ .05)',
                           output_file=str(FIG/'positive_maxT_FWE.png'),black_bg=False,colorbar=True)
    plotting.plot_stat_map(ni(np.where(p_fwe<=.05,t_obs,0)),bg_img=datasets.load_mni152_template(resolution=2),
                           display_mode='ortho',cut_coords=tuple(peak_xyz),threshold=0,
                           title='Whole-brain positive max-T FWE clusters (p ≤ .05)',
                           output_file=str(FIG/'positive_maxT_FWE_peak.png'),black_bg=False,colorbar=True)
    plotting.plot_stat_map(ni(t_obs),bg_img=datasets.load_mni152_template(resolution=2),
                           display_mode='ortho',cut_coords=tuple(peak_xyz),threshold=3,
                           title='Unthresholded one-sample t map at peak (t > 3 shown)',
                           output_file=str(FIG/'tmap_peak_slices.png'),black_bg=False,colorbar=True)
    plotting.plot_stat_map(ni(t_obs),bg_img=datasets.load_mni152_template(resolution=2),
                           display_mode='ortho',cut_coords=(0,40,-10),threshold=3,
                           title='Unthresholded one-sample t map (t > 3 shown)',
                           output_file=str(FIG/'tmap_unthresholded.png'),black_bg=False,colorbar=True)
    result={'n':n,'df':df,'excluded_ids':[],'included_ids':ids,'mask':'intersection of nonzero voxels in all 54 effect maps',
            'mask_voxels':int(mask.sum()),'mask_fraction_grid':float(mask.mean()),'shape':shape,'affine':affine.tolist(),
            'direction':'positive','permutations':args.permutations,'seed':args.seed,
            'permutation_p_resolution':1/(args.permutations+1),'maxT_FWE_alpha_0.05_voxels':int(sig.sum()),
            'clusters':clusters,'max_t_95pct':float(np.quantile(max_t,.95)),'max_t_99pct':float(np.quantile(max_t,.99)),
            'smallest_fwe_p':float(p_fwe.min()),'smallest_uncorrected_p':float(p_unc.min()),
            'smallest_BH_FDR_p':float(p_fdr.min()),'BH_FDR_q05_voxels':int((p_fdr<=.05).sum()),
            'peak_t_voxel':{'ijk':list(map(int,peak_idx)),'mni_mm':peak_xyz,'aal_label':peak_label,**peak_stats},
            'vmPFC_proxy':roi_summary,'source_files_sha256':all_hashes,
            'participant_map_mean_range': [float(subj_summary.map_mean_common_support.min()),float(subj_summary.map_mean_common_support.max())],
            'versions':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,'nibabel':nib.__version__,'nilearn':__import__('nilearn').__version__,'scipy':__import__('scipy').__version__,'matplotlib':__import__('matplotlib').__version__},
            'outputs':stat_paths}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_files_sha256','versions','outputs','included_ids')},indent=2))

if __name__=='__main__': main()
