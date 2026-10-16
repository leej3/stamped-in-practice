#!/usr/bin/env python3
"""Group inference for NARPS AO86 equal-indifference gain cope maps.

Primary inference: one-sample positive t test with one-sided sign-flip
maximum-t familywise correction over a map-coverage mask. A parametric
one-sample t / Bonferroni result is saved as a sensitivity analysis.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy.ndimage import label
import matplotlib.pyplot as plt
from nilearn import plotting, datasets

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
N_PERM = 5000
SEED = 20261016

participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
files = sorted((INPUT / "data").glob("sub-*_hypo1_cope.nii.gz"))
expected = set(participants.participant_id)
found = {f.name.split("_")[0] for f in files}
if found != expected or len(files) != 54:
    raise RuntimeError(f"Map/cohort mismatch: {len(files)} maps, missing={expected-found}, extra={found-expected}")

imgs = [nib.load(str(f)) for f in files]
ref = imgs[0]
for f, im in zip(files, imgs):
    if im.shape != ref.shape or not np.allclose(im.affine, ref.affine, atol=1e-5):
        raise RuntimeError(f"Spatial grid mismatch: {f.name}")
data = np.stack([im.get_fdata(dtype=np.float32) for im in imgs])
if not np.isfinite(data).all():
    raise RuntimeError("Non-finite values found in supplied maps")

# Map coverage is inferred from nonzero estimates. Retain voxels nonzero in
# at least 90% of maps, reducing boundary/coverage artifacts without
# requiring an unprovided analysis mask.
coverage = np.count_nonzero(data, axis=0)
mask = coverage >= int(np.ceil(0.90 * len(files)))
X = data[:, mask].astype(np.float64, copy=False)
n, nvox = X.shape
mean = X.mean(axis=0)
sd = X.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(n))
p_unc = stats.t.sf(t_obs, df=n - 1)

# One-sided sign-flip maximum-t inference. Under the one-sample null, signs
# are exchangeable when participant effects are symmetric about zero.
rng = np.random.default_rng(SEED)
sum_sq = np.einsum("ij,ij->j", X, X)
max_null = np.empty(N_PERM, dtype=np.float64)
batch = 50
for start in range(0, N_PERM, batch):
    b = min(batch, N_PERM - start)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
    sums = signs @ X
    denom = np.sqrt(np.maximum(n * sum_sq[None, :] - sums * sums, 1e-30))
    t_perm = sums * np.sqrt(n - 1) / denom
    max_null[start:start+b] = np.max(t_perm, axis=1)

perm_cut = float(np.quantile(max_null, 0.95, method="higher"))
p_fwe = (1 + N_PERM - np.searchsorted(np.sort(max_null), t_obs, side="left")) / (N_PERM + 1)
sig = p_fwe <= 0.05

# Anatomical vmPFC approximation in MNI coordinates (bilateral medial,
# anterior and ventral frontal cortex). It is used to localize/describe the
# hypothesis region only; whole-brain corrected inference remains primary.
ijk = np.argwhere(mask)
xyz = nib.affines.apply_affine(ref.affine, ijk)
vm_roi = ((np.abs(xyz[:, 0]) <= 15) & (xyz[:, 1] >= 25) &
          (xyz[:, 1] <= 60) & (xyz[:, 2] >= -20) & (xyz[:, 2] <= 10))
roi_values = X[:, vm_roi]
roi_subject_mean = roi_values.mean(axis=1)
roi_mean = float(roi_subject_mean.mean())
roi_se = float(stats.sem(roi_subject_mean))
roi_ci = stats.t.interval(0.95, df=n-1, loc=roi_mean, scale=roi_se)
roi_t = float(roi_mean / roi_se)
roi_p = float(stats.t.sf(roi_t, df=n-1))
roi_vox = int(vm_roi.sum())

# Write whole-brain images in the supplied spatial grid.
def full_img(values, fill=np.nan):
    arr = np.full(mask.shape, fill, dtype=np.float32)
    arr[mask] = values.astype(np.float32)
    return nib.Nifti1Image(arr, ref.affine, ref.header)

nib.save(full_img(t_obs), OUT / "group_t_unthresholded.nii.gz")
nib.save(full_img(p_fwe), OUT / "p_fwe_signflip_maxT.nii.gz")
nib.save(full_img(np.where(sig, t_obs, 0.0), fill=0), OUT / "group_t_fwe05_positive.nii.gz")

# Parametric sensitivity: one-sided t probabilities with voxelwise Bonferroni.
p_bonf = np.minimum(1, p_unc * nvox)
bonf_sig = p_bonf <= 0.05

# Cluster summary of positive max-T significant voxels (26-neighbor).
sig_img = np.zeros(mask.shape, dtype=np.uint8)
sig_img[mask] = sig
clusters, nclusters = label(sig_img, structure=np.ones((3, 3, 3), dtype=int))
cluster_rows = []
for cid in range(1, nclusters + 1):
    vox = np.argwhere(clusters == cid)
    if len(vox) == 0:
        continue
    coord = nib.affines.apply_affine(ref.affine, vox)
    vals = np.array([t_obs[np.flatnonzero(np.all(ijk == v, axis=1))[0]] for v in vox])
    cluster_rows.append({"cluster": cid, "voxels": len(vox), "peak_t": float(vals.max()),
                         "peak_x": float(coord[np.argmax(vals), 0]),
                         "peak_y": float(coord[np.argmax(vals), 1]),
                         "peak_z": float(coord[np.argmax(vals), 2]),
                         "centroid_x": float(coord[:, 0].mean()),
                         "centroid_y": float(coord[:, 1].mean()),
                         "centroid_z": float(coord[:, 2].mean())})
pd.DataFrame(cluster_rows).to_csv(OUT / "fwe_clusters.csv", index=False)

summary = {
    "n_participants": n, "n_excluded": 0, "n_tested_voxels": int(nvox),
    "mask_coverage_rule": "nonzero in >=90% of 54 maps", "n_permutations": N_PERM,
    "random_seed": SEED, "permutation_maxT_95pct": perm_cut,
    "n_voxels_fwe05_signflip": int(sig.sum()),
    "n_voxels_bonferroni05_parametric": int(bonf_sig.sum()),
    "peak_t": float(t_obs.max()), "peak_p_fwe_signflip": float(p_fwe.min()),
    "vmPFC_roi_definition_mni": {"abs_x_max": 15, "y_min": 25, "y_max": 60, "z_min": -20, "z_max": 10},
    "vmPFC_roi_voxels": roi_vox, "vmPFC_mean_effect": roi_mean,
    "vmPFC_mean_effect_95ci": [float(roi_ci[0]), float(roi_ci[1])],
    "vmPFC_t": roi_t, "vmPFC_one_sided_p_uncorrected_descriptive": roi_p,
    "vmPFC_max_t": float(t_obs[vm_roi].max()),
    "vmPFC_min_p_fwe_signflip": float(p_fwe[vm_roi].min()),
    "vmPFC_min_p_bonferroni": float(p_bonf[vm_roi].min()),
    "maps_shape": list(ref.shape), "voxel_size_mm": [float(v) for v in ref.header.get_zooms()[:3]],
    "coordinate_system": "MNI152NLin2009cAsym (as supplied)",
    "data_sha256": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
pd.DataFrame({"participant_id": [f.name.split("_")[0] for f in files],
              "mean_vmPFC_effect": roi_subject_mean}).to_csv(OUT / "vmPFC_subject_means.csv", index=False)

# Compact scientific figures.
template = datasets.load_mni152_template(resolution=2)
threshold = perm_cut
disp = plotting.plot_stat_map(full_img(t_obs, fill=0), bg_img=template,
    threshold=threshold, display_mode="ortho", cut_coords=(0, 40, -5),
    cmap="magma", colorbar=True, black_bg=False,
    title="Positive gain effect: sign-flip max-T FWE, p ≤ .05")
disp.add_markers([(0, 40, -5)], marker_color="cyan", marker_size=55)
disp.savefig(FIG / "whole_brain_fwe_and_vmpfc.png", dpi=180)
disp.close()

disp = plotting.plot_stat_map(full_img(t_obs, fill=0), bg_img=template,
    threshold=threshold, display_mode="ortho", cut_coords=(-26, -100, -4),
    cmap="magma", colorbar=True, black_bg=False,
    title="Corrected posterior cluster at its peak (MNI −26, −102, −4)")
disp.savefig(FIG / "posterior_fwe_cluster.png", dpi=180)
disp.close()

disp = plotting.plot_glass_brain(full_img(t_obs, fill=0), threshold=threshold,
    display_mode="lyrz", colorbar=True, cmap="magma", black_bg=False,
    title="All positive voxels surviving whole-brain FWE correction")
disp.savefig(FIG / "whole_brain_fwe_glassbrain.png", dpi=180)
disp.close()

fig, ax = plt.subplots(figsize=(7, 4.2))
ax.scatter(np.arange(1, n+1), roi_subject_mean, color="#235789", alpha=.8, s=28)
ax.axhline(0, color="black", linewidth=1)
ax.axhline(roi_mean, color="#d1495b", linewidth=2, label=f"Mean = {roi_mean:.3f}")
ax.fill_between([0, n+1], roi_ci[0], roi_ci[1], color="#d1495b", alpha=.15,
                label="95% t interval across participants")
ax.set(xlim=(0, n+1), xlabel="Participant (ordered by ID)",
       ylabel="Mean gain-effect estimate in vmPFC box",
       title="Descriptive vmPFC summary (not whole-brain inference)")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIG / "vmpfc_participant_effects.png", dpi=180)
plt.close(fig)

print(json.dumps({k: v for k, v in summary.items() if k != "data_sha256"}, indent=2))
