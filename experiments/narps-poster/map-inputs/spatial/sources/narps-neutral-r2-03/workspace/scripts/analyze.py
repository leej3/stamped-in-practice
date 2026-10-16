#!/usr/bin/env python3
"""Group analysis of AO86 equal-indifference gain cope maps.

The upstream participant models are fixed inputs. This script performs only
group-stage quality checks, one-sample inference, and visualization.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets, image, plotting
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
N_PERM = 9999
SEED = 20261016
BATCH = 100


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "figures").mkdir(exist_ok=True)
    source = json.loads((ROOT / "input/sources.json").read_text())
    participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
    ids = participants.participant_id.tolist()
    if len(ids) != 54 or len(ids) != len(set(ids)):
        raise RuntimeError("Expected 54 unique participant records")

    arrays = []
    ref = None
    checks = []
    for pid in ids:
        rel = f"data/{pid}_hypo1_cope.nii.gz"
        meta = source["files"][rel]
        path = ROOT / rel
        if path.stat().st_size != meta["bytes"] or sha256(path) != meta["sha256"]:
            raise RuntimeError(f"Provenance mismatch: {rel}")
        im = nib.load(path)
        if ref is None:
            ref = im
        elif im.shape != ref.shape or not np.allclose(im.affine, ref.affine, atol=1e-5):
            raise RuntimeError(f"Geometry mismatch: {rel}")
        x = im.get_fdata(dtype=np.float32)
        if not np.isfinite(x).all():
            raise RuntimeError(f"Non-finite voxel in {rel}")
        arrays.append(x)
        checks.append({"participant_id": pid, "bytes": path.stat().st_size,
                       "sha256_verified": True,
                       "nonzero_voxels": int(np.count_nonzero(x))})

    data = np.stack(arrays).astype(np.float32, copy=False)
    n = len(data)
    # Input maps are zero outside their individual estimation support. Use the
    # intersection of nonzero supports so every included voxel has estimates
    # for all 54 participants; zero-valued inside-brain estimates are rare and
    # therefore a small limitation of this support rule.
    support = data != 0
    mask = support.all(axis=0)
    if mask.sum() < 10000:
        raise RuntimeError("Unexpectedly small complete-case support mask")
    X = data[:, mask].astype(np.float64)
    means = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    t_obs = means / (sd / np.sqrt(n))
    p_unc = stats.t.sf(t_obs, df=n - 1)

    # One-sided whole-brain max-T sign-flip test. Sign flips are appropriate to
    # a one-sample null under exchangeability/symmetric errors. Studentize each
    # permutation, and use the maximum positive t over the complete support.
    rng = np.random.default_rng(SEED)
    ss = np.einsum("ij,ij->j", X, X)
    maxima = np.empty(N_PERM, dtype=np.float32)
    for start in range(0, N_PERM, BATCH):
        stop = min(start + BATCH, N_PERM)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(stop - start, n))
        sums = signs @ X
        den2 = np.maximum((ss[None, :] - sums * sums / n) / (n - 1) * n, 1e-15)
        t_perm = sums / np.sqrt(den2)
        maxima[start:stop] = t_perm.max(axis=1)
    maxima.sort()
    # Add-one correction gives valid Monte Carlo p-values and avoids zeroes.
    ranks = np.searchsorted(maxima, t_obs, side="left")
    p_fwe = (1 + N_PERM - ranks) / (N_PERM + 1)

    mean_img_data = np.zeros(ref.shape, dtype=np.float32)
    t_img_data = np.zeros(ref.shape, dtype=np.float32)
    pfwe_img_data = np.ones(ref.shape, dtype=np.float32)
    mean_img_data[mask] = means
    t_img_data[mask] = t_obs
    pfwe_img_data[mask] = p_fwe
    mean_img = nib.Nifti1Image(mean_img_data, ref.affine, ref.header)
    t_img = nib.Nifti1Image(t_img_data, ref.affine, ref.header)
    p_img = nib.Nifti1Image(pfwe_img_data, ref.affine, ref.header)
    mask_img = nib.Nifti1Image(mask.astype(np.uint8), ref.affine, ref.header)
    nib.save(mean_img, ROOT / "results/group_mean_cope.nii.gz")
    nib.save(t_img, ROOT / "results/group_t_unthresholded.nii.gz")
    nib.save(p_img, ROOT / "results/group_p_fwe_maxT.nii.gz")
    nib.save(mask_img, ROOT / "results/group_common_support_mask.nii.gz")

    atlas = datasets.fetch_atlas_harvard_oxford(
        "cort-maxprob-thr25-2mm", data_dir=ROOT / "results/atlases", verbose=0)
    atlas_img = image.resample_to_img(atlas.maps, ref, interpolation="nearest")
    atlas_vol = atlas_img.get_fdata().astype(int)
    roi_names = ["Frontal Medial Cortex", "Subcallosal Cortex", "Frontal Orbital Cortex"]
    roi_ids = [atlas.labels.index(x) for x in roi_names]
    roi = np.isin(atlas_vol, roi_ids) & mask
    if not roi.any():
        raise RuntimeError("vmPFC proxy ROI does not overlap the common support")
    nib.save(nib.Nifti1Image(roi.astype(np.uint8), ref.affine, ref.header),
             ROOT / "results/vmPFC_anatomical_proxy_mask.nii.gz")
    roi_means = data[:, roi].mean(axis=1)
    roi_mean = float(roi_means.mean())
    roi_sd = float(roi_means.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_ci = stats.t.interval(0.95, n - 1, loc=roi_mean, scale=roi_se)
    roi_t, roi_p_one = stats.ttest_1samp(roi_means, popmean=0, alternative="greater")
    roi_p_two = stats.ttest_1samp(roi_means, popmean=0).pvalue
    roi_t_values = t_obs[roi[mask]]
    roi_pfwe_values = p_fwe[roi[mask]]
    # ROI summaries are descriptive and not used for the required whole-brain
    # decision; include uncorrected p only as context, not a confirmatory result.

    significant = np.flatnonzero(p_fwe < 0.05)
    peak_index = int(np.argmax(t_obs))
    flat_mask_indices = np.flatnonzero(mask)
    peak_ijk = np.array(np.unravel_index(flat_mask_indices[peak_index], ref.shape))
    peak_coord = nib.affines.apply_affine(ref.affine, peak_ijk)
    desc = {
        "n_participants": n,
        "n_excluded": 0,
        "exclusions": [],
        "checksums_and_geometry": checks,
        "image_shape": list(ref.shape),
        "voxel_size_mm": [float(x) for x in nib.affines.voxel_sizes(ref.affine)],
        "common_support_voxels": int(mask.sum()),
        "support_union_voxels": int(support.any(axis=0).sum()),
        "support_intersection_fraction_of_union": float(mask.sum() / support.any(axis=0).sum()),
        "whole_brain_inference": {
            "method": "one-sample one-sided sign-flip permutation max-T",
            "permutations": N_PERM,
            "seed": SEED,
            "familywise_alpha": 0.05,
            "significant_voxels_positive": int(len(significant)),
            "minimum_corrected_p": float(p_fwe.min()),
            "peak_t": float(t_obs[peak_index]),
            "peak_mean_cope": float(means[peak_index]),
            "peak_mni_mm": [float(c) for c in peak_coord],
            "peak_uncorrected_one_sided_p": float(p_unc[peak_index]),
            "peak_maxT_fwe_p": float(p_fwe[peak_index]),
            "critical_maxT_t_95": float(np.quantile(maxima, 0.95, method="higher")),
        },
        "vmPFC_anatomical_proxy": {
            "atlas": "Harvard-Oxford cortical atlas, max-probability, 25% threshold, 2 mm",
            "regions": roi_names,
            "voxel_count_in_common_support": int(roi.sum()),
            "participant_mean_cope_mean": roi_mean,
            "participant_mean_cope_sd": roi_sd,
            "participant_mean_cope_ci95_t": [float(roi_ci[0]), float(roi_ci[1])],
            "one_sided_unadjusted_p_descriptive_only": float(roi_p_one),
            "two_sided_unadjusted_p_descriptive_only": float(roi_p_two),
            "mean_of_participants_mean_t": float(roi_t),
            "maximum_voxel_t": float(roi_t_values.max()),
            "minimum_whole_brain_FWE_p": float(roi_pfwe_values.min()),
            "positive_voxels_with_whole_brain_FWE_p_below_0.05": int((roi_pfwe_values < .05).sum()),
        },
        "cohort_age_mean_sd": [float(participants.age.mean()), float(participants.age.std(ddof=1))],
        "cohort_gender_counts": {str(k): int(v) for k, v in participants.gender.value_counts().items()},
        "software": {"numpy": np.__version__, "nibabel": nib.__version__,
                     "nilearn": __import__("nilearn").__version__},
    }
    (ROOT / "results/summary.json").write_text(json.dumps(desc, indent=2) + "\n")
    pd.DataFrame({"participant_id": ids, "mean_cope_in_vmPFC_proxy": roi_means}).to_csv(
        ROOT / "results/vmPFC_proxy_participant_means.csv", index=False)
    pd.DataFrame(checks).to_csv(ROOT / "results/input_quality_checks.csv", index=False)

    # Figure 1: spatial group effect and unthresholded evidence, with the
    # anatomical proxy outlined; right plot reports corrected evidence.
    roi_img = nib.Nifti1Image(roi.astype(np.uint8), ref.affine)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), constrained_layout=True)
    display = plotting.plot_stat_map(mean_img, bg_img=None, display_mode="x", cut_coords=[0],
                           threshold=0, cmap="RdBu_r", colorbar=True,
                           title=None, axes=axes[0],
                           black_bg=False, vmin=-0.20, vmax=0.20)
    display.add_contours(roi_img, levels=[.5], colors="black", linewidths=1)
    plotting.plot_stat_map(t_img, bg_img=None, display_mode="x", cut_coords=[0],
                           threshold=0, cmap="RdBu_r", colorbar=True,
                           title=None, axes=axes[1],
                           black_bg=False, vmin=-4, vmax=4)
    axes[0].set_title("Mean gain cope (effect estimate)")
    axes[1].set_title("Unthresholded one-sample t")
    p_sig = np.zeros(ref.shape, dtype=np.float32)
    p_sig[mask] = np.where(p_fwe < .05, t_obs, 0)
    sig_img = nib.Nifti1Image(p_sig, ref.affine)
    plotting.plot_stat_map(sig_img, bg_img=None, display_mode="x", cut_coords=[float(peak_coord[0])],
                           threshold=0, cmap="Reds", colorbar=True,
                           title=None,
                           axes=axes[2], black_bg=False)
    axes[2].set_title("Whole-brain FWE p < .05\npeak sagittal slice")
    fig.suptitle("NARPS Hypothesis 1 — equal-indifference group (n=54)", fontsize=14)
    fig.savefig(ROOT / "figures/group_maps.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.4), constrained_layout=True)
    x = np.arange(1, n + 1)
    ax.scatter(x, roi_means, s=24, color="#356b91", alpha=.8, edgecolor="white", linewidth=.3)
    ax.axhline(0, color="black", lw=1, ls="--")
    ax.axhline(roi_mean, color="#b3473f", lw=2, label="Group mean")
    ax.fill_between([0, n + 1], roi_ci[0], roi_ci[1], color="#b3473f", alpha=.14,
                    label="95% t interval")
    ax.set(xlim=(0, n + 1), xlabel="Participant (source order)",
           ylabel="Mean gain cope within vmPFC anatomical proxy",
           title="Participant-level ROI summaries (descriptive)")
    ax.legend(frameon=False)
    fig.savefig(ROOT / "figures/vmPFC_participant_means.png", dpi=180)
    plt.close(fig)

    print(json.dumps(desc["whole_brain_inference"], indent=2))
    print(json.dumps(desc["vmPFC_anatomical_proxy"], indent=2))


if __name__ == "__main__":
    main()
