#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference gain effect maps.

Inference is a one-sided, one-sample sign-flip permutation t test with a
whole-brain maximum-statistic familywise correction. Inputs are fixed
participant-level cope maps; this script does not refit first-level models.
"""
from pathlib import Path
import json
import sys

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from nilearn import datasets, image, plotting
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
FIG = OUT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
N_PERM = 10_000
SEED = 20261016
ALPHA = 0.05


def save_nii(data, ref, path, dtype=np.float32):
    im = nib.Nifti1Image(np.asarray(data, dtype=dtype), ref.affine, ref.header)
    im.set_data_dtype(dtype)
    nib.save(im, path)


def main():
    participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
    files = sorted((ROOT / "input/data").glob("sub-*_hypo1_cope.nii.gz"))
    file_ids = [p.name.split("_")[0] for p in files]
    assert len(files) == 54 and len(set(file_ids)) == 54
    assert set(file_ids) == set(participants.participant_id)
    participants = participants.set_index("participant_id").loc[file_ids].reset_index()

    imgs = [nib.load(str(p)) for p in files]
    ref = imgs[0]
    assert all(img.shape == ref.shape and np.allclose(img.affine, ref.affine) for img in imgs)
    data = np.stack([np.asarray(img.dataobj, dtype=np.float32) for img in imgs])
    assert np.isfinite(data).all()
    # These cope maps use exact zeros outside the estimated brain/field mask.
    # Use the intersection of nonzero voxels so every participant contributes
    # to every voxel, and intersect with a standard MNI brain mask.
    observed_coverage = np.all(np.isfinite(data) & (data != 0), axis=0)
    standard_mask = datasets.load_mni152_brain_mask(resolution=2)
    standard_mask = image.resample_to_img(standard_mask, ref, interpolation="nearest")
    mask = observed_coverage & (np.asarray(standard_mask.dataobj) > 0)
    assert mask.sum() > 20_000
    X = data[:, mask].astype(np.float64, copy=False)
    n, v = X.shape

    # QC without outcome-dependent exclusions.
    qc = participants.copy()
    qc["map_file"] = [p.name for p in files]
    qc["nonzero_voxels"] = [int(np.count_nonzero(d)) for d in data]
    qc["brain_mask_mean"] = X.mean(axis=1)
    qc["brain_mask_sd"] = X.std(axis=1, ddof=1)
    qc["brain_mask_median"] = np.median(X, axis=1)
    qc["global_mean_z"] = stats.zscore(qc.brain_mask_mean, ddof=1)
    qc.to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)

    # Observed one-sample t statistic for positive mean cope.
    sums = X.sum(axis=0)
    sumsq = np.square(X).sum(axis=0)
    centered_ss = np.maximum(sumsq - sums * sums / n, 0)
    se = np.sqrt(centered_ss / (n - 1) / n)
    mean = sums / n
    t_obs = np.divide(mean, se, out=np.zeros_like(mean), where=se > 0)

    # Sign-flip the participant maps under the one-sample null; use the maximum
    # positive t over all tested voxels for one-sided whole-brain FWE control.
    rng = np.random.default_rng(SEED)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n))
    max_t = np.full(N_PERM, -np.inf, dtype=np.float64)
    chunk_size = 1800
    for start in range(0, v, chunk_size):
        stop = min(start + chunk_size, v)
        chunk = X[:, start:stop]
        ss = np.square(chunk).sum(axis=0)
        t_perm = signs @ chunk
        den_perm = np.sqrt(np.maximum(ss[None, :] - t_perm * t_perm / n, 0) / (n - 1) / n)
        t_perm = np.divide(t_perm, den_perm, out=np.zeros_like(t_perm), where=den_perm > 0)
        max_t = np.maximum(max_t, np.max(t_perm, axis=1))

    p_fwe = (1 + np.sum(max_t[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)
    sig = p_fwe <= ALPHA
    threshold = float(np.quantile(max_t, 1 - ALPHA, method="higher"))
    # Transparent parametric sensitivity: one-sample t map with conservative
    # Bonferroni correction over the same whole-brain mask.
    p_param = stats.t.sf(t_obs, n - 1)
    p_bonf = np.minimum(1, p_param * v)

    t_vol = np.zeros(mask.shape, np.float32)
    p_vol = np.ones(mask.shape, np.float32)
    mean_vol = np.zeros(mask.shape, np.float32)
    t_vol[mask], p_vol[mask], mean_vol[mask] = t_obs, p_fwe, mean
    save_nii(t_vol, ref, OUT / "group_t_map.nii.gz")
    save_nii(p_vol, ref, OUT / "group_p_fwe_map.nii.gz")
    save_nii(mean_vol, ref, OUT / "group_mean_cope_map.nii.gz")
    save_nii(np.where(p_vol <= ALPHA, t_vol, 0), ref, OUT / "group_t_fwe05_map.nii.gz")
    p_bonf_vol = np.ones(mask.shape, np.float32)
    p_bonf_vol[mask] = p_bonf
    save_nii(p_bonf_vol, ref, OUT / "group_p_bonferroni_map.nii.gz")
    np.savetxt(OUT / "permutation_max_t.tsv", max_t, delimiter="\t", header="maximum_positive_t", comments="")

    # Atlas-based anatomical reference for vmPFC: Harvard-Oxford cortical
    # "Frontal Medial Cortex" (broad atlas parcel; used for localization only).
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    labels = list(atlas.labels)
    roi_idx = labels.index("Frontal Medial Cortex")
    atlas_img = image.resample_to_img(atlas.maps, ref, interpolation="nearest")
    roi = np.asarray(atlas_img.dataobj) == roi_idx
    roi &= mask
    roi_values = data[:, roi].mean(axis=1)
    roi_mean = float(roi_values.mean())
    roi_sd = float(roi_values.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_t = roi_mean / roi_se
    roi_p = float(stats.t.sf(roi_t, n - 1))
    roi_ci = stats.t.interval(0.95, n - 1, loc=roi_mean, scale=roi_se)
    roi_summary = {
        "roi": "Harvard-Oxford cortical atlas: Frontal Medial Cortex",
        "role": "anatomical localization only; primary support requires whole-brain FWE",
        "voxels": int(roi.sum()), "participants": n,
        "mean_cope": roi_mean, "sd_across_participant_roi_means": roi_sd,
        "ci95_low": float(roi_ci[0]), "ci95_high": float(roi_ci[1]),
        "t_one_sample": float(roi_t), "p_one_sided_unadjusted": roi_p,
    }
    (OUT / "vmPFC_roi_summary.json").write_text(json.dumps(roi_summary, indent=2) + "\n")
    pd.DataFrame({"participant_id": file_ids, "mean_cope_frontal_medial_cortex": roi_values}).to_csv(
        OUT / "vmPFC_roi_participants.tsv", sep="\t", index=False
    )

    # Compact whole-brain results and reproducibility metadata.
    observed_max = float(t_obs.max())
    max_idx = int(np.argmax(t_obs))
    coords = nib.affines.apply_affine(ref.affine, np.array(np.unravel_index(np.flatnonzero(mask)[max_idx], mask.shape)))
    summary = {
        "n_participants": n, "n_voxels_tested": int(v), "n_fwe_significant_positive": int(sig.sum()),
        "alpha_one_sided": ALPHA, "n_sign_flips": N_PERM, "random_seed": SEED,
        "max_t_fwe_critical": threshold, "max_observed_t": observed_max,
        "max_t_mni_mm": [float(q) for q in coords],
        "max_observed_t_fwe_p": float((1 + np.sum(max_t >= observed_max)) / (N_PERM + 1)),
        "smallest_possible_permutation_p": 1 / (N_PERM + 1),
        "parametric_bonferroni_sensitivity": {
            "method": "one-sample t test, one-sided, Bonferroni over all tested voxels",
            "n_significant_voxels": int(np.sum(p_bonf <= ALPHA)),
            "minimum_corrected_p": float(p_bonf.min()),
            "interpretation": "sensitivity analysis; normality of participant estimates is assumed",
        },
        "mask": "intersection of nonzero participant-map coverage and resampled MNI152 brain mask",
        "software": {
            "python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__,
            "scipy": __import__("scipy").__version__, "nibabel": nib.__version__,
            "nilearn": __import__("nilearn").__version__,
        },
        "roi": roi_summary,
        "exclusions": [],
    }
    (OUT / "analysis_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Figure 1: unthresholded whole-brain t map with atlas vmPFC outline;
    # the primary permutation-FWE result has no surviving voxels.
    fig = plt.figure(figsize=(12, 4.3))
    display = plotting.plot_stat_map(
        nib.Nifti1Image(t_vol, ref.affine),
        bg_img=datasets.load_mni152_template(resolution=2), display_mode="z",
        cut_coords=[-12, -4, 4, 12, 20], threshold=2,
        cmap="magma", colorbar=True, vmax=observed_max,
        title="Positive gain effect: unthresholded group t map (primary permutation-FWE: none)",
        figure=fig, black_bg=False,
    )
    display.add_contours(nib.Nifti1Image(roi.astype(np.uint8), ref.affine), levels=[0.5], colors="cyan", linewidths=1)
    fig.text(0.02, 0.01, "Cyan outline: Harvard–Oxford Frontal Medial Cortex anatomical proxy for vmPFC.", fontsize=8)
    fig.savefig(FIG / "whole_brain_fwe_vmPFC.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: participant-level atlas ROI mean cope estimates.
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    jitter = rng.normal(0, 0.035, n)
    ax.scatter(jitter, roi_values, s=26, alpha=0.72, color="#315a7d", edgecolor="white", linewidth=0.35)
    ax.errorbar(0, roi_mean, yerr=[[roi_mean - roi_ci[0]], [roi_ci[1] - roi_mean]],
                fmt="D", color="#c23b22", capsize=5, markersize=7, label="Mean and 95% t CI")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set(xlim=(-0.18, 0.18), xticks=[], ylabel="Participant mean cope within atlas parcel",
           title="vmPFC anatomical reference: Frontal Medial Cortex")
    ax.legend(frameon=False, loc="best")
    fig.tight_layout()
    fig.savefig(FIG / "vmPFC_roi_estimates.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
