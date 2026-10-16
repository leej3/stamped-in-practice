#!/usr/bin/env python3
"""Group analysis of fixed NARPS AO86 participant gain-effect maps."""
from pathlib import Path
import glob, hashlib, json
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
import matplotlib.pyplot as plt
from nilearn import plotting, image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
FIG = OUT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
SEED, N_PERM = 20261016, 5000

meta = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
files = sorted(glob.glob(str(ROOT / "input/data/*_hypo1_cope.nii.gz")))
assert len(files) == len(meta) == 54
ids = [Path(f).name.split("_")[0] for f in files]
assert ids == sorted(meta.participant_id.tolist())
imgs = [nib.load(f) for f in files]
ref = imgs[0]
assert all(im.shape == ref.shape and np.allclose(im.affine, ref.affine) for im in imgs)
A = np.stack([im.get_fdata(dtype=np.float32) for im in imgs])
assert np.isfinite(A).all()

# Zero-valued voxels are outside some participant's estimation support. Use a
# fixed common analysis mask requiring coverage in at least 90% of participants.
support = A != 0
mask = support.sum(axis=0) >= int(np.ceil(.90 * len(files)))
Y = A[:, mask].astype(np.float64)
n, v = Y.shape
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
tobs = mean / (sd / np.sqrt(n))
df = n - 1
p_unc = stats.t.sf(tobs, df)

# One-sided sign-flip max-t test, controlling FWE over every voxel in the mask.
# Sign flips are valid for a one-sample test under symmetric, independent
# participant-level errors. The +1 correction gives valid Monte Carlo p values.
rng = np.random.default_rng(SEED)
denom = np.sqrt((n * np.sum(Y * Y, axis=0) - (np.sum(Y, axis=0) ** 2)) / (n - 1))
max_null = np.empty(N_PERM, dtype=np.float32)
batch = 100
for start in range(0, N_PERM, batch):
    b = min(batch, N_PERM - start)
    signs = rng.choice(np.array([-1., 1.]), size=(b, n))
    sums = signs @ Y
    tperm = sums / denom
    max_null[start:start+b] = np.max(tperm, axis=1)
    if (start + b) % 1000 == 0:
        print(f"permutations {start+b}/{N_PERM}", flush=True)
p_fwe = (1 + (max_null[:, None] >= tobs[None, :]).sum(axis=0)) / (N_PERM + 1)

def out_img(values, name, dtype=np.float32, fill=0):
    vol = np.full(ref.shape, fill, dtype=dtype)
    vol[mask] = values.astype(dtype)
    out = nib.Nifti1Image(vol, ref.affine, ref.header)
    out.set_data_dtype(dtype)
    nib.save(out, OUT / name)
    return out

mean_img = out_img(mean, "group_mean_effect.nii.gz")
t_img = out_img(tobs, "group_t.nii.gz")
pfwe_img = out_img(p_fwe, "group_p_fwe.nii.gz", fill=1)
punc_img = out_img(p_unc, "group_p_uncorrected.nii.gz", fill=1)
mask_img = nib.Nifti1Image(mask.astype(np.uint8), ref.affine, ref.header)
nib.save(mask_img, OUT / "group_mask_90pct.nii.gz")

# Descriptive vmPFC coordinate box; the inferential claim remains the whole-brain
# test. Coordinates are MNI mm, chosen to cover medial orbitofrontal/subgenual PFC.
ijk = np.indices(ref.shape).reshape(3, -1).T
xyz = nib.affines.apply_affine(ref.affine, ijk).reshape(*ref.shape, 3)
roi = mask & (np.abs(xyz[..., 0]) <= 20) & (xyz[..., 1] >= 20) & (xyz[..., 1] <= 60) & (xyz[..., 2] >= -25) & (xyz[..., 2] <= 10)
roi_y = A[:, roi]
roi_subject_mean = roi_y.mean(axis=1)
roi_mean = roi_subject_mean.mean()
roi_se = stats.sem(roi_subject_mean)
roi_t, roi_p_two = stats.ttest_1samp(roi_subject_mean, 0)
roi_ci = stats.t.interval(.95, n-1, loc=roi_mean, scale=roi_se)
roi_p_fwe_min = float(p_fwe[roi[mask]].min())
roi_t_max = float(tobs[np.where(roi[mask])].max())

# Sensitivity to the support threshold: 100% coverage subset, with max-t
# probabilities evaluated against the larger (90% coverage) search-space null.
mask100 = support.all(axis=0)
Y100 = A[:, mask100].astype(float)
t100 = Y100.mean(axis=0) / (Y100.std(axis=0, ddof=1) / np.sqrt(n))
p100_conservative = (1 + (max_null[:, None] >= t100[None, :]).sum(axis=0)) / (N_PERM + 1)

peak_i = np.argmax(tobs)
peak_ijk = np.argwhere(mask)[peak_i]
peak_xyz = nib.affines.apply_affine(ref.affine, peak_ijk)
peak = {"t": float(tobs[peak_i]), "p_uncorrected_one_sided": float(p_unc[peak_i]), "p_fwe_max_t": float(p_fwe[peak_i]), "mean_effect": float(mean[peak_i]), "mni_mm": [float(x) for x in peak_xyz]}
res = {
    "n_included": n, "n_excluded": 0, "exclusion_reason": None,
    "grid_shape": list(ref.shape), "voxel_size_mm": [float(x) for x in ref.header.get_zooms()[:3]],
    "mask_rule": "nonzero estimation support in at least 90% of participants",
    "mask_voxels": int(v), "mask100_voxels": int(mask100.sum()),
    "participants_support_voxels_min_median_max": [int(support.sum(axis=(1,2,3)).min()), float(np.median(support.sum(axis=(1,2,3)))), int(support.sum(axis=(1,2,3)).max())],
    "test": "one-sided one-sample sign-flip max-t; familywise error controlled over 90%-coverage whole-brain mask",
    "n_permutations": N_PERM, "seed": SEED,
    "minimum_fwe_p": float(p_fwe.min()), "n_voxels_fwe_p_lt_0.05": int((p_fwe < .05).sum()),
    "n_voxels_uncorrected_p_lt_0.001": int((p_unc < .001).sum()),
    "n_mask100_voxels_with_conservative_p_lt_0.05": int((p100_conservative < .05).sum()),
    "max_null_95th_percentile": float(np.quantile(max_null, .95)), "peak_positive_voxel": peak,
    "vmPFC_coordinate_box_mm": {"x": [-20,20], "y": [20,60], "z": [-25,10]},
    "vmPFC_descriptive_subject_mean_effect": float(roi_mean), "vmPFC_descriptive_SE": float(roi_se),
    "vmPFC_descriptive_95pct_t_CI": [float(x) for x in roi_ci], "vmPFC_descriptive_t": float(roi_t),
    "vmPFC_descriptive_two_sided_p_unadjusted": float(roi_p_two), "vmPFC_roi_voxels": int(roi.sum()),
    "vmPFC_min_whole_brain_fwe_p": roi_p_fwe_min, "vmPFC_max_voxel_t": roi_t_max,
}
(OUT / "summary.json").write_text(json.dumps(res, indent=2) + "\n")
pd.DataFrame({"participant_id": ids, "vmPFC_mean_effect": roi_subject_mean}).to_csv(OUT / "vmPFC_subject_estimates.tsv", sep="\t", index=False)
pd.DataFrame({"mni_x": [peak_xyz[0]], "mni_y": [peak_xyz[1]], "mni_z": [peak_xyz[2]], **{k:[v] for k,v in peak.items() if k != "mni_mm"}}).to_csv(OUT / "peak.tsv", sep="\t", index=False)

# Figure 1: group mean effect, unthresholded with FWE-significant voxels outlined.
fig = plotting.plot_stat_map(mean_img, threshold=None, display_mode="z", cut_coords=[-15, -5, 5, 15, 25],
    cmap="RdBu_r", symmetric_cbar=True, title="Mean gain effect estimate (all participants)", colorbar=True, black_bg=False)
fig.savefig(FIG / "mean_effect_slices.png", dpi=180)
fig.close()

# Figure 2: subject-level descriptive ROI values and mean/CI.
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.scatter(np.arange(1, n+1), roi_subject_mean, color="#315a7d", alpha=.8, s=24)
ax.axhline(0, color="black", lw=.9)
ax.axhline(roi_mean, color="#c44e52", lw=2, label=f"mean = {roi_mean:.3f}")
ax.fill_between([1, n], [roi_ci[0]]*2, [roi_ci[1]]*2, color="#c44e52", alpha=.15, label="95% t interval")
ax.set(xlabel="Participant (sorted by ID)", ylabel="Mean cope in vmPFC coordinate box", title="Descriptive vmPFC estimates (not whole-brain corrected)")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(FIG / "vmPFC_subject_effects.png", dpi=180); plt.close(fig)

# Figure 3: thresholded whole-brain FWE result. An empty map is informative.
sigvol = np.zeros(ref.shape, dtype=np.float32); sigvol[mask] = np.where(p_fwe < .05, mean, 0)
sig_img = nib.Nifti1Image(sigvol, ref.affine, ref.header)
fig = plotting.plot_stat_map(sig_img, threshold=0, display_mode="z", cut_coords=[-15,-5,5,15,25],
    cmap="Reds", title="Positive gain effect, whole-brain max-t FWE p < .05", colorbar=True, black_bg=False)
fig.savefig(FIG / "positive_fwe_result.png", dpi=180); fig.close()
print(json.dumps(res, indent=2))
