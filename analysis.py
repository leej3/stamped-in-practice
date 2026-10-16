"""Group-level NARPS Hypothesis 1 analysis of fixed AO86 participant maps.

Run from the workspace root with the supplied Python environment:
  python analysis.py --permutations 5000 --seed 20261016

Uses a one-sample random-effects t statistic and participant sign-flip max-T
permutation inference (one-sided; whole-brain voxelwise FWE). The supplied
maps are first-level contrast estimates, not t/z maps.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from scipy import ndimage
from scipy.stats import t as student_t


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = OUT / "figures"
VM_PFC = {"x_min": -20, "x_max": 20, "y_min": 20, "y_max": 60,
          "z_min": -20, "z_max": 20}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main(n_perm: int, seed: int, chunk_size: int) -> None:
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    sources = json.loads((INPUT / "sources.json").read_text())
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    expected_ids = set(participants.participant_id)
    files = sorted((INPUT / "data").glob("*_hypo1_cope.nii.gz"))
    if len(files) != 54 or {p.name.split("_")[0] for p in files} != expected_ids:
        raise RuntimeError("Map count/participant IDs do not match the pinned cohort table")

    data = []
    images = []
    checks = []
    for path in files:
        key = path.relative_to(INPUT).as_posix()
        expected = sources["files"][key]
        actual_hash = sha256(path)
        if path.stat().st_size != expected["bytes"] or actual_hash != expected["sha256"]:
            raise RuntimeError(f"Checksum or byte-size mismatch: {key}")
        img = nib.load(str(path))
        arr = img.get_fdata(dtype=np.float32)
        if not np.isfinite(arr).all():
            raise RuntimeError(f"Non-finite values in {key}")
        data.append(arr)
        images.append(img)
        checks.append({"file": key, "bytes": path.stat().st_size, "sha256": actual_hash})

    ref = images[0]
    if any(a.shape != ref.shape or not np.allclose(a.affine, ref.affine) for a in images):
        raise RuntimeError("Maps do not share an identical voxel grid")
    X4 = np.stack(data, axis=0)
    n = X4.shape[0]
    # Values equal to zero encode out-of-estimation-mask voxels in these maps.
    # A common support avoids treating such absent values as observed zeros.
    mask = np.all(X4 != 0, axis=0)
    if not mask.any():
        raise RuntimeError("No common map support")
    X = X4[:, mask].T.astype(np.float64, copy=False)  # voxels x participants
    mean = X.mean(axis=1)
    sd = X.std(axis=1, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = student_t.sf(t_obs, n - 1)

    rng = np.random.default_rng(seed)
    sumsq = np.sum(X * X, axis=1)
    max_null = np.empty(n_perm, dtype=np.float32)
    for start in range(0, n_perm, chunk_size):
        stop = min(start + chunk_size, n_perm)
        signs = rng.choice(np.array([-1.0, 1.0], dtype=np.float32),
                           size=(stop - start, n), replace=True)
        signed_sums = signs @ X.T.astype(np.float32, copy=False)
        denominator = np.sqrt(np.maximum(n * sumsq[None, :] - signed_sums ** 2, 1e-20))
        t_perm = signed_sums * np.sqrt(n - 1) / denominator
        max_null[start:stop] = t_perm.max(axis=1)
    observed_max = float(np.max(t_obs))
    exceed = int(np.sum(max_null >= observed_max))
    p_max = (exceed + 1) / (n_perm + 1)
    critical = float(np.quantile(max_null, 0.95, method="higher"))
    p_fwe = (1 + n_perm - np.searchsorted(np.sort(max_null), t_obs, side="left")) / (n_perm + 1)
    significant = t_obs >= critical

    # Anatomical identification rule set before reading the result: medial,
    # anterior ventral prefrontal territory in MNI coordinates. This is for
    # labeling corrected whole-brain findings, not for inferential masking.
    ijk = np.column_stack(np.where(mask))
    xyz = nib.affines.apply_affine(ref.affine, ijk)
    roi = ((xyz[:, 0] >= VM_PFC["x_min"]) & (xyz[:, 0] <= VM_PFC["x_max"]) &
           (xyz[:, 1] >= VM_PFC["y_min"]) & (xyz[:, 1] <= VM_PFC["y_max"]) &
           (xyz[:, 2] >= VM_PFC["z_min"]) & (xyz[:, 2] <= VM_PFC["z_max"]))
    sig_roi = significant & roi
    roi_mean = X[roi].mean(axis=0)
    roi_mean_group = float(roi_mean.mean())
    roi_mean_sd = float(roi_mean.std(ddof=1))
    roi_ci = student_t.interval(0.95, n - 1, loc=roi_mean_group,
                                scale=roi_mean_sd / np.sqrt(n))
    roi_peak_i = int(np.argmax(np.where(roi, t_obs, -np.inf)))
    peak_i = int(np.argmax(t_obs))

    mean_vol = np.zeros(mask.shape, dtype=np.float32)
    t_vol = np.zeros(mask.shape, dtype=np.float32)
    p_vol = np.ones(mask.shape, dtype=np.float32)
    mean_vol[mask] = mean
    t_vol[mask] = t_obs
    p_vol[mask] = p_fwe
    sig_vol = np.zeros(mask.shape, dtype=np.uint8)
    sig_vol[mask] = significant.astype(np.uint8)
    nib.save(nib.Nifti1Image(mean_vol, ref.affine, ref.header), OUT / "group_mean_cope.nii.gz")
    nib.save(nib.Nifti1Image(t_vol, ref.affine, ref.header), OUT / "group_t_map.nii.gz")
    nib.save(nib.Nifti1Image(p_vol, ref.affine, ref.header), OUT / "voxelwise_fwe_p.nii.gz")
    nib.save(nib.Nifti1Image(sig_vol, ref.affine, ref.header), OUT / "fwe_significant_mask.nii.gz")
    nib.save(nib.Nifti1Image(mask.astype(np.uint8), ref.affine, ref.header), OUT / "common_support_mask.nii.gz")
    np.save(OUT / "permutation_max_t.npy", max_null)

    cluster_labels, n_clusters = ndimage.label(sig_vol, structure=np.ones((3, 3, 3), dtype=np.uint8))
    cluster_rows = []
    voxel_rows = []
    voxel_volume_mm3 = float(np.prod(ref.header.get_zooms()[:3]))
    tested_flat = np.flatnonzero(mask)
    flat_to_tested = np.full(mask.size, -1, dtype=np.int64)
    flat_to_tested[tested_flat] = np.arange(len(tested_flat))
    for label_id in range(1, n_clusters + 1):
        cluster_ijk = np.column_stack(np.where(cluster_labels == label_id))
        cluster_indices = np.ravel_multi_index(cluster_ijk.T, mask.shape)
        cluster_stat_indices = flat_to_tested[cluster_indices]
        # All cluster voxels lie within `mask`; indices above map them back to the
        # compact tested-voxel arrays without changing their spatial locations.
        local_peak = int(cluster_stat_indices[np.argmax(t_obs[cluster_stat_indices])])
        peak_ijk = ijk[local_peak]
        peak_xyz_cluster = nib.affines.apply_affine(ref.affine, peak_ijk)
        cluster_rows.append({
            "cluster": label_id,
            "voxels": len(cluster_ijk),
            "volume_mm3": len(cluster_ijk) * voxel_volume_mm3,
            "peak_t": float(t_obs[local_peak]),
            "peak_p_FWE": float(p_fwe[local_peak]),
            "peak_x_mm": float(peak_xyz_cluster[0]),
            "peak_y_mm": float(peak_xyz_cluster[1]),
            "peak_z_mm": float(peak_xyz_cluster[2]),
        })
        for ij in cluster_ijk:
            coord = nib.affines.apply_affine(ref.affine, ij)
            compact_idx = flat_to_tested[np.ravel_multi_index(ij, mask.shape)]
            voxel_rows.append({"cluster": label_id, "x_mm": coord[0], "y_mm": coord[1], "z_mm": coord[2],
                               "t": float(t_obs[compact_idx]), "p_FWE": float(p_fwe[compact_idx])})
    pd.DataFrame(cluster_rows).to_csv(OUT / "fwe_clusters.tsv", sep="\t", index=False)
    pd.DataFrame(voxel_rows).to_csv(OUT / "fwe_significant_voxels.tsv", sep="\t", index=False)

    peak_xyz = xyz[peak_i]
    roi_peak_xyz = xyz[roi_peak_i]
    result = {
        "n_participants": n,
        "n_excluded": 0,
        "map_checksums_verified": len(checks),
        "grid_shape": list(ref.shape),
        "voxel_size_mm": [float(x) for x in ref.header.get_zooms()[:3]],
        "common_support_voxels": int(mask.sum()),
        "common_support_volume_ml": float(mask.sum() * np.prod(ref.header.get_zooms()[:3]) / 1000),
        "vmPFC_coordinate_box_MNI_mm": VM_PFC,
        "vmPFC_voxels": int(roi.sum()),
        "vmPFC_mean_cope": roi_mean_group,
        "vmPFC_mean_cope_95pct_t_CI": [float(roi_ci[0]), float(roi_ci[1])],
        "vmPFC_peak_t": float(t_obs[roi_peak_i]),
        "vmPFC_peak_xyz_MNI_mm": [float(x) for x in roi_peak_xyz],
        "vmPFC_FWE_significant_voxels": int(sig_roi.sum()),
        "whole_brain_peak_t": observed_max,
        "whole_brain_peak_xyz_MNI_mm": [float(x) for x in peak_xyz],
        "whole_brain_peak_p_FWE": float(p_max),
        "maxT_critical_t_95pct": critical,
        "whole_brain_FWE_significant_voxels": int(significant.sum()),
        "permutation": {"method": "one-sample participant sign flips; one-sided max-T", "n": n_perm,
                        "seed": seed, "chunk_size": chunk_size,
                        "p_resolution": 1 / (n_perm + 1)},
        "software": {"python": platform.python_version(), "numpy": np.__version__,
                     "scipy": scipy.__version__, "nibabel": nib.__version__,
                     "pandas": pd.__version__},
        "input_files": checks,
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    participants.to_csv(OUT / "included_participants.tsv", sep="\t", index=False)

    # Four informative axial panels: mean contrast estimate, t field,
    # FWE-supported voxels, and distribution of participant vmPFC averages.
    fig, axs = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=True)
    xs = np.arange(mask.shape[0]) * ref.header.get_zooms()[0] + ref.affine[0, 3]
    ys = np.arange(mask.shape[1]) * ref.header.get_zooms()[1] + ref.affine[1, 3]
    zs = np.arange(mask.shape[2]) * ref.header.get_zooms()[2] + ref.affine[2, 3]
    z_index = int(np.argmin(np.abs(zs - 0)))
    extent = [xs[0], xs[-1], ys[0], ys[-1]]
    axial_mean = mean_vol[:, :, z_index].T
    axial_t = t_vol[:, :, z_index].T
    axial_sig = sig_vol[:, :, z_index].T
    axs[0, 0].imshow(axial_mean, origin="lower", extent=extent,
                     cmap="RdBu_r", vmin=-0.15, vmax=0.15)
    axs[0, 0].set_title("Mean gain contrast estimate (z=0 mm)")
    axs[0, 0].set_ylabel("MNI y (mm)")
    axs[0, 1].imshow(axial_t, origin="lower", extent=extent,
                     cmap="magma", vmin=0, vmax=max(critical, 3))
    axs[0, 1].contour(axial_sig, levels=[0.5], colors="cyan",
                      linewidths=0.8, origin="lower", extent=extent)
    axs[0, 1].set_title("One-sample t; cyan = whole-brain FWE p<.05")
    axs[0, 1].set_ylabel("MNI y (mm)")
    for ax in axs[0]:
        ax.set_xlabel("MNI x (mm)")
        ax.set_xlim(-50, 50)
        ax.set_ylim(ys[0], ys[-1])
        ax.add_patch(Rectangle((VM_PFC["x_min"], VM_PFC["y_min"]),
                               VM_PFC["x_max"] - VM_PFC["x_min"],
                               VM_PFC["y_max"] - VM_PFC["y_min"],
                               fill=False, edgecolor="cyan", linewidth=1.0, linestyle="--"))
    axs[1, 0].hist(roi_mean, bins=12, color="#427AA1", edgecolor="white")
    axs[1, 0].axvline(roi_mean_group, color="#C44536", lw=2, label="group mean")
    axs[1, 0].axvline(0, color="black", lw=1)
    axs[1, 0].set_title("Participant mean estimates in vmPFC zone")
    axs[1, 0].set_xlabel("Mean contrast estimate (arbitrary units)")
    axs[1, 0].set_ylabel("Participants")
    axs[1, 0].legend(frameon=False)
    axs[1, 1].axis("off")
    axs[1, 1].text(0, 0.92,
        "Inference summary\n"
        f"N = {n}; exclusions = 0\n"
        f"Whole-brain max-T p = {p_max:.4g}\n"
        f"Whole-brain FWE voxels = {int(significant.sum())}\n"
        f"vmPFC-zone FWE voxels = {int(sig_roi.sum())}\n"
        f"vmPFC mean = {roi_mean_group:.4f} [95% CI {roi_ci[0]:.4f}, {roi_ci[1]:.4f}]\n"
        f"vmPFC-zone peak t = {t_obs[roi_peak_i]:.2f}",
        va="top", fontsize=12, linespacing=1.7)
    fig.suptitle("NARPS equal-indifference group: potential-gain effect", fontsize=15)
    fig.savefig(FIG / "group_gain_effect.png", dpi=180)
    plt.close(fig)

    print(json.dumps({k: v for k, v in result.items() if k != "input_files"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--permutations", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261016)
    parser.add_argument("--chunk-size", type=int, default=16)
    args = parser.parse_args()
    main(args.permutations, args.seed, args.chunk_size)
