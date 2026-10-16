#!/usr/bin/env python3
"""Group inference for NARPS AO86 equal-indifference gain-effect maps.

Primary test: one-sample, one-sided sign-flip max-T inference across the
whole common-support brain mask. This does not reconstruct the upstream model.
"""
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
import scipy
import nilearn
import matplotlib
from nilearn import datasets, image, plotting
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
N_PERM = 10_000
SEED = 20261016
CHUNK = 256


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def save_img(values: np.ndarray, ref: nib.spatialimages.SpatialImage, path: Path,
             dtype=np.float32) -> None:
    data = np.zeros(ref.shape, dtype=dtype)
    data[mask] = values.astype(dtype)
    nib.save(nib.Nifti1Image(data, ref.affine, ref.header), path)


def t_obs_to_volume(values, m, shape):
    out = np.zeros(shape, dtype=np.float32)
    out[m] = values
    return out


participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
manifest = json.loads((ROOT / "input/sources.json").read_text())
records = manifest["files"]
expected = participants.participant_id.tolist()
assert len(expected) == 54 and len(set(expected)) == 54
assert set(expected) == {v["participant_id"] for k, v in records.items() if k.endswith(".nii.gz")}
paths = [ROOT / f"input/data/{pid}_hypo1_cope.nii.gz" for pid in expected]
imgs = [nib.load(str(p)) for p in paths]
ref = imgs[0]
assert all(img.shape == ref.shape and np.allclose(img.affine, ref.affine) for img in imgs)

# Verify each delivered file against the retrieved-byte hashes in the manifest.
hash_checks = []
for p in paths:
    expected_hash = records[f"data/{p.name}"]["sha256"]
    actual_hash = sha256(p)
    if actual_hash != expected_hash:
        raise ValueError(f"Checksum mismatch: {p.name}")
    hash_checks.append({"file": p.name, "sha256": actual_hash, "match": True})

vols = np.stack([np.asarray(im.dataobj, dtype=np.float32) for im in imgs])
if not np.isfinite(vols).all():
    raise ValueError("Non-finite values found")
coverage = np.mean(vols != 0, axis=0)
# Nonzero support is determined without reference to the sign or size of effect.
# Retain voxels represented in at least 90% of participants.
mask = coverage >= 0.90
if mask.sum() < 10_000:
    raise ValueError(f"Unexpectedly small common support: {mask.sum()}")
X = vols[:, mask].astype(np.float64)
n, v = X.shape

# Primary one-sample t statistic and its conventional uncorrected summary.
mu = X.mean(axis=0)
sd = X.std(axis=0, ddof=1)
t_obs = mu / (sd / np.sqrt(n))
p_unc = stats.t.sf(t_obs, df=n - 1)
ci_lo = mu - stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
ci_hi = mu + stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)

# Monte-Carlo sign-flips, studentized at each voxel. The maximum positive t
# from each whole-brain permutation gives one-sided family-wise error control.
rng = np.random.default_rng(SEED)
null_max = np.empty(N_PERM, dtype=np.float32)
sum_sq = np.sum(X * X, axis=0)
for start in range(0, N_PERM, CHUNK):
    stop = min(start + CHUNK, N_PERM)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(stop - start, n))
    signed_sums = signs @ X
    means = signed_sums / n
    variances = np.maximum((sum_sq[None, :] - signed_sums**2 / n) / (n - 1), 1e-20)
    t_perm = means / np.sqrt(variances / n)
    null_max[start:stop] = t_perm.max(axis=1)
sorted_null_max = np.sort(null_max)
p_fwe = (1 + N_PERM - np.searchsorted(sorted_null_max, t_obs, side="left")) / (N_PERM + 1)
global_p = (1 + np.count_nonzero(null_max >= t_obs.max())) / (N_PERM + 1)
sig = p_fwe <= 0.05

save_img(mu, ref, OUT / "group_mean_cope.nii.gz")
save_img(t_obs, ref, OUT / "group_t.nii.gz")
save_img(-np.log10(p_unc), ref, OUT / "minus_log10_p_uncorrected.nii.gz")
save_img(-np.log10(p_fwe), ref, OUT / "minus_log10_p_fwe.nii.gz")
save_img(sig.astype(float), ref, OUT / "significant_fwe05.nii.gz")
nib.save(nib.Nifti1Image(mask.astype(np.uint8), ref.affine, ref.header), OUT / "analysis_mask.nii.gz")

# Atlas-defined vmPFC summary, independently specified from activation results.
# Harvard-Oxford cortical maximum-probability atlas, 25% threshold; medial
# frontal plus subcallosal labels operationalize a conservative vmPFC region.
atlas = datasets.fetch_atlas_harvard_oxford(
    "cort-maxprob-thr25-2mm", data_dir=str(OUT / "atlas"), verbose=0
)
atlas_on_ref = image.resample_to_img(atlas.maps, ref, interpolation="nearest")
atlas_data = np.asarray(atlas_on_ref.dataobj)
labels = list(atlas.labels)
roi_names = ["Frontal Medial Cortex", "Subcallosal Cortex"]
roi_codes = [labels.index(x) for x in roi_names]
roi_mask_img = np.isin(atlas_data, roi_codes) & mask
roi_mask = roi_mask_img[mask]
if roi_mask.sum() == 0:
    raise ValueError("Empty vmPFC mask after atlas resampling")
roi_values = X[:, roi_mask].mean(axis=1)
roi_mu = float(roi_values.mean())
roi_sd = float(roi_values.std(ddof=1))
roi_sem = roi_sd / np.sqrt(n)
roi_t = roi_mu / roi_sem
roi_p_one = float(stats.t.sf(roi_t, n - 1))
roi_ci = [float(roi_mu - stats.t.ppf(.975, n - 1) * roi_sem),
          float(roi_mu + stats.t.ppf(.975, n - 1) * roi_sem)]
roi_loo = np.array([(np.delete(roi_values, i)).mean() for i in range(n)])
roi_labels_img = nib.Nifti1Image(roi_mask_img.astype(np.uint8), ref.affine, ref.header)
nib.save(roi_labels_img, OUT / "vmPFC_atlas_roi.nii.gz")

# Concise reproducible QC: per-person robust center, spread, and extremum.
qc = pd.DataFrame({
    "participant_id": expected,
    "mean_cope_in_mask": X.mean(axis=1),
    "median_cope_in_mask": np.median(X, axis=1),
    "sd_cope_in_mask": X.std(axis=1, ddof=1),
    "max_abs_cope_in_mask": np.max(np.abs(X), axis=1),
    "vmPFC_mean_cope": roi_values,
})
qc.to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)
pd.DataFrame({"max_t_null": null_max}).to_csv(OUT / "permutation_max_t.tsv", sep="\t", index=False)

# Figure 1: unthresholded t map with whole-brain significant voxels outlined.
template_path = OUT / "atlas/mni152_template_2mm.nii.gz"
if not template_path.exists():
    nib.save(datasets.load_mni152_template(resolution=2), template_path)
disp = plotting.plot_stat_map(
    nib.Nifti1Image(t_obs_to_volume(t_obs, mask, ref.shape), ref.affine),
    bg_img=nib.load(str(template_path)), display_mode="ortho",
    cut_coords=(0, 35, -8), threshold=stats.t.ppf(.99, n-1),
    cmap="cold_hot", colorbar=True, title="Gain coefficient: group t map (uncorrected display)"
)
# Display the FWE-significant mask contours if any.
if sig.any():
    sig_img = nib.Nifti1Image(t_obs_to_volume(sig.astype(float), mask, ref.shape), ref.affine)
    disp.add_contours(sig_img, levels=[0.5], colors="lime", linewidths=1.5)
disp.add_contours(roi_labels_img, levels=[0.5], colors="cyan", linewidths=1.2)
disp.savefig(OUT / "figure1_whole_brain.png", dpi=180)
disp.close()

# Figure 2: subject-level average cope estimate inside the independent ROI.
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2), constrained_layout=True)
rng_plot = np.random.default_rng(SEED)
ax.scatter(rng_plot.normal(0, .045, size=n), roi_values, color="#245a81", alpha=.75, s=24, linewidth=0)
ax.errorbar(0, roi_mu, yerr=[[roi_mu-roi_ci[0]], [roi_ci[1]-roi_mu]], fmt="D", color="#bd4b32", capsize=5, ms=7, label="Mean and 95% CI")
ax.axhline(0, color="0.4", lw=1)
ax.set(xlim=(-.18, .18), xticks=[], ylabel="Mean gain-effect coefficient in vmPFC ROI",
       title="Equal-indifference participants (n=54)")
ax.legend(frameon=False, loc="best")
fig.savefig(OUT / "figure2_vmPFC_participants.png", dpi=180)
plt.close(fig)

result = {
    "analysis": "one-sample one-sided positive sign-flip max-T",
    "n": n,
    "n_voxels": int(v),
    "permutations": N_PERM,
    "random_seed": SEED,
    "null": "participant-wise sign symmetry around zero; studentized t statistic",
    "whole_brain_correction": "one-sided max statistic across all common-support voxels",
    "t_max_observed": float(t_obs.max()),
    "global_fwe_p": float(global_p),
    "min_voxelwise_fwe_p": float(p_fwe.min()),
    "n_voxels_fwe05": int(sig.sum()),
    "peak_mni_xyz": [float(x) for x in nib.affines.apply_affine(ref.affine, np.argwhere(mask)[int(np.argmax(t_obs))])],
    "peak_t": float(t_obs.max()),
    "peak_uncorrected_p": float(p_unc.min()),
    "atlas": "Harvard-Oxford cortical max-probability, 25% threshold, resampled nearest-neighbor",
    "vmPFC_roi_labels": roi_names,
    "vmPFC_voxels": int(roi_mask.sum()),
    "vmPFC_mean_cope": roi_mu,
    "vmPFC_sd_between_subjects": roi_sd,
    "vmPFC_t_df53": float(roi_t),
    "vmPFC_one_sided_uncorrected_p_descriptive": roi_p_one,
    "vmPFC_two_sided_95pct_ci": roi_ci,
    "vmPFC_leave_one_out_mean_range": [float(roi_loo.min()), float(roi_loo.max())],
    "vmPFC_FWE05_voxels": int((sig & roi_mask).sum()),
    "mask_rule": "nonzero cope support in >=90% of participants; no effect-direction selection",
    "mask_voxels": int(mask.sum()),
    "hash_verified": len(hash_checks),
    "input_hash_checks": hash_checks,
    "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "nibabel": nib.__version__, "nilearn": nilearn.__version__, "matplotlib": matplotlib.__version__},
}
(OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "input_hash_checks"}, indent=2))
