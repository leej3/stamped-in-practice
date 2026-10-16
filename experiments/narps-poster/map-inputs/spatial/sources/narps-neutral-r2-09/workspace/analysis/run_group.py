#!/usr/bin/env python3
"""Reproducible group analysis of the supplied NARPS AO86 gain cope maps."""
from __future__ import annotations
import hashlib, json, platform, sys
from pathlib import Path

import nibabel as nib
import nilearn
from nilearn import datasets, image, plotting
import numpy as np
import pandas as pd
import scipy
from scipy import stats
from scipy import ndimage
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
N_PERM = 9999
SEED = 20261016
ALPHA = .05
CHUNK = 10000

sources = json.loads((IN / "sources.json").read_text())
participants = pd.read_csv(IN / "participants.tsv", sep="\t")
if participants.participant_id.duplicated().any(): raise ValueError("Duplicate participant IDs")
if participants.participant_id.isna().any() or participants.group.isna().any(): raise ValueError("Missing cohort metadata")
if not (participants.group == "equalIndifference").all(): raise ValueError("Unexpected participant group")
expected = sorted(participants.participant_id.tolist())
files = {p: IN / "data" / f"{p}_hypo1_cope.nii.gz" for p in expected}
qc=[]; data=[]; ref=None; mask_stack=[]
for pid in expected:
    path=files[pid]
    if not path.exists(): raise FileNotFoundError(path)
    item=sources["files"][f"data/{path.name}"]
    h=hashlib.sha256(path.read_bytes()).hexdigest()
    if h != item["sha256"]: raise ValueError(f"SHA256 mismatch: {pid}")
    img=nib.load(path)
    if ref is None: ref=img
    if img.shape != ref.shape or not np.allclose(img.affine, ref.affine, atol=1e-5):
        raise ValueError(f"Geometry mismatch: {pid}")
    a=img.get_fdata(dtype=np.float32)
    finite=np.isfinite(a)
    if not finite.all(): raise ValueError(f"Non-finite values: {pid}")
    # Upstream cope images have exactly-zero values outside the fitted support.
    support=(a != 0)
    data.append(a)
    mask_stack.append(support)
    nz=a[support]
    qc.append({"participant_id":pid,"sha256":h,"n_nonzero_support":int(support.sum()),
               "mean_nonzero":float(nz.mean()),"sd_nonzero":float(nz.std(ddof=1)),
               "min":float(a.min()),"max":float(a.max()),"finite":bool(finite.all())})
X4=np.stack(data).astype(np.float32)
S=np.stack(mask_stack)
mask=S.all(axis=0)
if int(mask.sum()) < 1000: raise ValueError("Unexpectedly small common-support mask")
X=X4[:,mask].astype(np.float64)
n,p=X.shape
if n != 54: raise ValueError(f"Expected 54 participants, found {n}")

# Descriptive one-sample OLS / t statistic.
mean=X.mean(axis=0)
sd=X.std(axis=0,ddof=1)
tobs=mean/(sd/np.sqrt(n))
p_unc=stats.t.sf(tobs,n-1)

# Sign-flip maximum-t familywise correction. Sum of squares is invariant to sign flips.
rng=np.random.default_rng(SEED)
signs=rng.choice(np.array([-1.,1.]),size=(N_PERM,n))
# Avoid identity row (the observed sign pattern is assessed separately).
signs[0,:]=-1.
max_null=np.full(N_PERM,-np.inf,dtype=np.float64)
sumsq=np.einsum('ij,ij->j',X,X)
# Check the sign-flip statistic against the conventional t statistic before
# permutations; this guards the scale used for maximum-statistic inference.
all_positive_t=X.sum(axis=0)*np.sqrt(n-1)/np.sqrt(np.maximum(n*sumsq-X.sum(axis=0)**2,1e-30))
if not np.allclose(all_positive_t,tobs,rtol=1e-9,atol=1e-9):
    raise ValueError("Sign-flip and one-sample t statistics disagree")
for start in range(0,p,CHUNK):
    stop=min(start+CHUNK,p)
    xb=X[:,start:stop]
    perm_sum=signs @ xb
    den=np.sqrt(np.maximum((n*sumsq[start:stop]-perm_sum**2)/(n-1),0))
    pt=np.divide(perm_sum,den,out=np.zeros_like(perm_sum),where=den>0)
    max_null=np.maximum(max_null,pt.max(axis=1))
p_fwe=(1+(max_null[:,None] >= tobs[None,:]).sum(axis=0))/(N_PERM+1)

# Output maps in original image space.
def save_map(name, vals, dtype=np.float32):
    arr=np.zeros(ref.shape,dtype=dtype)
    if np.asarray(vals).shape == ref.shape:
        arr[mask]=np.asarray(vals)[mask]
    else:
        arr[mask]=vals
    img=nib.Nifti1Image(arr,ref.affine,ref.header.copy())
    img.set_data_dtype(dtype)
    nib.save(img,OUT/name)
save_map("common_mask.nii.gz",mask.astype(np.uint8),np.uint8)
save_map("group_mean_cope.nii.gz",mean)
save_map("group_tstat.nii.gz",tobs)
save_map("p_uncorrected_one_sided.nii.gz",p_unc.astype(np.float32))
save_map("p_fwe_maxT_one_sided.nii.gz",p_fwe.astype(np.float32))

# Independent anatomical ROI: Harvard-Oxford cortical atlas labels chosen in protocol.
atlas=datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm", verbose=0)
atlas_res=image.resample_to_img(atlas.maps,ref,interpolation="nearest",force_resample=True)
atlas_arr=atlas_res.get_fdata().astype(int)
labels=list(atlas.labels)
atlas_res.set_data_dtype(np.uint8)
nib.save(atlas_res,OUT/"harvard_oxford_cortical_25pct_resampled.nii.gz")
np.save(OUT/"harvard_oxford_cortical_labels.npy",atlas_arr.astype(np.uint8))
(OUT/"harvard_oxford_labels.json").write_text(json.dumps(labels,indent=2)+"\n")
roi_labels=["Frontal Medial Cortex","Subcallosal Cortex"]
roi_ids=[labels.index(x) for x in roi_labels]
roi=(np.isin(atlas_arr,roi_ids) & mask)
if not roi.any(): raise ValueError("Atlas vmPFC proxy has no overlap with common mask")
# Independent, atlas-derived binary ROI retained to document exact operationalization.
nib.save(nib.Nifti1Image(roi.astype(np.uint8),ref.affine,ref.header.copy()),OUT/"vmPFC_HO_proxy.nii.gz")
# X is p by n in selected mask; select ROI positions in same flattened ordering.
roi_mask_flat=roi[mask]
roi_by_subj=X[:,roi_mask_flat].mean(axis=1)
roi_summary={
    "atlas":"Harvard-Oxford cortical atlas, max-probability threshold 25%, 2-mm source, nearest-neighbour resampled to cope grid",
    "labels":roi_labels,"roi_voxels_common_support":int(roi.sum()),
    "mean_cope":float(roi_by_subj.mean()),"sd_between_subjects":float(roi_by_subj.std(ddof=1)),
    "sem":float(stats.sem(roi_by_subj)),
    "ci95_t":[float(x) for x in stats.t.interval(.95,n-1,loc=roi_by_subj.mean(),scale=stats.sem(roi_by_subj))],
    "one_sample_t":float(stats.ttest_1samp(roi_by_subj,0,alternative="greater").statistic),
    "one_sided_p_uncorrected":float(stats.ttest_1samp(roi_by_subj,0,alternative="greater").pvalue),
    "interpretation":"descriptive/localization summary; not used as the primary whole-brain test"
}

# Connected components and atlas labels describe the already FWE-significant voxels.
sig_vol=np.zeros(ref.shape,dtype=bool); sig_vol[mask]=(p_fwe<=ALPHA)
components,n_components=ndimage.label(sig_vol,structure=np.ones((3,3,3),dtype=int))
dist_mm=ndimage.distance_transform_edt(mask,sampling=ref.header.get_zooms()[:3])
cluster_rows=[]
for cid in range(1,n_components+1):
    cm=components==cid
    if not cm.any(): continue
    ijk_all=np.array(np.where(cm))
    flat_in_mask=np.flatnonzero(cm[mask])
    vals=tobs[flat_in_mask]
    peak_index=int(np.argmax(vals)); peak_ijk=ijk_all[:,peak_index]
    peak_tuple=tuple(peak_ijk)
    peak_mni=nib.affines.apply_affine(ref.affine,peak_ijk).tolist()
    cluster_rows.append({"cluster":cid,"n_voxels_26_connected":int(cm.sum()),
        "peak_t":float(vals[peak_index]),"peak_p_fwe":float(p_fwe[flat_in_mask[peak_index]]),
        "peak_x_mm":float(peak_mni[0]),"peak_y_mm":float(peak_mni[1]),"peak_z_mm":float(peak_mni[2]),
        "peak_harvard_oxford_label":labels[int(atlas_arr[peak_tuple])],
        "peak_distance_to_common_mask_edge_mm":float(dist_mm[peak_tuple])})
pd.DataFrame(cluster_rows).to_csv(OUT/"fwe_clusters.tsv",sep="\t",index=False)

# Tables, summary and run identity.
pd.DataFrame(qc).to_csv(OUT/"participant_qc.tsv",sep="\t",index=False)
results={
    "n_participants":n,"n_excluded":0,"excluded":[],"image_shape":list(ref.shape),
    "affine":ref.affine.tolist(),"n_common_support_voxels":int(p),
    "median_individual_nonzero_support":int(np.median(S.reshape(n,-1).sum(1))),
    "min_individual_nonzero_support":int(S.reshape(n,-1).sum(1).min()),
    "max_individual_nonzero_support":int(S.reshape(n,-1).sum(1).max()),
    "metadata":{"age_mean":float(participants.age.mean()),"age_sd":float(participants.age.std(ddof=1)),
        "age_min":int(participants.age.min()),"age_max":int(participants.age.max()),
        "gender_counts":{str(k):int(v) for k,v in participants.gender.value_counts().sort_index().items()}},
    "one_sided_hypothesis":"mean participant gain cope > 0",
    "whole_brain_method":"one-sample t statistic; participant sign-flip max-t; one-sided FWE",
    "permutations":N_PERM,"seed":SEED,"alpha":ALPHA,"n_fwe_voxels_p_le_0.05":int((p_fwe<=ALPHA).sum()),
    "max_t_observed":float(tobs.max()),"max_t_fwe_p_at_max":float(p_fwe[tobs.argmax()]),
    "max_t_uncorrected_p_at_max":float(p_unc[tobs.argmax()]),
    "positive_fwe_min_p":float(p_fwe.min()),"positive_fwe_max_t_threshold":float(np.quantile(max_null,1-ALPHA,method="higher")),
    "fwe_significant_voxels_in_vmPFC_proxy":int((sig_vol & roi).sum()),
    "fwe_significant_voxels_by_harvard_oxford_label":{
        labels[int(k)]:int(v) for k,v in zip(*np.unique(atlas_arr[sig_vol],return_counts=True))},
    "fwe_clusters_26_connected":cluster_rows,
    "vmPFC_proxy":roi_summary,
    "environment":{"python":sys.version,"platform":platform.platform(),"nibabel":nib.__version__,"nilearn":nilearn.__version__,"numpy":np.__version__,"scipy":scipy.__version__,"pandas":pd.__version__},
    "inputs_manifest_sha256":hashlib.sha256((IN/"sources.json").read_bytes()).hexdigest()
}
(OUT/"summary.json").write_text(json.dumps(results,indent=2)+"\n")

# Figure: FWE-corrected map if present; otherwise uncorrected p<.001 visualization explicitly labeled exploratory.
if (p_fwe<=ALPHA).any():
    shown=np.where(p_fwe<=ALPHA,tobs,0)
    title="Positive gain effect: whole-brain max-T FWE p ≤ .05"
    fname="whole_brain_fwe.png"
else:
    shown=np.where(p_unc<.001,tobs,0)
    title="Exploratory only: positive effect, uncorrected p < .001; no voxel passed whole-brain FWE"
    fname="whole_brain_exploratory.png"
vis=np.zeros(ref.shape,dtype=np.float32); vis[mask]=shown
vis_img=nib.Nifti1Image(vis,ref.affine,ref.header.copy())
# Standard MNI152 anatomy is used for display only; statistic maps remain on
# the supplied MNI152NLin2009cAsym cope grid.
display_template=datasets.load_mni152_template(resolution=2)
plotting.plot_stat_map(vis_img,bg_img=display_template,display_mode="z",cut_coords=(-8,-4,0),
                       threshold=0,colorbar=True,title=title,black_bg=False,
                       output_file=str(FIG/fname),annotate=True,draw_cross=False)
# ROI participant variability.
fig,ax=plt.subplots(figsize=(7.2,4.4),layout="constrained")
ax.scatter(np.arange(1,n+1),roi_by_subj,s=22,alpha=.72,color="#315b7d",edgecolor="white",linewidth=.3)
mu=roi_by_subj.mean(); lo,hi=roi_summary["ci95_t"]
ax.axhline(0,color="#666666",lw=1,ls="--")
ax.axhline(mu,color="#b33f35",lw=2,label=f"mean = {mu:.3f}")
ax.axhspan(lo,hi,color="#b33f35",alpha=.15,label=f"95% t CI [{lo:.3f}, {hi:.3f}]")
ax.set(xlabel="Participants (ordered by ID)",ylabel="Mean cope in vmPFC atlas proxy (upstream units)",
       title="Participant-level gain-effect estimates in vmPFC proxy")
ax.legend(frameon=False,loc="best"); ax.spines[["top","right"]].set_visible(False)
fig.savefig(FIG/"vmPFC_participant_estimates.png",dpi=180); plt.close(fig)
print(json.dumps(results,indent=2))
