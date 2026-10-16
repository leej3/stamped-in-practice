#!/usr/bin/env python3
"""Group analysis of NARPS AO86 gain effect maps (fixed input maps only)."""
from __future__ import annotations

import hashlib
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from scipy import ndimage
from nilearn import datasets, plotting, image


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = OUT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
ALPHA = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    sources = json.loads((INPUT / "sources.json").read_text())
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    expected = participants.loc[participants.group.eq("equalIndifference"), "participant_id"].tolist()
    if len(expected) != 54 or participants.shape[0] != 54:
        raise ValueError(f"Expected 54 equalIndifference participants; found {len(expected)}")

    # Fixed-input integrity and alignment checks.
    rows, arrays, headers = [], [], []
    for sub in expected:
        rel = f"data/{sub}_hypo1_cope.nii.gz"
        path = INPUT / rel
        record = sources["files"][rel]
        if not path.exists():
            raise FileNotFoundError(path)
        actual_sha = sha256(path)
        if path.stat().st_size != record["bytes"] or actual_sha != record["sha256"]:
            raise ValueError(f"Input integrity mismatch: {rel}")
        img = nib.load(path)
        arr = img.get_fdata(dtype=np.float32)
        if arrays and (img.shape != headers[0].shape or not np.allclose(img.affine, headers[0].affine)):
            raise ValueError(f"Spatial grid mismatch: {rel}")
        if not np.isfinite(arr).all():
            raise ValueError(f"Nonfinite values in {rel}")
        arrays.append(arr)
        headers.append(img)
        rows.append({"participant_id": sub, "age": int(participants.set_index("participant_id").loc[sub, "age"]),
                     "gender": participants.set_index("participant_id").loc[sub, "gender"],
                     "sha256_verified": True, "nonzero_voxels": int(np.count_nonzero(arr)),
                     "map_mean_nonzero": float(arr[arr != 0].mean()),
                     "map_sd_nonzero": float(arr[arr != 0].std())})
    qc = pd.DataFrame(rows)
    qc.to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)

    # Restrict inference to the intersection of participant analysis supports.
    # Exact zeros are the outside-brain/background convention in these maps.
    data = np.stack(arrays, axis=0)
    mask = np.all(data != 0, axis=0)
    n_vox = int(mask.sum())
    if n_vox == 0:
        raise ValueError("Empty common nonzero mask")
    x = data[:, mask].astype(np.float64)
    n = x.shape[0]

    # Positive one-sample t: group mean of contrast parameter estimates > 0.
    means = x.mean(axis=0)
    sd = x.std(axis=0, ddof=1)
    tvals = means / (sd / np.sqrt(n))
    p_unc = stats.t.sf(tvals, df=n - 1)
    p_fwe = np.minimum(p_unc * n_vox, 1.0)
    p_fdr = stats.false_discovery_control(p_unc, method="bh")
    fdr_reject = p_fdr <= ALPHA
    max_idx = int(np.argmax(tvals))
    max_t = float(tvals[max_idx])
    max_p_fwe = float(p_fwe[max_idx])
    whole_sig = p_fwe <= ALPHA

    def make_img(vals, name="map"):
        out = np.zeros(headers[0].shape, dtype=np.float32)
        out[mask] = vals.astype(np.float32)
        return nib.Nifti1Image(out, headers[0].affine, headers[0].header)

    mean_img = make_img(means)
    t_img = make_img(tvals)
    p_img = make_img(p_fwe)
    sig_img = make_img(np.where(whole_sig, tvals, 0))
    nib.save(mean_img, OUT / "group_mean_effect.nii.gz")
    nib.save(t_img, OUT / "group_t_positive.nii.gz")
    nib.save(p_img, OUT / "group_p_fwe_bonferroni.nii.gz")
    nib.save(sig_img, OUT / "group_t_positive_fwe05.nii.gz")

    # Independent anatomical operationalization of vmPFC: Harvard-Oxford
    # cortical labels for Frontal Medial, Subcallosal, and Frontal Orbital Cortex.
    # The atlas is a reference label map only; all inferential familywise control
    # remains across the entire group analysis mask.
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    atlas_img = image.resample_to_img(atlas.maps, headers[0], interpolation="nearest")
    atlas_data = atlas_img.get_fdata().astype(int)
    labels = list(atlas.labels)
    wanted = ["Frontal Medial Cortex", "Subcallosal Cortex", "Frontal Orbital Cortex"]
    # Labels are selected before inspecting the group results. These medial and
    # orbital parcels form a broad anatomical proxy, not a uniquely defined vmPFC.
    selected = [i for i, lab in enumerate(labels) if lab in wanted]
    if not selected:
        raise ValueError(f"Could not find vmPFC proxy labels: {wanted}; available={labels}")
    roi = np.isin(atlas_data, selected) & mask
    if not roi.any():
        raise ValueError("vmPFC anatomical proxy does not overlap common analysis support")
    roi_betas = data[:, roi].mean(axis=1)
    roi_mean = float(roi_betas.mean())
    roi_sd = float(roi_betas.std(ddof=1))
    roi_sem = roi_sd / np.sqrt(n)
    roi_ci = stats.t.interval(0.95, df=n-1, loc=roi_mean, scale=roi_sem)
    roi_t, roi_p = stats.ttest_1samp(roi_betas, popmean=0, alternative="greater")
    roi_rows = pd.DataFrame({"participant_id": expected, "vmPFC_proxy_mean_effect": roi_betas})
    roi_rows.to_csv(OUT / "vmPFC_proxy_participant_effects.tsv", sep="\t", index=False)

    # Summarize support and distribution checks without excluding participants.
    grid = {"shape": list(headers[0].shape), "affine": headers[0].affine.tolist(),
            "voxel_size_mm": list(nib.affines.voxel_sizes(headers[0].affine))}
    # Report every suprathreshold cluster and its MNI peak, even when outside ROI.
    whole_sig_grid = np.zeros(headers[0].shape, dtype=bool)
    whole_sig_grid[mask] = whole_sig
    labeled, n_clusters = ndimage.label(whole_sig_grid, structure=np.ones((3, 3, 3), dtype=bool))
    cluster_rows = []
    for c in range(1, n_clusters + 1):
        ijk = np.argwhere(labeled == c)
        cluster_t = np.array([t_img.get_fdata()[tuple(v)] for v in ijk])
        peak_ijk = ijk[int(cluster_t.argmax())]
        peak_xyz = nib.affines.apply_affine(headers[0].affine, peak_ijk).round(1)
        peak_label = labels[atlas_data[tuple(peak_ijk)]] if atlas_data[tuple(peak_ijk)] < len(labels) else "Unknown"
        cluster_rows.append({"cluster": c, "voxels": len(ijk), "peak_t": float(cluster_t.max()),
                             "peak_x_mm": peak_xyz[0], "peak_y_mm": peak_xyz[1], "peak_z_mm": peak_xyz[2],
                             "peak_HO_label": peak_label,
                             "overlaps_vmPFC_proxy": bool(np.any(roi[tuple(ijk.T)]))})
    pd.DataFrame(cluster_rows).to_csv(OUT / "whole_brain_fwe_clusters.tsv", sep="\t", index=False)
    results = {
        "n_participants": n, "n_excluded": 0, "analysis_mask": "intersection of nonzero participant support",
        "n_analysis_voxels": n_vox, "grid": grid, "direction": "positive (one-sided)",
        "group_model": "one-sample voxelwise t test across participant contrast estimates",
        "degrees_of_freedom": n - 1, "whole_brain_correction": "Bonferroni over all common-support voxels",
        "alpha": ALPHA, "max_positive_t": max_t, "max_t_uncorrected_p_one_sided": float(p_unc[max_idx]),
        "max_t_fwe_p": max_p_fwe, "n_voxels_fwe_significant": int(whole_sig.sum()),
        "n_voxels_fdr_significant_supplementary": int(fdr_reject.sum()),
        "vmPFC_roi_definition": {"atlas": "Harvard-Oxford cortical atlas, max-probability threshold 25%",
                                 "labels": [labels[i] for i in selected], "n_voxels": int(roi.sum()),
                                 "interpretation": "broad anatomical vmPFC proxy, not a uniquely canonical parcel"},
        "vmPFC_proxy_mean_effect": roi_mean, "vmPFC_proxy_sd_between_participants": roi_sd,
        "vmPFC_proxy_95ci": [float(roi_ci[0]), float(roi_ci[1])], "vmPFC_proxy_t": float(roi_t),
        "vmPFC_proxy_p_one_sided_unadjusted_secondary": float(roi_p),
        "roi_positive_voxels_fwe_significant": int(np.sum(whole_sig & roi[mask])),
        "n_fwe_clusters_26_connected": n_clusters,
        "qc": {"all_checksums_match": True, "all_maps_finite": True, "same_grid": True,
               "map_nonzero_voxels_min": int(qc.nonzero_voxels.min()), "map_nonzero_voxels_max": int(qc.nonzero_voxels.max()),
               "max_abs_standardized_roi_outlier": float(np.max(np.abs(stats.zscore(roi_betas, ddof=1))))}
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    pd.DataFrame([{"voxelwise_p": "one-sided t(53)", "mask_voxels": n_vox,
                   "bonferroni_alpha_uncorrected": ALPHA / n_vox,
                   "max_positive_t": max_t, "max_t_fwe_p": max_p_fwe,
                   "fwe_sig_voxels": int(whole_sig.sum()), "fdr_sig_voxels_supplementary": int(fdr_reject.sum())}]
                 ).to_csv(OUT / "whole_brain_summary.tsv", sep="\t", index=False)

    # Figure 1: participant-level ROI estimates; no participant is excluded.
    fig, ax = plt.subplots(figsize=(5.6, 4.8))
    ax.axhline(0, color="0.35", lw=1)
    ax.scatter(np.ones(n) + np.random.default_rng(17).normal(0, .045, n), roi_betas,
                   s=22, alpha=.72, color="#2878B5", edgecolor="white", linewidth=.3)
    ax.errorbar(1.18, roi_mean, yerr=[[roi_mean-roi_ci[0]], [roi_ci[1]-roi_mean]],
                    fmt="D", color="#B33B32", capsize=4, markersize=6, label="Mean and 95% CI")
    ax.set_xlim(.75, 1.4); ax.set_xticks([1], ["vmPFC proxy"])
    ax.set_ylabel("Mean gain-effect estimate (arbitrary model units)")
    ax.set_title("Participant-level vmPFC proxy summaries")
    ax.legend(frameon=False, loc="best", fontsize=8)
    ax.text(.03, .98, f"n={n}; ROI-only one-sided p={roi_p:.3g}\n(not whole-brain corrected)",
            transform=ax.transAxes, va="top", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "vmPFC_proxy_participant_effects.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: unthresholded whole-brain map and preregistered anatomical proxy.
    disp = plotting.plot_stat_map(t_img, bg_img=datasets.load_mni152_template(resolution=2),
                                  threshold=None, display_mode="z", cut_coords=[-12, 0, 12, 24, 36],
                                  cmap="RdBu_r", colorbar=True, vmin=-5, vmax=5,
                                  title="Unthresholded signed group t map (black: vmPFC proxy)")
    # Plot selected atlas ROI contours as a visual guide.
    disp.add_contours(nib.Nifti1Image(roi.astype(np.uint8), headers[0].affine), levels=[.5],
                      colors="black", linewidths=1)
    disp.savefig(FIG / "group_t_unthresholded_with_vmPFC.png", dpi=180)
    disp.close()

    # Figure 3: voxels passing the positive whole-brain FWE threshold.
    d = plotting.plot_stat_map(sig_img, bg_img=datasets.load_mni152_template(resolution=2),
                               threshold=.001, display_mode="ortho", cut_coords=(0, 40, -5),
                               cmap="Reds", colorbar=True,
                               title="Positive group effects surviving voxelwise Bonferroni FWE (α=.05)")
    d.savefig(FIG / "positive_fwe_thresholded.png", dpi=180)
    d.close()

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning)
    main()
