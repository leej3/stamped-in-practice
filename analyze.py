#!/usr/bin/env python3
"""Group inference for fixed NARPS AO86 gain-effect maps."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from scipy.stats import t as t_dist
from scipy import ndimage


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input"
OUT = ROOT / "results"
PARTICIPANTS = INPUT / "participants.tsv"
MAP_DIR = INPUT / "data"
ROI_CENTER = np.array([0.0, 42.0, -8.0])  # MNI mm, anterior medial OFC / vmPFC
ROI_RADIUS_MM = 10.0
N_PERMUTATIONS = 9999
SEED = 20261015


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_nifti(data: np.ndarray, reference: nib.spatialimages.SpatialImage, path: Path) -> None:
    hdr = reference.header.copy()
    hdr.set_data_dtype(np.float32)
    nib.save(nib.Nifti1Image(data.astype(np.float32), reference.affine, hdr), str(path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    start = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)

    participants = pd.read_csv(PARTICIPANTS, sep="\t")
    paths = [MAP_DIR / f"{pid}_hypo1_cope.nii.gz" for pid in participants.participant_id]
    source_meta = json.loads((INPUT / "sources.json").read_text())
    expected_paths = {f"input/data/{pid}_hypo1_cope.nii.gz" for pid in participants.participant_id}
    actual_paths = {str(p.relative_to(ROOT)) for p in MAP_DIR.glob("*.nii.gz")}
    if len(participants) != 54 or actual_paths != expected_paths:
        raise ValueError("Participant table and supplied gain maps do not match the expected 54-person cohort")
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing maps: {missing}")
    imgs = [nib.load(str(p)) for p in paths]
    ref = imgs[0]
    for p, img in zip(paths, imgs):
        if img.shape != ref.shape or not np.allclose(img.affine, ref.affine):
            raise ValueError(f"Spatial mismatch: {p}")
    # All supplied images are finite; zero is the upstream outside-mask fill.
    # A 90% participant-coverage mask reduces edge voxels with inconsistent coverage.
    data = np.stack([np.asarray(img.dataobj, dtype=np.float32) for img in imgs])
    if not np.isfinite(data).all():
        raise ValueError("At least one input map contains non-finite values")
    input_hashes = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    for relpath, sha in input_hashes.items():
        manifest_key = str((ROOT / relpath).relative_to(INPUT))
        if source_meta["files"][manifest_key]["sha256"] != sha:
            raise ValueError(f"Input checksum differs from supplied source manifest: {relpath}")
    coverage = np.count_nonzero(data, axis=0)
    mask = coverage >= int(np.ceil(0.90 * len(paths)))
    if mask.sum() == 0:
        raise ValueError("Empty analysis mask")
    X = data[:, mask].astype(np.float64)
    n, v = X.shape
    means = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    observed_t = means / (sd / np.sqrt(n))
    p_unc = t_dist.sf(observed_t, df=n - 1)

    # One-sided sign-flip max-T controls family-wise error over the entire
    # coverage mask. Studentization is recomputed for every sign permutation.
    rng = np.random.default_rng(args.seed)
    sumsq = np.einsum("ij,ij->j", X, X)
    max_null = np.empty(args.permutations, dtype=np.float32)
    batch = 64
    done = 0
    while done < args.permutations:
        b = min(batch, args.permutations - done)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
        # Each sign pattern is a participant-level randomization under a
        # symmetric null; participant observations are never spatially shuffled.
        perm_sum = signs @ X
        perm_mean = perm_sum / n
        perm_ss = np.maximum(sumsq[None, :] - n * perm_mean**2, 0.0)
        perm_sd = np.sqrt(perm_ss / (n - 1))
        denom = perm_sd / np.sqrt(n)
        tvals = np.divide(perm_mean, denom, out=np.zeros_like(perm_mean), where=denom > 0)
        max_null[done:done + b] = np.max(tvals, axis=1)
        done += b
    p_fwer = (1.0 + np.sum(max_null[:, None] >= observed_t[None, :], axis=0)) / (args.permutations + 1)

    # ROI is specified independently from the observed maps: 10-mm sphere
    # centered at [0, 42, -8] MNI, a conventional anterior vmPFC / medial OFC
    # location. It is used for anatomical localization and descriptive estimates;
    # the confirmatory decision still requires whole-brain max-T correction.
    ijk = np.array(np.where(mask)).T
    xyz = nib.affines.apply_affine(ref.affine, ijk)
    roi_vox = np.sum((xyz - ROI_CENTER) ** 2, axis=1) <= ROI_RADIUS_MM**2
    if roi_vox.sum() < 5:
        raise ValueError("ROI has fewer than five voxels in coverage mask")
    # map the ROI voxels to X columns (mask order is C-order)
    roi_idx = np.flatnonzero(roi_vox)
    subject_roi = X[:, roi_idx].mean(axis=1)
    roi_mean = float(subject_roi.mean())
    roi_sd = float(subject_roi.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    ci = (roi_mean - t_dist.ppf(.975, n - 1) * roi_se,
          roi_mean + t_dist.ppf(.975, n - 1) * roi_se)
    roi_t = roi_mean / roi_se
    roi_p = float(t_dist.sf(roi_t, n - 1))

    t_img = np.zeros(ref.shape, dtype=np.float32)
    p_img = np.ones(ref.shape, dtype=np.float32)
    fwer_img = np.ones(ref.shape, dtype=np.float32)
    mean_img = np.zeros(ref.shape, dtype=np.float32)
    t_img[mask], p_img[mask], fwer_img[mask], mean_img[mask] = observed_t, p_unc, p_fwer, means
    save_nifti(t_img, ref, OUT / "group_t.nii.gz")
    save_nifti(p_img, ref, OUT / "p_uncorrected.nii.gz")
    save_nifti(fwer_img, ref, OUT / "p_fwer_maxT.nii.gz")
    save_nifti(mean_img, ref, OUT / "mean_cope.nii.gz")
    mask_img = np.zeros(ref.shape, dtype=np.uint8)
    mask_img[mask] = 1
    save_nifti(mask_img, ref, OUT / "analysis_mask.nii.gz")

    sig = (p_fwer < .05)
    roi_sig = sig & roi_vox
    sig_img = np.zeros(ref.shape, dtype=np.uint8)
    sig_img[mask] = sig.astype(np.uint8)
    save_nifti(sig_img, ref, OUT / "fwer_significant_mask.nii.gz")
    labels, n_clusters = ndimage.label(sig_img, structure=np.ones((3, 3, 3), dtype=np.uint8))
    cluster_rows = []
    for label_id in range(1, n_clusters + 1):
        inds3 = np.array(np.where(labels == label_id)).T
        world3 = nib.affines.apply_affine(ref.affine, inds3)
        flat_inds = np.ravel_multi_index(inds3.T, ref.shape)
        t_values = t_img.ravel()[flat_inds]
        p_values = fwer_img.ravel()[flat_inds]
        peak_local = int(np.argmax(t_values))
        cluster_rows.append({"cluster": label_id, "voxels": int(len(inds3)),
                             "peak_mni_mm": world3[peak_local].tolist(),
                             "peak_t": float(t_values[peak_local]),
                             "peak_p_fwer_maxT": float(p_values[peak_local])})
    cluster_rows.sort(key=lambda row: row["voxels"], reverse=True)
    max_t_idx = int(np.argmax(observed_t))
    peak_ijk = ijk[max_t_idx]
    peak_xyz = nib.affines.apply_affine(ref.affine, peak_ijk)
    max_p_roi_idx = roi_idx[int(np.argmax(observed_t[roi_idx]))]
    roi_peak_ijk = ijk[max_p_roi_idx]
    roi_peak_xyz = nib.affines.apply_affine(ref.affine, roi_peak_ijk)

    # A small, transparent report table supports reproducibility.
    roi_rows = []
    for pid, val in zip(participants.participant_id, subject_roi):
        roi_rows.append({"participant_id": pid, "vmPFC_mean_cope": float(val)})
    pd.DataFrame(roi_rows).to_csv(OUT / "vmPFC_subject_values.tsv", sep="\t", index=False)

    summary = {
        "n_participants": n, "n_maps": len(paths), "n_excluded": 0,
        "source_manifest_checksums_verified": True, "all_map_values_finite": True,
        "coverage_rule": "voxels nonzero in at least 90% of participant maps",
        "analysis_voxels": int(v), "voxel_volume_mm3": float(abs(np.linalg.det(ref.affine[:3, :3]))),
        "permutation_test": "one-sided participant sign-flip max-T; family-wise corrected across coverage mask",
        "permutations": args.permutations, "seed": args.seed,
        "whole_brain_alpha": 0.05, "n_whole_brain_fwer_significant": int(sig.sum()),
        "n_26_connected_fwer_clusters": int(n_clusters), "fwer_clusters": cluster_rows,
        "n_fwer_significant_in_vmPFC_roi": int(roi_sig.sum()),
        "whole_brain_peak": {"ijk": peak_ijk.tolist(), "mni_mm": peak_xyz.tolist(),
                             "mean_cope": float(means[max_t_idx]), "t": float(observed_t[max_t_idx]),
                             "p_uncorrected": float(p_unc[max_t_idx]), "p_fwer_maxT": float(p_fwer[max_t_idx])},
        "vmPFC_roi": {"definition": "10-mm radius sphere centered at MNI [0, 42, -8] mm",
                      "center_mni_mm": ROI_CENTER.tolist(), "radius_mm": ROI_RADIUS_MM,
                      "voxels": int(len(roi_idx)), "mean_subject_roi_cope": roi_mean,
                      "between_subject_sd": roi_sd, "se": float(roi_se), "ci95_t": [float(x) for x in ci],
                      "one_sample_t": float(roi_t), "p_one_sided_uncorrected_descriptive": roi_p,
                      "peak": {"ijk": roi_peak_ijk.tolist(), "mni_mm": roi_peak_xyz.tolist(),
                               "t": float(observed_t[max_p_roi_idx]), "p_fwer_maxT": float(p_fwer[max_p_roi_idx])}},
        "software": {"python": platform.python_version(), "numpy": np.__version__,
                     "scipy": scipy.__version__, "nibabel": nib.__version__, "pandas": pd.__version__},
        "input_sha256": input_hashes,
        "elapsed_seconds": round(time.time() - start, 2),
        "command": [sys.executable, str(Path(__file__).resolve()), "--permutations", str(args.permutations), "--seed", str(args.seed)],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Figure 1: unthresholded mean estimate with whole-brain corrected locations
    # outlined in black and the independently specified vmPFC sphere in gold.
    fig, axes = plt.subplots(1, 3, figsize=(11, 4), constrained_layout=True)
    for ax, (axis, coord, title) in zip(axes, [(1, 42, "Coronal y=42"), (2, 0, "Axial z=0"), (0, 0, "Sagittal x=0")]):
        world = [0., 0., 0.]
        world[axis] = coord
        sl = int(round(nib.affines.apply_affine(np.linalg.inv(ref.affine), world)[axis]))
        if axis == 1:
            im = mean_img[:, sl, :].T; extent = [-96, 98, -78, 116]
            ax.imshow(im, origin="lower", cmap="RdBu_r", vmin=-.12, vmax=.12, extent=extent)
            sig_slice = sig_img[:, sl, :].T
            if sig_slice.any(): ax.contour(sig_slice, levels=[.5], colors=["black"], linewidths=.8, origin="lower", extent=extent)
            theta = np.linspace(0, 2*np.pi, 200)
            ax.plot(ROI_CENTER[0] + ROI_RADIUS_MM*np.cos(theta), ROI_CENTER[2] + ROI_RADIUS_MM*np.sin(theta), color="gold", lw=1.2)
        elif axis == 2:
            im = mean_img[:, :, sl].T; extent = [-96, 98, -132, 98]
            ax.imshow(im, origin="lower", cmap="RdBu_r", vmin=-.12, vmax=.12, extent=extent)
            sig_slice = sig_img[:, :, sl].T
            if sig_slice.any(): ax.contour(sig_slice, levels=[.5], colors=["black"], linewidths=.8, origin="lower", extent=extent)
            theta = np.linspace(0, 2*np.pi, 200)
            ax.plot(ROI_CENTER[0] + ROI_RADIUS_MM*np.cos(theta), ROI_CENTER[1] + ROI_RADIUS_MM*np.sin(theta), color="gold", lw=1.2)
        else:
            im = mean_img[sl, :, :].T; extent = [-132, 98, -78, 116]
            ax.imshow(im, origin="lower", cmap="RdBu_r", vmin=-.12, vmax=.12, extent=extent)
            sig_slice = sig_img[sl, :, :].T
            if sig_slice.any(): ax.contour(sig_slice, levels=[.5], colors=["black"], linewidths=.8, origin="lower", extent=extent)
            theta = np.linspace(0, 2*np.pi, 200)
            ax.plot(ROI_CENTER[1] + ROI_RADIUS_MM*np.cos(theta), ROI_CENTER[2] + ROI_RADIUS_MM*np.sin(theta), color="gold", lw=1.2)
        ax.set_title(title); ax.set_xlabel("MNI mm"); ax.set_ylabel("MNI mm")
    fig.colorbar(axes[1].images[0], ax=axes, label="Mean gain-effect estimate (a.u.)", shrink=.8)
    fig.suptitle("Mean gain-effect estimate; black: whole-brain FWER voxels; gold: vmPFC sphere")
    fig.savefig(OUT / "figures" / "group_mean_vmPFC.png", dpi=180)
    plt.close(fig)

    # Figure 2: participant-level ROI means with group estimate and CI.
    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
    ax.axhline(0, color="0.4", lw=1)
    jitter = rng.normal(0, .035, len(subject_roi))
    ax.scatter(jitter, subject_roi, color="#356a8a", alpha=.8, s=28, edgecolor="white", linewidth=.4)
    ax.errorbar([.25], [roi_mean], yerr=[[roi_mean-ci[0]], [ci[1]-roi_mean]], fmt="D", color="#b33b2e", capsize=4, label="Mean and 95% t CI")
    ax.set_xlim(-.18, .48); ax.set_xticks([0, .25], ["Participants", "Group mean"])
    ax.set_ylabel("Mean vmPFC gain-effect estimate (a.u.)")
    ax.set_title("Prespecified vmPFC sphere, participant-level estimates")
    ax.legend(frameon=False)
    fig.savefig(OUT / "figures" / "vmPFC_subject_estimates.png", dpi=180)
    plt.close(fig)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
