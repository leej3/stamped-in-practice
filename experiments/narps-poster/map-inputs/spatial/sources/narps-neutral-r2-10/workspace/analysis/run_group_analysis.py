#!/usr/bin/env python3
"""Reproducible group analysis for NARPS AO86 equal-indifference gain maps."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from nilearn import datasets, image as nimg, plotting

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
SEED = 20261016
ROI_CENTER = np.array([2.0, 46.0, -8.0])  # MNI focus reported for positive vmPFC value effects
ROI_RADIUS_MM = 10.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_nii(data: np.ndarray, ref: nib.Nifti1Image, path: Path) -> None:
    img = nib.Nifti1Image(data.astype(np.float32), ref.affine, ref.header.copy())
    nib.save(img, path)


def main() -> None:
    source = json.loads((INPUT / "sources.json").read_text())
    cohort = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    files = source["files"]
    ids = cohort.participant_id.tolist()
    image_files = {k: v for k, v in files.items() if k.startswith("data/")}
    assert len(ids) == 54 and len(image_files) == 54
    assert cohort.group.eq("equalIndifference").all()
    assert set(ids) == {v["participant_id"] for v in image_files.values()}

    paths = [ROOT / "input" / "data" / f"{pid}_hypo1_cope.nii.gz" for pid in ids]
    images = [nib.load(str(p)) for p in paths]
    ref = images[0]
    shape = ref.shape
    affine = ref.affine
    qc_rows, arrays, supports = [], [], []
    for pid, p, im in zip(ids, paths, images):
        arr = im.get_fdata(dtype=np.float32)
        assert im.shape == shape and np.allclose(im.affine, affine, atol=1e-4)
        assert np.isfinite(arr).all()
        meta = image_files[f"data/{p.name}"]
        file_hash = sha256(p)
        assert p.stat().st_size == meta["bytes"] and file_hash == meta["sha256"]
        supports.append(arr != 0)
        arrays.append(arr)
        qc_rows.append({"participant_id": pid, "bytes": p.stat().st_size, "sha256_ok": True,
                        "nonzero_voxels": int(np.count_nonzero(arr)), "mean_nonzero": float(arr[arr != 0].mean()),
                        "sd_nonzero": float(arr[arr != 0].std()), "max_abs": float(np.abs(arr).max())})
    arrs = np.stack(arrays, axis=0)
    # Use a standard whole-brain mask resampled to the provided MNI152NLin2009cAsym
    # grid, intersected with all maps' nonzero support. This excludes numerical edge
    # voxels while avoiding zeros outside common first-level coverage.
    support_mask = np.logical_and.reduce(supports)
    standard_mask = datasets.load_mni152_brain_mask(resolution=2)
    standard_mask = nimg.resample_to_img(standard_mask, ref, interpolation="nearest")
    mask = support_mask & (standard_mask.get_fdata() > 0)
    n, nvox = arrs.shape[0], int(mask.sum())
    Y = arrs[:, mask].astype(np.float64)
    means = Y.mean(axis=0)
    sd = Y.std(axis=0, ddof=1)
    tmap = means / (sd / math.sqrt(n))
    dof = n - 1
    p_unc = stats.t.sf(tmap, dof)
    peak_idx = int(np.argmax(tmap))

    # Whole-brain family-wise error correction by Bonferroni across every voxel in
    # the common brain mask. It is conservative but valid under the t-model even when
    # spatial dependence is present.
    p_bonf = np.minimum(1.0, p_unc * nvox)

    # Map the ROI from an independent published meta-analytic vmPFC focus; the 10 mm
    # sphere is specified before inspecting these data and is descriptive secondary evidence.
    ijk = nib.affines.apply_affine(np.linalg.inv(affine), ROI_CENTER)
    ii, jj, kk = np.indices(shape)
    xyz = nib.affines.apply_affine(affine, np.column_stack((ii.ravel(), jj.ravel(), kk.ravel())))
    roi_all = np.linalg.norm(xyz - ROI_CENTER, axis=1).reshape(shape) <= ROI_RADIUS_MM
    roi = mask & roi_all
    roi_nvox = int(roi.sum())
    roi_values = arrs[:, roi].mean(axis=1)
    roi_mean = float(roi_values.mean())
    roi_sd = float(roi_values.std(ddof=1))
    roi_sem = roi_sd / math.sqrt(n)
    roi_t = roi_mean / roi_sem
    roi_p = float(stats.t.sf(roi_t, dof))
    ci = stats.t.interval(0.95, dof, loc=roi_mean, scale=roi_sem)
    wilcoxon = stats.wilcoxon(roi_values, alternative="greater", zero_method="wilcox", method="approx")

    # Save summary tables and maps.
    pd.DataFrame(qc_rows).to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)
    pd.DataFrame({"participant_id": ids, "vmPFC_mean_effect": roi_values}).to_csv(OUT / "vmPFC_participant_values.tsv", sep="\t", index=False)
    full_t = np.zeros(shape, dtype=np.float32); full_t[mask] = tmap
    full_p = np.ones(shape, dtype=np.float32); full_p[mask] = p_bonf
    full_mean = np.zeros(shape, dtype=np.float32); full_mean[mask] = means
    save_nii(full_t, ref, OUT / "group_t.nii.gz")
    save_nii(full_p, ref, OUT / "p_fwe_bonferroni.nii.gz")
    save_nii(full_mean, ref, OUT / "group_mean_effect.nii.gz")
    save_nii(mask.astype(np.uint8), ref, OUT / "analysis_mask.nii.gz")
    save_nii(roi_all.astype(np.uint8), ref, OUT / "vmPFC_sphere_10mm.nii.gz")

    sig = p_bonf < .05
    best = peak_idx
    best_xyz = nib.affines.apply_affine(affine, np.unravel_index(np.flatnonzero(mask)[best], shape))
    summary = {
        "n_participants": n, "n_excluded": 0, "mask_voxels": nvox,
        "mask_voxel_volume_mm3": float(np.prod(ref.header.get_zooms()[:3])),
        "fwe_method": "one-sided parametric t tests, Bonferroni over all common brain-mask voxels",
        "bonferroni_min_fwe_p": float(p_bonf.min()),
        "bonferroni_significant_voxels_p_fwe_lt_0.05": int((p_bonf < .05).sum()),
        "peak_t": float(tmap[best]), "peak_uncorrected_one_sided_p": float(p_unc[best]),
        "peak_mni_mm": [float(x) for x in best_xyz],
        "vmPFC_roi": {"definition": f"{ROI_RADIUS_MM:g}-mm radius sphere centered at MNI {ROI_CENTER.tolist()}",
                       "source": "Bartra et al. 2013 positive-value vmPFC focus (2, 46, -8)",
                       "voxels": roi_nvox, "participants": n, "mean_effect": roi_mean,
                       "sd_between_participants": roi_sd, "ci95_t": [float(ci[0]), float(ci[1])],
                       "t_53": float(roi_t), "p_one_sided": roi_p,
                       "wilcoxon_p_one_sided_sensitivity": float(wilcoxon.pvalue),
                       "participants_positive": int((roi_values > 0).sum()),
                       "median_effect": float(np.median(roi_values))}
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Figure 1: unthresholded whole-brain map with a visible, prespecified ROI boundary.
    fig = plt.figure(figsize=(10, 5))
    display = plotting.plot_stat_map(OUT / "group_t.nii.gz", threshold=2.0, display_mode="z",
                                     cut_coords=[-16, -8, 0, 8, 16, 24], cmap="cold_hot",
                                     colorbar=True, title="Gain-effect group t map (uncorrected; t53)",
                                     figure=fig, black_bg=False)
    display.add_contours(OUT / "vmPFC_sphere_10mm.nii.gz", levels=[0.5], colors=["#1f77b4"], linewidths=1.2)
    fig.savefig(FIG / "whole_brain_tmap.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Corrected positive whole-brain effects (if any) use the same one-sided FWE threshold.
    tcrit = float(stats.t.isf(.05 / nvox, dof))
    fig = plt.figure(figsize=(10, 5))
    display = plotting.plot_stat_map(OUT / "group_t.nii.gz", threshold=tcrit, display_mode="z",
                                     cut_coords=[-16, -8, 0, 8, 16, 24], cmap="autumn",
                                     colorbar=True, title=f"Positive gain effect, Bonferroni FWE p < .05 (t > {tcrit:.2f})",
                                     figure=fig, black_bg=False)
    display.add_contours(OUT / "vmPFC_sphere_10mm.nii.gz", levels=[0.5], colors=["#2166ac"], linewidths=1.2)
    fig.savefig(FIG / "whole_brain_fwe.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: ROI participant effects and mean CI.
    fig, ax = plt.subplots(figsize=(7.4, 4.5))
    jitter = np.random.default_rng(SEED).normal(0, 0.035, n)
    ax.scatter(1 + jitter, roi_values, color="#2b6f9c", alpha=.72, s=28, edgecolor="white", linewidth=.35)
    ax.errorbar(1.18, roi_mean, yerr=[[roi_mean-ci[0]], [ci[1]-roi_mean]], fmt="D", color="#ba3d36",
                capsize=5, markersize=7, label="Mean and 95% t interval")
    ax.axhline(0, color="black", lw=1, ls="--")
    ax.set(xlim=(.72, 1.48), xticks=[1], xticklabels=["Participants"], ylabel="Mean gain-effect estimate in vmPFC sphere",
           title="Prespecified vmPFC summary (54 participants)")
    ax.legend(frameon=False, loc="best")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "vmPFC_participant_effects.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
