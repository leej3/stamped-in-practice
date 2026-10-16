#!/usr/bin/env python3
"""Group inference for the fixed NARPS AO86 equal-indifference gain maps."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats, ndimage
from nibabel.processing import resample_from_to

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "primary_v2_template_mask"
FIG = ROOT / "figures" / "primary_v2_template_mask"
N_PERM = 9999
SEED = 20261016


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    sources = json.loads((ROOT / "input/sources.json").read_text())
    participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
    ids = participants.participant_id.tolist()
    expected = set(sources["files"])
    map_names = [f"data/{sid}_hypo1_cope.nii.gz" for sid in ids]
    if len(ids) != 54 or participants.participant_id.duplicated().any():
        raise ValueError("Expected 54 unique participant IDs")
    if set(map_names) != (expected - {"participants.tsv", "study-task.md", "upstream-methods.md"}):
        raise ValueError("Participant/map IDs do not match source inventory")

    arrays: list[np.ndarray] = []
    input_records = []
    ref_img = None
    for sid, rel in zip(ids, map_names):
        path = ROOT / "input" / rel
        checksum = sha256(path)
        declared = sources["files"][rel]
        if checksum != declared["sha256"]:
            raise ValueError(f"SHA256 mismatch for {rel}")
        img = nib.load(str(path))
        if ref_img is None:
            ref_img = img
        elif img.shape != ref_img.shape or not np.allclose(img.affine, ref_img.affine, atol=1e-5):
            raise ValueError(f"Image geometry mismatch: {rel}")
        data = img.get_fdata(dtype=np.float32)
        arrays.append(data)
        input_records.append({"participant_id": sid, "path": f"input/{rel}", "bytes": path.stat().st_size, "sha256": checksum,
                              "shape": list(img.shape), "finite_voxels": int(np.isfinite(data).sum()),
                              "nonzero_voxels": int(np.count_nonzero(data))})

    Ximg = np.stack(arrays).astype(np.float32, copy=False)
    n = Ximg.shape[0]
    finite = np.isfinite(Ximg).all(axis=0)
    # Use the matching MNI152NLin2009cAsym template brain mask, then require
    # complete nonzero support in every participant map.
    template_mask_path = ROOT / "external/tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz"
    template_mask = nib.load(str(template_mask_path))
    brain_mask_img = resample_from_to(template_mask, (ref_img.shape, ref_img.affine), order=0)
    brain_mask = brain_mask_img.get_fdata() > 0.5
    mask = finite & np.all(Ximg != 0, axis=0) & brain_mask
    nvox = int(mask.sum())
    if nvox < 1000:
        raise ValueError(f"Unexpectedly small common nonzero support: {nvox}")
    X = Ximg[:, mask].astype(np.float64)
    sum_x = X.sum(axis=0)
    ss_x = np.square(X).sum(axis=0)
    denom = np.sqrt(np.maximum(n * ss_x - sum_x**2, 0.0))
    t_obs = sum_x * np.sqrt(n - 1) / denom
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    se = sd / np.sqrt(n)
    ci_lo, ci_hi = mean + stats.t.ppf([0.025, 0.975], n - 1)[:, None] * se
    raw_p = stats.t.sf(t_obs, n - 1)

    # One-sided max-T sign-flip null. The variance numerator's sum of squares is
    # invariant to sign flips, so each permutation only needs a matrix product.
    rng = np.random.default_rng(SEED)
    max_t = np.empty(N_PERM, dtype=np.float64)
    batch = 100
    for start in range(0, N_PERM, batch):
        stop = min(start + batch, N_PERM)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(stop - start, n))
        sums = signs @ X
        ts = sums * np.sqrt(n - 1) / np.sqrt(np.maximum(n * ss_x[None, :] - sums**2, 1e-30))
        max_t[start:stop] = np.max(ts, axis=1)
    max_t.sort()
    p_fwe = (1 + N_PERM - np.searchsorted(max_t, t_obs, side="left")) / (N_PERM + 1)
    # Independent validation: recompute ten complete-brain permutation maxima
    # with SciPy's sample-variance t statistic, then check max-T p by direct count.
    check_rng = np.random.default_rng(SEED)
    check_signs = check_rng.choice(np.array([-1.0, 1.0]), size=(batch, n))[:10]
    independent_maxima = []
    for sign in check_signs:
        scipy_t = stats.ttest_1samp(X * sign[:, None], 0.0, axis=0).statistic
        independent_maxima.append(float(np.nanmax(scipy_t)))
    optimized_first_batch = []
    for signs in check_signs:
        sums = signs @ X
        ts = sums * np.sqrt(n - 1) / np.sqrt(np.maximum(n * ss_x - sums**2, 1e-30))
        optimized_first_batch.append(float(np.max(ts)))
    permutation_check_passed = bool(np.allclose(independent_maxima, optimized_first_batch, rtol=1e-10, atol=1e-10))
    if not permutation_check_passed:
        raise AssertionError("Independent permutation max-T check failed")

    def vol(values: np.ndarray, dtype=np.float32) -> nib.Nifti1Image:
        full = np.full(ref_img.shape, np.nan, dtype=dtype)
        full[mask] = values.astype(dtype, copy=False)
        img = nib.Nifti1Image(full, ref_img.affine, ref_img.header.copy())
        img.set_data_dtype(dtype)
        return img

    mean_img, t_img, p_img = vol(mean), vol(t_obs), vol(p_fwe)
    sig_t_values = np.where(p_fwe <= 0.05, t_obs, 0.0)
    sig_t_img = vol(sig_t_values)
    nib.save(mean_img, OUT / "group_mean_effect.nii.gz")
    nib.save(t_img, OUT / "group_t_positive.nii.gz")
    nib.save(p_img, OUT / "p_fwe_maxT_positive.nii.gz")
    nib.save(sig_t_img, OUT / "group_t_fwe05_positive.nii.gz")

    # Anatomically explicit descriptive vmPFC midline box in MNI mm.
    ijk = np.array(np.where(mask)).T
    xyz = nib.affines.apply_affine(ref_img.affine, ijk)
    roi = (np.abs(xyz[:, 0]) <= 10) & (xyz[:, 1] >= 20) & (xyz[:, 1] <= 60) & (xyz[:, 2] >= -20) & (xyz[:, 2] <= 20)
    roi_values = X[:, roi].mean(axis=1)
    roi_mean = float(roi_values.mean())
    roi_sd = float(roi_values.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_ci = stats.t.interval(0.95, n - 1, loc=roi_mean, scale=roi_se)
    roi_t = float(roi_mean / roi_se)
    roi_p = float(stats.t.sf(roi_t, n - 1))
    roi_peak_i = int(np.flatnonzero(roi)[np.argmax(t_obs[roi])])
    roi_peak_xyz = nib.affines.apply_affine(ref_img.affine, ijk[roi_peak_i])
    roi_peak_t = float(t_obs[roi_peak_i])
    roi_peak_fwe_p = float(p_fwe[roi_peak_i])
    pd.DataFrame({"participant_id": ids, "vmPFC_box_mean_effect": roi_values}).to_csv(OUT / "vmPFC_participant_summary.csv", index=False)

    # QC independent reference calculation at the positive max-t voxel.
    best = int(np.argmax(t_obs))
    voxel_t_ref, voxel_p_ref = stats.ttest_1samp(X[:, best], 0.0, alternative="greater")
    if not np.isclose(voxel_t_ref, t_obs[best], rtol=1e-10, atol=1e-10):
        raise AssertionError("Independent SciPy t statistic check failed")
    max_vox = ijk[best]
    max_xyz = nib.affines.apply_affine(ref_img.affine, max_vox)
    if not np.isclose(voxel_p_ref, raw_p[best], rtol=1e-10, atol=1e-10):
        raise AssertionError("Independent SciPy raw p check failed")
    max_p = float(p_fwe[best])
    support = Ximg[:, mask]
    summary = {
        "analysis": "one-sample random-effects t; one-sided positive whole-brain max-T sign-flip permutation",
        "n_participants": n, "excluded_participants": [], "n_map_voxels_common_nonzero_support": nvox,
        "participant_metadata": {"group": "equalIndifference", "age_mean": float(participants.age.mean()), "age_sd": float(participants.age.std(ddof=1)),
                                 "age_range": [int(participants.age.min()), int(participants.age.max())],
                                 "gender_counts_as_recorded": participants.gender.value_counts().to_dict()},
        "permutations": N_PERM, "seed": SEED, "familywise_alpha": 0.05,
        "whole_brain_positive_fwe_voxels": int(np.count_nonzero(p_fwe <= 0.05)),
        "max_t_voxel": {"ijk": max_vox.tolist(), "mni_mm": np.round(max_xyz, 2).tolist(), "t": float(t_obs[best]),
                         "raw_one_sided_p": float(raw_p[best]), "maxT_fwe_p": max_p,
                         "fwe_p_mc_resolution": 1 / (N_PERM + 1)},
        "vmPFC_definition": "MNI box |x|<=10, y=20..60, z=-20..20 mm, intersected with final analysis mask",
        "vmPFC_voxels": int(roi.sum()), "vmPFC_group_mean_effect": roi_mean,
        "vmPFC_group_sd": roi_sd, "vmPFC_group_se": float(roi_se),
        "vmPFC_mean_95ci": [float(roi_ci[0]), float(roi_ci[1])],
        "vmPFC_descriptive_t": roi_t, "vmPFC_descriptive_one_sided_p_uncorrected": roi_p,
        "vmPFC_peak_t": roi_peak_t, "vmPFC_peak_mni_mm": np.round(roi_peak_xyz, 2).tolist(), "vmPFC_peak_maxT_fwe_p": roi_peak_fwe_p,
        "global_map_value_range": [float(Ximg[:, mask].min()), float(Ximg[:, mask].max())],
        "participant_map_mean_range": [float(X.mean(axis=1).min()), float(X.mean(axis=1).max())],
        "max_mean_map_sd": float(sd.max()), "mask_definition": "MNI152NLin2009cAsym res-02 brain mask (nearest-neighbor resampled to the supplied grid), intersected with finite nonzero support in every participant map",
        "template_brain_mask_voxels_resampled": int(brain_mask.sum()),
        "analysis_mask_coverage_of_template_brain": float(nvox / brain_mask.sum()),
        "template_brain_mask": {"path": "external/tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz", "url": "https://templateflow.s3.amazonaws.com/tpl-MNI152NLin2009cAsym/tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz", "sha256": sha256(template_mask_path)},
        "template_t1": {"path": "external/tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz", "url": "https://templateflow.s3.amazonaws.com/tpl-MNI152NLin2009cAsym/tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz", "sha256": sha256(ROOT / "external/tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz")},
        "geometry": {"shape": list(ref_img.shape), "affine": ref_img.affine.tolist(), "zooms_mm": list(map(float, ref_img.header.get_zooms()[:3]))},
        "independent_scipy_check": {"max_t_t": float(voxel_t_ref), "max_t_raw_p": float(voxel_p_ref), "permutation_maxima_recomputed_full_brain": len(independent_maxima), "permutation_maxima_match": permutation_check_passed,
                                    "max_t_fwe_p_direct_count": float((1 + np.count_nonzero(max_t >= t_obs[best])) / (N_PERM + 1)), "passed": True},
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": __import__("scipy").__version__,
                     "pandas": pd.__version__, "nibabel": nib.__version__, "matplotlib": matplotlib.__version__, "nilearn": __import__("nilearn").__version__},
        "provenance": {"analysis_script_sha256": sha256(Path(__file__).resolve()), "protocol_sha256": sha256(ROOT / "research-protocol.md"),
                       "source_manifest_sha256": sha256(ROOT / "input/sources.json"), "command": f"{sys.executable} analysis/analyze.py"},
        "inputs": input_records,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    pd.DataFrame([{"voxel_t": float(t_obs[i]), "mean_effect": float(mean[i]), "raw_one_sided_p": float(raw_p[i]),
                   "maxT_fwe_p": float(p_fwe[i]), "i": int(ijk[i, 0]), "j": int(ijk[i, 1]), "k": int(ijk[i, 2]),
                   "x_mm": float(nib.affines.apply_affine(ref_img.affine, ijk[i])[0]),
                   "y_mm": float(nib.affines.apply_affine(ref_img.affine, ijk[i])[1]),
                   "z_mm": float(nib.affines.apply_affine(ref_img.affine, ijk[i])[2])}
                  for i in np.argsort(t_obs)[-20:][::-1]]).to_csv(OUT / "top20_positive_voxels.csv", index=False)
    sig_indices = np.flatnonzero(p_fwe <= 0.05)
    sig_mask_volume = np.zeros(ref_img.shape, dtype=bool)
    sig_mask_volume[tuple(ijk[sig_indices].T)] = True
    labeled, n_clusters = ndimage.label(sig_mask_volume, structure=np.ones((3, 3, 3), dtype=bool))
    cluster_ids = labeled[tuple(ijk[sig_indices].T)]
    sig_rows = []
    for i, cluster_id in zip(sig_indices, cluster_ids):
        xyz_i = nib.affines.apply_affine(ref_img.affine, ijk[i])
        sig_rows.append({"cluster_26conn": int(cluster_id), "voxel_t": float(t_obs[i]), "mean_effect": float(mean[i]),
                         "maxT_fwe_p": float(p_fwe[i]), "i": int(ijk[i, 0]), "j": int(ijk[i, 1]), "k": int(ijk[i, 2]),
                         "x_mm": float(xyz_i[0]), "y_mm": float(xyz_i[1]), "z_mm": float(xyz_i[2])})
    pd.DataFrame(sig_rows).to_csv(OUT / "whole_brain_fwe_voxels.csv", index=False)
    summary["whole_brain_fwe_cluster_count_26conn_descriptive"] = int(n_clusters)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    pd.DataFrame(input_records).to_csv(OUT / "input_qc.csv", index=False)

    # Figure 1: whole-brain max-T familywise-error corrected positive t map.
    from nilearn import plotting
    bg_path = ROOT / "external/tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz"
    bg_img = nib.load(str(bg_path))
    display_data = np.zeros(ref_img.shape, dtype=np.float32)
    display_data[mask] = sig_t_values.astype(np.float32)
    plot_img = nib.Nifti1Image(display_data, ref_img.affine, ref_img.header.copy())
    display = plotting.plot_stat_map(plot_img, bg_img=bg_img, display_mode="z", cut_coords=[-10, 0, 10, 20],
                                     threshold=0, cmap="cold_hot", colorbar=True,
                                     title="Gain-effect t statistics (positive whole-brain max-T FWE p < .05)",
                                     black_bg=False, annotate=True)
    display.savefig(FIG / "group_t_map.png", dpi=160)
    display.close()

    # Figure 2: participant-level distribution of the independent vmPFC box summary.
    fig, ax = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    ax.axhline(0, color="#555555", lw=1, ls="--")
    ax.scatter(np.ones(n), roi_values, s=30, alpha=.72, color="#315a8a", edgecolor="white", linewidth=.4)
    ax.errorbar([1], [roi_mean], yerr=[[roi_mean - roi_ci[0]], [roi_ci[1] - roi_mean]], fmt="D", color="#b24735",
                capsize=5, markersize=7, label="Mean and 95% t interval")
    ax.set(xlim=(.65, 1.35), xticks=[1], xticklabels=["Participants"], ylabel="Mean gain-effect estimate (COPE units)",
           title="Descriptive vmPFC midline box")
    ax.legend(frameon=False, loc="best")
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(FIG / "vmPFC_participant_effects.png", dpi=180)
    plt.close(fig)
    print(json.dumps({k: summary[k] for k in ["n_participants", "n_map_voxels_common_nonzero_support", "whole_brain_positive_fwe_voxels", "whole_brain_fwe_cluster_count_26conn_descriptive", "max_t_voxel", "vmPFC_voxels", "vmPFC_group_mean_effect", "vmPFC_mean_95ci", "vmPFC_descriptive_one_sided_p_uncorrected", "vmPFC_peak_t", "vmPFC_peak_mni_mm", "vmPFC_peak_maxT_fwe_p"]}, indent=2))


if __name__ == "__main__":
    main()
