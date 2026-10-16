#!/usr/bin/env python3
"""Group analysis of NARPS AO86 participant gain-effect maps.

Run from the project root with the supplied Python environment.  The input
maps are participant-level effect estimates, not t/z maps.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import nibabel as nib
from nilearn import datasets, image, plotting
from scipy import stats
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
IN = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
SEED = 8601
N_PERM = 10000

participants = pd.read_csv(IN / "participants.tsv", sep="\t")
paths = [IN / "data" / f"{pid}_hypo1_cope.nii.gz" for pid in participants.participant_id]
assert len(participants) == 54 and all(p.exists() for p in paths)
imgs = [nib.load(str(p)) for p in paths]
ref = imgs[0]
assert all(img.shape == ref.shape and np.allclose(img.affine, ref.affine) for img in imgs)
arr = np.stack([img.get_fdata(dtype=np.float32) for img in imgs])
assert np.isfinite(arr).all()

# Use a standard MNI152 brain mask resampled to the supplied MNI152NLin2009cAsym
# grid, intersected with voxels represented in at least 95% of participant maps.
template_mask = datasets.load_mni152_brain_mask(resolution=2)
brain = image.resample_to_img(template_mask, ref, interpolation="nearest").get_fdata() > 0
coverage = np.mean(arr != 0, axis=0)
mask = brain & (coverage >= 0.95)
assert mask.sum() > 10000
X = arr[:, mask].astype(np.float64)
n, v = X.shape

# One-sample group model, equal participant weights. Direction was prespecified
# as positive; sign-flip max-T controls family-wise error over all tested voxels.
mean = X.mean(axis=0)
sd = X.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(n))
df = n - 1
p_unc = stats.t.sf(t_obs, df)

rng = np.random.default_rng(SEED)
max_null = np.empty(N_PERM, dtype=np.float64)
batch = 20
for start in range(0, N_PERM, batch):
    b = min(batch, N_PERM - start)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
    sums = signs @ X
    means = sums / n
    # Under sign flips, the sample SD is calculated from signed observations.
    sq = np.sum(X * X, axis=0)[None, :]
    variances = np.maximum((sq - n * means * means) / (n - 1), 1e-20)
    t_perm = means / np.sqrt(variances / n)
    max_null[start:start+b] = np.max(t_perm, axis=1)

p_fwe = (1 + N_PERM - np.searchsorted(np.sort(max_null), t_obs, side="left")) / (N_PERM + 1)

# Operational anatomical vmPFC proxy: 12 mm sphere centered at MNI [0, 40, -12].
# This is a descriptive prespecified ROI estimate; whole-brain max-T is the
# confirmatory decision rule.
ijk = np.indices(ref.shape).reshape(3, -1).T
xyz = nib.affines.apply_affine(ref.affine, ijk)
roi_volume = ((xyz[:, 0]**2 + (xyz[:, 1]-40)**2 + (xyz[:, 2]+12)**2) <= 12**2).reshape(ref.shape)
roi = roi_volume & mask
roi_data = arr[:, roi]
roi_subj = roi_data.mean(axis=1)
roi_mean = float(roi_subj.mean())
roi_sd = float(roi_subj.std(ddof=1))
roi_se = roi_sd / np.sqrt(n)
roi_ci = stats.t.interval(0.95, df, loc=roi_mean, scale=roi_se)
roi_t = roi_mean / roi_se
roi_p = float(stats.t.sf(roi_t, df))
roi_mask_flat = roi[mask]
roi_peak_local = int(np.argmax(t_obs[roi_mask_flat]))
roi_voxel_indices = np.flatnonzero(roi_mask_flat)
roi_peak_index = int(roi_voxel_indices[roi_peak_local])
roi_peak_xyz = nib.affines.apply_affine(ref.affine, np.argwhere(mask)[roi_peak_index])

# Subject-level summary and map QC.
subj = pd.DataFrame({
    "participant_id": participants.participant_id,
    "mean_effect_in_brain_mask": arr[:, mask].mean(axis=1),
    "mean_effect_in_vmPFC_sphere": roi_subj,
    "nonzero_brain_fraction": (arr[:, brain] != 0).mean(axis=1),
})
subj.to_csv(OUT / "participant_qc_and_roi.csv", index=False)
qc = {
    "n_participants": n, "n_excluded": 0, "n_voxels_tested": int(v),
    "n_brain_template_voxels": int(brain.sum()),
    "n_common_coverage_voxels": int(mask.sum()),
    "map_shape": list(ref.shape), "voxel_sizes_mm": list(map(float, ref.header.get_zooms()[:3])),
    "map_value_min": float(arr.min()), "map_value_max": float(arr.max()),
    "map_value_mean": float(arr.mean()),
    "nonzero_brain_fraction_min": float(subj.nonzero_brain_fraction.min()),
    "nonzero_brain_fraction_max": float(subj.nonzero_brain_fraction.max()),
    "permutation_draws": N_PERM, "random_seed": SEED,
    "test": "one-sided positive one-sample t; sign-flip max-T FWE across brain mask",
    "mask_rule": "MNI152 2mm brain mask resampled to input; nonzero in >=95% participants",
    "roi_rule": "12-mm sphere centered MNI [0, 40, -12], intersected with tested mask",
}

# Peak and corrected extent.
idx_sig = np.flatnonzero(p_fwe < .05)
peak = int(np.argmax(t_obs))
peak_ijk = np.argwhere(mask)[peak]
peak_xyz = nib.affines.apply_affine(ref.affine, peak_ijk)
peak_result = {
    "peak_t": float(t_obs[peak]), "peak_p_uncorrected_one_sided": float(p_unc[peak]),
    "peak_p_fwe": float(p_fwe[peak]), "peak_mni_mm": [float(x) for x in peak_xyz],
    "positive_voxels_p_fwe_lt_0_05": int(len(idx_sig)),
    "roi_voxels": int(roi.sum()), "roi_mean_effect": roi_mean,
    "roi_sd_across_participants": roi_sd, "roi_ci95": [float(roi_ci[0]), float(roi_ci[1])],
    "roi_t": float(roi_t), "roi_df": int(df), "roi_p_uncorrected_one_sided": roi_p,
    "roi_peak_t": float(t_obs[roi_peak_index]),
    "roi_peak_p_fwe_whole_brain": float(p_fwe[roi_peak_index]),
    "roi_peak_mni_mm": [float(x) for x in roi_peak_xyz],
    "roi_voxels_p_fwe_lt_0_05": int(np.sum(p_fwe[roi_mask_flat] < .05)),
}
with open(OUT / "summary.json", "w") as f:
    json.dump({"qc": qc, "results": peak_result}, f, indent=2)

# Save statistical maps.
def full_map(vals, fill=np.nan):
    out = np.full(ref.shape, fill, dtype=np.float32)
    out[mask] = vals.astype(np.float32)
    return nib.Nifti1Image(out, ref.affine, ref.header)

for name, vals in [("group_mean_effect", mean), ("t_statistic", t_obs),
                   ("p_uncorrected_one_sided", p_unc), ("p_fwe_maxT", p_fwe)]:
    nib.save(full_map(vals), OUT / f"{name}.nii.gz")

# Figure 1: unthresholded group mean effect and whole-brain corrected findings.
mean_img = full_map(mean)
vlim = float(np.nanpercentile(np.abs(mean), 98))
display = plotting.plot_stat_map(full_map(mean, fill=0), display_mode="z", cut_coords=[-12, -6, 0, 6],
                       threshold=None, cmap="cold_hot", colorbar=True,
                       title="Mean participant gain-effect estimate", vmax=vlim)
display.savefig(FIG / "group_mean_effect.png", dpi=180)
display.close()
sig_t = np.where(p_fwe < .05, t_obs, np.nan)
display = plotting.plot_stat_map(full_map(sig_t, fill=0),
                       display_mode="ortho", cut_coords=tuple(peak_xyz),
                       threshold=0, cmap="hot", colorbar=True,
                       title="Positive voxels: whole-brain max-T FWE p < .05")
display.savefig(FIG / "whole_brain_fwe.png", dpi=180)
display.close()

# Figure 2: participant-level ROI effects with group mean/CI.
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.scatter(np.arange(n), roi_subj, color="#315a7d", s=24, alpha=.8)
ax.axhline(0, color="0.4", linewidth=1)
ax.axhline(roi_mean, color="#bd4b36", linewidth=2, label=f"Mean = {roi_mean:.4g}")
ax.fill_between([-1, n], roi_ci[0], roi_ci[1], color="#bd4b36", alpha=.14,
                label="95% t interval for mean")
ax.set(xlim=(-1, n), xlabel="Participant (listed in participant_qc_and_roi.csv order)",
       ylabel="Mean effect estimate in vmPFC sphere",
       title="Participant effects in the prespecified vmPFC proxy")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIG / "vmPFC_participants.png", dpi=180)
plt.close(fig)

print(json.dumps({"qc": qc, "results": peak_result}, indent=2))
