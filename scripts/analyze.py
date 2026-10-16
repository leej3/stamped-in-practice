#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference gain cope maps."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from nilearn import plotting
from nilearn.image import resample_to_img
from templateflow.api import get as templateflow_get

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
DATA = ROOT / "input" / "data"
N_PERM = int(os.environ.get("NARPS_N_PERM", "4999"))
SEED = 20261015


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    manifest = json.loads((ROOT / "input/sources.json").read_text())
    cohort = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
    group = cohort.loc[cohort["group"] == "equalIndifference"].copy()
    paths = [ROOT / "input" / k for k in manifest["files"] if k.endswith(".nii.gz")]
    expected = {v["participant_id"]: v for v in manifest["files"].values() if "participant_id" in v}
    if len(group) != 54 or len(paths) != 54:
        raise RuntimeError(f"Expected 54 maps and cohort rows; got {len(paths)}, {len(group)}")
    paths.sort(key=lambda p: p.name)
    ids = [p.name.split("_")[0] for p in paths]
    if set(ids) != set(expected) or set(ids) != set(group["participant_id"]):
        raise RuntimeError("Input IDs do not match source manifest and equal-indifference cohort")

    imgs, arrays, qc = [], [], []
    ref_shape = ref_aff = ref_hdr = None
    for p, sid in zip(paths, ids):
        img = nib.load(str(p))
        data = np.asarray(img.get_fdata(dtype=np.float32))
        if ref_shape is None:
            ref_shape, ref_aff, ref_hdr = data.shape, img.affine, img.header.copy()
        if data.shape != ref_shape or not np.allclose(img.affine, ref_aff, atol=1e-4):
            raise RuntimeError(f"Inconsistent spatial geometry: {p.name}")
        digest = sha256(p)
        exp = expected[sid]
        if digest != exp["sha256"] or p.stat().st_size != exp["bytes"]:
            raise RuntimeError(f"Source manifest checksum/size mismatch: {p.name}")
        finite = np.isfinite(data)
        nonzero = finite & (data != 0)
        qc.append({"participant_id": sid, "sha256": digest, "bytes": p.stat().st_size,
                   "finite_voxels": int(finite.sum()), "nonzero_voxels": int(nonzero.sum()),
                   "nonzero_fraction_of_finite": float(nonzero.sum()/max(1, finite.sum())),
                   "mean_nonzero": float(np.mean(data[nonzero])),
                   "sd_nonzero": float(np.std(data[nonzero], ddof=1))})
        imgs.append(img)
        arrays.append(data)

    # Common supported, nonzero brain voxels; require map support in >=90% of participants.
    stack = np.stack(arrays, axis=0)
    support = np.mean(np.isfinite(stack) & (stack != 0), axis=0)
    # Use a brain mask in the maps' reported MNI152NLin2009cAsym space.
    brain_mask_img = resample_to_img(
        str(templateflow_get("MNI152NLin2009cAsym", desc="brain", suffix="mask", resolution=2)),
        imgs[0], interpolation="nearest")
    brain_mask = brain_mask_img.get_fdata() > 0
    mask = (support >= 0.90) & brain_mask
    if mask.sum() < 1000:
        raise RuntimeError(f"Unexpectedly small common analysis mask: {mask.sum()}")
    Y = stack[:, mask].astype(np.float64)
    if not np.isfinite(Y).all():
        raise RuntimeError("Non-finite values within analysis mask")

    # Robust participant-level QC is descriptive; do not delete valid participants post hoc.
    row_means = Y.mean(axis=1)
    med = np.median(row_means)
    mad = np.median(np.abs(row_means-med)) * 1.4826
    robust_z = (row_means-med)/mad if mad else np.zeros_like(row_means)
    for i, row in enumerate(qc):
        row["analysis_mask_mean"] = float(row_means[i])
        row["analysis_mask_robust_z"] = float(robust_z[i])
    pd.DataFrame(qc).to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)

    n, v = Y.shape
    sums = Y.sum(axis=0)
    sumsq = np.square(Y).sum(axis=0)
    sd = Y.std(axis=0, ddof=1)
    mean = Y.mean(axis=0)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = stats.t.sf(t_obs, df=n-1)
    # Exact single-voxel t p-values under Gaussian participant errors; Bonferroni
    # controls the familywise error rate regardless of spatial dependence.
    bonf_p = np.minimum(1.0, p_unc * v)
    bonf_critical_t = float(stats.t.isf(.05 / v, df=n-1))

    # One-sided sign-flip max-T: weak null plus symmetric errors; whole mask is family.
    rng = np.random.default_rng(SEED)
    max_t = np.empty(N_PERM, dtype=np.float32)
    batch_size = 32
    for start in range(0, N_PERM, batch_size):
        b = min(batch_size, N_PERM-start)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
        s = signs @ Y
        t_perm = s / np.sqrt(np.maximum((sumsq[None, :] - np.square(s)/n)/(n-1), 1e-20))
        max_t[start:start+b] = np.max(t_perm, axis=1)
    max_p = (1 + np.sum(max_t[:, None] >= t_obs[None, :], axis=0))/(N_PERM+1)
    critical_t = float(np.quantile(max_t, .95, method="higher"))

    # MNI-coordinate vmPFC sphere: center (0, 40, -12) mm, radius 12 mm.
    # The confirmatory decision still uses whole-brain max-T corrected p values.
    ijk = np.indices(ref_shape).reshape(3, -1).T
    xyz = nib.affines.apply_affine(ref_aff, ijk)
    vm_mask_full = (np.sum((xyz - np.array([0., 40., -12.]))**2, axis=1) <= 12.**2).reshape(ref_shape)
    vm_in_mask = vm_mask_full[mask]
    if vm_in_mask.sum() < 5:
        raise RuntimeError("vmPFC sphere has insufficient overlap with analysis mask")
    roi = Y[:, vm_in_mask]
    roi_mean = float(roi.mean())
    roi_sd = float(roi.mean(axis=1).std(ddof=1))
    roi_t = roi_mean/(roi_sd/np.sqrt(n))
    roi_ci = stats.t.interval(.95, n-1, loc=roi_mean, scale=roi_sd/np.sqrt(n))
    roi_p = float(stats.t.sf(roi_t, n-1))
    roi_voxel_p = max_p[vm_in_mask]
    roi_sig_vox = int(np.sum(roi_voxel_p < .05))

    # Effect-map and statistic NIfTIs in the original MNI152NLin2009cAsym grid.
    mean_full = np.zeros(ref_shape, dtype=np.float32); mean_full[mask] = mean
    t_full = np.zeros(ref_shape, dtype=np.float32); t_full[mask] = t_obs
    p_full = np.ones(ref_shape, dtype=np.float32); p_full[mask] = max_p
    def save_map(data, name):
        hdr = ref_hdr.copy(); hdr.set_data_dtype(np.float32)
        nib.save(nib.Nifti1Image(data, ref_aff, hdr), OUT / name)
    save_map(mean_full, "group_mean_gain_effect.nii.gz")
    save_map(t_full, "group_tstat.nii.gz")
    save_map(p_full, "group_maxT_fwe_p.nii.gz")
    mask_full = mask.astype(np.uint8)
    mask_hdr = ref_hdr.copy(); mask_hdr.set_data_dtype(np.uint8)
    nib.save(nib.Nifti1Image(mask_full, ref_aff, mask_hdr), OUT / "analysis_mask.nii.gz")

    bonf_full = np.ones(ref_shape, dtype=np.float32); bonf_full[mask] = bonf_p
    save_map(bonf_full, "group_bonferroni_fwe_p.nii.gz")
    sig = mask & (bonf_full < .05)
    vox_sig = np.argwhere(sig)
    peak = None
    if len(vox_sig):
        peak_ijk = vox_sig[np.argmax(t_full[sig])]
        peak = {"ijk": peak_ijk.tolist(), "mni_mm": nib.affines.apply_affine(ref_aff, peak_ijk).round(2).tolist(),
                "t": float(t_full[tuple(peak_ijk)]),
                "bonferroni_fwe_p": float(bonf_full[tuple(peak_ijk)]),
                "maxT_fwe_p": float(p_full[tuple(peak_ijk)])}
    result = {
        "analysis": "one-sample group model; positive gain effect; whole-brain Bonferroni primary with sign-flip max-T sensitivity",
        "n_included": n, "n_excluded": 0, "n_maps": len(paths), "analysis_mask_voxels": int(v),
        "mask_rule": "MNI152 brain mask intersected with nonzero finite map support in at least 90% of participants",
        "space": "MNI152NLin2009cAsym (source-reported)",
        "permutations": N_PERM, "random_seed": SEED,
        "primary_correction": "one-sided one-sample Student t; Bonferroni across all analysis-mask voxels",
        "bonferroni_critical_t": bonf_critical_t,
        "whole_brain_bonferroni_fwe_voxels_p_lt_0.05": int(sig.sum()),
        "whole_brain_bonferroni_peak": peak,
        "maxT_sensitivity_critical_t_95": critical_t,
        "whole_brain_maxT_fwe_voxels_p_lt_0.05": int(np.sum(max_p < .05)),
        "observed_t_max": float(np.max(t_obs)),
        "observed_t_max_uncorrected_one_sided_p": float(np.min(p_unc)),
        "maxT_fwe_p_minimum": float(np.min(max_p)),
        "maxT_null_quantiles_90_95_99": [float(x) for x in np.quantile(max_t, [.90, .95, .99])],
        "vmPFC_roi": {"definition": "12 mm sphere centered MNI (0, 40, -12)",
                      "voxels_in_mask": int(vm_in_mask.sum()), "mean_effect_estimate": roi_mean,
                      "participant_mean_effect_sd": roi_sd, "ci95_t": [float(roi_ci[0]), float(roi_ci[1])],
                      "one_sample_t": float(roi_t), "df": n-1, "uncorrected_one_sided_p": roi_p,
                      "voxels_whole_brain_FWE_p_lt_0.05": roi_sig_vox,
                      "voxels_Bonferroni_whole_brain_p_lt_0.05": int(np.sum(bonf_p[vm_in_mask] < .05)),
                      "minimum_voxelwise_Bonferroni_whole_brain_p_in_roi": float(np.min(bonf_p[vm_in_mask])),
                      "minimum_voxelwise_whole_brain_FWE_p_in_roi": float(np.min(roi_voxel_p))},
        "participant_global_mean_median": float(med), "participant_global_mean_mad_scaled": float(mad),
        "participants_global_robust_z_gt_3_abs": [ids[i] for i in range(n) if abs(robust_z[i]) > 3],
        "median_voxel_mean_effect": float(np.median(mean)),
        "mean_effect_across_mask_voxels": float(np.mean(mean)),
        "notes": ["Maps are participant contrast parameter estimates, not standardized statistics.",
                  "The gain modulator was variance-normalized upstream; effects are not per-currency-unit slopes.",
                  "No participant variance maps are supplied; group model treats participant estimates equally.",
                  "Bonferroni inference assumes Gaussian participant effects for the voxelwise t tests but not independent voxels.",
                  "Sign-flip max-T sensitivity assumes independent participants and symmetric errors under the null; the empirical null maxima were extreme relative to observed t statistics."]
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")

    # Figure 1: anatomical slices of mean effect with FWE-significant voxels.
    mean_img = nib.Nifti1Image(mean_full, ref_aff)
    t_img = nib.Nifti1Image(t_full, ref_aff)
    bg_img = resample_to_img(
        str(templateflow_get("MNI152NLin2009cAsym", suffix="T1w", resolution=2, desc=None)),
        mean_img, interpolation="continuous")
    fig = plt.figure(figsize=(11, 4.2))
    mean_display = plotting.plot_stat_map(mean_img, bg_img=bg_img, threshold=None, display_mode="ortho",
                                          cut_coords=(0, 40, -12), colorbar=True, cmap="cold_hot",
                                          title="Mean gain-effect estimate (arbitrary model units)", figure=fig,
                                          annotate=True, draw_cross=False, transparency=.55)
    mean_display.add_markers([(0, 40, -12)], marker_color="#00ff00", marker_size=35)
    fig.savefig(OUT / "mean_effect_orthogonal.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    fig = plt.figure(figsize=(11, 4.2))
    display_cuts = tuple(peak["mni_mm"]) if peak else (0, 40, -12)
    plotting.plot_stat_map(t_img, bg_img=bg_img, threshold=bonf_critical_t, display_mode="ortho",
                           cut_coords=display_cuts, colorbar=True, cmap="cold_hot",
                           title=f"Whole-brain Bonferroni FWE p < .05 (t > {bonf_critical_t:.2f})",
                           figure=fig, annotate=True, draw_cross=False)
    fig.savefig(OUT / "wholebrain_bonferroni_fwe.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: participant-level vmPFC sphere averages with group estimate and CI.
    roi_subject = roi.mean(axis=1)
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    x = np.arange(1, n+1)
    ax.scatter(x, roi_subject, s=25, alpha=.75, color="#315b7d", edgecolor="none")
    ax.axhline(roi_mean, color="#a83232", lw=2, label=f"Mean {roi_mean:.3g}")
    ax.axhspan(*roi_ci, color="#a83232", alpha=.13, label="95% CI")
    ax.axhline(0, color="black", lw=.8)
    ax.set(xlabel="Participant (sorted by ID)", ylabel="Mean participant effect estimate in vmPFC sphere",
           title="Participant-level vmPFC effect estimates")
    ax.legend(frameon=False); fig.tight_layout()
    fig.savefig(OUT / "vmPFC_participants.png", dpi=180)
    plt.close(fig)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
