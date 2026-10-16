#!/usr/bin/env python3
"""Group inference for NARPS AO86 equal-indifference participant gain effects."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy.ndimage import label
from nilearn import datasets, image, plotting
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'input' / 'data'
OUT = ROOT / 'results'; FIG = ROOT / 'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
N_PERM = 10000
SEED = 20261016
ALPHA = .05

# Cohort lock: exact participant set from supplied TSV, sorted by identifier.
meta = pd.read_csv(ROOT / 'input' / 'participants.tsv', sep='\t')
paths = sorted(DATA.glob('*_hypo1_cope.nii.gz'))
by_id = {p.name.split('_')[0]: p for p in paths}
ids = sorted(meta.participant_id)
assert len(ids) == 54 and set(ids) == set(by_id) and len(paths) == 54
imgs = [nib.load(str(by_id[s])) for s in ids]
ref = imgs[0]
assert all(im.shape == ref.shape and np.allclose(im.affine, ref.affine) for im in imgs)
arrays = np.stack([im.get_fdata(dtype=np.float32) for im in imgs])
finite = np.isfinite(arrays).all(axis=0)
# Supplied effects use zero for outside-brain voxels. Common nonzero support avoids
# comparing different participant coverage; a standard MNI152 brain mask excludes
# non-brain edge/background voxels from whole-brain inference.
nonzero = np.all(arrays != 0, axis=0)
brain = image.resample_to_img(datasets.load_mni152_brain_mask(resolution=2), ref,
                              interpolation='nearest').get_fdata() > .5
mask = finite & nonzero & brain
X = arrays[:, mask].astype(np.float64)
n, v = X.shape
assert n == 54 and v > 10000

# QC: spatial coverage, global distribution and subject-level summary.
qc = []
for i, sid in enumerate(ids):
    a = arrays[i]
    vals = a[mask]
    qc.append({'participant_id':sid, 'age':int(meta.set_index('participant_id').loc[sid,'age']),
               'gender':meta.set_index('participant_id').loc[sid,'gender'],
               'nonzero_voxels':int(np.count_nonzero(a)), 'common_mask_mean':float(vals.mean()),
               'common_mask_sd':float(vals.std(ddof=1)), 'common_mask_min':float(vals.min()),
               'common_mask_max':float(vals.max()), 'n_nonfinite':int((~np.isfinite(a)).sum())})
pd.DataFrame(qc).to_csv(OUT/'participant_qc.tsv',sep='\t',index=False)

# One-sample positive-direction t test. Participants are the independent units.
mean = X.mean(axis=0)
sd = X.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(n))
df = n - 1
p_unc = stats.t.sf(t_obs, df)

# One-sided whole-brain max-T sign-flip permutation test. Sign flips are valid
# under the null of symmetric participant-level errors; each permutation's maximum
# t controls family-wise error over every voxel in the common-support mask.
rng = np.random.default_rng(SEED)
max_t = np.empty(N_PERM, dtype=np.float32)
# Batch multiplication uses optimized BLAS and avoids storing permuted volumes.
for start in range(0, N_PERM, 100):
    b = min(100, N_PERM-start)
    signs = rng.choice(np.array([-1.,1.]), size=(b,n))
    sums = signs @ X
    # sign flipping preserves each participant's squared observation
    ss = np.sum(X*X, axis=0)[None,:] - (sums*sums)/n
    var = np.maximum(ss/(n-1), 0)
    tp = (sums/n) / np.sqrt(var/n)
    max_t[start:start+b] = np.max(tp, axis=1)
    del signs, sums, ss, var, tp
max_t_sorted = np.sort(max_t)
# Search each observed t against the sorted permutation maxima to avoid a
# permutations-by-voxels temporary array.
p_fwe = (1 + (N_PERM - np.searchsorted(max_t_sorted, t_obs, side='left'))) / (N_PERM + 1)
pd.DataFrame({'permutation':np.arange(1,N_PERM+1), 'max_t':max_t}).to_csv(
    OUT/'permutation_max_t.tsv.gz',sep='\t',index=False,compression='gzip')

# Save maps on source grid with zero outside common support.
def save_map(vals, name, dtype=np.float32):
    out = np.zeros(ref.shape, dtype=dtype)
    out[mask] = vals
    nii = nib.Nifti1Image(out, ref.affine, ref.header)
    nii.set_data_dtype(dtype)
    nib.save(nii, OUT/name)
    return nii
mean_img = save_map(mean, 'mean_gain_effect.nii.gz')
t_img = save_map(t_obs, 'tstat_one_sample.nii.gz')
p_volume = np.ones(ref.shape, dtype=np.float32)
p_volume[mask] = p_fwe
p_img = nib.Nifti1Image(p_volume, ref.affine, ref.header)
p_img.set_data_dtype(np.float32)
nib.save(p_img, OUT/'p_fwe_maxT.nii.gz')
logp_img = save_map(-np.log10(np.maximum(p_fwe, 1/(N_PERM+1))), 'neglog10_p_fwe.nii.gz')

# Independent atlas label supports the anatomical localization. Harvard-Oxford
# cortical atlas, 25% max-probability; vmPFC operationalization: Frontal Medial
# Cortex label restricted to y >= 0 and z <= 0 in MNI coordinates. This is an
# explicit ventral medial subset, not a region used to select whole-brain results.
atlas = datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')
atlas_img = image.resample_to_img(atlas.maps, ref, interpolation='nearest')
labels = [str(x.decode() if isinstance(x, bytes) else x) for x in atlas.labels]
frontal_idx = next(i for i, label in enumerate(labels) if label.lower() == 'frontal medial cortex')
atlas_dat = atlas_img.get_fdata().astype(int)
ijk = np.indices(ref.shape)
xyz = nib.affines.apply_affine(ref.affine, np.moveaxis(ijk,0,-1))
vm_mask = mask & (atlas_dat == frontal_idx) & (xyz[...,1] >= 0) & (xyz[...,2] <= 0)
vm_idx = np.flatnonzero(vm_mask[mask])
vm_fwe_sig = p_fwe[vm_idx] <= ALPHA

# Label significant whole-brain voxels and identify overlap with anatomical ROI.
sig = p_fwe <= ALPHA
sig_vol = np.zeros(ref.shape, dtype=bool)
sig_vol[mask] = sig
coords = np.column_stack(np.where(sig_vol))
world = nib.affines.apply_affine(ref.affine, coords) if len(coords) else np.empty((0,3))
cluster_labels, n_clusters = label(sig_vol, structure=np.ones((3,3,3), dtype=int))
cluster_rows = []
for cluster_id in range(1, n_clusters+1):
    vox = np.column_stack(np.where(cluster_labels == cluster_id))
    tv = t_img.get_fdata()[cluster_labels == cluster_id]
    peak = vox[np.argmax(tv)]
    peak_world = nib.affines.apply_affine(ref.affine, peak)
    cluster_rows.append({'cluster':cluster_id,'voxels':len(vox),'peak_t':float(tv.max()),
                         'peak_x':float(peak_world[0]),'peak_y':float(peak_world[1]),
                         'peak_z':float(peak_world[2])})
pd.DataFrame(cluster_rows).to_csv(OUT/'fwe_clusters.tsv',sep='\t',index=False)
sig_roi = bool(np.any(vm_fwe_sig))
roi_mean = float(np.mean(mean[vm_idx])) if len(vm_idx) else float('nan')
roi_median_t = float(np.median(t_obs[vm_idx])) if len(vm_idx) else float('nan')
roi_max_t = float(np.max(t_obs[vm_idx])) if len(vm_idx) else float('nan')
roi_max_p = float(np.min(p_fwe[vm_idx])) if len(vm_idx) else float('nan')
roi_mean_t = float(np.mean(t_obs[vm_idx])) if len(vm_idx) else float('nan')
# An interpretable unthresholded ROI summary with t-based CI; descriptive, not the
# inferential basis for hypothesis support.
roi_data = arrays[:, vm_mask]
subject_roi = roi_data.mean(axis=1)
roi_se = subject_roi.std(ddof=1)/np.sqrt(n)
roi_ci = stats.t.interval(.95, df, loc=subject_roi.mean(), scale=roi_se)

summary = {
 'n_participants':n, 'n_voxels_common_mask':int(v), 'mask_rule':'finite and nonzero in all 54 maps, intersected with resampled MNI152 2 mm brain mask',
 'permutations':N_PERM, 'seed':SEED, 'test':'one-sided positive one-sample t; sign-flip max-T whole-brain FWE',
 'minimum_attainable_p':1/(N_PERM+1), 'whole_brain_fwe_alpha':ALPHA,
 'n_fwe_significant_voxels':int(sig.sum()), 'n_fwe_significant_clusters_26conn':int(n_clusters),
 'n_positive_voxels_uncorrected_p_lt_05':int(np.sum((p_unc < .05) & (t_obs > 0))),
 'max_t_whole_brain':float(np.max(t_obs)), 'min_p_fwe_whole_brain':float(np.min(p_fwe)),
 'permutation_max_t_range':[float(max_t.min()),float(max_t.max())],
 'significant_peak_mni_mm':(world[np.argmax(t_obs[np.flatnonzero(sig)])].round(1).tolist() if np.any(sig) else None),
 'vmPFC_roi_definition':'Harvard-Oxford cortical Frontal Medial Cortex max-probability 25%, MNI y>=0 and z<=0; descriptive localization only',
 'vmPFC_n_voxels':int(vm_mask.sum()), 'vmPFC_mean_across_voxels_effect':roi_mean,
 'vmPFC_subject_mean_effect':float(subject_roi.mean()), 'vmPFC_subject_mean_95ci': [float(roi_ci[0]),float(roi_ci[1])],
 'vmPFC_mean_t_across_voxels':roi_mean_t, 'vmPFC_median_voxel_t':roi_median_t,
 'vmPFC_max_voxel_t':roi_max_t, 'vmPFC_min_voxel_p_fwe':roi_max_p,
 'vmPFC_max_voxel_p_uncorrected':float(np.min(p_unc[vm_idx])) if len(vm_idx) else None,
 'vmPFC_has_fwe_significant_voxel':sig_roi,
 'all_subject_maps_finite':bool(np.isfinite(arrays).all()), 'excluded_participants':[],
 'subject_mean_effect_range':[float(subject_roi.min()),float(subject_roi.max())],
 'subject_global_sd_range':[float(np.min([q['common_mask_sd'] for q in qc])),float(np.max([q['common_mask_sd'] for q in qc]))]
}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
pd.DataFrame({'voxelwise_t':t_obs,'p_uncorrected':p_unc,'p_fwe_maxT':p_fwe,'mean_effect':mean}).to_csv(OUT/'voxelwise_results_common_mask.tsv.gz',sep='\t',index=False,compression='gzip')

# Whole-brain visual: display unthresholded t and FWE significant voxels.
# MNI template is only a background for localization.
template = datasets.load_mni152_template(resolution=2)
# Positive-direction uncorrected display only. Whole-brain support is assessed
# from the max-T family-wise corrected results above.
pos_unc_img = save_map(np.where(t_obs > stats.t.ppf(.95,df), t_obs, 0),
                       'tstat_positive_uncorrected_p05.nii.gz')
plotting.plot_stat_map(pos_unc_img, bg_img=template, threshold=0, display_mode='z',
                       cut_coords=[-24,-12,0,12,24,36,48], cmap='hot',
                       title='Positive gain effect: uncorrected p < .05 (display only)',
                       colorbar=True, output_file=str(FIG/'whole_brain_t_uncorrected.png'))
# Save corrected effects separately. An all-zero map means none pass.
sig_img = save_map(np.where(sig, t_obs, 0), 'tstat_fwe_significant.nii.gz')
plotting.plot_stat_map(sig_img, bg_img=template, threshold=0, display_mode='z',
                       cut_coords=[-12,-8,-4,0,4,8,12], cmap='hot',
                       title='Positive gain effect: whole-brain max-T FWE p ≤ .05',
                       colorbar=True, output_file=str(FIG/'whole_brain_fwe.png'))

# Anatomical ROI descriptive estimate plot; one participant is one point.
fig, ax = plt.subplots(figsize=(7.2,4.6))
ax.axhline(0,color='0.5',lw=1)
ax.scatter(np.arange(1,n+1), subject_roi, s=24, alpha=.75, edgecolor='none')
ax.axhline(subject_roi.mean(),color='#b2182b',lw=2,label=f'Mean {subject_roi.mean():.3f}')
ax.fill_between([1,n], roi_ci[0],roi_ci[1],color='#b2182b',alpha=.14,label='95% t interval for mean')
ax.set(xlabel='Participant (sorted ID)',ylabel='Mean gain-effect estimate in vmPFC mask',
       title='Participant-level vmPFC summaries (descriptive)')
ax.set_xlim(.5,n+.5)
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(FIG/'vmPFC_subject_estimates.png',dpi=180); plt.close(fig)
print(json.dumps(summary,indent=2))
