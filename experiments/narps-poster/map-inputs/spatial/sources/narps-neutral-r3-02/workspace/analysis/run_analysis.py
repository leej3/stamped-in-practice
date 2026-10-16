#!/usr/bin/env python3
"""Group inference from the supplied NARPS AO86 participant cope maps."""
from pathlib import Path
import json, hashlib, platform, sys, time
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats, ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from nilearn import plotting, image

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'input'
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
B = 5000
SEED = 20261016
ALPHA = 0.05

meta = pd.read_csv(INPUT/'participants.tsv', sep='\t')
files = sorted((INPUT/'data').glob('*_hypo1_cope.nii.gz'))
ids = [p.name.split('_')[0] for p in files]
assert len(meta) == 54 and meta.participant_id.is_unique
assert len(files) == 54 and len(set(ids)) == 54
assert set(ids) == set(meta.participant_id), 'Map IDs do not match metadata'

imgs, arrs, qc = [], [], []
for p in files:
    im = nib.load(p)
    d = im.get_fdata(dtype=np.float32)
    imgs.append(im); arrs.append(d)
    qc.append({'participant_id':p.name.split('_')[0], 'shape':'x'.join(map(str, im.shape)),
               'finite_fraction':float(np.isfinite(d).mean()),
               'nonzero_voxels':int(np.count_nonzero(d)),
               'mean_nonzero':float(np.mean(d[d!=0])),
               'sd_nonzero':float(np.std(d[d!=0])),
               'min':float(np.min(d)), 'max':float(np.max(d))})
ref = imgs[0]
for p, im, d in zip(files, imgs, arrs):
    if im.shape != ref.shape or not np.allclose(im.affine, ref.affine, atol=1e-5):
        raise ValueError(f'Geometry mismatch: {p.name}')
    if not np.isfinite(d).all():
        raise ValueError(f'Nonfinite values: {p.name}')
# The source maps encode outside-mask voxels as exact zero. Use the intersection
# to prevent different edge coverage from changing the tested voxel set.
mask = np.logical_and.reduce([d != 0 for d in arrs])
if mask.sum() < 100_000:
    raise ValueError(f'Unexpectedly small common support: {mask.sum()}')
X = np.stack([d[mask].astype(np.float64) for d in arrs], axis=0)  # n x voxels
n, nv = X.shape
mean = X.mean(axis=0)
sd = X.std(axis=0, ddof=1)
tobs = mean / (sd / np.sqrt(n))
# Independent statistic check against SciPy at fixed sampled voxels.
check_idx = np.linspace(0, nv-1, 17, dtype=int)
ref_t = stats.ttest_1samp(X[:,check_idx], 0, axis=0).statistic
if not np.allclose(tobs[check_idx], ref_t, rtol=1e-10, atol=1e-10):
    raise AssertionError('Group t statistic disagrees with scipy.stats.ttest_1samp')
# Sign flips preserve each participant's spatial map and test the symmetric
# one-sample null. Max positive t over all in-mask voxels controls one-sided FWE.
rng = np.random.default_rng(SEED)
max_null = np.empty(B, dtype=np.float32)
sumsq = np.sum(X*X, axis=0)
start = time.time()
chunk = 100
for lo in range(0, B, chunk):
    m = min(chunk, B-lo)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(m,n))
    ss = signs @ X
    # Equivalent one-sample t after sign flipping: sum(x)*sqrt(n-1) /
    # sqrt(n*sum(x^2)-sum(x)^2).
    ts = ss*np.sqrt(n-1) / np.sqrt(np.maximum(n*sumsq - ss*ss, 1e-30))
    max_null[lo:lo+m] = np.max(ts, axis=1)
# Include-one correction. Corrected p at a voxel is its rank against max-null.
max_null_sorted = np.sort(max_null)
pfwe = (1 + (B - np.searchsorted(max_null_sorted, tobs, side='left'))) / (B+1)
crit = float(np.quantile(max_null, 1-ALPHA, method='higher'))

mean_img = np.zeros(ref.shape, np.float32); mean_img[mask] = mean
sd_img = np.zeros(ref.shape, np.float32); sd_img[mask] = sd
stat_img = np.zeros(ref.shape, np.float32); stat_img[mask] = tobs
p_img = np.ones(ref.shape, np.float32); p_img[mask] = pfwe
mask_img = nib.Nifti1Image(mask.astype(np.uint8), ref.affine, ref.header)
for name, data in [('mean_effect.nii.gz',mean_img),('group_t.nii.gz',stat_img),('fwe_p.nii.gz',p_img),('common_mask.nii.gz',mask.astype(np.uint8))]:
    nib.save(nib.Nifti1Image(data, ref.affine, ref.header), OUT/name)

sig = (pfwe <= ALPHA) & (tobs > 0)
sig_img_data = np.zeros(ref.shape, np.uint8); sig_img_data[mask] = sig.astype(np.uint8)
labels, nclusters = ndimage.label(sig_img_data, structure=np.ones((3,3,3), dtype=np.uint8))
loc_labels = labels[tuple(np.unravel_index(np.flatnonzero(mask), ref.shape))]
cluster_rows = []
for lab in range(1, nclusters+1):
    ind = np.flatnonzero(sig & (loc_labels == lab))
    cluster_peak_local = ind[np.argmax(tobs[ind])]
    peak_vox = np.array(np.unravel_index(np.flatnonzero(mask)[cluster_peak_local], ref.shape))
    peak_xyz = nib.affines.apply_affine(ref.affine, peak_vox)
    cluster_rows.append({'cluster':lab,'voxels':int(len(ind)),'peak_x_mm':peak_xyz[0],
                         'peak_y_mm':peak_xyz[1],'peak_z_mm':peak_xyz[2],
                         'peak_t':float(tobs[cluster_peak_local]),
                         'peak_fwe_p':float(pfwe[cluster_peak_local])})
pd.DataFrame(cluster_rows).to_csv(OUT/'fwe_clusters.tsv',sep='\t',index=False)
# Peak coordinate and parametric reference result at observed peak.
if sig.any():
    peak_idx = int(np.argmax(np.where(sig, tobs, -np.inf)))
else:
    peak_idx = int(np.argmax(tobs))
ijk = np.array(np.unravel_index(np.flatnonzero(mask)[peak_idx], ref.shape))
xyz = nib.affines.apply_affine(ref.affine, ijk)
peak_p = float(pfwe[peak_idx]); peak_t = float(tobs[peak_idx])
peak_param_p = float(stats.t.sf(peak_t, n-1))
peak_effect = float(mean[peak_idx]); peak_sd = float(sd[peak_idx])
peak_se = peak_sd/np.sqrt(n)
peak_ci = stats.t.interval(.95, n-1, loc=peak_effect, scale=peak_se)

# Anatomical vmPFC proxy for descriptive summary only: a conservative bilateral
# medial orbital/subcallosal coordinate envelope in MNI space. Not an ROI test.
coords = np.array(np.unravel_index(np.flatnonzero(mask), ref.shape)).T
xyz_all = nib.affines.apply_affine(ref.affine, coords)
roi = ((np.abs(xyz_all[:,0]) <= 15) & (xyz_all[:,1] >= 0) & (xyz_all[:,1] <= 50) &
       (xyz_all[:,2] >= -25) & (xyz_all[:,2] <= 0))
roi_x = X[:,roi]
roi_part_mean = roi_x.mean(axis=1)
roi_mean = float(roi_x.mean())
roi_sd = float(roi_part_mean.std(ddof=1))
roi_se = roi_sd/np.sqrt(n)
roi_t = roi_mean/roi_se
roi_p = float(stats.t.sf(roi_t,n-1))
roi_ci = stats.t.interval(.95,n-1,loc=roi_mean,scale=roi_se)

pd.DataFrame(qc).to_csv(OUT/'participant_qc.tsv',sep='\t',index=False)
pd.DataFrame({'participant_id':ids,'vmPFC_proxy_mean':roi_part_mean}).to_csv(OUT/'vmPFC_proxy_participant_values.tsv',sep='\t',index=False)
# Record checksums for exact inputs and executable source.
source_meta=json.loads((INPUT/'sources.json').read_text())
checks={}
for p in files:
    checks[p.relative_to(ROOT).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
checks['input/participants.tsv']=hashlib.sha256((INPUT/'participants.tsv').read_bytes()).hexdigest()
checks['analysis/run_analysis.py']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
for p in files:
    rel=p.relative_to(ROOT).as_posix()
    source_key=p.relative_to(INPUT).as_posix()
    if checks[rel] != source_meta['files'][source_key]['sha256']:
        raise ValueError(f'Supplied map checksum differs from pinned source manifest: {rel}')
if checks['input/participants.tsv'] != source_meta['files']['participants.tsv']['sha256']:
    raise ValueError('Participant table checksum differs from pinned source manifest')
summary={
 'n_participants':n,'n_excluded':0,'n_common_support_voxels':nv,'shape':list(ref.shape),'affine':ref.affine.tolist(),
 'mask_rule':'exactly nonzero in all 54 maps','model':'one-sample participant-effects t; equal participant weights',
 'inference':'one-sided sign-flip max-t whole-brain FWE','permutations':B,'seed':SEED,'alpha':ALPHA,
 'permutation_critical_t':crit,'significant_voxels_fwe05':int(sig.sum()),
 'peak_mni_mm':xyz.tolist(),'peak_t':peak_t,'peak_fwe_p':peak_p,'peak_parametric_one_sided_p':peak_param_p,
 'peak_mean_effect':peak_effect,'peak_sd_between_participants':peak_sd,'peak_se':peak_se,'peak_ci95':list(map(float,peak_ci)),
 'vmPFC_proxy_definition_mni_mm':'|x|<=15, 0<=y<=50, -25<=z<=0 (descriptive proxy; not inferential ROI)',
 'vmPFC_proxy_voxels':int(roi.sum()),'vmPFC_proxy_mean_effect':roi_mean,'vmPFC_proxy_between_participant_sd':roi_sd,
 'vmPFC_proxy_se':roi_se,'vmPFC_proxy_ci95':list(map(float,roi_ci)),'vmPFC_proxy_t':float(roi_t),
 'vmPFC_proxy_parametric_one_sided_p':roi_p,
 'runtime_seconds':time.time()-start,'python':sys.version,'platform':platform.platform(),
 'packages':{'numpy':np.__version__,'scipy':__import__('scipy').__version__,'pandas':pd.__version__,
             'nibabel':nib.__version__,'nilearn':__import__('nilearn').__version__,
             'matplotlib':matplotlib.__version__},
 'input_sha256':checks,'source_metadata_scope':source_meta['checksum_scope']}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

# Render separate orthogonal views. Center the corrected map on its actual
# posterior peak; show medial prefrontal slices for the mean-effect map.
display = plotting.plot_stat_map(nib.Nifti1Image(mean_img,ref.affine), bg_img=None,
                       threshold=None, display_mode='ortho', cut_coords=(0,30,-10),
                       cmap='cold_hot', colorbar=True,
                       title='Mean participant gain effect (coefficient units; not currency units)',
                       black_bg=False)
display.savefig(FIG/'mean_gain_effect.png',dpi=180)
display.close()
display = plotting.plot_glass_brain(nib.Nifti1Image(stat_img,ref.affine),
                       threshold=crit, display_mode='lyrz', cmap='hot',
                       colorbar=True, plot_abs=False,
                       title=f'Positive t, whole-brain max-t FWE (α={ALPHA})',
                       black_bg=False)
display.savefig(FIG/'wholebrain_fwe_peak.png',dpi=180)
display.close()
# Distribution figure gives the variation across the independent units.
fig,ax=plt.subplots(figsize=(7,4.2))
ax.hist(roi_part_mean,bins=12,color='#4c78a8',edgecolor='white')
ax.axvline(0,color='black',lw=1)
ax.axvline(roi_mean,color='#d62728',lw=2,label=f'Mean {roi_mean:.3g}; 95% CI [{roi_ci[0]:.3g}, {roi_ci[1]:.3g}]')
ax.set(xlabel='Participant mean gain coefficient in vmPFC coordinate proxy',ylabel='Participants',
       title='Participant-level variation (54 participants)')
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(FIG/'vmPFC_proxy_distribution.png',dpi=180); plt.close(fig)
print(json.dumps(summary,indent=2))
