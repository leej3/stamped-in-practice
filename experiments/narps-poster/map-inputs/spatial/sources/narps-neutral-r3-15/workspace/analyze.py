#!/usr/bin/env python3
"""Group inference for NARPS AO86 equal-indifference gain effect maps.

One-sample positive-direction t field with sign-flip max-T family-wise
correction. Inputs and all transformations are recorded in results/.
"""
from pathlib import Path
import hashlib, json, time

import nibabel as nib
import numpy as np
import pandas as pd
from scipy.stats import t as t_dist
import matplotlib.pyplot as plt
from nilearn import plotting
from nilearn.datasets import load_mni152_template

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "input" / "data"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
N_PERM = 9999
SEED = 861734

participants = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
src = json.loads((ROOT / "input" / "sources.json").read_text())
files = src["files"]
ids = participants.participant_id.tolist()
assert len(ids) == 54 and len(set(ids)) == 54
assert set(ids) == {v["participant_id"] for k, v in files.items() if k.endswith(".nii.gz")}

imgs, rows = [], []
ref = None
for pid in ids:
    path = DATA / f"{pid}_hypo1_cope.nii.gz"
    img = nib.load(path)
    arr = np.asarray(img.dataobj, dtype=np.float32)
    if ref is None:
        ref = img
    if arr.shape != ref.shape or not np.allclose(img.affine, ref.affine):
        raise ValueError(f"Grid mismatch: {pid}")
    if not np.isfinite(arr).all():
        raise ValueError(f"Non-finite values: {pid}")
    rows.append({"participant_id": pid, "age": int(participants.set_index("participant_id").loc[pid,"age"]),
                 "gender": participants.set_index("participant_id").loc[pid,"gender"],
                 "nonzero_voxels": int(np.count_nonzero(arr)), "min": float(arr.min()), "max": float(arr.max()),
                 "mean_nonzero": float(arr[arr != 0].mean()) if np.any(arr != 0) else np.nan})
    imgs.append(arr)
X = np.stack(imgs, axis=0)
pd.DataFrame(rows).to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)

# Analysis mask: voxels represented by at least 90% of participants. Zero is
# treated as outside-map support; this retains edges without relying on signal.
coverage = np.count_nonzero(X, axis=0) / X.shape[0]
mask = coverage >= 0.90
if not mask.any():
    raise ValueError("Empty analysis mask")
Y = X[:, mask].astype(np.float64)
n, m = Y.shape
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
se = sd / np.sqrt(n)
t_obs = np.divide(mean, se, out=np.zeros_like(mean), where=se > 0)
df = n - 1
p_unc = t_dist.sf(t_obs, df)

# One-sided sign-flip max-T: the prespecified hypothesis is positive. Generate
# random sign patterns and retain each permutation's maximum t across every
# voxel in the whole analysis mask. This controls voxelwise FWE at alpha=.05.
rng = np.random.default_rng(SEED)
max_t = np.empty(N_PERM, dtype=np.float64)
batch = 100
for start in range(0, N_PERM, batch):
    b = min(batch, N_PERM-start)
    signs = rng.choice(np.array([-1., 1.]), size=(b, n))
    # For each permutation, recompute the one-sample t field under sign flips.
    perm = signs @ Y
    perm_mean = perm / n
    # sum of squares after centering = sum(y^2) - sum(y)^2/n for each voxel.
    # Each subject's squared observation is invariant under sign flips.
    ss = np.sum(Y * Y, axis=0)[None, :] - (perm * perm) / n
    perm_sd = np.sqrt(np.maximum(ss, 0) / (n - 1))
    pt = np.divide(perm_mean, perm_sd / np.sqrt(n), out=np.zeros_like(perm_mean), where=perm_sd > 0)
    max_t[start:start+b] = pt.max(axis=1)

p_fwe = (1 + (max_t[:, None] >= t_obs[None, :]).sum(axis=0)) / (N_PERM + 1)
crit = float(np.quantile(max_t, .95, method="higher"))
sig = p_fwe <= .05

def masked_img(values, dtype=np.float32):
    full = np.zeros(mask.shape, dtype=dtype)
    full[mask] = values
    return nib.Nifti1Image(full, ref.affine, ref.header)

for name, vals in [("mean_effect.nii.gz", mean), ("t_statistic.nii.gz", t_obs),
                   ("p_fwe.nii.gz", p_fwe), ("coverage.nii.gz", coverage[mask])]:
    nib.save(masked_img(vals), OUT / name)

# Operational vmPFC ROI: bilateral medial, anterior, ventral prefrontal volume
# (|x|<=10, y>=0, z<=10 mm in MNI152NLin2009cAsym). This is fixed in advance
# from anatomical coordinates, independent of observed effect values.
ijk = np.array(np.where(mask)).T
xyz = nib.affines.apply_affine(ref.affine, ijk)
roi_local = (np.abs(xyz[:,0]) <= 10) & (xyz[:,1] >= 0) & (xyz[:,1] <= 50) & (xyz[:,2] >= -20) & (xyz[:,2] <= 10)
roi_idx = np.flatnonzero(roi_local)
if not len(roi_idx): raise ValueError("Empty vmPFC ROI")
roi_data = Y[:, roi_idx]
roi_subj = roi_data.mean(axis=1)
roi_mean = float(roi_subj.mean()); roi_sd = float(roi_subj.std(ddof=1))
roi_se = roi_sd / np.sqrt(n)
roi_t = roi_mean / roi_se
roi_p = float(t_dist.sf(roi_t, n-1))
roi_ci = [float(roi_mean - t_dist.ppf(.975, n-1)*roi_se), float(roi_mean + t_dist.ppf(.975, n-1)*roi_se)]
roi_voxel_sig = int(sig[roi_idx].sum())
roi_voxel_count = len(roi_idx)

coords = ijk[sig]
sig_xyz = nib.affines.apply_affine(ref.affine, coords) if len(coords) else np.empty((0,3))
sig_vals = t_obs[sig]
order = np.argsort(-sig_vals)
peaks = [{"x": float(sig_xyz[i,0]), "y": float(sig_xyz[i,1]), "z": float(sig_xyz[i,2]),
          "t": float(sig_vals[i]), "p_fwe": float(p_fwe[sig][i])} for i in order[:20]]
out = {
    "n": n, "excluded": [], "analysis_mask_voxels": int(m), "mask_rule": "nonzero map support in >=90% of participants",
    "grid_shape": list(ref.shape), "voxel_size_mm": [float(x) for x in ref.header.get_zooms()[:3]],
    "permutations": N_PERM, "seed": SEED, "test": "one-sided one-sample t, positive direction; sign-flip max-T FWE across whole analysis mask",
    "maxT_95_critical": crit, "fwe_significant_voxels": int(sig.sum()),
    "max_observed_t": float(t_obs.max()), "max_positive_t_uncorrected_p": float(t_dist.sf(t_obs.max(), df)),
    "vmPFC_roi_definition_mni_mm": "|x|<=10, 0<=y<=50, -20<=z<=10; bilateral medial anterior ventral PFC coordinate ROI",
    "vmPFC_roi_voxels": roi_voxel_count, "vmPFC_roi_subject_mean_effect": roi_mean,
    "vmPFC_roi_subject_mean_effect_95ci": roi_ci, "vmPFC_roi_t": float(roi_t), "vmPFC_roi_one_sided_uncorrected_p": roi_p,
    "vmPFC_roi_fwe_significant_voxels": roi_voxel_sig, "whole_brain_fwe_positive_overlap_with_vmPFC": bool(roi_voxel_sig > 0),
    "positive_fwe_peaks": peaks,
}
(OUT / "summary.json").write_text(json.dumps(out, indent=2))

# Figures: corrected whole-brain result and transparent ROI effect distribution.
bg = load_mni152_template(resolution=2)
disp = plotting.plot_stat_map(masked_img(t_obs), bg_img=bg, threshold=crit,
    display_mode="ortho", cut_coords=(0, 30, -8), cmap="hot", colorbar=True,
    title="Gain effect: positive one-sample t; whole-brain max-T FWE p < .05")
disp.savefig(OUT / "whole_brain_fwe.png", dpi=180)
disp.close()
fig, ax = plt.subplots(figsize=(7,4.5))
ax.hist(roi_subj, bins=12, color="#567d9a", edgecolor="white")
ax.axvline(roi_mean, color="#a23b32", linewidth=2, label=f"mean = {roi_mean:.3g}")
ax.axvline(0, color="black", linewidth=1, linestyle="--")
ax.set(xlabel="Participant mean gain-effect estimate in vmPFC ROI (arbitrary model units)", ylabel="Participants",
       title="vmPFC ROI participant estimates")
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(OUT / "vmPFC_roi_distribution.png", dpi=180); plt.close(fig)

print(json.dumps(out, indent=2))
