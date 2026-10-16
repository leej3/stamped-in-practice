#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference gain cope maps.

Primary inference is a one-sided, one-sample sign-flip permutation max-t test
across the common participant brain coverage. The atlas ROI is descriptive and
does not replace the required whole-brain corrected test.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from nilearn import datasets, image, plotting
from nilearn.glm.second_level import non_parametric_inference
from nibabel.affines import apply_affine
from scipy import ndimage, stats


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = OUT / "figures"
N_PERM = 10_000
SEED = 20261015
ALPHA = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_img(data: np.ndarray, ref: nib.spatialimages.SpatialImage, path: Path, dtype=None) -> None:
    out = nib.Nifti1Image(data.astype(dtype or np.float32), ref.affine, ref.header.copy())
    out.set_data_dtype(dtype or np.float32)
    nib.save(out, path)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((INPUT / "sources.json").read_text())
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    file_entries = manifest["files"]
    paths = [INPUT / name for name in file_entries if name.endswith(".nii.gz")]
    paths.sort(key=lambda p: p.name)
    ids = [p.name.split("_")[0] for p in paths]

    # Validate the frozen cohort, input identity, and image geometry before inference.
    checks = []
    expected_ids = set(participants.participant_id)
    if len(paths) != 54 or set(ids) != expected_ids or len(set(ids)) != len(ids):
        raise ValueError(f"cohort mismatch: {len(paths)} images; {len(expected_ids)} metadata rows")
    if set(ids) != {file_entries[p.relative_to(INPUT).as_posix()]["participant_id"] for p in paths}:
        raise ValueError("image IDs do not match the source manifest")
    imgs = []
    arrs = []
    ref = None
    for p in paths:
        entry = file_entries[p.relative_to(INPUT).as_posix()]
        digest = sha256(p)
        if p.stat().st_size != entry["bytes"] or digest != entry["sha256"]:
            raise ValueError(f"checksum or byte-count mismatch: {p.name}")
        im = nib.load(p)
        if len(im.shape) != 3:
            raise ValueError(f"not a 3D map: {p.name}, shape={im.shape}")
        if ref is None:
            ref = im
        elif im.shape != ref.shape or not np.allclose(im.affine, ref.affine, atol=1e-5):
            raise ValueError(f"spatial geometry mismatch: {p.name}")
        d = im.get_fdata(dtype=np.float32)
        if not np.isfinite(d).all():
            raise ValueError(f"non-finite values: {p.name}")
        imgs.append(im)
        arrs.append(d)
        checks.append({"participant_id": ids[len(checks)], "file": p.relative_to(INPUT).as_posix(),
                       "bytes": p.stat().st_size, "sha256": digest,
                       "nonzero_voxels": int(np.count_nonzero(d)),
                       "min": float(d.min()), "max": float(d.max()),
                       "mean_nonzero": float(d[d != 0].mean())})

    data = np.stack(arrs, axis=0)
    coverage = np.all(np.isfinite(data) & (data != 0), axis=0)
    n_vox = int(coverage.sum())
    if n_vox < 10_000:
        raise ValueError(f"unexpectedly small common coverage mask: {n_vox} voxels")
    save_img(coverage, ref, OUT / "common_brain_mask.nii.gz", np.uint8)

    # Whole-brain primary test: one-sample intercept, positive direction, sign flips.
    # Nilearn returns -log10 FWE-corrected p-values using the permutation max-t null.
    model = pd.DataFrame({"intercept": np.ones(len(imgs))})
    perm = non_parametric_inference(
        second_level_input=imgs,
        design_matrix=model,
        second_level_contrast="intercept",
        mask=OUT / "common_brain_mask.nii.gz",
        model_intercept=False,
        n_perm=N_PERM,
        two_sided_test=False,
        random_state=SEED,
        n_jobs=max(1, min(8, os.cpu_count() or 1)),
        tfce=False,
        verbose=1,
    )
    # Model uses no implicit intercept because the explicit all-ones column is tested.
    # With tfce=False and threshold=None, Nilearn returns the max-t corrected -log10(p).
    logp_img = perm
    mean_map = np.mean(data, axis=0)
    sd_map = np.std(data, axis=0, ddof=1)
    t_data = np.zeros(ref.shape, dtype=np.float32)
    t_data[coverage] = mean_map[coverage] / (sd_map[coverage] / np.sqrt(len(imgs)))
    t_img = nib.Nifti1Image(t_data, ref.affine, ref.header.copy())
    t_data = t_img.get_fdata(dtype=np.float32)
    logp_data = logp_img.get_fdata(dtype=np.float32)
    p_fwe = np.power(10.0, -logp_data)
    sig = coverage & np.isfinite(p_fwe) & (p_fwe <= ALPHA)

    save_img(np.where(coverage, mean_map, 0), ref, OUT / "mean_gain_cope.nii.gz")
    save_img(np.where(coverage, sd_map, 0), ref, OUT / "sd_gain_cope.nii.gz")
    save_img(t_data, ref, OUT / "one_sample_t.nii.gz")
    save_img(logp_data, ref, OUT / "max_t_log10_fwe_p.nii.gz")
    save_img(sig, ref, OUT / "max_t_fwe_p05_mask.nii.gz", np.uint8)

    # AAL SPM12 bilateral medial orbitofrontal parcels, independent of observed effects.
    # This ROI is a transparent anatomical operationalization of vmPFC; the whole-brain
    # corrected test remains the sole confirmatory criterion.
    atlas = datasets.fetch_atlas_aal(version="SPM12", verbose=0)
    label_names = {"Frontal_Med_Orb_L", "Frontal_Med_Orb_R"}
    label_ids = {int(i) for i, name in zip(atlas.indices, atlas.labels) if name in label_names}
    roi_native = image.resample_to_img(atlas.maps, imgs[0], interpolation="nearest")
    roi_labels = roi_native.get_fdata(dtype=np.float32).astype(int)
    roi = coverage & np.isin(roi_labels, list(label_ids))
    if not roi.any():
        raise ValueError("vmPFC medial-orbitofrontal ROI did not intersect common coverage")
    save_img(roi, ref, OUT / "vmPFC_AAL_medial_orbitofrontal_mask.nii.gz", np.uint8)
    roi_means = data[:, roi].mean(axis=1)
    roi_t = stats.ttest_1samp(roi_means, popmean=0, alternative="greater")
    roi_mean = float(roi_means.mean())
    roi_se = float(stats.sem(roi_means))
    roi_ci = stats.t.interval(0.95, len(roi_means) - 1, loc=roi_mean, scale=roi_se)
    roi_dz = float(roi_mean / roi_means.std(ddof=1))
    component_labels, n_components = ndimage.label(sig, structure=np.ones((3, 3, 3), dtype=np.uint8))
    components = []
    for component_id in range(1, n_components + 1):
        component = component_labels == component_id
        voxels = np.argwhere(component)
        peak_offset = int(np.argmax(t_data[component]))
        peak_ijk = voxels[peak_offset]
        components.append({
            "extent_voxels_descriptive_26_connectivity": int(component.sum()),
            "peak_t": float(t_data[tuple(peak_ijk)]),
            "peak_mni_xyz_mm": [float(v) for v in apply_affine(ref.affine, peak_ijk)],
            "peak_max_t_fwe_p": float(10 ** (-logp_data[tuple(peak_ijk)])),
            "vmPFC_roi_overlap_voxels": int((component & roi).sum()),
        })
    components.sort(key=lambda item: item["peak_t"], reverse=True)
    roi_summary = {
        "roi": "AAL SPM12 bilateral Frontal_Med_Orb_L/R",
        "roi_atlas_label_ids": sorted(label_ids),
        "roi_voxels_in_common_mask": int(roi.sum()),
        "mean_cope": roi_mean,
        "sd_participant_roi_means": float(roi_means.std(ddof=1)),
        "se": roi_se,
        "ci95_t": [float(x) for x in roi_ci],
        "cohen_dz": roi_dz,
        "one_sided_t": float(roi_t.statistic),
        "one_sided_p_uncorrected_descriptive": float(roi_t.pvalue),
        "n": len(roi_means),
    }
    pd.DataFrame({"participant_id": ids, "roi_mean_cope": roi_means}).to_csv(
        OUT / "vmPFC_participant_effects.tsv", sep="\t", index=False
    )
    pd.DataFrame(checks).to_csv(OUT / "input_qc.tsv", sep="\t", index=False)

    max_t = float(np.nanmax(t_data[coverage]))
    max_logp = float(np.nanmax(logp_data[coverage]))
    result = {
        "analysis": "AO86 equal-indifference group gain cope, one-sided positive whole-brain max-t sign-flip test",
        "n": len(imgs), "n_excluded": 0, "n_permutations": N_PERM,
        "seed": SEED, "alpha_fwe": ALPHA,
        "common_mask_voxels": n_vox,
        "voxel_size_mm": [float(abs(x)) for x in ref.header.get_zooms()[:3]],
        "max_t_in_mask": max_t,
        "max_t_log10_fwe_p": max_logp,
        "max_t_fwe_p": float(10 ** (-max_logp)),
        "significant_voxels_fwe_p_le_0_05": int(sig.sum()),
        "significant_components_descriptive_only": components,
        "vmPFC_descriptive_summary": roi_summary,
        "data_interpretation": "participant-level cope estimates from a mean-centered, variance-normalized gain modulator; not currency-unit slopes or standardized test statistics",
        "group_model_limit": "no first-level variance maps are supplied; unweighted one-sample group inference cannot reproduce precision-weighted mixed-effects estimation",
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                     "nilearn": __import__("nilearn").__version__, "nibabel": nib.__version__,
                     "platform": platform.platform()},
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")

    # Group effect figure: cope estimates in atlas-scaled ROI and whole-brain inference.
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2), constrained_layout=True)
    axes[0].hist(roi_means, bins=12, color="#557a95", edgecolor="white")
    axes[0].axvline(0, color="#555555", lw=1, ls="--")
    axes[0].axvline(roi_mean, color="#b13c31", lw=2)
    axes[0].set(xlabel="Participant mean cope in bilateral medial OFC ROI",
                ylabel="Participants", title="vmPFC operationalization")
    axes[0].text(0.03, 0.97,
                 f"n = {len(roi_means)}\nmean = {roi_mean:.3g}\n95% CI [{roi_ci[0]:.3g}, {roi_ci[1]:.3g}]",
                 va="top", ha="left", transform=axes[0].transAxes, fontsize=9)
    axes[1].axis("off")
    axes[1].text(0.02, 0.96,
                 "Whole-brain positive-direction max-t permutation test\n\n"
                 f"{N_PERM:,} sign flips; family-wise α = .05\n"
                 f"Common mask: {n_vox:,} voxels\n"
                 f"FWE-significant voxels: {int(sig.sum()):,}\n"
                 f"vmPFC ROI overlap: {int((sig & roi).sum()):,} voxels\n"
                 f"Strongest corrected p: {10**(-max_logp):.4g}\n\n"
                 "Corrected p-values control error across the full mask.",
                 va="top", ha="left", transform=axes[1].transAxes, fontsize=11,
                 bbox={"boxstyle": "round,pad=0.6", "facecolor": "#f3f4f5", "edgecolor": "#d5d8dc"})
    fig.suptitle("Potential gain effect: group analysis", fontsize=14)
    fig.savefig(FIG / "gain_group_inference.png", dpi=220)
    plt.close(fig)

    # Show the unthresholded group effect and the whole-brain corrected result at vmPFC slices.
    template = datasets.load_mni152_template(resolution=2)
    display = plotting.plot_stat_map(
        t_img, bg_img=template, threshold=stats.t.ppf(0.95, len(imgs)-1),
        display_mode="ortho", cut_coords=(0, 45, -10),
        title=None,
        colorbar=True, black_bg=False,
    )
    display.title("vmPFC group t map (uncorrected display threshold)", y=0.95, size=13)
    display.add_contours(OUT / "vmPFC_AAL_medial_orbitofrontal_mask.nii.gz", colors=["cyan"], linewidths=1.2)
    display.add_contours(OUT / "max_t_fwe_p05_mask.nii.gz", colors=["magenta"], linewidths=1.5)
    display.savefig(FIG / "gain_tmap_vmPFC.png", dpi=220)
    display.close()

    corrected_t = np.where(sig, t_data, 0)
    corrected_img = nib.Nifti1Image(corrected_t, ref.affine, ref.header.copy())
    corrected_display = plotting.plot_stat_map(
        corrected_img, bg_img=template, threshold=0,
        display_mode="ortho", cut_coords=(-26, -100, -4),
        title=None,
        colorbar=True, black_bg=False,
    )
    corrected_display.title("Positive t values surviving whole-brain max-t FWE", y=0.95, size=13)
    corrected_display.savefig(FIG / "gain_fwe_significant_map.png", dpi=220)
    corrected_display.close()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
