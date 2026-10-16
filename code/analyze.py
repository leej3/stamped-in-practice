#!/usr/bin/env python3
"""One-sample group inference for supplied NARPS AO86 gain contrast maps."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets, image, plotting
from scipy.stats import t as t_dist

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "input/sources.json"
PARTICIPANTS = ROOT / "input/participants.tsv"
OUT = ROOT / "results"
ATLAS_PATH = ROOT / "input/reference/HarvardOxford-cort-maxprob-thr25-2mm.nii.gz"
N_PERM = 5000
SEED = 20261016


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def get_atlas():
    if not ATLAS_PATH.exists():
        atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
        ATLAS_PATH.parent.mkdir(parents=True, exist_ok=True)
        nib.save(atlas.maps, ATLAS_PATH)
    return nib.load(ATLAS_PATH)


def load_inputs(limit: int | None = None):
    manifest = json.loads(MANIFEST.read_text())
    cohort = pd.read_csv(PARTICIPANTS, sep="\t")
    if cohort.participant_id.duplicated().any():
        raise ValueError("Duplicate participant_id in cohort table")
    source_files = manifest["files"]
    entries = [(p, m) for p, m in source_files.items() if p.endswith(".nii.gz")]
    entries.sort(key=lambda item: item[1]["participant_id"])
    if limit:
        entries = entries[:limit]
    ids = [m["participant_id"] for _, m in entries]
    if limit is None and (len(entries) != 54 or set(ids) != set(cohort.participant_id)):
        raise ValueError("Input maps do not match all 54 cohort participants")
    if len(ids) != len(set(ids)) or not set(ids) <= set(cohort.participant_id):
        raise ValueError("Map IDs are duplicated or absent from participant table")
    arrays, img0, checkrows = [], None, []
    for rel, meta in entries:
        path = ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(path)
        digest = sha256(path)
        if digest != meta["sha256"]:
            raise ValueError(f"Checksum mismatch: {rel}")
        img = nib.load(path)
        arr = img.get_fdata(dtype=np.float32)
        if img0 is None:
            img0 = img
        if arr.shape != img0.shape or not np.allclose(img.affine, img0.affine, atol=1e-5):
            raise ValueError(f"Spatial shape/affine mismatch: {rel}")
        if not np.isfinite(arr).all():
            raise ValueError(f"Nonfinite values: {rel}")
        arrays.append(arr)
        checkrows.append({"participant_id": meta["participant_id"], "path": rel,
                          "sha256": digest, "shape": arr.shape,
                          "min": float(arr.min()), "max": float(arr.max())})
    return np.stack(arrays), img0, ids, checkrows


def tstat(values):
    n = values.shape[0]
    mean = values.mean(axis=0)
    sd = values.std(axis=0, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        stat = mean / (sd / np.sqrt(n))
    return mean, np.nan_to_num(stat, nan=0.0, posinf=0.0, neginf=0.0)


def perm_max_t(voxels, observed, n_perm=N_PERM, seed=SEED, chunk=8192):
    """One-sided max-t sign flip with invariant sum of squares, chunked over voxels."""
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(n_perm, voxels.shape[0]))
    n = voxels.shape[0]
    maxima = np.full(n_perm, -np.inf)
    for start in range(0, voxels.shape[1], chunk):
        x = voxels[:, start:start + chunk]
        sums = signs @ x
        means = sums / n
        centered_ss = np.maximum(np.sum(x * x, axis=0)[None, :] - n * means * means, 1e-30)
        stats = means / np.sqrt(centered_ss / (n - 1) / n)
        maxima = np.maximum(maxima, stats.max(axis=1))
    fwe = (1 + (maxima[:, None] >= observed[None, :]).sum(axis=0)) / (n_perm + 1)
    return fwe, maxima


def save_map(data, ref, path, dtype=np.float32):
    img = nib.Nifti1Image(np.asarray(data, dtype=dtype), ref.affine, ref.header)
    nib.save(img, path)


def pilot():
    data, ref, ids, rows = load_inputs(limit=3)
    support = np.all(np.isfinite(data), axis=0) & np.any(data != 0, axis=0)
    if not support.any():
        raise ValueError("Pilot common nonzero support is empty")
    mean, stat = tstat(data[:, support])
    print(json.dumps({"mode": "pilot", "participants": ids, "shape": data.shape,
                      "support_voxels": int(support.sum()), "mean_range": [float(mean.min()), float(mean.max())],
                      "t_range": [float(stat.min()), float(stat.max())],
                      "checksum_verified": len(rows)}, indent=2))


def run():
    OUT.mkdir(exist_ok=True)
    data, ref, ids, input_rows = load_inputs()
    n = len(ids)
    support = np.all(np.isfinite(data), axis=0) & np.all(data != 0, axis=0)
    if not support.any():
        raise ValueError("Common nonzero support is empty")
    flat = data[:, support].astype(np.float64)
    mean, observed = tstat(flat)
    p_unc = t_dist.sf(observed, n - 1)
    p_fwe, null_maxima = perm_max_t(flat, observed)

    atlas_img = get_atlas()
    atlas_res = image.resample_to_img(atlas_img, ref, interpolation="nearest")
    atlas_arr = atlas_res.get_fdata().astype(int)
    labels = list(datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm").labels)
    roi_labels = ["Frontal Medial Cortex", "Subcallosal Cortex", "Paracingulate Gyrus", "Frontal Orbital Cortex"]
    roi_ids = [labels.index(name) for name in roi_labels]
    roi = np.isin(atlas_arr, roi_ids)
    roi_support = roi & support
    if not roi_support.any():
        raise ValueError("vmPFC atlas ROI does not overlap common tested support")
    # Use 0.05 FWE threshold as the sole confirmatory decision rule.
    fwe_vol = np.zeros(ref.shape, dtype=np.float32)
    pvol = np.ones(ref.shape, dtype=np.float32)
    meanvol = np.zeros(ref.shape, dtype=np.float32)
    tvol = np.zeros(ref.shape, dtype=np.float32)
    fwe_vol[support] = p_fwe
    pvol[support] = p_unc
    meanvol[support] = mean
    tvol[support] = observed
    sig = support & (fwe_vol < .05) & (tvol > 0)
    roi_sig = sig & roi
    roi_sig_idx = np.flatnonzero((p_fwe < .05) & (observed > 0) & roi_support[support])
    p_index = int(roi_sig_idx[np.argmax(observed[roi_sig_idx])]) if len(roi_sig_idx) else None
    peak_index = int(np.argmax(tvol))
    flat_indices = np.flatnonzero(support)
    def peak_record(k):
        ijk = np.unravel_index(int(flat_indices[k]), ref.shape)
        xyz = nib.affines.apply_affine(ref.affine, ijk)
        return {"ijk": [int(x) for x in ijk], "mni_xyz_mm": [round(float(x), 1) for x in xyz],
                "mean_effect": float(mean[k]), "t": float(observed[k]), "p_uncorrected": float(p_unc[k]),
                "p_fwe_max_t": float(p_fwe[k])}
    roi_values = data[:, roi_support].mean(axis=1)
    roi_mean = float(roi_values.mean())
    roi_se = float(roi_values.std(ddof=1) / np.sqrt(n))
    roi_ci = [roi_mean - t_dist.ppf(.975, n - 1) * roi_se,
              roi_mean + t_dist.ppf(.975, n - 1) * roi_se]
    loo = [(roi_values.sum() - x) / (n - 1) for x in roi_values]
    table = pd.DataFrame({"participant_id": ids, "vmPFC_mean_effect": roi_values})
    table.to_csv(OUT / "participant-vmpfc-effects.tsv", sep="\t", index=False)
    pd.DataFrame(input_rows).drop(columns="shape").to_csv(OUT / "input-checksums.tsv", sep="\t", index=False)
    save_map(meanvol, ref, OUT / "group-mean-effect.nii.gz")
    save_map(tvol, ref, OUT / "group-t.nii.gz")
    save_map(fwe_vol, ref, OUT / "group-fwe-p.nii.gz")
    save_map(roi.astype(np.uint8), ref, OUT / "vmpfc-mask.nii.gz", dtype=np.uint8)
    save_map(sig.astype(np.uint8), ref, OUT / "wholebrain-fwe-significant.nii.gz", dtype=np.uint8)

    summary = {
        "analysis": "one-sample positive group mean; maximum-t sign-flip permutation FWE",
        "n": n, "participant_ids": ids, "excluded": [], "voxel_count": int(support.sum()),
        "roi_voxels_in_support": int(roi_support.sum()), "roi_labels": roi_labels,
        "atlas": "Harvard-Oxford cortical max-probability 25%, 2 mm; nearest-neighbor resampled to input space",
        "permutations": N_PERM, "seed": SEED, "monte_carlo_min_p": 1/(N_PERM+1),
        "voxelwise_fwe_alpha": .05, "significant_positive_voxels_whole_brain": int(sig.sum()),
        "significant_positive_voxels_vmpfc": int(roi_sig.sum()), "positive_vmpfc_support": bool(roi_sig.any()),
        "strongest_positive_voxel": peak_record(peak_index),
        "strongest_positive_vmpfc_fwe_voxel": peak_record(p_index) if p_index is not None else None,
        "vmpfc_participant_mean": roi_mean, "vmpfc_t_ci95": [float(x) for x in roi_ci],
        "vmpfc_leave_one_out_mean_range": [float(min(loo)), float(max(loo))],
        "vmpfc_participant_sd": float(roi_values.std(ddof=1)),
        "null_max_t_quantiles": {str(q): float(np.quantile(null_maxima, q)) for q in [.5, .95, .99]},
        "input_manifest_sha256": sha256(MANIFEST), "participants_tsv_sha256": sha256(PARTICIPANTS),
        "python": sys.version, "platform": platform.platform(),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    pd.DataFrame({"null_max_t": null_maxima}).to_csv(OUT / "permutation-max-t.tsv.gz", sep="\t", index=False, compression="gzip")
    print(json.dumps(summary, indent=2))

    # Descriptive participant spread with estimate and interval.
    fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
    jitter = np.random.default_rng(SEED).normal(0, .045, n)
    ax.scatter(1 + jitter, roi_values, s=25, alpha=.7, color="#34495e", edgecolor="white", linewidth=.35)
    ax.errorbar(1.18, roi_mean, yerr=[[roi_mean - roi_ci[0]], [roi_ci[1] - roi_mean]], fmt="D",
                color="#c0392b", capsize=4, label="Mean and 95% t interval")
    ax.axhline(0, color="black", linewidth=.8, linestyle="--")
    ax.set(xlim=(.72, 1.48), xticks=[], ylabel="Participant mean gain-effect estimate",
           title="vmPFC atlas-mask estimates (descriptive; n=54)")
    ax.legend(frameon=False, loc="best")
    fig.savefig(OUT / "vmpfc-participant-estimates.png", dpi=180)
    plt.close(fig)

    # Display the t map with only whole-brain FWE-significant voxels retained.
    display_stat = np.where(sig, tvol, 0)
    stat_img = nib.Nifti1Image(display_stat, ref.affine, ref.header)
    if sig.any():
        display = plotting.plot_stat_map(stat_img, display_mode="ortho", cut_coords=(0, 35, -10),
                                         threshold=0, cmap="magma", colorbar=True,
                                         title="Positive effects surviving whole-brain max-t FWE p < .05")
    else:
        display = plotting.plot_stat_map(nib.Nifti1Image(tvol, ref.affine, ref.header),
                                         display_mode="ortho", cut_coords=(0, 35, -10),
                                         threshold=0, cmap="magma", colorbar=True,
                                         title="Group t map (no positive voxels survive whole-brain FWE p < .05)")
    display.savefig(OUT / "wholebrain-fwe-map.png", dpi=180)
    display.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    pilot() if args.pilot else run()
