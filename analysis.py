#!/usr/bin/env python3
"""Whole-brain group inference for NARPS Hypothesis 1 fixed participant cope maps."""
from pathlib import Path
import hashlib, json, re, time
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from nilearn import plotting

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'input/data'
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
N_PERM = 5000
SEED = 20261016
COVERAGE = 1.0

manifest=json.loads((ROOT/'input/sources.json').read_text())
meta=pd.read_csv(ROOT/'input/participants.tsv',sep='\t')
ids=meta.participant_id.tolist()
assert len(ids)==54 and meta.group.eq('equalIndifference').all()
imgs=[]; headers=[]; qc=[]
for pid in ids:
    rel=f'data/{pid}_hypo1_cope.nii.gz'
    info=manifest['files'][rel]
    path=ROOT/'input'/rel
    raw=path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if len(raw)!=info['bytes'] or sha!=info['sha256']:
        raise ValueError(f'Checksum/size mismatch: {rel}')
    im=nib.load(str(path)); a=np.asanyarray(im.dataobj,dtype=np.float64)
    if imgs and (a.shape!=imgs[0].shape or not np.allclose(im.affine,headers[0].affine)):
        raise ValueError(f'Inconsistent geometry: {rel}')
    if not np.isfinite(a).all(): raise ValueError(f'Nonfinite voxel: {rel}')
    imgs.append(a); headers.append(im)
    nz=a!=0
    qc.append({'participant_id':pid,'nonzero_voxels':int(nz.sum()),'nonzero_fraction':float(nz.mean()),
               'map_mean_nonzero':float(a[nz].mean()),'map_sd_nonzero':float(a[nz].std()),
               'map_max_abs':float(np.abs(a).max()),'sha256_verified':True})
Xfull=np.stack(imgs)
coverage=(Xfull!=0).mean(axis=0)
mask=coverage>=COVERAGE
assert mask.sum()>10000
X=Xfull[:,mask]
n,V=X.shape
mean=X.mean(axis=0)
sd=X.std(axis=0,ddof=1)
tobs=mean/(sd/np.sqrt(n))
df=n-1
p_unc=stats.t.sf(tobs,df)
# Exact parametric summary; primary familywise inference uses sign-flip max-T.
# Sign flipping is appropriate for the one-sample null under symmetric subject effects.
rng=np.random.default_rng(SEED)
max_t=np.empty(N_PERM,dtype=np.float32)
sumsq=np.sum(X*X,axis=0)
# Batched BLAS multiplies limit memory use. Include observed sign vector as one draw for bookkeeping only.
B=64
start=time.time()
for lo in range(0,N_PERM,B):
    b=min(B,N_PERM-lo)
    signs=rng.choice(np.array([-1.,1.]),size=(b,n))
    sy=signs @ X
    tt=sy*np.sqrt(n-1)/np.sqrt(np.maximum(n*sumsq[None,:]-sy*sy,1e-30))
    max_t[lo:lo+b]=tt.max(axis=1)
maxdist=np.sort(max_t)
p_fwer=np.searchsorted(maxdist,tobs,side='left')
p_fwer=(N_PERM-p_fwer+1)/(N_PERM+1)

# Prespecified descriptive vmPFC sphere: MNI coordinates in mm, 12-mm radius.
# It does not replace the required whole-brain familywise test.
coords=np.array(np.where(mask)).T
ijk=np.column_stack([coords,np.ones(len(coords))])
xyz=(headers[0].affine @ ijk.T).T[:,:3]
roi_center=np.array([0.,42.,-10.])
roi=(np.linalg.norm(xyz-roi_center,axis=1)<=12.)
if roi.sum()<10: raise ValueError('vmPFC sphere has too few voxels in analysis mask')
roi_subj=X[:,roi].mean(axis=1)
roi_mean=float(roi_subj.mean()); roi_sd=float(roi_subj.std(ddof=1)); roi_se=roi_sd/np.sqrt(n)
roi_t=roi_mean/roi_se
roi_p=float(stats.t.sf(roi_t,n-1))
roi_ci=stats.t.interval(.95,n-1,loc=roi_mean,scale=roi_se)
loo_mean=np.empty(n); loo_t=np.empty(n)
for s in range(n):
    v=np.delete(roi_subj,s)
    loo_mean[s]=v.mean()
    loo_t[s]=v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))
roi_wilcoxon=stats.wilcoxon(roi_subj,alternative='greater',zero_method='wilcox',method='auto')
# Sign-flip ROI p-value (secondary, uncorrected) using same randomization seed stream independent.
rng_roi=np.random.default_rng(SEED+1)
roi_null=np.empty(N_PERM)
for lo in range(0,N_PERM,B):
    b=min(B,N_PERM-lo)
    signs=rng_roi.choice(np.array([-1.,1.]),size=(b,n))
    val=signs@roi_subj
    roi_null[lo:lo+b]=val*np.sqrt(n-1)/np.sqrt(np.maximum(n*np.sum(roi_subj**2)-val**2,1e-30))
roi_perm_p=float((np.count_nonzero(roi_null>=roi_t)+1)/(N_PERM+1))

# Place vectors into image grids.
def save_map(vec, name, dtype=np.float32):
    arr=np.zeros(mask.shape,dtype=dtype); arr[mask]=vec
    im=nib.Nifti1Image(arr,headers[0].affine,headers[0].header.copy())
    im.set_data_dtype(dtype); nib.save(im,str(OUT/name))
save_map(mean,'group_mean_cope.nii.gz')
save_map(tobs,'group_t_positive.nii.gz')
save_map(p_fwer,'group_p_fwer_positive.nii.gz')
save_map((p_fwer<=.05).astype(np.uint8),'group_fwer05_positive.nii.gz',np.uint8)

# Save tabular QC and statistical summaries.
pd.DataFrame(qc).to_csv(OUT/'participant_qc.tsv',sep='\t',index=False)
pd.DataFrame({'participant_id':ids,'vmPFC_sphere_mean_cope':roi_subj,
              'leave_one_out_group_mean':loo_mean,'leave_one_out_t':loo_t}).to_csv(
              OUT/'vmPFC_participant_summary.tsv',sep='\t',index=False)
vox=pd.DataFrame({'i':coords[:,0],'j':coords[:,1],'k':coords[:,2],
                  'x':xyz[:,0],'y':xyz[:,1],'z':xyz[:,2],
                  'mean_cope':mean,'t':tobs,'p_uncorrected_one_sided':p_unc,
                  'p_fwer_maxT_one_sided':p_fwer})
vox.to_csv(OUT/'voxel_results.tsv.gz',sep='\t',index=False,compression='gzip')
# Local maxima among whole brain t values, reported as descriptive coordinates.
from scipy.ndimage import maximum_filter
all_t=np.zeros(mask.shape); all_t[mask]=tobs
loc=(all_t==maximum_filter(all_t,size=5)) & mask
peaks=np.argwhere(loc)
peakrows=[]
for c in peaks:
    c4=np.r_[c,1]; cxyz=(headers[0].affine@c4)[:3]
    ix=np.ravel_multi_index(tuple(c),mask.shape)
    peakrows.append((all_t[tuple(c)],*cxyz))
peakrows=sorted(peakrows,reverse=True)[:20]
pd.DataFrame(peakrows,columns=['t','x','y','z']).to_csv(OUT/'top_peaks.tsv',sep='\t',index=False)
summary={
 'n':n,'n_excluded':0,'n_mask_voxels':int(mask.sum()),'mask_coverage_threshold':COVERAGE,
 'n_permutations':N_PERM,'seed':SEED,'primary_direction':'positive, one-sided',
 'maxT_FWER_alpha':.05,'maxT_threshold_95':float(np.quantile(max_t,.95,method='higher')),
 'global_max_t':float(np.max(tobs)),'global_max_t_coordinate_mni_mm':next((list(map(float,row[1:])) for row in peakrows[:1]),None),
 'global_max_p_fwer':float(np.min(p_fwer)),
 'n_fwer_significant':int(np.count_nonzero(p_fwer<=.05)),
 'vmPFC_max_t':float(np.max(tobs[roi])),
 'vmPFC_min_p_fwer':float(np.min(p_fwer[roi])),
 'vmPFC_sphere_center_mni_mm':roi_center.tolist(),'vmPFC_sphere_radius_mm':12,
 'vmPFC_voxels':int(roi.sum()),'vmPFC_mean_cope':roi_mean,'vmPFC_sd_subject_means':roi_sd,
 'vmPFC_median_subject_mean':float(np.median(roi_subj)),
 'vmPFC_ci95_t':[float(roi_ci[0]),float(roi_ci[1])],'vmPFC_t':float(roi_t),
 'vmPFC_wilcoxon_p_one_sided':float(roi_wilcoxon.pvalue),
 'vmPFC_leave_one_out_mean_range':[float(loo_mean.min()),float(loo_mean.max())],
 'vmPFC_leave_one_out_t_range':[float(loo_t.min()),float(loo_t.max())],
 'vmPFC_p_uncorrected_one_sided_t':roi_p,'vmPFC_p_signflip_one_sided':roi_perm_p,
 'whole_brain_permutation_seconds':time.time()-start,
 'interpretation_units':'upstream contrast parameter estimate; not per currency unit'
}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

# Figure 1: mean participant contrast in sagittal/coronal/axial views.
mean_img=nib.load(str(OUT/'group_mean_cope.nii.gz'))
fig=plotting.plot_stat_map(mean_img,display_mode='ortho',cut_coords=(0,42,-10),
  title='Mean gain-effect estimate (unthresholded)',threshold=0.02,
  cmap='cold_hot',colorbar=True,black_bg=False,annotate=True,draw_cross=True)
fig.savefig(FIG/'mean_gain_effect.png',dpi=180); fig.close()
# Figure 2: t map with whole-brain max-T corrected p<=.05 threshold only.
thresholded=np.zeros(mask.shape,dtype=float)
thresholded[mask]=np.where(p_fwer<=.05,tobs,0.)
# For unsupported result, show unthresholded t with corrected-significant locations outlined by image.
if np.any(p_fwer<=.05):
    timg=nib.Nifti1Image(thresholded,headers[0].affine)
else:
    timg=nib.Nifti1Image(all_t,headers[0].affine)
fig=plotting.plot_stat_map(timg,display_mode='ortho',cut_coords=(-26,-102,-4),
  title='Positive group t; max-T whole-brain FWER p≤.05' if np.any(p_fwer<=.05) else 'Positive group t (no voxels pass max-T FWER p≤.05)',
  threshold=float(np.quantile(max_t,.95,method='higher')) if np.any(p_fwer<=.05) else float(np.quantile(tobs,.995)),
  cmap='cold_hot',colorbar=True,black_bg=False,annotate=True,draw_cross=True)
fig.savefig(FIG/'whole_brain_maxT.png',dpi=180); fig.close()
# Figure 3: distribution of subject vmPFC sphere means.
fig,ax=plt.subplots(figsize=(6.5,4.2))
ax.hist(roi_subj,bins=12,color='#4878a8',edgecolor='white')
ax.axvline(0,color='black',lw=1); ax.axvline(roi_mean,color='#d1495b',lw=2,label=f'mean={roi_mean:.3f}')
ax.set(xlabel='Mean participant gain-effect estimate in vmPFC sphere',ylabel='Participants',
       title='vmPFC summary (descriptive ROI; all participants)')
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(FIG/'vmPFC_subject_distribution.png',dpi=180); plt.close(fig)
print(json.dumps(summary,indent=2))
