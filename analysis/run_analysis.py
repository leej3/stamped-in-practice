#!/usr/bin/env python3
"""Group analysis of the supplied NARPS AO86 participant cope images."""
from __future__ import annotations

import hashlib
import json
import os
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
from scipy import stats
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
BASE_OUT = ROOT / "results"
N_PERM = 9999
SEED = 20261016
ALPHA = 0.05
COVERAGE_MIN = float(os.environ.get("NARPS_COVERAGE_MIN", "1.0"))
RUN_LABEL = "primary_100pct" if COVERAGE_MIN == 1.0 else f"sensitivity_{int(COVERAGE_MIN * 100):02d}pct"
OUT = BASE_OUT if RUN_LABEL == "primary_100pct" else BASE_OUT / RUN_LABEL
FIG = ROOT / "figures" if RUN_LABEL == "primary_100pct" else ROOT / "figures" / RUN_LABEL


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    sources = json.loads((INPUT / "sources.json").read_text())
    files = sources["files"]
    if participants.participant_id.duplicated().any():
        raise ValueError("Duplicate participant IDs in cohort metadata")
    declared_ids = {v["participant_id"] for k, v in files.items() if k.startswith("data/")}
    if declared_ids != set(participants.participant_id):
        raise ValueError("Map manifest IDs do not exactly match the cohort table")
    if not (participants.group == "equalIndifference").all():
        raise ValueError("Input participant table includes a participant outside equalIndifference")
    maps = []
    ids = []
    img0 = None
    reasons = []
    for pid in participants.participant_id:
        rel = f"data/{pid}_hypo1_cope.nii.gz"
        p = INPUT / rel
        if rel not in files or not p.exists():
            reasons.append({"participant_id": pid, "reason": "missing map"})
            continue
        metadata = files[rel]
        if metadata["participant_id"] != pid:
            raise ValueError(f"Manifest participant mismatch for {rel}")
        if p.stat().st_size != metadata["bytes"] or sha256(p) != metadata["sha256"]:
            raise ValueError(f"Supplied map size or SHA256 does not match manifest: {rel}")
        img = nib.load(str(p))
        if img0 is None:
            img0 = img
        if img.shape != img0.shape or not np.allclose(img.affine, img0.affine, atol=1e-5):
            reasons.append({"participant_id": pid, "reason": "incompatible geometry"})
            continue
        dat = img.get_fdata(dtype=np.float32)
        if not np.isfinite(dat).all():
            reasons.append({"participant_id": pid, "reason": "nonfinite values"})
            continue
        # Zero outside the individual modeled coverage is treated as unavailable.
        maps.append(dat)
        ids.append(pid)
    if not maps:
        raise RuntimeError("No valid maps")
    data = np.stack(maps)
    n = len(ids)
    coverage = np.count_nonzero(data, axis=0) / n
    mask = coverage >= COVERAGE_MIN
    if mask.sum() < 1000:
        raise RuntimeError(f"Implausibly small common coverage mask: {mask.sum()}")
    X = data[:, mask].astype(np.float64)
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    se = sd / np.sqrt(n)
    t_obs = mean / se
    df = n - 1
    p_unc = stats.t.sf(t_obs, df)

    # Random sign flips are valid under the one-sample null's sign symmetry.
    # Max positive t over the full data-derived common coverage mask controls FWE.
    rng = np.random.default_rng(SEED)
    sumsq = np.sum(X * X, axis=0)
    max_t = np.empty(N_PERM, dtype=np.float32)
    block = 200
    for start in range(0, N_PERM, block):
        stop = min(start + block, N_PERM)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(stop - start, n))
        sums = signs @ X
        # Studentized one-sample statistic; sumsq is invariant under sign flips.
        denom2 = np.maximum((n * sumsq[None, :] - sums * sums) / (n - 1), 0.0)
        t_perm = sums / np.sqrt(denom2)
        max_t[start:stop] = np.max(t_perm, axis=1)
    p_fwe = (1 + np.sum(max_t[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)
    sig = p_fwe <= ALPHA

    # Independent formula check: SciPy's one-sample t statistic at sampled voxels.
    rng_check = np.random.default_rng(68)
    sample_idx = rng_check.choice(X.shape[1], size=min(200, X.shape[1]), replace=False)
    t_scipy = stats.ttest_1samp(X[:, sample_idx], 0.0, axis=0).statistic
    formula_error = float(np.max(np.abs(t_scipy - t_obs[sample_idx])))
    check_signs = rng_check.choice(np.array([-1.0, 1.0]), size=n)
    check_idx = sample_idx[:min(100, len(sample_idx))]
    t_perm_check = (check_signs @ X[:, check_idx]) / np.sqrt(np.maximum(
        (n * np.sum(X[:, check_idx] ** 2, axis=0) - (check_signs @ X[:, check_idx]) ** 2) / (n - 1), 0.0
    ))
    t_perm_scipy = stats.ttest_1samp(X[:, check_idx] * check_signs[:, None], 0.0, axis=0).statistic
    perm_formula_error = float(np.max(np.abs(t_perm_scipy - t_perm_check)))

    # Anatomical annotation is independent of effects: Harvard-Oxford cortical atlas.
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    atlas_img = image.resample_to_img(atlas.maps, img0, interpolation="nearest")
    atlas_data = atlas_img.get_fdata().astype(int)
    labels = list(atlas.labels)
    vm_labels = ["Frontal Medial Cortex", "Subcallosal Cortex", "Frontal Orbital Cortex"]
    vm_ids = [labels.index(label) for label in vm_labels if label in labels]
    roi = np.isin(atlas_data, vm_ids) & mask
    roi_mask = roi[mask]
    roi_coverage = float(roi.sum() / np.isin(atlas_data, vm_ids).sum())
    roi_subject = data[:, roi].mean(axis=1)
    roi_mean = float(roi_subject.mean())
    roi_sd = float(roi_subject.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_ci = stats.t.interval(0.95, n - 1, loc=roi_mean, scale=roi_se)
    roi_t = float(roi_mean / roi_se)
    roi_p_unc = float(stats.t.sf(roi_t, n - 1))
    roi_p_fwe_min = float(p_fwe[roi_mask].min())
    roi_positive_n = int(np.count_nonzero(roi_subject > 0))
    roi_sign_p = float(stats.binomtest(roi_positive_n, n, p=0.5, alternative="greater").pvalue)
    loo_means = (roi_subject.sum() - roi_subject) / (n - 1)

    # Output NIfTI maps retain source geometry; outside the common mask is NaN.
    def save_map(name: str, values: np.ndarray, dtype=np.float32):
        full = np.full(img0.shape, np.nan, dtype=dtype)
        full[mask] = values
        nib.save(nib.Nifti1Image(full, img0.affine, img0.header), OUT / name)

    save_map("group_mean_cope.nii.gz", mean)
    save_map("group_t.nii.gz", t_obs)
    save_map("group_p_uncorrected.nii.gz", p_unc)
    save_map("group_p_fwe_maxT.nii.gz", p_fwe)
    save_map("group_significant_fwe05.nii.gz", sig.astype(np.float32))
    nib.save(nib.Nifti1Image(mask.astype(np.uint8), img0.affine, img0.header), OUT / "analysis_mask.nii.gz")
    nib.save(nib.Nifti1Image(roi.astype(np.uint8), img0.affine, img0.header), OUT / "vmPFC_annotation_mask.nii.gz")

    subj_qc = []
    for i, pid in enumerate(ids):
        a = data[i]
        subj_qc.append({
            "participant_id": pid,
            "mean_nonzero_cope": float(a[a != 0].mean()),
            "sd_nonzero_cope": float(a[a != 0].std(ddof=1)),
            "max_abs_cope": float(np.max(np.abs(a))),
            "nonzero_voxels": int(np.count_nonzero(a)),
            "vmPFC_roi_mean": float(roi_subject[i]),
        })
    pd.DataFrame(subj_qc).to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)
    pd.DataFrame([{"participant_id": r["participant_id"], "exclusion_reason": r["reason"]} for r in reasons], columns=["participant_id", "exclusion_reason"]).to_csv(OUT / "exclusions.tsv", sep="\t", index=False)
    pd.DataFrame({
        "participant_id": ids,
        "vmPFC_mean_cope": roi_subject,
    }).to_csv(OUT / "vmPFC_participant_effects.tsv", sep="\t", index=False)

    max_vox = int(np.argmax(t_obs))
    full_coords = np.argwhere(mask)
    peak_ijk = full_coords[max_vox]
    sig_full = np.zeros(img0.shape, dtype=bool); sig_full[mask] = sig
    labels3d, n_clusters = ndimage.label(sig_full, structure=np.ones((3, 3, 3), dtype=bool))
    clusters = []
    for label_id in range(1, n_clusters + 1):
        coords = np.argwhere(labels3d == label_id)
        c_mask = sig & (labels3d[mask] == label_id)
        peak_coord = full_coords[np.flatnonzero(c_mask)[np.argmax(t_obs[c_mask])]]
        clusters.append({"cluster_id": label_id, "voxels": int(len(coords)), "peak_mni_mm": [float(v) for v in nib.affines.apply_affine(img0.affine, peak_coord)], "peak_t": float(t_obs[c_mask].max()), "min_fwe_p": float(p_fwe[c_mask].min())})
    summary = {
        "question": "Positive group mean gain-effect cope in equal-indifference group",
        "run_label": RUN_LABEL,
        "n_supplied": int(len(participants)), "n_included": n, "n_excluded": reasons,
        "analysis_mask": {"definition": f"nonzero cope coverage in >= {COVERAGE_MIN:.0%} of included participants", "voxels": int(mask.sum()), "voxel_volume_mm3": float(np.prod(img0.header.get_zooms()[:3]))},
        "inference": {"model": "one-sample group mean; participant-level sign flips; max positive t FWE", "alpha": ALPHA, "permutations": N_PERM, "seed": SEED, "p_resolution": 1/(N_PERM+1), "maxT_95_threshold": float(np.quantile(max_t, 0.95, method="higher")), "significant_voxels": int(sig.sum()), "smallest_fwe_p": float(p_fwe.min())},
        "strongest_voxel": {"ijk": [int(v) for v in peak_ijk], "mni_mm": [float(v) for v in nib.affines.apply_affine(img0.affine, peak_ijk)], "mean_cope": float(mean[max_vox]), "t": float(t_obs[max_vox]), "p_uncorrected": float(p_unc[max_vox]), "p_fwe": float(p_fwe[max_vox])},
        "significant_clusters_26_connected": clusters,
        "vmPFC_annotation": {"atlas": "Harvard-Oxford cortical max-probability, threshold 25%, 2 mm", "labels": vm_labels, "voxel_count_within_analysis_mask": int(roi.sum()), "atlas_voxel_coverage": roi_coverage, "mean_participant_roi_cope": roi_mean, "sd_participant_roi_cope": roi_sd, "mean_cope_95pct_t_interval": [float(x) for x in roi_ci], "t_53": roi_t, "one_sided_unadjusted_p": roi_p_unc, "minimum_whole_brain_FWE_p_in_ROI": roi_p_fwe_min, "significant_voxels_in_ROI": int((sig & roi_mask).sum()), "positive_participant_roi_estimates": roi_positive_n, "one_sided_sign_test_p_descriptive": roi_sign_p, "median_participant_roi_cope": float(np.median(roi_subject)), "leave_one_out_mean_range": [float(loo_means.min()), float(loo_means.max())]},
        "cross_check": {"scipy_ttest_1samp_voxels": len(sample_idx), "max_abs_t_difference": formula_error, "permuted_scipy_ttest_voxels": len(check_idx), "permuted_max_abs_t_difference": perm_formula_error},
        "runtime_environment": {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__, "nibabel": nib.__version__, "nilearn": nilearn.__version__, "pandas": pd.__version__},
        "annotation_atlas": {"retrieval": "nilearn.datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')", "cache_file": str(Path(atlas.filename)), "sha256": sha256(Path(atlas.filename))},
        "source_sha256": {"participant_table": sha256(INPUT / "participants.tsv"), "sources_manifest": sha256(INPUT / "sources.json"), "study_task": sha256(INPUT / "study-task.md"), "upstream_methods": sha256(INPUT / "upstream-methods.md")},
        "analysis_code_sha256": sha256(Path(__file__)),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    mni_coords = nib.affines.apply_affine(img0.affine, full_coords)
    voxel_table = pd.DataFrame({
        "i": full_coords[:, 0], "j": full_coords[:, 1], "k": full_coords[:, 2],
        "x_mm": mni_coords[:, 0], "y_mm": mni_coords[:, 1], "z_mm": mni_coords[:, 2],
        "observed_t": t_obs, "mean_cope": mean,
        "p_uncorrected_one_sided": p_unc, "p_fwe_maxT": p_fwe,
    })
    voxel_table.to_csv(OUT / "voxel_statistics.tsv.gz", sep="\t", index=False, compression="gzip")
    pd.DataFrame({"permutation": np.arange(1, N_PERM + 1), "maximum_positive_t": max_t}).to_csv(OUT / "max_t_null.tsv", sep="\t", index=False)

    # Participant-level ROI estimates and whole-brain corrected result are
    # separate panels so each spatial slice remains large enough to inspect.
    fig, ax = plt.subplots(figsize=(7, 4.8), constrained_layout=True)
    ax.scatter(np.arange(1, n + 1), roi_subject, s=19, alpha=.75, color="#25658a")
    ax.axhline(roi_mean, color="#a33d2c", lw=2, label=f"Mean {roi_mean:.3g}")
    ax.axhspan(roi_ci[0], roi_ci[1], color="#a33d2c", alpha=.15, label="95% t interval")
    ax.axhline(0, color="black", lw=.8)
    ax.set(xlabel="Participant", ylabel="Mean vmPFC cope", title="vmPFC participant estimates (n=54)")
    ax.legend(frameon=False, fontsize=9)
    fig.savefig(FIG / "vmPFC_estimates.png", dpi=180)
    plt.close(fig)

    d = np.zeros(img0.shape, dtype=np.float32)
    if sig.any():
        d[mask] = np.where(sig, t_obs, 0)
        spatial_title = "Positive voxels surviving whole-brain max-T FWE (α=.05)"
        threshold = float(np.quantile(max_t, 0.95, method="higher"))
    else:
        d[mask] = t_obs
        spatial_title = "Observed one-sample t; no voxels survive max-T FWE"
        threshold = 2.0
    spatial_img = nib.Nifti1Image(d, img0.affine)
    display = plotting.plot_stat_map(spatial_img, display_mode="z", cut_coords=[-8, -4, 0], threshold=threshold, colorbar=True, title=spatial_title, cmap="magma", symmetric_cbar=False)
    display.savefig(FIG / "whole_brain_fwe.png", dpi=180)
    display.close()
    print(json.dumps({k: summary[k] for k in ["n_supplied", "n_included", "analysis_mask", "inference", "strongest_voxel", "vmPFC_annotation", "cross_check"]}, indent=2))


if __name__ == "__main__":
    main()
