#!/usr/bin/env python3
"""Create a coordinate-based localization figure from checked group maps."""
from pathlib import Path
import nibabel as nib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
fig.savefig(R / "corrected_voxel_coordinates.png", dpi=180)
plt.close(fig)
print(f"saved results/corrected_voxel_coordinates.png ({len(t)} voxels)")
