#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference gain-effect maps.

Run from the workspace root with the prepared Python environment:
  python analysis.py

This analyzes only the supplied participant-level contrast estimates. It does
not retrieve scans, redo preprocessing, or reconstruct the first-level model.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("output/.mplconfig").resolve()))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from scipy.ndimage import gaussian_filter
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
FIG = OUT / "figures"
MAPS = OUT / "maps"
SEED = 20261016
N_PERM = 5000
FWHM_MM = 6.0
ALPHA = 0.05


def main():
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    MAPS.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((ROOT / "input/sources.json").read_text())
    participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
    participants = participants.sort_values("participant_id").reset_index(drop=True)
    if len(participants) != 54 or participants.participant_id.nunique() != 54:
        raise ValueError("Expected the complete, unique 54-person cohort")

    arrays = []
    ref = None
    qc = []
    for _, row in participants.iterrows():
        rel = f"data/{row.participant_id}_hypo1_cope.nii.gz"
        file_path = ROOT / "input" / rel
        entry = metadata["files"][rel]
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"SHA256 mismatch: {rel}")
        img = nib.load(file_path)
        if ref is None:
            ref = img
        elif img.shape != ref.shape or not np.allclose(img.affine, ref.affine, atol=1e-5):
            raise ValueError(f"Spatial geometry mismatch: {rel}")
        data = img.get_fdata(dtype=np.float32)
        if not np.isfinite(data).all():
            raise ValueError(f"Non-finite values: {rel}")
        arrays.append(data)
        qc.append({
            "participant_id": row.participant_id,
            "age": int(row.age),
            "gender": row.gender,
            "sha256_verified": True,
            "nonzero_voxels": int(np.count_nonzero(data)),
            "minimum": float(data.min()),
            "maximum": float(data.max()),
            "mean_all_voxels": float(data.mean()),
        })
    Y0 = np.stack(arrays)

    # Common-support mask excludes image background and edge voxels not
    # estimated for at least 90% of participants. The supplied maps are zero
    # filled outside their acquired/estimated brain support.
    coverage = np.mean(Y0 != 0, axis=0)
    mask = coverage >= 0.90
    if mask.sum() < 10000:
        raise ValueError("Unexpectedly small common brain mask")
    zooms = ref.header.get_zooms()[:3]
    sigma = [FWHM_MM / (2.0 * np.sqrt(2 * np.log(2)) * z) for z in zooms]
    # Smooth within the common support using normalized convolution, avoiding
    # the artificial attenuation caused by smoothing zeros outside the brain.
    Y = np.empty_like(Y0)
    for i, v in enumerate(Y0):
        smoothed = gaussian_filter(v * mask, sigma=sigma, mode="constant")
        weight = gaussian_filter(mask.astype(np.float32), sigma=sigma, mode="constant")
        Y[i] = np.divide(smoothed, weight, out=np.zeros_like(smoothed), where=weight > 1e-5)
    vox = np.flatnonzero(mask.ravel())
    X = Y.reshape(len(Y), -1)[:, vox].astype(np.float64)
    n, p = X.shape
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    # Constant voxels carry no estimable t statistic. Drop them from the
    # inferential family, and standardize each remaining voxel to unit sample
    # SD before permutations. Studentized t is scale invariant; normalization
    # avoids catastrophic cancellation for estimates close to zero.
    variable = np.isfinite(sd) & (sd > 0)
    n_constant = int((~variable).sum())
    X = X[:, variable]
    vox = vox[variable]
    p = X.shape[1]
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = stats.t.sf(t_obs, df=n - 1)

    # One-sided, one-sample sign-flip permutation with the maximum positive t
    # across the full common-support brain on each permutation (FWER control).
    # The sign-flip null is exact under exchangeability/symmetry of participant
    # errors around zero; use a Monte Carlo sample of 5,000 transformations.
    rng = np.random.default_rng(SEED)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n))
    X_perm = X / sd
    sumsq = np.sum(X_perm * X_perm, axis=0)
    max_t = np.empty(N_PERM, dtype=np.float64)
    with threadpool_limits(limits=6):
        for start in range(0, N_PERM, 100):
            stop = min(start + 100, N_PERM)
            s = signs[start:stop]
            sums = s @ X_perm
            variances = np.maximum((sumsq[None, :] - sums * sums / n) / (n - 1), 0)
            ts = (sums / n) / np.sqrt(variances / n)
            max_t[start:stop] = np.max(ts, axis=1)
    p_fwe = (1 + (max_t[:, None] >= t_obs[None, :]).sum(axis=0)) / (N_PERM + 1)
    sig = p_fwe <= ALPHA

    # A transparent, prespecified anatomical search space for descriptive
    # localization: medial prefrontal voxels x +/-20, y 25..55, z -20..15 mm.
    # It is an approximate operational mask for ventral mPFC/rostral ACC and
    # does not restrict the primary whole-brain multiple-comparison family.
    ijk = np.array(np.unravel_index(vox, mask.shape)).T
    xyz = nib.affines.apply_affine(ref.affine, ijk)
    vm_roi = (np.abs(xyz[:, 0]) <= 20) & (xyz[:, 1] >= 25) & (xyz[:, 1] <= 55) & (xyz[:, 2] >= -20) & (xyz[:, 2] <= 15)
    if not vm_roi.any():
        raise ValueError("No voxels in stated vmPFC operationalization")
    roi_subject = X[:, vm_roi].mean(axis=1)
    roi_mean = float(roi_subject.mean())
    roi_sd = float(roi_subject.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    ci = stats.t.interval(0.95, df=n - 1, loc=roi_mean, scale=roi_se)
    roi_t, roi_p_two = stats.ttest_1samp(roi_subject, 0)
    roi_p_one = float(stats.t.sf(roi_t, n - 1))

    # Save maps back into the exact supplied grid.
    def save_map(values, name):
        full = np.zeros(mask.size, dtype=np.float32)
        full[vox] = values.astype(np.float32)
        img = nib.Nifti1Image(full.reshape(mask.shape), ref.affine, ref.header)
        img.set_data_dtype(np.float32)
        nib.save(img, MAPS / name)

    save_map(t_obs, "gain_group_t.nii.gz")
    save_map(p_unc, "gain_p_uncorrected.nii.gz")
    save_map(p_fwe, "gain_p_fwe_maxT.nii.gz")
    save_map(np.where(sig, t_obs, 0), "gain_t_fwe05.nii.gz")
    save_map(np.ones(p, dtype=np.float32), "analysis_mask_90pct_support.nii.gz")

    peak_index = int(np.argmax(t_obs))
    peak_xyz = xyz[peak_index].tolist()
    peak = {
        "t": float(t_obs[peak_index]),
        "p_uncorrected_one_sided": float(p_unc[peak_index]),
        "p_fwe_maxT_one_sided": float(p_fwe[peak_index]),
        "mni_xyz_mm": [round(v, 2) for v in peak_xyz],
        "in_vmPFC_operational_mask": bool(vm_roi[peak_index]),
    }
    result = {
        "n": n,
        "excluded": [],
        "maps_verified_sha256": len(qc),
        "dimensions": list(ref.shape),
        "voxel_sizes_mm": [float(x) for x in zooms],
        "analysis_mask_voxels": int(p),
        "constant_voxels_excluded_from_t_test": n_constant,
        "analysis_mask_coverage_threshold": 0.90,
        "smoothing_fwhm_mm": FWHM_MM,
        "test": "one-sample t; one-sided positive; sign-flip max-statistic whole-brain FWER",
        "permutations": N_PERM,
        "permutation_seed": SEED,
        "alpha_fwe": ALPHA,
        "maxT_null_median": float(np.median(max_t)),
        "maxT_null_95th_percentile": float(np.quantile(max_t, 0.95)),
        "whole_brain_significant_voxels": int(sig.sum()),
        "whole_brain_max_t": peak,
        "vmPFC_mask_definition": "|x|<=20, 25<=y<=55, -20<=z<=15 mm MNI; descriptive, approximate ventral medial PFC/rostral ACC box",
        "vmPFC_voxels": int(vm_roi.sum()),
        "vmPFC_mean_smoothed_cope": roi_mean,
        "vmPFC_mean_95pct_t_CI": [float(ci[0]), float(ci[1])],
        "vmPFC_roi_t": float(roi_t),
        "vmPFC_roi_p_one_sided_unadjusted": roi_p_one,
        "vmPFC_roi_p_two_sided_unadjusted": float(roi_p_two),
        "vmPFC_significant_voxels_fwe05": int((sig & vm_roi).sum()),
        "group_mean_cope_whole_brain_median": float(np.median(mean)),
        "participant_map_qc": {
            "mean_nonzero_voxels": float(np.mean([q["nonzero_voxels"] for q in qc])),
            "sd_nonzero_voxels": float(np.std([q["nonzero_voxels"] for q in qc], ddof=1)),
            "median_voxelwise_sd_in_mask": float(np.median(sd)),
            "max_absolute_studentized_residual_at_voxel": float(np.max(np.abs((X - mean) / np.maximum(sd, 1e-8)), axis=0).max()),
        },
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    pd.DataFrame(qc).to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)
    pd.DataFrame({"participant_id": participants.participant_id, "vmPFC_mean_cope": roi_subject}).to_csv(
        OUT / "vmPFC_participant_estimates.tsv", sep="\t", index=False
    )
    np.savetxt(OUT / "maxT_null_distribution.tsv", max_t, fmt="%.7g", header="max_positive_t")

    # Visualization: whole-brain unthresholded t map with significant voxels
    # highlighted; transformed arrays retain their NIfTI affine for labels.
    t_img = nib.Nifti1Image(np.zeros(mask.shape, np.float32), ref.affine)
    tvol = np.zeros(mask.size, np.float32); tvol[vox] = t_obs
    t_img = nib.Nifti1Image(tvol.reshape(mask.shape), ref.affine)
    sigvol = np.zeros(mask.size, np.float32); sigvol[vox] = sig.astype(np.float32)
    sig_img = nib.Nifti1Image(sigvol.reshape(mask.shape), ref.affine)
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.2))
    vmax = max(3, float(np.percentile(np.abs(t_obs), 99.9)))
    for ax, mode, coord, title in zip(
        axes, ["x", "z", "y"], [-26, -4, 40],
        ["Sagittal (x=-26)", "Axial (z=-4)", "Coronal (y=40)"],
    ):
        from nilearn.plotting import plot_stat_map
        display = plot_stat_map(t_img, bg_img=None, display_mode=mode,
                                cut_coords=[coord], threshold=None, colorbar=False, cmap="RdBu_r",
                                symmetric_cbar=True, vmax=vmax,
                                axes=ax, annotate=False, black_bg=False)
        if sig.any():
            display.add_contours(sig_img, levels=[0.5], colors=["#ffd400"], linewidths=1.7)
        display.close()
        ax.set_title(title, fontsize=10, color="black", pad=8)
    sup = "Gain-effect group t map"
    if sig.any():
        sup += "; yellow outlines mark whole-brain max-T FWER p ≤ .05"
    else:
        sup += "; no voxels pass whole-brain max-T FWER p ≤ .05"
    fig.suptitle(sup, fontsize=11)
    scalar = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=-vmax, vmax=vmax), cmap="RdBu_r")
    fig.subplots_adjust(top=0.82, bottom=0.05, wspace=0.18, right=0.90)
    cax = fig.add_axes([0.93, 0.22, 0.018, 0.56])
    fig.colorbar(scalar, cax=cax, label="Group t statistic")
    fig.savefig(FIG / "whole_brain_gain_effect.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.3, 4.5))
    rng_plot = np.random.default_rng(SEED + 1)
    ax.scatter(rng_plot.normal(0, 0.035, n), roi_subject, color="#315b74", alpha=.78, s=30, edgecolor="white", linewidth=.3)
    ax.errorbar(0, roi_mean, yerr=[[roi_mean-ci[0]], [ci[1]-roi_mean]], color="#b34b31", capsize=5, linewidth=2.2, marker="D", markersize=6)
    ax.axhline(0, color="black", linewidth=.8, linestyle="--")
    ax.set(xlim=(-.18, .18), xticks=[], ylabel="Mean gain-effect estimate in vmPFC box (arbitrary model units)",
           title=f"vmPFC descriptive summary (n={n}); mean {roi_mean:.3f}, 95% CI [{ci[0]:.3f}, {ci[1]:.3f}]")
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "vmPFC_estimates.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
