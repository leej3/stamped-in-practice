"""Render figures from group maps produced by analyze.py."""
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
from nilearn import plotting
from nilearn.image import new_img_like
from scipy import stats
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT, FIG = ROOT / "results", ROOT / "figures"
mean_img = nib.load(OUT / "group_mean_gain_effect.nii.gz")
logp_img = nib.load(OUT / "group_log10p_fwe_maxT.nii.gz")
vm_img = nib.load(OUT / "vmPFC_proxy_mask.nii.gz")
summary = pd.read_csv(OUT / "participant_qc.tsv", sep="\t")
# Figure 1 uses the family-wise corrected map as the statistic, with the anatomical
# vmPFC proxy outlined for context. Values above 1.301 correspond to p_FWE < .05.
fig = plt.figure(figsize=(11, 5))
display = plotting.plot_stat_map(
    logp_img, display_mode="ortho", cut_coords=(0, -100, -4),
    threshold=-np.log10(.05), cmap="hot", colorbar=True, dim=0,
    title="Positive gain effect: voxelwise max-T FWE evidence",
    figure=fig,
)
display.add_contours(vm_img, levels=[.5], colors="#00D9E8", linewidths=1.0)
fig.suptitle("One-sided max-T permutation test, pFWE < .05", y=.99, fontsize=12)
fig.text(.02, .01, "Yellow: significant positive effect; cyan: vmPFC proxy (Harvard–Oxford medial frontal + subcallosal, clipped to medial ventral coordinates).", fontsize=8)
display.savefig(FIG / "whole_brain_fwe_maxT.png", dpi=180)
plt.close("all")

# Figure 2 summarizes the participant mean effect within the anatomical proxy.
# The displayed CI is descriptive; it is not the confirmatory whole-brain test.
vm = nib.load(OUT / "vmPFC_proxy_mask.nii.gz").get_fdata() > 0
arrs = [nib.load(p).get_fdata(dtype=np.float32) for p in sorted((ROOT / "input/data").glob("*_hypo1_cope.nii.gz"))]
values = np.array([a[vm].mean() for a in arrs])
mean = values.mean(); se = stats.sem(values)
ci = stats.t.interval(.95, len(values)-1, loc=mean, scale=se)
rng = np.random.default_rng(20261016)
fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.scatter(rng.normal(1, .035, len(values)), values, s=25, alpha=.66, color="#355C7D", edgecolors="none")
ax.errorbar([1], [mean], yerr=[[mean-ci[0]], [ci[1]-mean]], fmt="o", color="#C06C84", capsize=5, lw=2, label="mean and 95% t interval")
ax.axhline(0, color="black", lw=1, ls="--")
ax.set(xlim=(.82, 1.18), xticks=[1], xticklabels=["vmPFC proxy"], ylabel="Participant mean gain-effect estimate (cope units)", title="Descriptive participant effects in vmPFC proxy")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIG / "vmPFC_subject_effects.png", dpi=180)
plt.close(fig)
print(f"n={len(values)}, mean={mean:.5f}, CI95=({ci[0]:.5f}, {ci[1]:.5f})")
