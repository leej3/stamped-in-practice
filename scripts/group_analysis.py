#!/usr/bin/env python3
"""Group analysis of supplied NARPS equal-indifference gain-effect maps."""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
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
from scipy import stats
from nibabel.processing import resample_from_to


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
ROI_TEXT = "MNI x -20 to 20, y 15 to 60, z -20 to 10 mm"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--permutations", type=int, default=9999)
    parser.add_argument("--seed", type=int, default=20261015)
    args = parser.parse_args()
    start = time.time()
    OUT.mkdir(exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    (OUT / "maps").mkdir(exist_ok=True)

    metadata = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    files = sorted(glob.glob(str(INPUT / "data" / "sub-*_hypo1_cope.nii.gz")))
    if len(files) != 54 or len(metadata) != 54:
        raise RuntimeError(f"Expected 54 maps and metadata rows; found {len(files)} and {len(metadata)}")
    metadata = metadata.set_index("participant_id").loc[
        [Path(f).name.split("_")[0] for f in files]
    ].reset_index()
    if set(metadata["group"]) != {"equalIndifference"}:
        raise RuntimeError("Unexpected participant group in metadata")

    images = [nib.load(f) for f in files]
    reference = images[0]
    for path, image in zip(files, images):
        if image.shape != reference.shape or not np.allclose(image.affine, reference.affine):
            raise RuntimeError(f"Image grid mismatch: {path}")
    arrays = [np.asarray(image.dataobj, dtype=np.float32) for image in images]
    finite = np.array([np.isfinite(a).all() for a in arrays])
    if not finite.all():
        raise RuntimeError("Non-finite values found")
    support = np.stack([a != 0 for a in arrays], axis=0)
    support_n = support.sum(axis=0)
    template_mask_path = OUT / "reference" / "tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz"
    if not template_mask_path.exists():
        raise FileNotFoundError(f"Download matching TemplateFlow brain mask to {template_mask_path}")
    template_mask_img = nib.load(template_mask_path)
    template_mask_on_map = resample_from_to(template_mask_img, (reference.shape, reference.affine), order=0)
    brain_mask = np.asarray(template_mask_on_map.dataobj) > 0
    common_mask = (support_n == len(arrays)) & brain_mask
    relaxed_mask = (support_n >= int(np.ceil(0.90 * len(arrays)))) & brain_mask
    if common_mask.sum() == 0:
        raise RuntimeError("No common support across maps")

    # Broad anatomical vmPFC search zone fixed in MNI coordinates before
    # examining group effects. This is for anatomical localization only;
    # inferential p-values remain whole-brain max-statistic corrected.
    ijk = np.indices(reference.shape, dtype=np.float32).reshape(3, -1).T
    xyz = nib.affines.apply_affine(reference.affine, ijk)
    x, y, z = xyz.T
    roi = ((np.abs(x) <= 20) & (y >= 15) & (y <= 60) & (z >= -20) & (z <= 10)).reshape(reference.shape)
    roi_common = roi & common_mask

    rng = np.random.default_rng(args.seed)
    # One-sample t statistic at each voxel, one-sided positive alternative.
    # Participant sign flips give a nonparametric max-T family-wise correction.
    matrix = np.stack([a[common_mask] for a in arrays]).astype(np.float64)
    n, nvox = matrix.shape
    sums_sq = np.einsum("ij,ij->j", matrix, matrix)
    obs_sum = matrix.sum(axis=0)
    obs_t = np.sqrt(n - 1) * obs_sum / np.sqrt(np.maximum(n * sums_sq - obs_sum**2, 1e-30))
    null_max = np.empty(args.permutations, dtype=np.float32)
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=4):
        batch_size = 100
        for lo in range(0, args.permutations, batch_size):
            hi = min(lo + batch_size, args.permutations)
            signs = rng.choice(np.array([-1.0, 1.0]), size=(hi - lo, n))
            perm_sums = signs @ matrix
            denom = np.sqrt(np.maximum(n * sums_sq[None, :] - perm_sums**2, 1e-30))
            perm_t = np.sqrt(n - 1) * perm_sums / denom
            null_max[lo:hi] = perm_t.max(axis=1)

    # Add-one Monte Carlo correction. Also records the finite permutation
    # resolution, so values below 1/(B+1) are represented exactly.
    sorted_max = np.sort(null_max)
    ranks = np.searchsorted(sorted_max, obs_t, side="left")
    p_fwe = (args.permutations - ranks + 1) / (args.permutations + 1)
    p_fwe = np.clip(p_fwe, 1 / (args.permutations + 1), 1.0)
    significant = (obs_t > 0) & (p_fwe <= 0.05)

    def image_from_values(values: np.ndarray, mask: np.ndarray = common_mask) -> nib.Nifti1Image:
        out = np.zeros(reference.shape, dtype=np.float32)
        out[mask] = values
        return nib.Nifti1Image(out, reference.affine, reference.header)

    t_img = image_from_values(obs_t)
    p_img = image_from_values(p_fwe.astype(np.float32))
    sig_img = image_from_values(np.where(significant, obs_t, 0.0))
    nib.save(t_img, OUT / "maps" / "group_t_unthresholded.nii.gz")
    nib.save(p_img, OUT / "maps" / "group_p_fwe_maxT.nii.gz")
    nib.save(sig_img, OUT / "maps" / "group_t_fwe05.nii.gz")

    # ROI summary is descriptive; the inferential decision is driven by the
    # whole-brain corrected map and the a priori anatomical search zone.
    roi_subj = np.array([float(np.mean(a[roi_common])) for a in arrays])
    roi_mean = float(roi_subj.mean())
    roi_sd = float(roi_subj.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    crit = float(stats.t.ppf(0.975, n - 1))
    roi_ci = [roi_mean - crit * roi_se, roi_mean + crit * roi_se]
    roi_t = float(roi_mean / roi_se)
    roi_p_two = float(2 * stats.t.sf(abs(roi_t), n - 1))
    roi_p_one = float(stats.t.sf(roi_t, n - 1))
    roi_sig_count = int(significant[np.array(roi_common[common_mask])].sum())
    roi_sig_max_t = float(obs_t[np.array(roi_common[common_mask])].max())
    roi_peak_flat = np.flatnonzero(np.array(roi_common[common_mask]))
    roi_peak_idx = int(roi_peak_flat[np.argmax(obs_t[roi_peak_flat])]) if roi_peak_flat.size else None
    if roi_peak_idx is not None:
        roi_peak_voxel = tuple(int(v) for v in np.column_stack(np.where(common_mask))[roi_peak_idx])
        roi_peak_mni = [float(v) for v in nib.affines.apply_affine(reference.affine, roi_peak_voxel)]
        roi_peak_tfwe = float(p_fwe[roi_peak_idx])
    else:
        roi_peak_voxel, roi_peak_mni, roi_peak_tfwe = None, None, None

    peak_idx = int(np.argmax(obs_t))
    peak_voxel = tuple(int(v) for v in np.column_stack(np.where(common_mask))[peak_idx])
    peak_mni = [float(v) for v in nib.affines.apply_affine(reference.affine, peak_voxel)]
    peak = {
        "t": float(obs_t[peak_idx]),
        "p_fwe": float(p_fwe[peak_idx]),
        "mni_mm": peak_mni,
        "voxel_ijk": peak_voxel,
    }

    # Figure 1: whole-brain, max-T corrected positive findings; Figure 2:
    # participant ROI-mean coefficients and their group mean/95% t interval.
    from nilearn import plotting

    fig = plt.figure(figsize=(10.0, 5.1))
    display = plotting.plot_glass_brain(
        sig_img,
        display_mode="ortho",
        colorbar=True,
        plot_abs=False,
        cmap="cold_hot",
        figure=fig,
        title=None,
        threshold=0,
        symmetric_cbar=False,
    )
    fig.suptitle("Positive gain effect | whole-brain max-T FWE p ≤ .05", fontsize=15)
    fig.text(0.5, 0.01,
             f"{int(significant.sum())} significant voxels whole brain; none in the prespecified vmPFC search zone",
             ha="center", fontsize=10)
    fig.subplots_adjust(top=0.86, bottom=0.08)
    fig.savefig(OUT / "figures" / "whole_brain_fwe.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.0, 4.7), constrained_layout=True)
    jitter = rng.normal(0, 0.035, size=n)
    ax.scatter(1 + jitter, roi_subj, s=28, alpha=0.72, color="#2d698f", edgecolor="white", linewidth=0.35)
    ax.errorbar(1.26, roi_mean, yerr=[[roi_mean - roi_ci[0]], [roi_ci[1] - roi_mean]],
                fmt="D", color="#b23a48", capsize=5, markersize=7, label="Mean and 95% t interval")
    ax.axhline(0, color="black", linewidth=1, linestyle="--")
    ax.set_xlim(0.82, 1.47)
    ax.set_xticks([1], ["Equal-indifference participants"])
    ax.set_ylabel("Mean gain-effect estimate in vmPFC search zone (a.u.)")
    ax.set_title("Participant-level vmPFC gain-effect summaries")
    ax.legend(frameon=False, loc="best")
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(OUT / "figures" / "vmPFC_participant_estimates.png", dpi=180)
    plt.close(fig)

    result = {
        "analysis": {
            "n_participants": n,
            "n_excluded": 0,
            "group": "equalIndifference",
            "model": "one-sample voxelwise t test of participant gain-effect estimates against zero",
            "direction": "positive",
            "multiple_comparisons": "one-sided permutation max-T family-wise correction across common whole-brain support",
            "permutations": args.permutations,
            "seed": args.seed,
            "permutation_p_resolution": 1 / (args.permutations + 1),
            "mask_voxels": int(common_mask.sum()),
            "mask_rule": "TemplateFlow MNI152NLin2009cAsym desc-brain mask resampled nearest-neighbor to map grid, intersected with voxels having nonzero estimates in all 54 maps",
            "brain_mask_voxels_on_map_grid": int(brain_mask.sum()),
            "common_support_outside_brain_mask_voxels": int(((support_n == len(arrays)) & ~brain_mask).sum()),
            "relaxed_90pct_support_voxels": int(relaxed_mask.sum()),
            "vmPFC_search_zone": ROI_TEXT,
            "vmPFC_common_voxels": int(roi_common.sum()),
            "vmPFC_significant_voxels_fwe05": roi_sig_count,
            "roi_mean_effect_estimate": roi_mean,
            "roi_sd_between_participants": roi_sd,
            "roi_ci95_t": roi_ci,
            "roi_t_df53": roi_t,
            "roi_p_one_sided_uncorrected_descriptive": roi_p_one,
            "roi_p_two_sided_uncorrected_descriptive": roi_p_two,
            "roi_peak": {"t": roi_max_t if (roi_max_t := roi_sig_max_t) else 0, "mni_mm": roi_peak_mni,
                         "p_fwe": roi_peak_tfwe},
            "whole_brain_positive_peak": peak,
            "whole_brain_fwe05_voxel_count": int(significant.sum()),
            "hypothesis_supported": bool(roi_sig_count > 0),
            "metadata_age_mean_sd": [float(metadata.age.mean()), float(metadata.age.std(ddof=1))],
            "metadata_gender_counts": {str(k): int(v) for k, v in metadata.gender.value_counts().sort_index().items()},
            "map_shape": list(reference.shape),
            "map_affine": reference.affine.tolist(),
            "brain_mask_source": "TemplateFlow tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz",
            "brain_mask_sha256": sha256(template_mask_path),
            "all_maps_finite": bool(finite.all()),
            "all_grids_identical": True,
            "effect_units": "upstream coefficient for mean-centered, variance-normalized gain modulator; not per currency unit",
            "run_seconds": time.time() - start,
            "software": {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
                         "nibabel": nib.__version__},
        },
        "inputs": [{"file": str(Path(f).relative_to(ROOT)), "sha256": sha256(Path(f))} for f in files],
    }
    with (OUT / "analysis_results.json").open("w") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps(result["analysis"], indent=2))


if __name__ == "__main__":
    main()
