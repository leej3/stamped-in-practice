#!/usr/bin/env python
"""One-sample whole-brain permutation inference for the NARPS AO86 gain maps."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import nilearn
import numpy as np
import pandas as pd
import scipy
from nilearn import datasets, image, plotting
from scipy import ndimage, stats


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
SEED = 20261015
N_PERM = 5000
FWE_ALPHA = 0.05
MIN_COVERAGE = 1.00
CHUNK = 10_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def affine_close(a: np.ndarray, b: np.ndarray) -> bool:
    return bool(np.allclose(a, b, atol=1e-4))


def one_sample_t(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = values.shape[0]
    mean = values.mean(axis=0)
    sd = values.std(axis=0, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        tvals = mean / (sd / np.sqrt(n))
    tvals = np.where(np.isfinite(tvals), tvals, 0.0)
    return mean, sd, tvals


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    manifest = json.loads((INPUT / "sources.json").read_text())
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    expected = participants.participant_id.tolist()
    mapping = {key: value for key, value in manifest["files"].items() if key.startswith("data/")}
    if len(expected) != 54 or len(mapping) != 54:
        raise ValueError(f"Expected 54 maps and participants; found {len(mapping)}, {len(expected)}")
    if participants.participant_id.duplicated().any():
        raise ValueError("Duplicate participant identifiers")

    imgs: list[nib.spatialimages.SpatialImage] = []
    arrays: list[np.ndarray] = []
    quality: list[dict] = []
    reference_affine = None
    reference_shape = None
    for participant_id in expected:
        rel = f"data/{participant_id}_hypo1_cope.nii.gz"
        record = mapping[rel]
        path = INPUT / rel
        if record["participant_id"] != participant_id:
            raise ValueError(f"Participant mismatch in source manifest for {rel}")
        observed_hash = sha256(path)
        if observed_hash != record["sha256"]:
            raise ValueError(f"SHA-256 mismatch for {rel}: {observed_hash}")
        img = nib.load(str(path))
        data = img.get_fdata(dtype=np.float32)
        if reference_affine is None:
            reference_affine, reference_shape = img.affine.copy(), img.shape
        if img.shape != reference_shape or not affine_close(img.affine, reference_affine):
            raise ValueError(f"Spatial grid mismatch for {rel}")
        if not np.isfinite(data).all():
            raise ValueError(f"Non-finite data in {rel}")
        support = data != 0
        quality.append(
            {
                "participant_id": participant_id,
                "sha256_verified": True,
                "nonzero_voxels": int(support.sum()),
                "mean_nonzero": float(data[support].mean()),
                "sd_nonzero": float(data[support].std(ddof=1)),
                "min": float(data.min()),
                "max": float(data.max()),
                "finite_fraction": float(np.isfinite(data).mean()),
            }
        )
        imgs.append(img)
        arrays.append(data)

    data4d = np.stack(arrays, axis=0)
    n = data4d.shape[0]
    support_n = np.count_nonzero(data4d != 0, axis=0)
    # Input zeros mark voxels outside an individual's estimation mask; use the
    # all-participant intersection so no absent estimate is treated as zero.
    mask = support_n == n
    if mask.sum() < 10_000:
        raise ValueError(f"Unexpectedly small group mask ({mask.sum()} voxels)")
    flat_indices = np.flatnonzero(mask.ravel())
    matrix = data4d.reshape(n, -1)[:, flat_indices].astype(np.float64, copy=False)
    mean, sd, t_obs = one_sample_t(matrix)

    rng = np.random.default_rng(SEED)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n))
    max_null = np.full(N_PERM, -np.inf, dtype=np.float64)
    # Synchronized participant-level sign flips preserve the spatial dependence
    # among voxels; the maximum positive t controls one-sided whole-brain FWE.
    for start in range(0, matrix.shape[1], CHUNK):
        stop = min(start + CHUNK, matrix.shape[1])
        block = matrix[:, start:stop]
        signed_sums = signs @ block
        signed_means = signed_sums / n
        signed_var = (np.sum(block * block, axis=0)[None, :] - signed_sums**2 / n) / (n - 1)
        signed_var = np.maximum(signed_var, 0.0)
        denom = np.sqrt(signed_var / n)
        with np.errstate(divide="ignore", invalid="ignore"):
            t_perm = signed_means / denom
        t_perm = np.where(np.isfinite(t_perm), t_perm, 0.0)
        max_null = np.maximum(max_null, t_perm.max(axis=1))
        print(f"Permutation chunk complete: voxels {start + 1}-{stop}/{matrix.shape[1]}", flush=True)

    t_critical = float(np.quantile(max_null, 1 - FWE_ALPHA, method="higher"))
    p_fwe = np.empty_like(t_obs, dtype=np.float64)
    for start in range(0, len(t_obs), CHUNK):
        stop = min(start + CHUNK, len(t_obs))
        p_fwe[start:stop] = (
            1 + np.count_nonzero(max_null[:, None] >= t_obs[None, start:stop], axis=0)
        ) / (N_PERM + 1)
    p_unc = stats.t.sf(t_obs, df=n - 1)
    sig = (t_obs >= t_critical) & (p_fwe <= FWE_ALPHA)
    p_unc_two = stats.t.sf(np.abs(t_obs), df=n - 1) * 2

    full_mean = np.zeros(mask.size, dtype=np.float32)
    full_sd = np.zeros(mask.size, dtype=np.float32)
    full_t = np.zeros(mask.size, dtype=np.float32)
    full_p = np.ones(mask.size, dtype=np.float32)
    full_sig = np.zeros(mask.size, dtype=np.uint8)
    full_mean[flat_indices] = mean.astype(np.float32)
    full_sd[flat_indices] = sd.astype(np.float32)
    full_t[flat_indices] = t_obs.astype(np.float32)
    full_p[flat_indices] = p_fwe.astype(np.float32)
    full_sig[flat_indices] = sig.astype(np.uint8)
    affine = reference_affine
    header = imgs[0].header.copy()

    def save_map(name: str, data: np.ndarray, dtype=None) -> None:
        arr = data.reshape(reference_shape)
        if dtype is not None:
            arr = arr.astype(dtype)
        nib.save(nib.Nifti1Image(arr, affine, header), RESULTS / name)

    save_map("mean_gain_cope.nii.gz", full_mean)
    save_map("sd_gain_cope.nii.gz", full_sd)
    save_map("t_gain.nii.gz", full_t)
    save_map("p_fwe_gain.nii.gz", full_p)
    save_map("sig_fwe_gain.nii.gz", full_sig, np.uint8)
    save_map("group_coverage_mask.nii.gz", mask.ravel().astype(np.uint8), np.uint8)

    # Anatomical localization is descriptive: Harvard-Oxford atlas labels
    # approximate medial orbitofrontal/subgenual vmPFC, with a midline restriction.
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    labels = [str(x) for x in atlas.labels]
    target_labels = [
        "Frontal Medial Cortex",
        "Subcallosal Cortex",
        "Frontal Orbital Cortex",
        "Paracingulate Gyrus",
    ]
    missing_labels = [x for x in target_labels if x not in labels]
    if missing_labels:
        raise ValueError(f"Missing expected Harvard-Oxford labels: {missing_labels}; labels={labels}")
    atlas_img = atlas.maps if isinstance(atlas.maps, nib.spatialimages.SpatialImage) else nib.load(atlas.maps)
    atlas_data = image.resample_to_img(atlas_img, imgs[0], interpolation="nearest").get_fdata()
    atlas_ids = [labels.index(x) for x in target_labels]
    atlas_roi = np.isin(atlas_data.astype(int), atlas_ids)
    ijk = np.array(np.where(np.ones(reference_shape, dtype=bool))).T
    xyz = nib.affines.apply_affine(affine, ijk)
    medial = (np.abs(xyz[:, 0]) <= 20) & (xyz[:, 1] >= 0) & (xyz[:, 2] <= 0)
    medial_grid = np.zeros(reference_shape, dtype=bool)
    medial_grid.ravel()[np.flatnonzero(medial)] = True
    roi = atlas_roi & medial_grid & mask.reshape(reference_shape)
    if roi.sum() == 0:
        raise ValueError("Atlas-defined vmPFC approximation is empty")
    save_map("vmPFC_atlas_approx_mask.nii.gz", roi.astype(np.uint8), np.uint8)

    # Re-read array extraction in participant order for a descriptive ROI estimate.
    roi_idx = np.flatnonzero(roi.ravel())
    roi_subject = data4d.reshape(n, -1)[:, roi_idx].mean(axis=1)
    roi_t, roi_p = stats.ttest_1samp(roi_subject, 0, alternative="greater")
    roi_ci = stats.t.interval(0.95, n - 1, loc=roi_subject.mean(), scale=stats.sem(roi_subject))
    roi_peak_flat = roi_idx[np.argmax(full_t[roi_idx])]
    roi_peak_ijk = np.array(np.unravel_index(roi_peak_flat, reference_shape))
    roi_peak_xyz = nib.affines.apply_affine(affine, roi_peak_ijk)
    pd.DataFrame({"participant_id": expected, "roi_mean_cope": roi_subject}).to_csv(
        RESULTS / "vmPFC_participant_means.tsv", sep="\t", index=False
    )
    pd.DataFrame(quality).to_csv(RESULTS / "map_quality.tsv", sep="\t", index=False)

    # Connected components among corrected positive voxels, 26-connectivity.
    sig_grid = np.zeros(reference_shape, dtype=bool)
    sig_grid.ravel()[flat_indices] = sig
    component, count = ndimage.label(sig_grid, structure=np.ones((3, 3, 3), dtype=np.uint8))
    clusters = []
    for cid in range(1, count + 1):
        cluster_indices = np.flatnonzero(component.ravel() == cid)
        peak_linear = cluster_indices[np.argmax(full_t[cluster_indices])]
        peak_ijk = np.array(np.unravel_index(peak_linear, reference_shape))
        peak_xyz = nib.affines.apply_affine(affine, peak_ijk)
        clusters.append(
            {
                "cluster_id": cid,
                "voxels": int(len(cluster_indices)),
                "peak_t": float(full_t[peak_linear]),
                "peak_mean_cope": float(full_mean[peak_linear]),
                "peak_mni_x": float(peak_xyz[0]),
                "peak_mni_y": float(peak_xyz[1]),
                "peak_mni_z": float(peak_xyz[2]),
                "overlaps_vmPFC_approx": bool(np.any(roi.ravel()[cluster_indices])),
            }
        )
    clusters.sort(key=lambda x: x["peak_t"], reverse=True)
    pd.DataFrame(clusters).to_csv(RESULTS / "fwe_clusters.tsv", sep="\t", index=False)

    counts = {
        "voxels": int(mask.sum()),
        "significant_positive_voxels": int(sig.sum()),
        "vmPFC_approx_voxels": int(roi.sum()),
        "significant_vmPFC_approx_voxels": int(np.count_nonzero(sig_grid & roi)),
    }
    max_obs_idx = int(np.argmax(t_obs))
    max_obs_flat = int(flat_indices[max_obs_idx])
    peak_ijk = np.array(np.unravel_index(max_obs_flat, reference_shape))
    peak_xyz = nib.affines.apply_affine(affine, peak_ijk)
    output = {
        "analysis": "one-sample positive group effect; participant-level sign-flip max-t correction",
        "n_participants": n,
        "n_excluded": 0,
        "permutations": N_PERM,
        "seed": SEED,
        "fwe_alpha": FWE_ALPHA,
        "fwe_t_critical": t_critical,
        "max_null_t_95": float(np.quantile(max_null, 0.95)),
        "min_coverage_fraction": MIN_COVERAGE,
        "mask_voxels": int(mask.sum()),
        "mask_volume_ml": float(mask.sum() * np.prod(nib.affines.voxel_sizes(affine)) / 1000),
        "peak_unthresholded": {
            "t": float(t_obs[max_obs_idx]),
            "p_fwe": float(p_fwe[max_obs_idx]),
            "p_unc_one_sided": float(p_unc[max_obs_idx]),
            "mean_cope": float(mean[max_obs_idx]),
            "sd_cope": float(sd[max_obs_idx]),
            "mni_xyz": [float(v) for v in peak_xyz],
        },
        "counts": counts,
        "fwe_clusters": clusters,
        "vmPFC_atlas_approx": {
            "atlas": "Harvard-Oxford cortical atlas, max-probability 25% threshold, resampled nearest-neighbor",
            "labels": target_labels,
            "additional_coordinate_limits_mni": "|x| <= 20 mm, y >= 0 mm, z <= 0 mm",
            "n_voxels": int(roi.sum()),
            "mean_subject_roi_cope": float(roi_subject.mean()),
            "sd_subject_roi_cope": float(roi_subject.std(ddof=1)),
            "ci95_t": [float(roi_ci[0]), float(roi_ci[1])],
            "t_one_sided_uncorrected_descriptive": float(roi_t),
            "p_one_sided_uncorrected_descriptive": float(roi_p),
            "peak_voxel_t": float(full_t[roi_peak_flat]),
            "peak_voxel_p_fwe": float(full_p[roi_peak_flat]),
            "peak_voxel_mni_xyz": [float(v) for v in roi_peak_xyz],
            "participant_positive_fraction": float(np.mean(roi_subject > 0)),
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "nibabel": nib.__version__,
            "nilearn": nilearn.__version__,
            "pandas": pd.__version__,
        },
        "quality_summary": {
            "all_hashes_match_manifest": True,
            "all_grids_match": True,
            "all_voxels_finite": True,
            "map_nonzero_voxels_min": int(min(q["nonzero_voxels"] for q in quality)),
            "map_nonzero_voxels_max": int(max(q["nonzero_voxels"] for q in quality)),
        },
    }
    (RESULTS / "group_results.json").write_text(json.dumps(output, indent=2) + "\n")

    # Figure 1: unthresholded t values, with vmPFC atlas approximation as contour.
    bg = datasets.load_mni152_template(resolution=2)
    t_img = nib.Nifti1Image(full_t.reshape(reference_shape), affine, header)
    display = plotting.plot_stat_map(
        t_img,
        bg_img=bg,
        threshold=stats.t.ppf(0.999, n - 1),
        display_mode="z",
        cut_coords=[-16, -8, 0, 8, 16],
        cmap="cold_hot",
        colorbar=True,
        title="Gain-effect group t map (uncorrected display threshold)",
        vmin=0,
        vmax=max(7.0, float(np.max(t_obs))),
        annotate=True,
        black_bg=False,
    )
    fig1 = display.frame_axes.figure
    fig1.text(0.015, 0.01, f"One-sided whole-brain max-t FWE t*={t_critical:.2f}; {sig.sum()} voxels pass FWE. vmPFC ROI estimate is summarized separately.", fontsize=8)
    fig1.savefig(FIGURES / "whole_brain_gain_t_map.png", dpi=180, bbox_inches="tight")
    plt.close(fig1)

    # Figure 2: descriptive participant-level effect summaries in the anatomical approximation.
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.axhline(0, color="0.35", linewidth=1)
    jitter = rng.normal(0, 0.035, size=n)
    ax.scatter(np.ones(n) + jitter, roi_subject, alpha=0.78, s=28, color="#2878B5", edgecolor="white", linewidth=0.3)
    ax.errorbar([1], [roi_subject.mean()], yerr=[[roi_subject.mean() - roi_ci[0]], [roi_ci[1] - roi_subject.mean()]], fmt="D", color="#B33B2E", capsize=5, markersize=6, label="Mean and 95% t CI")
    ax.set_xlim(0.72, 1.28)
    ax.set_xticks([1], ["vmPFC atlas approximation"])
    ax.set_ylabel("Mean participant gain-effect coefficient (arbitrary model units)")
    ax.set_title("Participant effects in the anatomical vmPFC approximation")
    ax.legend(frameon=False, loc="best")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES / "vmPFC_participant_effects.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
