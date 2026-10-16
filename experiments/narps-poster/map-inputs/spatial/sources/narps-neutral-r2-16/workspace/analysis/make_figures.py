"""Render final figures and a descriptive vmPFC proxy summary from checked results."""
from pathlib import Path
import json

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from nilearn.image import new_img_like
from nilearn.plotting import plot_stat_map

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
INPUT = ROOT / "input"

ref = nib.load(str(INPUT / "data/sub-001_hypo1_cope.nii.gz"))
template_path = RESULTS / "reference_data/tpl-MNI152NLin2009cAsym_res-02_T1w.nii.gz"
template = nib.load(str(template_path))
data = np.load(RESULTS / "primary_group_arrays.npz")
mean, logp, mask = data["mean"], data["logp_fwe"], data["mask"].astype(bool)
participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
n = len(participants)
sig = mask & (logp >= -np.log10(.05))

# Descriptive coordinate box centered over ventromedial/orbitomedial frontal cortex.
ijk = np.indices(ref.shape).reshape(3, -1).T
xyz = nib.affines.apply_affine(ref.affine, ijk)
roi = (((np.abs(xyz[:, 0]) <= 12) & (xyz[:, 1] >= 24) & (xyz[:, 1] <= 56) &
        (xyz[:, 2] >= -20) & (xyz[:, 2] <= 4)).reshape(ref.shape) & mask)
stack = np.stack([
    nib.load(str(INPUT / f"data/{pid}_hypo1_cope.nii.gz")).get_fdata(dtype=np.float32)
    for pid in participants.participant_id
])
roi_vals = stack[:, roi].mean(axis=1)
sem = stats.sem(roi_vals)
ci = stats.t.interval(.95, df=n-1, loc=roi_vals.mean(), scale=sem)
roi_summary = {
    "definition": "MNI152NLin2009cAsym coordinate box: |x|<=12, y=24..56, z=-20..4 mm, intersected with common nonzero participant support",
    "n_participants": n, "roi_voxels": int(roi.sum()),
    "mean_of_participant_means": float(roi_vals.mean()),
    "sd_between_participants": float(roi_vals.std(ddof=1)),
    "t_based_95pct_ci": [float(ci[0]), float(ci[1])],
    "corrected_voxels_in_proxy": int((sig & roi).sum()),
    "interpretation": "descriptive ROI summary only; no ROI p-value used for the primary decision",
}
(RESULTS / "primary_vmPFC_proxy_summary.json").write_text(json.dumps(roi_summary, indent=2) + "\n")

# Whole-brain corrected map in its matching TemplateFlow anatomical reference.
fwe_img = new_img_like(ref, logp.astype(np.float32))
display = plot_stat_map(
    fwe_img, bg_img=template, display_mode="ortho", cut_coords=(-26, -100, -4),
    threshold=-np.log10(.05), cmap="magma", colorbar=True,
    title="Positive gain effect: whole-brain max-t FWE, −log10(p)",
    black_bg=False, dim=0.5, draw_cross=False,
)
display.savefig(FIGURES / "primary_whole_brain_maxt.png", dpi=180)
display.close()

# All participant estimates show dispersion, mean and a t-based interval.
fig, ax = plt.subplots(figsize=(7.4, 4.6))
rng = np.random.default_rng(20261016)
x_jitter = rng.uniform(-.08, .08, size=n)
ax.scatter(x_jitter, roi_vals, s=34, color="#1f5b78", alpha=.8, linewidth=.4, edgecolor="white")
ax.errorbar([.28], [roi_vals.mean()], yerr=[[roi_vals.mean()-ci[0]], [ci[1]-roi_vals.mean()]],
            fmt="D", color="#bd4f28", capsize=5, linewidth=2, label="mean and 95% t interval")
ax.axhline(0, color="black", linewidth=1, linestyle="--")
ax.set(xlim=(-.2, .55), xticks=[0], xticklabels=["Participants"], ylabel="Mean gain-effect estimate (a.u.)",
       title="Participant estimates in the vmPFC coordinate proxy\n(descriptive; not the corrected hypothesis test)")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIGURES / "primary_vmPFC_proxy.png", dpi=180)
plt.close(fig)
print(json.dumps(roi_summary, indent=2))
