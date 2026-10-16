#!/usr/bin/env python3
"""Independent numerical checks against SciPy and saved permutation draws."""
import json
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
ids = participants.participant_id.tolist()
data = np.stack([np.asarray(nib.load(ROOT / "input/data" / f"{pid}_hypo1_cope.nii.gz").dataobj, dtype=np.float64) for pid in ids])
support = np.asarray(nib.load(OUT / "coverage_count.nii.gz").dataobj) > 0
X = data[:, support]
scipy_result = stats.ttest_1samp(X, 0, axis=0, alternative="greater")
t_map = np.asarray(nib.load(OUT / "group_t.nii.gz").dataobj)[support]
p_map = np.asarray(nib.load(OUT / "p_uncorrected.nii.gz").dataobj)[support]
p_fwer_map = np.asarray(nib.load(OUT / "p_fwer_maxT.nii.gz").dataobj)[support]
null = np.load(OUT / "permutation_maxT.npz")["max_null"]
p_fwer_ref = (1 + np.count_nonzero(null[:, None] >= t_map[None, :], axis=0)) / (len(null) + 1)
roi_mask = np.asarray(nib.load(OUT / "vmPFC_atlas_mask.nii.gz").dataobj)[support].astype(bool)
# NIfTI stores p maps as float32; include the representation of exact .05.
corrected = p_fwer_map <= .050001
bonferroni = p_map < .05 / support.sum()
summary = json.loads((OUT / "summary.json").read_text())
validation = {
    "scipy_ttest_max_abs_t_difference": float(np.max(np.abs(t_map - scipy_result.statistic))),
    "scipy_ttest_max_abs_p_difference": float(np.max(np.abs(p_map - scipy_result.pvalue))),
    "nifti_storage_precision_tolerance": 1e-6,
    "permutation_p_map_max_abs_difference": float(np.max(np.abs(p_fwer_map - p_fwer_ref))),
    "permutation_p_map_matches_within_nifti_precision": bool(np.allclose(p_fwer_map, p_fwer_ref, atol=1e-6, rtol=0)),
    "fwer_significant_voxels": int(corrected.sum()),
    "fwer_significant_vmPFC_voxels": int(np.count_nonzero(corrected & roi_mask)),
    "bonferroni_voxels": int(bonferroni.sum()),
    "bonferroni_vmPFC_voxels": int(np.count_nonzero(bonferroni & roi_mask)),
    "max_null_statistic": float(null.max()),
    "null_95th_percentile": float(np.quantile(null, .95)),
    "coverage_voxels": int(support.sum()),
    "matches_summary_counts": bool(corrected.sum() == summary["n_voxels_fwer_lt_alpha"]),
}
if validation["scipy_ttest_max_abs_t_difference"] > 1e-6 or validation["scipy_ttest_max_abs_p_difference"] > 1e-6:
    raise AssertionError("Observed t/p differ from independent SciPy calculation")
if not validation["permutation_p_map_matches_within_nifti_precision"] or not validation["matches_summary_counts"]:
    raise AssertionError("Saved p map does not match independent p-value reconstruction")
(OUT / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
print(json.dumps(validation, indent=2))
