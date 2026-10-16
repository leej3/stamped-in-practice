#!/usr/bin/env python3
"""Group inference for NARPS Hypothesis 1 supplied AO86 cope maps.

No upstream processing is performed. The participant cope maps are tested with
a one-sample t model and a one-sided sign-flip max-t whole-brain correction.
"""
from pathlib import Path
import hashlib
import json
import glob

import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import matplotlib.pyplot as plt
from nilearn import plotting
from nilearn.datasets import load_mni152_template

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "input"
OUT = ROOT / "results"
FIG = OUT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
N_PERM = 9999
SEED = 20261016


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def save_nifti(array, ref, path, dtype=np.float32):
    hdr = ref.header.copy()
    hdr.set_data_dtype(dtype)
    nib.save(nib.Nifti1Image(np.asarray(array, dtype=dtype), ref.affine, hdr), path)


def main():
    participants = pd.read_csv(IN / "participants.tsv", sep="\t")
    files = sorted(glob.glob(str(IN / "data" / "sub-*_hypo1_cope.nii.gz")))
    file_by_id = {Path(f).name.split("_")[0]: f for f in files}
    ids = participants.participant_id.tolist()
    assert len(ids) == 54 and len(files) == 54 and set(ids) == set(file_by_id)
    ref = nib.load(file_by_id[ids[0]])
    raw, support = [], []
    qc = []
    for pid in ids:
        path = file_by_id[pid]
        im = nib.load(path)
        assert im.shape == ref.shape and np.allclose(im.affine, ref.affine, atol=1e-5)
        x = np.asarray(im.dataobj, dtype=np.float32)
        valid = np.isfinite(x) & (x != 0)
        assert np.isfinite(x).all()
        raw.append(x)
        support.append(valid)
        qc.append({"participant_id": pid, "file": str(Path(path).relative_to(ROOT)),
                   "sha256": sha256(path), "nonzero_voxels": int(valid.sum()),
                   "minimum": float(x.min()), "maximum": float(x.max()),
                   "mean_nonzero": float(x[valid].mean())})
    maps = np.stack(raw)
    support = np.stack(support)
    mask = support.all(axis=0)
    assert int(mask.sum()) > 100000
    Y = maps[:, mask].astype(np.float64)
    n, v = Y.shape

    mean = Y.mean(axis=0)
    sd = Y.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = stats.t.sf(t_obs, n - 1)

    # Sign-flip null for a one-sample test. Studentized statistic is recomputed
    # for each permutation; max positive t controls FWE for the directional test.
    rng = np.random.default_rng(SEED)
    signs = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(N_PERM, n))
    max_t = np.empty(N_PERM, dtype=np.float32)
    chunk = 100
    # Permutation sums use one BLAS-backed matrix product per chunk.
    for start in range(0, N_PERM, chunk):
        stop = min(start + chunk, N_PERM)
        z = signs[start:stop].astype(np.float64) @ Y
        m = z / n
        # For signs +/-1, the sum of squared data at each voxel is invariant.
        var = np.maximum((np.sum(Y * Y, axis=0)[None, :] - z * z / n) / (n - 1), 1e-20)
        tt = m / np.sqrt(var / n)
        max_t[start:stop] = np.max(tt, axis=1)

    # Plus-one correction gives valid finite Monte Carlo p values.
    sorted_max = np.sort(max_t)
    p_fwe = (N_PERM + 1 - np.searchsorted(sorted_max, t_obs, side="left")) / (N_PERM + 1)
    p_fwe = np.clip(p_fwe, 1 / (N_PERM + 1), 1)
    max_observed = float(t_obs.max())
    peak_idx = int(np.argmax(t_obs))
    p_global = float((1 + np.sum(max_t >= max_observed)) / (N_PERM + 1))
    tcrit_fwe = float(np.quantile(max_t, .95, method="higher"))

    full_mean = np.zeros(ref.shape, dtype=np.float32); full_mean[mask] = mean
    full_t = np.zeros(ref.shape, dtype=np.float32); full_t[mask] = t_obs
    full_pfwe = np.ones(ref.shape, dtype=np.float32); full_pfwe[mask] = p_fwe
    full_sig = np.zeros(ref.shape, dtype=np.float32); full_sig[mask] = (p_fwe < .05)
    save_nifti(full_mean, ref, OUT / "group_mean_cope.nii.gz")
    save_nifti(full_t, ref, OUT / "group_t_one_sided.nii.gz")
    save_nifti(full_pfwe, ref, OUT / "group_p_fwe_maxT.nii.gz")
    save_nifti(full_sig, ref, OUT / "group_sig_fwe05.nii.gz")
    save_nifti(mask, ref, OUT / "group_intersection_mask.nii.gz", dtype=np.uint8)

    # Prespecified anatomical vmPFC box, MNI coordinates; not selected by peaks.
    ijk = np.indices(ref.shape).reshape(3, -1).T
    xyz = nib.affines.apply_affine(ref.affine, ijk)
    xyz = xyz.reshape(*ref.shape, 3)
    roi = mask & (xyz[..., 0] >= -12) & (xyz[..., 0] <= 12) & \
          (xyz[..., 1] >= 25) & (xyz[..., 1] <= 55) & \
          (xyz[..., 2] >= -15) & (xyz[..., 2] <= 20)
    assert roi.sum() > 0
    # Equal-weight mean across ROI voxels per participant avoids treating
    # spatially correlated voxels as independent observations.
    roi_subject = maps[:, roi].mean(axis=1)
    roi_test = stats.ttest_1samp(roi_subject, 0, alternative="greater")
    roi_mean = float(roi_subject.mean())
    roi_sd = float(roi_subject.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    ci = stats.t.interval(.95, n - 1, loc=roi_mean, scale=roi_se)
    roi_p_two = float(stats.ttest_1samp(roi_subject, 0).pvalue)
    roi_data = pd.DataFrame({"participant_id": ids, "roi_mean_cope": roi_subject})
    roi_data.to_csv(OUT / "vmPFC_participant_estimates.tsv", sep="\t", index=False)
    pd.DataFrame(qc).to_csv(OUT / "map_qc.tsv", sep="\t", index=False)

    # Figure 1: whole-brain FWE thresholded positive effects around medial PFC.
    peak_mni = nib.affines.apply_affine(ref.affine, np.unravel_index(np.argmax(full_t), ref.shape))
    anatomical = load_mni152_template(resolution=2)
    display = plotting.plot_stat_map(
        OUT / "group_t_one_sided.nii.gz", bg_img=anatomical,
        threshold=tcrit_fwe, display_mode="ortho", cut_coords=tuple(float(x) for x in peak_mni),
        cmap="magma", colorbar=True, title="Whole-brain positive effect | max-T FWE 0.05",
        black_bg=False, annotate=True, dim=-0.4, vmax=max(tcrit_fwe, max_observed))
    display.savefig(FIG / "whole_brain_fwe_vmPFC.png", dpi=180)
    display.close()

    # Figure 2: participant-level vmPFC means and group estimate.
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    jitter = np.linspace(-.12, .12, n)
    ax.scatter(jitter, roi_subject, color="#426f9b", alpha=.78, s=30,
               edgecolor="white", linewidth=.35, zorder=2)
    ax.errorbar(0, roi_mean, yerr=[[roi_mean-ci[0]], [ci[1]-roi_mean]],
                fmt="D", color="#a64032", capsize=5, markersize=7,
                label="Mean and 95% t interval", zorder=3)
    ax.axhline(0, color="black", linewidth=.8)
    ax.set(xlim=(-.3, .3), xticks=[], ylabel="Mean participant cope in vmPFC ROI",
           title="vmPFC participant estimates (n=54)")
    ax.legend(frameon=False, loc="upper right")
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "vmPFC_participant_estimates.png", dpi=180)
    plt.close(fig)

    result = {
        "n_participants": n, "n_excluded": 0, "n_mask_voxels": int(v),
        "voxel_size_mm": list(ref.header.get_zooms()[:3]),
        "mask_definition": "intersection of exact nonzero support across all 54 maps",
        "roi_definition_mni_mm": {"x": [-12, 12], "y": [25, 55], "z": [-15, 20]},
        "roi_voxels": int(roi.sum()), "roi_mean_cope": roi_mean,
        "roi_sd_between_participants": roi_sd, "roi_95pct_t_ci": [float(ci[0]), float(ci[1])],
        "roi_one_sided_t": float(roi_test.statistic), "roi_one_sided_p_uncorrected": float(roi_test.pvalue),
        "roi_two_sided_p_uncorrected": roi_p_two,
        "roi_positive_participant_n": int((roi_subject > 0).sum()),
        "roi_max_voxel_t": float(t_obs[roi[mask]].max()),
        "roi_max_voxel_p_fwe": float(p_fwe[roi[mask]][np.argmax(t_obs[roi[mask]])]),
        "roi_voxels_significant_p_fwe_lt_0.05": int((p_fwe[roi[mask]] < .05).sum()),
        "whole_brain_test": "one-sided one-sample t; sign-flip max-t FWE",
        "permutations": N_PERM, "seed": SEED, "maxT_95pct_threshold": tcrit_fwe,
        "largest_observed_t": max_observed, "global_maxT_p_fwe": p_global,
        "fwe_significant_voxels_p_lt_0.05": int((p_fwe < .05).sum()),
        "peak_voxel_mni_mm": [float(a) for a in peak_mni],
        "peak_t": max_observed,
        "peak_p_uncorrected_one_sided": float(p_unc[peak_idx]),
        "peak_p_fwe": float(p_fwe[peak_idx]),
        "support_counts_per_voxel": {"intersection": int(mask.sum()), "union": int(support.any(axis=0).sum())},
        "age_mean_sd": [float(participants.age.mean()), float(participants.age.std(ddof=1))],
        "gender_counts": participants.gender.value_counts().to_dict(),
        "map_checksum_failures_vs_manifest": [],
        "software": {"python": "3.13", "numpy": np.__version__, "scipy": scipy.__version__, "nibabel": nib.__version__},
    }
    manifest = json.loads((IN / "sources.json").read_text())
    failed = []
    for item in qc:
        expected = manifest["files"][item["file"].replace("input/", "")]["sha256"]
        if item["sha256"] != expected:
            failed.append(item["participant_id"])
    result["map_checksum_failures_vs_manifest"] = failed
    render_json = json.dumps(result, indent=2, default=lambda value: value.item() if isinstance(value, np.generic) else str(value))
    (OUT / "summary.json").write_text(render_json + "\n")
    print(render_json)


if __name__ == "__main__":
    main()
