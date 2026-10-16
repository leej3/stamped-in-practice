#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference gain-effect maps.

Runs an intercept-only one-sample model and one-sided sign-flip max-T
permutation inference over the common nonzero coverage mask. No individual
models or time-series scans are processed.
"""
from pathlib import Path
import json, hashlib, glob, warnings
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats, ndimage
from nilearn import datasets, image, plotting
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent
DATA = ROOT / 'input' / 'data'
OUT = ROOT / 'results'
FIG = OUT / 'figures'
TAB = OUT / 'tables'
for p in (OUT, FIG, TAB): p.mkdir(parents=True, exist_ok=True)
B = 20000
SEED = 20261016
ALPHA = .05

manifest = json.loads((ROOT/'input/sources.json').read_text())
meta = pd.read_csv(ROOT/'input/participants.tsv', sep='\t')
entries = manifest['files']
paths = []
for participant in meta.participant_id:
    rel = f'data/{participant}_hypo1_cope.nii.gz'
    path = ROOT/'input'/rel
    expected = entries[rel]
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if len(raw) != expected['bytes'] or digest != expected['sha256']:
        raise ValueError(f'Input failed checksum: {path}')
    paths.append(path)

imgs = [nib.load(str(p)) for p in paths]
ref = imgs[0]
for p, im in zip(paths, imgs):
    if im.shape != ref.shape or not np.allclose(im.affine, ref.affine):
        raise ValueError(f'Inconsistent image geometry: {p}')
arr = np.stack([np.asarray(im.dataobj, dtype=np.float32) for im in imgs])
if not np.isfinite(arr).all(): raise ValueError('Non-finite map values')
# All maps are finite, but zeros indicate no estimate outside the individual
# support. Analyze voxels with nonzero coverage in every participant.
mask = np.all(arr != 0, axis=0)
if mask.sum() < 10000: raise ValueError('Unexpectedly small common support')
X = arr[:, mask].astype(np.float64)
n, v = X.shape
mean = X.mean(axis=0)
sd = X.std(axis=0, ddof=1)
tobs = mean / (sd / np.sqrt(n))
p_unc = stats.t.sf(tobs, df=n-1)

# Sign flip null for the one-sided alternative (positive gain association).
# Under H0, subject-level effect estimates are assumed sign-exchangeable.
rng = np.random.default_rng(SEED)
# sum of squares is invariant to sign flips. Chunking limits memory use.
sumsq = np.sum(X*X, axis=0)
max_null = np.empty(B, dtype=np.float32)
chunk = 40
for start in range(0, B, chunk):
    m = min(chunk, B-start)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(m,n))
    sums = signs @ X
    # equivalent to one-sample t, using signed sum and invariant sumsq
    denom = np.sqrt(np.maximum((n*sumsq[None,:] - sums*sums)/(n-1), 1e-30))
    tperm = sums / denom
    max_null[start:start+m] = np.max(tperm, axis=1)
    if (start+ m) % 1000 == 0 or start+m == B:
        print(f'permutations {start+m}/{B}', flush=True)

p_fwe = (1 + (max_null[:,None] >= tobs[None,:]).sum(axis=0)) / (B+1)
# whole-brain critical threshold from empirical maximum-null distribution
crit = float(np.quantile(max_null, 1-ALPHA, method='higher'))
sig = p_fwe < ALPHA

# Save spatial maps. Significance map is a whole-brain max-T FWE mask.
def save_map(vals, name, dtype=np.float32):
    vol = np.zeros(ref.shape, dtype=dtype)
    vol[mask] = vals.astype(dtype)
    out = nib.Nifti1Image(vol, ref.affine, ref.header.copy())
    nib.save(out, OUT/name)
    return out
mean_img = save_map(mean, 'mean_effect.nii.gz')
t_img = save_map(tobs, 't_statistic.nii.gz')
fwe_t_img = save_map(np.where(sig, tobs, 0), 't_fwe_p05.nii.gz')
p_img = save_map(p_fwe, 'p_fwe_maxT.nii.gz')

# Atlas-derived anatomical characterization, independent of the observed map.
# Operational vmPFC territory combines the ventral medial orbital and
# subcallosal Harvard-Oxford cortical labels. It is descriptive only;
# inference remains whole-brain.
atlas = datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm', data_dir=str(OUT/'atlas'), verbose=0)
atlas_img = image.resample_to_img(atlas.maps, ref, interpolation='nearest')
atlas_data = np.asarray(atlas_img.dataobj)
labels = list(atlas.labels)
roi_labels = ['Subcallosal Cortex', 'Frontal Orbital Cortex']
roi_ids = [labels.index(x) for x in roi_labels]
roi_mask = np.isin(atlas_data, roi_ids) & mask
if roi_mask.sum() == 0: raise ValueError('vmPFC operational ROI is empty')
roi_nvox = int(roi_mask.sum())
roi_mask_img = nib.Nifti1Image(roi_mask.astype(np.uint8), ref.affine, ref.header.copy())
nib.save(roi_mask_img, OUT/'vmPFC_anatomical_mask.nii.gz')
roi_subj = arr[:,roi_mask].mean(axis=1)
roi_mean = float(roi_subj.mean())
roi_sd = float(roi_subj.std(ddof=1))
roi_se = roi_sd/np.sqrt(n)
roi_ci = stats.t.interval(.95, n-1, loc=roi_mean, scale=roi_se)
roi_t, roi_p = stats.ttest_1samp(roi_subj, popmean=0, alternative='greater')
roi_d = roi_mean/roi_sd

# Corrected clusters, if any, labeled anatomically from atlas; use 26-connectivity.
sigvol = np.zeros(ref.shape, bool); sigvol[mask] = sig
cc, ncl = ndimage.label(sigvol, structure=np.ones((3,3,3), dtype=int))
rows=[]
for lab in range(1,ncl+1):
    coords = np.argwhere(cc==lab)
    if len(coords)==0: continue
    # coordinates index into original volume
    ii = np.ravel_multi_index(coords.T, ref.shape)
    flatmask = mask.ravel(); map_ix = np.full(flatmask.shape,-1,dtype=int); map_ix[np.flatnonzero(flatmask)] = np.arange(v)
    datidx = map_ix[ii]
    peak_idx = int(datidx[np.argmax(tobs[datidx])])
    peak_vox = np.unravel_index(np.flatnonzero(mask)[peak_idx], ref.shape)
    xyz = nib.affines.apply_affine(ref.affine, peak_vox)
    top = pd.Series(atlas_data[tuple(peak_vox)]).iloc[0]
    rows.append({'cluster':lab,'voxels':len(coords),'peak_t':float(tobs[peak_idx]),'peak_p_fwe':float(p_fwe[peak_idx]),'peak_x':float(xyz[0]),'peak_y':float(xyz[1]),'peak_z':float(xyz[2]),'atlas_label':labels[int(top)]})
clusters = pd.DataFrame(rows)
clusters.to_csv(TAB/'corrected_clusters.csv',index=False)

# Subject-level descriptive quality summaries. No participants excluded.
subject_means = arr[:,roi_mask].mean(axis=1)
q1,q3=np.quantile(subject_means,[.25,.75]); iqr=q3-q1
outlier_ids=meta.loc[(subject_means<q1-3*iqr)|(subject_means>q3+3*iqr),'participant_id'].tolist()
keep = ~meta.participant_id.isin(outlier_ids).to_numpy()
qc_sens_t, qc_sens_p = stats.ttest_1samp(subject_means[keep], popmean=0, alternative='greater')
qc_sens_mean = float(subject_means[keep].mean())
qc = meta[['participant_id','age','gender']].copy()
qc['vmPFC_mean_effect'] = subject_means
qc['robust_3IQR_flag'] = qc.participant_id.isin(outlier_ids)
qc.to_csv(TAB/'participant_qc.tsv',sep='\t',index=False)

# Save unthresholded and primary inference summaries.
summary = {
 'n':n,'n_excluded':0,'n_common_mask_voxels':int(v),'voxel_size_mm':list(map(float,ref.header.get_zooms()[:3])),
 'permutations':B,'seed':SEED,'alternative':'greater','familywise_alpha':ALPHA,
 'maxT_critical_95':crit,'maximum_observed_t':float(np.max(tobs)),
 'global_maxT_p':float((1+np.sum(max_null>=np.max(tobs)))/(B+1)),
 'significant_voxels':int(sig.sum()),'significant_clusters':int(ncl),
 'roi_name':'Harvard-Oxford cortical max-probability (25%) labels: '+', '.join(roi_labels),
 'roi_voxels':roi_nvox,'roi_max_positive_t':float(np.max(tobs[roi_mask[mask]])),
 'roi_best_voxel_p_fwe_maxT':float(np.min(p_fwe[roi_mask[mask]])),
 'roi_fwe_significant_voxels':int(np.sum(sig & roi_mask[mask])),
 'roi_mean_effect_estimate':roi_mean,'roi_sd_between_subjects':roi_sd,
 'roi_ci95_unadjusted':[float(roi_ci[0]),float(roi_ci[1])],'roi_t':float(roi_t),'roi_p_one_sided_unadjusted':float(roi_p),
 'roi_standardized_mean_d':float(roi_d),'roi_outlier_flags_3IQR':outlier_ids,
 'roi_sensitivity_excluding_flags_n':int(keep.sum()),'roi_sensitivity_mean':qc_sens_mean,
 'roi_sensitivity_t':float(qc_sens_t),'roi_sensitivity_p_one_sided_unadjusted':float(qc_sens_p),
 'software':{'python':__import__('sys').version.split()[0],'numpy':np.__version__,'scipy':__import__('scipy').__version__,'pandas':pd.__version__,'nibabel':nib.__version__,'nilearn':__import__('nilearn').__version__},
 'age_mean':float(meta.age.mean()),'age_sd':float(meta.age.std(ddof=1)),
 'gender_counts':meta.gender.value_counts().to_dict(),
 'map_min':float(arr.min()),'map_max':float(arr.max()),
 'mean_map_range':[float(mean.min()),float(mean.max())],
 'assumptions':'Participant effects are independent and sign-exchangeable under the null; the one-sample model weights participants equally.'
}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

# Figures: separate native Nilearn displays remain legible at report size.
template = datasets.load_mni152_template(resolution=2)
disp = plotting.plot_stat_map(mean_img, bg_img=template, display_mode='ortho',
    cut_coords=(0,40,-10), threshold=0.01, cmap='RdBu_r', colorbar=True,
    title='Mean participant gain effect (descriptive)')
disp.savefig(FIG/'mean_gain_effect_map.png', dpi=180)
disp.close()
disp = plotting.plot_stat_map(fwe_t_img, bg_img=template, display_mode='ortho',
    cut_coords=(-26,-100,-4), threshold=0, cmap='hot', colorbar=True,
    title='Positive t; whole-brain max-T FWE p < .05')
disp.savefig(FIG/'whole_brain_fwe_map.png', dpi=180)
disp.close()

fig,ax=plt.subplots(figsize=(6.4,4.6))
ax.axhline(0,color='0.45',lw=1)
order=np.argsort(subject_means)
ax.scatter(np.arange(n),subject_means[order],color='#276FBF',alpha=.85,s=28)
ax.axhline(roi_mean,color='#C33C54',lw=2,label=f'Mean = {roi_mean:.3g}')
ax.fill_between([-1,n],roi_ci[0],roi_ci[1],color='#C33C54',alpha=.12,label='95% CI of mean')
ax.set(xlabel='Participant (sorted by vmPFC effect)',ylabel='Mean vmPFC estimate (arbitrary model units)',title='Participant-level estimates in anatomical vmPFC mask')
ax.set_xticks([]); ax.legend(frameon=False); fig.tight_layout()
fig.savefig(FIG/'vmPFC_subject_effects.png',dpi=180,bbox_inches='tight')
plt.close(fig)
print(json.dumps(summary,indent=2))
