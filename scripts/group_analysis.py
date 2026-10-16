#!/usr/bin/env python3
"""Group inference for NARPS equal-indifference gain-effect maps.

Each image is a participant-level first-level gain coefficient (cope), not a
standard error or test statistic. The group model is a one-sample random-effects
model. Positive one-sided inference uses participant-wise sign flips and a
whole-brain max-t family-wise error correction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import nilearn
import numpy as np
import pandas as pd
import scipy
from nilearn import datasets, image
from scipy.stats import t as student_t


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_inputs() -> tuple[pd.DataFrame, list[Path], list[nib.Nifti1Image], dict]:
    participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
    sources = json.loads((ROOT / "input/sources.json").read_text())
    if len(participants) != 54 or participants.participant_id.nunique() != 54:
        raise ValueError("Expected 54 unique participants.")
    if not participants.group.eq("equalIndifference").all():
        raise ValueError("Unexpected group in participants.tsv.")
    records = sources["files"]
    ids = set(participants.participant_id)
    map_ids = {v["participant_id"] for k, v in records.items() if k.endswith(".nii.gz")}
    if ids != map_ids or len(map_ids) != 54:
        raise ValueError("Participant table and map manifest do not match exactly.")
    paths = [ROOT / f"input/data/{pid}_hypo1_cope.nii.gz" for pid in participants.participant_id]
    imgs = []
    for path, pid in zip(paths, participants.participant_id):
        item = records[f"data/{path.name}"]
        if path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            raise ValueError(f"Source integrity check failed for {pid}.")
        imgs.append(nib.load(str(path)))
    ref = imgs[0]
    for pid, img in zip(participants.participant_id, imgs):
        if img.shape != ref.shape or not np.allclose(img.affine, ref.affine, atol=1e-5):
            raise ValueError(f"Shape or affine mismatch for {pid}.")
        if len(img.shape) != 3:
            raise ValueError(f"Expected 3D image for {pid}, got {img.shape}.")
    return participants, paths, imgs, sources


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--permutations", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261015)
    parser.add_argument("--block-voxels", type=int, default=2048)
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    started = time.time()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(exist_ok=True)
    (out / "maps").mkdir(exist_ok=True)

    participants, paths, imgs, sources = load_inputs()
    data = np.stack([np.asarray(img.dataobj, dtype=np.float32) for img in imgs])
    finite = np.isfinite(data)
    nonzero = finite & (data != 0)
    # Fixed common coverage avoids treating zeros outside any participant's
    # acquired/modelled support as estimated effects.
    mask = nonzero.all(axis=0)
    if not np.any(mask):
        raise ValueError("No common nonzero map coverage.")
    X = data[:, mask].astype(np.float64, copy=False).T  # voxel x participant
    n, n_voxels = X.shape[1], X.shape[0]
    df = n - 1
    mean = X.mean(axis=1)
    sd = X.std(axis=1, ddof=1)
    se = sd / np.sqrt(n)
    t_obs = mean / se
    p_unc = student_t.sf(t_obs, df)

    # Sign-flip each participant's whole map, then retain the maximum positive
    # t over all in-mask voxels. Blocking limits RAM while preserving the joint
    # sign-flip field and global maximum statistic.
    rng = np.random.default_rng(args.seed)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(args.permutations, n))
    max_t = np.full(args.permutations, -np.inf, dtype=np.float64)
    sum_sq = np.sum(X * X, axis=1)
    for lo in range(0, n_voxels, args.block_voxels):
        hi = min(lo + args.block_voxels, n_voxels)
        xb = X[lo:hi]
        sums = xb @ signs.T
        # t = sum / sqrt((sum(x^2)-sum(x)^2/n)/(n(n-1)))
        denom = np.sqrt(np.maximum(sum_sq[lo:hi, None] - sums * sums / n, 1e-30) / (n * df))
        perm_t = (sums / n) / denom
        max_t = np.maximum(max_t, np.max(perm_t, axis=0))
    max_t_sorted = np.sort(max_t)
    ge_count = args.permutations - np.searchsorted(max_t_sorted, t_obs, side="left")
    p_fwe = (1 + ge_count) / (args.permutations + 1)
    significant = p_fwe <= 0.05

    # AAL3's bilateral medial orbital frontal parcels are used to label the
    # vmPFC hypothesis anatomically, after whole-brain inference is complete.
    atlas = datasets.fetch_atlas_aal(version="3v2", data_dir=str(out / "reference-atlas-cache"), verbose=0)
    labels = [x.decode() if isinstance(x, bytes) else str(x) for x in atlas.labels]
    roi_names = ["Frontal_Med_Orb_L", "Frontal_Med_Orb_R"]
    absent = set(roi_names) - set(labels)
    if absent:
        raise ValueError(f"Expected AAL3 ROI labels not found: {sorted(absent)}")
    label_values = [int(atlas.indices[labels.index(x)]) for x in roi_names]
    ref_img = imgs[0]
    roi_img = image.resample_to_img(atlas.maps, ref_img, interpolation="nearest", force_resample=True, copy_header=True)
    aal = np.asarray(roi_img.dataobj)
    roi_mask = np.isin(aal, label_values) & mask
    if roi_mask.sum() == 0:
        raise ValueError("AAL3 bilateral medial orbital frontal parcel has no common coverage.")
    roi_values = data[:, roi_mask]
    roi_subject_mean = roi_values.mean(axis=1)
    roi_group_mean = float(roi_subject_mean.mean())
    roi_group_sd = float(roi_subject_mean.std(ddof=1))
    roi_se = roi_group_sd / np.sqrt(n)
    roi_ci = [float(roi_group_mean - student_t.ppf(0.975, df) * roi_se),
              float(roi_group_mean + student_t.ppf(0.975, df) * roi_se)]
    roi_t = float(roi_group_mean / roi_se)
    roi_p_unc = float(student_t.sf(roi_t, df))
    roi_robust_z = (roi_subject_mean - np.median(roi_subject_mean)) / max(
        1.4826 * np.median(np.abs(roi_subject_mean - np.median(roi_subject_mean))), 1e-12
    )
    outlier_idx = np.flatnonzero(np.abs(roi_robust_z) > 3)
    loo = None
    if len(outlier_idx) == 1:
        keep = np.arange(n) != outlier_idx[0]
        loo_mean = float(roi_subject_mean[keep].mean())
        loo_se = float(roi_subject_mean[keep].std(ddof=1) / np.sqrt(keep.sum()))
        loo_ci = [float(loo_mean - student_t.ppf(0.975, keep.sum() - 1) * loo_se),
                  float(loo_mean + student_t.ppf(0.975, keep.sum() - 1) * loo_se)]
        loo = {"flagged_participant_id": str(participants.participant_id.iloc[outlier_idx[0]]),
               "mean_without_flagged_participant": loo_mean, "mean_95pct_t_CI_without_flagged_participant": loo_ci}
    roi_linear_indices = np.flatnonzero(roi_mask[mask])
    roi_peak_linear_index = roi_linear_indices[np.argmax(t_obs[roi_linear_indices])]
    global_peak_linear_index = int(np.argmax(t_obs))
    ijk_mask = np.argwhere(mask)
    roi_peak_ijk = ijk_mask[roi_peak_linear_index]
    global_peak_ijk = ijk_mask[global_peak_linear_index]
    roi_peak_xyz = nib.affines.apply_affine(ref_img.affine, roi_peak_ijk).tolist()
    global_peak_xyz = nib.affines.apply_affine(ref_img.affine, global_peak_ijk).tolist()
    roi_fwe_significant_count = int(significant[roi_linear_indices].sum())

    # Group-level image outputs use NIfTI in the original MNI grid.
    def save_map(values: np.ndarray, name: str, dtype=np.float32, outside_value=0) -> None:
        volume = np.full(ref_img.shape, outside_value, dtype=dtype)
        volume[mask] = values.astype(dtype)
        img = nib.Nifti1Image(volume, ref_img.affine, ref_img.header.copy())
        img.set_data_dtype(dtype)
        nib.save(img, out / "maps" / name)

    save_map(mean, "group_mean_effect.nii.gz")
    save_map(t_obs, "group_tstat.nii.gz")
    save_map(p_fwe, "group_positive_maxT_pFWE.nii.gz", outside_value=np.nan)
    save_map(np.where(significant, t_obs, 0), "group_positive_maxT_FWE05_tstat.nii.gz")
    roi_volume = np.zeros(ref_img.shape, dtype=np.uint8)
    roi_volume[roi_mask] = 1
    nib.save(nib.Nifti1Image(roi_volume, ref_img.affine, ref_img.header.copy()), out / "maps/vmpfc_aal3_medial_orbitofrontal_mask.nii.gz")

    # Connected components summarize the corrected voxels without using a
    # cluster-extent threshold for inference.
    from scipy import ndimage
    sig_volume = np.zeros(ref_img.shape, dtype=bool)
    sig_volume[mask] = significant
    labels_3d, n_clusters = ndimage.label(sig_volume, structure=np.ones((3, 3, 3), dtype=bool))
    aal_lookup = {int(index): label for label, index in zip(labels, atlas.indices)}
    cluster_rows = []
    for cluster_id in range(1, n_clusters + 1):
        ijk = np.argwhere(labels_3d == cluster_id)
        # Map component coordinates back to the compact common-mask vector.
        ijk_to_linear = np.ravel_multi_index(ijk.T, ref_img.shape)
        compact = np.searchsorted(np.flatnonzero(mask), ijk_to_linear)
        peak_compact = compact[np.argmax(t_obs[compact])]
        peak_ijk = ijk[np.argmax(t_obs[compact])]
        peak_xyz = nib.affines.apply_affine(ref_img.affine, peak_ijk)
        atlas_value = int(aal[tuple(peak_ijk)])
        cluster_rows.append({
            "cluster": cluster_id, "voxels_26_connected": int(len(ijk)),
            "volume_mm3": float(len(ijk) * np.prod(ref_img.header.get_zooms()[:3])),
            "peak_t": float(t_obs[peak_compact]),
            "peak_maxT_pFWE": float(p_fwe[peak_compact]),
            "peak_x_mm": float(peak_xyz[0]), "peak_y_mm": float(peak_xyz[1]), "peak_z_mm": float(peak_xyz[2]),
            "peak_AAL3_label": aal_lookup.get(atlas_value, "outside_AAL3_labeled_regions"),
        })
    pd.DataFrame(cluster_rows).to_csv(out / "whole_brain_fwe_clusters.csv", index=False)

    table = pd.DataFrame({
        "participant_id": participants.participant_id,
        "vmPFC_mean_effect": roi_subject_mean,
        "robust_z": roi_robust_z,
        "flag_robust_abs_z_gt_3": np.abs(roi_robust_z) > 3,
    })
    table.to_csv(out / "participant_roi_effects.csv", index=False)
    voxel_table = pd.DataFrame({
        "mask_voxels": [n_voxels], "significant_positive_maxT_FWE05": [int(significant.sum())],
        "max_observed_t": [float(t_obs.max())], "max_t_monte_carlo_pFWE": [float(p_fwe.min())],
        "roi_voxels": [int(roi_mask.sum())], "roi_peak_t": [float(t_obs[roi_peak_linear_index])],
        "roi_peak_x_mm": [float(roi_peak_xyz[0])], "roi_peak_y_mm": [float(roi_peak_xyz[1])], "roi_peak_z_mm": [float(roi_peak_xyz[2])],
    })
    voxel_table.to_csv(out / "group_summary.csv", index=False)

    # Visual 1: participant effects in the atlas-defined ROI; inference is
    # shown descriptively and is not the primary, whole-brain corrected test.
    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    jitter = rng.normal(0, 0.045, size=n)
    ax.scatter(jitter, roi_subject_mean, s=26, color="#356a9a", alpha=0.8, edgecolor="white", linewidth=0.35)
    ax.errorbar([0.33], [roi_group_mean], yerr=[[roi_group_mean - roi_ci[0]], [roi_ci[1] - roi_group_mean]],
                fmt="D", color="#ad5d24", capsize=4, markersize=6, label="Mean and 95% t interval")
    ax.axhline(0, color="#4c4c4c", linewidth=1)
    ax.set_xlim(-0.18, 0.52)
    ax.set_xticks([0, 0.33], ["Participants", "Group mean"])
    ax.set_ylabel("First-level gain coefficient (arbitrary model units)")
    ax.set_title("Participant gain effects in bilateral AAL3 medial orbitofrontal cortex")
    ax.text(0.02, 0.98, f"n = {n}; voxel-average per participant\n95% t CI [{roi_ci[0]:.3g}, {roi_ci[1]:.3g}]",
            transform=ax.transAxes, va="top", ha="left", fontsize=9)
    ax.legend(frameon=False, loc="lower right")
    fig.savefig(out / "figures/roi_participant_effects.png", dpi=220)
    plt.close(fig)

    # Visual 2: unthresholded t field with the atlas parcel outline. The map
    # carries no threshold-based claim; the tested outcome is the max-T pFWE.
    from nilearn import plotting
    t_img = nib.load(str(out / "maps/group_tstat.nii.gz"))
    roi_nii = nib.load(str(out / "maps/vmpfc_aal3_medial_orbitofrontal_mask.nii.gz"))
    disp = plotting.plot_stat_map(t_img, bg_img=None, display_mode="ortho", cut_coords=(0, 28, -8),
                                  threshold=0.0, cmap="cold_hot", colorbar=True,
                                  title="t map + vmPFC ROI")
    disp.add_contours(roi_nii, levels=[0.5], colors="#f0c04a", linewidths=1.3)
    disp.savefig(out / "figures/group_tmap_vmPFC.png", dpi=220)
    disp.close()
    sig_img = nib.load(str(out / "maps/group_positive_maxT_FWE05_tstat.nii.gz"))
    disp = plotting.plot_stat_map(sig_img, bg_img=None, display_mode="ortho",
                                  cut_coords=tuple(float(v) for v in global_peak_xyz), threshold=0,
                                  cmap="Reds", colorbar=True,
                                  title="FWE hits (n = 24)")
    disp.savefig(out / "figures/whole_brain_maxT_FWE.png", dpi=220)
    disp.close()

    all_effects = np.asarray(data[:, mask])
    qc = {
        "n_participants": n,
        "participant_id_match": True,
        "source_sha256_and_byte_checks": "passed for all 54 maps",
        "map_shape": list(ref_img.shape),
        "voxel_sizes_mm": [float(x) for x in ref_img.header.get_zooms()[:3]],
        "common_nonzero_voxels": int(n_voxels),
        "nonfinite_values": int((~finite).sum()),
        "zero_voxel_fraction_per_map_min": float((~nonzero).reshape(n, -1).mean(axis=1).min()),
        "zero_voxel_fraction_per_map_max": float((~nonzero).reshape(n, -1).mean(axis=1).max()),
        "effect_abs_percentiles_50_95_99_999": [float(v) for v in np.percentile(np.abs(all_effects), [50, 95, 99, 99.9])],
        "roi_subject_robust_outlier_flags": int((np.abs(roi_robust_z) > 3).sum()),
        "vmPFC_roi_positive_maxT_FWE05_voxels": roi_fwe_significant_count,
        "roi_subject_effect_min_max": [float(roi_subject_mean.min()), float(roi_subject_mean.max())],
    }
    (out / "quality_checks.json").write_text(json.dumps(qc, indent=2) + "\n")
    result = {
        "analysis": "one-sample random-effects group model with positive one-sided participant-level sign-flip max-t FWE inference",
        "n": n, "df": df, "permutations": args.permutations, "seed": args.seed,
        "mask_definition": "voxels finite and nonzero in every supplied effect map",
        "whole_brain_voxels": n_voxels,
        "fwe_alpha": 0.05,
        "significant_positive_whole_brain_voxels": int(significant.sum()),
        "smallest_monte_carlo_maxT_pFWE": float(p_fwe.min()),
        "observed_max_t": float(t_obs.max()),
        "whole_brain_peak_mni_xyz_mm": [float(v) for v in global_peak_xyz],
        "whole_brain_peak_positive_maxT_pFWE": float(p_fwe[global_peak_linear_index]),
        "vmPFC_anatomical_label": "bilateral AAL3 Frontal_Med_Orb parcels; descriptive localization only",
        "vmPFC_roi_voxels": int(roi_mask.sum()),
        "vmPFC_roi_mean_effect": roi_group_mean,
        "vmPFC_roi_mean_95pct_t_CI": roi_ci,
        "vmPFC_roi_one_sided_uncorrected_p_descriptive_only": roi_p_unc,
        "vmPFC_roi_mean_t_descriptive_only": roi_t,
        "vmPFC_roi_peak_t": float(t_obs[roi_peak_linear_index]),
        "vmPFC_roi_peak_mni_xyz_mm": [float(v) for v in roi_peak_xyz],
        "vmPFC_roi_peak_positive_maxT_pFWE": float(p_fwe[roi_peak_linear_index]),
        "vmPFC_roi_positive_maxT_FWE05_voxels": roi_fwe_significant_count,
        "vmPFC_roi_outlier_leave_one_out_sensitivity": loo,
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                     "nibabel": nib.__version__, "nilearn": nilearn.__version__, "pandas": pd.__version__},
        "runtime_seconds": round(time.time() - started, 3),
    }
    (out / "analysis_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print(f"QC: {json.dumps(qc, sort_keys=True)}")
    print(f"Completed in {time.time() - started:.1f} s; output={out}")


if __name__ == "__main__":
    main()
