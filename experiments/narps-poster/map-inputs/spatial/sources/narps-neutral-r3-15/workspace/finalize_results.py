"""Add connected-component summaries and refresh publication-sized figures."""
from pathlib import Path
import json
import nibabel as nib
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
from nilearn import plotting
from nilearn.datasets import load_mni152_template

root = Path(__file__).resolve().parent
out = root / "results"
summary = json.loads((out / "summary.json").read_text())
summary.pop("max_t_uncorrected_p", None)
timg = nib.load(out / "t_statistic.nii.gz")
pimg = nib.load(out / "p_fwe.nii.gz")
tmap = timg.get_fdata()
pmap = pimg.get_fdata()
sig = (pmap <= .05) & (tmap > 0)
labels, nlab = ndimage.label(sig, structure=np.ones((3,3,3), dtype=int))
clusters = []
for lab in range(1, nlab+1):
    ijk = np.argwhere(labels == lab)
    vals = tmap[labels == lab]
    peak_idx = ijk[np.argmax(vals)]
    xyz = nib.affines.apply_affine(timg.affine, peak_idx)
    clusters.append({"voxels_26conn": int(len(ijk)), "peak_mni_mm": [float(v) for v in xyz],
                     "peak_t": float(vals.max()), "peak_p_fwe": float(pmap[tuple(peak_idx)])})
clusters.sort(key=lambda c: -c["peak_t"])
summary["positive_fwe_clusters_26conn"] = clusters
summary["max_positive_t_uncorrected_p"] = float(__import__("scipy").stats.t.sf(summary["max_observed_t"], summary["n"]-1))
(out / "summary.json").write_text(json.dumps(summary, indent=2))

# Show the location of all corrected positive voxels with axial sections.
fig = plt.figure(figsize=(11, 4.2))
disp = plotting.plot_stat_map(timg, bg_img=load_mni152_template(resolution=2),
    threshold=summary["maxT_95_critical"], display_mode="z", cut_coords=[-8, -4, 0],
    cmap="hot", colorbar=True, title=None, figure=fig)
fig.subplots_adjust(top=.97, wspace=.04)
fig.savefig(out / "whole_brain_fwe.png", dpi=180, bbox_inches="tight")
disp.close()
