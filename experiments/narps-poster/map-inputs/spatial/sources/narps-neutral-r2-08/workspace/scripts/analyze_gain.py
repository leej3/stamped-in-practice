#!/usr/bin/env python3
"""Group inference for the NARPS equal-indifference gain-effect maps."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib
import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from nilearn import datasets, image, plotting
import nilearn
from scipy import ndimage, stats
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
SEED = 20261016
N_PERM = 4999


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


manifest = json.loads((INPUT / "sources.json").read_text())
participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
assert participants.participant_id.is_unique
assert len(participants) == 54 and set(participants.group) == {"equalIndifference"}
files = []
for rel, meta in manifest["files"].items():
    if not rel.endswith("_hypo1_cope.nii.gz"):
        continue
    path = INPUT / rel
    assert path.stat().st_size == meta["bytes"], (rel, path.stat().st_size)
    assert sha256(path) == meta["sha256"], rel
    files.append((meta["participant_id"], path))
assert {pid for pid, _ in files} == set(participants.participant_id)
files.sort()

imgs = [nib.load(str(path)) for _, path in files]
ref = imgs[0]
assert all(im.shape == ref.shape and np.allclose(im.affine, ref.affine) for im in imgs)
arr = np.stack([im.get_fdata(dtype=np.float32) for im in imgs])
assert np.isfinite(arr).all()
coverage = np.count_nonzero(arr, axis=(1, 2, 3))
# All supplied maps share an analysis mask; its intersection avoids changing the
# search space by participant and excludes zero-filled locations outside it.
mask = np.all(arr != 0, axis=0)
if mask.sum() < 100_000:
    raise RuntimeError(f"Unexpectedly small common support mask: {mask.sum()}")
Y = arr[:, mask].astype(np.float64)
n, v = Y.shape

# One-sample t statistic for the directional group mean (> 0).
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(n))
p_unc = stats.t.sf(t_obs, df=n - 1)

# Random sign-flip maximum-t correction controls one-sided whole-brain FWE.
# This is valid under independent, symmetric participant-level errors under H0.
# Denominator uses the sign-invariant sum of squares and the permuted mean.
rng = np.random.default_rng(SEED)
max_t = np.empty(N_PERM, dtype=np.float32)
ss = np.sum(Y * Y, axis=0)
den0 = np.sqrt(np.maximum(ss, 1e-20) / (n * (n - 1)))
with threadpool_limits(limits=6):
    for start in range(0, N_PERM, 256):
        stop = min(start + 256, N_PERM)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(stop - start, n))
        maxima = np.full(stop - start, -np.inf)
        for j in range(0, v, 8192):
            e = min(j + 8192, v)
            signed_sum = signs @ Y[:, j:e]
            denom = np.sqrt(np.maximum(ss[j:e][None, :] - signed_sum**2 / n, 1e-20) / (n * (n - 1)))
            # signed_sum is a sum; divide by n to obtain the permuted mean.
            maxima = np.maximum(maxima, np.max((signed_sum / n) / denom, axis=1))
        max_t[start:stop] = maxima
    p_fwe = (1 + np.sum(max_t[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)

sig = p_fwe < 0.05
vol_shape = ref.shape
def as_img(values, dtype=np.float32):
    out = np.zeros(vol_shape, dtype=dtype)
    out[mask] = values
    return nib.Nifti1Image(out, ref.affine, ref.header)

mean_img = as_img(mean)
t_img = as_img(t_obs)
p_out = np.full(vol_shape, np.nan, dtype=np.float32)
p_out[mask] = p_fwe
p_img = nib.Nifti1Image(p_out, ref.affine, ref.header)
for name, im in [("mean_gain_effect.nii.gz", mean_img), ("t_gain_effect.nii.gz", t_img),
                 ("p_fwe_gain_effect.nii.gz", p_img)]:
    nib.save(im, OUT / name)
nib.save(as_img(sig.astype(np.uint8), dtype=np.uint8), OUT / "significant_fwe05.nii.gz")

# Independent anatomical definition: the bilateral AAL3 medial orbital frontal
# parcels, used as an anatomical vmPFC proxy. This summarizes the target; the
# confirmatory result remains the whole-brain corrected analysis above.
aal = datasets.fetch_atlas_aal(version="3v2")
atlas = image.load_img(aal.maps)
atlas_r = image.resample_to_img(atlas, ref, interpolation="nearest")
atlas_data = atlas_r.get_fdata().astype(int)
labels = [str(x.decode() if isinstance(x, bytes) else x) for x in aal.labels]
target_names = ["Frontal_Med_Orb_L", "Frontal_Med_Orb_R"]
label_index = {name: i for i, name in enumerate(labels)}
target_ids = [label_index[x] for x in target_names]
roi = mask & np.isin(atlas_data, target_ids)
roi_data = arr[:, roi]
roi_mean = roi_data.mean(axis=1)
roi_t = stats.ttest_1samp(roi_mean, 0, alternative="greater")
roi_ci = stats.t.interval(0.95, n-1, loc=roi_mean.mean(), scale=stats.sem(roi_mean))
roi_wilcoxon = stats.wilcoxon(roi_mean, alternative="greater", zero_method="wilcox", method="auto")
loo_min = min(np.delete(roi_mean, i).mean() for i in range(n))
loo_max = max(np.delete(roi_mean, i).mean() for i in range(n))

# Connected components in the original 3-D mask.
sig3 = np.zeros(vol_shape, dtype=bool); sig3[mask] = sig
clab, ncl = ndimage.label(sig3)
clusters = []
for k in range(1, ncl + 1):
    ijk = np.argwhere(clab == k)
    peak_flat = np.flatnonzero((clab == k) & (t_img.get_fdata() == np.max(t_img.get_fdata()[clab == k])))[0]
    xyz = nib.affines.apply_affine(ref.affine, np.array(np.unravel_index(peak_flat, vol_shape)))
    clusters.append({"voxels": int(len(ijk)), "peak_t": float(t_img.get_fdata()[clab == k].max()),
                     "peak_mni_mm": [float(z) for z in xyz]})
clusters.sort(key=lambda q: q["voxels"], reverse=True)

res = {
    "n_expected": 54, "n_included": n, "n_excluded": [],
    "input_manifest_checksums_verified": True,
    "shape": list(vol_shape), "voxel_size_mm": [float(abs(x)) for x in ref.header.get_zooms()[:3]],
    "common_nonzero_mask_voxels": int(v), "common_mask_percent_of_grid": float(v / np.prod(vol_shape) * 100),
    "participant_nonzero_voxel_range": [int(coverage.min()), int(coverage.max())],
    "participants_age_mean_sd": [float(participants.age.mean()), float(participants.age.std(ddof=1))],
    "group_counts_gender": participants.gender.value_counts().to_dict(),
    "software_versions": {"python": "3.13", "numpy": np.__version__, "scipy": scipy.__version__,
        "pandas": pd.__version__, "nibabel": nib.__version__, "nilearn": nilearn.__version__,
        "matplotlib": matplotlib.__version__},
    "permutation": {"method": "one-sided random sign-flip maximum-t", "n_randomizations": N_PERM,
                    "seed": SEED, "minimum_attainable_p": 1/(N_PERM+1),
                    "max_t_95_percentile": float(np.quantile(max_t, .95)),
                    "max_t_99_percentile": float(np.quantile(max_t, .99)),
                    "significant_voxels_p_fwe_lt_0_05": int(sig.sum()),
                    "minimum_voxelwise_fwe_p": float(p_fwe.min()),
                    "peak_t": float(t_obs.max()), "peak_uncorrected_p": float(p_unc.min()),
                    "clusters": clusters},
    "vmPFC_anatomical_summary": {"atlas": "AAL3 v1", "labels": target_names,
        "mask_voxels": int(roi.sum()), "mean_participant_effect": float(roi_mean.mean()),
        "sd_participant_effect": float(roi_mean.std(ddof=1)),
        "ci95_t": [float(roi_ci[0]), float(roi_ci[1])], "t_one_sample_one_sided": float(roi_t.statistic),
        "p_one_sample_one_sided_unadjusted": float(roi_t.pvalue),
        "wilcoxon_one_sided_unadjusted": float(roi_wilcoxon.pvalue),
        "leave_one_out_mean_range": [float(loo_min), float(loo_max)],
        "significant_voxels_p_fwe_lt_0_05": int(np.sum(p_fwe[roi[mask]] < .05))},
}
(OUT / "summary.json").write_text(json.dumps(res, indent=2))
pd.DataFrame({"participant_id": [x[0] for x in files], "roi_mean_effect": roi_mean}).to_csv(OUT / "participant_vmPFC_effects.tsv", sep="\t", index=False)
pd.DataFrame({"max_t": max_t}).to_csv(OUT / "permutation_max_t.tsv.gz", sep="\t", index=False, compression="gzip")

# Figure 1: mean estimate and only the voxels surviving whole-brain correction.
fig, axes = plt.subplots(2, 3, figsize=(12.5, 6.5), constrained_layout=True)
views = [("x", -26, "Sagittal x = -26"), ("y", -98, "Coronal y = -98"), ("z", -4, "Axial z = -4")]
for ax, (mode, coord, title) in zip(axes[0], views):
    plotting.plot_stat_map(mean_img, display_mode=mode, cut_coords=[coord], threshold=0,
                           cmap="cold_hot", colorbar=True, axes=ax, figure=fig,
                           vmin=-0.15, vmax=0.15, annotate=False)
    ax.text(.5, 1.02, title + " · mean", transform=ax.transAxes, ha="center", va="bottom", fontsize=10)
fwe_height = float(np.quantile(max_t, .95))
for ax, (mode, coord, title) in zip(axes[1], views):
    plotting.plot_stat_map(t_img, display_mode=mode, cut_coords=[coord], threshold=fwe_height,
                           cmap="inferno", colorbar=True, axes=ax, figure=fig,
                           vmin=fwe_height, vmax=max(fwe_height + .1, float(t_obs.max())), annotate=False)
    ax.text(.5, 1.02, title + " · FWE p<.05", transform=ax.transAxes, ha="center", va="bottom", fontsize=10)
fig.suptitle("Positive gain-effect group response: mean estimates and corrected voxels", fontsize=14)
fig.savefig(FIG / "whole_brain_gain_effect.png", dpi=180)
plt.close(fig)

# Figure 2: participant ROI estimates and group mean with t-based CI.
fig, ax = plt.subplots(figsize=(7.0, 4.4), constrained_layout=True)
ax.axhline(0, color="0.3", lw=1)
jit = np.random.default_rng(SEED).normal(0, .015, n)
ax.scatter(roi_mean, jit, s=27, alpha=.75, color="#315b7d", edgecolors="white", linewidths=.35)
ax.errorbar(roi_mean.mean(), -.09, xerr=[[roi_mean.mean()-roi_ci[0]], [roi_ci[1]-roi_mean.mean()]],
            fmt="D", color="#b44632", capsize=5, lw=2, label="Mean and 95% t CI")
ax.set(yticks=[], xlabel="Mean gain-effect estimate in AAL3 vmPFC parcels (arbitrary model units)",
       title="Participant-level vmPFC summary (n=54)")
ax.legend(frameon=False, loc="best")
fig.savefig(FIG / "vmPFC_participant_effects.png", dpi=180)
plt.close(fig)

print(json.dumps(res, indent=2))
