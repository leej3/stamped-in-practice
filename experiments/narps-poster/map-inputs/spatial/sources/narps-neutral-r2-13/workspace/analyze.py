#!/usr/bin/env python3
"""Group inference for NARPS equal-indifference gain-effect maps.

Primary inference: one-sample, positive-direction sign-flip max-T permutation test.
Maps are participant parameter estimates (not t/z maps), so the group statistic
is formed from participant effects and variability. No first-level variance maps
are available for inverse-variance weighting.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
import matplotlib.pyplot as plt
from nilearn import plotting, datasets, image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
N_PERM = 10000
SEED = 20261016

participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
sources = json.loads((ROOT / "input/sources.json").read_text())
files = sorted((ROOT / "input/data").glob("*_hypo1_cope.nii.gz"))
by_id = {f.name.split("_")[0]: f for f in files}
assert len(files) == 54 and set(by_id) == set(participants.participant_id)
arrays=[]; ref=None
for pid in participants.participant_id:
    im=nib.load(str(by_id[pid]))
    expected=sources["files"][f"data/{by_id[pid].name}"]["sha256"]
    actual=hashlib.sha256(by_id[pid].read_bytes()).hexdigest()
    assert actual == expected, f"SHA256 mismatch for {by_id[pid].name}"
    if ref is None: ref=im
    assert im.shape == ref.shape and np.allclose(im.affine, ref.affine)
    arrays.append(im.get_fdata(dtype=np.float32))
data=np.stack(arrays) # participant x i x j x k
assert np.isfinite(data).all()
n=data.shape[0]
# Intersect a standard MNI brain mask with common map coverage to exclude
# extracerebral edge voxels and sparse image-boundary support.
coverage=np.mean(data != 0, axis=0)
brain=image.resample_to_img(datasets.load_mni152_brain_mask(),ref,interpolation="nearest").get_fdata()>0
mask=(coverage >= .90) & brain
X=data[:,mask].astype(np.float64)
v=X.shape[1]
if v < 10000: raise RuntimeError(f"Unexpectedly small analysis mask: {v}")

mean=X.mean(0)
sd=X.std(0,ddof=1)
t_classic=mean/(sd/np.sqrt(n))
# The RMS scale is invariant to participant sign flips, giving an exact
# sign-flip randomization test without near-zero sample-variance artifacts.
scale=np.sqrt(np.mean(X*X,axis=0))
t_obs=mean/(scale/np.sqrt(n))
p_unc=stats.t.sf(t_classic,n-1)

# Sign-flip permutation under a symmetric zero-centered null. The positive
# maximum RMS-standardized mean over every voxel on each sign flip provides one-sided whole-brain
# family-wise correction. Independent voxelwise sign flips are not used: each
# participant's full spatial map receives one shared sign per permutation.
rng=np.random.default_rng(SEED)
max_t=np.empty(N_PERM)
chunk=128
for lo in range(0,N_PERM,chunk):
    m=min(chunk,N_PERM-lo)
    signs=rng.choice(np.array([-1.,1.]), size=(m,n))
    sums=signs @ X
    t=sums / (scale[None,:]*np.sqrt(n))
    max_t[lo:lo+m]=np.max(t,axis=1)
p_fwe=(1+N_PERM-np.searchsorted(np.sort(max_t),t_obs,side="left"))/(N_PERM+1)

# Anatomical localization uses Harvard-Oxford cortical labels; this deliberately
# broad midline ventral-frontal mask is descriptive. Whole-brain max-T, not this
# ROI average, determines support for the hypothesis.
ho=datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
ho_img=image.resample_to_img(ho.maps,ref,interpolation="nearest")
ho_data=ho_img.get_fdata().astype(int)
ho_ids={name:i for i,name in enumerate(ho.labels)}
roi_names=["Frontal Medial Cortex","Subcallosal Cortex","Frontal Orbital Cortex","Cingulate Gyrus, anterior division"]
roi_ids=[ho_ids[x] for x in roi_names]
xyz=np.stack(np.meshgrid(*[np.arange(s) for s in ref.shape],indexing="ij"),axis=-1)
world=nib.affines.apply_affine(ref.affine,xyz.reshape(-1,3)).reshape(*ref.shape,3)
vmroi=np.isin(ho_data,roi_ids)&(np.abs(world[...,0])<=20)&(world[...,1]>=0)&(world[...,2]<=10)&mask
if vmroi.sum()==0: raise RuntimeError("vmPFC localization mask is empty")
roi_sub=data[:,vmroi].mean(axis=1)
roi_mean=float(roi_sub.mean()); roi_sd=float(roi_sub.std(ddof=1)); roi_se=roi_sd/np.sqrt(n)
roi_t=roi_mean/roi_se; roi_ci=stats.t.interval(.95,n-1,loc=roi_mean,scale=roi_se)
roi_result={"roi_definition":"Harvard-Oxford Frontal Medial, Subcallosal, Frontal Orbital, and anterior Cingulate labels; |x|<=20, y>=0, z<=10 mm; intersected with analysis mask",
            "atlas_labels":roi_names,"voxels":int(vmroi.sum()),"mean_participant_roi_effect":roi_mean,"sd_between_participants":roi_sd,
            "se":float(roi_se),"ci95":[float(x) for x in roi_ci],"t_df53":float(roi_t),"p_two_sided_descriptive":float(2*stats.t.sf(abs(roi_t),n-1)),
            "interpretation":"descriptive only; whole-brain corrected map is the confirmatory test"}
(OUT/"vmPFC_roi_summary.json").write_text(json.dumps(roi_result,indent=2))
pd.DataFrame({"participant_id":participants.participant_id,"vmPFC_roi_mean_effect":roi_sub}).to_csv(OUT/"participant_vmPFC_means.csv",index=False)

def unmask(vals, fill=0):
    a=np.full(ref.shape,fill,dtype=np.float32); a[mask]=vals.astype(np.float32); return a
def save_map(name, vals):
    nib.save(nib.Nifti1Image(unmask(vals),ref.affine,ref.header),OUT/name)
save_map("mean_effect.nii.gz",mean)
save_map("rms_standardized_stat.nii.gz",t_obs)
save_map("p_fwe_maxT.nii.gz",p_fwe)

# Participant-level global summary and ROI-independent QC.
global_mean=data[:,mask].mean(axis=1)
qc=pd.DataFrame({"participant_id":participants.participant_id,"mean_effect_in_mask":global_mean})
qc.to_csv(OUT/"participant_global_means.csv",index=False)

meta={"n_participants":int(n),"excluded":[],"checksum_validation":"all 54 source SHA256 values matched","mask_voxels":int(v),"mask_rule":"resampled MNI152 brain mask AND nonzero cope in >=90% participants",
      "mask_fraction_of_grid":float(mask.mean()),"grid_shape":list(ref.shape),"voxel_sizes_mm":list(nib.affines.voxel_sizes(ref.affine)),
      "n_permutations":N_PERM,"seed":SEED,"direction":"positive one-sided","primary_correction":"sign-flip permutation maximum RMS-standardized mean, whole analysis mask, FWE p<.05",
      "min_max_t":float(max_t.min()),"max_max_t":float(max_t.max()),"mean_mask_effect":float(mean.mean()),
      "median_mask_effect":float(np.median(mean)),"n_fwe_voxels":int(np.sum(p_fwe<.05)),"peak_t_classic":float(np.max(t_classic)),"peak_permutation_stat":float(np.max(t_obs)),
      "min_classic_one_sided_p":float(np.min(p_unc)),"n_classic_bonferroni_voxels":int(np.sum(p_unc<.05/v)),
      "peak_mni_mm":[float(x) for x in nib.affines.apply_affine(ref.affine,np.array(np.unravel_index(np.argmax(unmask(t_obs)),ref.shape)))],
      "peak_p_fwe":float(p_fwe[np.argmax(t_obs)]),"min_p_fwe":float(p_fwe.min()),"permutation_p_min_resolution":1/(N_PERM+1),
      "global_mean_effect_mean":float(global_mean.mean()),"global_mean_effect_sd":float(global_mean.std(ddof=1)),
      "age_mean":float(participants.age.mean()),"age_sd":float(participants.age.std(ddof=1)),"gender_counts":participants.gender.value_counts().to_dict()}
(OUT/"summary.json").write_text(json.dumps(meta,indent=2))

# Tabulate clusters of positive max-T corrected voxels, if any.
from scipy.ndimage import label
sig=(unmask((p_fwe<.05).astype(float))>0)
lab,nlab=label(sig, structure=np.ones((3,3,3)))
cl=[]
for k in range(1,nlab+1):
    vox=np.argwhere(lab==k); idx=np.unravel_index(np.argmax(unmask(t_obs)*(lab==k)),ref.shape)
    cxyz=nib.affines.apply_affine(ref.affine,idx); at=ho_data[idx]
    cl.append({"cluster":k,"voxels":len(vox),"peak_stat":float(unmask(t_obs)[idx]),"peak_mni_mm":[float(x) for x in cxyz],"atlas_label":ho.labels[int(at)],"peak_p_fwe":float(unmask(p_fwe)[idx])})
pd.DataFrame(cl,columns=["cluster","voxels","peak_stat","peak_mni_mm","atlas_label","peak_p_fwe"]).to_csv(OUT/"corrected_clusters.csv",index=False)

# Summary visualization; cyan contour marks whole-brain permutation FWE.
mean_img=nib.Nifti1Image(unmask(mean),ref.affine)
timg=nib.Nifti1Image(unmask(t_obs),ref.affine)
pfwe_img=nib.Nifti1Image(unmask(-np.log10(p_fwe)),ref.affine)
bg=image.resample_to_img(datasets.load_mni152_template(),ref,interpolation="continuous")
fig=plt.figure(figsize=(12,7))
disp=plotting.plot_stat_map(timg,bg_img=bg,display_mode="z",cut_coords=[-8,0,8,16,24],threshold=2,
    title="Positive gain effect: RMS-standardized group statistic (cyan = whole-brain FWE)",cmap="cold_hot",colorbar=True,figure=fig)
if sig.any(): disp.add_contours(nib.Nifti1Image(sig.astype(np.uint8),ref.affine),levels=[.5],colors="cyan",linewidths=1.6)
fig.savefig(FIG/"whole_brain_t_and_fwe.png",dpi=180,bbox_inches="tight"); plt.close(fig)

fig=plt.figure(figsize=(12,7))
plotting.plot_stat_map(mean_img,bg_img=bg,display_mode="z",cut_coords=[-8,0,8,16,24],threshold=0,
    title="Mean participant gain-effect estimate (arbitrary model units)",cmap="cold_hot",colorbar=True,figure=fig)
fig.savefig(FIG/"mean_gain_effect.png",dpi=180,bbox_inches="tight"); plt.close(fig)

fig,ax=plt.subplots(figsize=(8,4.5))
ax.hist(global_mean,bins=12,color="#4c78a8",edgecolor="white")
ax.axvline(0,color="black",lw=1)
ax.set(xlabel="Participant mean cope across common-coverage mask",ylabel="Participants",title="Participant-level global effect summary (QC only)")
fig.tight_layout(); fig.savefig(FIG/"participant_global_means.png",dpi=180); plt.close(fig)

fig,ax=plt.subplots(figsize=(8,4.5))
ax.scatter(np.arange(1,n+1),roi_sub,s=22,alpha=.75,color="#4c78a8",edgecolor="white",linewidth=.3)
ax.axhline(0,color="black",lw=1)
ax.axhline(roi_mean,color="#d62728",lw=2,label="Mean")
ax.axhspan(roi_ci[0],roi_ci[1],color="#d62728",alpha=.12,label="95% CI")
ax.set(xlabel="Participant (roster order)",ylabel="Mean vmPFC ROI gain-effect estimate",title="Descriptive vmPFC ROI effects")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(FIG/"vmPFC_roi_effects.png",dpi=180); plt.close(fig)

print(json.dumps(meta,indent=2))
