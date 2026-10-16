#!/usr/bin/env python3
"""Group inference for supplied NARPS equal-indifference gain-effect maps."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import nilearn
import numpy as np
import pandas as pd
import scipy
from nilearn.glm.second_level import non_parametric_inference
from nilearn.image import new_img_like
from nilearn.plotting import plot_stat_map


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def image_grid_equal(a: nib.spatialimages.SpatialImage, b: nib.spatialimages.SpatialImage) -> bool:
    return a.shape == b.shape and np.allclose(a.affine, b.affine, atol=1e-5)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true", help="run a bounded 99-permutation whole-brain pilot")
    parser.add_argument("--n-perm", type=int, default=5000)
    args = parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    out_name = "pilot" if args.pilot else "primary"
    n_perm = 99 if args.pilot else args.n_perm

    sources = json.loads((INPUT / "sources.json").read_text())
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    entries = [(pid, INPUT / f"data/{pid}_hypo1_cope.nii.gz", sources["files"][f"data/{pid}_hypo1_cope.nii.gz"])
               for pid in participants.participant_id]

    # Contract and provenance checks are run before model fitting.
    if len(participants) != 54 or participants.participant_id.nunique() != len(participants):
        raise ValueError("Expected 54 unique participant rows")
    if set(participants.group) != {"equalIndifference"}:
        raise ValueError("Unexpected participant group")
    if len(sources["files"]) != 57:  # 54 maps plus the two source tables
        raise ValueError(f"Unexpected source manifest length: {len(sources['files'])}")

    images, arrays, qc_rows = [], [], []
    ref = None
    for pid, path, meta in entries:
        if not path.is_file():
            raise FileNotFoundError(path)
        digest = sha256(path)
        if path.stat().st_size != meta["bytes"] or digest != meta["sha256"]:
            raise ValueError(f"Source byte identity mismatch for {pid}")
        img = nib.load(str(path))
        if ref is None:
            ref = img
        elif not image_grid_equal(ref, img):
            raise ValueError(f"Spatial grid mismatch for {pid}")
        arr = img.get_fdata(dtype=np.float32)
        finite = np.isfinite(arr)
        if not finite.all():
            raise ValueError(f"Nonfinite values in {pid}")
        nz = arr != 0
        arrays.append(arr)
        images.append(str(path))
        qc_rows.append({
            "participant_id": pid,
            "bytes": path.stat().st_size,
            "sha256": digest,
            "finite_voxels": int(finite.sum()),
            "nonzero_voxels": int(nz.sum()),
            "nonzero_fraction": float(nz.mean()),
            "map_mean_allvox": float(arr.mean()),
            "map_sd_allvox": float(arr.std()),
            "map_min": float(arr.min()),
            "map_max": float(arr.max()),
        })

    stack = np.stack(arrays, axis=0)
    # Exact zeros are outside the participant model support in these contrast maps.
    mask = np.all(stack != 0, axis=0) & np.isfinite(stack).all(axis=0)
    n_vox = int(mask.sum())
    if n_vox < 10_000:
        raise ValueError(f"Unexpectedly small common support: {n_vox}")
    mask_img = new_img_like(ref, mask.astype(np.uint8))
    mean = np.mean(stack, axis=0, dtype=np.float64)
    std = np.std(stack, axis=0, ddof=1, dtype=np.float64)
    n = stack.shape[0]
    t_map = np.divide(mean, std / np.sqrt(n), out=np.zeros_like(mean), where=std > 0)
    t_map[~mask] = 0
    mean[~mask] = 0
    # Independent reference statistic on 250 deterministic in-mask voxels.
    flat_ids = np.flatnonzero(mask.ravel())
    ref_ids = flat_ids[np.linspace(0, len(flat_ids) - 1, 250, dtype=int)]
    scipy_t = scipy.stats.ttest_1samp(stack.reshape(n, -1)[:, ref_ids], 0, axis=0,
                                      alternative="greater").statistic
    t_formula_error = float(np.nanmax(np.abs(scipy_t - t_map.ravel()[ref_ids])))

    # One-sample intercept-only, positive direction. Nilearn uses sign-flip
    # permutations for this intercept contrast; maximum-t is whole-mask FWE-corrected.
    dm = pd.DataFrame({"intercept": np.ones(n)})
    inference = non_parametric_inference(
        images,
        design_matrix=dm,
        second_level_contrast="intercept",
        mask=mask_img,
        smoothing_fwhm=None,
        n_perm=n_perm,
        two_sided_test=False,
        random_state=20261016,
        n_jobs=1,
        tfce=False,
        verbose=1,
    )
    logp = inference.get_fdata(dtype=np.float32)
    tperm = t_map.astype(np.float32)
    sig = mask & (logp >= -np.log10(0.05))

    mean_img = new_img_like(ref, mean.astype(np.float32))
    t_img = new_img_like(ref, tperm)
    logp_img = new_img_like(ref, logp)
    nib.save(mean_img, RESULTS / f"{out_name}_mean_effect.nii.gz")
    nib.save(t_img, RESULTS / f"{out_name}_t_unthresholded.nii.gz")
    nib.save(logp_img, RESULTS / f"{out_name}_log10p_maxt_fwe.nii.gz")
    pd.DataFrame(qc_rows).to_csv(RESULTS / f"{out_name}_participant_qc.tsv", sep="\t", index=False)
    np.savez_compressed(RESULTS / f"{out_name}_group_arrays.npz", mean=mean, sd=std, t=tperm, logp_fwe=logp, mask=mask)

    # Summarize corrected voxels and connected components without additional tests.
    from scipy import ndimage
    labels, n_clusters = ndimage.label(sig, structure=ndimage.generate_binary_structure(3, 3))
    clusters = []
    for lab in range(1, n_clusters + 1):
        coords = np.argwhere(labels == lab)
        vals = tperm[labels == lab]
        peak_idx = tuple(coords[np.argmax(vals)])
        xyz = nib.affines.apply_affine(ref.affine, peak_idx).tolist()
        clusters.append({"cluster_id": lab, "voxels_26conn": int(len(coords)), "peak_t": float(np.max(vals)),
                         "peak_mni_mm": [round(float(v), 1) for v in xyz],
                         "peak_log10p_fwe": float(logp[peak_idx])})
    clusters.sort(key=lambda x: x["peak_t"], reverse=True)
    summary = {
        "analysis": out_name, "n_participants": n, "n_permutations": n_perm,
        "seed": 20261016, "alpha": 0.05, "direction": "positive one-sided",
        "correction": "whole-mask maximum-t family-wise error rate",
        "grid_shape": list(ref.shape), "voxel_sizes_mm": [float(v) for v in ref.header.get_zooms()[:3]],
        "common_nonzero_mask_voxels": n_vox, "common_mask_fraction_of_grid": n_vox / np.prod(ref.shape),
        "uncorrected_mean_summary_in_mask": {"mean_of_voxel_means": float(mean[mask].mean()),
                                             "median_of_voxel_means": float(np.median(mean[mask]))},
        "independent_scipy_t_reference_voxels": int(len(ref_ids)),
        "independent_scipy_t_max_abs_difference": t_formula_error,
        "threshold_log10p_fwe": float(-np.log10(.05)), "corrected_voxel_count": int(sig.sum()),
        "clusters_26conn": clusters,
        "software": {"python": platform.python_version(), "nilearn": nilearn.__version__,
                     "nibabel": nib.__version__, "numpy": np.__version__, "scipy": scipy.__version__,
                     "pandas": pd.__version__},
        "input_hashes_sha256": {pid: row["sha256"] for (pid, _, _), row in zip(entries, qc_rows, strict=True)},
    }
    (RESULTS / f"{out_name}_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # A compact group map and an individual-level vmPFC proxy summary.
    fig = plt.figure(figsize=(10, 6))
    display = plot_stat_map(logp_img, bg_img=None, display_mode="ortho", cut_coords=(0, 42, -8),
                            threshold=-np.log10(.05), cmap="magma", colorbar=True,
                            title=f"Positive gain effect: whole-brain max-t FWE (−log10 p), n={n}")
    display.savefig(FIGURES / f"{out_name}_whole_brain_maxt.png", dpi=160)
    display.close()
    plt.close(fig)

    # Plot participant mean estimates in a coordinate-defined medial OFC proxy
    # (x +/- 12, y 24..56, z -20..4 mm); descriptive only, never a primary test.
    ijk = np.indices(ref.shape).reshape(3, -1).T
    xyz = nib.affines.apply_affine(ref.affine, ijk)
    roi_flat = ((np.abs(xyz[:, 0]) <= 12) & (xyz[:, 1] >= 24) & (xyz[:, 1] <= 56) &
                (xyz[:, 2] >= -20) & (xyz[:, 2] <= 4))
    roi = roi_flat.reshape(ref.shape) & mask
    if roi.sum() > 0:
        vals = stack[:, roi].mean(axis=1)
        pd.DataFrame({"participant_id": participants.participant_id, "mean_effect_in_medial_OFC_proxy": vals}).to_csv(
            RESULTS / f"{out_name}_vmPFC_proxy.tsv", sep="\t", index=False)
        fig, ax = plt.subplots(figsize=(7, 4.2))
        ax.scatter(np.arange(1, n + 1), vals, s=25, color="#1f5b78", alpha=.8)
        ax.axhline(0, color="black", linewidth=1)
        ax.axhline(vals.mean(), color="#bd4f28", linewidth=2, label=f"mean = {vals.mean():.4g}")
        ax.set(xlabel="Participant (source table order)", ylabel="Mean gain-effect estimate",
               title="Participant estimates in medial OFC proxy\n(descriptive; uncorrected ROI summary)")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(FIGURES / f"{out_name}_vmPFC_proxy.png", dpi=160)
        plt.close(fig)

    print(json.dumps({k: summary[k] for k in ["analysis", "n_participants", "n_permutations", "common_nonzero_mask_voxels", "corrected_voxel_count", "clusters_26conn"]}, indent=2))


if __name__ == "__main__":
    main()
