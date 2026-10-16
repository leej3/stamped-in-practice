#!/usr/bin/env python3
"""Group inference for NARPS Hypothesis 1, AO86 equal-indifference gain cope maps.

Primary: one-sample random-effects t test with one-sided whole-brain max-T
sign-flip permutation FWE correction. No first-level variance maps are supplied,
so participants receive equal weight. All randomization and masks are deterministic.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from nilearn import datasets, image, plotting
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
FIG = ROOT / "figures"
DATA = ROOT / "input" / "data"
N_PERM = 9999
SEED = 8601
ALPHA = .05

meta = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
files = sorted(DATA.glob("sub-*_hypo1_cope.nii.gz"))
file_ids = [p.name.split("_")[0] for p in files]
assert len(files) == 54 and set(file_ids) == set(meta.participant_id)
meta = meta.set_index("participant_id").loc[file_ids].reset_index()
imgs = [nib.load(str(p)) for p in files]
ref = imgs[0]
for p, im in zip(files, imgs):
    assert im.shape == ref.shape, f"shape mismatch: {p.name}"
    assert np.allclose(im.affine, ref.affine, atol=1e-5), f"affine mismatch: {p.name}"

# An independent standard MNI brain mask, nearest-neighbor resampled to the
# supplied MNI152NLin2009cAsym grid. Positive-coverage voxels inside brain only.
std_mask = datasets.load_mni152_brain_mask(resolution=2)
mask_img = image.resample_to_img(std_mask, ref, interpolation="nearest", force_resample=True)
brain = np.asarray(mask_img.dataobj) > 0
Yvol = np.stack([np.asarray(im.dataobj, dtype=np.float32) for im in imgs], axis=0)
finite = np.isfinite(Yvol).all(axis=0)
# NIfTI zeros mark locations outside each participant's estimation mask in this
# collection. Use their intersection so no fabricated zero observations enter
# the group test; an exactly zero floating-point contrast throughout all maps
# is vanishingly unlikely.
coverage = np.all(Yvol != 0, axis=0)
mask = brain & finite & coverage
assert mask.sum() > 50000
Y = Yvol[:, mask].astype(np.float64, copy=False)
n, v = Y.shape

# One-sample t and one-sided parametric p maps for descriptive comparison.
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
tobs = mean / (sd / np.sqrt(n))
p_unc = stats.t.sf(tobs, df=n-1)

# Sign-flip randomization under the null of symmetric participant effects.
# For each sign vector, calculate all voxel statistics and retain its maximum.
rng = np.random.default_rng(SEED)
max_t = np.empty(N_PERM, dtype=np.float64)
sumsq = np.einsum("ij,ij->j", Y, Y)
batch = 64
for start in range(0, N_PERM, batch):
    b = min(batch, N_PERM-start)
    signs = rng.choice(np.array([-1., 1.]), size=(b, n))
    sums = signs @ Y
    denom2 = (sumsq[None, :] - sums*sums/n) / (n-1)
    ts = (sums / n) / np.sqrt(np.maximum(denom2, 1e-30) / n)
    max_t[start:start+b] = np.max(ts, axis=1)
p_fwe = (1 + (max_t[:, None] >= tobs[None, :]).sum(axis=0)) / (N_PERM + 1)

# Convert maps back to reference image space.
def out_img(vals):
    arr = np.zeros(ref.shape, dtype=np.float32)
    arr[mask] = np.asarray(vals, dtype=np.float32)
    return nib.Nifti1Image(arr, ref.affine, ref.header)
t_img = out_img(tobs)
p_img = out_img(p_fwe)
mean_img = out_img(mean)
for name, im in [("mean_gain_effect.nii.gz", mean_img), ("t_statistic.nii.gz", t_img), ("p_fwe_maxT.nii.gz", p_img)]:
    nib.save(im, OUT / name)

# A fixed, broad anatomical vmPFC core envelope in MNI coordinates, used only
# for an interpretable descriptive summary. Inference remains whole-brain.
ijk = np.indices(ref.shape).reshape(3, -1).T
xyz = nib.affines.apply_affine(ref.affine, ijk)
roi_flat = ((np.abs(xyz[:,0]) <= 15) & (xyz[:,1] >= 20) & (xyz[:,1] <= 55) &
            (xyz[:,2] >= -20) & (xyz[:,2] <= 5))
roi = roi_flat.reshape(ref.shape) & mask
assert roi.sum() > 20
roi_vals = Yvol[:, roi]
subj_roi = roi_vals.mean(axis=1)
roi_mean = subj_roi.mean()
roi_sd = subj_roi.std(ddof=1)
roi_se = roi_sd / np.sqrt(n)
roi_ci = stats.t.interval(.95, n-1, loc=roi_mean, scale=roi_se)
roi_t = roi_mean / roi_se
roi_p = stats.t.sf(roi_t, n-1)

# Peak and cluster-like extent in max-T FWE-significant voxels (voxelwise FWE).
sig = p_fwe <= ALPHA
sig_count = int(sig.sum())
sig_t_img = out_img(np.where(sig, tobs, 0.0))
nib.save(sig_t_img, OUT / "t_fwe_significant.nii.gz")
peak_idx = None
if sig_count:
    peak_local = np.argmax(np.where(sig, tobs, -np.inf))
    peak_idx = np.argwhere(mask)[peak_local]
    peak_xyz = nib.affines.apply_affine(ref.affine, peak_idx)
    peak_t = float(tobs[peak_local]); peak_pfwe = float(p_fwe[peak_local])
else:
    peak_xyz = None; peak_t = None; peak_pfwe = None

# QC metrics and checks.
nonzero_frac = np.mean(Yvol != 0, axis=(1,2,3))
subj_whole_mean = Y.mean(axis=1)
qc = {
  "n_maps": len(files), "n_metadata": len(meta), "all_metadata_ids_matched": True,
  "excluded_participants": [], "common_grid_shape": list(ref.shape),
  "voxel_sizes_mm": [float(x) for x in ref.header.get_zooms()[:3]],
  "reference_affine": ref.affine.tolist(), "whole_brain_mask_voxels": int(mask.sum()),
  "vmPFC_core_mask_voxels": int(roi.sum()), "map_nonzero_fraction_range": [float(nonzero_frac.min()), float(nonzero_frac.max())],
  "participant_whole_brain_mean_range": [float(subj_whole_mean.min()), float(subj_whole_mean.max())],
  "participant_vmPFC_mean_range": [float(subj_roi.min()), float(subj_roi.max())]
}
summary = {
  "analysis": "one-sample equal-weight random-effects t test; positive gain effect",
  "n": n, "df": n-1, "mask_voxels": v, "permutations": N_PERM,
  "permutation_seed": SEED, "test": "one-sided sign-flip max-T voxelwise family-wise error control",
  "alpha": ALPHA, "vmPFC_roi_definition_mni_mm": {"x": [-15,15], "y": [20,55], "z": [-20,5]},
  "vmPFC_roi_role": "descriptive summary only; confirmatory inference uses full brain mask",
  "vmPFC_roi_mean_effect": float(roi_mean), "vmPFC_roi_sd_between_participants": float(roi_sd),
  "vmPFC_roi_se": float(roi_se), "vmPFC_roi_95ci": [float(roi_ci[0]), float(roi_ci[1])],
  "vmPFC_roi_t": float(roi_t), "vmPFC_roi_uncorrected_one_sided_p": float(roi_p),
  "whole_brain_maxT_fwe_significant_voxels": sig_count,
  "peak_if_significant_mni_mm": None if peak_xyz is None else [float(q) for q in peak_xyz],
  "peak_t": peak_t, "peak_p_fwe": peak_pfwe,
  "most_extreme_wholebrain_t": float(tobs.max()), "most_extreme_wholebrain_mni_mm": [float(q) for q in nib.affines.apply_affine(ref.affine, np.argwhere(mask)[np.argmax(tobs)])],
  "maxT_95pct_critical_t": float(np.quantile(max_t, .95)),
  "n_voxels_uncorrected_p_lt_0_001": int((p_unc < .001).sum()),
  "qc": qc
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

# Figure 1: group t statistic on sagittal and coronal slices, with vmPFC envelope outline.
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
plotting.plot_stat_map(t_img, bg_img=datasets.load_mni152_template(resolution=2),
    display_mode="x", cut_coords=[0], threshold=stats.t.ppf(.999, n-1),
    cmap="cold_hot", colorbar=True, vmax=max(4, float(np.nanpercentile(tobs,99.9))),
    axes=axes[0], title="Group t map (display threshold p < .001 uncorrected)")
plotting.plot_stat_map(t_img, bg_img=datasets.load_mni152_template(resolution=2),
    display_mode="y", cut_coords=[35], threshold=stats.t.ppf(.999, n-1),
    cmap="cold_hot", colorbar=True, vmax=max(4, float(np.nanpercentile(tobs,99.9))),
    axes=axes[1], title="Coronal view through vmPFC")
fig.suptitle("NARPS equal-indifference gain effect (n=54)", fontsize=13)
fig.tight_layout()
fig.savefig(FIG / "group_t_map.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Corrected whole-brain findings, plotted at the peak and vmPFC midsagittal plane.
fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
for ax, mode, coord, title in [
    (axes[0], "x", -26, "Sagittal: peak x = -26"),
    (axes[1], "y", -102, "Coronal: peak y = -102"),
    (axes[2], "z", -4, "Axial: peak z = -4"),
]:
    plotting.plot_stat_map(sig_t_img, bg_img=datasets.load_mni152_template(resolution=2),
        display_mode=mode, cut_coords=[coord], threshold=0, cmap="cold_hot",
        colorbar=True, axes=ax, title=title)
fig.suptitle("Positive voxels surviving one-sided whole-brain max-T FWE (p ≤ .05)", fontsize=12)
fig.tight_layout()
fig.savefig(FIG / "whole_brain_fwe_findings.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Figure 2: participant vmPFC ROI effect distribution and group estimate.
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.scatter(np.arange(1,n+1), subj_roi, s=24, color="#345995", alpha=.8)
ax.axhline(roi_mean, color="#c44536", lw=2, label=f"Mean = {roi_mean:.3f}")
ax.axhspan(roi_ci[0], roi_ci[1], color="#c44536", alpha=.15, label="95% t interval")
ax.axhline(0, color="black", lw=.8)
ax.set(xlabel="Participant (ordered by ID)", ylabel="Mean gain contrast estimate in vmPFC core", title="Participant-level vmPFC gain effect")
ax.legend(frameon=False); fig.tight_layout()
fig.savefig(FIG / "vmPFC_participant_effects.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print(json.dumps(summary, indent=2))
