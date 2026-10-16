#!/usr/bin/env python3
"""Group analysis of fixed NARPS AO86 gain-effect maps."""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy import ndimage
from nilearn import datasets, image, plotting
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "input" / "data"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
participants = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
files = [DATA / f"{pid}_hypo1_cope.nii.gz" for pid in participants.participant_id]
assert len(files) == 54 and all(f.exists() for f in files)
source_index = json.loads((ROOT / "input" / "sources.json").read_text())
for pid, path in zip(participants.participant_id, files):
    expected = source_index["files"][f"data/{path.name}"]["sha256"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected:
        raise ValueError(f"SHA256 mismatch for {pid}: {digest} != {expected}")

imgs = [nib.load(str(f)) for f in files]
ref = imgs[0]
for pid, im in zip(participants.participant_id, imgs):
    if im.shape != ref.shape or not np.allclose(im.affine, ref.affine, atol=1e-5):
        raise ValueError(f"Image geometry mismatch: {pid}")
arr = np.stack([im.get_fdata(dtype=np.float32) for im in imgs])
finite = np.isfinite(arr)
valid = finite & (arr != 0)
# Restrict tests to voxels covered in every subject and within an anatomical
# whole-brain mask. The supplied MNI152NLin2009cAsym data are close to the
# symmetric 2009a ICBM template; resampling uses world coordinates.
common = np.all(valid, axis=0)
icbm = datasets.fetch_icbm152_2009(data_dir=str(ROOT / "analysis" / "atlases"))
brainmask_img = image.resample_to_img(image.load_img(icbm.mask), ref, interpolation="nearest")
brainmask = np.asarray(brainmask_img.dataobj) > 0
common &= brainmask
if not np.any(common):
    raise ValueError("No common nonzero coverage")
Y = arr[:, common]
n, m = Y.shape
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
tmap = mean / (sd / np.sqrt(n))
pmap = stats.t.sf(tmap, n - 1)  # prespecified positive direction
p_fwe = np.minimum(pmap * m, 1.0)  # valid voxelwise Bonferroni FWE
sig = p_fwe < .05
sig_volume = np.zeros(ref.shape, dtype=bool); sig_volume[common] = sig
clusters, n_clusters = ndimage.label(sig_volume, structure=np.ones((3,3,3), dtype=int))
full_tmap = np.zeros(ref.shape, dtype=np.float32); full_tmap[common] = tmap
cluster_rows=[]
for lab in range(1,n_clusters+1):
    ijk=np.argwhere(clusters==lab)
    vals=full_tmap[clusters==lab]
    peak_ijk=ijk[np.argmax(vals)]
    peak_xyz=nib.affines.apply_affine(ref.affine,peak_ijk)
    cluster_rows.append({"cluster":lab,"voxels":len(ijk),"peak_t":float(vals.max()),
                         "peak_raw_p_one_sided":float(stats.t.sf(vals.max(), n-1)),
                         "peak_fwe_p_bonferroni":float(min(stats.t.sf(vals.max(),n-1)*m,1)),
                         "peak_x_mm":float(peak_xyz[0]),"peak_y_mm":float(peak_xyz[1]),"peak_z_mm":float(peak_xyz[2])})

def save_map(values, name, dtype=np.float32):
    data = np.zeros(ref.shape, dtype=dtype)
    data[common] = values
    path = OUT / name
    nib.save(nib.Nifti1Image(data, ref.affine, ref.header), path)
    return path

mean_img = save_map(mean, "mean_gain_effect.nii.gz")
t_img = save_map(tmap, "onesample_t_positive.nii.gz")
pfwe_img = save_map(p_fwe, "p_fwe_bonferroni_positive.nii.gz")

# Prespecified anatomical vmPFC proxy: bilateral medial orbital frontal cortex
# and gyrus rectus from AAL (Tzourio-Mazoyer et al.); resampled to map grid.
aal = datasets.fetch_atlas_aal(version="SPM12", data_dir=str(ROOT / "analysis" / "atlases"))
atlas = image.load_img(aal.maps)
labels = [str(x.decode() if isinstance(x, bytes) else x) for x in aal.labels]
roi_labels = ["Frontal_Med_Orb_L", "Frontal_Med_Orb_R", "Rectus_L", "Rectus_R"]
missing = [lab for lab in roi_labels if lab not in labels]
if missing:
    raise ValueError(f"AAL labels missing: {missing}")
roi_ids = [int(aal.indices[labels.index(lab)]) for lab in roi_labels]
aal_on_grid = image.resample_to_img(atlas, ref, interpolation="nearest")
aal_data = np.asarray(aal_on_grid.dataobj)
roi = np.isin(aal_data, roi_ids) & common
for row in cluster_rows:
    row["vmPFC_overlap_voxels"] = int(np.sum(roi & (clusters == row["cluster"])))
if roi.sum() < 10:
    raise ValueError(f"vmPFC proxy too small after coverage intersection: {roi.sum()}")
roi_subject = arr[:, roi].mean(axis=1)
roi_mean = float(roi_subject.mean())
roi_sd = float(roi_subject.std(ddof=1))
roi_se = roi_sd / np.sqrt(n)
roi_ci = stats.t.interval(.95, n-1, loc=roi_mean, scale=roi_se)
roi_t = roi_mean / roi_se
roi_p = float(stats.t.sf(roi_t, n-1))
roi_d = roi_mean / roi_sd

def stat(v):
    v = np.asarray(v)
    return {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "se": float(v.std(ddof=1)/np.sqrt(len(v))),
            "ci95_low": float(stats.t.interval(.95,len(v)-1,loc=v.mean(),scale=stats.sem(v))[0]),
            "ci95_high": float(stats.t.interval(.95,len(v)-1,loc=v.mean(),scale=stats.sem(v))[1])}

qc = {
    "n_metadata": int(len(participants)), "n_images": int(len(imgs)), "n_included": int(n),
    "input_sha256_verified": True,
    "excluded": [], "image_shape": list(ref.shape), "voxel_sizes_mm": list(nib.affines.voxel_sizes(ref.affine)),
    "finite_fraction": float(finite.mean()), "nonzero_voxels_each_min": int(valid.reshape(n,-1).sum(axis=1).min()),
    "nonzero_voxels_each_max": int(valid.reshape(n,-1).sum(axis=1).max()),
    "common_coverage_voxels": int(m), "common_coverage_volume_ml": float(m*np.prod(nib.affines.voxel_sizes(ref.affine))/1000),
    "analysis_mask": "intersection of nonzero participant coverage and resampled ICBM 2009 brain mask",
    "roi": {"atlas":"AAL SPM12", "labels":roi_labels, "covered_voxels":int(roi.sum()), "volume_ml":float(roi.sum()*np.prod(nib.affines.voxel_sizes(ref.affine))/1000),
            "subject_roi_means":stat(roi_subject), "one_sample_t_df": [float(roi_t), int(n-1)], "one_sided_p_uncorrected":roi_p,
            "cohen_dz":float(roi_d)},
    "whole_brain": {"test":"one-sample t, positive-direction", "df":int(n-1), "familywise_method":"Bonferroni across all common-coverage voxels",
            "tested_voxels":int(m), "fwe_alpha":0.05, "fwe_significant_voxels":int(sig.sum()),
            "maximum_t":float(np.max(tmap)), "maximum_raw_p":float(np.min(pmap)), "minimum_fwe_p":float(np.min(p_fwe)),
            "mean_effect_at_max_t":float(mean[np.argmax(tmap)]), "fwe_clusters_26_neighbor":cluster_rows},
    "map_scale_note":"Subject contrast estimates are not standardized test statistics; the gain modulator was variance-normalized within the upstream model, so effects are not per currency unit."
}
(OUT/"summary.json").write_text(json.dumps(qc,indent=2)+"\n")
pd.DataFrame(cluster_rows).to_csv(OUT/"wholebrain_fwe_clusters.tsv",sep="\t",index=False)
pd.DataFrame({"participant_id":participants.participant_id,"group":participants.group,"age":participants.age,"gender":participants.gender,"mean_vmPFC_effect":roi_subject}).to_csv(OUT/"vmPFC_subject_estimates.tsv",sep="\t",index=False)

# Figures: anatomical ROI is shown on the group mean; whole-brain evidence map
# shows only voxels passing the prespecified whole-brain FWE criterion.
roi_img_data = np.zeros(ref.shape,dtype=np.uint8); roi_img_data[roi]=1
roi_img = nib.Nifti1Image(roi_img_data,ref.affine)
fig = plt.figure(figsize=(12,5))
display = plotting.plot_stat_map(mean_img, display_mode="z", cut_coords=[-20,-10,0,10,20],
                                threshold=0, cmap="RdBu_r", symmetric_cbar=True,
                                colorbar=True, title="Mean participant gain effect; vmPFC atlas mask contours",
                                figure=fig, black_bg=False)
display.add_contours(roi_img, levels=[.5], colors="lime", linewidths=1.4)
fig.savefig(FIG/"mean_effect_vmPFC.png",dpi=180,bbox_inches="tight"); plt.close(fig)
if sig.any():
    sig_data=np.zeros(ref.shape,dtype=np.float32); sig_data[common]=np.where(sig,tmap,0)
    sig_img=nib.Nifti1Image(sig_data,ref.affine)
else:
    sig_data=np.zeros(ref.shape,dtype=np.float32); sig_img=nib.Nifti1Image(sig_data,ref.affine)
fig=plt.figure(figsize=(12,5))
plotting.plot_stat_map(sig_img, display_mode="z", cut_coords=[-20,-10,0,10,20], threshold=0,
                       cmap="hot", colorbar=True, title="Positive t-statistics passing whole-brain Bonferroni FWE p < .05",
                       figure=fig, black_bg=False)
fig.savefig(FIG/"wholebrain_fwe.png",dpi=180,bbox_inches="tight"); plt.close(fig)

fig,ax=plt.subplots(figsize=(7,4.6))
x=np.arange(n)
ax.scatter(x,roi_subject,s=28,alpha=.8,color="#3b6f8f")
ax.axhline(roi_mean,color="#c45139",lw=2,label=f"Mean = {roi_mean:.3g}")
ax.axhspan(roi_ci[0],roi_ci[1],color="#c45139",alpha=.15,label="95% CI")
ax.axhline(0,color="black",lw=.8)
ax.set(xlabel="Participant (ordered as in cohort table)",ylabel="Mean gain-effect estimate in vmPFC proxy",title="Participant-level vmPFC estimates")
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(FIG/"vmPFC_subject_estimates.png",dpi=180); plt.close(fig)
print(json.dumps(qc,indent=2))
