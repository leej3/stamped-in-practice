#!/usr/bin/env python3
"""Replay the delivered analysis and compare scientific outputs exactly."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
import nibabel as nib
import numpy as np
from scipy import stats

root=Path(__file__).resolve().parents[1]
results=root/"results"
summary_path=results/"summary.json"
before=json.loads(summary_path.read_text())
map_names=["common_mask.nii.gz","group_mean_cope.nii.gz","group_tstat.nii.gz",
           "p_fwe_maxT_one_sided.nii.gz","vmPFC_HO_proxy.nii.gz",
           "harvard_oxford_cortical_25pct_resampled.nii.gz"]
before_maps={name:nib.load(results/name).get_fdata() for name in map_names}
runlog=results/"attempts"/"replay_run.log"
with runlog.open("w") as log:
    subprocess.run([sys.executable,str(root/"analysis"/"run_group.py")],cwd=root,
                   stdout=log,stderr=subprocess.STDOUT,check=True)
after=json.loads(summary_path.read_text())
for key in ["n_participants","n_common_support_voxels","n_fwe_voxels_p_le_0.05",
            "max_t_observed","max_t_fwe_p_at_max","positive_fwe_max_t_threshold",
            "fwe_significant_voxels_by_harvard_oxford_label","vmPFC_proxy"]:
    if key in before and before[key]!=after.get(key): raise AssertionError(f"Summary changed: {key}")
for name,old in before_maps.items():
    new=nib.load(results/name).get_fdata()
    if not np.array_equal(old,new): raise AssertionError(f"Map changed: {name}")
mask=nib.load(results/"common_mask.nii.gz").get_fdata()>0
tmap=nib.load(results/"group_tstat.nii.gz").get_fdata()
meanmap=nib.load(results/"group_mean_cope.nii.gz").get_fdata()
peak_ijk=np.unravel_index(np.argmax(np.where(mask,tmap,-np.inf)),tmap.shape)
import glob
source_maps=sorted(glob.glob(str(root/"input"/"data"/"*_hypo1_cope.nii.gz")))
peak_values=np.array([nib.load(path).get_fdata(dtype=np.float32)[peak_ijk] for path in source_maps])
reference=stats.ttest_1samp(peak_values,0).statistic
if not np.isclose(reference,tmap[peak_ijk],rtol=1e-6): raise AssertionError("Peak t does not match independent SciPy reference")
if not np.isclose(peak_values.mean(),meanmap[peak_ijk],rtol=1e-6): raise AssertionError("Peak mean does not match independent source-map reference")
lines=["Replay validation: PASS",
       "Same interpreter, inputs, seed and code produced identical selected scientific maps and summary values.",
       f"Independent SciPy check at peak: t={reference:.6f}; mean cope={peak_values.mean():.6f}; voxel={peak_ijk}.",
       f"n={after['n_participants']}; common voxels={after['n_common_support_voxels']}; FWE-significant voxels={after['n_fwe_voxels_p_le_0.05']}; max-t pFWE={after['max_t_fwe_p_at_max']}"]
for name in ["summary.json",*map_names]:
    digest=hashlib.sha256((results/name).read_bytes()).hexdigest()
    lines.append(f"{name} SHA256 {digest}")
(results/"replay_validation.txt").write_text("\n".join(lines)+"\n")
print("\n".join(lines))
