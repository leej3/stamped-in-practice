#!/usr/bin/env python3
"""Group analysis of supplied NARPS AO86 participant gain-effect maps."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets, image, plotting
from scipy import stats
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
SEED = 20261016
N_PERM = 4999
ALPHA = 0.05
MIN_COVERAGE = 0.90


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    source = json.loads((ROOT / "input/sources.json").read_text())
    participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
    maps = source["files"]
    ids = participants.participant_id.tolist()
    map_entries = {k: v for k, v in maps.items() if k.endswith(".nii.gz")}
    if len(ids) != 54 or len(set(ids)) != 54 or len(map_entries) != 54:
        raise ValueError("Expected exactly 54 unique participant IDs and maps")
    if set(ids) != {v["participant_id"] for v in map_entries.values()}:
        raise ValueError("Participant table and image manifest IDs do not match")

    paths = [ROOT / "input/data" / f"{pid}_hypo1_cope.nii.gz" for pid in ids]
    imgs = []
    qc = []
    ref = None
    for pid, path in zip(ids, paths):
        if not path.is_file():
            raise FileNotFoundError(path)
        expected = maps[f"data/{path.name}"]
        digest = sha256(path)
        if path.stat().st_size != expected["bytes"] or digest != expected["sha256"]:
            raise ValueError(f"Manifest checksum/size mismatch: {path.name}")
        img = nib.load(path)
        if ref is None:
            ref = img
        if img.shape != ref.shape or not np.allclose(img.affine, ref.affine, atol=1e-5):
            raise ValueError(f"Image geometry differs: {path.name}")
        data = np.asarray(img.dataobj, dtype=np.float32)
        finite = np.isfinite(data)
        if not finite.all():
            raise ValueError(f"Nonfinite map values: {path.name}")
        coverage = data != 0
        qc.append({"participant_id": pid, "bytes": path.stat().st_size,
                   "sha256": digest, "finite_voxels": int(finite.sum()),
                   "nonzero_voxels": int(coverage.sum()),
                   "nonzero_fraction": float(coverage.mean()),
                   "minimum": float(data.min()), "maximum": float(data.max()),
                   "mean_nonzero": float(data[coverage].mean()),
                   "sd_nonzero": float(data[coverage].std(ddof=1))})
        imgs.append(data)
    pd.DataFrame(qc).to_csv(OUT / "input_qc.tsv", sep="\t", index=False)

    arr = np.stack(imgs, axis=0)
    coverage_count = np.count_nonzero(arr, axis=0)
    support = coverage_count >= int(np.ceil(MIN_COVERAGE * len(ids)))
    nvox = int(support.sum())
    if nvox == 0:
        raise ValueError("No voxels meet the prespecified coverage rule")
    # Double precision is important in sign-flip variance calculations where
    # sum(x^2) - sum(x)^2/n can otherwise lose precision.
    X = arr[:, support].astype(np.float64, copy=False)
    del arr, imgs
    n = X.shape[0]
    means = X.mean(axis=0, dtype=np.float64)
    sds = X.std(axis=0, ddof=1, dtype=np.float64)
    t_obs = means / (sds / np.sqrt(n))
    p_unc = stats.t.sf(t_obs, n - 1)

    # Whole-brain one-sided max-T permutation correction. Participant sign
    # flips are applied to voxelwise observations standardized by their
    # observed SD; this makes the numerator statistic equal to the observed
    # one-sample t statistic and avoids cancellation in recomputed variances.
    rng = np.random.default_rng(SEED)
    signs = rng.choice(np.array([-1.0, 1.0], dtype=np.float64), size=(N_PERM, n))
    max_null = np.full(N_PERM, -np.inf, dtype=np.float32)
    start = 0
    chunk_vox = 25000
    batch_perm = 100
    while start < nvox:
        stop = min(start + chunk_vox, nvox)
        xx = X[:, start:stop]
        denom = sds[start:stop] * np.sqrt(n)
        valid_denom = np.isfinite(denom) & (denom > 0)
        chunk_max = np.full(N_PERM, -np.inf, dtype=np.float32)
        for ps in range(0, N_PERM, batch_perm):
            pe = min(ps + batch_perm, N_PERM)
            sums = signs[ps:pe] @ xx
            tperm = np.zeros_like(sums)
            tperm[:, valid_denom] = sums[:, valid_denom] / denom[valid_denom]
            chunk_max[ps:pe] = np.max(tperm, axis=1)
        max_null = np.maximum(max_null, chunk_max)
        start = stop
    del signs

    # Monte Carlo plus-one p-values avoid zero estimates.
    p_fwer = (1 + np.count_nonzero(max_null[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)
    order = np.argsort(p_unc)
    sig = p_fwer <= ALPHA
    q = np.full(nvox, np.nan, dtype=np.float32)
    ranks = np.arange(1, nvox + 1)
    raw_q = p_unc[order] * nvox / ranks
    q_sorted = np.minimum.accumulate(raw_q[::-1])[::-1]
    q[order] = np.minimum(q_sorted, 1)

    def volume(values: np.ndarray, fill: float = 0) -> np.ndarray:
        v = np.full(ref.shape, fill, dtype=np.float32)
        v[support] = np.asarray(values, dtype=np.float32)
        return v

    def save_map(filename: str, values: np.ndarray) -> None:
        nib.save(nib.Nifti1Image(volume(values), ref.affine, ref.header), OUT / filename)

    save_map("group_mean.nii.gz", means)
    save_map("group_t.nii.gz", t_obs)
    save_map("p_uncorrected.nii.gz", p_unc)
    save_map("p_fwer_maxT.nii.gz", p_fwer)
    save_map("q_fdr_bh.nii.gz", q)
    save_map("coverage_count.nii.gz", coverage_count[support])
    save_map("t_fwer_significant.nii.gz", np.where(sig, t_obs, 0))

    # Independent anatomical vmPFC mask from Harvard-Oxford cortical atlas.
    atlas_file = ROOT / "reference/HarvardOxford-cort-maxprob-thr25-2mm.nii.gz"
    atlas_hash = sha256(atlas_file)
    expected_atlas_hash = "586d76a7defd278fcea4d83d301994d7e096aa8272d26e3c7539b4f8ebd588c1"
    if atlas_hash != expected_atlas_hash:
        raise ValueError("Bundled vmPFC atlas checksum mismatch")
    atlas_img = nib.load(atlas_file)
    atlas_on_maps = image.resample_to_img(atlas_img, ref, interpolation="nearest")
    labels = np.asarray(atlas_on_maps.dataobj)
    # Harvard-Oxford deterministic atlas indices: frontal pole=1, frontal
    # medial=25, subcallosal=27, paracingulate=28.
    atlas_ids = [1, 25, 27, 28]
    xyz = nib.affines.apply_affine(ref.affine, np.column_stack(np.where(np.ones(ref.shape, dtype=bool))))
    xyzvol = np.empty(ref.shape + (3,), dtype=np.float32)
    xyzvol[...] = xyz.reshape(ref.shape + (3,))
    vm_mask = np.isin(labels, atlas_ids) & (np.abs(xyzvol[..., 0]) <= 14) & (xyzvol[..., 2] < 0)
    roi = vm_mask[support]
    if roi.sum() == 0:
        raise ValueError("Independent vmPFC ROI has no supported voxels")
    nib.save(nib.Nifti1Image(vm_mask.astype(np.uint8), ref.affine), OUT / "vmPFC_atlas_mask.nii.gz")
    roi_values = X[:, roi]
    roi_by_sub = roi_values.mean(axis=1, dtype=np.float64)
    roi_mean = float(roi_by_sub.mean())
    roi_sd = float(roi_by_sub.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_ci = stats.t.interval(0.95, n - 1, loc=roi_mean, scale=roi_se)
    roi_t = roi_mean / roi_se
    roi_p_one = float(stats.t.sf(roi_t, n - 1))
    pd.DataFrame({"participant_id": ids, "mean_vmPFC_effect": roi_by_sub}).to_csv(
        OUT / "participant_vmPFC_effects.tsv", sep="\t", index=False)

    coords = np.column_stack(np.where(support))
    mni = nib.affines.apply_affine(ref.affine, coords)
    sig_idx = np.flatnonzero(sig)
    peak_rows = []
    for j in sig_idx[np.argsort(p_fwer[sig_idx])]:
        i, k, l = coords[j]
        peak_rows.append({"i": int(i), "j": int(k), "k": int(l),
                          "x_mni": float(mni[j, 0]), "y_mni": float(mni[j, 1]), "z_mni": float(mni[j, 2]),
                          "mean_effect": float(means[j]), "t": float(t_obs[j]),
                          "p_uncorrected": float(p_unc[j]), "p_fwer_maxT": float(p_fwer[j]),
                          "q_fdr_bh": float(q[j]), "in_vmPFC_atlas_mask": bool(roi[j])})
    pd.DataFrame(peak_rows, columns=["i", "j", "k", "x_mni", "y_mni", "z_mni", "mean_effect", "t", "p_uncorrected", "p_fwer_maxT", "q_fdr_bh", "in_vmPFC_atlas_mask"]).to_csv(
        OUT / "whole_brain_corrected_voxels.tsv", sep="\t", index=False)

    sig_volume = np.zeros(ref.shape, dtype=bool)
    sig_volume[tuple(coords[sig].T)] = True
    clusters, n_clusters = ndimage.label(sig_volume, structure=np.ones((3, 3, 3), dtype=np.uint8))
    cluster_rows = []
    label_names = {1: "Frontal Pole", 25: "Frontal Medial Cortex", 27: "Subcallosal Cortex", 28: "Paracingulate Gyrus"}
    for cluster_id in range(1, n_clusters + 1):
        vox = np.column_stack(np.where(clusters == cluster_id))
        flat = np.ravel_multi_index(vox.T, ref.shape)
        idx = np.searchsorted(np.ravel_multi_index(coords.T, ref.shape), flat)
        idx = np.clip(idx, 0, len(coords)-1)
        # Find the peak using coordinates matched to this cluster's support voxels.
        actual = np.flatnonzero(sig & np.isin(np.ravel_multi_index(coords.T, ref.shape), flat))
        peak = actual[np.argmax(t_obs[actual])]
        peak_xyz = nib.affines.apply_affine(ref.affine, coords[peak])
        peak_label = int(labels[tuple(coords[peak])])
        cluster_rows.append({"cluster": cluster_id, "n_voxels": len(vox),
                             "peak_x_mni": float(peak_xyz[0]), "peak_y_mni": float(peak_xyz[1]),
                             "peak_z_mni": float(peak_xyz[2]), "peak_t": float(t_obs[peak]),
                             "peak_p_fwer": float(p_fwer[peak]), "peak_atlas_label": label_names.get(peak_label, str(peak_label)),
                             "vmPFC_overlap": bool(np.any(vm_mask[tuple(vox.T)]))})
    pd.DataFrame(cluster_rows).sort_values("n_voxels", ascending=False).to_csv(OUT / "whole_brain_clusters.tsv", sep="\t", index=False)

    summary = {
        "n_participants": n, "n_input_maps": len(paths), "n_excluded": 0,
        "shape": list(ref.shape), "zooms_mm": [float(z) for z in ref.header.get_zooms()[:3]],
        "affine": ref.affine.tolist(), "coverage_threshold_fraction": MIN_COVERAGE,
        "n_inference_voxels": nvox, "n_vmPFC_supported_voxels": int(roi.sum()),
        "vmPFC_definition": "Harvard-Oxford cortical labels 1,25,27,28; |MNI x|<=14 mm; MNI z<0",
        "vmPFC_atlas_sha256": atlas_hash,
        "vmPFC_mean_effect": roi_mean, "vmPFC_sd_between_participants": roi_sd,
        "vmPFC_mean_95ci": [float(x) for x in roi_ci], "vmPFC_t": float(roi_t),
        "vmPFC_df": n-1, "vmPFC_p_one_sided_descriptive": roi_p_one,
        "whole_brain_method": "one-sided studentized mean, participant sign flips, single-step max-T (observed voxelwise SD fixed across flips)",
        "permutations": N_PERM, "random_seed": SEED,
        "min_attainable_mc_p": 1/(N_PERM+1), "alpha": ALPHA,
        "n_voxels_fwer_lt_alpha": int(sig.sum()),
        "n_fwer_clusters_26_connected": int(n_clusters),
        "n_voxels_fdr_lt_alpha": int(np.count_nonzero(q < ALPHA)),
        "smallest_fwer_p": float(p_fwer.min()), "largest_observed_t": float(t_obs.max()),
        "max_null_t_95pct": float(np.quantile(max_null, .95)),
        "checksums_verified": len(qc),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    np.savez_compressed(OUT / "permutation_maxT.npz", max_null=max_null)

    # Figure 1: distribution of participant-level ROI averages with group CI.
    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    rngj = np.random.default_rng(SEED)
    ax.scatter(rngj.normal(0, .035, n), roi_by_sub, color="#375a7f", alpha=.78, s=28, edgecolor="white", linewidth=.35)
    ax.errorbar(0, roi_mean, yerr=[[roi_mean-roi_ci[0]], [roi_ci[1]-roi_mean]], fmt="D", color="#c0392b", capsize=5, markersize=7, label="Mean and 95% t interval")
    ax.axhline(0, color="black", linewidth=.8)
    ax.set(xlim=(-.18, .18), xticks=[], ylabel="Mean gain-effect estimate in vmPFC atlas mask", title="Participant variation in vmPFC gain-effect estimates")
    ax.legend(frameon=False, loc="best")
    fig.savefig(OUT / "vmPFC_participants.png", dpi=180)
    plt.close(fig)

    # Figure 2: unthresholded group t map, shown for context; corrected
    # significance is represented by the separate FWER p map.
    t_img = nib.load(OUT / "t_fwer_significant.nii.gz")
    disp = plotting.plot_stat_map(t_img, bg_img=datasets.load_mni152_template(resolution=2),
                                  threshold=0, display_mode="ortho", cut_coords=(30, -100, -5),
                                  title="Positive gain effects: whole-brain max-T FWE p<.05",
                                  cmap="cold_hot", colorbar=True, draw_cross=False)
    disp.savefig(OUT / "whole_brain_fwer_map.png", dpi=180)
    disp.close()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
