#!/usr/bin/env python3
"""Group analysis of the supplied NARPS AO86 participant gain cope maps."""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy.ndimage import label
import matplotlib.pyplot as plt
from nilearn import plotting, image

ROOT = Path(__file__).parent
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
SEED = 20261016
N_PERM = 4999

sources = json.loads((ROOT / "input/sources.json").read_text())
participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
paths = [ROOT / "input" / name for name in sources["files"] if name.endswith("_cope.nii.gz")]
paths.sort(key=lambda p: p.name)
assert len(paths) == len(participants) == 54
assert [p.stem.split("_")[0] for p in paths] == sorted(participants.participant_id)

imgs, data = [], []
qc = []
for p in paths:
    img = nib.load(p)
    x = img.get_fdata(dtype=np.float32)
    assert x.shape == (97, 115, 81) and np.isfinite(x).all()
    imgs.append(img)
    data.append(x)
    qc.append({"participant_id": p.name.split("_")[0], "nonzero_voxels": int(np.count_nonzero(x)),
               "mean_nonzero": float(np.mean(x[x != 0])), "sd_nonzero": float(np.std(x[x != 0])),
               "min": float(x.min()), "max": float(x.max()),
               "sha256_matches_manifest": hashlib.sha256(p.read_bytes()).hexdigest() == sources["files"][str(p.relative_to(ROOT / "input"))]["sha256"]})
assert all(q["sha256_matches_manifest"] for q in qc)
assert all(np.allclose(img.affine, imgs[0].affine) for img in imgs)

# Supplied cope maps are zero outside each participant's acquired analysis support.
# Use the intersection, preventing coverage differences from changing n voxelwise.
Y = np.stack(data).astype(np.float64)
mask = np.all(Y != 0, axis=0)
n, shape = Y.shape[0], Y.shape[1:]
vox = Y[:, mask]
mean = vox.mean(axis=0)
sd = vox.std(axis=0, ddof=1)
tobs = mean / (sd / np.sqrt(n))
p_unc = stats.t.sf(tobs, df=n-1)

# One-sided sign-flip max-T permutation: under the group null participant effects
# are exchangeable under sign reversal. Max positive t controls FWE over all mask voxels.
rng = np.random.default_rng(SEED)
ss = np.square(vox).sum(axis=0)
max_t = np.empty(N_PERM, dtype=np.float64)
chunk = 32
for start in range(0, N_PERM, chunk):
    k = min(chunk, N_PERM-start)
    signs = rng.choice(np.array([-1., 1.]), size=(k, n))
    sums = signs @ vox
    var_num = np.maximum(ss[None, :] - (sums*sums)/n, 1e-16)
    ts = (sums / n) / np.sqrt(var_num / (n-1) / n)
    max_t[start:start+k] = np.max(ts, axis=1)
p_fwe = (1 + (max_t[:, None] >= tobs[None, :]).sum(axis=0)) / (N_PERM + 1)
crit = float(np.quantile(max_t, .95, method="higher"))

def make_img(arr, fill=0):
    out = np.full(shape, fill, dtype=np.float32)
    out[mask] = arr.astype(np.float32)
    return nib.Nifti1Image(out, imgs[0].affine)

mean_img = make_img(mean)
t_img = make_img(tobs)
pfwe_img = make_img(p_fwe)
sig_img = make_img(np.where(p_fwe <= .05, tobs, 0))
nib.save(mean_img, OUT/"group_mean_cope.nii.gz")
nib.save(t_img, OUT/"group_t_positive.nii.gz")
nib.save(pfwe_img, OUT/"group_p_fwe_maxT.nii.gz")
nib.save(sig_img, OUT/"group_t_fwe05.nii.gz")

# Summarize contiguous 26-neighbor regions in the corrected map.
sig_data = sig_img.get_fdata()
lab, nlab = label(sig_data > 0, structure=np.ones((3, 3, 3)))
clusters = []
for ci in range(1, nlab + 1):
    ijk_sig = np.argwhere(lab == ci)
    vals = sig_data[lab == ci]
    xyz = nib.affines.apply_affine(imgs[0].affine, ijk_sig[np.argmax(vals)])
    peak_idx = np.argmax(vals)
    peak_ijk = ijk_sig[peak_idx]
    xyz = nib.affines.apply_affine(imgs[0].affine, peak_ijk)
    clusters.append({"cluster": ci, "voxels": len(ijk_sig), "peak_t": float(vals[peak_idx]),
                     "peak_p_fwe": float(pfwe_img.get_fdata()[tuple(peak_ijk)]),
                     "peak_x": float(xyz[0]), "peak_y": float(xyz[1]), "peak_z": float(xyz[2])})
pd.DataFrame(clusters).to_csv(OUT/"fwe_significant_clusters.csv", index=False)

# A broad, anatomically specified descriptive vmPFC region: 12-mm sphere around
# a conventional medial orbitofrontal/vmPFC reference coordinate. This is not
# used to select or correct the primary whole-brain result.
ijk = np.indices(shape).reshape(3, -1).T
xyz = nib.affines.apply_affine(imgs[0].affine, ijk)
roi = np.linalg.norm(xyz - np.array([0, 42, -8]), axis=1) <= 12
roi = roi.reshape(shape) & mask
roi_data = Y[:, roi].mean(axis=1)
roi_m, roi_sd = float(roi_data.mean()), float(roi_data.std(ddof=1))
roi_se = roi_sd / np.sqrt(n)
roi_ci = stats.t.interval(.95, n-1, loc=roi_m, scale=roi_se)
roi_t = roi_m / roi_se
roi_p = float(stats.t.sf(roi_t, n-1))

# Subject-level ROI values and QC, plus voxelwise summary with adjusted values.
pd.DataFrame(qc).to_csv(OUT/"participant_qc.csv", index=False)
pd.DataFrame({"participant_id": participants.participant_id, "vmPFC_mean_cope": roi_data}).to_csv(OUT/"vmPFC_participant_values.csv", index=False)
pd.DataFrame({"n": [n], "mask_voxels": [int(mask.sum())], "permutations": [N_PERM], "seed": [SEED],
              "maxT_critical_95": [crit], "maxT_FWE_significant_voxels": [int((p_fwe <= .05).sum())],
              "maxT_FWE_min_p": [float(p_fwe.min())], "peak_t": [float(tobs.max())],
              "peak_p_uncorrected": [float(p_unc.min())], "peak_p_FWE": [float(p_fwe.min())],
              "vmPFC_roi_voxels": [int(roi.sum())], "vmPFC_mean_cope": [roi_m], "vmPFC_sd": [roi_sd],
              "vmPFC_ci95_low": [float(roi_ci[0])], "vmPFC_ci95_high": [float(roi_ci[1])],
              "vmPFC_t": [float(roi_t)], "vmPFC_p_one_sided_descriptive": [roi_p]}).to_csv(OUT/"group_summary.csv", index=False)

summary = {
    "cohort_n": n, "excluded": [], "map_shape": list(shape), "affine": imgs[0].affine.tolist(),
    "mask_definition": "intersection of nonzero support across all 54 cope maps",
    "mask_voxels": int(mask.sum()), "map_sha256_all_match_manifest": True,
    "model": "one-sample group t statistic of participant cope estimates; positive one-sided alternative",
    "correction": "one-sided sign-flip permutation max-T over whole common-support mask; FWE alpha .05",
    "permutations": N_PERM, "seed": SEED, "maxT_critical_95": crit,
    "significant_voxels_fwe05": int((p_fwe <= .05).sum()), "minimum_maxT_fwe_p": float(p_fwe.min()),
    "peak": {"t": float(tobs.max()), "p_uncorrected": float(p_unc.min()), "p_fwe": float(p_fwe.min()),
             "mni_xyz": nib.affines.apply_affine(imgs[0].affine, np.array(np.unravel_index(np.argmax(make_img(tobs).get_fdata()), shape))).tolist()},
    "vmPFC_descriptive_roi": {"definition": "12-mm radius sphere centered MNI (0,42,-8), clipped to analysis mask",
        "voxels": int(roi.sum()), "mean_cope": roi_m, "sd_between_participants": roi_sd,
        "mean_cope_ci95_t_based": [float(roi_ci[0]), float(roi_ci[1])], "t": float(roi_t),
        "p_one_sided_uncorrected_descriptive_only": roi_p,
        "n_voxels_fwe05": int(np.sum((p_fwe <= .05) & roi[mask]))},
    "limitations": ["cope coefficients are per normalized gain modulator, not per currency unit",
        "participant variance maps are unavailable; group inference uses equal-weight participant effects",
        "sign-flip inference assumes participant effects are sign-exchangeable under the null",
        "whole-brain correction is limited to common nonzero map support"]
}
(OUT/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")

# Figure 1: group mean cope and the whole-brain corrected positive statistic.
fig = plt.figure(figsize=(11, 4.8))
ax1 = fig.add_subplot(1, 2, 1)
plotting.plot_stat_map(mean_img, display_mode="ortho", cut_coords=(0, 42, -8), threshold=None,
                       colorbar=True, cmap="cold_hot", axes=ax1, black_bg=False)
ax2 = fig.add_subplot(1, 2, 2)
plotting.plot_stat_map(sig_img, display_mode="ortho", cut_coords=(-26, -98, -4), threshold=None,
                       colorbar=True, cmap="cold_hot", axes=ax2, black_bg=False)
fig.text(.25, .98, "Mean gain cope (arbitrary units)", ha="center", va="top", fontsize=13)
fig.text(.75, .98, "Positive t, max-T FWE p ≤ .05", ha="center", va="top", fontsize=13)
fig.savefig(OUT/"figure1_group_maps.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Figure 2: participant-level ROI estimates, showing heterogeneity and the mean CI.
fig, ax = plt.subplots(figsize=(7.4, 4.4))
ax.scatter(np.arange(1,n+1), roi_data, s=24, color="#345995", alpha=.8, edgecolor="white", linewidth=.4)
ax.axhline(0, color="black", lw=1)
ax.axhline(roi_m, color="#d1495b", lw=2, label=f"mean = {roi_m:.3g}")
ax.axhspan(*roi_ci, color="#d1495b", alpha=.14, label="95% t interval")
ax.set(xlabel="Participant (sorted by ID)", ylabel="Mean vmPFC gain cope", title="Descriptive vmPFC ROI participant estimates")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT/"figure2_vmPFC_roi.png", dpi=180)
plt.close(fig)
print(json.dumps(summary, indent=2))
