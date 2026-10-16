#!/usr/bin/env python3
"""Group analysis of supplied NARPS AO86 Hypothesis 1 participant cope maps."""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import nibabel as nib
from nilearn import datasets, image, plotting
import matplotlib.pyplot as plt
from scipy import stats, ndimage

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
DATA = ROOT / "input" / "data"
N_PERM = 5000
SEED = 20261016

files = sorted(DATA.glob("sub-*_hypo1_cope.nii.gz"))
assert len(files) == 54, f"Expected 54 maps, found {len(files)}"
participants = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
expected_ids = set(participants.loc[participants["group"] == "equalIndifference", "participant_id"].astype(str))
found_ids = {p.name.split("_")[0] for p in files}
assert expected_ids == found_ids and len(expected_ids) == 54
source_manifest = json.loads((ROOT / "input" / "sources.json").read_text())
hash_checks = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() == source_manifest["files"][f"data/{p.name}"]["sha256"]
               for p in files}
assert len(hash_checks) == 54 and all(hash_checks.values()), "Input checksum mismatch"
imgs = [nib.load(str(p)) for p in files]
ref = imgs[0]
assert all(im.shape == ref.shape and np.allclose(im.affine, ref.affine) for im in imgs)
arr = np.stack([im.get_fdata(dtype=np.float32) for im in imgs])
finite = np.isfinite(arr)
nonzero = finite & (arr != 0)
coverage = nonzero.sum(axis=0)
# Intersect map coverage with an independent standard brain mask.
standard_mask = datasets.load_mni152_brain_mask(resolution=2, threshold=.2)
standard_mask_on_ref = image.resample_to_img(standard_mask, ref, interpolation="nearest",
                                              force_resample=True, copy_header=True)
mask = ((coverage >= int(np.ceil(.90 * len(files)))) & np.all(finite, axis=0)
        & (np.asarray(standard_mask_on_ref.dataobj) > 0))
X = arr[:, mask].astype(np.float64)
n, v = X.shape
assert n == 54 and v > 10000

# One-sample t statistic, positive direction. Random sign flips test the zero-mean null.
# The same maximum statistic from every permutation controls whole-brain voxelwise FWER.
sum_sq = np.sum(X * X, axis=0)
def t_from_sum(s):
    denom2 = (n * sum_sq - s * s) / (n - 1)
    return s / np.sqrt(np.maximum(denom2, np.finfo(float).tiny))

t_obs = t_from_sum(X.sum(axis=0))
rng = np.random.default_rng(SEED)
max_t = np.empty(N_PERM, dtype=np.float64)
batch = 32
for start in range(0, N_PERM, batch):
    b = min(batch, N_PERM - start)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
    sums = signs @ X
    t_perm = sums / np.sqrt(np.maximum((n * sum_sq[None, :] - sums * sums) / (n - 1), np.finfo(float).tiny))
    max_t[start:start+b] = np.max(t_perm, axis=1)
sorted_max = np.sort(max_t)
# plus-one Monte Carlo correction; adjusted p is based on whole-brain maximum T.
idx = np.searchsorted(sorted_max, t_obs, side="left")
p_fwe = (N_PERM - idx + 1) / (N_PERM + 1)

def full_img(vals, dtype=np.float32):
    a = np.zeros(ref.shape, dtype=dtype)
    a[mask] = vals
    return nib.Nifti1Image(a, ref.affine, ref.header)

mean = X.mean(axis=0)
sd = X.std(axis=0, ddof=1)
nib.save(nib.Nifti1Image(mask.astype(np.uint8), ref.affine, ref.header), OUT / "group_mask.nii.gz")
nib.save(full_img(mean), OUT / "mean_effect.nii.gz")
nib.save(full_img(t_obs), OUT / "t_statistic.nii.gz")
nib.save(full_img(p_fwe), OUT / "p_fwe_maxT.nii.gz")

# Anatomical vmPFC proxy: bilateral medial orbitofrontal cortex from AAL3v2.
atlas = datasets.fetch_atlas_aal(version="3v2", data_dir=str(ROOT / "atlas_cache"), verbose=0)
atlas_img = nib.load(atlas.maps) if isinstance(atlas.maps, str) else atlas.maps
labels = list(atlas.labels)
label_text = [x.decode() if isinstance(x, bytes) else str(x) for x in labels]
roi_ids = [i for i, name in enumerate(label_text) if "Frontal_Med_Orb" in name]
if not roi_ids:
    raise RuntimeError(f"AAL3 medial orbitofrontal labels not found: {label_text}")
# AAL uses background label 0; IDs align with label-table index.
atlas_on_ref = image.resample_to_img(atlas_img, ref, interpolation="nearest")
roi_native = np.isin(np.asarray(atlas_on_ref.dataobj), roi_ids)
roi = roi_native & mask
if not roi.any():
    raise RuntimeError("vmPFC proxy ROI has no overlap with group mask")
roi_values = X[:, roi[mask]]
roi_mean = roi_values.mean(axis=1)
roi_sd = float(roi_mean.std(ddof=1))
roi_se = roi_sd / np.sqrt(n)
roi_t = float(roi_mean.mean() / roi_se)
roi_ci = [float(roi_mean.mean() - stats.t.ppf(.975, n-1) * roi_se),
          float(roi_mean.mean() + stats.t.ppf(.975, n-1) * roi_se)]
roi_mask_img = nib.Nifti1Image(roi.astype(np.uint8), ref.affine, ref.header)
nib.save(roi_mask_img, OUT / "vmPFC_proxy_aal3.nii.gz")

# Summaries and QC, no data-driven subject exclusions.
participant_mean = arr[:, mask].mean(axis=1)
participant_sd = arr[:, mask].std(axis=1, ddof=1)
participant_roi_mean = roi_values.mean(axis=1)
qc = pd.DataFrame({"participant": [p.name.split("_")[0] for p in files],
                   "mean_in_mask": participant_mean, "sd_in_mask": participant_sd,
                   "mean_in_vmPFC_proxy": participant_roi_mean,
                   "fraction_finite": finite.reshape(n, -1).mean(axis=1),
                   "fraction_nonzero": nonzero.reshape(n, -1).mean(axis=1)})
qc.to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)

summ = {
    "n_maps": n, "input_sha256_checks_passed": bool(all(hash_checks.values())),
    "n_voxels_whole_brain_mask": int(v), "mask_rule": "MNI152 standard brain mask intersected with finite voxels nonzero in >=90% (>=49/54) maps",
    "n_permutations": N_PERM, "seed": SEED, "test": "one-sided positive one-sample t with random sign flips and whole-brain maximum-T FWER",
    "fwe_alpha": 0.05, "max_t_critical_95": float(np.quantile(max_t, .95, method="higher")),
    "whole_brain_sig_voxels": int(np.sum(p_fwe <= .05)),
    "max_t_observed": float(np.max(t_obs)), "minimum_p_fwe": float(np.min(p_fwe)),
    "group_mean_effect_range": [float(mean.min()), float(mean.max())],
    "group_mean_effect_peak_mni": [float(x) for x in nib.affines.apply_affine(ref.affine, np.array(np.unravel_index(int(np.argmax(full_img(t_obs).get_fdata())), ref.shape)))],
    "vmPFC_proxy_atlas": "AAL3v2 bilateral Frontal_Med_Orb", "vmPFC_label_ids": roi_ids,
    "vmPFC_proxy_voxels": int(roi.sum()), "vmPFC_proxy_mean_effect": float(roi_mean.mean()),
    "vmPFC_proxy_sd_between_participants": roi_sd,
    "vmPFC_proxy_mean_effect_95CI_t_descriptive": roi_ci,
    "vmPFC_proxy_mean_t_descriptive": roi_t,
    "vmPFC_proxy_p_positive_t_descriptive": float(stats.t.sf(roi_t, n-1)),
    "vmPFC_proxy_min_whole_brain_adjusted_p": float(p_fwe[roi[mask]].min()),
    "vmPFC_proxy_significant_voxels_fwe05": int(np.sum(p_fwe[roi[mask]] <= .05)),
    "participant_mean_effect_mean": float(participant_mean.mean()),
    "participant_mean_effect_sd": float(participant_mean.std(ddof=1)),
    "exclusions": [],
}
(OUT / "summary.json").write_text(json.dumps(summ, indent=2) + "\n")

# Connected components are descriptive summaries of the globally corrected voxels.
sig_data = np.zeros(ref.shape, dtype=bool)
sig_data[mask] = p_fwe <= .05
components, n_comp = ndimage.label(sig_data, structure=ndimage.generate_binary_structure(3, 3))
t_full = np.zeros(ref.shape, dtype=np.float64)
t_full[mask] = t_obs
cluster_rows = []
for lab in range(1, n_comp + 1):
    ijk = np.argwhere(components == lab)
    tvals = t_full[tuple(ijk.T)]
    peak_ijk = ijk[int(np.argmax(tvals))]
    xyz = nib.affines.apply_affine(ref.affine, peak_ijk)
    cluster_rows.append({"cluster": lab, "voxels_input_grid": len(ijk), "peak_t": float(tvals.max()),
                         "peak_mni_x": float(xyz[0]), "peak_mni_y": float(xyz[1]), "peak_mni_z": float(xyz[2])})
pd.DataFrame(cluster_rows).to_csv(OUT / "fwe_clusters.tsv", sep="\t", index=False)

# Participant vmPFC proxy averages: one value per participant, with a descriptive t interval.
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(5.8, 4.2), constrained_layout=True)
ax.scatter(np.random.default_rng(SEED).normal(0, .045, n), roi_mean, s=24, alpha=.75,
           color="#547a9a", edgecolor="white", linewidth=.3)
ax.errorbar(0, roi_mean.mean(), yerr=[[roi_mean.mean()-roi_ci[0]], [roi_ci[1]-roi_mean.mean()]],
            fmt="D", color="#b54b3a", capsize=4, markersize=7, label="Mean and 95% t CI")
ax.axhline(0, color="black", linewidth=1, linestyle="--")
ax.set(xlim=(-.25,.25), xlabel="Participants (jittered)", ylabel="Mean effect in vmPFC proxy (supplied units)",
       title="Bilateral medial orbitofrontal proxy")
ax.set_xticks([])
ax.legend(frameon=False, fontsize=8)
fig.savefig(OUT / "vmPFC_proxy_effects.png", dpi=180)
plt.close(fig)

# Whole-brain corrected positive group findings; green outline shows the independent ROI proxy.
fig = plt.figure(figsize=(7.0, 5.0))
template = datasets.load_mni152_template(resolution=2)
display = plotting.plot_stat_map(full_img(t_obs), bg_img=template, threshold=float(np.quantile(max_t, .95, method="higher")),
                                 display_mode="ortho", cut_coords=(-26, -102, -4), cmap="hot", colorbar=True,
                                 black_bg=False, figure=fig, title=None, draw_cross=True)
display.add_contours(roi_mask_img, levels=[.5], colors=["#18a558"], linewidths=1.5)
fig.suptitle("Positive t above whole-brain max-T FWE threshold\nGreen: bilateral vmPFC proxy", fontsize=12)
fig.savefig(OUT / "wholebrain_fwe_map.png", dpi=180)
plt.close(fig)

print(json.dumps(summ, indent=2))
