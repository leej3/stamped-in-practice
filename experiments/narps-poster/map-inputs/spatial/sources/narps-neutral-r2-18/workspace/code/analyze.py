#!/usr/bin/env python3
"""Group analysis of NARPS AO86 gain cope maps (fixed first-level inputs)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from nilearn import plotting

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = OUT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
N_PERM = 9999
SEED = 20261016


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    metadata = json.loads((INPUT / "sources.json").read_text())
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    records = metadata["files"]
    paths = []
    for participant in participants.participant_id:
        rel = f"data/{participant}_hypo1_cope.nii.gz"
        path = INPUT / rel
        assert rel in records and path.is_file(), f"Missing map: {participant}"
        assert path.stat().st_size == records[rel]["bytes"]
        assert sha256(path) == records[rel]["sha256"], f"Checksum mismatch: {participant}"
        paths.append(path)
    assert len(paths) == 54 and participants.participant_id.is_unique

    imgs = [nib.load(str(p)) for p in paths]
    ref = imgs[0]
    for img in imgs[1:]:
        assert img.shape == ref.shape and np.allclose(img.affine, ref.affine), "Grid mismatch"
    data = np.stack([img.get_fdata(dtype=np.float32) for img in imgs])
    finite = np.isfinite(data)
    support = np.mean(finite & (data != 0), axis=0)
    # Strict intersection prevents out-of-coverage zeros in some participants
    # from being treated as measured effects in the group model.
    mask = support >= 1.0
    X = data[:, mask].astype(np.float64)
    assert np.isfinite(X).all() and X.shape[1] > 10000

    n, v = X.shape
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = stats.t.sf(t_obs, n - 1)
    # Sign-flip randomization tests the one-sided group mean under a symmetric
    # zero-centered null. The family-wise statistic is max(t) over every voxel
    # in the whole-brain common-coverage mask.
    rng = np.random.default_rng(SEED)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n))
    signs[0] = 1.0  # include observed orientation in the reference distribution
    # Resampling standardized residuals is unnecessary for the one-sample
    # sign-flip test: each participant's full map is sign-flipped as a unit.
    sumsq = np.einsum("ij,ij->j", X, X)
    max_null = np.empty(N_PERM, dtype=np.float64)
    batch = 64
    denom_df = n - 1
    for start in range(0, N_PERM, batch):
        stop = min(start + batch, N_PERM)
        sums = signs[start:stop] @ X
        numer = sums / n
        var = np.maximum((sumsq[None, :] - sums * sums / n) / denom_df, 0.0)
        t_perm = numer / np.sqrt(np.maximum(var, 1e-30) / n)
        max_null[start:stop] = np.max(t_perm, axis=1)
    p_fwe = (1 + np.sum(max_null[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)
    # Percentile confidence interval for the group mean, voxelwise, uncorrected
    # (descriptive only); inference is the whole-brain permutation test above.
    se = sd / np.sqrt(n)
    ci_low, ci_high = mean - stats.t.ppf(.975, n - 1) * se, mean + stats.t.ppf(.975, n - 1) * se

    # Anatomical localization aid only: independent meta-analytic vmPFC peak
    # (MNI [2, 46, -8]) with a 10-mm sphere. Inference is still max-T whole brain;
    # ROI summaries are descriptive and do not generate a second claim.
    xyz = nib.affines.apply_affine(ref.affine, np.array(np.where(mask)).T)
    roi = np.linalg.norm(xyz - np.array([2., 46., -8.]), axis=1) <= 10.
    roi_mask = np.zeros(ref.shape, dtype=bool)
    roi_mask[mask] = roi
    roi_values = data[:, roi_mask].mean(axis=1)
    roi_ci = stats.t.interval(.95, n - 1, loc=roi_values.mean(), scale=stats.sem(roi_values))
    roi_pmin = float(np.min(p_fwe[roi])) if roi.any() else 1.0

    mean_img_data = np.zeros(ref.shape, np.float32)
    t_img_data = np.zeros(ref.shape, np.float32)
    p_img_data = np.ones(ref.shape, np.float32)
    mask_img_data = mask.astype(np.uint8)
    mean_img_data[mask] = mean
    t_img_data[mask] = t_obs
    p_img_data[mask] = p_fwe
    hdr = ref.header.copy()
    nib.save(nib.Nifti1Image(mean_img_data, ref.affine, hdr), OUT / "mean_effect.nii.gz")
    nib.save(nib.Nifti1Image(t_img_data, ref.affine, hdr), OUT / "t_statistic.nii.gz")
    nib.save(nib.Nifti1Image(p_img_data, ref.affine, hdr), OUT / "p_fwe_maxT.nii.gz")
    nib.save(nib.Nifti1Image(mask_img_data, ref.affine, hdr), OUT / "common_brain_mask.nii.gz")

    sig = p_fwe < .05
    voxel_sizes = ref.header.get_zooms()[:3]
    voxel_vol = float(np.prod(voxel_sizes))
    flat_indices = np.flatnonzero(mask)
    rows = []
    for j in np.argsort(t_obs)[::-1][:20]:
        ijk = np.array(np.unravel_index(flat_indices[j], ref.shape))
        xyz = nib.affines.apply_affine(ref.affine, ijk).round(1)
        rows.append({"rank": len(rows)+1, "x": xyz[0], "y": xyz[1], "z": xyz[2],
                     "mean_effect": mean[j], "t": t_obs[j], "p_uncorrected": p_unc[j], "p_fwe": p_fwe[j]})
    pd.DataFrame(rows).to_csv(OUT / "top_voxels.csv", index=False)

    # Data QC summary and subject-level peak/mean checks, without outlier-based
    # exclusion; effect maps are cope estimates, not variance-normalized Z maps.
    subj = []
    for i, participant in enumerate(participants.participant_id):
        vals = X[i]
        subj.append({"participant_id": participant, "mean_in_mask": vals.mean(),
                     "sd_in_mask": vals.std(ddof=1), "max_abs_in_mask": np.max(np.abs(vals)),
                     "fraction_nonzero": float(np.mean(data[i] != 0))})
    pd.DataFrame(subj).to_csv(OUT / "participant_qc.csv", index=False)

    # Figure 1: unthresholded group mean for effect scale/context.
    mean_img = nib.Nifti1Image(mean_img_data, ref.affine, hdr)
    display = plotting.plot_stat_map(mean_img, display_mode="ortho", cut_coords=(0, 40, -8),
                                     threshold=0.05, cmap="cold_hot", symmetric_cbar=True,
                                     title="Mean gain effect estimate (cope units)",
                                     colorbar=True, output_file=str(FIG / "mean_effect.png"),
                                     black_bg=False)
    display.close()
    # Figure 2: whole-brain FWE-corrected positive evidence, if any.
    stat_img = nib.Nifti1Image(t_img_data, ref.affine, hdr)
    if sig.any():
        # Use t statistic for color, masking by maxT-adjusted p < .05.
        sig_img_data = np.zeros(ref.shape, dtype=np.float32)
        sig_img_data[mask] = np.where(sig, t_obs, 0)
        sig_img = nib.Nifti1Image(sig_img_data, ref.affine, hdr)
        display = plotting.plot_stat_map(sig_img, display_mode="ortho", cut_coords=(0, 40, -8),
                                         threshold=0, cmap="inferno", title="Positive effects, whole-brain max-T FWE p < .05",
                                         colorbar=True, output_file=str(FIG / "positive_fwe.png"), black_bg=False)
        display.close()
    else:
        display = plotting.plot_stat_map(stat_img, display_mode="ortho", cut_coords=(0, 40, -8),
                                         threshold=0, cmap="cold_hot", symmetric_cbar=True,
                                         title="No voxels pass whole-brain max-T FWE p < .05",
                                         colorbar=True, output_file=str(FIG / "t_map_unthresholded.png"), black_bg=False)
        display.close()

    # QC figure: distribution of individual means and SD across common mask.
    q = pd.DataFrame(subj)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(q.mean_in_mask, q.sd_in_mask, s=28, alpha=.8)
    ax.set(xlabel="Participant mean cope in common mask", ylabel="Within-map SD of cope",
           title="Participant map QC (all 54 included)")
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(FIG / "participant_qc.png", dpi=180)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axhline(0, color="0.45", lw=1, ls="--")
    ax.scatter(np.ones(n) + rng.normal(0, .035, n), roi_values, s=26, alpha=.75)
    ax.set(xlim=(.75, 1.25), xticks=[1], xticklabels=["vmPFC sphere\n(2, 46, −8; r=10 mm)"],
           ylabel="Participant mean gain cope", title="Descriptive vmPFC effect estimates")
    ax.grid(axis="y", alpha=.2)
    fig.tight_layout()
    fig.savefig(FIG / "vmpfc_effects.png", dpi=180)
    plt.close(fig)

    result = {
        "n_participants": n, "n_voxels": int(v), "mask_rule": "nonzero finite in all 54 participants (strict intersection)",
        "voxel_size_mm": list(map(float, voxel_sizes)), "n_permutations": N_PERM,
        "rng_seed": SEED, "test": "one-sided one-sample sign-flip max-t permutation",
        "familywise_correction": "max t over all common-coverage brain-mask voxels",
        "n_voxels_fwe_p_lt_0_05": int(sig.sum()),
        "peak": rows[0], "peak_fwe_p": float(np.min(p_fwe)),
        "mean_effect_at_peak": float(mean[np.argmax(t_obs)]), "t_at_peak": float(np.max(t_obs)),
        "max_null_t_95": float(np.quantile(max_null, .95)),
        "subjects_excluded": [], "map_effect_mean_range": [float(np.min(data)), float(np.max(data))],
        "fraction_masked_per_map_median": float(np.median([np.mean(d == 0) for d in data])),
        "vmPFC_descriptive": {"sphere_center_MNI_mm": [2, 46, -8], "radius_mm": 10,
                              "n_voxels": int(roi.sum()), "mean_of_participant_roi_means": float(roi_values.mean()),
                              "participant_mean_95pct_t_CI": [float(roi_ci[0]), float(roi_ci[1])],
                              "whole_brain_adjusted_min_p_in_sphere": roi_pmin,
                              "significant_voxels_in_sphere": int(np.sum(sig & roi))},
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
