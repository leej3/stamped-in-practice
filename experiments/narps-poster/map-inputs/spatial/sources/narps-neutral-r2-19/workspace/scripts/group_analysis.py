"""One-sample whole-brain group test for the NARPS AO86 gain-effect maps."""
from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import plotting
from scipy.stats import t as t_dist

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "work" / "maps"
OUT = ROOT / "results"
FIG = ROOT / "figures"
N_PERM = int(os.environ.get("NARPS_PERMUTATIONS", "10000"))
SEED = 20261016
ALPHA = 0.05


def save_like(ref, data, path, dtype=np.float32):
    hdr = ref.header.copy()
    hdr.set_data_dtype(dtype)
    nib.save(nib.Nifti1Image(np.asarray(data, dtype=dtype), ref.affine, hdr), str(path))


def main():
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    cohort = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
    files = sorted(MAPS.glob("sub-*_hypo1_cope.nii.gz"))
    ids = [p.name.split("_")[0] for p in files]
    if len(files) != 54 or set(ids) != set(cohort.participant_id):
        raise ValueError(f"Map/cohort mismatch: maps={len(files)}, cohort={len(cohort)}")
    imgs = [nib.load(str(p)) for p in files]
    ref = imgs[0]
    for path, img in zip(files, imgs):
        if img.shape != ref.shape or not np.allclose(img.affine, ref.affine, atol=1e-5):
            raise ValueError(f"Geometry mismatch: {path}")
    arr = np.stack([img.get_fdata(dtype=np.float32) for img in imgs])
    finite = np.isfinite(arr)
    # All maps are unthresholded but zero-filled outside their participant brain mask.
    # The intersection gives a fixed, common-coverage analysis mask without filling gaps.
    mask = finite.all(axis=0) & (arr != 0).all(axis=0)
    if mask.sum() < 10000:
        raise ValueError(f"Implausibly small common mask: {mask.sum()} voxels")
    Y = arr[:, mask].astype(np.float64, copy=False)  # participants x voxels
    n, nvox = Y.shape
    mean = Y.mean(axis=0)
    sd = Y.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = t_dist.sf(t_obs, df=n - 1)

    # One-sided random-effects one-sample inference by participant-level sign flips.
    # The maximum positive t statistic controls FWE over every tested brain voxel.
    rng = np.random.default_rng(SEED)
    max_null = np.empty(N_PERM, dtype=np.float32)
    batch = 64
    sumsq = np.sum(Y * Y, axis=0)
    for start in range(0, N_PERM, batch):
        b = min(batch, N_PERM - start)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
        sums = signs @ Y
        means = sums / n
        var = np.maximum((sumsq[None, :] - (sums * sums) / n) / (n - 1), 1e-20)
        ts = means / np.sqrt(var / n)
        max_null[start:start+b] = np.max(ts, axis=1)
    max_null.sort()
    p_fwe = (1 + N_PERM - np.searchsorted(max_null, t_obs, side="left")) / (N_PERM + 1)
    # Observed threshold whose permutation maximum has upper-tail alpha probability.
    t_fwe = float(np.quantile(max_null, 1 - ALPHA, method="higher"))

    # Anatomically defined vmPFC search mask in MNI152NLin2009cAsym coordinates.
    # Bilateral medial prefrontal/orbitofrontal and subgenual territory, specified
    # independently of these maps. Inference remains whole-brain corrected.
    ijk = np.column_stack(np.where(mask))
    xyz = nib.affines.apply_affine(ref.affine, ijk)
    roi = ((np.abs(xyz[:, 0]) <= 15) & (xyz[:, 1] >= 25) & (xyz[:, 1] <= 65)
           & (xyz[:, 2] >= -25) & (xyz[:, 2] <= 10))
    if roi.sum() == 0:
        raise ValueError("vmPFC coordinate mask is empty")
    roi_Y = Y[:, roi].mean(axis=1)
    roi_mean = float(roi_Y.mean())
    roi_sd = float(roi_Y.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_t = roi_mean / roi_se
    roi_p = float(t_dist.sf(roi_t, df=n - 1))
    roi_ci = [float(roi_mean - t_dist.ppf(.975, n - 1) * roi_se),
              float(roi_mean + t_dist.ppf(.975, n - 1) * roi_se)]

    # Save spatial maps in the original grid and explicit voxelwise results.
    mean_img = np.zeros(ref.shape, dtype=np.float32)
    t_img = np.zeros(ref.shape, dtype=np.float32)
    p_img = np.ones(ref.shape, dtype=np.float32)
    fwe_img = np.ones(ref.shape, dtype=np.float32)
    mean_img[mask], t_img[mask] = mean, t_obs
    p_img[mask], fwe_img[mask] = p_unc, p_fwe
    save_like(ref, mean_img, OUT / "group_mean_effect.nii.gz")
    save_like(ref, t_img, OUT / "group_t_positive.nii.gz")
    save_like(ref, p_img, OUT / "group_p_uncorrected.nii.gz")
    save_like(ref, fwe_img, OUT / "group_p_fwe_maxT.nii.gz")

    # Participant-level quality summary; no statistical outlier exclusions.
    rows = []
    for i, pid in enumerate(ids):
        vals = arr[i][mask]
        rows.append({"participant_id": pid, "n_common_voxels": int(vals.size),
                     "mean_effect": float(vals.mean()), "sd_effect": float(vals.std(ddof=1)),
                     "min_effect": float(vals.min()), "max_effect": float(vals.max()),
                     "nonzero_fraction": float(np.count_nonzero(arr[i]) / arr[i].size),
                     "vmPFC_mean_effect": float(roi_Y[i])})
    qc = pd.DataFrame(rows).merge(cohort, on="participant_id", validate="one_to_one")
    qc.to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)

    peak_idx = int(np.argmax(t_obs))
    peak_xyz = xyz[peak_idx]
    sig = p_fwe < ALPHA
    roi_sig = sig & roi
    result = {
        "n": n, "excluded": [], "common_mask_voxels": int(nvox),
        "common_mask_mm3": float(nvox * np.prod(ref.header.get_zooms()[:3])),
        "grid_shape": list(ref.shape), "voxel_size_mm": list(map(float, ref.header.get_zooms()[:3])),
        "permutations": N_PERM, "random_seed": SEED, "test": "one-sided one-sample sign-flip max-t",
        "correction": "max positive t over common brain mask; permutation FWE",
        "alpha": ALPHA, "t_fwe_threshold": t_fwe, "n_fwe_significant_voxels": int(sig.sum()),
        "n_fwe_significant_voxels_vmPFC": int(roi_sig.sum()),
        "vmPFC_mask_voxels": int(roi.sum()), "vmPFC_definition_mni_mm": {
            "x": [-15, 15], "y": [25, 65], "z": [-25, 10]},
        "vmPFC_mean_effect": roi_mean, "vmPFC_sd_between_participants": roi_sd,
        "vmPFC_95ci": roi_ci, "vmPFC_t_descriptive": roi_t, "vmPFC_p_uncorrected_descriptive": roi_p,
        "max_t": float(t_obs[peak_idx]), "max_t_mni_mm": [float(v) for v in peak_xyz],
        "max_t_p_fwe": float(p_fwe[peak_idx]),
        "min_p_fwe": float(p_fwe.min()), "mean_effect_whole_brain": float(mean.mean()),
    }
    (OUT / "group_results.json").write_text(json.dumps(result, indent=2) + "\n")
    pd.DataFrame({"t": t_obs, "p_uncorrected_one_sided": p_unc, "p_fwe_maxT": p_fwe,
                  "in_vmPFC_coordinate_mask": roi}).to_csv(OUT / "voxel_results.csv.gz", index=False)

    # Compact, interpretation-focused figure: average conditional gain effect and
    # whole-brain family-wise corrected one-sided group t map.
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    plt.sca(axes[0])
    d1 = plotting.plot_stat_map(OUT / "group_mean_effect.nii.gz", display_mode="ortho",
        cut_coords=(0, 45, -10), colorbar=True, cmap="RdBu_r", symmetric_cbar=True,
        title="Mean participant gain-effect estimate", axes=axes[0], annotate=True,
        black_bg=False, resampling_interpolation="continuous")
    # second plot uses a threshold exactly corresponding to the permutation max-t cutoff
    plt.sca(axes[1])
    d2 = plotting.plot_stat_map(OUT / "group_t_positive.nii.gz", display_mode="ortho",
        cut_coords=(0, 45, -10), colorbar=True, cmap="hot", threshold=t_fwe,
        title=f"vmPFC: no voxels pass whole-brain FWE p < .05\nmax-t threshold = {t_fwe:.2f}",
        axes=axes[1], annotate=True, black_bg=False, symmetric_cbar=False, vmin=0,
        vmax=float(np.max(t_obs)), resampling_interpolation="continuous")
    fig.savefig(FIG / "group_effect_and_fwe.png", dpi=180)
    plt.close(fig)

    display = plotting.plot_glass_brain(OUT / "group_t_positive.nii.gz", display_mode="ortho",
        colorbar=True, cmap="hot", threshold=t_fwe, plot_abs=False, black_bg=False,
        symmetric_cbar=False, vmin=0, vmax=float(np.max(t_obs)),
        title=f"FWE corrected ({int(sig.sum())} voxels)")
    display.savefig(FIG / "whole_brain_fwe.png", dpi=180)
    display.close()

    # Distribution of subject-specific vmPFC averages (descriptive; not a second test).
    fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
    x = np.arange(1, n + 1)
    ax.scatter(x, roi_Y, s=24, alpha=.8, color="#26547c")
    ax.axhline(0, color="black", lw=1)
    ax.axhline(roi_mean, color="#d1495b", lw=2, label=f"mean = {roi_mean:.3f}")
    ax.fill_between([0, n + 1], roi_ci[0], roi_ci[1], color="#d1495b", alpha=.15,
                    label="95% CI for mean")
    ax.set(xlim=(0, n + 1), xlabel="Participant (maps sorted by ID)",
           ylabel="Mean gain-effect estimate in vmPFC mask",
           title="Participant-level vmPFC effect estimates")
    ax.legend(frameon=False)
    fig.savefig(FIG / "vmPFC_participant_effects.png", dpi=180)
    plt.close(fig)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
