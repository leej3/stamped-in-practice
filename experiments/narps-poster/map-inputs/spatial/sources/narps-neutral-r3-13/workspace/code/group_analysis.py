#!/usr/bin/env python3
"""One-sample group inference on fixed AO86 participant gain-effect maps.

Reproduces a positive one-sample t statistic and one-sided voxelwise FWE
correction using sign-flip max-statistic permutations. No upstream data are fit.
"""
from __future__ import annotations
import hashlib, json, platform
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from scipy import ndimage, stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nilearn
from nilearn import plotting

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
SEED = 864201
N_PERM = 5000
BATCH = 100
ALPHA = .05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
    source = json.loads((INPUT / "sources.json").read_text())
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    participants = participants.loc[participants.group.eq("equalIndifference")].copy()
    participants = participants.sort_values("participant_id")
    if len(participants) != 54:
        raise ValueError(f"Expected 54 equalIndifference participants, found {len(participants)}")
    expected = {v["participant_id"]: (k, v) for k, v in source["files"].items() if k.endswith(".nii.gz")}
    if set(participants.participant_id) != set(expected):
        raise ValueError("Participant IDs do not exactly match the map manifest")
    cohort = {"n":int(len(participants)),"age_mean":float(participants.age.mean()),
        "age_sd":float(participants.age.std(ddof=1)),"age_min":int(participants.age.min()),
        "age_max":int(participants.age.max()),
        "gender_counts":{str(k):int(v) for k,v in participants.gender.value_counts().sort_index().items()}}
    (OUT/"cohort_summary.json").write_text(json.dumps(cohort,indent=2)+"\n")

    imgs, arrays, audit = [], [], []
    for pid in participants.participant_id:
        rel, info = expected[pid]
        path = INPUT / rel
        if not path.exists(): raise FileNotFoundError(path)
        digest = sha256(path)
        if digest != info["sha256"]: raise ValueError(f"SHA-256 mismatch for {path}")
        img = nib.load(str(path)); arr = np.asarray(img.dataobj, dtype=np.float32)
        if not np.isfinite(arr).all(): raise ValueError(f"Nonfinite values in {path}")
        if imgs and (img.shape != imgs[0].shape or not np.allclose(img.affine, imgs[0].affine)):
            raise ValueError(f"Geometry mismatch for {path}")
        imgs.append(img); arrays.append(arr)
        audit.append({"participant_id":pid,"file":rel,"bytes":path.stat().st_size,"sha256":digest,
                      "n_nonzero":int(np.count_nonzero(arr)),"mean_nonzero":float(arr[arr!=0].mean())})
    (OUT / "input_audit.json").write_text(json.dumps({"n_maps":len(arrays),"verified_sha256":True,"maps":audit},indent=2)+"\n")

    # Common analysis mask: voxels with nonzero finite estimates in every map.
    # The input images share a fixed-space grid; zeros denote outside participant coverage.
    data = np.stack(arrays, axis=0).astype(np.float64)
    mask = np.isfinite(data).all(axis=0) & np.all(data != 0, axis=0)
    nvox = int(mask.sum())
    if nvox < 1000: raise ValueError(f"Unexpectedly small common mask: {nvox}")
    X = data[:, mask]
    n = X.shape[0]
    sum_x = X.sum(axis=0)
    sumsq = np.square(X).sum(axis=0)
    denom_sq = np.maximum(n * sumsq - sum_x**2, 1e-15)
    t_obs = sum_x * np.sqrt(n - 1) / np.sqrt(denom_sq)
    mean_obs = sum_x / n
    p_unc = stats.t.sf(t_obs, df=n-1)

    # Studentized sign-flip randomization; max-T controls one-sided FWE over all
    # common-mask voxels. Draw random signs for each independent participant.
    rng = np.random.default_rng(SEED)
    max_null = np.empty(N_PERM, dtype=np.float64)
    for start in range(0, N_PERM, BATCH):
        b = min(BATCH, N_PERM-start)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(b,n))
        sums = signs @ X
        ts = sums * np.sqrt(n - 1) / np.sqrt(np.maximum(n*sumsq[None,:] - sums**2, 1e-15))
        max_null[start:start+b] = np.max(ts, axis=1)
    p_fwe = (1 + (max_null[:,None] >= t_obs[None,:]).sum(axis=0)) / (N_PERM+1)
    threshold_t = float(np.quantile(max_null, 1-ALPHA, method="higher"))

    def make_img(values, dtype=np.float32):
        vol = np.full(imgs[0].shape, np.nan, dtype=dtype)
        vol[mask] = values
        return nib.Nifti1Image(vol, imgs[0].affine, imgs[0].header)
    mean_img = make_img(mean_obs)
    t_img = make_img(t_obs)
    p_img = make_img(p_fwe)
    sig = p_fwe <= ALPHA
    sig_values = np.where(sig, t_obs, np.nan)
    sig_img = make_img(sig_values)
    for name, img in [("group_mean_effect.nii.gz",mean_img),("group_t_positive.nii.gz",t_img),
                      ("group_p_fwe_positive.nii.gz",p_img),("group_t_fwe05.nii.gz",sig_img)]:
        nib.save(img, OUT/name)

    # Connected components among voxels passing voxelwise whole-brain FWE.
    sig_volume = np.zeros(imgs[0].shape, dtype=bool)
    sig_volume[mask] = sig
    labels, nlab = ndimage.label(sig_volume, structure=np.ones((3,3,3),dtype=int))
    clusters = []
    for lab in range(1,nlab+1):
        ijk = np.argwhere(labels == lab)
        vals = t_img.get_fdata()[labels == lab]
        peak_idx = ijk[np.argmax(vals)]
        xyz = nib.affines.apply_affine(imgs[0].affine, peak_idx)
        clusters.append({"cluster":lab,"n_voxels":int(len(ijk)),"peak_t":float(vals.max()),
                         "peak_i":int(peak_idx[0]),"peak_j":int(peak_idx[1]),"peak_k":int(peak_idx[2]),
                         "peak_x_mm":float(xyz[0]),"peak_y_mm":float(xyz[1]),"peak_z_mm":float(xyz[2]),
                         "peak_p_fwe":float("nan")})
    # Correct p values at exact voxel indices (the previous vector is mask flattened).
    for c in clusters:
        c["peak_p_fwe"] = float(p_img.get_fdata()[c["peak_i"],c["peak_j"],c["peak_k"]])
        # Operational vmPFC localization: midline (|x|<=12), anterior (y>=0),
        # ventral (z<=15 mm); used only to describe whole-brain significant peaks.
        c["peak_in_vmpfc_bounds"] = bool(abs(c["peak_x_mm"]) <= 12 and 0 <= c["peak_y_mm"] <= 60 and -20 <= c["peak_z_mm"] <= 10)
    pd.DataFrame(clusters).to_csv(OUT/"fwe_clusters.csv",index=False)

    # Coordinate-bounded vmPFC summary is descriptive only; support is
    # judged by full-mask max-T corrected voxel p-values, never this summary.
    affine = imgs[0].affine
    ijk = np.argwhere(mask)
    xyz = nib.affines.apply_affine(affine, ijk)
    vmpfc_roi = (np.abs(xyz[:,0]) <= 12) & (xyz[:,1] >= 0) & (xyz[:,1] <= 60) & (xyz[:,2] >= -20) & (xyz[:,2] <= 10)
    roi_vals = X[:,vmpfc_roi]
    roi_t = np.sum(roi_vals,axis=0)*np.sqrt(n-1)/np.sqrt(np.maximum(n*np.square(roi_vals).sum(axis=0)-np.sum(roi_vals,axis=0)**2,1e-15))
    roi_summary = {"definition":"common-mask voxels with |x|<=12, 0<=y<=60, -20<=z<=10 mm MNI; medial anterior ventral prefrontal bounds",
       "n_voxels":int(vmpfc_roi.sum()),"mean_of_voxelwise_group_means":float(mean_obs[vmpfc_roi].mean()),
       "mean_of_participant_roi_means":float(roi_vals.mean(axis=1).mean()),
       "participant_roi_mean_sd":float(roi_vals.mean(axis=1).std(ddof=1)),
       "participant_roi_mean_ci95":stats.t.interval(.95,df=n-1,loc=roi_vals.mean(axis=1).mean(),scale=stats.sem(roi_vals.mean(axis=1))),
       "max_t":float(roi_t.max()),"min_positive_fwe_p_in_roi":float(p_fwe[vmpfc_roi].min()),
       "n_voxels_fwe05":int((p_fwe[vmpfc_roi]<=ALPHA).sum())}
    (OUT/"vmpfc_descriptive.json").write_text(json.dumps(roi_summary,indent=2,default=float)+"\n")

    # Participant-level ROI summaries and distribution.
    submeans = roi_vals.mean(axis=1)
    pd.DataFrame({"participant_id":participants.participant_id,"vmpfc_mean_effect":submeans}).to_csv(OUT/"vmpfc_participant_summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(7,4.4))
    ax.axhline(0,color="#555",lw=1)
    ax.scatter(np.arange(1,n+1),submeans,s=24,color="#31688e",alpha=.8)
    ax.axhline(submeans.mean(),color="#b23a48",lw=2,label=f"mean {submeans.mean():.3f}")
    ci=stats.t.interval(.95,n-1,loc=submeans.mean(),scale=stats.sem(submeans))
    ax.axhspan(ci[0],ci[1],color="#b23a48",alpha=.15,label="95% t interval")
    ax.set(xlabel="Participant (sorted ID)",ylabel="Mean gain-effect estimate in broad vmPFC bounds",
           title="Participant vmPFC summaries (descriptive)")
    ax.legend(frameon=False); fig.tight_layout(); fig.savefig(FIG/"vmpfc_participant_effects.png",dpi=180); plt.close(fig)

    # Whole-brain figure: max-T FWE thresholded result and unthresholded t map.
    if sig.any():
        coords = clusters[0]
        cuts=(coords["peak_x_mm"],coords["peak_y_mm"],coords["peak_z_mm"])
    else:
        # Representative vmPFC slices for unthresholded visualization.
        cuts=(0, 35, -5)
    display = plotting.plot_stat_map(sig_img, display_mode="ortho", cut_coords=cuts,
         title="Positive gain effect: voxelwise max-T FWE p ≤ .05",threshold=0,
         cmap="cold_hot",colorbar=True,black_bg=False,annotate=True,draw_cross=True)
    display.savefig(FIG/"whole_brain_fwe.png",dpi=180); display.close()
    glass = plotting.plot_glass_brain(sig_img, display_mode="lyrz", threshold=0, colorbar=True,
        plot_abs=False, title="Positive gain effect: voxelwise max-T FWE p ≤ .05")
    glass.savefig(FIG/"whole_brain_fwe_glass.png",dpi=180); glass.close()
    display = plotting.plot_stat_map(t_img, display_mode="ortho", cut_coords=cuts,
         title=f"Unthresholded positive group t map (max-T cutoff {threshold_t:.2f})",threshold=None,
         cmap="cold_hot",colorbar=True,black_bg=False,annotate=True,draw_cross=True)
    display.savefig(FIG/"whole_brain_t_unthresholded.png",dpi=180); display.close()

    # Compact run record, including useful direction-aware summary.
    best_i = int(np.argmax(t_obs)); best_ijk = ijk[best_i]; best_xyz=nib.affines.apply_affine(affine,best_ijk)
    report = {"n_participants":n,"n_common_mask_voxels":nvox,"permutation_draws":N_PERM,
      "seed":SEED,"alpha_one_sided":ALPHA,"max_t_fwe_critical":threshold_t,
      "largest_positive_t":float(t_obs[best_i]),"largest_positive_t_xyz_mm":[float(v) for v in best_xyz],
      "largest_positive_t_p_fwe":float(p_fwe[best_i]),"n_fwe_significant_voxels":int(sig.sum()),
      "n_fwe_clusters":int(nlab),"vmpfc_summary":roi_summary,
      "software":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,
                   "nibabel":nib.__version__,"matplotlib":matplotlib.__version__,"nilearn":nilearn.__version__}}
    (OUT/"analysis_summary.json").write_text(json.dumps(report,indent=2,default=float)+"\n")
    print(json.dumps(report,indent=2,default=float))

if __name__ == "__main__": main()
