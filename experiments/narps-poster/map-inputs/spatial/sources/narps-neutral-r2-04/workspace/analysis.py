#!/usr/bin/env python3
"""Group inference for NARPS Hypothesis 1 (fixed AO86 participant maps)."""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from scipy.ndimage import label
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
IN = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
B = 5000
SEED = 20261016

meta = json.loads((IN / "sources.json").read_text())
participants = pd.read_csv(IN / "participants.tsv", sep="\t")
assert len(participants) == 54 and participants.participant_id.is_unique
assert (participants.group == "equalIndifference").all()
files = meta["files"]
images = []
qc_rows = []
ref_img = None
for row in participants.itertuples(index=False):
    name = f"data/{row.participant_id}_hypo1_cope.nii.gz"
    spec = files[name]
    path = IN / name
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != spec["sha256"] or len(raw) != spec["bytes"]:
        raise ValueError(f"Checksum/size mismatch: {name}")
    img = nib.load(str(path))
    if ref_img is None:
        ref_img = img
    if img.shape != ref_img.shape or not np.allclose(img.affine, ref_img.affine, atol=1e-5):
        raise ValueError(f"Spatial mismatch: {name}")
    arr = img.get_fdata(dtype=np.float32)
    if not np.isfinite(arr).all():
        raise ValueError(f"Non-finite values: {name}")
    images.append(arr)
    qc_rows.append({"participant_id":row.participant_id,"age":row.age,"gender":row.gender,
                    "file_bytes":len(raw),"sha256_ok":True,"nonzero_voxels":int(np.count_nonzero(arr)),
                    "min":float(arr.min()),"max":float(arr.max()),"mean_nonzero":float(arr[arr!=0].mean()),
                    "sd_nonzero":float(arr[arr!=0].std())})

Yall = np.stack(images)
# Zero is the supplied outside-coverage value. Use the intersection of nonzero
# coverage to avoid mixing structural zeros with estimated contrasts.
mask = np.all(Yall != 0, axis=0)
nvox = int(mask.sum())
if nvox == 0:
    raise ValueError("No common nonzero coverage")
Y = Yall[:, mask].astype(np.float64)  # participants x voxels
n = Y.shape[0]
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(n))

# One-sided sign-flip max-T permutation test under a symmetric zero-mean null.
# For each sign vector, recompute the t statistic at all common-coverage voxels
# and retain its largest positive value (whole-brain FWE control).
rng = np.random.default_rng(SEED)
max_t = np.empty(B, dtype=np.float32)
sum_sq = np.sum(Y * Y, axis=0)
for start in range(0, B, 100):
    m = min(100, B-start)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(m,n))
    sums = signs @ Y
    denom = np.sqrt(np.maximum((n*sum_sq[None,:] - sums*sums)/(n-1), 1e-30))
    ts = sums / denom
    max_t[start:start+m] = ts.max(axis=1)
    del signs, sums, denom, ts
max_t.sort()
max_corr_p = (1 + B - np.searchsorted(max_t, t_obs, side="left")) / (B+1)
max_observed = float(t_obs.max())
p_max = float((1 + np.sum(max_t >= max_observed)) / (B+1))

def as_img(data, dtype=np.float32):
    vol = np.zeros(ref_img.shape, dtype=dtype)
    vol[mask] = np.asarray(data, dtype=dtype)
    return nib.Nifti1Image(vol, ref_img.affine, ref_img.header)

mask_img = nib.Nifti1Image(mask.astype(np.uint8), ref_img.affine, ref_img.header)
nib.save(mask_img, OUT / "common_coverage_mask.nii.gz")
nib.save(as_img(t_obs), OUT / "group_t_positive.nii.gz")
nib.save(as_img(max_corr_p), OUT / "fwe_p_positive_maxT.nii.gz")
nib.save(as_img(mean), OUT / "group_mean_effect.nii.gz")

# A fixed, coordinate-defined vmPFC ROI for interpretable descriptive estimation;
# primary support still requires the corrected whole-brain test above.
ijk = np.indices(ref_img.shape).reshape(3,-1).T
xyz = nib.affines.apply_affine(ref_img.affine, ijk)
roi_full = np.linalg.norm(xyz - np.array([0.,40.,-10.]), axis=1) <= 10.
roi_mask = roi_full.reshape(ref_img.shape) & mask
roi_nvox = int(roi_mask.sum())
if roi_nvox == 0: raise ValueError("vmPFC coordinate sphere has no common coverage")
roi_vals = Yall[:, roi_mask].mean(axis=1)
roi_mean = float(roi_vals.mean())
roi_se = float(stats.sem(roi_vals))
roi_ci = stats.t.interval(.95, n-1, loc=roi_mean, scale=roi_se)
roi_t, roi_p2 = stats.ttest_1samp(roi_vals, 0)
roi_p1 = float(stats.t.sf(roi_t, n-1)) if roi_t >= 0 else float(1-stats.t.cdf(roi_t,n-1))
roi_w = stats.wilcoxon(roi_vals, alternative="greater", method="auto")

# Connected supra-threshold descriptive clusters; voxel threshold is uncorrected
# p<.001 one-sided. This does not define the primary corrected inference.
p_unc = stats.t.sf(t_obs, n-1)
sig_unc = p_unc < .001
vol_sig = np.zeros(ref_img.shape, dtype=bool); vol_sig[mask] = sig_unc
tvol = np.zeros(ref_img.shape); tvol[mask] = t_obs
labs, nlab = label(vol_sig, structure=np.ones((3,3,3),dtype=np.uint8))
clusters=[]
for cid in range(1,nlab+1):
    coords = np.argwhere(labs==cid)
    if len(coords)<10: continue
    xyz_c = nib.affines.apply_affine(ref_img.affine, coords)
    # peak lookup in voxel coordinates
    ts = tvol[tuple(coords.T)]; pi = int(np.argmax(ts))
    clusters.append({"cluster":cid,"voxels":int(len(coords)),"volume_mm3":float(len(coords)*abs(np.linalg.det(ref_img.affine[:3,:3]))),
                     "peak_t":float(ts[pi]),"peak_mni_x":float(xyz_c[pi,0]),"peak_mni_y":float(xyz_c[pi,1]),"peak_mni_z":float(xyz_c[pi,2]),
                     "overlap_vmPFC_sphere":bool(np.any(roi_mask[tuple(coords.T)]))})
clusters.sort(key=lambda x:x["voxels"], reverse=True)
sig_vol = np.zeros(ref_img.shape, dtype=bool); sig_vol[mask] = max_corr_p < .05
pvol = np.ones(ref_img.shape, dtype=np.float32); pvol[mask] = max_corr_p
sig_labs, nsiglab = label(sig_vol, structure=np.ones((3,3,3),dtype=np.uint8))
fwe_clusters=[]
for cid in range(1,nsiglab+1):
    coords=np.argwhere(sig_labs==cid)
    ts=tvol[tuple(coords.T)]
    xyz_c=nib.affines.apply_affine(ref_img.affine,coords)
    pi=int(np.argmax(ts))
    fwe_clusters.append({"cluster":cid,"voxels":int(len(coords)),"volume_mm3":float(len(coords)*abs(np.linalg.det(ref_img.affine[:3,:3]))),
        "peak_t":float(ts[pi]),"peak_fwe_p":float(pvol[tuple(coords.T)].min()),
        "peak_mni_x":float(xyz_c[pi,0]),"peak_mni_y":float(xyz_c[pi,1]),"peak_mni_z":float(xyz_c[pi,2]),
        "overlap_vmPFC_sphere":bool(np.any(roi_mask[tuple(coords.T)]))})
fwe_clusters.sort(key=lambda x:x["voxels"],reverse=True)

pd.DataFrame(qc_rows).to_csv(OUT/"participant_qc.tsv",sep="\t",index=False)
pd.DataFrame(clusters).to_csv(OUT/"uncorrected_clusters_p001.tsv",sep="\t",index=False)
pd.DataFrame(fwe_clusters).to_csv(OUT/"fwe_clusters_p05.tsv",sep="\t",index=False)
summary = {
 "n_participants_input":len(participants),"n_participants_analyzed":n,"excluded":[],
 "common_nonzero_coverage_voxels":nvox,"voxel_volume_mm3":float(abs(np.linalg.det(ref_img.affine[:3,:3]))),
 "permutation_test":{"method":"one-sided sign-flip max-T; positive direction","permutations":B,"seed":SEED,
                     "maximum_observed_t":max_observed,"whole_brain_FWE_p_at_max":p_max,
                     "minimum_attainable_p":1/(B+1)},
 "vmPFC_coordinate_sphere":{"center_mni_mm":[0,40,-10],"radius_mm":10,"voxels":roi_nvox,
    "mean_effect":roi_mean,"sd_participant_values":float(roi_vals.std(ddof=1)),"se":roi_se,
    "ci95_t":[float(roi_ci[0]),float(roi_ci[1])],"t":float(roi_t),"p_one_sided_unadjusted":roi_p1,
    "p_two_sided_unadjusted":float(roi_p2),"wilcoxon_one_sided_unadjusted_p":float(roi_w.pvalue)},
 "voxelwise_corrected_significant_voxels":int(np.sum(max_corr_p<.05)),
 "fwe_clusters_p05":fwe_clusters,
 "clusters_uncorrected_p001_min10vox":clusters,
 "mask_definition":"intersection of nonzero voxels across all 54 maps"
}
(OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")

# Figures: participant values in fixed vmPFC sphere and corrected whole-brain t map.
fig,ax=plt.subplots(figsize=(7.5,4.3))
ax.scatter(np.arange(1,n+1), roi_vals, s=24, alpha=.75, color="#345995", edgecolor="white", linewidth=.35)
ax.axhline(0,color="black",linewidth=.8)
ax.axhline(roi_mean,color="#c44536",linewidth=1.8,label=f"Mean = {roi_mean:.3f}")
ax.fill_between([1,n],roi_ci[0],roi_ci[1],color="#c44536",alpha=.12,label="95% t interval for mean")
ax.set(xlabel="Participant (input order)",ylabel="Mean gain-effect estimate in vmPFC sphere",title="Participant-level vmPFC gain-effect estimates")
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(FIG/"vmPFC_participant_estimates.png",dpi=180); plt.close(fig)

try:
    from nilearn import plotting
    tcrit = float(max_t[min(B-1,int(np.ceil(.95*B)-1))])
    plot_img = as_img(t_obs)
    disp = plotting.plot_stat_map(plot_img, display_mode="z", cut_coords=[-16,-8,0,8,16],
       threshold=tcrit, cmap="cold_hot", colorbar=True,
       title=f"Positive t map, whole-brain max-T FWE p < .05; peak p = {p_max:.3f}",
       vmin=tcrit, vmax=max(5.,max_observed))
    disp.add_markers([[0,40,-10]], marker_color="lime", marker_size=90)
    disp.savefig(FIG/"whole_brain_fwe.png",dpi=180); disp.close()
except Exception as exc:
    (OUT/"plotting_note.txt").write_text(f"Nilearn whole-brain plotting failed: {exc}\n")

print(json.dumps(summary,indent=2))
