#!/usr/bin/env python3
"""Group inference for NARPS Hypothesis 1, fixed AO86 participant cope maps."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
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
VMPCF_CENTER = (0.0, 40.0, -10.0)  # MNI mm; operational anatomical anchor
VMPCF_RADIUS_MM = 12.0


def main() -> None:
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    files = sorted((INPUT / "data").glob("sub-*_hypo1_cope.nii.gz"))
    meta = pd.read_csv(INPUT / "participants.tsv", sep="\t").set_index("participant_id")
    if len(files) != 54 or len(meta) != 54:
        raise RuntimeError(f"Expected 54 maps and participant rows; got {len(files)}, {len(meta)}")

    ref = nib.load(str(files[0]))
    shape, affine = ref.shape, ref.affine
    data = []
    qc = []
    for f in files:
        img = nib.load(str(f))
        if img.shape != shape or not np.allclose(img.affine, affine, atol=1e-5):
            raise ValueError(f"Geometry mismatch: {f.name}")
        x = np.asarray(img.dataobj, dtype=np.float32)
        pid = f.name.split("_")[0]
        if pid not in meta.index or meta.loc[pid, "group"] != "equalIndifference":
            raise ValueError(f"Unexpected participant {pid}")
        finite = np.isfinite(x)
        if not finite.all():
            raise ValueError(f"Non-finite voxels in {f.name}")
        data.append(x)
        nz = x != 0
        qc.append({"participant_id": pid, "nonzero_voxels": int(nz.sum()),
                   "min": float(x.min()), "max": float(x.max()),
                   "mean_abs_nonzero": float(np.abs(x[nz]).mean())})
    Xall = np.stack(data)
    # A conservative common-support mask: every participant's contrast map is nonzero.
    # This prevents zeros outside individual coverage from becoming artificial evidence.
    mask = np.all(Xall != 0, axis=0)
    X = Xall[:, mask].astype(np.float64)
    n, m = X.shape
    if n != 54 or m < 100_000:
        raise RuntimeError(f"Unexpected analysis matrix dimensions {X.shape}")

    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = stats.t.sf(t_obs, n - 1)
    p_bonf = np.minimum(1.0, p_unc * m)
    bonf_tcrit = float(stats.t.isf(.05 / m, n - 1))

    mean_vol = np.zeros(shape, dtype=np.float32)
    t_vol = np.zeros(shape, dtype=np.float32)
    mean_vol[mask] = mean.astype(np.float32)
    t_vol[mask] = t_obs.astype(np.float32)
    affine_img = nib.Nifti1Image(mean_vol, affine, ref.header)
    t_img = nib.Nifti1Image(t_vol, affine, ref.header)
    nib.save(affine_img, OUT / "group_mean_effect.nii.gz")
    nib.save(t_img, OUT / "group_t_map.nii.gz")
    bonf_vol = np.ones(shape, dtype=np.float32)
    bonf_vol[mask] = p_bonf.astype(np.float32)
    nib.save(nib.Nifti1Image(bonf_vol, affine), OUT / "group_bonferroni_fwe_p.nii.gz")

    # Independent anatomical summary: MNI sphere around ventromedial PFC (radius 12 mm).
    ijk = np.indices(shape).reshape(3, -1).T
    xyz = nib.affines.apply_affine(affine, ijk)
    roi = (np.linalg.norm(xyz - np.array(VMPCF_CENTER), axis=1) <= VMPCF_RADIUS_MM).reshape(shape)
    roi &= mask
    if roi.sum() == 0:
        raise RuntimeError("vmPFC ROI has no common-support voxels")
    roi_subject = Xall[:, roi].mean(axis=1)
    roi_mean = float(roi_subject.mean())
    roi_sd = float(roi_subject.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_t = roi_mean / roi_se
    roi_p = float(stats.t.sf(roi_t, n - 1))
    roi_ci = stats.t.interval(.95, n - 1, loc=roi_mean, scale=roi_se)
    roi_d = roi_mean / roi_sd
    peak_ijk = np.unravel_index(np.argmax(np.where(mask, t_vol, -np.inf)), shape)
    peak_mni = [float(v) for v in nib.affines.apply_affine(affine, peak_ijk)]

    q = np.quantile(X, [0, .01, .5, .99, 1])
    summary = {
        "n_expected": 54, "n_included": n, "n_excluded": 0,
        "analysis_mask": "intersection of nonzero support across all 54 maps",
        "mask_voxels": int(m), "voxel_size_mm": [float(v) for v in nib.affines.voxel_sizes(affine)],
        "finite_all_maps": True,
        "whole_brain_primary": "one-sided positive one-sample t with Bonferroni FWER control over common support",
        "bonferroni_t_critical_fwe05": bonf_tcrit,
        "bonferroni_positive_voxels_fwe05": int((p_bonf <= .05).sum()),
        "bonferroni_min_adjusted_p": float(p_bonf.min()),
        "bonferroni_fwe_significant_voxels_in_vmPFC": int((p_bonf[roi[mask]] <= .05).sum()),
        "max_t_observed": float(t_obs.max()), "max_t_peak_mni": peak_mni,
        "masked_effect_quantiles": dict(zip(["min", "p01", "median", "p99", "max"], map(float, q))),
        "vmPFC_roi": {"definition": "12-mm MNI sphere centered at (0, 40, -10); common-support voxels",
                      "voxels": int(roi.sum()), "mean_effect": roi_mean, "sd_between_participants": roi_sd,
                      "se": float(roi_se), "ci95": [float(roi_ci[0]), float(roi_ci[1])],
                      "t53": float(roi_t), "p_one_sided_uncorrected": roi_p,
                      "cohens_dz": float(roi_d)},
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    pd.DataFrame(qc).to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)

    # Figure 1: positive t-statistics surviving Bonferroni whole-brain FWE.
    positive_t_img = nib.Nifti1Image(np.maximum(t_vol, 0), affine)
    disp = plotting.plot_glass_brain(positive_t_img, threshold=bonf_tcrit,
                                    display_mode="lyrz", plot_abs=False,
                                    title="Positive group t-statistics (Bonferroni whole-brain FWE .05)",
                                    cmap="cold_hot", colorbar=True, black_bg=False)
    disp.savefig(FIG / "whole_brain_fwe_t.png", dpi=180)
    disp.close()

    # Figure 2: vmPFC anatomical ROI participant summaries.
    fig, ax = plt.subplots(figsize=(6.2, 4.3))
    jitter = np.random.default_rng(20261016).normal(0, .045, n)
    ax.scatter(np.ones(n) + jitter, roi_subject, s=24, color="#325f8c", alpha=.78,
               edgecolor="white", linewidth=.35)
    ax.errorbar([1.28], [roi_mean], yerr=[[roi_mean-roi_ci[0]], [roi_ci[1]-roi_mean]],
                fmt="D", color="#bb4a32", capsize=5, lw=2, label="Mean and 95% CI")
    ax.axhline(0, color="black", lw=.8, ls="--")
    ax.set_xlim(.82, 1.55); ax.set_xticks([1], ["Participants"])
    ax.set_ylabel("Mean cope within vmPFC sphere (arbitrary model units)")
    ax.set_title("vmPFC group estimate (descriptive ROI summary)")
    ax.legend(frameon=False, loc="best"); fig.tight_layout()
    fig.savefig(FIG / "vmpfc_participant_effects.png", dpi=180)
    plt.close(fig)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
