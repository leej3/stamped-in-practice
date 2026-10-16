#!/usr/bin/env python
"""Group inference for the fixed NARPS AO86 gain cope maps."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import scipy
import nilearn
from scipy.stats import t as student_t
from nilearn import datasets, image

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("NILEARN_DATA", str(ROOT / "resources" / "nilearn"))
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
SEED = 20261015
N_PERM = int(os.environ.get("N_PERM", "9999"))
BATCH = 48


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    start = time.time()
    subjects = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
    assert len(subjects) == 54 and subjects["participant_id"].is_unique
    files = [ROOT / "input" / "data" / f"{sid}_hypo1_cope.nii.gz" for sid in subjects.participant_id]
    assert all(p.is_file() for p in files), "A listed participant map is missing"

    imgs = [nib.load(str(p)) for p in files]
    ref = imgs[0]
    assert all(img.shape == ref.shape and np.allclose(img.affine, ref.affine) for img in imgs)
    data = np.stack([img.get_fdata(dtype=np.float32) for img in imgs])
    finite = np.isfinite(data).all(axis=0)
    # Intersect common map support with an independent skull-stripped MNI brain
    # mask. Common nonzero support alone includes edge voxels beyond the brain.
    common_support = finite & np.all(data != 0, axis=0)
    brain = datasets.load_mni152_brain_mask(resolution=2)
    brain_on_ref = image.resample_to_img(brain, ref, interpolation="nearest")
    mask = common_support & (brain_on_ref.get_fdata() > 0)
    nvox = int(mask.sum())
    if nvox < 1000:
        raise RuntimeError(f"Unexpectedly small common support: {nvox} voxels")
    X = data[:, mask].astype(np.float64)
    n, v = X.shape
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    se = sd / np.sqrt(n)
    t_obs = mean / se
    p_unc = student_t.sf(t_obs, n - 1)
    p_bonf = np.minimum(1.0, p_unc * v)
    sig_bonf = p_bonf <= 0.05

    # One-sided participant-level sign-flip max-T test. Under the one-sample null,
    # sign flips preserve each participant map's spatial structure and control
    # family-wise error across every tested voxel.
    rng = np.random.default_rng(SEED)
    max_null = np.empty(N_PERM, dtype=np.float32)
    # Keep the observed voxelwise standard error fixed in the randomization
    # statistic. This studentized sign-flip score is valid under sign symmetry
    # and avoids catastrophic cancellation from recomputing a variance as
    # sum(x^2) - sum(x)^2/n at near-constant voxels.
    fixed_se = np.maximum(se, np.finfo(np.float64).tiny)
    for lo in range(0, N_PERM, BATCH):
        hi = min(lo + BATCH, N_PERM)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(hi - lo, n))
        sums = signs @ X
        t_perm = sums / (fixed_se[None, :] * np.sqrt(n))
        max_null[lo:hi] = np.max(t_perm, axis=1)
    p_fwe = (1 + (max_null[:, None] >= t_obs[None, :]).sum(axis=0)) / (N_PERM + 1)
    tcrit = float(np.quantile(max_null, 0.95, method="higher"))
    sig = (p_fwe <= 0.05)

    # Independent anatomical interpretation mask: AAL3v2 medial orbital frontal
    # label (the atlas's explicit vmPFC area), bilaterally. This ROI is descriptive;
    # confirmatory inference remains the whole-brain max-T test above.
    atlas = datasets.fetch_atlas_aal(version="3v2", data_dir=str(ROOT / "resources" / "nilearn"))
    atlas_img = nib.load(atlas.maps)
    labels = [x.decode() if isinstance(x, bytes) else str(x) for x in atlas.labels]
    chosen = [i for i, label in enumerate(labels) if "frontal_med_orb" in label.lower()]
    if len(chosen) != 2:
        raise RuntimeError(f"Could not identify bilateral vmPFC labels in AAL3v2: {labels}")
    atlas_on_ref = image.resample_to_img(atlas_img, ref, interpolation="nearest")
    atlas_data = atlas_on_ref.get_fdata()
    roi = np.isin(atlas_data, chosen) & mask
    if roi.sum() == 0:
        raise RuntimeError("vmPFC anatomical mask has no overlap with map support")
    roi_values = data[:, roi]
    roi_mean = roi_values.mean(axis=1)
    roi_sd = roi_values.std(axis=1, ddof=1)
    roi_summary = {
        "n": n, "roi_voxels": int(roi.sum()), "mean_coefficient": float(roi_mean.mean()),
        "sd_between_participant_roi_mean": float(roi_mean.std(ddof=1)),
        "ci95_low": float(roi_mean.mean() - student_t.ppf(.975, n-1) * roi_mean.std(ddof=1) / np.sqrt(n)),
        "ci95_high": float(roi_mean.mean() + student_t.ppf(.975, n-1) * roi_mean.std(ddof=1) / np.sqrt(n)),
        "participants_positive_roi_mean": int((roi_mean > 0).sum()),
        "aal3v2_labels": [labels[i] for i in chosen],
        "interpretation": "descriptive only; whole-brain corrected inference is primary",
    }

    # Participant QC: coefficient scale/range, spatial support, and gross outliers.
    subj_qc = []
    for i, sid in enumerate(subjects.participant_id):
        vals = data[i, mask]
        subj_qc.append({"participant_id": sid, "mean_brain_coefficient": float(vals.mean()),
                        "sd_brain_coefficient": float(vals.std(ddof=1)),
                        "min": float(vals.min()), "max": float(vals.max()),
                        "nonzero_voxels": int(np.count_nonzero(data[i]))})
    qc = pd.DataFrame(subj_qc)
    qc["mean_brain_z"] = (qc.mean_brain_coefficient - qc.mean_brain_coefficient.mean()) / qc.mean_brain_coefficient.std(ddof=1)
    qc["sd_brain_z"] = (qc.sd_brain_coefficient - qc.sd_brain_coefficient.mean()) / qc.sd_brain_coefficient.std(ddof=1)
    qc.to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)
    subjects.to_csv(OUT / "analysis_cohort.tsv", sep="\t", index=False)
    with (OUT / "vmPFC_summary.json").open("w") as f:
        json.dump(roi_summary, f, indent=2)

    # Save unthresholded and corrected results in map space.
    def save_map(name: str, vals: np.ndarray, dtype=np.float32, fill: float = 0) -> None:
        arr = np.full(ref.shape, fill, dtype=dtype)
        arr[mask] = vals.astype(dtype)
        nib.save(nib.Nifti1Image(arr, ref.affine, ref.header), str(OUT / name))
    save_map("group_mean_coefficient.nii.gz", mean)
    save_map("group_t_positive.nii.gz", t_obs)
    save_map("group_p_fwe_maxT.nii.gz", p_fwe, fill=1)
    save_map("group_positive_fwe05.nii.gz", sig.astype(np.float32))
    save_map("group_p_fwe_bonferroni.nii.gz", p_bonf, fill=1)
    save_map("group_positive_bonferroni_fwe05.nii.gz", sig_bonf.astype(np.float32))
    save_map("whole_brain_search_mask.nii.gz", np.ones(nvox, dtype=np.float32))

    # Whole-brain descriptive effect distribution and atlas ROI display.
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.hist(roi_mean, bins=14, color="#517b9b", edgecolor="white")
    ax.axvline(0, color="#333333", lw=1)
    ax.axvline(roi_mean.mean(), color="#d1495b", lw=2, label=f"mean = {roi_mean.mean():.3g}")
    ax.set(xlabel="Mean participant gain coefficient within vmPFC atlas mask", ylabel="Participants",
           title="vmPFC gain-effect estimates (descriptive)\nAAL3v2 bilateral medial orbital frontal area")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "vmPFC_participant_distribution.png", dpi=180)
    plt.close(fig)

    # Sagittal x≈0 view in the input MNI affine: show the t statistic and
    # independent anatomical vmPFC outline. The displayed slice is not inferential.
    tvol = np.zeros(ref.shape, dtype=np.float32); tvol[mask] = t_obs
    xcoord = np.arange(ref.shape[0]) * ref.affine[0, 0] + ref.affine[0, 3]
    xi = int(np.argmin(np.abs(xcoord)))
    ycoord = np.arange(ref.shape[1]) * ref.affine[1, 1] + ref.affine[1, 3]
    zcoord = np.arange(ref.shape[2]) * ref.affine[2, 2] + ref.affine[2, 3]
    fig, ax = plt.subplots(figsize=(7.8, 6.2))
    sl = tvol[xi, :, :].T
    ax.imshow(sl, origin="lower", extent=[ycoord[0], ycoord[-1], zcoord[0], zcoord[-1]],
              cmap="RdBu_r", vmin=-5, vmax=5, interpolation="nearest", aspect="equal")
    roi_sl = roi[xi, :, :].T.astype(float)
    if roi_sl.max() > 0:
        ax.contour(roi_sl, levels=[.5], colors="#ffcf33", linewidths=1.0,
                   extent=[ycoord[0], ycoord[-1], zcoord[0], zcoord[-1]])
    ax.set_xlim(-80, 80); ax.set_ylim(-40, 80)
    ax.set(xlabel="MNI y (mm)", ylabel="MNI z (mm)", title="One-sample t map, sagittal x≈0\nYellow: independent AAL3v2 vmPFC mask")
    cb = fig.colorbar(ax.images[0], ax=ax, shrink=.78); cb.set_label("t (positive gain effect)")
    fig.tight_layout()
    fig.savefig(OUT / "whole_brain_t_sagittal.png", dpi=180)
    plt.close(fig)

    max_t_ijk = np.argwhere(mask)[int(np.argmax(t_obs))]
    max_t_xyz = nib.affines.apply_affine(ref.affine, max_t_ijk)
    metadata = {
        "analysis": "positive one-sample t test with Bonferroni whole-brain FWE; fixed-SE sign-flip max-T sensitivity",
        "n": n, "voxels_tested": v, "n_permutations": N_PERM, "seed": SEED,
        "grid_shape": list(ref.shape), "search_mask": "common nonzero support intersected with MNI152 brain mask resampled to input grid",
        "bonferroni_alpha": 0.05, "degrees_of_freedom": n - 1,
        "maxT_95_threshold": tcrit, "n_voxels_fwe05": int(sig.sum()),
        "parametric_bonferroni_fwe05_voxels": int(sig_bonf.sum()),
        "parametric_bonferroni_fwe05_voxels_in_vmPFC": int((sig_bonf & roi[mask]).sum()),
        "max_observed_t": float(t_obs.max()),
        "max_observed_t_uncorrected_p": float(p_unc.min()),
        "max_observed_t_bonferroni_p": float(p_bonf.min()),
        "max_observed_t_mni_mm": [float(x) for x in max_t_xyz],
        "minimum_attainable_mc_p": 1/(N_PERM+1), "vmPFC": roi_summary,
        "maps_sha256": {p.name: sha256(p) for p in files},
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                     "nibabel": nib.__version__, "nilearn": nilearn.__version__, "pandas": pd.__version__},
        "elapsed_seconds": time.time() - start,
    }
    with (OUT / "analysis_summary.json").open("w") as f:
        json.dump(metadata, f, indent=2)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
