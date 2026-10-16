#!/usr/bin/env python3
"""Group analysis of the supplied NARPS AO86 participant gain-effect maps."""
from pathlib import Path
import json
import hashlib

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import plotting
from nilearn import datasets
from nilearn.mass_univariate import permuted_ols
from nilearn.image import resample_to_img
from scipy import stats

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "input" / "data"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
N_PERM = 5000
SEED = 20261016

participants = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
files = sorted(DATA.glob("*_hypo1_cope.nii.gz"))
assert len(files) == len(participants) == 54
assert set(p.stem.split("_")[0] for p in files) == set(participants.participant_id)

# Check grid consistency, finite values, and the retrieved-byte checksums recorded
# in sources.json. Construct a conservative common brain mask from nonzero support.
manifest = json.loads((ROOT / "input" / "sources.json").read_text())
arrays = []
first = nib.load(str(files[0]))
checks = []
for path in files:
    img = nib.load(str(path))
    if img.shape != first.shape or not np.allclose(img.affine, first.affine, atol=1e-5):
        raise ValueError(f"Grid mismatch: {path}")
    arr = img.get_fdata(dtype=np.float32)
    if not np.isfinite(arr).all():
        raise ValueError(f"Non-finite image values: {path}")
    arrays.append(arr)
    expected = manifest["files"][f"data/{path.name}"]["sha256"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected:
        raise ValueError(f"SHA256 mismatch for {path.name}")
    checks.append({"participant_id": path.name.split("_")[0], "shape": list(img.shape),
                   "min": float(arr.min()), "max": float(arr.max()),
                   "nonzero_voxels": int(np.count_nonzero(arr)), "sha256_verified": True})
Y = np.stack(arrays, axis=0)
# Intersect a standard MNI152 brain mask, resampled nearest-neighbor to the
# supplied MNI152NLin2009cAsym grid, with shared map support. The support rule
# excludes outside-brain zero padding without requiring an overly strict
# all-subject intersection.
support = np.count_nonzero(Y, axis=0) >= int(np.ceil(0.90 * Y.shape[0]))
template_brain_mask = datasets.load_mni152_brain_mask(resolution=2)
brain_mask_img = resample_to_img(template_brain_mask, first, interpolation="nearest")
mask = support & (brain_mask_img.get_fdata() > 0)
if mask.sum() == 0:
    raise ValueError("Empty common-support mask")
Yv = np.ascontiguousarray(Y[:, mask])
n, p = Yv.shape

# One-sample OLS (intercept tested): H1 mean effect > 0. Nilearn's Freedman-Lane
# permutation procedure supplies max-t FWE p-values over all masked voxels.
result = permuted_ols(
    tested_vars=np.ones((n, 1), dtype=np.float64),
    target_vars=Yv,
    model_intercept=True,
    n_perm=N_PERM,
    two_sided_test=False,
    random_state=SEED,
    n_jobs=4,
    output_type="dict",
)
print("permuted_ols keys", result.keys())

# Calculate ordinary one-sample t and mean maps for interpretable estimates.
mean = Yv.mean(axis=0)
sd = Yv.std(axis=0, ddof=1)
se = sd / np.sqrt(n)
t_obs = mean / se
df = n - 1
p_unc = stats.t.sf(t_obs, df)
ci_lo = mean - stats.t.ppf(.975, df) * se
ci_hi = mean + stats.t.ppf(.975, df) * se

def extract_result(key):
    a = np.asarray(result[key]).squeeze()
    return a

for k, v in result.items():
    print(k, np.shape(v), (np.nanmin(v), np.nanmax(v)) if np.size(v) else "empty")

# The dict output's first two maps are the FWE negative-log10 p values and t
# statistics; preserve all arrays and fail loudly if API output changes.
logp_fwe = extract_result("logp_max_t")
if logp_fwe.size != p:
    raise RuntimeError("Unexpected permuted_ols logp_max_t shape")
p_fwe = 10.0 ** (-logp_fwe)

def unmask(vals, dtype=np.float32):
    full = np.zeros(mask.shape, dtype=dtype)
    full[mask] = vals
    return nib.Nifti1Image(full, first.affine, first.header)

mean_img = unmask(mean)
t_img = unmask(t_obs)
# Outside-mask values are set to 1 (not 0) so the p map cannot imply
# significance in locations that were excluded from inference.
p_full = np.ones(mask.shape, dtype=np.float32)
p_full[mask] = p_fwe
p_img = nib.Nifti1Image(p_full, first.affine, first.header)
sig_img = unmask(np.where(p_fwe <= .05, t_obs, 0.0))
nib.save(mean_img, OUT / "group_mean_gain_effect.nii.gz")
nib.save(t_img, OUT / "group_t.nii.gz")
nib.save(p_img, OUT / "fwe_p.nii.gz")
nib.save(sig_img, OUT / "positive_fwe_p05_t.nii.gz")

# Whole-brain family-wise corrected cluster inventory (26-connected components).
from scipy.ndimage import label
sig = (p_fwe <= .05) & (t_obs > 0)
sig_full = unmask(sig.astype(np.uint8), dtype=np.uint8).get_fdata().astype(bool)
labels, nlab = label(sig_full)
clusters = []
for lab in range(1, nlab + 1):
    xyz = np.argwhere(labels == lab)
    # index in masked vector is recovered from full voxel flat indices
    flat = np.ravel_multi_index(xyz.T, mask.shape)
    maskflat = np.flatnonzero(mask.ravel())
    inds = np.searchsorted(maskflat, flat)
    peak_ind = inds[np.argmax(t_obs[inds])]
    ijk = np.array(np.unravel_index(np.flatnonzero(mask)[peak_ind], mask.shape))
    peak_xyz = nib.affines.apply_affine(first.affine, ijk)
    clusters.append({"cluster": lab, "voxels": int(len(xyz)), "peak_x": float(peak_xyz[0]),
                     "peak_y": float(peak_xyz[1]), "peak_z": float(peak_xyz[2]),
                     "peak_t": float(t_obs[peak_ind]), "peak_mean": float(mean[peak_ind]),
                     "peak_p_fwe": float(p_fwe[peak_ind])})
pd.DataFrame(clusters).to_csv(OUT / "fwe_clusters.csv", index=False)

# Transparent anatomical locator: bilateral midline ventral/anterior MNI search
# zone (|x|<=20, y=0..60, z=-25..10 mm). This broad coordinate-defined box is
# a descriptive operationalization, not a cytoarchitectonic boundary or an
# independent confirmatory ROI. The whole-brain max-T result remains primary.
ijk_all = np.array(np.unravel_index(np.flatnonzero(mask), mask.shape)).T
xyz_all = nib.affines.apply_affine(first.affine, ijk_all)
vm_mask = ((np.abs(xyz_all[:, 0]) <= 20) & (xyz_all[:, 1] >= 0) &
           (xyz_all[:, 1] <= 60) & (xyz_all[:, 2] >= -25) & (xyz_all[:, 2] <= 10))
vm_idx = np.flatnonzero(vm_mask)
if not len(vm_idx):
    raise ValueError("No common-mask voxels in coordinate-defined vmPFC search zone")
roi_subject = Yv[:, vm_idx].mean(axis=1)
roi_mean = float(roi_subject.mean())
roi_se = float(stats.sem(roi_subject))
roi_t, roi_p_two = stats.ttest_1samp(roi_subject, 0.0)
roi_p_positive = float(stats.t.sf(roi_t, n - 1))
roi_ci = stats.t.interval(.95, n - 1, loc=roi_mean, scale=roi_se)
roi_peak = vm_idx[np.argmax(t_obs[vm_idx])]
roi_metrics = {
    "definition_mni_mm": "|x|<=20, 0<=y<=60, -25<=z<=10",
    "voxels": int(len(vm_idx)), "n_participants": n,
    "mean_of_subject_roi_means": roi_mean,
    "sd_subject_roi_means": float(np.std(roi_subject, ddof=1)),
    "ci95_t": [float(roi_ci[0]), float(roi_ci[1])],
    "t_53": float(roi_t), "p_one_sided_nominal": roi_p_positive,
    "p_two_sided_nominal": float(roi_p_two),
    "peak_xyz_mni_mm": [float(x) for x in xyz_all[roi_peak]],
    "peak_t": float(t_obs[roi_peak]), "peak_whole_brain_fwe_p": float(p_fwe[roi_peak]),
    "interpretation": "exploratory regional summary; not an atlas-defined or preregistered independent ROI test",
}
(OUT / "vmPFC_search_zone.json").write_text(json.dumps(roi_metrics, indent=2))
pd.DataFrame({"participant_id": [f.name.split("_")[0] for f in files],
              "mean_gain_effect_in_coordinate_vmPFC_zone": roi_subject}).to_csv(
                  OUT / "vmPFC_search_zone_subject_values.csv", index=False)

# Quality-control and descriptive summaries.
rows = []
for i, path in enumerate(files):
    v = Y[i][mask]
    rows.append({"participant_id": path.name.split("_")[0], "age": int(participants.set_index("participant_id").loc[path.name.split("_")[0], "age"]),
                 "gain_map_mean": float(v.mean()), "gain_map_sd": float(v.std(ddof=1)),
                 "gain_map_median": float(np.median(v)), "finite": bool(np.isfinite(v).all())})
pd.DataFrame(rows).to_csv(OUT / "participant_qc_summary.csv", index=False)
summary = {
    "participants": n, "excluded": [], "mask_voxels": int(p),
    "mask_rule": "MNI152 brain mask intersected with voxels nonzero in >=90% of participants",
    "shape": list(first.shape), "affine": first.affine.tolist(),
    "permutations": N_PERM, "seed": SEED, "df_ordinary_t": df,
    "test": "one-sample OLS intercept, positive one-sided; permutation max-T FWE over whole mask",
    "max_observed_t": float(np.nanmax(t_obs)),
    "min_fwe_p": float(np.nanmin(p_fwe)),
    "voxels_fwe_p_le_05": int(sig.sum()),
    "grand_mean_voxel_effect": float(mean.mean()),
    "grand_mean_voxel_effect_sd_across_voxels": float(mean.std(ddof=1)),
    "checks": checks,
}
(OUT / "analysis_summary.json").write_text(json.dumps(summary, indent=2))

# Figures: corrected whole-brain findings and unthresholded vmPFC estimate.
template = datasets.load_mni152_template(resolution=2)
plotting.plot_stat_map(sig_img, bg_img=template, display_mode="z",
                       cut_coords=[-12, -4, 4, 12, 20, 28, 36], cmap="cold_hot",
                       threshold=0, colorbar=True,
                       title="Positive gain effect: whole-brain max-T FWE p ≤ .05",
                       output_file=str(FIG / "whole_brain_fwe_anatomical.png"))
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 4.4), constrained_layout=True)
ax.scatter(np.ones(n) + np.linspace(-.09, .09, n), roi_subject, s=22,
           color="#426a8c", alpha=.75, edgecolor="white", linewidth=.3)
ax.errorbar(1, roi_mean, yerr=[[roi_mean-roi_ci[0]], [roi_ci[1]-roi_mean]],
            fmt="D", color="#b44b39", capsize=5, markersize=7, linewidth=2,
            label="Mean and 95% t interval")
ax.axhline(0, color="black", linewidth=1, linestyle="--")
ax.set(xlim=(.75, 1.25), xticks=[1], xticklabels=["vmPFC search zone"],
       ylabel="Participant mean gain-effect estimate", title="Subject-level regional estimates")
ax.legend(frameon=False, loc="best")
fig.savefig(FIG / "vmPFC_subject_estimates.png", dpi=180)
plt.close(fig)
print(json.dumps({k: v for k, v in summary.items() if k != "checks"}, indent=2))
print("vmPFC search zone", json.dumps(roi_metrics))
