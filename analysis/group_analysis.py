#!/usr/bin/env python3
"""Group analysis of NARPS AO86 participant-level gain-effect estimates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets, image, plotting
from scipy.stats import t as t_dist
from scipy.ndimage import label


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
N_PERM = 10000
SEED = 20261016


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_map(data: np.ndarray, ref: nib.spatialimages.SpatialImage, path: Path) -> None:
    hdr = ref.header.copy()
    hdr.set_data_dtype(np.float32)
    nib.save(nib.Nifti1Image(data.astype(np.float32), ref.affine, hdr), path)


def main() -> None:
    meta = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    manifest = json.loads((INPUT / "sources.json").read_text())
    ids = meta.participant_id.tolist()
    paths = [INPUT / "data" / f"{pid}_hypo1_cope.nii.gz" for pid in ids]
    qc = []
    imgs = []
    for pid, path in zip(ids, paths):
        if not path.is_file():
            raise FileNotFoundError(path)
        img = nib.load(path)
        expected = manifest["files"][f"data/{path.name}"]
        digest = sha256(path)
        qc.append({"participant_id": pid, "bytes": path.stat().st_size,
                   "expected_bytes": expected["bytes"], "sha256": digest,
                   "expected_sha256": expected["sha256"],
                   "shape": "x".join(map(str, img.shape)),
                   "finite_fraction": float(np.isfinite(np.asarray(img.dataobj)).mean()),
                   "nonzero_voxels": int(np.count_nonzero(np.asarray(img.dataobj)))})
        if path.stat().st_size != expected["bytes"] or digest != expected["sha256"]:
            raise ValueError(f"Input integrity check failed: {path}")
        if img.shape != (97, 115, 81):
            raise ValueError(f"Unexpected shape for {path}: {img.shape}")
        imgs.append(img)
    pd.DataFrame(qc).to_csv(OUT / "input_qc.csv", index=False)

    ref = imgs[0]
    arr = np.stack([np.asarray(im.dataobj, dtype=np.float32) for im in imgs])
    if not all(np.allclose(im.affine, ref.affine) for im in imgs):
        raise ValueError("Participant images have inconsistent affines")
    if not np.isfinite(arr).all():
        raise ValueError("Non-finite participant effect values")
    # The inputs share a brain coverage mask. Use its intersection for all tests.
    mask = np.all(arr != 0, axis=0)
    n = arr.shape[0]
    flat = arr[:, mask].astype(np.float64, copy=False)
    m = flat.mean(axis=0)
    ss = np.einsum("ij,ij->j", flat, flat)
    sd = flat.std(axis=0, ddof=1)
    t_obs = m / (sd / np.sqrt(n))
    p_unc = t_dist.sf(t_obs, df=n - 1)

    # One-sided max-t sign-flip permutation: participant maps are independent
    # units; one sign is applied to each full image on every draw.
    rng = np.random.default_rng(SEED)
    max_t = np.empty(N_PERM, dtype=np.float32)
    chunk = 128
    denom_const = float(n - 1)
    for start in range(0, N_PERM, chunk):
        k = min(chunk, N_PERM - start)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(k, n))
        sums = signs @ flat
        denom_sq = (n * ss[None, :] - sums * sums) / denom_const
        t_perm = sums / np.sqrt(np.maximum(denom_sq, 1e-30))
        max_t[start:start + k] = np.max(t_perm, axis=1)
    max_t.sort()
    p_fwe = (1 + N_PERM - np.searchsorted(max_t, t_obs, side="left")) / (N_PERM + 1)
    threshold = float(max_t[int(np.ceil((1 - 0.05) * (N_PERM + 1))) - 1])

    mean_img = np.zeros(ref.shape, np.float32)
    t_img = np.zeros(ref.shape, np.float32)
    p_img = np.ones(ref.shape, np.float32)
    fwe_img = np.zeros(ref.shape, np.uint8)
    mean_img[mask] = m
    t_img[mask] = t_obs
    p_img[mask] = p_fwe
    fwe_img[mask] = p_fwe < 0.05
    save_map(mean_img, ref, OUT / "group_mean_effect.nii.gz")
    save_map(t_img, ref, OUT / "group_t.nii.gz")
    save_map(p_img, ref, OUT / "p_fwe_maxT.nii.gz")
    nib.save(nib.Nifti1Image(fwe_img, ref.affine, ref.header), OUT / "significant_fwe.nii.gz")

    # A transparent anatomical operationalization of vmPFC for localization.
    # Harvard-Oxford cortical labels (Frontal Medial, Subcallosal, and the
    # medial portion of Frontal Orbital), resampled nearest-neighbour to data.
    ho = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    atlas_img = image.resample_to_img(ho.maps, ref, interpolation="nearest")
    atlas = np.asarray(atlas_img.dataobj)
    # Labels are 25=Frontal Medial, 27=Subcallosal, 33=Frontal Orbital.
    ijk = np.indices(ref.shape)
    xyz = nib.affines.apply_affine(ref.affine, np.stack(ijk, axis=-1).reshape(-1, 3)).reshape((*ref.shape, 3))
    roi = (((atlas == 25) & (xyz[..., 2] <= 30)) | (atlas == 27) |
           ((atlas == 33) & (np.abs(xyz[..., 0]) <= 20) & (xyz[..., 2] <= 30)))
    roi &= mask
    save_map(roi.astype(np.float32), ref, OUT / "vmPFC_operational_mask.nii.gz")
    roi_n = int(roi.sum())
    roi_vals = arr[:, roi]
    subj_roi = roi_vals.mean(axis=1)
    roi_mean = float(subj_roi.mean())
    roi_sd = float(subj_roi.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_t = roi_mean / roi_se
    roi_p = float(t_dist.sf(roi_t, n - 1))
    roi_ci = [float(roi_mean - t_dist.ppf(.975, n - 1) * roi_se),
              float(roi_mean + t_dist.ppf(.975, n - 1) * roi_se)]
    roi_d = roi_mean / roi_sd
    sig_idx = np.flatnonzero((p_fwe < .05))
    voxel_idx = np.flatnonzero(mask)
    sig_voxels = voxel_idx[sig_idx]
    sig_coords = nib.affines.apply_affine(ref.affine, np.array(np.unravel_index(sig_voxels, ref.shape)).T) if len(sig_voxels) else np.empty((0, 3))
    roi_sig_count = int(np.sum((p_fwe < .05) & roi[mask]))
    pd.DataFrame({"participant_id": ids, "vmPFC_mean_effect": subj_roi}).to_csv(
        OUT / "vmPFC_participant_effects.csv", index=False)

    # Peak coordinates and effect sizes for the most significant positive voxels.
    top = np.argsort(-t_obs)[:10]
    top_vox = voxel_idx[top]
    top_xyz = nib.affines.apply_affine(ref.affine, np.array(np.unravel_index(top_vox, ref.shape)).T)
    peaks = []
    for j, xyzj in zip(top, top_xyz):
        peaks.append({"x": float(xyzj[0]), "y": float(xyzj[1]), "z": float(xyzj[2]),
                      "mean_effect": float(m[j]), "t": float(t_obs[j]),
                      "p_uncorrected": float(p_unc[j]), "p_fwe_maxT": float(p_fwe[j]),
                      "vmPFC_operational_roi": bool(roi[tuple(np.unravel_index(voxel_idx[j], ref.shape))])})
    pd.DataFrame(peaks).to_csv(OUT / "top_voxels.csv", index=False)

    # Cluster summaries describe, but do not replace, voxelwise max-T inference.
    labels, n_labels = label(fwe_img, structure=np.ones((3, 3, 3), dtype=np.uint8))
    clusters = []
    for lab in range(1, n_labels + 1):
        vox = np.flatnonzero(labels == lab)
        flat_indices = np.ravel_multi_index(np.array(np.unravel_index(vox, ref.shape)), ref.shape)
        mask_positions = np.searchsorted(voxel_idx, flat_indices)
        best = mask_positions[np.argmax(t_obs[mask_positions])]
        peak_ijk = np.unravel_index(voxel_idx[best], ref.shape)
        peak_xyz = nib.affines.apply_affine(ref.affine, peak_ijk)
        clusters.append({"cluster": lab, "voxels_26_connected": int(len(vox)),
                         "volume_mm3": float(len(vox) * np.prod(ref.header.get_zooms()[:3])),
                         "peak_x": float(peak_xyz[0]), "peak_y": float(peak_xyz[1]),
                         "peak_z": float(peak_xyz[2]), "peak_t": float(t_obs[best]),
                         "peak_mean_effect": float(m[best]),
                         "peak_p_fwe_maxT": float(p_fwe[best])})
    pd.DataFrame(clusters).to_csv(OUT / "fwe_clusters.csv", index=False)

    result = {
        "n_participants": n, "excluded_participants": [], "mask_voxels": int(mask.sum()),
        "voxel_volume_mm3": float(np.prod(ref.header.get_zooms()[:3])),
        "whole_brain_mask_volume_ml": float(mask.sum() * np.prod(ref.header.get_zooms()[:3]) / 1000),
        "permutations": N_PERM, "seed": SEED, "one_sided": True,
        "maxT_95_threshold": threshold, "whole_brain_fwe_significant_voxels": int((p_fwe < .05).sum()),
        "vmPFC_mask_voxels": roi_n, "vmPFC_mask_volume_ml": float(roi_n * np.prod(ref.header.get_zooms()[:3]) / 1000),
        "vmPFC_mean_effect": roi_mean, "vmPFC_95ci_t": roi_ci, "vmPFC_dz": roi_d,
        "vmPFC_t": float(roi_t), "vmPFC_p_one_sided_uncorrected": roi_p,
        "vmPFC_fwe_significant_voxels": roi_sig_count,
        "top_voxel": peaks[0],
        "group_mean_effect_median_in_mask": float(np.median(m)),
        "participant_map_mean_median": float(np.median(arr[:, mask].mean(axis=1))),
        "participant_map_mean_range": [float(arr[:, mask].mean(axis=1).min()), float(arr[:, mask].mean(axis=1).max())],
        "age_mean": float(meta.age.mean()), "age_sd": float(meta.age.std(ddof=1)),
        "gender_counts": meta.gender.value_counts().sort_index().to_dict(),
    }
    (OUT / "summary.json").write_text(json.dumps(result, indent=2))

    # Figure 1: whole-brain continuous average map and FWE discoveries.
    mean_nii = nib.load(OUT / "group_mean_effect.nii.gz")
    sig_nii = nib.load(OUT / "significant_fwe.nii.gz")
    fig = plt.figure(figsize=(12, 4.2))
    display = plotting.plot_stat_map(mean_nii, display_mode="z", cut_coords=[-8, 0, 8, 16, 24, 32],
                                    threshold=0, cmap="coolwarm", symmetric_cbar=True,
                                    title="Mean gain-effect estimate (unthresholded; FWE discoveries outlined)",
                                    colorbar=True, figure=fig, vmax=float(np.percentile(np.abs(m), 99.5)))
    display.add_contours(sig_nii, levels=[.5], colors="black", linewidths=1.5)
    display.savefig(FIG / "whole_brain_mean_and_fwe.png", dpi=180)
    plt.close(fig)

    # Figure 2: independent unit-level ROI summary, no voxel pseudoreplication.
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    rng_plot = np.random.default_rng(SEED)
    ax.scatter(rng_plot.normal(0, .045, n), subj_roi, s=28, alpha=.72, color="#355C7D", edgecolor="white", linewidth=.35)
    ax.axhline(0, color="0.4", lw=1, ls="--")
    ax.axhline(roi_mean, color="#C06C84", lw=2, label=f"mean = {roi_mean:.3g}")
    ax.fill_between([-.14, .14], roi_ci[0], roi_ci[1], color="#C06C84", alpha=.16,
                    label=f"95% CI [{roi_ci[0]:.3g}, {roi_ci[1]:.3g}]")
    ax.set(xlim=(-.16, .16), xlabel="Participants (jittered)", ylabel="Mean gain-effect estimate in vmPFC mask",
           title="Participant-level vmPFC estimates (n=54)")
    ax.set_xticks([])
    ax.legend(frameon=False, loc="best")
    fig.tight_layout()
    fig.savefig(FIG / "vmPFC_participant_effects.png", dpi=180)
    plt.close(fig)

    # Save atlas label rationale and exact mask definition for reproducibility.
    (OUT / "vmPFC_mask_definition.txt").write_text(
        "Harvard-Oxford cortical max-probability atlas, threshold 25%, labels: "
        "Frontal Medial Cortex (25) restricted to z <= 30 mm, Subcallosal Cortex (27), and "
        "Frontal Orbital Cortex (33) restricted to |MNI x| <= 20 mm and z <= 30 mm "
        "restricted to |MNI x| <= 20 mm and z <= 30 mm; nearest-neighbour resampled to participant grid; "
        "intersected with common participant nonzero coverage. This is an operational anatomical localization mask, "
        "not a uniquely established vmPFC boundary. Whole-brain max-T inference is primary.\n"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
