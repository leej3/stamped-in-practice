#!/usr/bin/env python3
"""Group-level NARPS Hypothesis 1 analysis from supplied AO86 participant maps."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets, image, plotting
from nilearn.glm.second_level import non_parametric_inference
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
DATA = INPUT / "data"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
SEED = 20261016
N_PERM = 10_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-permutation", action="store_true",
                        help="reuse the saved max-t map and regenerate summaries/figures without rerunning permutations")
    args = parser.parse_args()
    meta = json.loads((INPUT / "sources.json").read_text())
    cohort = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    cohort = cohort.loc[cohort.group.eq("equalIndifference")].copy()
    cohort = cohort.sort_values("participant_id").reset_index(drop=True)
    assert len(cohort) == 54, f"Expected 54 participants, found {len(cohort)}"
    if cohort.participant_id.duplicated().any():
        raise ValueError("Duplicate participant IDs in metadata")

    records = []
    images = []
    reference = None
    for row in cohort.itertuples(index=False):
        path = DATA / f"{row.participant_id}_hypo1_cope.nii.gz"
        expected = meta["files"][f"data/{path.name}"]
        digest = sha256(path)
        if digest != expected["sha256"]:
            raise ValueError(f"Checksum mismatch for {path.name}")
        img = nib.load(str(path))
        if reference is None:
            reference = img
        if img.shape != reference.shape or not np.allclose(img.affine, reference.affine):
            raise ValueError(f"Grid mismatch for {path.name}")
        data = img.get_fdata(dtype=np.float32)
        if not np.isfinite(data).all():
            raise ValueError(f"Non-finite values in {path.name}")
        images.append(img)
        records.append({
            "participant_id": row.participant_id,
            "age": row.age,
            "gender": row.gender,
            "sha256_ok": True,
            "n_nonzero_voxels": int(np.count_nonzero(data)),
            "global_mean": float(np.mean(data)),
            "global_sd": float(np.std(data, ddof=1)),
            "global_min": float(np.min(data)),
            "global_max": float(np.max(data)),
        })

    # Nonzero support is the only spatial coverage indicator supplied with these
    # maps. Intersect its shared support with a standard anatomical brain mask to
    # avoid treating an absent edge voxel as zero or searching nonbrain voxels.
    stack = np.stack([im.get_fdata(dtype=np.float32) for im in images])
    common_support = np.all(stack != 0, axis=0)
    standard_mask = datasets.load_mni152_brain_mask(resolution=2, threshold=0.2)
    standard_mask = image.resample_to_img(standard_mask, images[0], interpolation="nearest")
    mask = common_support & (standard_mask.get_fdata() > 0)
    n_vox = int(mask.sum())
    if n_vox == 0:
        raise ValueError("Empty common-support mask")
    flat = stack[:, mask]
    n = len(images)
    mean = flat.mean(axis=0)
    sd = flat.std(axis=0, ddof=1)
    tvals = mean / (sd / np.sqrt(n))
    p_unc = stats.t.sf(tvals, df=n - 1)
    t_img = image.new_img_like(reference, np.zeros(reference.shape, dtype=np.float32))
    mean_img = image.new_img_like(reference, np.zeros(reference.shape, dtype=np.float32))
    t_data = np.zeros(reference.shape, dtype=np.float32)
    mean_data = np.zeros(reference.shape, dtype=np.float32)
    t_data[mask] = tvals
    mean_data[mask] = mean
    t_img = image.new_img_like(reference, t_data)
    mean_img = image.new_img_like(reference, mean_data)
    mask_img = image.new_img_like(reference, mask.astype(np.uint8))

    # Independent anatomical localization: Harvard-Oxford cortical atlas labels
    # covering medial frontal, subcallosal and paracingulate cortex. These
    # prespecified medial territories operationalize vmPFC; this is descriptive
    # and does not replace the required whole-brain corrected test.
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm", verbose=0)
    atlas_img = image.resample_to_img(atlas.maps, reference, interpolation="nearest")
    atlas_data = atlas_img.get_fdata().astype(int)
    roi_atlas_labels = [25, 27, 28]  # Frontal Medial, Subcallosal, Paracingulate
    roi = np.isin(atlas_data, roi_atlas_labels) & mask
    if roi.sum() == 0:
        raise ValueError("vmPFC atlas ROI has no overlap with group mask")
    participant_roi = flat[:, roi[mask]].mean(axis=1)
    roi_mean = participant_roi.mean()
    roi_sd = participant_roi.std(ddof=1)
    roi_se = roi_sd / np.sqrt(n)
    roi_ci = stats.t.interval(0.95, df=n - 1, loc=roi_mean, scale=roi_se)
    roi_t = roi_mean / roi_se
    roi_p = stats.t.sf(roi_t, df=n - 1)
    records_frame = pd.DataFrame(records)
    records_frame["vmPFC_mean_effect"] = participant_roi
    records_frame.to_csv(OUT / "participant_qc_and_roi.csv", index=False)

    # One-sample intercept model; positive direction is the prespecified test.
    # Nilearn returns negative log10 family-wise corrected maximum-t p-values.
    saved_logp = OUT / "group_log10p_fwe_maxT.nii.gz"
    if args.reuse_permutation:
        if not saved_logp.exists():
            raise FileNotFoundError("No saved permutation map to reuse")
        perm_logp = nib.load(str(saved_logp))
    else:
        perm_logp = non_parametric_inference(
            second_level_input=images,
            design_matrix=pd.DataFrame({"intercept": np.ones(n)}),
            second_level_contrast="intercept",
            mask=mask_img,
            n_perm=N_PERM,
            two_sided_test=False,
            random_state=SEED,
            n_jobs=1,
            verbose=1,
        )
    nib.save(t_img, OUT / "group_t_unthresholded.nii.gz")
    nib.save(mean_img, OUT / "group_mean_effect.nii.gz")
    nib.save(perm_logp, OUT / "group_log10p_fwe_maxT.nii.gz")
    logp = perm_logp.get_fdata()
    p_fwe = np.power(10.0, -logp[roi])
    roi_max_logp = float(np.max(logp[roi]))
    roi_min_fwe = float(10 ** (-roi_max_logp))
    significant = (logp >= -np.log10(0.05)) & mask
    sig_n = int(significant.sum())

    # Peak among all positive voxels and among any FWE-significant voxels.
    peak_flat = int(np.argmax(tvals))
    peak_ijk = np.argwhere(mask)[peak_flat]
    peak_xyz = nib.affines.apply_affine(reference.affine, peak_ijk).round(1).tolist()
    peak_atlas = int(atlas_data[tuple(peak_ijk)])
    peak = {"t": float(tvals[peak_flat]), "mean_effect": float(mean[peak_flat]), "mni_xyz_mm": peak_xyz,
            "harvard_oxford_label": atlas.labels[peak_atlas]}
    sig_peak = None
    if sig_n:
        sig_t = np.where(significant, t_data, -np.inf)
        ijk = np.unravel_index(int(np.argmax(sig_t)), sig_t.shape)
        sig_peak = {"t": float(t_data[ijk]), "mean_effect": float(mean_data[ijk]),
                    "mni_xyz_mm": nib.affines.apply_affine(reference.affine, ijk).round(1).tolist(),
                    "p_fwe": float(10 ** (-logp[ijk]))}

    # ROI-only values are reported for estimation; the inferential decision is
    # based on maximum-t whole-brain FWE correction.
    summary = {
        "n_participants": n,
        "n_excluded": 0,
        "exclusions": [],
        "grid_shape": list(reference.shape),
        "voxel_size_mm": [2.0, 2.0, 2.4],
        "common_support_voxels": n_vox,
        "common_support_volume_cm3": float(n_vox * 2 * 2 * 2.4 / 1000),
        "mask_definition": "intersection of all 54 maps' nonzero support and the Nilearn MNI152 2 mm brain mask (nearest-neighbor resampled to map grid)",
        "model": "one-sample intercept t model, positive direction",
        "multiplicity": f"one-sided permutation maximum-t FWE, {N_PERM} permutations, seed {SEED}",
        "whole_brain_fwe_alpha": 0.05,
        "n_voxels_fwe_significant": sig_n,
        "vmPFC_definition": "Harvard-Oxford cortical max-probability atlas labels 25 Frontal Medial, 27 Subcallosal, 28 Paracingulate, intersected with common support",
        "vmPFC_roi_voxels": int(roi.sum()),
        "vmPFC_mean_effect": float(roi_mean),
        "vmPFC_sd_between_participants": float(roi_sd),
        "vmPFC_ci95": [float(roi_ci[0]), float(roi_ci[1])],
        "vmPFC_t_df53": float(roi_t),
        "vmPFC_one_sided_unadjusted_p_descriptive_only": float(roi_p),
        "best_vmPFC_voxel_p_fwe": roi_min_fwe,
        "whole_brain_positive_peak": peak,
        "highest_t_fwe_significant_peak": sig_peak,
        "decision": "supports positive gain-related response" if sig_n and np.any(roi & significant) else "does not support positive gain-related vmPFC response at whole-brain FWE 0.05",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Figure 1: unthresholded group t map with the atlas-defined vmPFC outline.
    fig = plt.figure(figsize=(10, 6))
    display = plotting.plot_stat_map(
        t_img, threshold=2.0, display_mode="ortho", cut_coords=(0, 42, -8),
        cmap="cold_hot", colorbar=True, title="Group mean gain-effect estimate (t map)\nvmPFC defined independently by Harvard-Oxford anatomy",
        figure=fig, black_bg=False,
    )
    display.add_contours(image.new_img_like(reference, roi.astype(np.uint8)), levels=[0.5], colors="cyan", linewidths=1.3)
    display.savefig(FIG / "group_tmap_vmPFC.png", dpi=180)
    plt.close(fig)

    # Figure 2: corrected p-value map. If nothing passes, show the strongest
    # corrected evidence on a continuous scale with the alpha threshold marked.
    p_vis = image.new_img_like(reference, np.where(mask, logp, 0).astype(np.float32))
    fig = plt.figure(figsize=(10, 6))
    display = plotting.plot_stat_map(
        p_vis, threshold=-np.log10(0.05), display_mode="ortho", cut_coords=(-26, -102, -4),
        cmap="inferno", colorbar=True,
        title="One-sided whole-brain maximum-t permutation inference\ncolor scale: -log10(FWE-corrected p); threshold = 1.301",
        figure=fig, black_bg=False,
    )
    display.add_contours(image.new_img_like(reference, roi.astype(np.uint8)), levels=[0.5], colors="cyan", linewidths=1.3)
    display.savefig(FIG / "group_fwe_maxT.png", dpi=180)
    plt.close(fig)

    # Figure 3: subject-level ROI estimates and group confidence interval.
    fig, ax = plt.subplots(figsize=(8, 4.6))
    x = np.arange(1, n + 1)
    ax.scatter(x, participant_roi, s=23, color="#315a7d", alpha=0.8)
    ax.axhline(roi_mean, color="#b33b2e", lw=2, label="Group mean")
    ax.axhspan(*roi_ci, color="#b33b2e", alpha=0.15, label="95% CI for mean")
    ax.axhline(0, color="black", lw=0.8)
    ax.set(xlabel="Participant (sorted by ID)", ylabel="Mean vmPFC gain-effect estimate",
           title="Atlas-defined vmPFC estimates (descriptive; participant cope values)")
    ax.set_xlim(0, n + 1)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "vmPFC_participant_estimates.png", dpi=180)
    plt.close(fig)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
