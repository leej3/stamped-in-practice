"""Independent numerical checks of the accepted group-analysis outputs."""
from __future__ import annotations

import json
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "group-analysis"


def close(actual: float, expected: float, label: str, tolerance: float = 1e-8) -> None:
    if not np.isclose(actual, expected, rtol=tolerance, atol=tolerance):
        raise AssertionError(f"{label}: {actual} != {expected}")


def main() -> None:
    summary = json.loads((OUT / "summary.json").read_text())
    participants = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
    roi = pd.read_csv(OUT / "vmPFC_subject_effects.tsv", sep="\t")
    ids = participants.loc[participants.group.eq("equalIndifference"), "participant_id"].tolist()
    if roi.participant_id.tolist() != ids or len(roi) != 54:
        raise AssertionError("ROI effect rows do not exactly match the source cohort order")

    values = roi.vmPFC_mean_effect.to_numpy(float)
    n = len(values)
    mean = float(values.mean())
    sd = float(values.std(ddof=1))
    t_stat, p_two_sided = stats.ttest_1samp(values, 0.0)
    ci = stats.t.interval(0.95, df=n - 1, loc=mean, scale=stats.sem(values))
    max_null = pd.read_csv(OUT / "null_max_t.tsv").max_t_permutation.to_numpy(float)
    t_img = nib.load(str(OUT / "group_t.nii.gz"))
    p_img = nib.load(str(OUT / "p_fwe_maxT.nii.gz"))
    t_map = np.asarray(t_img.dataobj)
    p_map = np.asarray(p_img.dataobj)
    finite = np.isfinite(t_map) & np.isfinite(p_map)
    if int(finite.sum()) != summary["n_voxels_tested"]:
        raise AssertionError("Finite statistic-map support does not match tested voxel count")
    corrected_count = int(np.sum(p_map[finite] <= 0.05))
    peak_xyz = np.asarray(summary["max_t_xyz_mm"], dtype=float)
    peak_ijk = np.rint(nib.affines.apply_affine(np.linalg.inv(t_img.affine), peak_xyz)).astype(int)
    peak_t = float(t_map[tuple(peak_ijk)])
    peak_p = float(p_map[tuple(peak_ijk)])
    max_t_p = (1 + int(np.sum(max_null >= peak_t))) / (len(max_null) + 1)

    close(mean, summary["vmPFC_mean_effect"], "ROI mean")
    close(sd, summary["vmPFC_effect_sd_between_participants"], "ROI SD")
    close(float(ci[0]), summary["vmPFC_mean_95ci"][0], "ROI CI lower")
    close(float(ci[1]), summary["vmPFC_mean_95ci"][1], "ROI CI upper")
    close(float(stats.t.sf(t_stat, df=n - 1)), summary["vmPFC_descriptive_one_sided_p_unadjusted"], "ROI one-sided p")
    close(peak_t, summary["max_t"], "whole-brain peak t")
    close(peak_p, max_t_p, "whole-brain peak max-T adjusted p")
    if corrected_count != summary["n_voxels_fwe_005"]:
        raise AssertionError("Corrected voxel count does not match summary")
    if summary["vmPFC_peak_p_fwe"] <= 0.05:
        raise AssertionError("vmPFC peak unexpectedly passed whole-brain FWE")

    audit = {
        "status": "passed",
        "independent_check": "SciPy one-sample ROI summary and max-null exceedance calculation",
        "n_roi_subjects": n,
        "roi_two_sided_p_for_audit_only": float(p_two_sided),
        "roi_mean": mean,
        "roi_95ci": [float(ci[0]), float(ci[1])],
        "whole_brain_peak_t": peak_t,
        "whole_brain_peak_p_fwe_recomputed": max_t_p,
        "fwe_voxel_count_recomputed": corrected_count,
        "tested_voxel_count_checked": int(finite.sum()),
    }
    (OUT / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
