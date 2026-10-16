#!/usr/bin/env python3
"""Group analysis of supplied NARPS AO86 participant gain-effect maps.

Primary inference: one-sided one-sample t statistic, family-wise correction over
common nonzero map coverage using participant-level sign-flip max-T permutation.
"""
from pathlib import Path
import hashlib, json, platform
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from nilearn import plotting
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'input' / 'data'
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
SEED = 20261016
N_PERM = 5000

meta = json.loads((ROOT/'input/sources.json').read_text())
participants = pd.read_csv(ROOT/'input/participants.tsv', sep='\t')
files = sorted(DATA.glob('*_hypo1_cope.nii.gz'))
file_ids = [p.name.split('_')[0] for p in files]
assert len(files) == 54 and len(set(file_ids)) == 54
assert set(file_ids) == set(participants.participant_id)
assert (participants.group == 'equalIndifference').all()

# Integrity and geometry QC, preserving every supplied participant.
imgs=[]; checksum_rows=[]
ref=None
for p in files:
    im=nib.load(str(p)); imgdata=im.get_fdata(dtype=np.float32)
    if ref is None: ref=im
    assert imgdata.shape == ref.shape and np.allclose(im.affine, ref.affine, atol=1e-5)
    assert np.isfinite(imgdata).all()
    rec=meta['files'][f'data/{p.name}']
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest == rec['sha256']
    imgs.append(imgdata)
    checksum_rows.append({'participant_id':p.name.split('_')[0], 'file':str(p.relative_to(ROOT)),
                          'bytes':p.stat().st_size,'sha256':digest,'finite':True,
                          'shape':'x'.join(map(str,imgdata.shape))})
X=np.stack(imgs).astype(np.float64) # participant x voxel grid
n=X.shape[0]
# These cope images encode zero outside the participant's modeled brain support.
# Use only voxels with nonzero estimates in every participant, so no zeros are
# mistaken for valid estimates and all voxelwise tests have the same N.
mask=np.all(X != 0, axis=0)
Y=X[:,mask]
assert Y.shape[1] > 100000

# Positive one-sample t map and exact parametric summary statistics.
sum_y=Y.sum(axis=0)
sumsq=(Y*Y).sum(axis=0)
den=np.sqrt(np.maximum(n*sumsq-sum_y**2, 0)/(n-1))
t_obs=(sum_y/n)/(den/np.sqrt(n))
p_unc=stats.t.sf(t_obs,n-1)
mean_map=np.zeros(ref.shape,dtype=np.float32); mean_map[mask]=Y.mean(axis=0)
t_map=np.zeros(ref.shape,dtype=np.float32); t_map[mask]=t_obs.astype(np.float32)
p_map=np.ones(ref.shape,dtype=np.float32); p_map[mask]=p_unc.astype(np.float32)

# Sign-flip permutation test under the one-sample null. The maximum positive
# t statistic across the entire common brain mask is the FWE reference.
rng=np.random.default_rng(SEED)
max_t=np.empty(N_PERM,dtype=np.float64)
# Chunk to bound temporary memory; matrix multiplication uses BLAS if available.
chunk=100
for start in range(0,N_PERM,chunk):
    b=min(chunk,N_PERM-start)
    signs=rng.choice(np.array([-1.0,1.0]),size=(b,n))
    perm_sum=signs @ Y
    perm_t=perm_sum*np.sqrt(n-1)/np.sqrt(np.maximum(n*sumsq[None,:]-perm_sum**2,1e-30))
    max_t[start:start+b]=np.max(perm_t,axis=1)
    del signs,perm_sum,perm_t
p_fwe=(1+(max_t[:,None] >= t_obs[None,:]).sum(axis=0))/(N_PERM+1)
pfwe_map=np.ones(ref.shape,dtype=np.float32); pfwe_map[mask]=p_fwe.astype(np.float32)
sig=p_fwe < .05
thresholded=np.zeros(ref.shape,dtype=np.float32); thresholded[mask]=np.where(sig,t_obs,0).astype(np.float32)

# Independent, coordinate-defined central vmPFC descriptive ROI: 10-mm sphere
# centered at MNI [0, 40, -10], chosen a priori from conventional vmPFC anatomy.
# It is not used to define the whole-brain mask or primary corrected inference.
ijk=np.indices(ref.shape).reshape(3,-1).T
xyz=nib.affines.apply_affine(ref.affine,ijk).reshape(*ref.shape,3)
roi=(np.sum((xyz-np.array([0.,40.,-10.]))**2,axis=-1) <= 10.**2) & mask
roi_nvox=int(roi.sum())
roi_subj=X[:,roi].mean(axis=1)
roi_mean=float(roi_subj.mean()); roi_sd=float(roi_subj.std(ddof=1)); roi_se=roi_sd/np.sqrt(n)
roi_t,roi_p_two=stats.ttest_1samp(roi_subj,0)
roi_ci=stats.t.interval(.95,n-1,loc=roi_mean,scale=roi_se)
roi_p_one=float(stats.t.sf(roi_t,n-1))
roi_median=float(np.median(roi_subj))
# Sensitivity to skew/outlier influence; this is descriptive, not primary.
wil=stats.wilcoxon(roi_subj, alternative='greater', zero_method='wilcox')

# Global descriptive QC and participant-level data.
mean_effect=float(Y.mean()); pooled_sd=float(Y.std(ddof=1))
participant_summary=pd.DataFrame({'participant_id':file_ids,
    'mean_effect_common_mask':Y.mean(axis=1),
    'median_effect_common_mask':np.median(Y,axis=1),
    'vmPFC_sphere_mean':roi_subj})
participant_summary=participant_summary.merge(participants,on='participant_id',how='left')
participant_summary.to_csv(OUT/'participant_summary.tsv',sep='\t',index=False)
pd.DataFrame(checksum_rows).to_csv(OUT/'input_qc.tsv',sep='\t',index=False)

# Save analysis maps in supplied MNI geometry.
for name,arr in [('group_mean_effect.nii.gz',mean_map),('group_tstat.nii.gz',t_map),
                 ('group_p_uncorrected.nii.gz',p_map),('group_p_fwe_maxT.nii.gz',pfwe_map),
                 ('group_tstat_fwe_p05.nii.gz',thresholded)]:
    nib.save(nib.Nifti1Image(arr,ref.affine,ref.header),OUT/name)

# Figures: descriptive mean cope and thresholded whole-brain FWE map.
mean_img=nib.Nifti1Image(mean_map,ref.affine,ref.header)
sig_img=nib.Nifti1Image(t_map,ref.affine,ref.header)
fig=plt.figure(figsize=(12,7))
plotting.plot_stat_map(mean_img,display_mode='ortho',cut_coords=(0,40,-10),
    threshold=0.01,title='Mean effect (cope)',
    colorbar=True,figure=fig,axes=(.02,.12,.46,.75),cmap='cold_hot',vmin=-.15,vmax=.15)
plotting.plot_stat_map(sig_img,display_mode='ortho',cut_coords=(0,40,-10),
    threshold=0,title='Unthresholded group t statistic',
    colorbar=True,figure=fig,axes=(.52,.12,.46,.75),cmap='cold_hot',vmin=-1,vmax=1)
fig.suptitle('Participant gain-effect maps: group mean and one-sample t',fontsize=14,y=.98)
fig.text(.75,.045,'Whole-brain max-T FWE p < .05: no voxels',ha='center',fontsize=10)
fig.savefig(FIG/'group_maps.png',dpi=180,bbox_inches='tight'); plt.close(fig)

# ROI participant distribution with mean and CI.
fig,ax=plt.subplots(figsize=(7,4.5))
ax.scatter(np.arange(1,n+1),roi_subj,s=22,alpha=.8,color='#365f91')
ax.axhline(0,color='black',lw=1)
ax.axhline(roi_mean,color='#b34827',lw=2,label=f'Mean {roi_mean:.4f}')
ax.fill_between([0,n+1],roi_ci[0],roi_ci[1],color='#b34827',alpha=.13,label='95% t CI for mean')
ax.set(xlabel='Participant (sorted by file ID)',ylabel='vmPFC sphere mean cope',
       title='Participant-level vmPFC gain-effect estimates')
ax.set_xlim(0,n+1); ax.legend(frameon=False); fig.tight_layout()
fig.savefig(FIG/'vmPFC_participants.png',dpi=180); plt.close(fig)

peak_idx=np.unravel_index(np.argmax(t_map),t_map.shape)
peak_xyz=nib.affines.apply_affine(ref.affine,np.array(peak_idx))
max_fwe=float(np.max(pfwe_map[mask])) # not inferentially helpful
res={
 'n_expected':54,'n_included':n,'n_excluded':0,'common_mask_voxels':int(mask.sum()),
 'image_shape':list(ref.shape),'voxel_size_mm':list(map(float,ref.header.get_zooms()[:3])),
 'number_permutations':N_PERM,'random_seed':SEED,'primary_test':'one-sided one-sample t; participant sign-flip max-T FWE across common nonzero coverage',
 'max_observed_t':float(t_obs.max()),'max_observed_t_mni_mm':list(map(float,peak_xyz)),
 'peak_fwe_p':float(p_fwe.max()) if False else float(p_fwe[np.argmax(t_obs)]),
 'permutation_maxT_95th_percentile':float(np.quantile(max_t,.95)),
 'n_voxels_fwe_p_lt_0_05':int(sig.sum()),'vmPFC_roi':'10-mm sphere centered MNI [0,40,-10], defined independently of maps',
 'vmPFC_roi_voxels':roi_nvox,'vmPFC_mean_cope':roi_mean,'vmPFC_sd_between_subjects':roi_sd,
 'vmPFC_95pct_t_CI_for_mean_cope':[float(roi_ci[0]),float(roi_ci[1])],
 'vmPFC_t_df':float(roi_t),'vmPFC_one_sided_uncorrected_p':roi_p_one,
 'vmPFC_two_sided_uncorrected_p':float(roi_p_two),'vmPFC_median_cope':roi_median,
 'vmPFC_wilcoxon_one_sided_p_sensitivity':float(wil.pvalue),
 'mean_cope_across_common_mask':mean_effect,'pooled_voxelwise_sd_descriptive':pooled_sd,
 'input_checksums_all_match':True,'software':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__,'nibabel':nib.__version__}
}
(OUT/'summary.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
