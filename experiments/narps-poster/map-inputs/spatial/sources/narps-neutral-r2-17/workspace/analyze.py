#!/usr/bin/env python3
"""Reproducible NARPS AO86 equal-indifference group analysis."""
from pathlib import Path
import json, hashlib, platform
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'input' / 'data'
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
N_PERM = 5000
SEED = 20261016

participants = pd.read_csv(ROOT/'input/participants.tsv', sep='\t')
source_meta = json.loads((ROOT/'input/sources.json').read_text())
files = sorted(DATA.glob('sub-*_hypo1_cope.nii.gz'))
assert len(files) == len(participants) == 54
ids = [f.name.split('_')[0] for f in files]
assert ids == sorted(participants.participant_id.tolist())
checksum_ok = {}
for f in files:
    expected = source_meta['files'][f.relative_to(ROOT/'input').as_posix()]['sha256']
    checksum_ok[f.name] = hashlib.sha256(f.read_bytes()).hexdigest() == expected
assert all(checksum_ok.values()), 'Input map checksum mismatch'
imgs = [nib.load(str(f)) for f in files]
ref = imgs[0]
assert all(im.shape == ref.shape and np.allclose(im.affine, ref.affine) for im in imgs)
arr = np.stack([im.get_fdata(dtype=np.float32) for im in imgs])
finite = np.isfinite(arr)
nonzero = finite & (arr != 0)
# Retain the shared brain support: a voxel must have an estimate in >=90% of participants.
mask = (nonzero.mean(axis=0) >= .90) & finite.all(axis=0)
Y = arr[:, mask].astype(np.float64)
n, v = Y.shape
assert n == 54 and v > 1000

# One-sample t-test of the group mean coefficient against zero.
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
se = sd / np.sqrt(n)
tobs = np.divide(mean, se, out=np.zeros_like(mean), where=se > 0)
df = n - 1
p_unc = stats.t.sf(tobs, df)

# One-sided max-t sign-flip permutation test. Sign flips test the sharp null under
# exchangeable, symmetric participant-level errors; max statistic controls FWE.
rng = np.random.default_rng(SEED)
max_null = np.empty(N_PERM, dtype=np.float32)
sum_sq = np.sum(Y*Y, axis=0)
chunk = 100
for start in range(0, N_PERM, chunk):
    m = min(chunk, N_PERM-start)
    signs = rng.choice(np.array([-1., 1.], dtype=np.float64), size=(m,n))
    sums = signs @ Y
    perm_mean = sums/n
    var = np.maximum((sum_sq[None,:] - sums*sums/n)/(n-1), 0.)
    perm_t = np.divide(perm_mean, np.sqrt(var/n), out=np.zeros_like(perm_mean), where=var>0)
    max_null[start:start+m] = np.max(perm_t, axis=1)
    if (start+m) % 1000 == 0: print(f'permutations {start+m}/{N_PERM}', flush=True)
p_fwe = (1 + (max_null[:,None] >= tobs[None,:]).sum(axis=0))/(N_PERM+1)
sig = p_fwe < .05

# Anatomical vmPFC search region specified in MNI coordinates before inspecting results.
# Bilateral medial prefrontal territory: |x|<=15, y=25..65, z=-15..5 mm.
ijk = np.array(np.where(mask)).T
xyz = nib.affines.apply_affine(ref.affine, ijk)
vm = (np.abs(xyz[:,0]) <= 15) & (xyz[:,1] >= 25) & (xyz[:,1] <= 65) & (xyz[:,2] >= -15) & (xyz[:,2] <= 5)
vm_t = tobs[vm]; vm_mean = mean[vm]; vm_punc = p_unc[vm]; vm_pfwe = p_fwe[vm]

def save_map(values, name, dtype=np.float32):
    full = np.zeros(ref.shape, dtype=dtype); full[mask] = values
    hdr = ref.header.copy(); hdr.set_data_dtype(dtype)
    nib.save(nib.Nifti1Image(full, ref.affine, hdr), OUT/name)

save_map(mean, 'group_mean.nii.gz')
save_map(tobs, 'group_t.nii.gz')
save_map(p_fwe, 'p_fwe_maxT.nii.gz')
save_map(sig.astype(np.uint8), 'significant_fwe05.nii.gz', np.uint8)
save_map(vm.astype(np.uint8), 'vmPFC_mask.nii.gz', np.uint8)

# Group-level QC and subject summaries.
subject_mean = Y.mean(axis=1)
subject_sd = Y.std(axis=1, ddof=1)
qc = pd.DataFrame({'participant_id':ids, 'mean_in_mask':subject_mean, 'sd_in_mask':subject_sd,
                   'finite_fraction':finite.mean(axis=(1,2,3)), 'nonzero_fraction':nonzero.mean(axis=(1,2,3))})
qc.to_csv(OUT/'participant_qc.tsv', sep='\t', index=False)

# Corrected cluster summaries: connected components on the 3D volume.
from scipy.ndimage import label
sigvol = np.zeros(ref.shape, bool); sigvol[mask] = sig
labs, nlab = label(sigvol)
clusters=[]
for lab in range(1,nlab+1):
    vox = np.array(np.where(labs==lab)).T
    coords = nib.affines.apply_affine(ref.affine, vox)
    cluster_mask = labs[tuple(vox.T)] == lab
    # Index back into compressed analysis vector through full index -> flat mapping.
    fidx=np.ravel_multi_index(vox.T, ref.shape)
    lookup=np.full(np.prod(ref.shape),-1,dtype=np.int64); lookup[np.ravel_multi_index(ijk.T,ref.shape)]=np.arange(v)
    ix=lookup[fidx]; ix=ix[ix>=0]
    peak=ix[np.argmax(tobs[ix])]
    peakxyz=xyz[peak]
    clusters.append({'voxels':int(len(vox)), 'volume_mm3':float(len(vox)*abs(np.linalg.det(ref.affine[:3,:3]))),
      'peak_t':float(tobs[peak]), 'peak_p_fwe':float(p_fwe[peak]),
      'peak_mni_x':float(peakxyz[0]), 'peak_mni_y':float(peakxyz[1]), 'peak_mni_z':float(peakxyz[2]),
      'intersects_vmPFC':bool(np.any(vm[ np.isin(np.arange(v),ix) ])) if False else bool(np.any((np.abs(coords[:,0])<=15)&(coords[:,1]>=25)&(coords[:,1]<=65)&(coords[:,2]>=-15)&(coords[:,2]<=5)))})
clusters.sort(key=lambda c:c['peak_t'], reverse=True)

roi_subject_means = Y[:,vm].mean(axis=1)
roi_stat=stats.ttest_1samp(roi_subject_means, 0, alternative='greater')
roi_n=int(vm.sum())
roi_se=float(roi_subject_means.std(ddof=1)/np.sqrt(n))
roi_ci=stats.t.interval(.95, df, loc=float(roi_subject_means.mean()), scale=roi_se)
result={
 'n_participants':n,'n_voxels':int(v),'voxel_size_mm':list(map(float,ref.header.get_zooms()[:3])),
 'mask_rule':'finite and nonzero in at least 90% of the 54 participant maps',
 'model':'one-sample group mean of participant gain-effect estimates vs 0; one-sided positive test',
 'whole_brain_inference':{'method':'5,000 participant sign-flips; one-sided maximum t statistic; voxelwise FWE p<.05', 'seed':SEED,
    'maxT_95_threshold':float(np.quantile(max_null,.95)), 'significant_voxels':int(sig.sum()), 'max_t_observed':float(tobs.max()),
    'smallest_fwe_p':float(p_fwe.min()), 'max_null_p_for_peak':float((1+(max_null>=tobs.max()).sum())/(N_PERM+1))},
 'vmPFC_definition':'a priori MNI box: |x|<=15, y=25..65, z=-15..5 mm',
 'vmPFC':{'voxels':roi_n,'mean_coefficient':float(roi_subject_means.mean()),'sd_across_participants_roi_average':float(roi_subject_means.std(ddof=1)),
   'se_across_participants_of_roi_average':roi_se,'ci95_t':list(map(float,roi_ci)),
   'one_sided_roi_average_t':float(roi_stat.statistic),'one_sided_roi_average_p_uncorrected':float(roi_stat.pvalue),
   'mean_voxelwise_t':float(np.mean(vm_t)),'max_voxel_t':float(np.max(vm_t)),
   'fwe_significant_voxels':int(np.sum(vm_pfwe<.05)), 'max_voxel_fwe_p':float(np.min(vm_pfwe))},
 'clusters':clusters,
 'quality':{'map_count':len(files),'excluded_participants':[],'any_nonfinite_values':bool(not finite.all()),
   'all_map_sha256_checksums_match_sources_json':bool(all(checksum_ok.values())),
   'finite_fraction_min':float(finite.mean(axis=(1,2,3)).min()),'zero_fraction_range':[float(nonzero.mean(axis=(1,2,3)).min()),float(nonzero.mean(axis=(1,2,3)).max())],
   'participant_in_mask_mean_range':[float(subject_mean.min()),float(subject_mean.max())]},
 'software':{'python':platform.python_version(),'numpy':np.__version__,'nibabel':nib.__version__,'scipy':__import__('scipy').__version__,'pandas':pd.__version__},
 'caveat':'Group mean inference treats participant estimates as equally precise; participant variance maps were unavailable.'
}
(OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')

# Figure 1: mean effect map and a priori vmPFC outline on three orthogonal slices.
meanvol=np.zeros(ref.shape); meanvol[mask]=mean
vmvol=np.zeros(ref.shape,bool); vmvol[tuple(ijk[vm].T)]=True
fig,axs=plt.subplots(1,3,figsize=(12,4.2))
coords=[(0,1,0,'Sagittal (x=0)'),(1,1,0,'Coronal (y=45)'),(2,1,0,'Axial (z=0)')]
for ax,(axis,_,__,title) in zip(axs,coords):
    # nearest index to requested MNI coordinate
    target=[0,45,0][axis]; inv=nib.affines.apply_affine(np.linalg.inv(ref.affine), [target,0,0] if axis==0 else ([0,target,0] if axis==1 else [0,0,target]))
    sl=int(round(inv[axis])); data=np.take(meanvol,sl,axis=axis).T; roi=np.take(vmvol,sl,axis=axis).T
    im=ax.imshow(data, origin='lower', cmap='RdBu_r', norm=TwoSlopeNorm(vmin=-.15,vcenter=0,vmax=.15), interpolation='nearest')
    ax.contour(roi.astype(float), levels=[.5], colors='black', linewidths=.8)
    ax.set_title(title); ax.axis('off')
fig.suptitle('Mean participant gain-effect coefficient; black outline = prespecified vmPFC region',fontsize=11)
fig.colorbar(im, ax=axs, shrink=.68, label='Mean coefficient (input scale)')
fig.tight_layout(); fig.savefig(FIG/'group_mean_and_vmPFC.png',dpi=180,bbox_inches='tight'); plt.close(fig)

# Figure 3: inferential map at the maximum-statistic FWE threshold.
tvol=np.zeros(ref.shape); tvol[mask]=tobs
fig,axs=plt.subplots(1,3,figsize=(12,4.2))
for ax,(axis,title,target) in zip(axs,[(0,'Sagittal (x=0)',0),(1,'Coronal (y=45)',45),(2,'Axial (z=0)',0)]):
    world=[0,0,0]; world[axis]=target
    sl=int(round(nib.affines.apply_affine(np.linalg.inv(ref.affine),world)[axis]))
    data=np.take(tvol,sl,axis=axis).T
    sigslice=np.take(sigvol,sl,axis=axis).T
    im=ax.imshow(data,origin='lower',cmap='magma',vmin=0,vmax=6.7,interpolation='nearest')
    ax.contour(sigslice.astype(float),levels=[.5],colors='#29e6d8',linewidths=1.2)
    ax.set_title(title); ax.axis('off')
fig.suptitle('Positive group t map; cyan outline = whole-brain max-t FWE p<.05',fontsize=11)
fig.colorbar(im, ax=axs, shrink=.68, label='One-sample t statistic')
fig.tight_layout(); fig.savefig(FIG/'whole_brain_fwe.png',dpi=180,bbox_inches='tight'); plt.close(fig)

# Figure 2: participant-level ROI average estimates, plus distribution and corrected evidence.
roi_subject=np.mean(arr[:, mask],axis=1) # whole analyzed brain average, for QC only
# Per-participant mean within the predefined ROI using the voxel order above.
roi_sub=roi_subject_means
fig,axs=plt.subplots(1,2,figsize=(9,4))
axs[0].scatter(np.arange(n)+1,roi_sub,s=18,color='#315a7d',alpha=.8)
axs[0].axhline(0,color='black',lw=.8); axs[0].axhline(roi_sub.mean(),color='#c44739',lw=1.5)
axs[0].set(xlabel='Participant (input order)',ylabel='Mean coefficient in vmPFC box',title='Participant ROI averages')
axs[1].hist(vm_t,bins=30,color='#779db7',edgecolor='white')
axs[1].axvline(0,color='black',lw=.8); axs[1].set(xlabel='Voxelwise one-sample t statistic',ylabel='Voxel count',title='vmPFC voxelwise statistics')
fig.tight_layout(); fig.savefig(FIG/'vmPFC_estimates.png',dpi=180,bbox_inches='tight'); plt.close(fig)
print(json.dumps(result,indent=2))
