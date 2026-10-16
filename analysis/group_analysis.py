#!/usr/bin/env python
"""Whole-brain sign-flip max-t inference for supplied NARPS participant effects."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import nilearn
import numpy as np
import pandas as pd
import scipy
from nilearn import image, plotting
from scipy import stats
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results" / "group-analysis"


def main() -> None:
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--permutations", type=int, default=9999)
    parser.add_argument("--seed", type=int, default=20261015)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    if args.permutations < 999:
        raise ValueError("Use at least 999 sign flips for stable tail resolution")
    started = time.time()
    OUT = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    OUT.mkdir(parents=True, exist_ok=True)

    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    source_manifest = json.loads((INPUT / "sources.json").read_text())
    participant_hash = hashlib.sha256((INPUT / "participants.tsv").read_bytes()).hexdigest()
    if participant_hash != source_manifest["files"]["participants.tsv"]["sha256"]:
        raise ValueError("Participant table checksum mismatch")
    paths = sorted((INPUT / "data").glob("*_hypo1_cope.nii.gz"))
    ids_from_maps = [p.name.split("_", 1)[0] for p in paths]
    expected = participants.loc[participants.group.eq("equalIndifference"), "participant_id"].tolist()
    if participants.participant_id.duplicated().any() or len(paths) != 54 or set(ids_from_maps) != set(expected):
        raise ValueError(f"Cohort/map mismatch: table={len(expected)}, maps={len(paths)}")
    by_id = {p.name.split("_", 1)[0]: p for p in paths}
    paths = [by_id[participant_id] for participant_id in expected]
    for path in paths:
        relpath = path.relative_to(ROOT).as_posix()
        expected_hash = source_manifest["files"][relpath]["sha256"]
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"Input checksum mismatch: {relpath}")

    images = [nib.load(str(p)) for p in paths]
    ref = images[0]
    shape = ref.shape
    affine = ref.affine
    if len(shape) != 3:
        raise ValueError(f"Expected 3D maps; got {shape}")
    for p, img in zip(paths, images):
        if img.shape != shape or not np.allclose(img.affine, affine, atol=1e-5):
            raise ValueError(f"Geometry mismatch: {p.name}")
    # N x voxels, float32 holds the supplied cope precision and limits memory.
    stack = np.stack([np.asarray(img.dataobj, dtype=np.float32) for img in images])
    finite = np.isfinite(stack).all(axis=0)
    mask = finite & np.any(stack != 0, axis=0)
    n_vox = int(mask.sum())
    if n_vox == 0:
        raise ValueError("No common nonzero finite voxels")
    X = stack[:, mask].astype(np.float64, copy=False)
    if not np.isfinite(X).all():
        raise ValueError("Nonfinite effect in analysis mask")

    n = len(paths)
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    sem = sd / np.sqrt(n)
    t_obs = np.divide(mean, sem, out=np.zeros_like(mean), where=sem > 0)

    rng = np.random.default_rng(args.seed)
    max_t = np.empty(args.permutations, dtype=np.float64)
    sumsq = np.einsum("ij,ij->j", X, X)
    with threadpool_limits(limits=2):
        for start in range(0, args.permutations, args.batch_size):
            stop = min(start + args.batch_size, args.permutations)
            signs = rng.choice(np.array([-1.0, 1.0]), size=(stop - start, n))
            sums = signs @ X
            means = sums / n
            var = np.maximum((sumsq[None, :] - sums * sums / n) / (n - 1), 0.0)
            t_perm = np.divide(means, np.sqrt(var / n), out=np.zeros_like(means), where=var > 0)
            max_t[start:stop] = np.max(t_perm, axis=1)

    # Correct each voxel against the maximum positive t over the entire mask.
    sorted_max = np.sort(max_t)
    first_ge = np.searchsorted(sorted_max, t_obs, side="left")
    p_fwe = (1 + args.permutations - first_ge) / (args.permutations + 1)
    sig = p_fwe <= 0.05

    # Atlas anatomical label is independent of the observed effects.
    atlas_path = INPUT / "atlas" / "HarvardOxford-cort-prob-2mm.nii.gz"
    atlas_xml = INPUT / "atlas" / "HarvardOxford-Cortical.xml"
    atlas_manifest = json.loads((INPUT / "atlas" / "sources.json").read_text())
    for path, expected_hash in [
        (atlas_path, atlas_manifest["atlas"]["files"][atlas_path.name]),
        (atlas_xml, atlas_manifest["atlas"]["files"][atlas_xml.name]),
        (INPUT / "atlas" / "MNI152_T1_2mm.nii.gz", atlas_manifest["display_template"]["sha256"]),
    ]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            raise ValueError(f"Atlas/display input checksum mismatch: {path.name}")
    atlas = nib.load(str(atlas_path))
    parsed_labels = ET.parse(atlas_xml).getroot().findall(".//label")
    labels = [None] * (max(int(label.attrib["index"]) for label in parsed_labels) + 1)
    for label in parsed_labels:
        labels[int(label.attrib["index"])] = (label.text or "").strip()
    label_indices = [i for i, label in enumerate(labels) if label in {"Frontal Orbital Cortex", "Subcallosal Cortex"}]
    if len(label_indices) != 2:
        raise ValueError("Harvard-Oxford atlas lacks expected orbital/subcallosal labels")
    prob_img = atlas
    prob_data = np.asarray(prob_img.dataobj)
    # Probabilistic atlas is 4D with one volume per cortical label. Use the
    # atlas-defined orbital/subcallosal anatomy, then select anterior midline,
    # ventral voxels; this is a descriptive anatomical ROI, not the search mask.
    prob_masks = []
    for label_idx in label_indices:
        prob = image.resample_img(nib.Nifti1Image(prob_data[..., label_idx], prob_img.affine),
                                  target_affine=affine, target_shape=shape, interpolation="continuous")
        prob_masks.append(np.asarray(prob.dataobj) >= 25)
    ijk = np.indices(shape, dtype=np.float32).reshape(3, -1)
    xyz = nib.affines.apply_affine(affine, ijk.T)
    xyz = xyz.reshape(*shape, 3)
    roi = np.logical_or.reduce(prob_masks) & (np.abs(xyz[..., 0]) <= 15) & (xyz[..., 1] >= 0) & (xyz[..., 2] <= 0) & mask
    n_roi = int(roi.sum())
    if n_roi == 0:
        raise ValueError("Atlas-defined vmPFC mask is empty on input grid")

    roi_subject = stack[:, roi].mean(axis=1).astype(float)
    roi_mean = float(roi_subject.mean())
    roi_sd = float(roi_subject.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_ci = stats.t.interval(0.95, df=n - 1, loc=roi_mean, scale=roi_se)
    roi_t = roi_mean / roi_se if roi_se > 0 else float("nan")
    roi_p_one_sided = float(stats.t.sf(roi_t, df=n - 1))

    # Peak within vmPFC and whole analysis mask, retaining coordinates and corrected p.
    tvol = np.full(shape, np.nan, dtype=np.float32)
    pvol = np.full(shape, np.nan, dtype=np.float32)
    mvol = np.full(shape, np.nan, dtype=np.float32)
    tvol[mask] = t_obs
    pvol[mask] = p_fwe
    mvol[mask] = mean
    # Use native flat-index vectors to avoid dependence on boolean traversal ordering.
    flat_mask = np.flatnonzero(mask)
    flat_t = np.full(np.prod(shape), np.nan)
    flat_t[flat_mask] = t_obs
    flat_roi = np.flatnonzero(roi)
    peak_roi = int(flat_roi[np.nanargmax(flat_t[flat_roi])])
    peak_all = int(flat_mask[np.argmax(t_obs)])
    peak_roi_ijk = np.array(np.unravel_index(peak_roi, shape))
    peak_all_ijk = np.array(np.unravel_index(peak_all, shape))
    peak_roi_xyz = nib.affines.apply_affine(affine, peak_roi_ijk)
    peak_all_xyz = nib.affines.apply_affine(affine, peak_all_ijk)

    nib.save(nib.Nifti1Image(tvol, affine, ref.header), str(OUT / "group_t.nii.gz"))
    nib.save(nib.Nifti1Image(pvol, affine, ref.header), str(OUT / "p_fwe_maxT.nii.gz"))
    nib.save(nib.Nifti1Image(mvol, affine, ref.header), str(OUT / "mean_effect.nii.gz"))
    summary = {
        "question": "Positive gain effect in vmPFC, equal-indifference cohort",
        "n_participants": n,
        "n_excluded": 0,
        "n_voxels_tested": n_vox,
        "n_voxels_fwe_005": int(sig.sum()),
        "permutations": args.permutations,
        "seed": args.seed,
        "test": "one-sided one-sample t; random sign-flip maximum-t whole-mask FWE",
        "p_fwe_min": float(p_fwe.min()),
        "max_t": float(t_obs.max()),
        "max_t_xyz_mm": peak_all_xyz.tolist(),
        "max_t_p_fwe": float(p_fwe[np.argmax(t_obs)]),
        "vmPFC_definition": "Harvard-Oxford cortical atlas Frontal Orbital or Subcallosal Cortex probability >=25%; MNI |x|<=15, y>=0, z<=0",
        "atlas_sha256": hashlib.sha256(atlas_path.read_bytes()).hexdigest(),
        "atlas_labels_sha256": hashlib.sha256(atlas_xml.read_bytes()).hexdigest(),
        "source_manifest": "input/sources.json",
        "atlas_manifest": "input/atlas/sources.json",
        "vmPFC_n_voxels": n_roi,
        "vmPFC_mean_effect": roi_mean,
        "vmPFC_effect_sd_between_participants": roi_sd,
        "vmPFC_mean_95ci": [float(roi_ci[0]), float(roi_ci[1])],
        "vmPFC_t_df": [float(roi_t), n - 1],
        "vmPFC_descriptive_one_sided_p_unadjusted": roi_p_one_sided,
        "vmPFC_peak_t": float(flat_t[peak_roi]),
        "vmPFC_peak_xyz_mm": peak_roi_xyz.tolist(),
        "vmPFC_peak_p_fwe": float(pvol.reshape(-1)[peak_roi]),
        "mask_rule": "all-participant finite and nonzero in at least one supplied map",
        "shape": list(shape),
        "affine": affine.tolist(),
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                     "nibabel": nib.__version__, "nilearn": nilearn.__version__, "pandas": pd.__version__},
        "runtime_seconds": time.time() - started,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    pd.DataFrame({"participant_id": expected, "vmPFC_mean_effect": roi_subject}).to_csv(OUT / "vmPFC_subject_effects.tsv", sep="\t", index=False)
    pd.DataFrame({"max_t_permutation": max_t}).to_csv(OUT / "null_max_t.tsv", sep="\t", index=False)

    # Distribution and uncertainty of independent participants' ROI averages.
    fig, ax = plt.subplots(figsize=(7.0, 4.5), constrained_layout=True)
    xj = rng.normal(0, 0.035, size=n)
    ax.scatter(xj, roi_subject, s=30, alpha=0.72, color="#355c7d", edgecolor="white", linewidth=0.35)
    ax.errorbar(0.24, roi_mean, yerr=[[roi_mean - roi_ci[0]], [roi_ci[1] - roi_mean]], fmt="D", color="#c44e52", capsize=5, markersize=6, label="Mean and 95% t interval")
    ax.axhline(0, color="0.45", linewidth=0.8)
    ax.set(xlim=(-0.12, 0.42), xticks=[0, 0.24], xticklabels=["Participants", "Mean"], ylabel="Mean gain effect in atlas vmPFC (cope units)", title="Participant-level vmPFC gain effects")
    ax.legend(frameon=False, loc="best")
    fig.savefig(OUT / "vmPFC_effects.png", dpi=180)
    plt.close(fig)

    # Whole-brain FWE display: show only voxels surviving max-T FWE, with anatomy.
    t_sig = np.full(shape, 0, dtype=np.float32)
    t_sig[mask] = np.where(sig, t_obs, 0)
    sig_img = nib.Nifti1Image(t_sig, affine)
    background = nib.load(str(INPUT / "atlas" / "MNI152_T1_2mm.nii.gz"))
    display = plotting.plot_stat_map(sig_img, bg_img=background,
                                    threshold=0.01, display_mode="ortho", cut_coords=(0, 30, -8),
                                    cmap="cold_hot", colorbar=True,
                                    title="Positive gain effect: whole-brain max-T FWE p <= .05; vmPFC outline")
    roi_img = nib.Nifti1Image(roi.astype(np.uint8), affine)
    display.add_contours(roi_img, levels=[0.5], colors="#00d7d7", linewidths=1.3)
    display.savefig(OUT / "whole_brain_fwe.png", dpi=180)
    display.close()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
