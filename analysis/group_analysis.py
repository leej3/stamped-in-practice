#!/usr/bin/env python3
"""One-sample whole-brain max-statistic sign-flip analysis of NARPS AO86 cope maps."""
from pathlib import Path
import glob, json, hashlib, platform, sys, time
import numpy as np
import pandas as pd
import nibabel as nib
import scipy
from scipy import stats, ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
SEED = 20261016
N_PERM = 10000
ALPHA = 0.05
BATCH = 128

OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
files = sorted(glob.glob(str(ROOT / 'input/data/*_hypo1_cope.nii.gz')))
meta = pd.read_csv(ROOT / 'input/participants.tsv', sep='\t')
source = json.loads((ROOT / 'input/sources.json').read_text())
ids = [Path(f).name.split('_')[0] for f in files]
assert len(files) == 54 and len(set(ids)) == 54
assert set(ids) == set(meta.participant_id) == {v['participant_id'] for k,v in source['files'].items() if k.startswith('data/')}
assert (meta.group == 'equalIndifference').all()

imgs = [nib.load(f) for f in files]
ref = imgs[0]
for im in imgs:
    if im.shape != ref.shape or not np.allclose(im.affine, ref.affine):
        raise ValueError('Image grid mismatch')
    if im.header.get_zooms()[:3] != ref.header.get_zooms()[:3]:
        raise ValueError('Voxel size mismatch')
# Load only after all image grid checks; one participant per leading axis.
Y4 = np.stack([im.get_fdata(dtype=np.float32) for im in imgs], axis=0)
finite = np.isfinite(Y4)
nonzero = Y4 != 0
coverage = np.all(finite & nonzero, axis=0)
if not coverage.any(): raise ValueError('Empty common nonzero coverage')
# We infer on identical, finite, nonzero coverage; no missing values are imputed.
Y = Y4[:, coverage].astype(np.float64)
N, V = Y.shape
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(N))
df = N - 1
# Exact parametric t summaries are retained for transparent descriptive maps;
# whole-brain decisions use permutation max-t.
p_unc = stats.t.sf(t_obs, df)

rng = np.random.default_rng(SEED)
max_null = np.empty(N_PERM, dtype=np.float64)
sumsq = np.sum(Y*Y, axis=0)
# A sign-flip randomization test; each row is one independent participant sign.
# The t denominator is recomputed per assignment (sum of squares is invariant).
for start in range(0, N_PERM, BATCH):
    b = min(BATCH, N_PERM-start)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(b, N))
    sums = signs @ Y
    var = np.maximum((sumsq[None, :] - sums*sums/N)/(N-1), 0.0)
    t_perm = sums / np.sqrt(N*var)
    max_null[start:start+b] = np.max(t_perm, axis=1)
    if (start+b) % 1024 < BATCH or start+b == N_PERM:
        print(f'permutations {start+b}/{N_PERM}', flush=True)
# Plus-one correction includes the observed assignment in numerator/denominator.
p_fwe = (1 + np.sum(max_null[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)
# Independent numerical cross-check at the strongest observed voxel.
peak = int(np.argmax(t_obs))
manual_t = stats.ttest_1samp(Y[:, peak], popmean=0).statistic
assert np.isclose(manual_t, t_obs[peak], rtol=1e-12, atol=1e-12)

# Convert masked vectors back into NIfTI maps (zero outside inferential mask).
def image_from_vector(vec, dtype=np.float32, fill=0.0):
    arr = np.full(ref.shape, fill, dtype=dtype)
    arr[coverage] = vec.astype(dtype)
    return nib.Nifti1Image(arr, ref.affine, ref.header)
for name, vec in [('mean_cope', mean), ('tstat', t_obs)]:
    nib.save(image_from_vector(vec), OUT / f'{name}.nii.gz')
# P maps use NaN outside coverage so unsupported voxels cannot be mistaken
# for perfectly significant zeros by downstream readers.
nib.save(image_from_vector(p_unc, fill=np.nan), OUT/'p_uncorrected.nii.gz')
nib.save(image_from_vector(p_fwe, fill=np.nan), OUT/'p_fwe_maxT.nii.gz')
nib.save(nib.Nifti1Image(coverage.astype(np.uint8), ref.affine, ref.header), OUT/'common_coverage_mask.nii.gz')
sig_volume = np.zeros(ref.shape, dtype=bool)
sig_volume[coverage] = p_fwe < ALPHA
_, n_sig_clusters = ndimage.label(sig_volume, structure=np.ones((3,3,3), dtype=bool))

# vmPFC locator: |x|<=10, y>=25, z<=15 mm in MNI coordinates. This is
# descriptive localization only; all p values still reference the whole-brain max.
ijk = np.array(np.where(coverage)).T
xyz = nib.affines.apply_affine(ref.affine, ijk)
vm = (np.abs(xyz[:,0]) <= 10) & (xyz[:,1] >= 25) & (xyz[:,2] <= 15)
if not vm.any(): raise ValueError('vmPFC locator contains no covered voxels')
vm_idx = np.flatnonzero(vm)
vm_peak_idx = vm_idx[np.argmax(t_obs[vm_idx])]
vm_peak_ijk = ijk[vm_peak_idx]
vm_peak_xyz = xyz[vm_peak_idx]
vm_mean = float(mean[vm].mean())
vm_mean_t = float(stats.ttest_1samp(Y[:, vm].mean(axis=1), 0).statistic)
vm_mean_ci = stats.t.interval(.95, df, loc=vm_mean, scale=stats.sem(Y[:, vm].mean(axis=1)))

# Compact diagnostics, included/excluded participant accounting, and checksums.
participant_rows=[]
for i, sid in enumerate(ids):
    a=Y4[i]
    finite_n=int(finite[i].sum())
    participant_rows.append({'participant_id':sid,'included':True,'finite_voxels':finite_n,
                             'nonzero_voxels':int(nonzero[i].sum()),'global_nonzero_mean':float(a[finite[i] & nonzero[i]].mean()),
                             'global_nonzero_sd':float(a[finite[i] & nonzero[i]].std(ddof=1)),
                             'global_nonzero_min':float(a[finite[i] & nonzero[i]].min()),'global_nonzero_max':float(a[finite[i] & nonzero[i]].max()),
                             'sha256':hashlib.sha256(Path(files[i]).read_bytes()).hexdigest()})
pd.DataFrame(participant_rows).to_csv(OUT/'participant_qc.tsv',sep='\t',index=False)

# Anatomical coordinate display based directly on NIfTI voxel geometry.
def idx_at(mm, axis):
    return int(np.argmin(np.abs(nib.affines.apply_affine(ref.affine, np.array([[0,0,0],[0,0,0],[0,0,0]]))[:,axis])))
# Reliable world coordinate -> nearest voxel using inverse affine.
def vox_at_world(x,y,z):
    return np.round(nib.affines.apply_affine(np.linalg.inv(ref.affine), [x,y,z])).astype(int)
# Show unthresholded t in coronal y=40 and axial z=-4, whole-brain corrected voxels outlined.
cor = vox_at_world(0,40,0)[1]; axi = vox_at_world(0,0,-4)[2]
Tvol=np.zeros(ref.shape); Tvol[coverage]=t_obs
Sig=np.zeros(ref.shape,dtype=bool); Sig[coverage]=p_fwe<ALPHA
# Panels use index axes; ticks show actual MNI coordinates.
fig, ax=plt.subplots(1,3,figsize=(12,4.1),constrained_layout=True)
# Coronal: horizontal x and vertical z.
cor_t=Tvol[:,cor,:].T; cor_s=Sig[:,cor,:].T
ax[0].imshow(cor_t,origin='lower',cmap='RdBu_r',vmin=-5,vmax=5,aspect='auto',extent=[-96,96,-78,114])
ax[0].contour(np.linspace(-96,96,ref.shape[0]),np.linspace(-78,114,ref.shape[2]),cor_s.astype(float),levels=[.5],colors='black',linewidths=.7)
ax[0].set_title(f'Coronal y={nib.affines.apply_affine(ref.affine, [0,cor,0])[1]:.0f} mm'); ax[0].set_xlabel('MNI x (mm)'); ax[0].set_ylabel('MNI z (mm)')
# Axial: horizontal x and vertical y.
axi_t=Tvol[:,:,axi].T; axi_s=Sig[:,:,axi].T
ax[1].imshow(axi_t,origin='lower',cmap='RdBu_r',vmin=-5,vmax=5,aspect='auto',extent=[-96,96,-132,96])
ax[1].contour(np.linspace(-96,96,ref.shape[0]),np.linspace(-132,96,ref.shape[1]),axi_s.astype(float),levels=[.5],colors='black',linewidths=.7)
ax[1].set_title(f'Axial z={nib.affines.apply_affine(ref.affine, [0,0,axi])[2]:.1f} mm'); ax[1].set_xlabel('MNI x (mm)'); ax[1].set_ylabel('MNI y (mm)')
# Distribution of participant mean estimates in vmPFC locator and at post-hoc peak.
peak_values=Y[:,vm_peak_idx]
ax[2].violinplot([Y[:,vm].mean(axis=1),peak_values],showmeans=True,showextrema=False)
ax[2].axhline(0,color='black',lw=.8); ax[2].set_xticks([1,2],['vmPFC mean','vmPFC peak voxel']); ax[2].set_ylabel('Participant cope (normalized regressor units)'); ax[2].set_title('Participant estimates')
fig.suptitle('Equal-indifference group gain effect (n=54)\nblack contours: whole-brain max-T FWE p < .05')
fig.savefig(FIG/'group_gain_effect.png',dpi=180)
plt.close(fig)

# Main summary and environment record.
summary={
 'n_input':len(files),'n_included':N,'n_excluded':0,'n_voxels_common_nonzero':int(V),
 'grid_shape':list(ref.shape),'voxel_sizes_mm':[float(x) for x in ref.header.get_zooms()[:3]],
 'model':'equal-weight one-sample t against zero; positive directional test',
 'inference':'10,000 random participant sign flips; whole-brain maximum positive t; plus-one FWE p',
 'seed':SEED,'alpha':ALPHA,'max_null_t_95':float(np.quantile(max_null,.95)),
 'whole_brain_fwe_voxels':int(np.sum(p_fwe<ALPHA)),
'whole_brain_fwe_clusters_26conn':int(n_sig_clusters),
 'whole_brain_fwe_min_p':float(p_fwe.min()),'whole_brain_peak_t':float(t_obs.max()),
 'whole_brain_peak_xyz_mm':[float(x) for x in xyz[np.argmax(t_obs)]],
 'whole_brain_peak_mean_cope':float(mean[np.argmax(t_obs)]),
 'whole_brain_peak_p_fwe':float(p_fwe.max()) if False else float(p_fwe[np.argmax(t_obs)]),
 'vmPFC_locator':'|x|<=10 mm, y>=25 mm, z<=15 mm MNI; descriptive locator, whole-brain correction retained',
 'vmPFC_voxels':int(vm.sum()),'vmPFC_fwe_voxels':int(np.sum(p_fwe[vm]<ALPHA)),
 'vmPFC_peak_t':float(t_obs[vm_peak_idx]),'vmPFC_peak_xyz_mm':[float(x) for x in vm_peak_xyz],
 'vmPFC_peak_mean_cope':float(mean[vm_peak_idx]),'vmPFC_peak_p_fwe':float(p_fwe[vm_peak_idx]),
 'vmPFC_region_mean_cope':vm_mean,'vmPFC_region_mean_t_descriptive':vm_mean_t,
 'vmPFC_region_mean_95pct_t_interval':[float(x) for x in vm_mean_ci],
 'participant_global_mean_range':[float(min(r['global_nonzero_mean'] for r in participant_rows)),float(max(r['global_nonzero_mean'] for r in participant_rows))],
 'age_range_years':[int(meta.age.min()),int(meta.age.max())], 'gender_counts':meta.gender.value_counts().to_dict(),
 'software':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'pandas':pd.__version__,'nibabel':nib.__version__,'matplotlib':matplotlib.__version__,'platform':platform.platform()},
 'input_map_sha256_verified_against_manifest':all(r['sha256']==source['files'][f"data/{Path(files[i]).name}"]['sha256'] for i,r in enumerate(participant_rows))
}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
