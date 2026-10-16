#!/usr/bin/env python3
"""NARPS AO86 equal-indifference gain-effect group analysis.

Inputs are fixed single-subject contrast parameter estimates; this script performs
only group analysis. See report.md for estimand, mask and inferential assumptions.
"""
from pathlib import Path
import hashlib, json, sys
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy.ndimage import label as connected_components
import matplotlib.pyplot as plt
from nilearn import plotting, image

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; OUT=ROOT/'results'; FIG=ROOT/'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
SEED=20261016
N_PERM=9999
COVERAGE=1.00
ROI=(0.0, 40.0, -10.0)  # pre-specified midline vmPFC sphere centre in MNI mm
ROI_RADIUS=10.0

# Verify every analysis image against the immutable source manifest.
manifest=json.loads((ROOT/'input/sources.json').read_text())
entries=[(rel,meta) for rel,meta in manifest['files'].items() if rel.startswith('data/')]
participants=pd.read_csv(ROOT/'input/participants.tsv',sep='\t')
by_id={r.participant_id:r for r in participants.itertuples()}
imgs=[]; ids=[]; header_ref=None
qc=[]
for rel,meta in entries:
    f=DATA/Path(rel).name
    b=f.read_bytes(); sha=hashlib.sha256(b).hexdigest()
    if len(b)!=meta['bytes'] or sha!=meta['sha256']:
        raise RuntimeError(f'Checksum mismatch for {f}')
    if meta['participant_id'] not in by_id:
        raise RuntimeError(f"{meta['participant_id']} absent from participant table")
    im=nib.load(str(f)); arr=im.get_fdata(dtype=np.float32)
    if header_ref is None: header_ref=im
    if arr.shape!=header_ref.shape or not np.allclose(im.affine,header_ref.affine,atol=1e-5):
        raise RuntimeError(f'Spatial grid mismatch: {f}')
    if np.isinf(arr).any() or not np.isfinite(arr).all():
        raise RuntimeError(f'Nonfinite values in {f}')
    imgs.append(arr); ids.append(meta['participant_id'])
    qc.append({'participant_id':meta['participant_id'],'bytes':len(b),'sha256':sha,
               'nonzero_voxels':int(np.count_nonzero(arr)),
               'min':float(np.min(arr)),'max':float(np.max(arr)),
               'mean_nonzero':float(arr[arr!=0].mean())})
if len(imgs)!=54 or len(set(ids))!=54: raise RuntimeError('Expected 54 unique maps')
# Keep source table order and maps matched by ID.
order={pid:i for i,pid in enumerate(ids)}
participants['map_order']=participants.participant_id.map(order)
if participants.map_order.isna().any(): raise RuntimeError('Missing map for participant')
participants=participants.sort_values('map_order').reset_index(drop=True)
X=np.stack([imgs[i] for i in participants.map_order.astype(int)],axis=0)
# Zero represents outside the per-subject model mask. Require finite, nonzero map
# values in every participant so unsupported voxels are never treated as zero effects.
coverage=np.mean(X!=0,axis=0)
mask=coverage>=COVERAGE
if mask.sum()<10000: raise RuntimeError('Implausibly small common group mask')
Y=X[:,mask].astype(np.float64)
n,v=Y.shape
# One-sample group t model: mean participant cope > 0. Group effect is the mean
# participant cope; t tests whether its population mean differs from zero.
mean=Y.mean(axis=0); sd=Y.std(axis=0,ddof=1); se=sd/np.sqrt(n)
t_obs=mean/se
p_unc=stats.t.sf(t_obs,n-1)
# Random sign flips test the directional null using the maximum positive t over
# the complete group coverage mask. This controls voxelwise FWER at alpha=.05.
rng=np.random.default_rng(SEED)
max_null=np.empty(N_PERM,dtype=np.float32)
Y32=Y.astype(np.float32)
sumsq=np.sum(Y*Y,axis=0)
batch=32
for start in range(0,N_PERM,batch):
    m=min(batch,N_PERM-start)
    signs=rng.choice(np.array([-1.0,1.0],dtype=np.float32),size=(m,n))
    signed_sum=signs @ Y32
    # Algebraic one-sample t; sum of squares is invariant to sign changes.
    denom=np.maximum((sumsq[None,:]-(signed_sum*signed_sum)/n)/(n-1),1e-20)
    tperm=(signed_sum/ n)/np.sqrt(denom/n)
    max_null[start:start+m]=np.max(tperm,axis=1)
sorted_max=np.sort(max_null)
count_ge=N_PERM-np.searchsorted(sorted_max,t_obs,side='left')
p_fwe=(1+count_ge)/(N_PERM+1)
# Save full-brain unthresholded and FWE p maps (outside mask = 0).
def save_map(values,name,dtype=np.float32):
    z=np.zeros(mask.shape,dtype=dtype); z[mask]=values
    out=ROOT/'results'/name
    nib.save(nib.Nifti1Image(z,header_ref.affine,header_ref.header),out)
    return out
save_map(mean,'group_mean_cope.nii.gz')
save_map(t_obs,'group_t_positive.nii.gz')
save_map(p_fwe,'group_p_fwe_positive.nii.gz')
save_map((p_fwe<.05).astype(np.uint8),'group_sig_fwe_p05.nii.gz',np.uint8)

# Coordinate-defined a priori ROI, used only to localize and summarize vmPFC;
# it does not alter the whole-brain corrected primary test.
ijk=np.indices(mask.shape).reshape(3,-1).T
xyz=nib.affines.apply_affine(header_ref.affine,ijk)
roi3=((xyz[:,0]-ROI[0])**2+(xyz[:,1]-ROI[1])**2+(xyz[:,2]-ROI[2])**2)<=ROI_RADIUS**2
roi3=roi3.reshape(mask.shape)&mask
roi_nvox=int(roi3.sum())
if roi_nvox==0: raise RuntimeError('vmPFC ROI has no voxels in analysis mask')
roi_subject=np.array([arr[roi3].mean() for arr in X])
rmean=float(roi_subject.mean()); rsd=float(roi_subject.std(ddof=1)); rse=rsd/np.sqrt(n)
rt=float(rmean/rse); rp=float(stats.t.sf(rt,n-1))
rcI=stats.t.interval(.95,n-1,loc=rmean,scale=rse)
# ROI is summarized descriptively; the corrected whole-brain map is the primary test.

maxidx=int(np.argmax(t_obs)); coord=xyz[mask.ravel()][maxidx]
sig=p_fwe<.05
n_sig=int(sig.sum())
# Connected components summarize the spatial extent of individually FWE-significant voxels.
sigvol=np.zeros(mask.shape,dtype=bool); sigvol[mask]=sig
labels,nclusters=connected_components(sigvol,structure=np.ones((3,3,3),dtype=np.uint8))
cluster_rows=[]
for cluster_id in range(1,nclusters+1):
    vox_ijk=np.argwhere(labels==cluster_id); flat=np.ravel_multi_index(vox_ijk.T,mask.shape)
    vals=np.zeros(mask.shape); vals[mask]=t_obs; vals=vals[labels==cluster_id]
    peak_local=int(np.argmax(vals)); peak_xyz=nib.affines.apply_affine(header_ref.affine,vox_ijk[peak_local])
    cluster_rows.append({'cluster_id':cluster_id,'voxels':int(len(vox_ijk)),
        'peak_t':float(vals[peak_local]),'peak_mni_x':float(peak_xyz[0]),
        'peak_mni_y':float(peak_xyz[1]),'peak_mni_z':float(peak_xyz[2]),
        'peak_p_fwe':float(np.min(p_fwe[labels[mask]==cluster_id]))})
pd.DataFrame(cluster_rows).sort_values('voxels',ascending=False).to_csv(OUT/'fwe_clusters.csv',index=False)
summary={
 'n_participants':n,'n_excluded':0,'analysis_mask_voxels':int(v),
 'mask_definition':f'nonzero in all {n} maps',
 'coverage_min_in_mask':float(coverage[mask].min()),
 'coverage_median_in_mask':float(np.median(coverage[mask])),
 'n_perm':N_PERM,'seed':SEED,'direction':'positive one-sample group mean',
 'fwe_alpha':.05,'n_fwe_significant_voxels':n_sig,
 'max_t':float(t_obs[maxidx]),'max_t_mni_mm':[float(x) for x in coord],
 'max_t_p_uncorrected':float(p_unc[maxidx]),'max_t_p_fwe':float(p_fwe[maxidx]),
 'n_fwe_voxels_overlapping_vmPFC_sphere':int(np.sum((p_fwe<.05)&roi3[mask])),
 'roi_center_mni_mm':ROI,'roi_radius_mm':ROI_RADIUS,'roi_n_voxels':roi_nvox,
 'roi_mean_cope':rmean,'roi_sd_between_subjects':rsd,
 'roi_ci95_mean_cope':[float(rcI[0]),float(rcI[1])],
 
 'mean_age':float(participants.age.mean()),'sd_age':float(participants.age.std(ddof=1)),
 'gender_counts':participants.gender.value_counts().to_dict(),
 'mean_map_nonzero_voxels':float(np.mean([x['nonzero_voxels'] for x in qc])),
 'mean_vmPFC_value':float(np.mean(roi_subject)),
}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
pd.DataFrame(qc).to_csv(OUT/'map_qc.csv',index=False)
pd.DataFrame({'participant_id':participants.participant_id,'vmPFC_mean_cope':roi_subject}).to_csv(OUT/'vmPFC_participant_values.csv',index=False)
pd.DataFrame({'max_t_null':max_null}).to_csv(OUT/'permutation_max_t.csv',index=False)

# Figures use an anatomical template for orientation. Whole-brain voxelwise
# inference remains based on the predefined coverage mask, not this display image.
from nilearn import datasets
bg=datasets.load_mni152_template(resolution=2)
sigimg=nib.load(str(ROOT/'results/group_sig_fwe_p05.nii.gz'))
timg=nib.load(str(ROOT/'results/group_t_positive.nii.gz'))
roivol=np.zeros(mask.shape,np.uint8); roivol[roi3]=1
roi_img=nib.Nifti1Image(roivol,header_ref.affine)
# Corrected whole-brain result centered on its peak; vmPFC is separately displayed.
disp=plotting.plot_stat_map(sigimg,bg_img=bg,threshold=0.5,display_mode='ortho',
    cut_coords=tuple(float(x) for x in coord),
    colorbar=False,cmap='autumn',black_bg=False,draw_cross=True)
disp.title(f'Positive group effect: voxelwise FWE p < .05\npeak MNI {coord.round(1).tolist()}, max-T p={p_fwe[maxidx]:.4f}',size=13)
disp.savefig(FIG/'whole_brain_fwe.png',dpi=180); disp.close()
# vmPFC is identified with a prespecified coordinate sphere. Display its location
# on the unthresholded statistic map and report all corrected overlap (zero here).
disp=plotting.plot_stat_map(timg,bg_img=bg,threshold=2.0,display_mode='z',cut_coords=[-16,-10,-4],
    colorbar=True,cmap='cold_hot',black_bg=False,draw_cross=False)
disp.title('Group |t| > 2 shown; green contour = vmPFC sphere',size=14)
disp.add_contours(roi_img,levels=[0.5],colors=['lime'],linewidths=1.5)
disp.savefig(FIG/'vmPFC_unthresholded.png',dpi=180); disp.close()
# Per-participant vmPFC contrast estimates; mean and conventional t-based 95% CI.
fig,ax=plt.subplots(figsize=(5.2,4.2),layout='constrained')
ax.scatter(rng.normal(0,.045,n),roi_subject,s=28,alpha=.72,color='#2463a6',edgecolor='white',linewidth=.4)
ax.errorbar([0],[rmean],yerr=[[rmean-rcI[0]],[rcI[1]-rmean]],fmt='o',color='#bb3c2e',capsize=5,lw=2,label='Mean and 95% CI')
ax.axhline(0,color='black',lw=1); ax.set_xlim(-.3,.3); ax.set_xticks([0],['vmPFC (10-mm sphere)'])
ax.set_ylabel('Participant gain-effect cope'); ax.set_title('Descriptive vmPFC estimates')
ax.legend(frameon=False,loc='best',fontsize=8)
fig.savefig(FIG/'vmPFC_participant_values.png',dpi=180); plt.close(fig)
# Coverage and permutation null are quality/inference diagnostics.
fig,axs=plt.subplots(1,2,figsize=(9,3.5),layout='constrained')
axs[0].hist(coverage[mask],bins=np.arange(.89,1.011,.01),color='#6389aa',edgecolor='white')
axs[0].set(xlabel='Fraction of participants with nonzero estimate',ylabel='Voxels',title='Analysis-mask coverage')
axs[1].hist(max_null,bins=35,color='#6389aa',edgecolor='white')
axs[1].axvline(t_obs[maxidx],color='#b23a2b',label=f'Observed max t = {t_obs[maxidx]:.2f}')
axs[1].set(xlabel='Permutation maximum positive t',ylabel='Permutations',title='Whole-brain max-statistic null')
axs[1].legend(frameon=False,fontsize=8)
fig.savefig(FIG/'quality_and_null.png',dpi=180)
plt.close(fig)
print(json.dumps(summary,indent=2))
