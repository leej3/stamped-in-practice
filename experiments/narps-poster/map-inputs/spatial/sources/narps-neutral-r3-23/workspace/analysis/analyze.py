#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference gain cope maps.

Primary inference: one-sample t statistic over participants, tested by participant-wise
sign flipping; voxelwise family-wise error controlled by the maximum t over the
common whole-brain analysis mask. The test is one-sided for positive gain effects.
"""
from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy import ndimage
import matplotlib.pyplot as plt
from nilearn import plotting

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'input' / 'data'
OUT = ROOT / 'analysis' / 'results'
FIG = ROOT / 'analysis' / 'figures'
OUT.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
N_PERM = 9999
SEED = 20261016

# Match map IDs to the pinned complete cohort; ordering is explicit and stable.
participants = pd.read_csv(ROOT / 'input' / 'participants.tsv', sep='\t')
participants = participants.loc[participants.group.eq('equalIndifference')].copy()
participants['map_path'] = participants.participant_id.map(lambda s: DATA / f'{s}_hypo1_cope.nii.gz')
missing = participants.loc[~participants.map_path.map(Path.exists), 'participant_id'].tolist()
if missing: raise FileNotFoundError(f'Missing participant maps: {missing}')
if len(participants) != 54: raise ValueError(f'Expected 54 participants, got {len(participants)}')

imgs = [nib.load(str(p)) for p in participants.map_path]
ref = imgs[0]
for p, im in zip(participants.participant_id, imgs):
    if im.shape != ref.shape or not np.allclose(im.affine, ref.affine, atol=1e-5):
        raise ValueError(f'Geometry mismatch for {p}')
    if not np.isfinite(im.get_fdata(dtype=np.float32)).all():
        raise ValueError(f'Non-finite values for {p}')
# Exact zero is background in these cope maps. Requiring nonzero support in >=90%
# of the cohort avoids edge voxels where missing support could be mistaken for zero.
vols = np.stack([im.get_fdata(dtype=np.float32) for im in imgs], axis=0)
nonzero_n = np.count_nonzero(vols, axis=0)
mask = nonzero_n >= int(np.ceil(.90 * len(participants)))
if not mask.any(): raise ValueError('Empty common-support mask')
Y = vols[:, mask].astype(np.float64)   # participants x voxels
n, v = Y.shape
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(n))
p_unc = stats.t.sf(t_obs, df=n-1)

# Monte-Carlo sign-flip max-t inference. Recompute the studentized statistic under
# each participant-level sign pattern; max statistic spans every masked voxel.
rng = np.random.default_rng(SEED)
sumsq = np.einsum('ij,ij->j', Y, Y)
max_t = np.empty(N_PERM, dtype=np.float64)
chunk = 32
for start in range(0, N_PERM, chunk):
    m = min(chunk, N_PERM-start)
    signs = rng.choice(np.array([-1., 1.]), size=(m, n))
    sums = signs @ Y
    means = sums / n
    variances = np.maximum((sumsq[None, :] - n * means**2) / (n-1), 0)
    ts = means / np.sqrt(np.maximum(variances, 1e-30) / n)
    max_t[start:start+m] = np.max(ts, axis=1)
# Monte Carlo corrected p: finite-sample plus-one correction.
p_fwe = (1 + np.sum(max_t[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)

# Map output arrays back to reference image space.
def save_map(name, values, dtype=np.float32):
    arr = np.zeros(ref.shape, dtype=dtype); arr[mask] = values.astype(dtype)
    nib.save(nib.Nifti1Image(arr, ref.affine, ref.header), OUT / name)
save_map('group_mean_cope.nii.gz', mean)
save_map('group_t_positive.nii.gz', t_obs)
save_map('group_p_uncorrected.nii.gz', p_unc)
save_map('group_p_fwe_maxT.nii.gz', p_fwe)
save_map('analysis_mask.nii.gz', np.ones(mask.sum(), dtype=np.uint8), np.uint8)

# Anatomical a priori vmPFC proxy, specified in MNI coordinates before inspection:
# medial (|x|<=10), anterior (y=30..60), ventral (z=-20..0), all mm.
# This descriptive ROI does not define significance; whole-brain max-T is primary.
ijk = np.indices(ref.shape).reshape(3, -1)
xyz = nib.affines.apply_affine(ref.affine, ijk.T)
roi_full = ((np.abs(xyz[:,0]) <= 10) & (xyz[:,1] >= 30) & (xyz[:,1] <= 60) &
            (xyz[:,2] >= -20) & (xyz[:,2] <= 0)).reshape(ref.shape)
roi = roi_full & mask
if roi.sum() == 0: raise ValueError('vmPFC ROI does not intersect analysis mask')
Yroi = vols[:, roi]
roi_subj = Yroi.mean(axis=1)
roi_t = stats.ttest_1samp(roi_subj, 0, alternative='greater')
roi_perm_n = N_PERM
# ROI sign-flip test is a descriptive, uncorrected sensitivity result (not primary).
roi_sign = rng.choice(np.array([-1., 1.]), size=(roi_perm_n, n))
obs_roi_t = roi_t.statistic
perm_roi_mean = (roi_sign * roi_subj[None, :]).mean(axis=1)
perm_roi_sd = (roi_sign * roi_subj[None, :]).std(axis=1, ddof=1)
perm_roi_t = perm_roi_mean / (perm_roi_sd / np.sqrt(n))
p_roi_perm = (1 + np.sum(perm_roi_t >= obs_roi_t))/(roi_perm_n+1)

# Participant level QC; no outcome-based exclusions.
qc = participants[['participant_id','group','gender','age']].copy()
qc['wholemask_mean_cope'] = Y.mean(axis=1)
qc['wholemask_sd_cope'] = Y.std(axis=1, ddof=1)
qc['vmPFC_mean_cope'] = roi_subj
qc.to_csv(OUT / 'participant_qc.tsv', sep='\t', index=False)

# Summaries and multiple comparison table.
peak_idx = int(np.argmax(t_obs))
peak_ijk = np.argwhere(mask)[peak_idx]
peak_xyz = nib.affines.apply_affine(ref.affine, peak_ijk)
sig = p_fwe <= .05
results = {
 'n_participants': n, 'n_excluded': 0, 'analysis_mask_voxels': int(v),
 'mask_rule': 'voxels nonzero in at least 90% (>=49/54) of participant cope maps',
 'permutations': N_PERM, 'seed': SEED, 'inference': 'one-sided participant sign-flip max-t, whole-mask FWE',
 'alpha': .05, 'n_fwe_significant_voxels': int(sig.sum()),
 'max_observed_t': float(t_obs[peak_idx]), 'peak_mni_mm': [float(z) for z in peak_xyz],
 'peak_mean_cope': float(mean[peak_idx]), 'peak_p_fwe': float(p_fwe[peak_idx]),
 'vmPFC_roi_definition_mni_mm': {'x':[-10,10], 'y':[30,60], 'z':[-20,0]},
 'vmPFC_roi_voxels': int(roi.sum()), 'vmPFC_mean_cope': float(roi_subj.mean()),
 'vmPFC_sd_subject_means': float(roi_subj.std(ddof=1)), 'vmPFC_t': float(obs_roi_t),
 'vmPFC_p_parametric_one_sided_uncorrected': float(roi_t.pvalue),
 'vmPFC_p_signflip_one_sided_uncorrected': float(p_roi_perm),
 'vmPFC_mean_cope_95ci': [float(z) for z in stats.t.interval(.95, df=n-1, loc=roi_subj.mean(), scale=stats.sem(roi_subj))],
 'all_finite': True, 'geometry_common': True,
 'nonzero_voxels_per_subject_min_median_max': [int(np.count_nonzero(vols[i])) for i in []]
}
# Spatial localization and cohort descriptors for the report.
roi_masked = roi[mask]
roi_peak_i = int(np.argmax(t_obs[roi_masked]))
roi_coords = np.argwhere(roi)[roi_peak_i]
roi_peak_xyz = nib.affines.apply_affine(ref.affine, roi_coords)
results['vmPFC_n_fwe_significant_voxels'] = int(np.sum(sig & roi_masked))
results['vmPFC_max_t'] = float(t_obs[roi_masked][roi_peak_i])
results['vmPFC_max_t_mni_mm'] = [float(z) for z in roi_peak_xyz]
results['age_mean_sd_years'] = [float(participants.age.mean()), float(participants.age.std(ddof=1))]
results['gender_counts'] = {str(k): int(v) for k, v in participants.gender.value_counts().sort_index().items()}
sig_full = np.zeros(ref.shape, dtype=bool); sig_full[mask] = sig
labels, n_clusters = ndimage.label(sig_full, structure=np.ones((3,3,3), dtype=int))
cluster_rows = []
for label_id in range(1, n_clusters+1):
    coords = np.argwhere(labels == label_id)
    centroid = nib.affines.apply_affine(ref.affine, coords.mean(axis=0))
    cluster_rows.append({'cluster': label_id, 'voxels': len(coords), 'centroid_x': centroid[0],
                         'centroid_y': centroid[1], 'centroid_z': centroid[2]})
pd.DataFrame(cluster_rows).to_csv(OUT/'fwe_clusters.tsv', sep='\t', index=False)
counts = np.count_nonzero(vols, axis=(1,2,3))
results['nonzero_voxels_per_subject_min_median_max'] = [int(counts.min()), int(np.median(counts)), int(counts.max())]
(OUT / 'summary.json').write_text(json.dumps(results, indent=2) + '\n')
pd.DataFrame({'mni_x': [float(peak_xyz[0])], 'mni_y':[float(peak_xyz[1])], 'mni_z':[float(peak_xyz[2])],
              't': [float(t_obs[peak_idx])], 'mean_cope':[float(mean[peak_idx])],
              'p_fwe_maxT':[float(p_fwe[peak_idx])]}).to_csv(OUT/'wholebrain_peak.tsv', sep='\t', index=False)
pd.DataFrame({'mni_x': xyz[mask.reshape(-1)][np.argsort(p_fwe)[:min(20,v)],0],
              'mni_y': xyz[mask.reshape(-1)][np.argsort(p_fwe)[:min(20,v)],1],
              'mni_z': xyz[mask.reshape(-1)][np.argsort(p_fwe)[:min(20,v)],2],
              't': t_obs[np.argsort(p_fwe)[:min(20,v)]],
              'mean_cope': mean[np.argsort(p_fwe)[:min(20,v)]],
              'p_fwe_maxT': p_fwe[np.argsort(p_fwe)[:min(20,v)]]}).to_csv(OUT/'top_voxels.tsv', sep='\t', index=False)

# Figure 1: group mean effect and whole-brain FWE-significant mask overlay.
mean_img = nib.load(str(OUT/'group_mean_cope.nii.gz'))
sig_img = nib.load(str(OUT/'group_p_fwe_maxT.nii.gz'))
sig_data = (sig_img.get_fdata() <= .05) & mask
sig_nifti = nib.Nifti1Image(sig_data.astype(np.uint8), ref.affine)
fig = plt.figure(figsize=(13,4.3))
display = plotting.plot_stat_map(mean_img, threshold=None, display_mode='z', cut_coords=[-12,-4,4,12,20],
                                 cmap='RdBu_r', colorbar=True, figure=fig, title='Mean participant gain-effect cope; black = max-T FWE p ≤ .05')
display.add_contours(sig_nifti, levels=[.5], colors='black', linewidths=1.2)
display.savefig(FIG/'wholebrain_mean_and_fwe.png', dpi=180)
plt.close(fig)

# Figure 2: distribution of participant ROI averages with mean and CI.
fig, ax = plt.subplots(figsize=(7,4.2))
ax.axhline(0, color='0.45', lw=1)
ax.scatter(np.arange(1,n+1), roi_subj, s=24, alpha=.78, color='#245b8f', edgecolor='white', linewidth=.35)
ci = results['vmPFC_mean_cope_95ci']
ax.axhline(roi_subj.mean(), color='#bd4b32', lw=2, label='Mean across participants')
ax.fill_between([0,n+1], ci[0], ci[1], color='#bd4b32', alpha=.16, label='95% CI for mean')
ax.set(xlim=(0,n+1), xlabel='Participant (ordered by ID)', ylabel='Mean gain-effect cope in vmPFC ROI',
       title='vmPFC ROI participant effects')
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(FIG/'vmPFC_participant_effects.png', dpi=180); plt.close(fig)

print(json.dumps(results, indent=2))
