#!/usr/bin/env python3
"""Independent numerical checks of the generated NARPS H1 maps and tables."""
from __future__ import annotations
import json
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
R, I = ROOT / "results", ROOT / "input"
summary = json.loads((R / "summary.json").read_text())
qc = pd.read_csv(R / "map_qc.tsv", sep="\t")
excluded = pd.read_csv(R / "exclusions.tsv", sep="\t")
assert len(qc) == summary["n_expected"] == 54
assert qc.checksum_ok.all() and qc.finite.all() and qc.qc_flags.fillna("").eq("").all()
assert len(excluded) == summary["n_excluded"] == 0
participants = pd.read_csv(I / "participants.tsv", sep="\t")
imgs = [nib.load(str(I / "data" / f"{pid}_hypo1_cope.nii.gz")) for pid in participants.participant_id]
mask = nib.load(str(R / "p_fwe.nii.gz"))
aff = imgs[0].affine
brain = nib.load(str(R / "t_unthresholded.nii.gz"))
assert all(im.shape == imgs[0].shape and np.allclose(im.affine, aff, atol=1e-4) for im in imgs)
assert np.allclose(brain.affine, aff, atol=1e-4)
arr = np.stack([np.asarray(im.dataobj, dtype=np.float64) for im in imgs])
T = np.asarray(brain.dataobj, dtype=np.float64)
M = np.asarray(mask.dataobj) < 1
rng = np.random.default_rng(71)
coords = np.argwhere(~M)
for xyz in coords[rng.choice(len(coords), size=20, replace=False)]:
    ijk = tuple(xyz)
    ref = stats.ttest_1samp(arr[(slice(None),) + ijk], 0, alternative="greater")
    assert np.isclose(T[ijk], ref.statistic, rtol=2e-5, atol=2e-5), (ijk, T[ijk], ref.statistic)
mean_img = np.asarray(nib.load(str(R / "mean_effect.nii.gz")).dataobj)
P = np.asarray(mask.dataobj, dtype=np.float64)
assert np.all((P >= 0) & (P <= 1))
null = pd.read_csv(R / "permutation_max_t.tsv", sep="\t").max_t_null.to_numpy()
assert len(null) == summary["permutations"] and np.all(np.diff(null) >= 0)
peaks = pd.read_csv(R / "top_voxels.tsv", sep="\t")
assert peaks.loc[0, "t"] == T[tuple(peaks.loc[0, ["i", "j", "k"]].astype(int))]
assert summary["n_fwe_positive_voxels"] == int(np.sum(np.asarray(nib.load(str(R / "t_fwe05.nii.gz")).dataobj) > 0))
assert summary["n_fwe_positive_voxels_in_vmPFC_box"] == 0
# Reconstruct the 95% CI from participant-level voxel averages inside the documented box.
coords_grid = np.indices(imgs[0].shape, dtype=float)
world = nib.affines.apply_affine(aff, np.stack(coords_grid, axis=-1).reshape(-1, 3)).reshape(*imgs[0].shape, 3)
box = (~M) & (np.abs(world[..., 0]) <= 10) & (world[..., 1] >= 20) & (world[..., 1] <= 60) & (world[..., 2] >= -20) & (world[..., 2] <= 20)
subject_means = arr[:, box].mean(axis=1)
assert np.isclose(subject_means.mean(), summary["vmPFC_box_mean_effect"], rtol=1e-6, atol=1e-8)
assert np.allclose(mean_img[box].mean(), summary["vmPFC_box_mean_effect"], rtol=2e-5, atol=2e-6)
print(json.dumps({"validated": True, "n_maps": len(imgs), "voxel_t_checks": 20,
                  "permutation_null_n": len(null), "fwe_significant_voxels": summary["n_fwe_positive_voxels"],
                  "vmPFC_fwe_voxels": summary["n_fwe_positive_voxels_in_vmPFC_box"]}, indent=2))
