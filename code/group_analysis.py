#!/usr/bin/env python3
"""Group inference for the supplied NARPS AO86 gain-effect maps.

Primary test: one-sample random-effects t statistic, positive direction, with
participant-level sign-flip max-T family-wise error correction over a data-derived
whole-brain coverage mask. The mask retains voxels represented by at least 90%
of participants. No participant maps are smoothed or resampled.
"""
from pathlib import Path
import json
import math
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy.ndimage import label
from nilearn import plotting, datasets
from nilearn.image import new_img_like, resample_to_img
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "input" / "data"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)
N_PERM = 5000
SEED = 20261016
MASK_COVERAGE = 0.90
ROI_MNI = np.array([0., 44., -10.])
ROI_RADIUS_MM = 10.

metadata = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
metadata = metadata.loc[metadata.group.eq("equalIndifference")].copy()
paths = [DATA / f"{pid}_hypo1_cope.nii.gz" for pid in metadata.participant_id]
missing = [str(p) for p in paths if not p.exists()]
if missing:
    raise FileNotFoundError(f"Missing participant maps: {missing}")

imgs = [nib.load(str(p)) for p in paths]
ref = imgs[0]
if any(img.shape != ref.shape or not np.allclose(img.affine, ref.affine) for img in imgs):
    raise ValueError("Participant maps have inconsistent grids")
arr = np.stack([img.get_fdata(dtype=np.float32) for img in imgs]).astype(np.float64)
if not np.isfinite(arr).all():
    raise ValueError("Non-finite map values found")
coverage = np.count_nonzero(arr, axis=0)
mask = coverage >= math.ceil(MASK_COVERAGE * len(imgs))
Y = arr[:, mask]
n, nvox = Y.shape

# Observed one-sample t statistic, equal participant weight (random-effects).
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(n))
df = n - 1
p_unc = stats.t.sf(t_obs, df)

# Sign-flip max-T null. The maximum positive t in each draw gives one-sided
# whole-brain FWER control without a spatial smoothness or cluster-form model.
rng = np.random.default_rng(SEED)
sum_sq = np.einsum("ij,ij->j", Y, Y)
max_null = np.empty(N_PERM, dtype=np.float32)
batch_size = 50
for start in range(0, N_PERM, batch_size):
    stop = min(start + batch_size, N_PERM)
    signs = rng.choice(np.array([-1., 1.]), size=(stop - start, n))
    sums = signs @ Y
    var_num = np.maximum(sum_sq[None, :] - sums * sums / n, 0.)
    t_perm = sums * np.sqrt((n - 1) / (n * var_num), where=var_num > 0,
                           out=np.zeros_like(var_num))
    max_null[start:stop] = np.max(t_perm, axis=1)

# Monte-Carlo adjusted p values and the global one-sided 5% max-T threshold.
max_sorted = np.sort(max_null)
p_fwe = (1 + N_PERM - np.searchsorted(max_sorted, t_obs, side="left")) / (N_PERM + 1)
threshold_t = float(np.quantile(max_null, .95, method="higher"))
sig = p_fwe <= .05

# Independent, literature-coordinate sphere for vmPFC interpretation only;
# the hypothesis decision remains the whole-brain max-T result.
ijk = np.indices(ref.shape).reshape(3, -1).T
xyz = nib.affines.apply_affine(ref.affine, ijk)
roi_full = (np.linalg.norm(xyz - ROI_MNI, axis=1) <= ROI_RADIUS_MM).reshape(ref.shape)
roi = roi_full & mask
roi_Y = arr[:, roi].mean(axis=1)
roi_mean = float(roi_Y.mean())
roi_sd = float(roi_Y.std(ddof=1))
roi_t, roi_p = stats.ttest_1samp(roi_Y, popmean=0, alternative="greater")
roi_ci = stats.t.interval(.95, n - 1, loc=roi_mean, scale=stats.sem(roi_Y))
roi_dz = roi_mean / roi_sd

# QC summaries and max-T map outputs.
mean_full = np.zeros(ref.shape, dtype=np.float32); mean_full[mask] = mean
sd_full = np.zeros(ref.shape, dtype=np.float32); sd_full[mask] = sd
t_full = np.zeros(ref.shape, dtype=np.float32); t_full[mask] = t_obs
pfwe_full = np.ones(ref.shape, dtype=np.float32); pfwe_full[mask] = p_fwe
sig_full = np.zeros(ref.shape, dtype=np.uint8); sig_full[mask] = sig.astype(np.uint8)
for name, data in [("group_mean_effect.nii.gz", mean_full), ("group_t_positive.nii.gz", t_full),
                   ("group_fwe_p_positive.nii.gz", pfwe_full), ("group_significant_fwe05.nii.gz", sig_full),
                   ("coverage_mask_90pct.nii.gz", mask.astype(np.uint8))]:
    nib.save(new_img_like(ref, data), RESULTS / name)

subject_summary = pd.DataFrame({
    "participant_id": metadata.participant_id.to_numpy(),
    "group": metadata.group.to_numpy(),
    "age": metadata.age.to_numpy(),
    "gender": metadata.gender.to_numpy(),
    "map_nonzero_voxels": np.count_nonzero(arr, axis=(1,2,3)),
    "mean_effect_in_coverage_mask": Y.mean(axis=1),
    "sd_effect_in_coverage_mask": Y.std(axis=1, ddof=1),
    "mean_effect_in_vmPFC_sphere": roi_Y,
})
subject_summary.to_csv(RESULTS / "participant_qc_and_roi.tsv", sep="\t", index=False)

# Connected components are descriptive only; inference was voxelwise max-T FWER.
labels, n_clusters = label(sig_full, structure=np.ones((3,3,3), dtype=int))
cluster_rows = []
for label_id in range(1, n_clusters + 1):
    ijk_c = np.argwhere(labels == label_id)
    xyz_c = nib.affines.apply_affine(ref.affine, ijk_c)
    vals = t_full[labels == label_id]
    cluster_rows.append({"cluster": label_id, "voxels": len(ijk_c), "peak_t": float(vals.max()),
                         "peak_x": float(xyz_c[np.argmax(vals),0]), "peak_y": float(xyz_c[np.argmax(vals),1]),
                         "peak_z": float(xyz_c[np.argmax(vals),2]),
                         "mean_x": float(xyz_c[:,0].mean()), "mean_y": float(xyz_c[:,1].mean()),
                         "mean_z": float(xyz_c[:,2].mean())})
pd.DataFrame(cluster_rows).to_csv(RESULTS / "fwe_clusters.tsv", sep="\t", index=False)
pd.DataFrame({"max_positive_t": max_null}).to_csv(RESULTS / "permutation_max_t.tsv", sep="\t", index=False)

# Separate maps keep the anatomical and glass-brain views legible.
mean_img = new_img_like(ref, mean_full)
t_img = new_img_like(ref, t_full)
bg_img = resample_to_img(datasets.load_mni152_template(resolution=2), mean_img, interpolation="continuous")
fig, ax = plt.subplots(figsize=(8.5, 5.2))
display = plotting.plot_stat_map(mean_img, bg_img=bg_img, display_mode="ortho", cut_coords=tuple(ROI_MNI),
                                 threshold=0.005, cmap="cold_hot", colorbar=True, black_bg=False,
                                 vmin=-0.10, vmax=0.10, cbar_tick_format="%.2f",
                                 title=None, axes=ax)
display.add_markers([ROI_MNI], marker_color="cyan", marker_size=75)
fig.suptitle("Mean gain-effect estimate (54 participants; supplied map units)\nCyan marker: vmPFC sphere center", fontsize=13)
fig.savefig(FIGURES / "mean_effect_map.png", dpi=180, bbox_inches="tight")
plt.close(fig)

peak_xyz = xyz[mask.ravel()][np.argmax(t_obs)]
fig, ax = plt.subplots(figsize=(8.5, 4.8))
positive_t_img = new_img_like(ref, np.where(t_full > 0, t_full, 0))
display2 = plotting.plot_glass_brain(positive_t_img, display_mode="ortho", plot_abs=False,
                                     threshold=threshold_t, cmap="hot", colorbar=True, black_bg=False,
                                     title=None, axes=ax)
display2.add_markers([ROI_MNI], marker_color="cyan", marker_size=75)
fig.suptitle(f"Positive t, whole-brain max-T FWE; threshold t={threshold_t:.2f}\n{int(sig.sum())} voxels; peak [{peak_xyz[0]:.0f}, {peak_xyz[1]:.0f}, {peak_xyz[2]:.1f}] MNI; cyan = vmPFC center", fontsize=13)
fig.savefig(FIGURES / "whole_brain_fwe.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(6.7, 4.5))
ordered = np.sort(roi_Y)
ax.scatter(np.arange(1, n+1), ordered, s=30, alpha=.8, color="#2673a5", edgecolor="white", linewidth=.4)
ax.axhline(0, color="black", linewidth=1)
ax.axhline(roi_mean, color="#c04b36", linewidth=2, label=f"mean {roi_mean:.4f}")
ax.axhspan(roi_ci[0], roi_ci[1], color="#c04b36", alpha=.15, label="95% t interval for mean")
ax.set(xlabel="Participants (sorted by ROI estimate)", ylabel="Mean cope in vmPFC sphere (map units)",
       title="Participant gain-effect estimates in literature-coordinate vmPFC sphere")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIGURES / "vmPFC_participant_effects.png", dpi=180)
plt.close(fig)

qc = {
    "n_maps": len(imgs), "n_group": int(n), "n_excluded": 0,
    "all_maps_finite": True, "shape": list(ref.shape), "voxel_size_mm": [float(x) for x in ref.header.get_zooms()[:3]],
    "mask_rule": f"nonzero coverage in >= {MASK_COVERAGE:.0%} of participants",
    "n_mask_voxels": int(mask.sum()), "coverage_min_in_mask": int(coverage[mask].min()),
    "coverage_voxels_90pct": int((coverage >= math.ceil(.9*n)).sum()),
    "coverage_voxels_95pct": int((coverage >= math.ceil(.95*n)).sum()),
    "coverage_voxels_100pct": int((coverage == n).sum()),
    "map_value_range_all": [float(arr.min()), float(arr.max())],
    "nonzero_voxels_per_participant_min_median_max": [int(np.min(subject_summary.map_nonzero_voxels)), int(np.median(subject_summary.map_nonzero_voxels)), int(np.max(subject_summary.map_nonzero_voxels))],
    "mask_mean_effect_range": [float(np.min(mean)), float(np.max(mean))],
    "mask_mean_effect_median": float(np.median(mean)),
    "permutation": {"method":"participant sign flips; max positive t across whole mask", "n_draws": N_PERM, "seed": SEED, "global_t_threshold_95pct": threshold_t,
                    "min_attainable_p": 1/(N_PERM+1), "n_fwe_sig_voxels": int(sig.sum()), "min_fwe_p": float(np.min(p_fwe)),
                    "max_observed_t": float(np.max(t_obs)), "max_observed_t_mni": [float(x) for x in xyz[mask.ravel()][np.argmax(t_obs)]], "maxT_fwe_p_at_peak": float(np.min(p_fwe))},
    "vmPFC_roi": {"definition":"10-mm-radius sphere centered at MNI [0, 44, -10] mm; literature-coordinate descriptive ROI, not used for primary inference",
                   "n_voxels": int(roi.sum()), "center_mni_mm": ROI_MNI.tolist(), "radius_mm": ROI_RADIUS_MM,
                   "mean_effect": roi_mean, "sd_between_participants": roi_sd, "ci95_t": [float(roi_ci[0]), float(roi_ci[1])],
                   "t_one_sample_descriptive_positive": float(roi_t), "p_one_sided_uncorrected_descriptive": float(roi_p), "cohen_dz": roi_dz},
    "group_model":"one-sample t over participant effect maps; equal participant weight; df=53",
}
(RESULTS / "summary.json").write_text(json.dumps(qc, indent=2) + "\n")
print(json.dumps(qc, indent=2))
