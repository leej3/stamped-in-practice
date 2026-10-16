#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference gain-effect maps.

Primary inference: positive one-sample effect across participants, with a
whole-brain family-wise-error correction from sign-flip max-t permutations.
The input maps are fixed first-level gain-modulator effect estimates.
"""

from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from nilearn import datasets, image, plotting
from scipy import stats
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "input" / "data"
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
ATLAS_DIR = RESULTS / "reference-atlases"
N_PERM = 5000
SEED = 20261015
MASK_PROP = 0.90
ALPHA = 0.05
CHUNK_VOXELS = 4000


def main() -> None:
    started = time.time()
    FIGURES.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(exist_ok=True)

    metadata = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
    files = sorted(DATA.glob("sub-*_hypo1_cope.nii.gz"))
    ids_from_files = [p.name.split("_")[0] for p in files]
    if len(files) != 54 or metadata.participant_id.tolist() != ids_from_files:
        raise RuntimeError("Expected one ordered map for each of 54 metadata rows")
    if not (metadata.group == "equalIndifference").all():
        raise RuntimeError("Unexpected group in participant metadata")

    first_img = nib.load(str(files[0]))
    ref_shape = first_img.shape
    ref_affine = first_img.affine
    arrays: list[np.ndarray] = []
    nonzero_masks: list[np.ndarray] = []
    excluded: list[dict[str, str]] = []
    for path in files:
        img = nib.load(str(path))
        if img.shape != ref_shape or not np.allclose(img.affine, ref_affine, atol=1e-5):
            excluded.append({"participant_id": path.name.split("_")[0], "reason": "grid mismatch"})
            continue
        values = np.asarray(img.dataobj, dtype=np.float32)
        if not np.isfinite(values).all():
            excluded.append({"participant_id": path.name.split("_")[0], "reason": "nonfinite values"})
            continue
        brain = values != 0
        if brain.sum() < 100_000:
            excluded.append({"participant_id": path.name.split("_")[0], "reason": "implausibly sparse map"})
            continue
        arrays.append(values)
        nonzero_masks.append(brain)
    if excluded:
        raise RuntimeError(f"Unexpected map QC exclusions: {excluded}")

    # Zeros in these cope maps represent outside-map coverage. Keep voxels with
    # valid estimates in at least 90% of maps; zero values inside support stay
    # valid numerical estimates in the group model.
    support = np.mean(np.stack(nonzero_masks, axis=0), axis=0)
    group_mask = support >= MASK_PROP
    if not group_mask.any():
        raise RuntimeError("No voxels passed group coverage threshold")
    Y = np.stack(arrays, axis=0)[:, group_mask].astype(np.float64, copy=False)
    n, n_vox = Y.shape
    mean = Y.mean(axis=0)
    sd = Y.std(axis=0, ddof=1)
    se = sd / np.sqrt(n)
    t_obs = mean / se
    p_unc = stats.t.sf(t_obs, df=n - 1)

    # Harvard-Oxford cortical max-probability atlas: an independent anatomical
    # locator (Frontal Medial + Subcallosal labels), not an inferential ROI.
    atlas = datasets.fetch_atlas_harvard_oxford(
        "cort-maxprob-thr25-2mm", data_dir=str(ATLAS_DIR)
    )
    atlas_img = image.resample_to_img(
        atlas.maps, first_img, interpolation="nearest", force_resample=True, copy_header=True
    )
    atlas_arr = np.asarray(atlas_img.dataobj)
    medial_label = atlas.labels.index("Frontal Medial Cortex")
    subcallosal_label = atlas.labels.index("Subcallosal Cortex")
    vmPFC_anatomical = np.isin(atlas_arr, [medial_label, subcallosal_label]) & group_mask
    if not vmPFC_anatomical.any():
        raise RuntimeError("Anatomical vmPFC reference does not intersect group mask")

    roi_values = np.asarray([row[vmPFC_anatomical[group_mask]].mean() for row in Y])
    roi_mean = float(roi_values.mean())
    roi_sd = float(roi_values.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_ci = stats.t.interval(1 - ALPHA, n - 1, loc=roi_mean, scale=roi_se)

    # One-sample sign flips preserve the participant-wise residual structure
    # under the symmetric null. Max positive t over every supported voxel gives
    # strong FWER control for the preregistered positive-direction hypothesis.
    rng = np.random.default_rng(SEED)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n)).astype(np.float32)
    sum_sq = np.sum(Y * Y, axis=0)
    null_max = np.empty(N_PERM, dtype=np.float64)
    for lo in range(0, n_vox, CHUNK_VOXELS):
        hi = min(lo + CHUNK_VOXELS, n_vox)
        signed_sums = signs @ Y[:, lo:hi].astype(np.float32, copy=False)
        denom = sum_sq[lo:hi][None, :] - signed_sums.astype(np.float64) ** 2 / n
        denom = np.maximum(denom, np.finfo(np.float64).tiny)
        perm_t = signed_sums * np.sqrt((n - 1) / n) / np.sqrt(denom)
        null_max = np.maximum(null_max, np.max(perm_t, axis=1)) if lo else np.max(perm_t, axis=1)

    p_fwe = (1 + np.sum(null_max[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)
    roi_idx = vmPFC_anatomical[group_mask]
    roi_sig_count = int(np.sum(p_fwe[roi_idx] <= ALPHA))
    roi_peak_idx = int(np.argmax(t_obs[roi_idx]))
    roi_t_peak = float(t_obs[roi_idx][roi_peak_idx])
    roi_p_fwe_peak = float(p_fwe[roi_idx][roi_peak_idx])
    t_crit = float(np.quantile(null_max, 1 - ALPHA, method="higher"))
    significant = p_fwe <= ALPHA
    sig_indices = np.flatnonzero(significant)
    sig_full = np.zeros(ref_shape, dtype=bool)
    sig_full[group_mask] = significant
    cluster_labels, n_clusters = ndimage.label(sig_full, structure=np.ones((3, 3, 3), dtype=int))
    cluster_rows = []
    for label_id in range(1, n_clusters + 1):
        voxels = np.argwhere(cluster_labels == label_id)
        flat_indices = np.ravel_multi_index(voxels.T, ref_shape)
        map_indices = np.searchsorted(np.flatnonzero(group_mask), flat_indices)
        cluster_peak_idx = int(map_indices[np.argmax(t_obs[map_indices])])
        peak_ijk = np.argwhere(group_mask)[cluster_peak_idx]
        peak_xyz = nib.affines.apply_affine(ref_affine, peak_ijk)
        cluster_rows.append({
            "cluster": label_id,
            "extent_voxels": int(len(voxels)),
            "peak_x_mm": float(peak_xyz[0]),
            "peak_y_mm": float(peak_xyz[1]),
            "peak_z_mm": float(peak_xyz[2]),
            "peak_t": float(t_obs[cluster_peak_idx]),
            "peak_p_fwe": float(p_fwe[cluster_peak_idx]),
            "peak_mean_effect": float(mean[cluster_peak_idx]),
            "atlas_label": atlas.labels[int(atlas_arr[tuple(peak_ijk)])],
        })
    pd.DataFrame(cluster_rows).to_csv(RESULTS / "whole_brain_fwe_clusters.tsv", sep="\t", index=False)
    peak = None
    if len(sig_indices):
        peak_voxel = int(sig_indices[np.argmax(t_obs[sig_indices])])
        ijk = np.argwhere(group_mask)[peak_voxel]
        xyz = nib.affines.apply_affine(ref_affine, ijk).tolist()
        peak = {
            "ijk": [int(v) for v in ijk],
            "mni_xyz_mm": [round(float(v), 2) for v in xyz],
            "t": float(t_obs[peak_voxel]),
            "p_fwe": float(p_fwe[peak_voxel]),
            "mean_effect": float(mean[peak_voxel]),
            "atlas_label": atlas.labels[int(atlas_arr[tuple(ijk)])],
        }

    # Full-volume derivative maps use zero outside the prespecified group mask.
    def save_map(values: np.ndarray, name: str) -> Path:
        data = np.zeros(ref_shape, dtype=np.float32)
        data[group_mask] = np.asarray(values, dtype=np.float32)
        out = RESULTS / name
        nib.save(nib.Nifti1Image(data, ref_affine, first_img.header), str(out))
        return out

    mean_path = save_map(mean, "group_mean_effect.nii.gz")
    t_path = save_map(t_obs, "group_t_positive.nii.gz")
    pfwe_path = save_map(p_fwe, "group_p_fwe_positive.nii.gz")
    mask_path = RESULTS / "group_mask_90pct_coverage.nii.gz"
    nib.save(nib.Nifti1Image(group_mask.astype(np.uint8), ref_affine, first_img.header), str(mask_path))
    roi_path = RESULTS / "vmPFC_reference_mask.nii.gz"
    nib.save(nib.Nifti1Image(vmPFC_anatomical.astype(np.uint8), ref_affine, first_img.header), str(roi_path))

    pd.DataFrame({
        "participant_id": metadata.participant_id,
        "age": metadata.age,
        "gender": metadata.gender,
        "vmPFC_mean_effect": roi_values,
    }).to_csv(RESULTS / "participant_vmPFC_effects.tsv", sep="\t", index=False)

    obs_max_idx = int(np.argmax(t_obs))
    obs_ijk = np.argwhere(group_mask)[obs_max_idx]
    obs_xyz = nib.affines.apply_affine(ref_affine, obs_ijk)
    summary = {
        "analysis": "one-sample positive test of AO86 equal-indifference gain effects",
        "n_participants_input": len(files),
        "n_participants_included": n,
        "excluded_participants": excluded,
        "n_voxels_tested": int(n_vox),
        "mask_rule": "nonzero map coverage in at least 90% of participants",
        "n_permutations_random_sign_flips": N_PERM,
        "seed": SEED,
        "alpha_fwe_one_sided": ALPHA,
        "max_t_critical_fwe": t_crit,
        "significant_voxels_fwe": int(significant.sum()),
        "significant_clusters_26_connected": int(n_clusters),
        "cluster_table": "whole_brain_fwe_clusters.tsv",
        "observed_peak": {
            "mni_xyz_mm": [round(float(v), 2) for v in obs_xyz],
            "t": float(t_obs[obs_max_idx]),
            "p_uncorrected_one_sided": float(p_unc[obs_max_idx]),
            "p_fwe": float(p_fwe[obs_max_idx]),
            "mean_effect": float(mean[obs_max_idx]),
            "atlas_label": atlas.labels[int(atlas_arr[tuple(obs_ijk)])],
        },
        "significant_peak": peak,
        "vmPFC_reference": {
            "atlas": "Harvard-Oxford cortical max-probability atlas, threshold 25%",
            "labels": ["Frontal Medial Cortex", "Subcallosal Cortex"],
            "atlas_template": "MNI152NLin6Asym; nearest-neighbor resampled to supplied map grid",
            "voxels_in_group_mask": int(vmPFC_anatomical.sum()),
            "whole_brain_fwe_significant_voxels": roi_sig_count,
            "peak_t_within_reference": roi_t_peak,
            "peak_p_fwe_within_reference": roi_p_fwe_peak,
            "mean_effect": roi_mean,
            "sd_between_participants": roi_sd,
            "ci95_t": [float(roi_ci[0]), float(roi_ci[1])],
        },
        "map_qc": {
            "all_maps_same_shape_and_affine": True,
            "all_values_finite": True,
            "grid_shape": [int(x) for x in ref_shape],
            "voxel_sizes_mm": [float(x) for x in first_img.header.get_zooms()[:3]],
            "coverage_fraction_min": float(np.min(support[group_mask])),
            "coverage_fraction_median": float(np.median(support[group_mask])),
            "coverage_fraction_max": float(np.max(support[group_mask])),
        },
        "outputs": [p.relative_to(ROOT).as_posix() for p in [mean_path, t_path, pfwe_path, mask_path, roi_path]],
        "software": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "nibabel": nib.__version__,
            "nilearn": __import__("nilearn").__version__,
            "pandas": pd.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "elapsed_seconds": round(time.time() - started, 2),
    }
    (RESULTS / "analysis_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Figure 1: unthresholded estimated group effect and independent atlas
    # locator. The atlas outline is only for localization; all claims use pFWE.
    mean_img = nib.load(str(mean_path))
    t_img = nib.load(str(t_path))
    roi_img = nib.load(str(roi_path))
    display = plotting.plot_stat_map(
        mean_img,
        bg_img=None,
        figure=plt.figure(figsize=(10, 4.8)),
        display_mode="ortho",
        cut_coords=(0, 36, -6),
        threshold=0,
        cmap="coolwarm",
        symmetric_cbar=True,
        colorbar=True,
        vmin=-0.15,
        vmax=0.15,
        black_bg=False,
        dim=-0.4,
        annotate=True,
    )
    display.add_contours(roi_img, levels=[0.5], colors=["#00a6a6"], linewidths=1.2)
    display.frame_axes.figure.suptitle(
        "Unthresholded mean gain effect; teal outline = vmPFC reference",
        color="black", fontsize=13, y=0.99,
    )
    display.savefig(FIGURES / "mean_effect_vmPFC_localization.png", dpi=180)
    display.close()

    # Figure 2: whole-brain corrected positive test (may be empty).
    corrected = np.zeros(ref_shape, dtype=np.float32)
    corrected[group_mask] = np.where(significant, t_obs, 0).astype(np.float32)
    corr_img = nib.Nifti1Image(corrected, ref_affine, first_img.header)
    display = plotting.plot_glass_brain(
        corr_img,
        figure=plt.figure(figsize=(10, 4.8)),
        display_mode="lyrz",
        threshold=0,
        cmap="Reds",
        colorbar=True,
        black_bg=False,
        plot_abs=False,
        vmin=0,
        vmax=float(np.max(t_obs[significant])) if significant.any() else 1,
        annotate=True,
    )
    display.frame_axes.figure.suptitle(
        "Whole-brain max-t FWER, positive direction (α = .05)\n"
        + ("Significant voxels shown at peak slices" if significant.any() else "No significant voxels"),
        color="black", fontsize=13, y=0.99,
    )
    display.savefig(FIGURES / "whole_brain_fwe_positive.png", dpi=180)
    display.close()

    # Figure 3: participant ROI estimates and group mean with t interval.
    fig, ax = plt.subplots(figsize=(7.0, 4.0), constrained_layout=True)
    ax.scatter(np.arange(1, n + 1), roi_values, s=23, color="#526b88", alpha=0.78)
    ax.axhline(roi_mean, color="#bc4b3c", lw=2, label="Group mean")
    ax.axhspan(roi_ci[0], roi_ci[1], color="#bc4b3c", alpha=0.15, label="95% t interval")
    ax.axhline(0, color="#333333", lw=0.8, ls="--")
    ax.set(xlabel="Participant (metadata order)", ylabel="Mean effect estimate (arbitrary units)",
           title="Descriptive vmPFC reference-region estimates")
    ax.legend(frameon=False)
    fig.savefig(FIGURES / "vmPFC_participant_effects.png", dpi=180)
    plt.close(fig)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
