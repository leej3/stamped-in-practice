#!/usr/bin/env python3
"""Group analysis of supplied AO86 NARPS Hypothesis 1 cope maps.

Primary inference: one-sample random-effects t test of participant cope maps
against zero, with one-sided whole-brain max-T sign-flip permutation FWE.
No upstream processing or individual model is rerun.
"""
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path

os.environ.setdefault("NILEARN_DATA", str(Path(__file__).resolve().parents[1] / ".cache" / "nilearn"))

import nibabel as nib
import numpy as np
import pandas as pd
import scipy
import nilearn
from scipy import stats, ndimage
from nilearn import datasets, image, plotting
from nilearn.masking import apply_mask, unmask
from threadpoolctl import threadpool_limits
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
DATA = INPUT / "data"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
N_PERM = 10000
SEED = 20261016


def main():
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    source_manifest = json.loads((INPUT / "sources.json").read_text())
    paths = sorted(DATA.glob("sub-*_hypo1_cope.nii.gz"))
    ids = [p.name.split("_")[0] for p in paths]
    assert len(paths) == 54 and ids == participants.participant_id.tolist(), "Map / participant roster mismatch"
    checksum_failures = []
    for p in paths:
        expected = source_manifest["files"][f"data/{p.name}"]["sha256"]
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != expected:
            checksum_failures.append(p.name)
    assert not checksum_failures, f"Source checksum mismatch: {checksum_failures}"

    imgs = [nib.load(str(p)) for p in paths]
    ref = imgs[0]
    assert all(im.shape == ref.shape and np.allclose(im.affine, ref.affine) for im in imgs)
    full = np.stack([im.get_fdata(dtype=np.float32) for im in imgs])
    finite = np.isfinite(full).all(axis=0)
    nonzero_n = np.count_nonzero(full != 0, axis=0)
    # A voxel is retained if at least 90% of participants have a nonzero cope.
    # This avoids treating exterior zero padding as measured signal.
    coverage_arr = finite & (nonzero_n >= int(np.ceil(0.90 * len(paths))))
    standard_brain = datasets.load_mni152_brain_mask(resolution=2)
    standard_brain_arr = image.resample_to_img(standard_brain, ref, interpolation="nearest").get_fdata() > 0
    mask_arr = coverage_arr & standard_brain_arr
    mask_img = nib.Nifti1Image(mask_arr.astype(np.uint8), ref.affine, ref.header)
    nib.save(mask_img, OUT / "group_mask.nii.gz")
    X = full[:, mask_arr].astype(np.float64, copy=False)
    n, v = X.shape

    # Distribution/QC summaries and spatial agreement with the group average.
    means = X.mean(axis=1)
    sds = X.std(axis=1, ddof=1)
    rms = np.sqrt(np.mean(X * X, axis=1))
    grand = X.mean(axis=0)
    corr = np.array([np.corrcoef(x, grand)[0, 1] for x in X])
    qc = pd.DataFrame({"participant_id": ids, "brain_mean_cope": means,
                       "brain_sd_cope": sds, "brain_rms_cope": rms,
                       "spatial_corr_with_group_mean": corr})
    qc.to_csv(OUT / "participant_qc.csv", index=False)

    # Standard one-sample t statistic over subject-level effect estimates.
    sumx = X.sum(axis=0)
    sumsq = np.square(X).sum(axis=0)
    t_obs = (sumx / n) / np.sqrt(np.maximum((sumsq - sumx * sumx / n) / (n - 1), 0) / n)
    df = n - 1
    p_unc = stats.t.sf(t_obs, df)

    # Sign-flipping is valid under the one-sample null with symmetric errors.
    # Max positive t across the analysis mask gives one-sided whole-brain FWE.
    perm_cache = OUT / f"max_positive_t_null_{N_PERM}_seed{SEED}_brainmask.npy"
    if perm_cache.exists():
        maxima = np.load(perm_cache)
    else:
        rng = np.random.default_rng(SEED)
        maxima = np.empty(N_PERM, dtype=np.float32)
        with threadpool_limits(limits=4):
            for start in range(0, N_PERM, 200):
                b = min(200, N_PERM - start)
                signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
                perm_sum = signs @ X
                perm_var_sum = np.maximum(sumsq[None, :] - perm_sum * perm_sum / n, 0)
                perm_t = (perm_sum / n) / np.sqrt(perm_var_sum / (n - 1) / n)
                maxima[start:start+b] = np.max(perm_t, axis=1)
        np.save(perm_cache, maxima)
    p_fwe = (1 + np.sum(maxima[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)
    crit95 = float(np.quantile(maxima, .95, method="higher"))
    sig = (p_fwe <= .05) & (t_obs > 0)

    t_img = unmask(t_obs, mask_img)
    mean_img = unmask(grand, mask_img)
    p_img = unmask(p_fwe, mask_img)
    sig_img = unmask(np.where(sig, t_obs, 0), mask_img)
    nib.save(t_img, OUT / "t_statistic.nii.gz")
    nib.save(mean_img, OUT / "mean_cope.nii.gz")
    nib.save(p_img, OUT / "p_fwe_positive.nii.gz")
    nib.save(sig_img, OUT / "t_fwe_p05_positive.nii.gz")

    # AAL3v2 is used only to define/label an anatomical vmPFC display region.
    # Bilateral medial orbital frontal, medial OFC, anterior/posterior OFC,
    # and gyrus rectus are anatomically ventromedial prefrontal territories.
    atlas = datasets.fetch_atlas_aal(version="3v2", verbose=0)
    atlas_img = nib.load(str(atlas.maps))
    aal_data = image.resample_to_img(atlas_img, ref, interpolation="nearest").get_fdata()
    labels = [x.decode() if isinstance(x, bytes) else str(x) for x in atlas.labels]
    roi_names = ["Frontal_Med_Orb_L", "Frontal_Med_Orb_R", "Rectus_L", "Rectus_R",
                 "OFCmed_L", "OFCmed_R", "OFCant_L", "OFCant_R", "OFCpost_L", "OFCpost_R"]
    missing = sorted(set(roi_names) - set(labels))
    assert not missing, f"AAL labels unavailable: {missing}"
    roi_codes = {labels.index(x) for x in roi_names}
    roi_arr = np.isin(aal_data, list(roi_codes)) & mask_arr
    roi_img = nib.Nifti1Image(roi_arr.astype(np.uint8), ref.affine, ref.header)
    nib.save(roi_img, OUT / "aal3_vmPFC_roi.nii.gz")
    roi_vec = full[:, roi_arr].mean(axis=1)
    roi_mean = float(roi_vec.mean())
    roi_se = float(stats.sem(roi_vec))
    roi_ci = stats.t.interval(.95, n - 1, loc=roi_mean, scale=roi_se)
    roi_t, roi_p_two = stats.ttest_1samp(roi_vec, 0)
    roi_p_one = float(stats.t.sf(roi_t, n - 1))

    # Cluster report from the corrected positive map, 26-neighbour connectivity.
    sig_full = np.zeros(ref.shape, dtype=bool)
    sig_full[mask_arr] = sig
    lab, nlab = ndimage.label(sig_full, structure=np.ones((3, 3, 3), dtype=int))
    clusters = []
    t_full = np.zeros(ref.shape, dtype=np.float32)
    t_full[mask_arr] = t_obs
    p_full = np.ones(ref.shape, dtype=np.float32)
    p_full[mask_arr] = p_fwe
    for cl in range(1, nlab + 1):
        coords = np.array(np.where(lab == cl)).T
        vals = t_full[tuple(coords.T)]
        peak_idx = coords[np.argmax(vals)]
        peak_xyz = nib.affines.apply_affine(ref.affine, peak_idx)
        clusters.append({"voxels": int(len(coords)), "volume_mm3": float(len(coords) * np.prod(ref.header.get_zooms()[:3])),
                         "peak_t": float(vals.max()), "peak_p_fwe": float(p_full[tuple(peak_idx)]),
                         "peak_mni_mm": [float(z) for z in peak_xyz],
                         "overlaps_vmPFC_roi": bool(np.any(roi_arr[tuple(coords.T)]))})
    clusters.sort(key=lambda x: x["peak_t"], reverse=True)

    # Visualizations: corrected positive t clusters and ROI/whole-brain distribution.
    template = datasets.load_mni152_template(resolution=2)
    disp = plotting.plot_stat_map(sig_img, bg_img=template, threshold=0,
                                  display_mode="ortho", cut_coords=(0, 42, -8),
                                  title="Gain effect: positive whole-brain FWE p ≤ .05",
                                  cmap="magma", colorbar=True, black_bg=False,
                                  dim=-.3, annotate=True)
    disp.add_contours(roi_img, levels=[.5], colors=["cyan"], linewidths=1.0)
    disp.savefig(FIG / "whole_brain_fwe_vmPFC.png", dpi=180)
    disp.close()
    disp2 = plotting.plot_glass_brain(sig_img, display_mode="lyrz", threshold=0,
                                      plot_abs=False, cmap="magma", colorbar=True,
                                      title="Positive clusters surviving voxelwise whole-brain FWE")
    disp2.add_contours(roi_img, levels=[.5], colors=["cyan"], linewidths=1.0)
    disp2.savefig(FIG / "whole_brain_fwe_glass_brain.png", dpi=180)
    disp2.close()

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.hist(means, bins=12, color="#4878a8", edgecolor="white")
    ax.axvline(0, color="black", lw=1)
    ax.set(xlabel="Participant mean cope within analysis mask (arbitrary model units)",
           ylabel="Participants", title="Distribution of whole-brain mean gain-effect estimates")
    fig.tight_layout(); fig.savefig(FIG / "participant_map_qc.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    rng_j = np.random.default_rng(SEED)
    ax.scatter(rng_j.normal(0, .045, n), roi_vec, s=32, color="#31688e", alpha=.8, edgecolors="white", linewidths=.4)
    ax.errorbar(0.22, roi_mean, yerr=[[roi_mean-roi_ci[0]], [roi_ci[1]-roi_mean]], fmt="o", color="#b23a48", capsize=4, label="Mean and 95% t CI")
    ax.axhline(0, color="black", lw=1)
    ax.set(xlim=(-.16, .5), xticks=[0, .22], xticklabels=["Participants", "Mean (95% CI)"],
           ylabel="Mean cope in AAL3 vmPFC ROI (arbitrary model units)",
           title="Participant gain-effect estimates in anatomical vmPFC")
    ax.legend(frameon=False); fig.tight_layout(); fig.savefig(FIG / "vmPFC_subject_estimates.png", dpi=180); plt.close(fig)

    genders = participants.gender.value_counts().to_dict()
    ages = participants.age.astype(float)
    report = {
        "n_participants": n, "excluded": [], "map_shape": list(ref.shape),
        "source_checksum_validation": "all 54 maps match supplied SHA256 manifest",
        "software": {"python": ".".join(map(str, __import__('sys').version_info[:3])),
                     "numpy": np.__version__, "scipy": scipy.__version__,
                     "nibabel": nib.__version__, "nilearn": nilearn.__version__},
        "sample_demographics": {"age_mean": float(ages.mean()), "age_sd": float(ages.std(ddof=1)),
                                "age_range": [float(ages.min()), float(ages.max())],
                                "gender_counts_as_recorded": genders},
        "voxel_size_mm": [float(x) for x in ref.header.get_zooms()[:3]],
        "mask_voxels": int(mask_arr.sum()), "mask_volume_mm3": float(mask_arr.sum() * np.prod(ref.header.get_zooms()[:3])),
        "coverage_voxels_before_template_intersection": int(coverage_arr.sum()),
        "mask_rule": "finite and nonzero cope in >=90% (49/54) of participants, intersected with nearest-neighbour-resampled MNI152 brain mask",
        "model": "one-sample t test of participant cope maps against zero; df=53",
        "primary_direction": "positive one-sided",
        "permutation": {"method": "whole-map sign flips; positive max-T across analysis mask", "n": N_PERM, "seed": SEED,
                        "fwe_alpha": .05, "critical_t95": crit95, "minimum_attainable_p": 1/(N_PERM+1)},
        "positive_fwe_voxels": int(sig.sum()), "positive_fwe_volume_mm3": float(sig.sum() * np.prod(ref.header.get_zooms()[:3])),
        "clusters": clusters,
        "vmPFC_roi": {"atlas": "AAL3 (nilearn AAL3v1 map)", "labels": roi_names, "voxels": int(roi_arr.sum()),
                      "mean_cope": roi_mean, "sd_between_participants": float(np.std(roi_vec, ddof=1)),
                      "ci95_t": [float(x) for x in roi_ci], "t53": float(roi_t),
                      "p_one_sided_uncorrected": roi_p_one, "p_two_sided_uncorrected": float(roi_p_two),
                      "peak_fwe_cluster_overlap": any(c["overlaps_vmPFC_roi"] for c in clusters)},
        "qc": {"participant_brain_mean_range": [float(means.min()), float(means.max())],
               "participant_brain_sd_range": [float(sds.min()), float(sds.max())],
               "spatial_correlation_range": [float(corr.min()), float(corr.max())],
               "lowest_spatial_correlations": qc.nsmallest(5, "spatial_corr_with_group_mean").to_dict(orient="records")}
    }
    (OUT / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
