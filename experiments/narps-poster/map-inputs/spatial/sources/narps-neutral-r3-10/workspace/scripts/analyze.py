#!/usr/bin/env python3
"""Group inference for NARPS equal-indifference gain-effect maps.

The supplied participant cope maps are fixed inputs. This script does not
re-run preprocessing or first-level modeling.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from scipy import ndimage
from threadpoolctl import threadpool_limits
from nilearn import plotting

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
DATA = INPUT / "data"
OUT = ROOT / "results"
FIG = OUT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
N_PERM = 4999
SEED = 8601
ROI_CENTER = np.array([0.0, 40.0, -8.0])  # MNI; independent valuation meta-analysis
ROI_RADIUS_MM = 10.0


def one_sample_t(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n = x.shape[0]
    mean = x.mean(axis=0, dtype=np.float64)
    sd = x.std(axis=0, ddof=1, dtype=np.float64)
    t = mean / (sd / np.sqrt(n))
    t[~np.isfinite(t)] = 0.0
    return mean, t


def max_t_signflip(x: np.ndarray, observed_t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """One-sided max-t sign-flip test, across voxels in x.

    Sign flips are sampled under the symmetric zero-mean null. The maximum
    positive t per draw provides a single-step whole-brain FWE correction.
    The voxel chunks cap temporary memory use.
    """
    rng = np.random.default_rng(SEED)
    n, p = x.shape
    signs = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(N_PERM, n))
    maxima = np.zeros(N_PERM, dtype=np.float32)
    sumsquares = np.sum(x * x, axis=0, dtype=np.float64)
    root_n = np.sqrt(n)
    with threadpool_limits(limits=4):
        for lo in range(0, p, 5000):
            hi = min(lo + 5000, p)
            block = np.asarray(x[:, lo:hi], dtype=np.float32)
            sums = signs @ block
            # Sign flips preserve sumsquares. This avoids storing the full
            # permutation-by-voxel t-statistic matrix.
            var_num = np.maximum(sumsquares[lo:hi][None, :] - sums.astype(np.float64) ** 2 / n, 0.0)
            denom = np.sqrt(var_num / (n - 1))
            with np.errstate(divide="ignore", invalid="ignore"):
                # sums/n is the permuted sample mean; divide it by its
                # standard error (sample SD / sqrt(n)).
                t_perm = sums / (denom * root_n)
            t_perm[~np.isfinite(t_perm)] = 0.0
            maxima = np.maximum(maxima, np.max(t_perm, axis=1))
    p_fwe = (1 + (maxima[:, None] >= observed_t[None, :]).sum(axis=0)) / (N_PERM + 1)
    cutoff = float(np.quantile(maxima, 0.95, method="higher"))
    return p_fwe.astype(np.float32), np.r_[maxima, np.float32(cutoff)]


def main() -> None:
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    paths = sorted(DATA.glob("sub-*_hypo1_cope.nii.gz"))
    ids = [p.name.split("_")[0] for p in paths]
    if set(ids) != set(participants.participant_id) or len(paths) != 54:
        raise ValueError("Map IDs do not exactly match the supplied 54-person cohort")

    imgs = [nib.load(str(p)) for p in paths]
    ref = imgs[0]
    ref_affine = ref.affine
    arrays = []
    qc = []
    for path, img in zip(paths, imgs):
        if img.shape != ref.shape or not np.allclose(img.affine, ref_affine, atol=1e-5):
            raise ValueError(f"Spatial grid mismatch: {path.name}")
        a = img.get_fdata(dtype=np.float32)
        finite = np.isfinite(a)
        if not finite.all():
            raise ValueError(f"Non-finite values in {path.name}")
        arrays.append(a)
        qc.append({"participant_id": path.name.split("_")[0],
                   "n_nonzero": int(np.count_nonzero(a)),
                   "mean_nonzero": float(a[a != 0].mean()),
                   "sd_nonzero": float(a[a != 0].std(ddof=1)),
                   "min": float(a.min()), "max": float(a.max())})
    stack = np.stack(arrays)
    # Intersection of the supplied nonzero supports: every analyzed voxel has
    # an estimated value for all participants; zeros outside source coverage
    # are not treated as genuine zero effects.
    mask = np.all(stack != 0, axis=0)
    if not mask.any():
        raise ValueError("No common nonzero voxel support")
    coords = nib.affines.apply_affine(ref_affine, np.column_stack(np.where(mask)))
    roi = np.linalg.norm(coords - ROI_CENTER, axis=1) <= ROI_RADIUS_MM
    if not roi.any():
        raise ValueError("vmPFC sphere has no voxels in common analysis mask")

    x = stack[:, mask].astype(np.float64)
    mean, t_obs = one_sample_t(x)
    p_fwe, maxdist_augmented = max_t_signflip(x, t_obs)
    maxdist = maxdist_augmented[:-1]
    max_t_cutoff = float(maxdist_augmented[-1])
    p_unc = stats.t.sf(t_obs, df=len(paths)-1)
    p_fwe_image = np.ones(ref.shape, dtype=np.float32)
    t_image = np.zeros(ref.shape, dtype=np.float32)
    mean_image = np.zeros(ref.shape, dtype=np.float32)
    p_fwe_image[mask] = p_fwe
    t_image[mask] = t_obs.astype(np.float32)
    mean_image[mask] = mean.astype(np.float32)

    roi_x = x[:, roi].mean(axis=1)
    n = len(roi_x)
    roi_mean = float(roi_x.mean())
    roi_sd = float(roi_x.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_t = float(roi_mean / roi_se)
    roi_p_one = float(stats.t.sf(roi_t, n-1))
    roi_ci = [float(roi_mean - stats.t.ppf(.975, n-1)*roi_se),
              float(roi_mean + stats.t.ppf(.975, n-1)*roi_se)]
    roi_vox_t = t_obs[roi]
    roi_vox_p_fwe = p_fwe[roi]
    peak_idx_mask = int(np.argmax(roi_vox_t))
    roi_coord = coords[roi]
    roi_peak_coord = [float(v) for v in roi_coord[peak_idx_mask]]
    roi_peak_t = float(roi_vox_t[peak_idx_mask])
    roi_peak_p_fwe = float(roi_vox_p_fwe[peak_idx_mask])

    # Group-level robustness summaries: mean/median sign agreement in ROI and
    # leave-one-out range for ROI mean. These are sensitivity descriptions.
    loo = [(roi_x.sum() - roi_x[i])/(n-1) for i in range(n)]
    roi_summary = pd.DataFrame({"participant_id": ids, "vmPFC_mean_cope": roi_x})
    roi_summary.to_csv(OUT / "vmPFC_participant_values.tsv", sep="\t", index=False)
    pd.DataFrame(qc).to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)
    for name, arr in [("mean_effect", mean_image), ("t_statistic", t_image), ("p_fwe", p_fwe_image)]:
        nib.save(nib.Nifti1Image(arr, ref_affine, ref.header), str(OUT / f"{name}.nii.gz"))
    roi_img = np.zeros(ref.shape, dtype=np.uint8)
    roi_img[mask] = roi.astype(np.uint8)
    nib.save(nib.Nifti1Image(roi_img, ref_affine, ref.header), str(OUT / "vmPFC_sphere_mask.nii.gz"))

    sig_volume = np.zeros(ref.shape, dtype=bool)
    sig_volume[mask] = p_fwe <= .05
    components, n_components = ndimage.label(sig_volume, structure=np.ones((3, 3, 3), dtype=int))
    cluster_rows = []
    for component_id in range(1, n_components + 1):
        component = components == component_id
        ijk_component = np.column_stack(np.where(component))
        world_component = nib.affines.apply_affine(ref_affine, ijk_component)
        t_component = t_image[component]
        peak_local = int(np.argmax(t_component))
        p_component = p_fwe_image[component]
        cluster_rows.append({"cluster_id": component_id, "n_voxels_26conn": int(component.sum()),
                             "peak_x_mni": float(world_component[peak_local, 0]),
                             "peak_y_mni": float(world_component[peak_local, 1]),
                             "peak_z_mni": float(world_component[peak_local, 2]),
                             "peak_t": float(t_component[peak_local]),
                             "peak_p_fwe": float(p_component[peak_local])})
    pd.DataFrame(cluster_rows).to_csv(OUT / "fwe_clusters.tsv", sep="\t", index=False)

    summary = {
        "n_participants": len(paths), "n_excluded": 0,
        "analysis_mask_voxels": int(mask.sum()), "analysis_mask_rule": "nonzero in all 54 supplied maps",
        "spatial_shape": list(ref.shape), "voxel_size_mm": [float(x) for x in nib.affines.voxel_sizes(ref_affine)],
        "inference": {"test": "one-sided one-sample t with sampled sign-flip max-t correction",
                      "permutations": N_PERM, "seed": SEED, "familywise_alpha": 0.05,
                      "max_t_95_cutoff": max_t_cutoff, "n_fwe_sig_voxels": int((p_fwe <= .05).sum()),
                      "n_clusters_26conn": int(n_components),
                      "minimum_fwe_p_resolution": 1/(N_PERM+1),
                      "max_t_null_median": float(np.median(maxdist)),
                      "largest_observed_t": float(t_obs.max()),
                      "largest_observed_t_mni": [float(v) for v in coords[np.argmax(t_obs)]],
                      "largest_observed_t_fwe_p": float(p_fwe[np.argmax(t_obs)])},
        "vmPFC_roi": {"definition": f"{ROI_RADIUS_MM:g} mm radius sphere centered MNI {ROI_CENTER.tolist()}",
                      "n_voxels": int(roi.sum()), "mean_cope": roi_mean, "sd_across_participants": roi_sd,
                      "se": roi_se, "ci95_t": roi_ci, "one_sided_t": roi_t,
                      "one_sided_p_unadjusted": roi_p_one,
                      "peak_voxel_t": roi_peak_t, "peak_voxel_mni": roi_peak_coord,
                      "peak_voxel_fwe_p": roi_peak_p_fwe,
                      "n_positive_participants": int((roi_x > 0).sum()),
                      "leave_one_out_mean_min": float(np.min(loo)),
                      "leave_one_out_mean_max": float(np.max(loo))},
        "qc": {"all_maps_finite": True, "all_same_shape_and_affine": True,
               "minimum_nonzero_voxels_per_participant": int(min(q["n_nonzero"] for q in qc)),
               "maximum_nonzero_voxels_per_participant": int(max(q["n_nonzero"] for q in qc))},
        "software": {"python": os.sys.version.split()[0], "numpy": np.__version__,
                     "nibabel": nib.__version__}
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Figure 1: display only voxels passing whole-brain max-t correction.
    corrected_effect = np.where(sig_volume, mean_image, 0).astype(np.float32)
    fig = plt.figure(figsize=(12, 5))
    disp = plotting.plot_glass_brain(
        nib.Nifti1Image(corrected_effect, ref_affine), display_mode="lyrz", colorbar=True,
        plot_abs=False, threshold=0, cmap="RdBu_r", vmin=-0.14, vmax=0.14,
        title="Positive gain effects surviving whole-brain max-t FWE correction (p < .05)",
        figure=fig, symmetric_cbar=True)
    # Mark the a priori vmPFC sphere center for spatial orientation.
    disp.add_markers([ROI_CENTER], marker_color="gold", marker_size=55)
    fig.savefig(FIG / "whole_brain_mean_effect.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: all participant ROI values, estimate and interval.
    fig, ax = plt.subplots(figsize=(7, 4.6))
    rng = np.random.default_rng(SEED)
    jitter = rng.normal(0, .035, size=n)
    ax.scatter(jitter, roi_x, color="#35618f", alpha=.75, s=28, edgecolor="white", linewidth=.35)
    ax.errorbar([.42], [roi_mean], yerr=[[roi_mean-roi_ci[0]], [roi_ci[1]-roi_mean]],
                fmt="o", color="#b43b32", capsize=5, markersize=7, label="Mean and 95% t CI")
    ax.axhline(0, color="black", linewidth=.8, linestyle="--")
    ax.set_xlim(-.2, .7)
    ax.set_xticks([0, .42], ["Participants", "Group mean"])
    ax.set_ylabel("vmPFC mean gain-effect estimate (cope)")
    ax.set_title(f"Independent vmPFC valuation sphere ({ROI_RADIUS_MM:g} mm radius; {int(roi.sum())} voxels)")
    ax.legend(frameon=False, loc="best")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "vmPFC_participant_estimates.png", dpi=180)
    plt.close(fig)

    # Record all voxel-level statistics in a tidy table (one row per tested voxel).
    ijk = np.column_stack(np.where(mask))
    world = coords
    pd.DataFrame({"i": ijk[:,0], "j": ijk[:,1], "k": ijk[:,2],
                  "x_mni": world[:,0], "y_mni": world[:,1], "z_mni": world[:,2],
                  "mean_cope": mean, "t": t_obs, "p_unc_one_sided": p_unc,
                  "p_fwe_max_t": p_fwe}).to_csv(OUT / "voxelwise_results.tsv.gz", sep="\t", index=False, compression="gzip")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
