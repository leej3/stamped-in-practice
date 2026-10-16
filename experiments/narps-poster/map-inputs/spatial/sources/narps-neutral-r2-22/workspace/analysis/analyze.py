#!/usr/bin/env python3
"""Group inference for NARPS AO86 equal-indifference gain-effect maps."""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from nilearn import datasets, image, plotting
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis'
RESULTS, FIGS = OUT / 'results', OUT / 'figures'
SEED, N_PERM = 20261016, 10000
ALPHA = .05

src = json.loads((ROOT / 'input/sources.json').read_text())
participants = pd.read_csv(ROOT / 'input/participants.tsv', sep='\t')
assert len(participants) == 54 and participants.participant_id.is_unique
assert set(participants.group) == {'equalIndifference'}
paths = [ROOT / 'input' / name for name in src['files'] if name.endswith('.nii.gz')]
by_id = {p.stem.split('_')[0]: p for p in paths}
assert set(by_id) == set(participants.participant_id), 'Map and cohort IDs do not match'
paths = [by_id[x] for x in participants.participant_id]

# Verify retrieved-byte checksums and a common grid before analyzing.
images, checks = [], []
for pid, path in zip(participants.participant_id, paths):
    rec = src['files'][str(path.relative_to(ROOT / 'input'))]
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    checks.append({'participant_id': pid, 'sha256_match': sha == rec['sha256'], 'bytes_match': path.stat().st_size == rec['bytes']})
    if sha != rec['sha256'] or path.stat().st_size != rec['bytes']:
        raise ValueError(f'Input checksum/size mismatch for {pid}')
    images.append(nib.load(str(path)))
ref = images[0]
for pid, im in zip(participants.participant_id, images):
    if im.shape != ref.shape or not np.allclose(im.affine, ref.affine, atol=1e-5):
        raise ValueError(f'Grid mismatch: {pid}')

# Arrays are only ~55 x 0.9M; restrict inference to common nonzero support,
# treating exact zeros as outside the participant's brain mask.
arr = np.stack([im.get_fdata(dtype=np.float32) for im in images], axis=0)
finite = np.isfinite(arr).all(axis=0)
nonzero_fraction = np.mean(arr != 0, axis=0)
mask = finite & (nonzero_fraction == 1.0)
if mask.sum() == 0:
    raise ValueError('Empty common mask')
X = arr[:, mask].astype(np.float64)
n, v = X.shape
mean = X.mean(axis=0)
sd = X.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(n))
# One-sided parametric values describe uncorrected voxelwise evidence only.
p_unc = stats.t.sf(t_obs, df=n-1)

# One-sample sign-flip randomization, max-T FWE correction over the full mask.
# Under a symmetric null, independently sign-flipping each participant's map
# gives the null distribution; add-one correction gives valid Monte Carlo p's.
rng = np.random.default_rng(SEED)
sumsq = np.sum(X * X, axis=0)
max_t = np.empty(N_PERM, dtype=np.float64)
for start in range(0, N_PERM, 128):
    b = min(128, N_PERM-start)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(b,n))
    sums = signs @ X
    denom = np.sqrt(np.maximum((sumsq[None,:] - sums*sums/n)/(n-1), 1e-30))
    tperm = (sums / np.sqrt(n)) / denom
    max_t[start:start+b] = tperm.max(axis=1)
sorted_max_t = np.sort(max_t)
p_fwe = (1 + N_PERM - np.searchsorted(sorted_max_t, t_obs, side='left')) / (N_PERM + 1)

# Atlas-defined anatomical proxy: bilateral Harvard-Oxford cortical labels
# Frontal Medial, Subcallosal and Frontal Orbital. Atlas is independent of map effects.
atlas = datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')
atlas_img = image.resample_to_img(atlas.maps, ref, interpolation='nearest')
atlas_data = atlas_img.get_fdata().astype(int)
label_ids = {label: atlas.labels.index(label) for label in ['Frontal Medial Cortex','Subcallosal Cortex','Frontal Orbital Cortex']}
roi_full = np.isin(atlas_data, [label_ids['Frontal Medial Cortex'], label_ids['Subcallosal Cortex']])
roi_broad_full = np.isin(atlas_data, list(label_ids.values()))
roi = roi_full[mask]
roi_broad = roi_broad_full[mask]
if roi.sum() == 0:
    raise ValueError('Empty atlas ROI after resampling')

# A descriptive subject-level ROI mean and one-sample t interval; not the
# confirmatory decision (which is whole-brain FWE max-T).
roi_subj = X[:, roi].mean(axis=1)
roi_broad_subj = X[:, roi_broad].mean(axis=1)
roi_broad_mean = float(roi_broad_subj.mean())
roi_broad_se = float(roi_broad_subj.std(ddof=1) / np.sqrt(n))
roi_broad_ci = stats.t.interval(.95, df=n-1, loc=roi_broad_mean, scale=roi_broad_se)
roi_broad_p = float(stats.t.sf(roi_broad_mean/roi_broad_se, df=n-1))
roi_mean = float(roi_subj.mean())
roi_sd = float(roi_subj.std(ddof=1))
roi_se = roi_sd / np.sqrt(n)
roi_ci = stats.t.interval(.95, df=n-1, loc=roi_mean, scale=roi_se)
roi_t = roi_mean / roi_se
roi_p = float(stats.t.sf(roi_t, df=n-1))

# Reconstruct statistic maps in input geometry.
def save_map(values, name, dtype=np.float32, fill=0):
    full = np.full(ref.shape, fill, dtype=dtype)
    full[mask] = values
    img = nib.Nifti1Image(full, ref.affine, ref.header.copy())
    img.set_data_dtype(dtype)
    nib.save(img, RESULTS / name)
    return img
mean_img = save_map(mean, 'group_mean_cope.nii.gz')
t_img = save_map(t_obs, 'group_t_positive.nii.gz')
p_img = save_map(p_fwe, 'group_p_fwe_maxT.nii.gz', fill=np.nan)
sig_img = save_map((p_fwe <= ALPHA).astype(np.uint8), 'group_significant_fwe05.nii.gz', np.uint8)
mask_img = save_map(np.ones(v), 'common_analysis_mask.nii.gz', np.uint8)
roi_img = nib.Nifti1Image(roi_full.astype(np.uint8), ref.affine, ref.header.copy())
nib.save(roi_img, RESULTS/'vmPFC_proxy_harvard_oxford.nii.gz')

sig = p_fwe <= ALPHA
if sig.any():
    i = int(np.argmax(np.where(sig, t_obs, -np.inf)))
    peak_vox = np.array(np.unravel_index(np.flatnonzero(mask)[i], ref.shape))
    peak_xyz = nib.affines.apply_affine(ref.affine, peak_vox).tolist()
    peak_t, peak_p = float(t_obs[i]), float(p_fwe[i])
else:
    peak_xyz, peak_t, peak_p = None, None, None

qc = {
 'n_maps': n, 'n_participants': int(len(participants)), 'n_voxels_common_mask': int(v),
 'grid_shape': list(ref.shape), 'voxel_sizes_mm': list(map(float, ref.header.get_zooms()[:3])),
 'common_nonzero_mask_voxels': int(mask.sum()), 'participant_zero_fraction_range': [float(np.mean(a == 0)) for a in arr],
 'input_checksums_all_match': all(c['sha256_match'] and c['bytes_match'] for c in checks),
 'age_mean_sd': [float(participants.age.mean()), float(participants.age.std(ddof=1))],
 'gender_counts': participants.gender.value_counts().to_dict(), 'exclusions': [],
 'mask_definition': 'finite and nonzero in every participant map',
 'atlas_labels': label_ids, 'vmPFC_core_voxels_on_common_mask': int(roi.sum()), 'vmPFC_plus_orbitofrontal_voxels_on_common_mask': int(roi_broad.sum()),
}
(RESULTS/'quality_checks.json').write_text(json.dumps(qc, indent=2))
pd.DataFrame(checks).to_csv(RESULTS/'input_integrity.tsv', sep='\t', index=False)
pd.DataFrame([{
 'n': n, 'common_mask_voxels': v, 'permutations': N_PERM, 'seed': SEED,
 'maxT_critical_95': float(np.quantile(max_t, .95, method='higher')),
 'significant_voxels_FWE05': int(sig.sum()), 'any_whole_brain_support': bool(sig.any()),
 'positive_peak_xyz_mm': peak_xyz, 'positive_peak_t': peak_t, 'positive_peak_p_fwe': peak_p,
 'vmPFC_proxy_mean_cope': roi_mean, 'vmPFC_proxy_sd_across_participants': roi_sd,
 'vmPFC_proxy_CI95_low': float(roi_ci[0]), 'vmPFC_proxy_CI95_high': float(roi_ci[1]),
 'vmPFC_proxy_t': float(roi_t), 'vmPFC_proxy_p_one_sided_uncorrected': roi_p,
 'vmPFC_proxy_min_p_fwe': float(p_fwe[roi].min()), 'vmPFC_proxy_sig_voxels_FWE05': int(np.sum(sig & roi)),
 'vmPFC_core_mean_cope': roi_mean, 'vmPFC_core_CI95': [float(roi_ci[0]), float(roi_ci[1])],
 'vmPFC_core_min_p_fwe': float(p_fwe[roi].min()), 'vmPFC_core_sig_voxels_FWE05': int(np.sum(sig & roi)),
 'vmPFC_plus_orbitofrontal_mean_cope': roi_broad_mean, 'vmPFC_plus_orbitofrontal_CI95': [float(roi_broad_ci[0]), float(roi_broad_ci[1])],
 'vmPFC_plus_orbitofrontal_p_one_sided_uncorrected': roi_broad_p, 'vmPFC_plus_orbitofrontal_min_p_fwe': float(p_fwe[roi_broad].min()),
 'vmPFC_plus_orbitofrontal_sig_voxels_FWE05': int(np.sum(sig & roi_broad)),
}]).to_csv(RESULTS/'summary.tsv', sep='\t', index=False)
pd.DataFrame({'participant_id':participants.participant_id, 'vmPFC_core_mean_cope':roi_subj, 'vmPFC_plus_orbitofrontal_mean_cope':roi_broad_subj}).to_csv(RESULTS/'vmPFC_proxy_participant_values.tsv', sep='\t', index=False)

# Figure 1: use a standard MNI anatomical template only as a display underlay.
underlay = datasets.load_mni152_template(resolution=2)
# Figure 1: 3 aligned axial panels with maps and atlas proxy.
for img, name, title, cmap, threshold in [
    (mean_img, 'group_mean_effect.png', 'Mean gain-effect estimate', 'cold_hot', None),
    (t_img, 'group_t_uncorrected.png', 'Positive group t (display only; uncorrected)', 'hot', 2.0),
    (t_img, 'group_t_fwe_corrected.png', 'Positive group t; whole-brain max-T FWE p ≤ .05', 'hot', float(np.quantile(max_t, .95, method='higher'))),
]:
    display = plotting.plot_stat_map(img, bg_img=underlay, display_mode='z', cut_coords=[-8, 4, 16],
                                     threshold=threshold, cmap=cmap, colorbar=True, title=title, black_bg=False)
    display.savefig(FIGS / name, dpi=180)
    display.close()
display = plotting.plot_roi(roi_img, bg_img=underlay, display_mode='z', cut_coords=[-8, 4, 16],
                            cmap='autumn', colorbar=False, title='vmPFC proxy: medial frontal + subcallosal', black_bg=False, alpha=.8, dim=-.5)
display.savefig(FIGS/'vmPFC_proxy.png', dpi=180)
display.close()

# Figure 2: participant ROI means with group estimate and CI.
fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.scatter(np.arange(1,n+1), roi_subj, color='#496a81', s=25, alpha=.8, edgecolor='white', linewidth=.3)
ax.axhline(roi_mean, color='#b33b2e', lw=2, label=f'Mean = {roi_mean:.3f}')
ax.axhspan(roi_ci[0], roi_ci[1], color='#b33b2e', alpha=.14, label='95% t interval for mean')
ax.axhline(0, color='black', lw=.8, ls=':')
ax.set(xlabel='Participant (cohort order)', ylabel='Mean cope in vmPFC proxy (arbitrary model units)',
       title='Participant-level estimates in atlas-defined vmPFC proxy')
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIGS/'vmPFC_participant_estimates.png', dpi=180)
plt.close(fig)
print(json.dumps({'n':n,'voxels':v,'roi_voxels':int(roi.sum()),'maxT_critical':float(np.quantile(max_t,.95,method='higher')),'significant_voxels':int(sig.sum()),'roi_mean':roi_mean,'roi_ci':roi_ci,'roi_p':roi_p,'peak_xyz':peak_xyz,'peak_p_fwe':peak_p},indent=2))
