#!/usr/bin/env python3
"""Reproducible group analysis of NARPS AO86 equal-indifference gain COPEs."""
from __future__ import annotations

import argparse
import hashlib
import csv
import json
import platform
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import nilearn
import numpy as np
import pandas as pd
import scipy
from nilearn import datasets, image, plotting
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parent
IN = ROOT / "input"
OUT = ROOT / "results"
SEED = 20261016
N_PERM = 4999
ALPHA = 0.05


def load_inputs():
    participants = pd.read_csv(IN / "participants.tsv", sep="\t")
    provenance = json.loads((IN / "sources.json").read_text())
    paths = sorted((IN / "data").glob("sub-*_hypo1_cope.nii.gz"))
    files = {p.name.split("_")[0]: p for p in paths}
    ids = participants.participant_id.tolist()
    assert len(ids) == len(set(ids)) == 54
    assert set(ids) == set(files), (set(ids) - set(files), set(files) - set(ids))
    for pid, path in files.items():
        expected = provenance["files"][f"data/{path.name}"]["sha256"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == expected, f"SHA-256 mismatch for {path.name}"
    imgs = [nib.load(str(files[s])) for s in ids]
    ref = imgs[0]
    assert all(im.shape == ref.shape and np.allclose(im.affine, ref.affine) for im in imgs)
    arrays = np.stack([np.asarray(im.dataobj, dtype=np.float32) for im in imgs])
    finite = np.isfinite(arrays)
    support = np.abs(arrays) > 0
    mask = finite.all(axis=0) & support.all(axis=0)
    if not mask.any():
        raise ValueError("No complete common nonzero voxel support")
    return participants, ids, ref, arrays, mask


def one_sample_t(X):
    n = X.shape[0]
    mean = X.mean(axis=0, dtype=np.float64)
    sd = X.std(axis=0, ddof=1, dtype=np.float64)
    tt = np.divide(mean, sd / np.sqrt(n), out=np.zeros_like(mean), where=sd > 0)
    return mean, tt


def max_t_signflip(X, observed_t, n_perm=N_PERM, seed=SEED, batch_size=64):
    """One-sided max-T randomization distribution; sign flips test zero mean."""
    rng = np.random.default_rng(seed)
    n, v = X.shape
    ss = np.einsum("ij,ij->j", X, X, dtype=np.float64)
    maxima = np.empty(n_perm, dtype=np.float64)
    offset = 0
    while offset < n_perm:
        b = min(batch_size, n_perm - offset)
        signs = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(b, n))
        sums = signs @ X
        means = sums / n
        var = np.maximum((ss[None, :] - sums.astype(np.float64) ** 2 / n) / (n - 1), 0)
        tvals = np.divide(means, np.sqrt(var / n), out=np.zeros_like(var), where=var > 0)
        maxima[offset:offset+b] = tvals.max(axis=1)
        offset += b
    threshold = float(np.quantile(maxima, 1 - ALPHA, method="higher"))
    p_fwe = (1 + (maxima[:, None] >= observed_t[None, :]).sum(axis=0)) / (n_perm + 1)
    p_global = float((1 + np.sum(maxima >= float(observed_t.max()))) / (n_perm + 1))
    return threshold, p_fwe, p_global, maxima


def make_atlas_mask(ref, group_mask):
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    atlas_img = image.resample_to_img(atlas.maps, ref, interpolation="nearest")
    labels = list(atlas.labels)
    target = ["Frontal Medial Cortex", "Subcallosal Cortex", "Frontal Orbital Cortex"]
    indices = [labels.index(s) for s in target]
    atlas_data = np.asarray(atlas_img.dataobj)
    roi = np.isin(atlas_data, indices) & group_mask
    return roi, target


def save_nii(data, ref, path, dtype=np.float32):
    out = nib.Nifti1Image(np.asarray(data, dtype=dtype), ref.affine, ref.header.copy())
    out.set_data_dtype(dtype)
    nib.save(out, str(path))


def run_analysis(n_perm=N_PERM):
    OUT.mkdir(exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    participants, ids, ref, data, mask = load_inputs()
    X = data[:, mask].astype(np.float32)
    mean, t_obs = one_sample_t(X)
    threshold, p_fwe, p_global, maxima = max_t_signflip(X, t_obs, n_perm=n_perm)
    sig = t_obs >= threshold
    roi_mask, roi_names = make_atlas_mask(ref, mask)
    roi_values = data[:, roi_mask].mean(axis=1, dtype=np.float64)
    rng = np.random.default_rng(SEED + 1)
    boots = rng.choice(roi_values, size=(10000, len(roi_values)), replace=True).mean(axis=1)
    roi_ci = np.quantile(boots, [0.025, 0.975]).tolist()
    roi_mean = float(roi_values.mean())
    roi_t = float(roi_mean / (roi_values.std(ddof=1) / np.sqrt(len(roi_values))))
    roi_p = float(student_t.sf(roi_t, len(roi_values)-1))
    loo_means = np.array([np.delete(roi_values, i).mean() for i in range(len(roi_values))])
    xyz_all = nib.affines.apply_affine(ref.affine, np.array(np.where(mask)).T)
    peak_flat = int(np.argmax(t_obs))
    peak_xyz = xyz_all[peak_flat].tolist()
    roi_idx = np.where(roi_mask[mask])[0]
    roi_peak_flat = int(roi_idx[np.argmax(t_obs[roi_idx])]) if len(roi_idx) else None
    roi_peak_xyz = xyz_all[roi_peak_flat].tolist() if roi_peak_flat is not None else None
    # Per-participant data QC and consistency summary.
    qcs = []
    for pid, arr in zip(ids, data):
        vals = arr[mask]
        qcs.append({"participant_id": pid, "finite_voxels": int(np.isfinite(arr).sum()),
                    "nonzero_voxels": int(np.count_nonzero(arr)), "mean_in_common_mask": float(vals.mean()),
                    "sd_in_common_mask": float(vals.std(ddof=1)), "max_abs_in_common_mask": float(np.abs(vals).max())})
    pd.DataFrame(qcs).to_csv(OUT / "participant_qc.csv", index=False)
    pd.DataFrame({"participant_id": ids, "vmPFC_proxy_mean_cope": roi_values}).to_csv(OUT / "vmPFC_participant_values.csv", index=False)
    mean_img = np.zeros(ref.shape, dtype=np.float32); mean_img[mask] = mean
    t_img_data = np.zeros(ref.shape, dtype=np.float32); t_img_data[mask] = t_obs
    p_img_data = np.ones(ref.shape, dtype=np.float32); p_img_data[mask] = p_fwe
    sig_img_data = np.zeros(ref.shape, dtype=np.float32); sig_img_data[mask] = np.where(sig, t_obs, 0)
    save_nii(mean_img, ref, OUT / "mean_cope.nii.gz")
    save_nii(t_img_data, ref, OUT / "t_unthresholded.nii.gz")
    save_nii(p_img_data, ref, OUT / "p_fwe_maxT.nii.gz")
    save_nii(sig_img_data, ref, OUT / "t_positive_FWE05.nii.gz")
    save_nii(mask.astype(np.uint8), ref, OUT / "common_support_mask.nii.gz", np.uint8)
    save_nii(roi_mask.astype(np.uint8), ref, OUT / "vmPFC_proxy_mask.nii.gz", np.uint8)
    results = {
        "n_participants": len(ids), "n_excluded": 0, "participants": ids,
        "group_mask_voxels": int(mask.sum()), "permutation_voxels": int(mask.sum()),
        "mask_rule": "finite and nonzero in every supplied participant COPE map",
        "n_permutations": int(n_perm), "random_seed": SEED, "one_sided": True,
        "alpha_whole_brain_fwe": ALPHA, "max_t_threshold": threshold,
        "whole_brain_max_observed_t": float(t_obs.max()), "whole_brain_global_p_fwe": p_global,
        "significant_positive_voxels": int(sig.sum()), "whole_brain_peak_mni_mm": peak_xyz,
        "whole_brain_peak_t": float(t_obs.max()), "whole_brain_peak_mean_cope": float(mean[peak_flat]),
        "vmPFC_proxy_atlas": "Harvard-Oxford cortical max-probability threshold 25%, 2 mm",
        "vmPFC_proxy_labels": roi_names, "vmPFC_proxy_voxels": int(roi_mask.sum()),
        "vmPFC_proxy_mean_cope": roi_mean, "vmPFC_proxy_bootstrap_95ci": roi_ci,
        "vmPFC_proxy_one_sample_t_descriptive": roi_t, "vmPFC_proxy_one_sided_p_uncorrected_descriptive": roi_p,
        "vmPFC_proxy_peak_mni_mm": roi_peak_xyz,
        "vmPFC_proxy_significant_positive_voxels_wholebrain_fwe": int(np.sum(sig[roi_idx])),
        "vmPFC_proxy_loo_mean_range": [float(loo_means.min()), float(loo_means.max())],
        "positive_participant_roi_means": int(np.sum(roi_values > 0)),
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                     "nibabel": nib.__version__, "nilearn": nilearn.__version__, "pandas": pd.__version__},
        "participant_mean_cope_summary": {"mean": float(np.mean([q["mean_in_common_mask"] for q in qcs])),
                                           "sd": float(np.std([q["mean_in_common_mask"] for q in qcs], ddof=1))}
    }
    with open(OUT / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    np.savetxt(OUT / "max_t_null_distribution.csv", maxima, delimiter=",", header="maximum_t", comments="")
    make_figures(ref, mean_img, t_img_data, sig_img_data, roi_values, roi_mean, roi_ci,
                 threshold, peak_xyz, int(sig.sum()))
    return results


def make_figures(ref, mean_img, t_img, sig_img, roi_values, roi_mean, roi_ci, threshold, peak_xyz, nsig):
    bg = datasets.load_mni152_template(resolution=2)
    mean_nifti = nib.Nifti1Image(mean_img, ref.affine)
    sig_nifti = nib.Nifti1Image(sig_img, ref.affine)
    fig = plt.figure(figsize=(13, 5.2))
    if nsig:
        display = plotting.plot_glass_brain(sig_nifti, display_mode="lyrz",
            threshold=threshold, plot_abs=False, colorbar=True, figure=fig,
            title="Positive group t: whole-brain max-T FWE, one-sided α=.05")
    else:
        display = plotting.plot_stat_map(mean_nifti, bg_img=bg, threshold=None,
            display_mode="ortho", cut_coords=(0, 30, -10),
            title="Mean gain-effect COPE (no positive voxel survived whole-brain FWE)",
            cmap="cold_hot", colorbar=True, figure=fig, vmax=None)
    display.savefig(OUT / "figures" / "whole_brain.png", dpi=180)
    plt.close("all")
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    jitter = np.random.default_rng(SEED).normal(0, 0.045, size=len(roi_values))
    ax.scatter(jitter, roi_values, s=28, alpha=.75, color="#326a8c", edgecolor="white", linewidth=.3)
    ax.errorbar([0], [roi_mean], yerr=[[roi_mean-roi_ci[0]], [roi_ci[1]-roi_mean]],
                fmt="D", color="#b33b35", capsize=5, markersize=8, label="Mean and participant-bootstrap 95% CI")
    ax.axhline(0, color="black", linewidth=1, linestyle="--")
    ax.set_xlim(-.35, .35); ax.set_xticks([])
    ax.set_ylabel("Mean participant gain-effect COPE\n(arbitrary upstream units)")
    ax.set_title("Independent anatomical vmPFC proxy\n(descriptive; whole-brain result is confirmatory)")
    ax.legend(frameon=False, loc="best")
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "vmPFC_values.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--permutations", type=int, default=N_PERM)
    args = parser.parse_args()
    print(json.dumps(run_analysis(args.permutations), indent=2))
