#!/usr/bin/env python3
"""One-sample gain-effect group analysis with whole-brain max-t sign flips."""
from __future__ import annotations

import json
import pathlib
import platform
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
manifest = json.loads((ROOT / "input/sources.json").read_text())
participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
map_items = [(p, x) for p, x in manifest["files"].items() if p.endswith(".nii.gz")]
map_items.sort(key=lambda x: x[1]["participant_id"])
ids = [v["participant_id"] for _, v in map_items]
assert len(ids) == 54 and len(set(ids)) == len(ids)
assert set(ids) == set(participants.participant_id)
assert (participants.set_index("participant_id").loc[ids, "group"] == "equalIndifference").all()

imgs = [nib.load(ROOT / rel) for rel, _ in map_items]
shape, affine = imgs[0].shape, imgs[0].affine
assert all(im.shape == shape and np.allclose(im.affine, affine, atol=1e-5) for im in imgs)
stack = np.stack([im.get_fdata(dtype=np.float32) for im in imgs])
assert np.isfinite(stack).all()
# In these effect maps, exact zero denotes no modeled voxel support. Requiring
# support in all participant maps avoids treating uncovered voxels as zero effects.
mask = np.all(stack != 0, axis=0)
assert mask.sum() > 1000
X = stack[:, mask].astype(np.float64)
n, v = X.shape
assert n == 54 and np.isfinite(X).all()

means = X.mean(axis=0)
sd = X.std(axis=0, ddof=1)
se = sd / np.sqrt(n)
t_obs = means / se
df = n - 1
p_unc = stats.t.sf(t_obs, df)

# Null symmetry permits participant-level sign flips. The maximum positive t
# across the full analysis mask controls one-sided voxelwise whole-brain FWE.
N_PERM = 9999
SEED = 20261016
rng = np.random.default_rng(SEED)
sum_sq = np.square(X).sum(axis=0)
max_null = np.empty(N_PERM, dtype=np.float64)
batch = 100
for start in range(0, N_PERM, batch):
    stop = min(start + batch, N_PERM)
    signs = rng.choice(np.array([-1., 1.]), size=(stop - start, n))
    sums = signs @ X
    # For each sign-flipped sample: t = sum(x)/(sqrt((sum(x^2)-sum(x)^2/n)/(n-1))/sqrt(n)).
    var = np.maximum((sum_sq[None, :] - np.square(sums) / n) / (n - 1), 0.)
    t_perm = (sums / n) / np.sqrt(var / n)
    max_null[start:stop] = np.max(t_perm, axis=1)
p_fwe = (1 + (max_null[:, None] >= t_obs[None, :]).sum(axis=0)) / (N_PERM + 1)

# A conservative analytic Bonferroni result provides a distributional reference.
p_bonf = np.minimum(1., p_unc * v)

# Descriptive, coordinate-defined vmPFC display region (MNI mm); it is not the
# hypothesis test or a substitute for the whole-brain-corrected inference.
ijk = np.indices(shape).reshape(3, -1).T
xyz = nib.affines.apply_affine(affine, ijk)
roi_full = ((xyz[:, 0] >= -12) & (xyz[:, 0] <= 12) &
            (xyz[:, 1] >= 30) & (xyz[:, 1] <= 55) &
            (xyz[:, 2] >= -15) & (xyz[:, 2] <= 10)).reshape(shape) & mask
roi_vals = stack[:, roi_full]
roi_subject_means = roi_vals.mean(axis=1)
roi_mean = float(roi_subject_means.mean())
roi_ci = stats.t.interval(.95, n - 1, loc=roi_mean,
                          scale=stats.sem(roi_subject_means))
roi_t, roi_p = stats.ttest_1samp(roi_subject_means, 0., alternative="greater")

# Independent implementation check at fixed voxels, including a max-stat p check.
candidate = np.argsort(p_unc)[:3]
checks = []
for j in candidate:
    ref_t, ref_p = stats.ttest_1samp(X[:, j], 0., alternative="greater")
    assert np.isclose(ref_t, t_obs[j], rtol=1e-10, atol=1e-10)
    assert np.isclose(ref_p, p_unc[j], rtol=1e-10, atol=1e-12)
    checks.append({"flat_index": int(np.flatnonzero(mask)[j]), "t_script": float(t_obs[j]),
                   "t_scipy": float(ref_t), "p_script": float(p_unc[j]), "p_scipy": float(ref_p)})

flat_indices = np.flatnonzero(mask)
order = np.argsort(p_fwe)
peak_j = int(order[0])
peak_ijk = np.unravel_index(int(flat_indices[peak_j]), shape)
peak_xyz = nib.affines.apply_affine(affine, np.array(peak_ijk))
sig = p_fwe <= .05
sig_count = int(sig.sum())

def write_map(name: str, values: np.ndarray, fill: float = 0.) -> None:
    arr = np.full(shape, fill, dtype=np.float32)
    arr[mask] = values.astype(np.float32)
    nib.save(nib.Nifti1Image(arr, affine, imgs[0].header), OUT / name)

write_map("group_mean.nii.gz", means)
write_map("group_t.nii.gz", t_obs)
write_map("group_p_fwe_max_t.nii.gz", p_fwe, 1.)

vm = p_fwe <= .05
clusters = []
if vm.any():
    vm_full = np.zeros(shape, dtype=bool)
    vm_full[mask] = vm
    from scipy.ndimage import label
    labels, nc = label(vm_full, structure=np.ones((3, 3, 3), dtype=int))
    t_full = np.zeros(shape, dtype=np.float64)
    t_full[mask] = t_obs
    for k in range(1, nc + 1):
        pts = np.argwhere(labels == k)
        c_xyz = nib.affines.apply_affine(affine, pts).mean(axis=0)
        peak = pts[np.argmax(t_full[tuple(pts.T)])]
        pxyz = nib.affines.apply_affine(affine, peak)
        clusters.append({"cluster": k, "voxels": len(pts), "centroid_x": c_xyz[0], "centroid_y": c_xyz[1], "centroid_z": c_xyz[2],
                         "peak_x": pxyz[0], "peak_y": pxyz[1], "peak_z": pxyz[2],
                         "peak_t": t_full[tuple(peak)]})
pd.DataFrame(clusters).to_csv(OUT / "fwe_clusters.csv", index=False)

qc = pd.DataFrame({"participant_id": ids,
                   "map_mean": stack.reshape(n, -1).mean(axis=1),
                   "map_sd": stack.reshape(n, -1).std(axis=1),
                   "fraction_nonzero": (stack.reshape(n, -1) != 0).mean(axis=1),
                   "vmPFC_box_mean": roi_subject_means})
qc.to_csv(OUT / "participant_qc.csv", index=False)

summary = {
    "n_participants": n, "n_excluded": 0, "map_shape": list(shape),
    "voxel_sizes_mm": [float(z) for z in imgs[0].header.get_zooms()[:3]],
    "n_common_support_voxels": int(v), "mask_definition": "nonzero support in all 54 maps",
    "degrees_freedom": df, "alternative": "mean > 0", "permutation_method": "participant sign-flip maximum t",
    "permutations": N_PERM, "seed": SEED, "minimum_fwe_p_resolution": 1/(N_PERM+1),
    "fwe_alpha": .05, "significant_voxels": sig_count,
    "peak_x_mni_mm": float(peak_xyz[0]), "peak_y_mni_mm": float(peak_xyz[1]),
    "peak_z_mni_mm": float(peak_xyz[2]), "peak_mean_contrast": float(means[peak_j]),
    "peak_t": float(t_obs[peak_j]), "peak_p_uncorrected": float(p_unc[peak_j]),
    "peak_p_fwe_max_t": float(p_fwe[peak_j]), "peak_p_fwe_bonferroni": float(p_bonf[peak_j]),
    "roi_definition_mni_box_mm": {"x": [-12, 12], "y": [30, 55], "z": [-15, 10]},
    "roi_n_voxels": int(roi_full.sum()), "roi_mean_contrast": roi_mean,
    "roi_mean_95ci": [float(roi_ci[0]), float(roi_ci[1])], "roi_t": float(roi_t),
    "roi_p_one_sided_descriptive": float(roi_p), "scipy_reference_checks": checks,
    "environment": {"python": sys.version.split()[0], "platform": platform.platform(),
                     "numpy": np.__version__, "scipy": scipy.__version__,
                     "nibabel": nib.__version__, "pandas": pd.__version__, "matplotlib": matplotlib.__version__}}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

# Figure: participant-level vmPFC box contrast estimates and corrected spatial map.
fig = plt.figure(figsize=(10, 4.5), layout="constrained")
gs = fig.add_gridspec(1, 2, width_ratios=[.8, 1.4])
ax = fig.add_subplot(gs[0, 0])
ax.scatter(np.ones(n) + rng.normal(0, .045, n), roi_subject_means, s=18, alpha=.6,
           color="#345995", edgecolors="none")
ax.errorbar([1], [roi_mean], yerr=[[roi_mean-roi_ci[0]], [roi_ci[1]-roi_mean]],
            fmt="o", color="#c0392b", capsize=4, markersize=6, label="mean and 95% CI")
ax.axhline(0, color="0.35", lw=.8, ls="--")
ax.set(xlim=(.75, 1.25), xticks=[1], xticklabels=["vmPFC display box"],
       ylabel="Gain effect estimate (arbitrary upstream units)",
       title="Participant summaries (n=54)")
ax.legend(frameon=False, loc="best", fontsize=8)

from nilearn import plotting
# Recreate whole-brain t map directly from the support mask.
tdata = np.zeros(shape, dtype=np.float32); tdata[mask] = t_obs
plotting.plot_stat_map(nib.Nifti1Image(tdata, affine), bg_img=None,
                       threshold=stats.t.isf(.001, df), display_mode="z",
                       cut_coords=[-10, 0, 10, 20, 30], cmap="cold_hot", colorbar=True,
                       title="Observed t map; display threshold p<.001 uncorrected",
                       axes=fig.add_subplot(gs[0, 1]))
fig.suptitle("Gain-modulator participant effects: descriptive vmPFC and whole-brain t map", fontsize=11)
fig.savefig(FIG / "group_results.png", dpi=180)
fig.savefig(FIG / "group_results.svg")
plt.close(fig)

print(json.dumps(summary, indent=2))
