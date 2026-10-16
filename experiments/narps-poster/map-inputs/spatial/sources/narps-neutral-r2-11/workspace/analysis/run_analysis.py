#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference gain cope maps."""
from pathlib import Path
import json, hashlib, platform
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from nilearn import datasets, image, plotting
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'input' / 'data'
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
SEED = 20261016
N_PERM = 9999
ALPHA = 0.05

# Cohort/map matching and image QC.
meta = pd.read_csv(ROOT / 'input' / 'participants.tsv', sep='\t')
files = sorted(DATA.glob('*_hypo1_cope.nii.gz'))
if len(files) != 54 or meta.shape[0] != 54:
    raise RuntimeError(f'Expected 54 maps and participants; got {len(files)} and {len(meta)}')
ids = [p.name.split('_')[0] for p in files]
if set(ids) != set(meta.participant_id) or meta.participant_id.duplicated().any():
    raise RuntimeError('Map IDs do not exactly match unique metadata IDs')
if set(meta['group'].dropna().unique()) != {'equalIndifference'}:
    raise RuntimeError('Metadata do not identify the complete equal-indifference cohort')
imgs = [nib.load(str(p)) for p in files]
ref = imgs[0]
if any(im.shape != ref.shape or not np.allclose(im.affine, ref.affine) for im in imgs):
    raise RuntimeError('Maps do not share an identical voxel grid')
arr = np.stack([im.get_fdata(dtype=np.float32) for im in imgs])
if not np.isfinite(arr).all():
    raise RuntimeError('Non-finite values found')
coverage = np.count_nonzero(arr, axis=0)
common_support = coverage == len(imgs)  # exact shared image support, independent of sign/magnitude
brain_mask_img = image.resample_to_img(
    datasets.load_mni152_brain_mask(resolution=2), ref, interpolation='nearest'
)
brain_mask = np.asarray(brain_mask_img.dataobj) > 0
mask = common_support & brain_mask
if mask.sum() < 100_000:
    raise RuntimeError('Unexpectedly small group intersection mask')
X = arr[:, mask].astype(np.float64, copy=False)
n, v = X.shape

# One-sample random-effects group model: mean participant contrast estimate > 0.
mean = X.mean(axis=0)
sd = X.std(axis=0, ddof=1)
se = sd / np.sqrt(n)
t_obs = mean / se
p_unc = stats.t.sf(t_obs, df=n-1)

# Sign-flip max-T permutation for one-sided, whole-brain FWE control.
# Under a symmetric zero-centered participant-effect null, flipping each map's sign
# is exchangeable. Use the maximum positive t over the full common mask each draw.
rng = np.random.default_rng(SEED)
sumsq = np.sum(X * X, axis=0)
max_null = np.empty(N_PERM, dtype=np.float64)
batch = 32
for start in range(0, N_PERM, batch):
    b = min(batch, N_PERM - start)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
    sums = signs @ X
    # Algebraically equivalent one-sample t, avoiding repeated variance calculations.
    denom2 = n * sumsq[None, :] - sums * sums
    tperm = sums * np.sqrt(n-1) / np.sqrt(np.maximum(denom2, np.finfo(float).tiny))
    max_null[start:start+b] = np.max(tperm, axis=1)
crit = float(np.quantile(max_null, 1-ALPHA, method='higher'))
max_obs = float(np.max(t_obs))
p_fwe = float((1 + np.count_nonzero(max_null >= max_obs)) / (N_PERM + 1))
p_fwe_vox = (1 + np.sum(max_null[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1) if False else None
sig = t_obs >= crit

# Bring whole-brain outputs back into the NIfTI grid.
def map_img(values, dtype=np.float32):
    out = np.zeros(ref.shape, dtype=dtype)
    out[mask] = values
    return nib.Nifti1Image(out, ref.affine, ref.header)
for name, values in [('mean_effect', mean), ('t_stat', t_obs), ('p_uncorrected', p_unc), ('fwe_significant', sig.astype(float))]:
    nib.save(map_img(values), OUT / f'{name}.nii.gz')

# Independent anatomical localization: AAL3 bilateral medial orbital frontal parcels.
# Atlas labels are resampled by nearest neighbor to the supplied MNI grid.
aal = datasets.fetch_atlas_aal(version='3v2', verbose=0)
aal_img = image.resample_to_img(aal.maps, ref, interpolation='nearest')
aal_arr = np.asarray(aal_img.dataobj)
labels = [x.decode() if isinstance(x, bytes) else str(x) for x in aal.labels]
roi_ids = [i for i, name in enumerate(labels) if 'Frontal_Med_Orb' in name]
if not roi_ids:
    raise RuntimeError('AAL3 medial orbital frontal labels were not found')
# AAL3 labels include Background at index 0; parcel integer values equal label indices.
roi_codes = roi_ids
roi_full = np.isin(aal_arr, roi_codes)
roi = roi_full[mask]
if roi.sum() == 0:
    raise RuntimeError('AAL3 vmPFC approximation has no voxels in group mask')
roi_X = X[:, roi]
roi_mean_vox = roi_X.mean(axis=0)
roi_sd_vox = roi_X.std(axis=0, ddof=1)
# Descriptive ROI-average participant effect, then one-sample one-sided t and CI.
roi_subject = roi_X.mean(axis=1)
pd.DataFrame({'participant_id': ids, 'group': 'equalIndifference',
              'mean_gain_effect_in_vmPFC_atlas_roi': roi_subject}).to_csv(
    OUT / 'participant_vmPFC_effects.tsv', sep='\t', index=False
)
rmean = float(roi_subject.mean())
rse = float(stats.sem(roi_subject))
r_t = float(rmean / rse)
r_p = float(stats.t.sf(r_t, df=n-1))
ci = stats.t.interval(0.95, df=n-1, loc=rmean, scale=rse)
roi_fwe_overlap = bool(np.any(sig[roi]))

# Peak locations in MNI coordinates and simple peak/ROI summaries.
ijk_peak = np.array(np.unravel_index(np.argmax(np.where(mask, np.pad(t_obs, (0,0)),0)), ref.shape)) if False else None
full_t = np.zeros(ref.shape); full_t[mask] = t_obs
peak_ijk = np.array(np.unravel_index(np.argmax(full_t), ref.shape))
peak_xyz = nib.affines.apply_affine(ref.affine, peak_ijk).tolist()
roi_best = np.where(roi, t_obs, -np.inf)
roi_peak_linear = np.flatnonzero(roi)[int(np.argmax(roi_best[roi]))]
# Convert compressed mask index to image coordinate.
roi_coords = np.argwhere(mask)[roi_peak_linear]
roi_peak_xyz = nib.affines.apply_affine(ref.affine, roi_coords).tolist()

# Map coverage and basic effect-map QC summaries.
nonzero_each = np.count_nonzero(arr, axis=(1,2,3))
whole_subject_mean = X.mean(axis=1)
summary = {
    'analysis': 'one-sample group model of participant gain contrast estimates',
    'n_participants': int(n), 'n_maps': len(files), 'excluded': [],
    'grid_shape': list(ref.shape), 'voxel_size_mm': [float(x) for x in nib.affines.voxel_sizes(ref.affine)],
    'common_support_before_standard_brain_mask_voxels': int(common_support.sum()),
    'standard_brain_mask_intersection_voxels': int(v),
    'common_support_voxels': int(v), 'common_support_volume_liters': float(v*np.prod(nib.affines.voxel_sizes(ref.affine))/1000),
    'individual_nonzero_voxels_min_median_max': [int(np.min(nonzero_each)), float(np.median(nonzero_each)), int(np.max(nonzero_each))],
    'estimate_mean_across_subject_voxel_means': float(whole_subject_mean.mean()),
    'permutation': {'method': 'participant-level sign flip; maximum positive t across all common-support voxels', 'draws': N_PERM, 'seed': SEED,
                    'one_sided': True, 'alpha': ALPHA, 'max_t_95pct_critical': crit, 'maximum_observed_t': max_obs,
                    'global_maxT_FWE_p_for_peak': p_fwe, 'significant_voxels': int(sig.sum())},
    'peak': {'t': max_obs, 'uncorrected_one_sided_p': float(p_unc[np.argmax(t_obs)]), 'mni_mm': [float(x) for x in peak_xyz]},
    'vmPFC_operationalization': {'atlas': 'AAL3 v3.2', 'labels': [labels[i] for i in roi_ids], 'n_voxels': int(roi.sum()),
                                'roi_mean_effect': rmean, 'roi_mean_se': rse, 'roi_mean_t': r_t,
                                'roi_mean_one_sided_p_descriptive': r_p, 'roi_mean_95pct_t_CI': [float(ci[0]), float(ci[1])],
                                'any_whole_brain_FWE_voxel_in_roi': roi_fwe_overlap,
                                'strongest_roi_voxel_t': float(np.max(t_obs[roi])), 'strongest_roi_voxel_mni_mm': [float(x) for x in roi_peak_xyz]},
    'software': {'python': platform.python_version(), 'numpy': np.__version__, 'nibabel': nib.__version__}
}
(OUT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')

# Descriptive distribution figure.
fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.hist(roi_subject, bins=12, color='#547a9e', edgecolor='white')
ax.axvline(0, color='black', lw=1, ls='--')
ax.axvline(rmean, color='#b24a3a', lw=2, label=f'Mean = {rmean:.3f}; 95% CI [{ci[0]:.3f}, {ci[1]:.3f}]')
ax.set(xlabel='Mean gain contrast estimate within AAL3 medial orbital frontal ROI', ylabel='Participants', title='Participant-level vmPFC gain effect estimates')
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(FIG/'participant_effect_distribution.png', dpi=180); plt.close(fig)

# Whole-brain group mean and corrected evidence views, with independent ROI outline.
roi_img = nib.Nifti1Image(roi_full.astype(np.uint8), ref.affine, ref.header)
mean_img = map_img(mean)
t_img = map_img(t_obs)
bg = datasets.load_mni152_template(resolution=2)
display = plotting.plot_stat_map(t_img, bg_img=bg, threshold=crit, display_mode='z', cut_coords=[-12,-4,4,12,20],
                       colorbar=True, title=f'Positive gain effect: sign-flip max-T FWE, t ≥ {crit:.2f}',
                       cmap='hot', black_bg=False, dim=0.15)
display.add_contours(roi_img, levels=[0.5], colors=['cyan'], linewidths=1.0)
display.savefig(FIG/'whole_brain_fwe.png', dpi=180); display.close()
# ROI estimate with uncertainty summarized across participants, presented on independent atlas mask.
roi_mean_values = np.zeros(v, dtype=float)
roi_mean_values[roi] = roi_mean_vox
roi_mean_img = map_img(roi_mean_values)
plotting.plot_stat_map(roi_mean_img, bg_img=bg, threshold=0.00001, display_mode='z', cut_coords=[-12,-4,4,12,20],
                       colorbar=True, title='Mean gain effect estimates in AAL3 medial orbital frontal parcels',
                       cmap='cold_hot', black_bg=False, output_file=str(FIG/'vmPFC_roi_effect.png'))

print(json.dumps(summary, indent=2))
