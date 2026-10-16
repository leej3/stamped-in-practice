#!/usr/bin/env python3
"""One-sample voxelwise max-t permutation analysis for NARPS H1."""
from __future__ import annotations
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
import nilearn
import numpy as np
import pandas as pd
from nilearn import datasets, plotting
from nilearn.image import resample_to_img
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
SEED = 20261015
N_PERM = 9999
ALPHA = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    started = time.time()
    manifest = json.loads((INPUT / "sources.json").read_text())
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    if participants.participant_id.duplicated().any():
        raise ValueError("Duplicate participant IDs in cohort table")
    if not (participants.group == "equalIndifference").all():
        raise ValueError("Unexpected group in cohort table")
    files = manifest["files"]
    ids = participants.participant_id.tolist()
    checks, exclusions, images = [], [], []
    reference_shape = reference_affine = None
    for pid in ids:
        rel = f"data/{pid}_hypo1_cope.nii.gz"
        path = INPUT / rel
        if rel not in files or not path.is_file():
            exclusions.append({"participant_id": pid, "reason": "missing map or manifest entry"})
            continue
        digest = sha256(path)
        expected = files[rel]["sha256"]
        img = nib.load(str(path))
        data = np.asarray(img.dataobj, dtype=np.float32)
        reasons = []
        if digest != expected:
            reasons.append("SHA256 mismatch")
        if not np.isfinite(data).all():
            reasons.append("nonfinite voxel values")
        if reference_shape is None:
            reference_shape, reference_affine = img.shape, img.affine
        elif img.shape != reference_shape or not np.allclose(img.affine, reference_affine, atol=1e-4):
            reasons.append("incompatible image geometry")
        voxel_sizes = nib.affines.voxel_sizes(img.affine)
        checks.append({"participant_id": pid, "sha256_expected": expected,
                       "sha256_observed": digest, "checksum_ok": digest == expected,
                       "shape": "x".join(map(str, img.shape)),
                       "voxel_sizes_mm": ",".join(f"{v:g}" for v in voxel_sizes),
                       "finite": bool(np.isfinite(data).all()),
                       "min": float(np.nanmin(data)), "max": float(np.nanmax(data)),
                       "mean_all_voxels": float(np.nanmean(data)),
                       "std_all_voxels": float(np.nanstd(data)),
                       "qc_flags": "; ".join(reasons)})
        if reasons:
            exclusions.append({"participant_id": pid, "reason": "; ".join(reasons)})
        else:
            images.append((pid, img, data))
    pd.DataFrame(checks).to_csv(OUT / "map_qc.tsv", sep="\t", index=False)
    pd.DataFrame(exclusions, columns=["participant_id", "reason"]).to_csv(OUT / "exclusions.tsv", sep="\t", index=False)
    if len(images) < 3:
        raise RuntimeError(f"Only {len(images)} valid maps")
    if [x[0] for x in images] != ids:
        raise RuntimeError("Validated map order differs from cohort table")

    mask_img = datasets.load_mni152_brain_mask(resolution=2)
    target_img = images[0][1]
    mask_img = resample_to_img(mask_img, target_img, interpolation="nearest", force_resample=True, copy_header=True)
    mask = np.asarray(mask_img.dataobj) > 0
    stack = np.stack([x[2] for x in images], axis=0)
    mask &= np.isfinite(stack).all(axis=0)
    if not mask.any():
        raise RuntimeError("No valid voxels in common MNI152 brain mask")
    x = stack[:, mask].astype(np.float64, copy=False)
    n, nvox = x.shape
    mean = x.mean(axis=0)
    sd = x.std(axis=0, ddof=1)
    se = sd / np.sqrt(n)
    t_obs = np.divide(mean, se, out=np.zeros_like(mean), where=se > 0)
    df = n - 1
    p_unc = stats.t.sf(t_obs, df)
    t_obs[~np.isfinite(t_obs)] = 0

    # Under sign flips, sum(x_i^2) is fixed. This identity computes the
    # studentized one-sample statistic from the sign-flipped sum efficiently.
    rng = np.random.default_rng(SEED)
    null_max = np.empty(N_PERM, dtype=np.float64)
    sumsq = np.sum(x * x, axis=0)
    offset = 0
    while offset < N_PERM:
        batch = min(32, N_PERM - offset)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(batch, n))
        sums = signs @ x
        means = sums / n
        variances = np.maximum((sumsq[None, :] - sums * sums / n) / (n - 1), 0)
        denom = np.sqrt(variances / n)
        t_perm = np.divide(means, denom, out=np.zeros_like(means), where=denom > 0)
        null_max[offset:offset + batch] = np.max(t_perm, axis=1)
        offset += batch
    null_sorted = np.sort(null_max)
    # Plus-one Monte Carlo correction; exceedance uses >=.
    first_ge = np.searchsorted(null_sorted, t_obs, side="left")
    p_fwe = (N_PERM - first_ge + 1) / (N_PERM + 1)
    p_fwe = np.clip(p_fwe, 1 / (N_PERM + 1), 1)

    mean_img_data = np.zeros(reference_shape, dtype=np.float32)
    t_img_data = np.zeros(reference_shape, dtype=np.float32)
    p_img_data = np.ones(reference_shape, dtype=np.float32)
    pu_img_data = np.ones(reference_shape, dtype=np.float32)
    thresh_img_data = np.zeros(reference_shape, dtype=np.float32)
    mean_img_data[mask] = mean
    t_img_data[mask] = t_obs
    p_img_data[mask] = p_fwe
    pu_img_data[mask] = p_unc
    thresh_img_data[mask] = np.where(p_fwe <= ALPHA, t_obs, 0)
    affine = images[0][1].affine
    header = images[0][1].header.copy()
    header.set_data_dtype(np.float32)
    for name, array in [("mean_effect", mean_img_data), ("t_unthresholded", t_img_data),
                        ("p_fwe", p_img_data), ("p_uncorrected", pu_img_data),
                        ("t_fwe05", thresh_img_data)]:
        nib.save(nib.Nifti1Image(array, affine, header), OUT / f"{name}.nii.gz")

    ijk = np.argwhere(mask)
    xyz = nib.affines.apply_affine(affine, ijk)
    peak_indices = np.argsort(t_obs)[::-1][:20]
    peaks = []
    for idx in peak_indices:
        i, j, k = ijk[idx]
        peaks.append({"rank": len(peaks) + 1, "i": int(i), "j": int(j), "k": int(k),
                      "x_mm": float(xyz[idx, 0]), "y_mm": float(xyz[idx, 1]), "z_mm": float(xyz[idx, 2]),
                      "mean_effect": float(mean[idx]), "sd_between_subjects": float(sd[idx]),
                      "t": float(t_obs[idx]), "p_uncorrected_one_sided": float(p_unc[idx]),
                      "p_fwe_max_t": float(p_fwe[idx])})
    pd.DataFrame(peaks).to_csv(OUT / "top_voxels.tsv", sep="\t", index=False)
    pd.DataFrame({"max_t_null": null_sorted}).to_csv(OUT / "permutation_max_t.tsv", sep="\t", index=False)

    # Coordinate-defined vmPFC box is used only for a descriptive participant
    # distribution; primary inference remains corrected across the whole mask.
    vm_roi = mask.copy()
    coords = np.indices(reference_shape, dtype=float)
    world = nib.affines.apply_affine(affine, np.stack(coords, axis=-1).reshape(-1, 3)).reshape(*reference_shape, 3)
    vm_roi &= (np.abs(world[..., 0]) <= 10) & (world[..., 1] >= 20) & (world[..., 1] <= 60) & (world[..., 2] >= -20) & (world[..., 2] <= 20)
    roi_nvox = int(vm_roi.sum())
    if roi_nvox == 0:
        raise RuntimeError("Coordinate-defined vmPFC descriptive region is empty")
    vm_effects = stack[:, vm_roi].mean(axis=1)
    roi_mean = float(vm_effects.mean())
    roi_sd = float(vm_effects.std(ddof=1))
    roi_ci = stats.t.interval(0.95, n - 1, loc=roi_mean, scale=roi_sd / np.sqrt(n))
    participant_summary = pd.DataFrame({"participant_id": [x[0] for x in images], "vmPFC_box_mean_effect": vm_effects})
    participant_summary.to_csv(OUT / "participant_vmPFC_summary.tsv", sep="\t", index=False)
    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    ax.scatter(np.arange(n) + 1, vm_effects, color="#356A8A", alpha=.8, s=24)
    ax.axhline(roi_mean, color="#B33C2E", lw=2, label=f"mean {roi_mean:.3g}; 95% CI [{roi_ci[0]:.3g}, {roi_ci[1]:.3g}]")
    ax.axhline(0, color="black", lw=1, ls="--")
    ax.set(xlabel="Participant (cohort table order)", ylabel="Mean participant gain effect (map units)",
           title="Descriptive vmPFC coordinate-box effects")
    ax.legend(frameon=False, loc="best")
    fig.savefig(OUT / "vmPFC_participant_effects.png", dpi=180)
    plt.close(fig)

    t_img = nib.Nifti1Image(t_img_data, affine, header)
    fwe_img = nib.Nifti1Image(thresh_img_data, affine, header)
    fig = plt.figure(figsize=(10, 5.4))
    plotting.plot_stat_map(t_img, display_mode="ortho", cut_coords=(0, 40, -8), threshold=None,
                           cmap="cold_hot", colorbar=True, title="Group gain effect: unthresholded t map",
                           figure=fig, axes=(0.03, 0.10, 0.62, 0.78))
    if np.any(thresh_img_data):
        plotting.plot_stat_map(fwe_img, display_mode="ortho", cut_coords=(0, 40, -8), threshold=0,
                               cmap="cold_hot", colorbar=True,
                               title="Positive voxels, whole-brain max-t FWE p ≤ .05",
                               figure=fig, axes=(0.68, 0.10, 0.30, 0.78))
    else:
        ax = fig.add_axes((0.68, 0.2, 0.30, 0.55))
        ax.axis("off")
        ax.text(.5, .5, "No positive voxel passed\nwhole-brain max-t FWE p ≤ .05", ha="center", va="center", fontsize=13)
    fig.savefig(OUT / "whole_brain_results.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    sig = p_fwe <= ALPHA
    vm_sig = sig & (np.abs(xyz[:, 0]) <= 10) & (xyz[:, 1] >= 20) & (xyz[:, 1] <= 60) & (xyz[:, 2] >= -20) & (xyz[:, 2] <= 20)
    summary = {
        "question": "Positive group mean gain effect in equal-indifference NARPS cohort",
        "n_expected": len(ids), "n_included": n, "n_excluded": len(exclusions),
        "n_voxels_tested": int(nvox), "alpha_one_sided": ALPHA,
        "permutation_method": "participant-level sign flips; one-sided max-t FWE",
        "permutations": N_PERM, "seed": SEED, "df": df,
        "n_fwe_positive_voxels": int(sig.sum()), "n_fwe_positive_voxels_in_vmPFC_box": int(vm_sig.sum()),
        "vmPFC_box_definition_mni_mm": {"x": [-10, 10], "y": [20, 60], "z": [-20, 20]},
        "vmPFC_box_voxels": roi_nvox, "vmPFC_box_mean_effect": roi_mean,
        "vmPFC_box_between_subject_sd": roi_sd, "vmPFC_box_mean_95ci_t": [float(roi_ci[0]), float(roi_ci[1])],
        "maximum_observed_t": float(t_obs.max()), "minimum_fwe_p": float(p_fwe.min()),
        "runtime_seconds": round(time.time() - started, 3),
        "python": sys.version.split()[0], "platform": platform.platform(),
        "numpy": np.__version__, "pandas": pd.__version__, "nibabel": nib.__version__, "nilearn": nilearn.__version__
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
