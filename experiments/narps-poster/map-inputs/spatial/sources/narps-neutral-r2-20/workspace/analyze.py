#!/usr/bin/env python3
"""Group analysis of fixed NARPS AO86 participant gain-effect maps."""
from __future__ import annotations

import json
import hashlib
import platform
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets, image, plotting
from scipy import stats
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
FIG = OUT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
N_PERM = 9999
SEED = 20261016


def save_nifti(data, ref, path, dtype=np.float32):
    img = nib.Nifti1Image(np.asarray(data, dtype=dtype), ref.affine, ref.header)
    img.set_data_dtype(dtype)
    nib.save(img, str(path))


def main():
    manifest = json.loads((ROOT / "input/sources.json").read_text())
    meta = manifest["files"]
    pids = [v["participant_id"] for k, v in meta.items() if k.startswith("data/")]
    participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
    assert set(pids) == set(participants.participant_id)
    imgs, arrays, checks = [], [], []
    for pid in pids:
        rel = f"data/{pid}_hypo1_cope.nii.gz"
        path = ROOT / "input" / rel
        raw = path.read_bytes()
        spec = meta[rel]
        digest = hashlib.sha256(raw).hexdigest()
        if len(raw) != spec["bytes"] or digest != spec["sha256"]:
            raise ValueError(f"Source integrity check failed: {rel}")
        img = nib.load(str(path))
        imgs.append(img)
        arrays.append(img.get_fdata(dtype=np.float32))
        checks.append({"participant_id": pid, "bytes": len(raw), "sha256": digest,
                       "shape": "x".join(map(str, img.shape)),
                       "nonzero_voxels": int(np.count_nonzero(arrays[-1])),
                       "finite": bool(np.isfinite(arrays[-1]).all())})

    ref = imgs[0]
    for im in imgs[1:]:
        if im.shape != ref.shape or not np.allclose(im.affine, ref.affine):
            raise ValueError("Participant image geometry differs")
    if not all(x["finite"] for x in checks):
        raise ValueError("Non-finite participant map values found")

    # Zeros encode locations outside the participant's supplied estimation mask.
    # The intersection supplies an identical whole-brain search space for all n.
    masks = np.stack([a != 0 for a in arrays])
    common = masks.all(axis=0)
    union = masks.any(axis=0)
    if common.sum() == 0:
        raise ValueError("No common valid voxels")
    Y = np.stack([a[common] for a in arrays]).astype(np.float32)
    n, v = Y.shape
    mean = Y.mean(axis=0, dtype=np.float64)
    sd = Y.std(axis=0, ddof=1, dtype=np.float64)
    t_obs = mean / (sd / np.sqrt(n))
    df = n - 1
    p_unc = stats.t.sf(t_obs, df)

    # One-sided sign-flip max-T permutation. The max is over the complete
    # common-brain search mask; a +1 correction gives valid Monte Carlo p-values.
    rng = np.random.default_rng(SEED)
    max_t = np.empty(N_PERM, dtype=np.float32)
    sumsq = np.sum(Y.astype(np.float64) ** 2, axis=0)
    batch = 128
    for start in range(0, N_PERM, batch):
        b = min(batch, N_PERM - start)
        signs = rng.choice(np.array([-1., 1.], dtype=np.float32), size=(b, n))
        sums = signs @ Y
        m = sums / n
        variance = (sumsq[None, :] - sums.astype(np.float64) ** 2 / n) / (n - 1)
        ts = m / np.sqrt(np.maximum(variance, 1e-15) / n)
        max_t[start:start+b] = ts.max(axis=1)
    sorted_max = np.sort(max_t)
    # FWE adjusted p per voxel, with inclusive tail and finite-sample correction.
    n_ge = N_PERM - np.searchsorted(sorted_max, t_obs, side="left")
    p_fwe = (n_ge + 1) / (N_PERM + 1)
    sig = p_fwe <= .05

    mean_img = np.zeros(ref.shape, np.float32); mean_img[common] = mean
    t_img = np.zeros(ref.shape, np.float32); t_img[common] = t_obs
    fwe_img = np.ones(ref.shape, np.float32); fwe_img[common] = p_fwe
    sig_img = np.zeros(ref.shape, np.uint8); sig_img[common] = sig.astype(np.uint8)
    save_nifti(mean_img, ref, OUT / "group_mean_effect.nii.gz")
    save_nifti(t_img, ref, OUT / "group_t_map.nii.gz")
    save_nifti(fwe_img, ref, OUT / "fwe_p_map.nii.gz")
    save_nifti(common.astype(np.uint8), ref, OUT / "common_brain_mask.nii.gz", np.uint8)
    save_nifti(sig_img, ref, OUT / "fwe_significant_mask.nii.gz", np.uint8)

    # Independent atlas proxy for vmPFC: the frontal medial and subcallosal
    # Harvard-Oxford cortical parcels; broad and imperfect anatomical proxy.
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    labels = list(atlas.labels)
    roi_labels = ["Frontal Medial Cortex", "Subcallosal Cortex"]
    roi_indices = [labels.index(x) for x in roi_labels]
    atlas_on_ref = image.resample_to_img(atlas.maps, ref, interpolation="nearest")
    atlas_data = atlas_on_ref.get_fdata().astype(int)
    roi = np.isin(atlas_data, roi_indices) & common
    if roi.sum() == 0:
        raise ValueError("vmPFC atlas proxy has no common voxels")
    save_nifti(roi.astype(np.uint8), ref, OUT / "vmPFC_HO_proxy_mask.nii.gz", np.uint8)
    roi_values = np.stack([a[roi].mean(dtype=np.float64) for a in arrays])
    roi_mean = roi_values.mean()
    roi_sd = roi_values.std(ddof=1)
    roi_se = roi_sd / np.sqrt(n)
    t_roi = roi_mean / roi_se
    ci = stats.t.interval(.95, df, loc=roi_mean, scale=roi_se)
    p_roi_one = stats.t.sf(t_roi, df)
    p_roi_two = stats.t.sf(abs(t_roi), df) * 2
    roi_positions = np.flatnonzero(roi[common])
    roi_peak_index = int(roi_positions[np.argmax(t_obs[roi_positions])])
    roi_peak_ijk = np.unravel_index(np.flatnonzero(common)[roi_peak_index], ref.shape)
    roi_peak_xyz = nib.affines.apply_affine(ref.affine, roi_peak_ijk)
    roi_peak_fwe = float(p_fwe[roi_peak_index])
    peak_ijk = np.unravel_index(np.flatnonzero(common)[int(t_obs.argmax())], ref.shape)
    peak_xyz = nib.affines.apply_affine(ref.affine, peak_ijk)
    peak_atlas_label = str(labels[int(atlas_data[peak_ijk])])
    # Robust check: subject-level ROI effect with one participant omitted at a time.
    loo = np.array([(np.delete(roi_values, i).mean(),
                     stats.ttest_1samp(np.delete(roi_values, i), 0, alternative="greater").statistic,
                     stats.ttest_1samp(np.delete(roi_values, i), 0, alternative="greater").pvalue)
                    for i in range(n)])

    pd.DataFrame(checks).to_csv(OUT / "input_qc.csv", index=False)
    pd.DataFrame({"participant_id": pids, "vmPFC_proxy_mean_effect": roi_values}).to_csv(
        OUT / "vmPFC_subject_effects.csv", index=False)
    # Voxelwise summary for reproducibility and mapping to thresholding.
    summary = {
        "n_participants": n, "n_voxels_common": int(common.sum()),
        "n_voxels_union": int(union.sum()),
        "common_fraction_of_union": float(common.sum()/union.sum()),
        "permutation": "one-sided sign-flip max-T, whole common-brain mask",
        "permutations": N_PERM, "seed": SEED, "familywise_alpha": 0.05,
        "minimum_attainable_fwe_p": 1/(N_PERM+1),
        "significant_voxels": int(sig.sum()),
        "max_observed_t": float(t_obs.max()),
        "max_observed_t_fwe_p": float(p_fwe[t_obs.argmax()]),
        "max_observed_t_xyz_mm": [float(x) for x in peak_xyz],
        "max_observed_t_atlas_label": peak_atlas_label,
        "max_observed_t_uncorrected_p": float(p_unc[t_obs.argmax()]),
        "roi_definition": "Harvard-Oxford cortical maxprob thr25 Frontal Medial Cortex + Subcallosal Cortex",
        "roi_voxels": int(roi.sum()), "roi_subject_mean": float(roi_mean),
        "roi_subject_sd": float(roi_sd), "roi_se": float(roi_se),
        "roi_95ci": [float(ci[0]), float(ci[1])], "roi_t": float(t_roi),
        "roi_df": df, "roi_p_one_sided_unadjusted": float(p_roi_one),
        "roi_p_two_sided_unadjusted": float(p_roi_two),
        "roi_significant_voxels_fwe": int(np.count_nonzero(sig[roi_positions])),
        "roi_max_t": float(t_obs[roi_peak_index]),
        "roi_max_t_xyz_mm": [float(x) for x in roi_peak_xyz],
        "roi_max_t_fwe_p": roi_peak_fwe,
        "roi_loo_mean_range": [float(loo[:,0].min()), float(loo[:,0].max())],
        "roi_loo_t_range": [float(loo[:,1].min()), float(loo[:,1].max())],
        "roi_loo_one_sided_p_range": [float(loo[:,2].min()), float(loo[:,2].max())],
        "software": {"python": platform.python_version(), "numpy": np.__version__,
                     "nibabel": nib.__version__}
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Figure 1: unthresholded group mean effect with atlas proxy outline.
    roi_img = nib.Nifti1Image(roi.astype(np.uint8), ref.affine)
    bg = datasets.load_mni152_template(resolution=2)
    disp = plotting.plot_anat(bg, display_mode="ortho", cut_coords=(0, 28, -10),
                              title="Mean gain effect estimate (unthresholded)",
                              colorbar=False, black_bg=False)
    disp.add_overlay(nib.Nifti1Image(mean_img, ref.affine), cmap="cold_hot",
                     colorbar=True, transparency=.8)
    disp.add_contours(roi_img, levels=[.5], colors="white", linewidths=1.0)
    disp.savefig(FIG / "group_mean_orthogonal.png", dpi=180)
    disp.close()

    # vmPFC ROI estimate and individual variation. Effect units inherit upstream
    # centered/variance-normalized gain regressor scaling.
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    rng_plot = np.random.default_rng(44)
    ax.scatter(rng_plot.normal(0, .045, n), roi_values, s=25, alpha=.7,
               color="#356b8c", edgecolor="white", linewidth=.35)
    ax.errorbar(0, roi_mean, yerr=[[roi_mean-ci[0]], [ci[1]-roi_mean]],
                fmt="D", color="#ba4a38", capsize=5, markersize=7,
                label="Group mean and 95% t interval")
    ax.axhline(0, color="black", lw=1)
    ax.set(xlim=(-.25,.25), xticks=[0], xticklabels=["All participants"],
           ylabel="Mean participant effect in vmPFC proxy",
           title="Participant-level ROI effect estimates")
    ax.legend(frameon=False, loc="best")
    ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / "vmPFC_roi_estimates.png", dpi=180); plt.close(fig)

    # Orthogonal views of whole-brain corrected p map; no thresholded voxels
    # are shown when the max-T test has no discoveries.
    if sig.any():
        plotvol = np.zeros(ref.shape, np.float32); plotvol[common] = np.where(sig, t_obs, 0)
        disp = plotting.plot_anat(bg, display_mode="ortho", cut_coords=(-26, -102, -4),
                                  title="Positive voxels surviving whole-brain max-T correction",
                                  colorbar=False, black_bg=False)
        disp.add_overlay(nib.Nifti1Image(plotvol, ref.affine), cmap="cold_hot",
                         colorbar=True, transparency=.95, threshold=0)
        disp.savefig(FIG / "whole_brain_fwe.png", dpi=180)
        disp.close()
    else:
        fig, ax = plt.subplots(figsize=(8,3.4)); ax.axis("off")
        ax.text(.5,.66,"No voxel passed whole-brain max-T FWE correction (α = .05)",
                ha="center",va="center",fontsize=14)
        ax.text(.5,.38,f"Maximum t = {t_obs.max():.2f}; FWE p = {p_fwe[t_obs.argmax()]:.4f}",
                ha="center",va="center",fontsize=12)
        fig.savefig(FIG / "whole_brain_fwe.png", dpi=180, bbox_inches="tight"); plt.close(fig)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
