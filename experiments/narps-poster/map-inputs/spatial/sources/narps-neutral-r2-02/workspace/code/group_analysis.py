#!/usr/bin/env python3
"""Group inference for fixed NARPS AO86 equal-indifference gain-effect maps."""
from __future__ import annotations
import hashlib, json, os, platform, sys
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy.ndimage import label
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from nilearn import plotting

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
SEED = 20261016
N_PERM = 10000
ROI_CENTER = np.array([0., 40., -8.])
ROI_RADIUS_MM = 10.

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def get_coords(img):
    ijk=np.indices(img.shape, dtype=np.float32).reshape(3,-1).T
    return nib.affines.apply_affine(img.affine, ijk)

def tstat_sums(sums, sumsq, n):
    # One-sample t computed from the signed sum; sumsq is invariant to sign flips.
    centered=np.maximum(sumsq - sums*sums/n, 0.)
    return (sums / n) / np.sqrt((centered/(n-1))/n + 1e-30)

meta=pd.read_csv(ROOT/'input/participants.tsv', sep='\t')
sources=json.loads((ROOT/'input/sources.json').read_text())
files=sources['files']
ids=meta.participant_id.tolist()
assert len(ids)==54 and len(set(ids))==54 and set(meta.group)=={'equalIndifference'}
assert len([k for k in files if k.endswith('.nii.gz')])==54
images=[]; qc=[]
ref=None
for pid in ids:
    rel=f'data/{pid}_hypo1_cope.nii.gz'
    info=files[rel]
    path=ROOT/'input'/rel
    assert path.exists(), f'missing map {path}'
    digest=sha256(path)
    assert digest==info['sha256'], (pid,digest,info['sha256'])
    assert path.stat().st_size==info['bytes']
    img=nib.load(path)
    arr=img.get_fdata(dtype=np.float32)
    if ref is None: ref=img
    assert img.shape==ref.shape and np.allclose(img.affine,ref.affine,atol=1e-5)
    assert img.header.get_xyzt_units()==ref.header.get_xyzt_units()
    assert np.isfinite(arr).all()
    images.append(arr)
    qc.append({'participant_id':pid,'bytes':path.stat().st_size,'sha256':digest,
               'finite_fraction':float(np.isfinite(arr).mean()),'nonzero_voxels':int(np.count_nonzero(arr)),
               'mean_nonzero':float(arr[arr!=0].mean()),'sd_nonzero':float(arr[arr!=0].std(ddof=1))})
X=np.stack(images,axis=0)
assert X.shape[0]==len(meta)==54
# Since input is a contrast map with exact zero outside coverage, define common support by
# observed nonzero frequency threshold, and report stricter-support sensitivity.
nonzero=(X!=0)
mask90=nonzero.mean(axis=0)>=.90
mask95=nonzero.mean(axis=0)>=.95
assert mask90.sum()>0 and mask95.sum()>0
coords=get_coords(ref).reshape(*ref.shape,3)
roi=(np.linalg.norm(coords-ROI_CENTER,axis=-1)<=ROI_RADIUS_MM)
roi90=roi & mask90
assert roi90.sum()>0

# Primary one-sample, positive-mean max-T sign-flip test over all voxels in common support.
# Matrix multiplication batches keep the full 10,000 x voxel null distribution out of memory.
Y=X[:,mask90].astype(np.float64)
n,v=Y.shape
sumsq=np.einsum('ij,ij->j',Y,Y)
obs_sum=Y.sum(axis=0)
tobs=tstat_sums(obs_sum,sumsq,n)
obs_max=float(np.max(tobs))
rng=np.random.default_rng(SEED)
B=N_PERM
max90=np.empty(B,dtype=np.float32)
batch=100
for start in range(0,B,batch):
    k=min(batch,B-start)
    signs=rng.choice(np.array([-1.,1.]),size=(k,n))
    perm_sum=signs @ Y
    # Explicit observed arrangement is separately included in p-value formula below.
    tperm=tstat_sums(perm_sum,sumsq[None,:],n)
    max90[start:start+k]=np.max(tperm,axis=1)
p_fwe=(1+np.count_nonzero(max90>=obs_max))/(B+1)
# Per-voxel max-T adjusted p values for displaying corrected evidence.
# p-adjusted map uses same sign-flip max distribution.
padj=np.array([(1+np.count_nonzero(max90>=t))/(B+1) for t in tobs],dtype=np.float32)

# Strict support sensitivity repeats the identical random sign assignments with the same seed.
Y95=X[:,mask95].astype(np.float64); sumsq95=np.einsum('ij,ij->j',Y95,Y95)
t95=tstat_sums(Y95.sum(axis=0),sumsq95,n); obsmax95=float(t95.max())
rng95=np.random.default_rng(SEED)
max95=np.empty(B,dtype=np.float32)
for start in range(0,B,batch):
    k=min(batch,B-start); signs=rng95.choice(np.array([-1.,1.]),size=(k,n))
    max95[start:start+k]=np.max(tstat_sums(signs @ Y95,sumsq95[None,:],n),axis=1)
p_fwe95=(1+np.count_nonzero(max95>=obsmax95))/(B+1)

# Descriptive prespecified coordinate-sphere summary. This is not the confirmatory test.
roi_values=X[:,roi90].mean(axis=1)
roi_mean=float(roi_values.mean()); roi_sd=float(roi_values.std(ddof=1)); roi_se=roi_sd/np.sqrt(n)
roi_ci=stats.t.interval(.95,df=n-1,loc=roi_mean,scale=roi_se)
roi_t,roi_p2=stats.ttest_1samp(roi_values,0)
roi_p1=float(stats.t.sf(roi_t,n-1))

# Numerical check against SciPy on preselected voxels (independent implementation).
check_ix=np.linspace(0,v-1,min(40,v),dtype=int)
check=stats.ttest_1samp(Y[:,check_ix],0,axis=0).statistic
assert np.allclose(check,tobs[check_ix],rtol=1e-9,atol=1e-9)
# Validate computed sign-flip statistics for a small set of fixed random patterns.
small_signs=np.array([[1]*n,[-1]*n]+[np.random.default_rng(SEED+i).choice([-1.,1.],n) for i in range(8)])
small_sum=small_signs @ Y[:,check_ix]
small_t=tstat_sums(small_sum,sumsq[check_ix][None,:],n)
for i in range(len(small_signs)):
    assert np.allclose(small_t[i],stats.ttest_1samp(Y[:,check_ix]*small_signs[i,:,None],0,axis=0).statistic,rtol=1e-9,atol=1e-9)

# Write maps on source grid.
def save_map(data, mask, filename, dtype=np.float32, outside=0.):
    out=np.full(ref.shape,outside,dtype=dtype); out[mask]=data
    nib.save(nib.Nifti1Image(out,ref.affine),OUT/filename)
save_map(X.mean(axis=0)[mask90],mask90,'group_mean_gain_effect.nii.gz')
save_map(tobs,mask90,'group_t_positive.nii.gz')
save_map(padj,mask90,'group_maxT_p_fwe.nii.gz',outside=1.)
# Check that derived NIfTI outputs preserve numeric values and out-of-mask p=1.
written_p=nib.load(OUT/'group_maxT_p_fwe.nii.gz').get_fdata(dtype=np.float32)
assert np.count_nonzero(written_p<=.05)==int(np.count_nonzero(padj<=.05))
assert np.allclose(written_p[mask90],padj,rtol=1e-6,atol=1e-7) and np.all(written_p[~mask90]==1.)

# Cluster description for voxels surviving whole-brain corrected alpha=.05.
sig=mask90.copy(); sig[mask90]=padj<=.05
labels,ncl=label(sig)
clusters=[]
flat_to_mask_index={int(q):i for i,q in enumerate(np.flatnonzero(mask90))}
for c in range(1,ncl+1):
    ijk=np.argwhere(labels==c)
    if len(ijk)==0: continue
    # Coordinates from affine; peak selected by the observed t map.
    peak_idx=ijk[np.argmax([tobs[flat_to_mask_index[int(np.ravel_multi_index(tuple(q),ref.shape))]] for q in ijk])]
    clusters.append({'cluster_id':int(c),'voxels_6connected':int(len(ijk)),
                     'peak_ijk':peak_idx.tolist(),'peak_mni_mm':[float(q) for q in nib.affines.apply_affine(ref.affine,peak_idx)],
                     'overlaps_vmPFC_sphere':bool(np.any(roi[tuple(ijk.T)]))})

# Result table, detailed QC and machine-readable run metadata.
pd.DataFrame(qc).to_csv(OUT/'participant_qc.tsv',sep='\t',index=False)
summary={
 'analysis':'one-sample positive-mean max-T sign-flip permutation test',
 'n_participants':n,'participant_ids':ids,'exclusions':[],'missing_maps':0,
 'map_shape':list(ref.shape),'affine':ref.affine.tolist(),'spatial_units':list(ref.header.get_xyzt_units()),
 'voxel_sizes_mm':list(ref.header.get_zooms()[:3]),'mask_rule':'map nonzero in >=90% participants',
 'mask90_voxels':int(mask90.sum()),'mask95_voxels':int(mask95.sum()),
 'vmPFC_operationalization':{'shape':'10 mm radius sphere','center_MNI_mm':ROI_CENTER.tolist(),'voxels_in_mask90':int(roi90.sum()),'descriptive_only':True},
 'seed':SEED,'permutations':B,'p_resolution':1/(B+1),'alpha':.05,
 'positive_max_t_observed':obs_max,'whole_brain_fwe_p_global':float(p_fwe),
 'maxT_significant_voxels_alpha_0.05':int(np.count_nonzero(padj<=.05)),
 'strict_mask95':{'observed_max_t':obsmax95,'whole_brain_fwe_p_global':float(p_fwe95),'voxels':int(mask95.sum())},
 'vmPFC_descriptive':{'mean':roi_mean,'sd_between_participants':roi_sd,'se':roi_se,'ci95_t':list(map(float,roi_ci)),
                     't':float(roi_t),'p_one_sided_uncorrected':roi_p1,'p_two_sided_uncorrected':float(roi_p2),
                     'participants_above_zero':int((roi_values>0).sum())},
 'clusters_fwe05':clusters,
 'validation':{'scipy_t_stat_check_voxels':int(len(check_ix)),'signflip_reference_checks':int(len(small_signs)*len(check_ix)),
               'derived_nifti_scaling_check':True,'checks_passed':True},
 'input_sha256':{x['participant_id']:x['sha256'] for x in qc},
 'environment':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':__import__('scipy').__version__,
                'pandas':pd.__version__,'nibabel':nib.__version__,'nilearn':__import__('nilearn').__version__,
                'matplotlib':matplotlib.__version__}
}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,default=lambda x: x.item() if isinstance(x,np.generic) else (x.tolist() if isinstance(x,np.ndarray) else str(x)))+'\n')
pd.DataFrame({'participant_id':ids,'vmPFC_mean_gain_effect':roi_values}).to_csv(OUT/'vmPFC_participant_values.tsv',sep='\t',index=False)

# Figure 1: individual ROI means and mean CI, transparent that this summary is uncorrected/descriptive.
fig,ax=plt.subplots(figsize=(7.2,4.6))
ax.scatter(np.arange(1,n+1),roi_values,s=24,color='#2369a1',alpha=.8,edgecolor='white',linewidth=.3)
ax.axhline(0,color='black',lw=1)
ax.axhline(roi_mean,color='#c43b34',lw=2,label=f'Mean {roi_mean:.3f}; 95% CI [{roi_ci[0]:.3f}, {roi_ci[1]:.3f}]')
ax.fill_between([0,n+1],roi_ci[0],roi_ci[1],color='#c43b34',alpha=.12)
ax.set(xlim=(0,n+1),xlabel='Participant (ordered by ID)',ylabel='Mean upstream gain-effect coefficient in vmPFC sphere',title='Participant-level estimates in the coordinate-defined vmPFC sphere')
ax.legend(frameon=False,loc='best'); fig.tight_layout(); fig.savefig(FIG/'vmPFC_participant_estimates.png',dpi=180); plt.close(fig)

# Figure 2: display only voxels passing max-T whole-brain FWE, in -log10(p) units.
p_img=nib.load(OUT/'group_maxT_p_fwe.nii.gz')
p_data=p_img.get_fdata(dtype=np.float32)
logp=np.zeros(p_data.shape,dtype=np.float32)
sig_p=(p_data<=.05)
logp[sig_p]=-np.log10(p_data[sig_p])
logp_img=nib.Nifti1Image(logp,p_img.affine)
nib.save(logp_img,OUT/'group_log10_fwe_p_significant.nii.gz')
display=plotting.plot_stat_map(logp_img,display_mode='ortho',cut_coords=(-26,-102,-4),
    threshold=-np.log10(.05),title='Whole-brain max-T FWE-significant voxels (−log10 p)',
    colorbar=True,cmap='hot',vmin=-np.log10(.05),vmax=max(2.,float(logp.max())))
display.savefig(FIG/'whole_brain_group_results.png',dpi=180)
print(json.dumps({k:summary[k] for k in ['n_participants','mask90_voxels','positive_max_t_observed','whole_brain_fwe_p_global','maxT_significant_voxels_alpha_0.05','strict_mask95','vmPFC_descriptive','environment']},indent=2))
