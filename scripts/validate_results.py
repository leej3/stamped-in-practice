#!/usr/bin/env python3
"""Independent numerical checks of generated NARPS H1 maps and tables."""
from __future__ import annotations
import json
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from nilearn import datasets
from nilearn.image import resample_to_img

ROOT = Path(__file__).resolve().parents[1]
R, I = ROOT / "results", ROOT / "input"
summary = json.loads((R / "summary.json").read_text())
qc = pd.read_csv(R / "map_qc.tsv", sep="\t")
excluded = pd.read_csv(R / "exclusions.tsv", sep="\t")
assert len(qc) == summary["n_expected"] == 54
assert qc.checksum_ok.all() and qc.finite.all() and qc.qc_flags.fillna("").eq("").all()
assert len(excluded) == summary["n_excluded"] == 0
participants = pd.read_csv(I / "participants.tsv", sep="\t")
imgs = [nib.load(str(I / "data" / f"{pid}_hypo1_cope.nii.gz")) for pid in participants.participant_id]
aff = imgs[0].affine
mask_img = resample_to_img(datasets.load_mni152_brain_mask(resolution=2), imgs[0], interpolation="nearest", force_resample=True, copy_header=True)
brain_mask = np.asarray(mask_img.dataobj) > 0
brain = nib.load(str(R / "t_unthresholded.nii.gz"))
pmap_img = nib.load(str(R / "p_fwe.nii.gz"))
assert all(im.shape == imgs[0].shape and np.allclose(im.affine, aff, atol=1e-4) for im in imgs)
assert np.allclose(brain.affine, aff, atol=1e-4)
arr = np.stack([np.asarray(im.dataobj, dtype=np.float64) for im in imgs])
x = arr[:, brain_mask]
T = np.asarray(brain.dataobj, dtype=np.float64)
# Independently recompute the one-sample statistic at 20 spatially sampled voxels.
rng_spatial = np.random.default_rng(71)
coords = np.argwhere(brain_mask)
for xyz in coords[rng_spatial.choice(len(coords), size=20, replace=False)]:
    ijk = tuple(xyz)
    ref = stats.ttest_1samp(arr[(slice(None),) + ijk], 0, alternative="greater")
    assert np.isclose(T[ijk], ref.statistic, rtol=2e-5, atol=2e-5), (ijk, T[ijk], ref.statistic)

# Recreate the first 20 fixed-seed sign flips with direct participant-wise
# multiplication, variance and max-t calculation, independent of the fast
# sum-of-squares identity used by the group-analysis script.
rng_perm = np.random.default_rng(summary["seed"])
raw_null = pd.read_csv(R / "permutation_max_t.tsv", sep="\t").max_t_null.to_numpy()
assert len(raw_null) == summary["permutations"]
for k in range(20):
    signs = rng_perm.choice(np.array([-1.0, 1.0]), size=len(imgs))
    permuted = x * signs[:, None]
    perm_mean = permuted.mean(axis=0)
    perm_denom = permuted.std(axis=0, ddof=1) / np.sqrt(len(imgs))
    perm_t = np.divide(perm_mean, perm_denom, out=np.zeros_like(perm_mean), where=perm_denom > 0)
    assert np.isclose(raw_null[k], np.max(perm_t), rtol=2e-5, atol=2e-5), (k, raw_null[k], np.max(perm_t))

# Reconstruct every voxel's corrected p-value from the stored max-t null and
# verify that the thresholded map is exactly the declared alpha decision.
null_sorted = np.sort(raw_null)
first_ge = np.searchsorted(null_sorted, T[brain_mask], side="left")
p_fwe_expected = (len(raw_null) - first_ge + 1) / (len(raw_null) + 1)
P = np.asarray(pmap_img.dataobj, dtype=np.float64)
assert np.max(np.abs(P[brain_mask] - p_fwe_expected)) <= 1 / (len(raw_null) + 1) + 1e-7
assert np.all(P[~brain_mask] == 1)
assert np.all((P >= 0) & (P <= 1))
fwe_expected = np.zeros_like(T)
fwe_expected[brain_mask] = np.where(p_fwe_expected <= summary["alpha_one_sided"], T[brain_mask], 0)
fwe_observed = np.asarray(nib.load(str(R / "t_fwe05.nii.gz")).dataobj)
assert np.allclose(fwe_observed, fwe_expected, rtol=2e-5, atol=2e-5)

# Verify the planned voxelwise Bonferroni sensitivity output.
p_unc = stats.t.sf(T[brain_mask], len(imgs) - 1)
bonf_expected = np.zeros_like(T)
bonf_expected[brain_mask] = np.where(p_unc <= .05 / summary["n_voxels_tested"], T[brain_mask], 0)
bonf_observed = np.asarray(nib.load(str(R / "t_bonferroni05.nii.gz")).dataobj)
assert np.allclose(bonf_observed, bonf_expected, rtol=2e-5, atol=2e-5)
assert int(np.sum(bonf_observed > 0)) == summary["n_bonferroni_positive_voxels"]

# Reconstruct vmPFC box summaries and selected-voxel descriptive interval.
coords_grid = np.indices(imgs[0].shape, dtype=float)
world = nib.affines.apply_affine(aff, np.stack(coords_grid, axis=-1).reshape(-1, 3)).reshape(*imgs[0].shape, 3)
box = brain_mask & (np.abs(world[..., 0]) <= 10) & (world[..., 1] >= 20) & (world[..., 1] <= 60) & (world[..., 2] >= -20) & (world[..., 2] <= 20)
subject_roi = arr[:, box].mean(axis=1)
assert np.isclose(subject_roi.mean(), summary["vmPFC_box_mean_effect"], rtol=2e-5, atol=5e-8)
mean_img = np.asarray(nib.load(str(R / "mean_effect.nii.gz")).dataobj)
assert np.allclose(mean_img[box].mean(), summary["vmPFC_box_mean_effect"], rtol=2e-5, atol=2e-6)
roi_t = T[box]
roi_coords = world[box]
peak_idx = int(np.argmax(roi_t))
roi_subjects = arr[:, box][:, peak_idx]
roi_peak = json.loads((R / "selected_vmPFC_voxel.json").read_text())
assert np.allclose([roi_peak["x_mm"], roi_peak["y_mm"], roi_peak["z_mm"]], roi_coords[peak_idx], atol=1e-4)
assert np.isclose(roi_peak["mean_effect"], roi_subjects.mean(), rtol=2e-5, atol=5e-8)
assert np.isclose(roi_peak["between_subject_sd"], roi_subjects.std(ddof=1), rtol=2e-5, atol=5e-8)

# Recompute descriptive participant averages over the whole tested mask.
global_values = arr[:, brain_mask].mean(axis=1)
global_table = pd.read_csv(R / "participant_global_brain_summary.tsv", sep="\t")
assert np.allclose(global_table.mean_effect_across_brain_mask, global_values, atol=5e-8)
assert np.isclose(global_values.mean(), summary["whole_brain_subject_average_mean"], atol=5e-8)
assert summary["n_fwe_positive_voxels_in_vmPFC_box"] == 0
world_masked = world[brain_mask]
box_masked = ((np.abs(world_masked[:, 0]) <= 10) & (world_masked[:, 1] >= 20) &
              (world_masked[:, 1] <= 60) & (world_masked[:, 2] >= -20) &
              (world_masked[:, 2] <= 20))
assert summary["n_bonferroni_positive_voxels_in_vmPFC_box"] == int(
    np.sum((p_unc <= .05 / summary["n_voxels_tested"]) & box_masked))

print(json.dumps({"validated": True, "n_maps": len(imgs), "voxel_t_checks": 20,
                  "direct_sign_flip_checks": 20, "voxelwise_fwe_values_checked": int(brain_mask.sum()),
                  "permutation_null_n": len(raw_null), "fwe_significant_voxels": summary["n_fwe_positive_voxels"],
                  "bonferroni_significant_voxels": summary["n_bonferroni_positive_voxels"],
                  "vmPFC_fwe_voxels": summary["n_fwe_positive_voxels_in_vmPFC_box"]}, indent=2))
