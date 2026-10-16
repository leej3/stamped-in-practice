#!/usr/bin/env python3
"""Independent numerical checks of the delivered group statistics."""
import json
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

root = Path(__file__).resolve().parents[1]
summary = json.loads((root / "results/summary.json").read_text())
meta = pd.read_csv(root / "input/participants.tsv", sep="\t")
images = [nib.load(root / "input/data" / f"{pid}_hypo1_cope.nii.gz").get_fdata(dtype=np.float64)
          for pid in meta.participant_id]
stack = np.stack(images, axis=-1)
mask = np.count_nonzero(stack, axis=-1) == len(images)
tmap = nib.load(root / "results/group_t_unthresholded.nii.gz").get_fdata()
permutation = pd.read_csv(root / "results/permutation_max_t.tsv", sep="\t").max_positive_t.to_numpy()

# SciPy's independent one-sample t implementation verifies selected full-data voxels.
coords = [tuple(x) for x in (np.argwhere(mask)[0], np.argwhere(mask)[len(np.argwhere(mask)) // 2],
                              np.argwhere(mask)[-1], np.argwhere(mask)[np.argmax(tmap[mask])])]
checks = []
for ijk in coords:
    y = stack[ijk]
    expected = float(stats.ttest_1samp(y, 0).statistic)
    observed = float(tmap[ijk])
    checks.append({"voxel_ijk": [int(v) for v in ijk], "t_scipy": expected, "t_delivered": observed,
                   "absolute_difference": abs(expected - observed)})
    assert np.isclose(expected, observed, atol=1e-6)

threshold = summary["primary"]["fwe_t_threshold"]
assert len(permutation) == summary["primary"]["permutations"]
threshold_recalculated = float(np.quantile(permutation, .95, method="higher"))
assert np.isclose(threshold, threshold_recalculated, atol=1e-6)
assert int(np.count_nonzero(tmap > threshold)) == summary["primary"]["significant_voxels"]
assert summary["primary"]["significant_voxels_in_vmPFC_sphere"] == 0
# Reconstruct the first generated participant sign pattern and independently compute
# its maximum t with SciPy, checking the resampling statistic that defines max-t FWE.
rng = np.random.default_rng(summary["primary"]["seed"])
signs = rng.choice(np.array([-1.0, 1.0]), size=(len(meta), 128))[:, 0]
first_perm = stack[mask] * signs
scipy_perm_t = stats.ttest_1samp(first_perm, 0.0, axis=1).statistic
first_perm_max = float(np.max(scipy_perm_t))
assert np.isclose(first_perm_max, permutation[0], atol=1e-6)
report = {"independent_implementation": "scipy.stats.ttest_1samp, checked at four voxels",
          "voxel_checks": checks, "max_t_threshold_recalculated": threshold,
          "permutation_count": len(permutation), "first_sign_flip_max_t_scipy": first_perm_max,
          "first_saved_max_t": float(permutation[0]),
          "significant_voxels_recalculated": int(np.count_nonzero(tmap > threshold)),
          "result": "passed"}
(root / "results/validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
