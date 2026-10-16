"""Descriptive connected-component summary at the voxelwise FWER threshold."""
from pathlib import Path
import pandas as pd
import nibabel as nib
import numpy as np
from scipy import ndimage
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
ref = nib.load(OUT / "group_t_one_sample.nii.gz")
t = ref.get_fdata()
p = nib.load(OUT / "group_fwe_p_maxT.nii.gz").get_fdata()
mask = nib.load(OUT / "group_mask.nii.gz").get_fdata() > 0
sig = (p < .05) & mask
labels, n = ndimage.label(sig, structure=np.ones((3, 3, 3), dtype=int))
rows = []
for label in range(1, n + 1):
    coords = np.argwhere(labels == label)
    values = t[labels == label]
    peak = coords[np.argmax(values)]
    xyz = nib.affines.apply_affine(ref.affine, peak)
    rows.append({"component": label, "voxels": len(coords), "extent_mm3": len(coords) * np.prod(ref.header.get_zooms()[:3]),
                 "peak_x_mm": xyz[0], "peak_y_mm": xyz[1], "peak_z_mm": xyz[2],
                 "peak_t": values.max(), "peak_p_fwe": p[tuple(peak)], "min_p_fwe": p[labels == label].min()})
pd.DataFrame(rows).to_csv(OUT / "significant_components.tsv", sep="\t", index=False)
print(pd.DataFrame(rows).to_string(index=False))
