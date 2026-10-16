#!/usr/bin/env python3
"""Create a coordinate-based localization figure from checked group maps."""
from pathlib import Path
import json
import os
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from nilearn import datasets
from nilearn.image import resample_to_img
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def save_figure(fig, target):
    suffix = "".join(target.suffixes)
    temp = target.with_name(f".{target.stem}.{os.getpid()}.tmp{suffix}")
    try:
        fig.savefig(temp, dpi=180, format="png", bbox_inches="tight")
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
t_img = nib.load(str(R / "t_unthresholded.nii.gz"))
sig = np.asarray(nib.load(str(R / "t_fwe05.nii.gz")).dataobj) > 0
t = np.asarray(t_img.dataobj)[sig]
ijk = np.argwhere(sig)
xyz = nib.affines.apply_affine(t_img.affine, ijk)
if len(t) == 0:
    raise RuntimeError("No corrected positive voxels to localize")

fig, axes = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
scatter = axes[0].scatter(xyz[:, 1], xyz[:, 2], c=t, cmap="Reds", vmin=0, vmax=float(t.max()),
                          s=75, edgecolor="black", linewidth=.4)
axes[0].add_patch(plt.Rectangle((20, -20), 40, 40, fill=False, linestyle="--",
                                edgecolor="#256D85", linewidth=2, label="vmPFC descriptive box"))
axes[0].set(xlabel="MNI y (mm; anterior →)", ylabel="MNI z (mm; superior →)",
            title="Sagittal-coordinate projection (all x)")
axes[0].legend(frameon=False, loc="best")
axes[0].grid(alpha=.2)
axes[1].scatter(xyz[:, 1], xyz[:, 0], c=t, cmap="Reds", vmin=0, vmax=float(t.max()),
                s=75, edgecolor="black", linewidth=.4)
axes[1].add_patch(plt.Rectangle((20, -10), 40, 20, fill=False, linestyle="--",
                                edgecolor="#256D85", linewidth=2, label="vmPFC descriptive box"))
axes[1].set(xlabel="MNI y (mm; anterior →)", ylabel="MNI x (mm; left ↔ right)",
            title="Axial coordinate projection")
axes[1].legend(frameon=False, loc="best")
axes[1].grid(alpha=.2)
fig.colorbar(scatter, ax=axes, label="Group t statistic at max-t FWE-significant voxel")
fig.suptitle(f"{len(t)} positive voxels survived whole-brain max-t FWE (p ≤ .05)", fontsize=14)
save_figure(fig, R / "corrected_voxel_coordinates.png")
plt.close(fig)

summary = json.loads((R / "summary.json").read_text())
t_img = nib.load(str(R / "t_unthresholded.nii.gz"))
mask_img = resample_to_img(datasets.load_mni152_brain_mask(resolution=2), t_img,
                           interpolation="nearest", force_resample=True, copy_header=True)
t_all = np.asarray(t_img.dataobj)[np.asarray(mask_img.dataobj) > 0]
null = pd.read_csv(R / "permutation_max_t.tsv", sep="\t").max_t_null.to_numpy()
threshold = float(np.quantile(null, .95, method="higher"))
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), gridspec_kw={"width_ratios": [1.35, 1]}, constrained_layout=True)
axes[0].hist(t_all, bins=90, color="#7897A8", edgecolor="white", linewidth=.25)
axes[0].axvline(0, color="black", lw=1)
axes[0].axvline(threshold, color="#B33C2E", lw=2, ls="--", label=f"95th percentile max-t null = {threshold:.2f}")
axes[0].set(xlabel="One-sample t statistic", ylabel="Tested voxels", title="Whole-brain voxelwise statistics")
axes[0].legend(frameon=False, fontsize=9)
axes[1].axis("off")
peak = pd.read_csv(R / "top_voxels.tsv", sep="\t").iloc[0]
axes[1].text(.02, .95,
        "One-sided max-t inference\n\n"
        f"{summary['n_voxels_tested']:,} tested voxels\n"
        f"{summary['n_fwe_positive_voxels']} positive voxels passed FWE p ≤ .05\n"
        f"{summary['n_fwe_positive_voxels_in_vmPFC_box']} in vmPFC search box\n\n"
        f"Peak: t = {peak.t:.2f}\n"
        f"MNI ({peak.x_mm:.1f}, {peak.y_mm:.1f}, {peak.z_mm:.1f})\n"
        f"FWE p = {peak.p_fwe_max_t:.4g}\n\n"
        "See coordinate figure for all corrected voxels.",
        ha="left", va="top", fontsize=11, linespacing=1.35)
fig.suptitle("Group gain effect: whole-brain inference", fontsize=14)
save_figure(fig, R / "whole_brain_results.png")
plt.close(fig)

subjects = pd.read_csv(R / "participant_vmPFC_summary.tsv", sep="\t")
values = subjects.vmPFC_box_mean_effect.to_numpy()
n = len(values)
mean = float(values.mean())
sd = float(values.std(ddof=1))
ci = stats.t.interval(.95, n - 1, loc=mean, scale=sd / np.sqrt(n))
fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
ax.scatter(np.arange(n) + 1, values, color="#356A8A", alpha=.8, s=24)
ax.axhline(mean, color="#B33C2E", lw=1.5, label=f"mean {mean:.3g}")
ax.errorbar((n + 1) / 2, mean, yerr=[[mean - ci[0]], [ci[1] - mean]], fmt="o",
            color="#B33C2E", capsize=5, lw=2, label=f"95% t CI [{ci[0]:.3g}, {ci[1]:.3g}]")
ax.axhline(0, color="black", lw=1, ls="--")
ax.set(xlabel="Participant (cohort table order)", ylabel="Mean participant gain effect (map units)",
       title="Descriptive vmPFC coordinate-box effects")
ax.legend(frameon=False, loc="best")
save_figure(fig, R / "vmPFC_participant_effects.png")
plt.close(fig)
print(f"saved three figures; {len(t)} voxels passed whole-brain correction")
