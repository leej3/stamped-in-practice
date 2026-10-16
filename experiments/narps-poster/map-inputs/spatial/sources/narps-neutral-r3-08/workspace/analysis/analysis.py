#!/usr/bin/env python3
"""Group inference for NARPS AO86 equal-indifference gain-effect maps."""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy.ndimage import label, generate_binary_structure
from scipy.ndimage import center_of_mass
import matplotlib.pyplot as plt
from nilearn import plotting

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
N_PERM = 9999
SEED = 8601

participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
sources = json.loads((ROOT / "input/sources.json").read_text())
files = [ROOT / "input/data" / f"{pid}_hypo1_cope.nii.gz" for pid in participants.participant_id]
images = [nib.load(str(f)) for f in files]
ref = images[0]
assert len(files) == 54 and all(f.exists() for f in files)
for f in files:
    expected = sources["files"][str(f.relative_to(ROOT / "input"))]["sha256"]
    digest = hashlib.sha256(f.read_bytes()).hexdigest()
    assert digest == expected, f"Checksum mismatch: {f.name}"
assert all(im.shape == ref.shape and np.allclose(im.affine, ref.affine) for im in images)
data = np.stack([im.get_fdata(dtype=np.float32) for im in images])
assert np.isfinite(data).all()

# Fixed common support: only voxels represented by every participant's nonzero map.
# Outside the first-level analysis mask AO86 stored zeros; this avoids treating
# absent estimates as measured zero effects.
mask = np.all(data != 0, axis=0)
if not mask.any():
    raise RuntimeError("No common nonzero coverage")
Y = data[:, mask].astype(np.float64)
n, v = Y.shape
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(n))
p_unc = stats.t.sf(t_obs, n - 1)

# One-sample random-effects t model with participant-level sign flips under H0.
# The maximum positive t over the complete common-coverage brain controls FWER.
rng = np.random.default_rng(SEED)
sum_sq = np.sum(Y * Y, axis=0)
max_null = np.empty(N_PERM, dtype=np.float32)
batch = 32
for start in range(0, N_PERM, batch):
    b = min(batch, N_PERM - start)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
    sums = signs @ Y
    denom = np.maximum((sum_sq[None, :] - sums * sums / n) / (n - 1), 1e-20)
    t_perm = (sums / n) / np.sqrt(denom / n)
    max_null[start:start+b] = np.max(t_perm, axis=1)
    del sums, denom, t_perm
crit = float(np.quantile(max_null, .95, method="higher"))
p_fwer = (1 + (max_null[:, None] >= t_obs[None, :]).sum(axis=0)) / (N_PERM + 1)

def write_map(values, name, dtype=np.float32):
    full = np.zeros(ref.shape, dtype=dtype)
    full[mask] = values
    hdr = ref.header.copy()
    hdr.set_data_dtype(dtype)
    nib.save(nib.Nifti1Image(full, ref.affine, hdr), OUT / name)

write_map(mean, "group_mean_gain_effect.nii.gz")
write_map(t_obs, "group_t_positive.nii.gz")
full_p = np.ones(ref.shape, dtype=np.float32)
full_p[mask] = p_fwer
hdr_p = ref.header.copy()
hdr_p.set_data_dtype(np.float32)
nib.save(nib.Nifti1Image(full_p, ref.affine, hdr_p), OUT / "group_p_fwer_positive.nii.gz")
write_map(np.where(p_fwer <= .05, t_obs, 0), "group_t_fwer05_positive.nii.gz")

# Descriptive 26-connected components of corrected positive voxels.
sig_full = np.zeros(ref.shape, dtype=bool)
sig_full[mask] = p_fwer <= .05
labels, n_clusters = label(sig_full, structure=generate_binary_structure(3, 3))
t_full = np.zeros(ref.shape, dtype=np.float64)
t_full[mask] = t_obs
p_full = np.ones(ref.shape, dtype=np.float64)
p_full[mask] = p_fwer
cluster_rows = []
for cid in range(1, n_clusters + 1):
    ijk = np.array(np.where(labels == cid)).T
    local_t = t_full[tuple(ijk.T)]
    peak = ijk[np.argmax(local_t)]
    cluster_rows.append({"cluster": cid, "voxels": len(ijk),
        "peak_x_mm": float(nib.affines.apply_affine(ref.affine, peak)[0]),
        "peak_y_mm": float(nib.affines.apply_affine(ref.affine, peak)[1]),
        "peak_z_mm": float(nib.affines.apply_affine(ref.affine, peak)[2]),
        "peak_t": float(local_t.max()),
        "peak_p_fwer": float(p_full[tuple(peak)])})
pd.DataFrame(cluster_rows).to_csv(OUT / "whole_brain_foci.tsv", sep="\t", index=False)

# A priori vmPFC summary: 10-mm-radius sphere around medial vmPFC at MNI
# (0, 40, -8), specified before examining group results. This is secondary;
# the confirmatory claim requires whole-brain max-T FWER support.
coords = np.indices(ref.shape).reshape(3, -1).T
xyz = nib.affines.apply_affine(ref.affine, coords)
roi_full = (np.linalg.norm(xyz - np.array([0., 40., -8.]), axis=1) <= 10).reshape(ref.shape)
roi = roi_full & mask
roi_subject = data[:, roi].mean(axis=1)
roi_mean = float(roi_subject.mean())
roi_sd = float(roi_subject.std(ddof=1))
roi_se = roi_sd / np.sqrt(n)
roi_t = roi_mean / roi_se
roi_p = float(stats.t.sf(roi_t, n-1))
roi_ci = stats.t.interval(.95, n-1, loc=roi_mean, scale=roi_se)
roi_d = roi_mean / roi_sd
roi_coords = [0., 40., -8.]

# Participant-level QC, including within-mask global summary. No data-driven
# exclusions: complete expected cohort and all maps pass geometry/finite checks.
subject_summary = pd.DataFrame({
    "participant_id": participants.participant_id,
    "mean_effect_common_mask": Y.mean(axis=1),
    "sd_effect_common_mask": Y.std(axis=1, ddof=1),
    "vmPFC_sphere_mean": roi_subject,
})
subject_summary.to_csv(OUT / "participant_qc_and_roi.tsv", sep="\t", index=False)

results = {
    "n_participants": int(n), "excluded": [], "map_dimensions": list(ref.shape),
    "voxel_size_mm": [float(x) for x in ref.header.get_zooms()[:3]],
    "common_nonzero_voxels": int(v), "mask_definition": "nonzero in all 54 participant maps",
    "model": "one-sample random-effects t test of participant gain-effect estimates against zero",
    "direction": "positive", "whole_brain_correction": "participant sign-flip max-t FWER, one-sided",
    "permutations": N_PERM, "random_seed": SEED, "maxT_t_critical_FWER_0.05": crit,
    "whole_brain_fwer_significant_voxels": int((p_fwer <= .05).sum()),
    "minimum_whole_brain_fwer_p": float(p_fwer.min()),
    "vmPFC_roi": {"definition": "10-mm sphere centered at MNI152NLin2009cAsym (0,40,-8)",
        "n_voxels": int(roi.sum()), "mean_effect": roi_mean, "sd_between_subjects": roi_sd,
        "t_53": float(roi_t), "p_one_sided_unadjusted": roi_p,
        "ci95_two_sided": [float(roi_ci[0]), float(roi_ci[1])], "cohen_dz": float(roi_d),
        "subject_effects": roi_subject.tolist()},
    "participant_global_effect_summary": {
        "mean_of_subject_means": float(Y.mean(axis=1).mean()),
        "subject_mean_range": [float(Y.mean(axis=1).min()), float(Y.mean(axis=1).max())],
        "subject_sd_range": [float(Y.std(axis=1, ddof=1).min()), float(Y.std(axis=1, ddof=1).max())]},
}
(OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
np.save(OUT / "maxT_null_distribution.npy", max_null)

# Figure 1: all-brain FWER map, with a vmPFC locator overlay.
stat_img = nib.load(str(OUT / "group_t_fwer05_positive.nii.gz"))
display = plotting.plot_glass_brain(stat_img, display_mode="lyrz", threshold=crit,
    colorbar=True, plot_abs=False,
    title="Positive group gain effect (max-T FWER < .05)")
display.add_markers([roi_coords], marker_color="yellow", marker_size=70, alpha=1)
display.savefig(FIG / "whole_brain_fwer_vmPFC.png", dpi=180)
plt.close("all")

# Figure 2: subject-level ROI effects and mean with 95% CI.
fig, ax = plt.subplots(figsize=(6.5, 4.2))
x = np.arange(1, n+1)
ax.scatter(x, roi_subject, s=22, color="#3b6f8f", alpha=.8, edgecolor="white", linewidth=.35)
ax.axhline(0, color="0.35", linewidth=1)
ax.axhline(roi_mean, color="#b34432", linewidth=2, label=f"Mean = {roi_mean:.3f}")
ax.axhspan(roi_ci[0], roi_ci[1], color="#b34432", alpha=.15, label="95% CI")
ax.set(xlabel="Participant (ordered by source table)", ylabel="Mean gain-effect estimate in vmPFC sphere",
       title="vmPFC gain-effect estimates")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIG / "vmPFC_participant_effects.png", dpi=180)
plt.close(fig)
print(json.dumps({k:v for k,v in results.items() if k != "vmPFC_roi"}, indent=2))
print(json.dumps({k:v for k,v in results["vmPFC_roi"].items() if k != "subject_effects"}, indent=2))
