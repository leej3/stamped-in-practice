#!/usr/bin/env python3
"""Create a coordinate-based localization figure from checked group maps."""
from pathlib import Path
import os
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
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
            title="Midsagittal coordinate projection")
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
print(f"saved results/corrected_voxel_coordinates.png ({len(t)} voxels) and participant interval figure")
