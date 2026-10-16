#!/usr/bin/env python3
"""Group inference for NARPS AO86 equal-indifference gain effect maps.

Runs a one-sample, positive-direction voxelwise t test with participant-wise
sign-flip max-T family-wise error correction over the common nonzero mask.
"""
from __future__ import annotations
import json, os
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from scipy.ndimage import label

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'input' / 'data'
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
N_PERM = int(os.environ.get('NARPS_N_PERM', '5000'))
SEED = 20261016

participants = pd.read_csv(ROOT / 'input' / 'participants.tsv', sep='\t')
participants = participants.loc[participants.group.eq('equalIndifference')].copy()
participants['participant_id'] = participants.participant_id.astype(str)
paths = {p.name.split('_')[0]: p for p in DATA.glob('sub-*_hypo1_cope.nii.gz')}
expected = participants.participant_id.tolist()
if set(paths) != set(expected):
    raise RuntimeError(f'Input mismatch: expected {len(expected)}, found {len(paths)}; '
                       f'missing={sorted(set(expected)-set(paths))}, extra={sorted(set(paths)-set(expected))}')

imgs, arrays = [], []
for sid in expected:
    img = nib.load(str(paths[sid]))
    if imgs and (img.shape != imgs[0].shape or not np.allclose(img.affine, imgs[0].affine)):
        raise RuntimeError(f'Spatial mismatch for {sid}')
    d = img.get_fdata(dtype=np.float32)
    if not np.isfinite(d).all():
        raise RuntimeError(f'Nonfinite values in {sid}')
    if not np.any(d):
        raise RuntimeError(f'Empty map for {sid}')
    imgs.append(img); arrays.append(d)

# Common valid support: all participants have nonzero estimates at a voxel.
# Supplied images encode outside-map support as zero, so this conservative
# intersection avoids treating unavailable voxels as measured zero effects.
Y = np.stack(arrays, axis=0)  # n x i x j x k, float32
mask = np.all(Y != 0, axis=0)
if mask.sum() == 0:
    raise RuntimeError('No common nonzero voxel support')
X = Y[:, mask].astype(np.float64, copy=False)
n, v = X.shape

# One-sample t statistic, positive direction.
sum_x = X.sum(axis=0)
sumsq_x = np.einsum('ij,ij->j', X, X)
mean = sum_x / n
var = np.maximum((sumsq_x - sum_x * sum_x / n) / (n - 1), 0)
se = np.sqrt(var / n)
t_obs = np.divide(mean, se, out=np.zeros_like(mean), where=se > 0)
p_unc = stats.t.sf(t_obs, n - 1)

# Sign-flip null for one-sample inference; max-T controls FWE over every voxel
# in the analysis mask. Batching bounds memory, and the plus-one p correction
# ensures valid Monte Carlo p-values.
rng = np.random.default_rng(SEED)
max_null = np.empty(N_PERM, dtype=np.float32)
batch = 100
for start in range(0, N_PERM, batch):
    b = min(batch, N_PERM - start)
    signs = rng.choice(np.array([-1.0, 1.0], dtype=np.float64), size=(b, n))
    sums = signs @ X
    # sign flips preserve each participant's magnitude at each voxel
    tsq = np.maximum(sumsq_x[None, :] - sums * sums / n, 1e-30) / (n - 1)
    t_perm = (sums / n) / np.sqrt(tsq / n)
    max_null[start:start+b] = np.max(t_perm, axis=1)

p_fwe = (1 + np.sum(max_null[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)
sig = p_fwe < 0.05
sig_full = np.zeros(mask.shape, dtype=bool)
sig_full[mask] = sig

# Independent, anatomically motivated vmPFC summary: 10 mm-radius sphere at
# MNI152 (0, 40, -10), centered in medial orbitofrontal/ventral medial PFC.
# This is a descriptive ROI and does not replace the whole-brain corrected test.
ijk = np.indices(imgs[0].shape).reshape(3, -1).T
xyz = nib.affines.apply_affine(imgs[0].affine, ijk)
roi_full = np.sum((xyz - np.array([0., 40., -10.]))**2, axis=1) <= 10.**2
roi = roi_full.reshape(imgs[0].shape) & mask
if not roi.any():
    raise RuntimeError('vmPFC sphere has no voxels in common mask')
roi_values = Y[:, roi].mean(axis=1).astype(float)
roi_sig_voxels = int(np.sum(sig_full & roi))
roi_t, roi_p2 = stats.ttest_1samp(roi_values, 0)
roi_p1 = float(stats.t.sf(roi_t, n - 1)) if roi_t >= 0 else float(1 - stats.t.cdf(roi_t, n - 1))
roi_mean = float(roi_values.mean())
roi_sd = float(roi_values.std(ddof=1))
roi_se = roi_sd / np.sqrt(n)
roi_ci = [float(roi_mean - stats.t.ppf(.975, n-1)*roi_se),
          float(roi_mean + stats.t.ppf(.975, n-1)*roi_se)]

# Descriptive quality checks. Flag potential outliers for review; do not remove
# participants based on observed effects.
roi_med = np.median(roi_values)
roi_mad = np.median(np.abs(roi_values - roi_med))
roi_robust_z = (roi_values - roi_med) / (1.4826 * roi_mad) if roi_mad > 0 else np.zeros(n)
map_means = Y[:, mask].mean(axis=1)
map_sds = Y[:, mask].std(axis=1, ddof=1)
subject_rows=[]
for i,sid in enumerate(expected):
    subject_rows.append({'participant_id':sid,'roi_mean_effect':float(roi_values[i]),
                         'roi_robust_z':float(roi_robust_z[i]),
                         'whole_mask_mean_effect':float(map_means[i]),
                         'whole_mask_sd':float(map_sds[i]),
                         'review_flag_abs_roi_robust_z_gt_3':bool(abs(roi_robust_z[i])>3),
                         'included':True})
pd.DataFrame(subject_rows).to_csv(OUT/'participant_qc.csv', index=False)

# Reconstruct volume outputs.
def image_from_masked(vals, dtype=np.float32):
    full = np.zeros(mask.shape, dtype=dtype)
    full[mask] = np.asarray(vals, dtype=dtype)
    return nib.Nifti1Image(full, imgs[0].affine, imgs[0].header)
mean_img = image_from_masked(mean)
t_img = image_from_masked(t_obs)
p_img = image_from_masked(p_fwe)
thresholded = np.where(sig, t_obs, 0)
sig_img = image_from_masked(thresholded)
nib.save(mean_img, OUT/'group_mean_effect.nii.gz')
nib.save(t_img, OUT/'group_tstat.nii.gz')
nib.save(p_img, OUT/'group_p_fwe.nii.gz')
nib.save(sig_img, OUT/'group_tstat_fwe05.nii.gz')

# Primary figure: effect map, whole-brain corrected t map, and independent ROI.
aff = imgs[0].affine
z_coords = nib.affines.apply_affine(aff, np.c_[np.zeros(mask.shape[2]),
                                               np.zeros(mask.shape[2]),
                                               np.arange(mask.shape[2])])[:, 2]
kz = int(np.argmin(np.abs(z_coords - (-4))))
z_mm = float(z_coords[kz])
xlo, xhi = sorted([float(aff[0,3] - aff[0,0]/2),
                   float(aff[0,3] + aff[0,0]*(mask.shape[0]-.5))])
ylo, yhi = sorted([float(aff[1,3] - aff[1,1]/2),
                   float(aff[1,3] + aff[1,1]*(mask.shape[1]-.5))])
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 5), constrained_layout=True)
effect_slice = mean_img.get_fdata()[:, :, kz].T
mask_slice = mask[:, :, kz].T
effect_slice = np.ma.masked_where(~mask_slice, effect_slice)
lim = float(np.quantile(np.abs(effect_slice.compressed()), .99))
im1 = ax1.imshow(effect_slice, origin='lower', extent=[xlo,xhi,ylo,yhi],
                 cmap='RdBu_r', vmin=-lim, vmax=lim, interpolation='nearest')
fig.colorbar(im1, ax=ax1, shrink=.75, label='Mean effect (COPE units)')
ax1.set_title(f'Mean gain effect, z = {z_mm:.1f} mm', fontsize=10)
sig_slice = sig_img.get_fdata()[:, :, kz].T
sig_slice = np.ma.masked_where(~(sig_slice > 0), sig_slice)
im2 = ax2.imshow(sig_slice, origin='lower', extent=[xlo,xhi,ylo,yhi],
                 cmap='hot', vmin=0, vmax=max(float(t_obs.max()), 1), interpolation='nearest')
fig.colorbar(im2, ax=ax2, shrink=.75, label='t statistic')
ax2.set_title('Positive voxels, max-T FWE < .05', fontsize=10)
for ax in (ax1, ax2):
    ax.set_xlabel('MNI x (mm; radiological view)')
    ax.set_ylabel('MNI y (mm)')
    ax.set_xlim(xhi, xlo)
    ax.set_ylim(ylo, yhi)
ax3.scatter(np.ones(n)+rng.normal(0,.035,n), roi_values, s=24, alpha=.72,
            color='#276678', edgecolor='white', linewidth=.35)
ax3.errorbar([1.25], [roi_mean], yerr=[[roi_mean-roi_ci[0]],[roi_ci[1]-roi_mean]],
             fmt='D', color='#b54735', capsize=4, markersize=6, label='Mean and 95% CI')
ax3.axhline(0, color='0.35', lw=1, ls='--')
ax3.set_xlim(.75,1.55); ax3.set_xticks([1.15], ['vmPFC sphere'])
ax3.set_ylabel('Mean participant effect (COPE units)')
ax3.set_title('vmPFC ROI participant values', fontsize=10)
ax3.legend(frameon=False, fontsize=8, loc='best')
fig.suptitle('NARPS equal-indifference group: gain-effect maps (n = 54)', fontsize=13)
fig.savefig(FIG/'group_gain_vmPFC.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Supplementary distributions of voxelwise statistics and effect scale.
fig,ax=plt.subplots(figsize=(7,4.4), constrained_layout=True)
ax.hist(t_obs, bins=70, color='#426b83', alpha=.88)
ax.axvline(stats.t.ppf(.95,n-1), color='#b54735', ls='--', label='Uncorrected one-sided t threshold (.05)')
ax.set(xlabel='Voxelwise one-sample t statistic', ylabel='Number of voxels',
       title='Whole-brain voxelwise statistics in common mask')
ax.legend(frameon=False, fontsize=8)
fig.savefig(FIG/'voxel_t_distribution.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Report the maximum positive observed t and its corrected empirical p-value,
# and contiguous significant components for descriptive localization.
imax = int(np.argmax(t_obs))
max_xyz = xyz[np.flatnonzero(mask.ravel())[imax]].tolist()
components, n_components = label(sig_full)
cluster_summaries = []
for component in range(1, n_components + 1):
    ijk_component = np.argwhere(components == component)
    comp_t = t_img.get_fdata()[components == component]
    comp_xyz = nib.affines.apply_affine(imgs[0].affine, ijk_component)
    cluster_summaries.append({
        'n_voxels': int(len(ijk_component)),
        'peak_t': float(comp_t.max()),
        'peak_mni_mm': [float(x) for x in comp_xyz[np.argmax(comp_t)]],
        'mean_effect': float(mean_img.get_fdata()[components == component].mean())
    })
results = {
 'analysis':'one-sample positive-direction t test; participant-wise sign-flip max-T FWE',
 'n_participants':n, 'n_excluded':0, 'n_common_nonzero_voxels':int(v),
 'n_permutations':N_PERM, 'random_seed':SEED, 'minimum_attainable_mc_p':1/(N_PERM+1),
 'fwe_alpha':0.05, 'n_positive_voxels_fwe05':int(sig.sum()),
 'n_vmPFC_roi_voxels_fwe05':roi_sig_voxels,
 'positive_fwe_components_26_neighbor':cluster_summaries,
 'max_positive_t':float(t_obs[imax]),'max_positive_t_mni_mm':[float(x) for x in max_xyz],
 'max_positive_t_p_uncorrected_one_sided':float(p_unc[imax]),
 'max_positive_t_p_fwe':float(p_fwe[imax]),
 'roi':{'definition':'10 mm radius sphere centered at MNI152 (0, 40, -10); independent descriptive vmPFC summary',
        'n_voxels':int(roi.sum()),'mean_effect':roi_mean,'sd_between_participants':roi_sd,
        'se':float(roi_se),'ci95_t':[float(x) for x in roi_ci], 't':float(roi_t),
        'p_one_sided_uncorrected':roi_p1,'p_two_sided_uncorrected':float(roi_p2),
        'n_positive_participant_roi_means':int(np.sum(roi_values>0)),
        'median':float(np.median(roi_values)),'range':[float(roi_values.min()),float(roi_values.max())]},
 'quality':{'all_54_maps_present':True,'same_shape_affine':True,'all_values_finite':True,
            'empty_maps':0,'roi_abs_robust_z_gt_3':int(np.sum(np.abs(roi_robust_z)>3)),
            'no_effect_based_exclusions':True}
}
(OUT/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
