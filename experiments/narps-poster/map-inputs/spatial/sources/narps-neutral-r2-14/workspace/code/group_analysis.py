#!/usr/bin/env python3
"""Group analysis of fixed NARPS AO86 participant gain-effect maps.

Primary inference: one-sided, one-sample sign-flip max-t permutation test,
controlling family-wise error over the complete analysis mask.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets, image
from scipy import stats, ndimage
import matplotlib.pyplot as plt
from nilearn import plotting


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
N_PERM_DEFAULT = 4999
SEED_DEFAULT = 20261016


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_inputs():
    src = json.loads((INPUT / "sources.json").read_text())
    table = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    files = sorted((INPUT / "data").glob("*_hypo1_cope.nii.gz"))
    expected = {x["participant_id"]: x for x in src["files"].values() if x.get("participant_id")}
    if len(files) != 54 or len(table) != 54 or len(expected) != 54:
        raise ValueError(f"Expected 54 maps/participants, got {len(files)}/{len(table)}")
    by_id = {p.stem.split("_")[0]: p for p in files}
    if set(by_id) != set(table.participant_id) or set(by_id) != set(expected):
        raise ValueError("Map participant IDs do not exactly match metadata/source manifest")
    imgs, checks = [], []
    ref = None
    for pid in table.participant_id:
        path = by_id[pid]
        img = nib.load(str(path))
        if ref is None:
            ref = img
        if img.shape != ref.shape or not np.allclose(img.affine, ref.affine, atol=1e-5):
            raise ValueError(f"Spatial grid mismatch for {pid}")
        a = img.get_fdata(dtype=np.float32)
        if not np.isfinite(a).all():
            raise ValueError(f"Non-finite voxels in {pid}")
        checksum = sha256(path)
        expected_item = expected[pid]
        if checksum != expected_item["sha256"]:
            raise ValueError(f"SHA256 mismatch for {pid}")
        if path.stat().st_size != expected_item["bytes"]:
            raise ValueError(f"Byte size mismatch for {pid}")
        checks.append({"participant_id": pid, "sha256": checksum, "bytes": path.stat().st_size})
        imgs.append(a)
    return table, np.stack(imgs, axis=0), ref, checks


def get_vmpfc_mask(ref):
    """AAL3 bilateral medial orbitofrontal anatomical proxy for vmPFC."""
    atlas = datasets.fetch_atlas_aal(version="3v2", verbose=0)
    atlas_img = nib.load(atlas.maps)
    labels = [x.decode() if isinstance(x, bytes) else str(x) for x in atlas.labels]
    # AAL3 labels use Frontal_Med_Orb_L/R; fail closed if atlas naming changes.
    selected = [i for i, label in enumerate(labels) if label in {"Frontal_Med_Orb_L", "Frontal_Med_Orb_R"}]
    if len(selected) != 2:
        raise RuntimeError(f"Could not uniquely identify bilateral AAL3 medial OFC parcels: {selected}")
    selected_ids = [int(atlas.indices[i]) for i in selected]
    atlas_data = np.asarray(atlas_img.dataobj)
    roi_native = np.isin(atlas_data, selected_ids).astype(np.uint8)
    roi_img = nib.Nifti1Image(roi_native, atlas_img.affine, atlas_img.header)
    roi_resampled = image.resample_to_img(roi_img, ref, interpolation="nearest", force_resample=True, copy_header=True)
    return np.asarray(roi_resampled.dataobj) > 0, atlas, [labels[i] for i in selected]


def one_sample_t(x):
    n = x.shape[0]
    mean = x.mean(axis=0, dtype=np.float64)
    sd = x.std(axis=0, ddof=1, dtype=np.float64)
    t = np.divide(mean, sd / np.sqrt(n), out=np.zeros_like(mean), where=sd > 0)
    return mean, sd, t


def max_t_permutation(x, n_perm, seed, block_voxels=4000, batch_size=64):
    """Sign-flip null for one-sample t; returns observed t and max-t null."""
    n, nvox = x.shape
    mean, sd, obs_t = one_sample_t(x)
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(n_perm, n)).astype(np.float32)
    null_max = np.full(n_perm, -np.inf, dtype=np.float64)
    sumsq = np.sum(x.astype(np.float64) ** 2, axis=0)
    for start in range(0, nvox, block_voxels):
        stop = min(start + block_voxels, nvox)
        xb = x[:, start:stop].astype(np.float32, copy=False)
        ss = sumsq[start:stop]
        for p0 in range(0, n_perm, batch_size):
            p1 = min(p0 + batch_size, n_perm)
            signed_sum = signs[p0:p1] @ xb
            perm_mean = signed_sum / n
            # Sign flips preserve each observation's squared value.
            perm_var = np.maximum((ss[None, :] - signed_sum.astype(np.float64) ** 2 / n) / (n - 1), 0)
            denom = np.sqrt(perm_var / n)
            t = np.divide(perm_mean, denom, out=np.zeros_like(perm_mean, dtype=np.float64), where=denom > 0)
            null_max[p0:p1] = np.maximum(null_max[p0:p1], np.max(t, axis=1))
    return mean, sd, obs_t, null_max


def save_img(data, ref, path, dtype=np.float32):
    h = ref.header.copy()
    h.set_data_dtype(dtype)
    nib.save(nib.Nifti1Image(np.asarray(data, dtype=dtype), ref.affine, h), str(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--permutations", type=int, default=N_PERM_DEFAULT)
    parser.add_argument("--seed", type=int, default=SEED_DEFAULT)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    table, maps, ref, checks = load_inputs()
    coverage = np.count_nonzero(maps, axis=0)
    mask = coverage >= int(np.ceil(0.90 * len(table)))
    if mask.sum() < 1000:
        raise RuntimeError("Analysis mask unexpectedly small")
    roi, atlas, roi_labels = get_vmpfc_mask(ref)
    roi &= mask
    X = maps[:, mask].astype(np.float32)
    voxel_coords = np.argwhere(mask)

    mean, sd, t_obs, max_null = max_t_permutation(X, args.permutations, args.seed)
    # Corrected empirical p for positive effects, family-wise over the whole mask.
    p_fwe = (1 + (max_null[:, None] >= t_obs[None, :]).sum(axis=0)) / (args.permutations + 1)
    alpha = 0.05
    critical = float(np.quantile(max_null, 1 - alpha, method="higher"))
    sig = t_obs >= critical
    roi_vec = roi[mask]
    roi_mean = float(mean[roi_vec].mean()) if roi_vec.any() else float("nan")
    roi_sd_vox = float(mean[roi_vec].std(ddof=1)) if roi_vec.sum() > 1 else float("nan")

    mean_img = np.zeros(ref.shape, dtype=np.float32); mean_img[mask] = mean
    t_img = np.zeros(ref.shape, dtype=np.float32); t_img[mask] = t_obs
    p_img = np.ones(ref.shape, dtype=np.float32); p_img[mask] = p_fwe
    sig_img = np.zeros(ref.shape, dtype=np.uint8); sig_img[mask] = sig.astype(np.uint8)
    mask_img = mask.astype(np.uint8)
    roi_img_data = roi.astype(np.uint8)
    save_img(mean_img, ref, OUT / "group_mean_effect.nii.gz")
    save_img(t_img, ref, OUT / "group_t_unthresholded.nii.gz")
    save_img(p_img, ref, OUT / "group_p_fwe_maxT.nii.gz")
    save_img(sig_img, ref, OUT / "group_positive_fwe05.nii.gz", dtype=np.uint8)
    save_img(mask_img, ref, OUT / "analysis_mask_90pct_coverage.nii.gz", dtype=np.uint8)
    save_img(roi_img_data, ref, OUT / "vmpfc_aal3_medial_orbitofrontal.nii.gz", dtype=np.uint8)

    # Save participant-level descriptive ROI summaries; the group coefficient is an
    # upstream scale-normalized parametric-modulator estimate, not a currency slope.
    roi_values = maps[:, roi].mean(axis=1) if roi.any() else np.full(len(table), np.nan)
    pd.DataFrame({"participant_id": table.participant_id, "roi_mean_effect": roi_values}).to_csv(OUT / "participant_roi_effects.tsv", sep="\t", index=False)
    roi_t, roi_p_two = stats.ttest_1samp(roi_values, 0.0, nan_policy="omit")
    roi_p_one = float(stats.t.sf(roi_t, df=np.isfinite(roi_values).sum() - 1)) if roi_t >= 0 else float(1 - stats.t.sf(roi_t, df=np.isfinite(roi_values).sum() - 1))
    roi_ci = stats.t.interval(0.95, np.isfinite(roi_values).sum() - 1, loc=np.nanmean(roi_values), scale=stats.sem(roi_values, nan_policy="omit"))
    null_df = pd.DataFrame({"permutation": np.arange(1, args.permutations + 1), "max_t_positive": max_null})
    null_df.to_csv(OUT / "permutation_max_t.tsv", sep="\t", index=False)
    checks_df = pd.DataFrame(checks)
    checks_df.to_csv(OUT / "input_checksums.tsv", sep="\t", index=False)

    labels_3d, n_clusters = ndimage.label(sig_img, structure=np.ones((3, 3, 3), dtype=np.uint8))
    cluster_rows = []
    for cluster_id in range(1, n_clusters + 1):
        cluster = labels_3d == cluster_id
        peak_idx = np.unravel_index(int(np.argmax(np.where(cluster, t_img, -np.inf))), ref.shape)
        peak_xyz = nib.affines.apply_affine(ref.affine, peak_idx)
        cluster_rows.append({"cluster": cluster_id, "voxels": int(cluster.sum()), "peak_t": float(t_img[peak_idx]),
                             "peak_x": float(peak_xyz[0]), "peak_y": float(peak_xyz[1]), "peak_z": float(peak_xyz[2]),
                             "overlaps_vmpfc_proxy": bool(np.any(cluster & roi_img_data.astype(bool)))})
    pd.DataFrame(cluster_rows, columns=["cluster", "voxels", "peak_t", "peak_x", "peak_y", "peak_z", "overlaps_vmpfc_proxy"]).to_csv(OUT / "fwe_clusters.tsv", sep="\t", index=False)

    # QC: characterize nonzero spatial support and participant ROI coefficients.
    per_map = []
    for pid, a in zip(table.participant_id, maps):
        per_map.append({"participant_id": pid, "nonzero_voxels": int(np.count_nonzero(a)), "map_min": float(a.min()), "map_max": float(a.max()), "finite_fraction": float(np.isfinite(a).mean())})
    pd.DataFrame(per_map).to_csv(OUT / "map_qc.tsv", sep="\t", index=False)

    summary = {
        "n_participants": len(table), "n_excluded": 0, "analysis_mask_voxels": int(mask.sum()),
        "analysis_mask_rule": "nonzero in at least 90% of all 54 participant maps",
        "roi_voxels_in_mask": int(roi.sum()), "roi_definition": f"AAL3 v3v2 bilateral medial orbitofrontal parcels: {', '.join(roi_labels)}",
        "atlas_name": "Automated Anatomical Labeling atlas 3, version 3v2 (AAL3v2)", "permutations": args.permutations, "seed": args.seed,
        "inference": "one-sided positive one-sample t; random sign flips; max-t family-wise correction across analysis mask",
        "fwe_alpha": alpha, "max_t_critical_95": critical, "n_fwe_significant_voxels": int(sig.sum()),
        "n_fwe_clusters_26_connected": int(n_clusters), "n_fwe_voxels_in_vmpfc_proxy": int(np.sum(sig_img.astype(bool) & roi)),
        "minimum_whole_brain_fwe_p_in_vmpfc_proxy": float(np.min(p_fwe[roi[mask]])) if roi_vec.any() else None,
        "max_observed_t": float(np.max(t_obs)), "peak_corrected_p_fwe": float(np.min(p_fwe)),
        "peak_voxel_mni_mm": [float(v) for v in nib.affines.apply_affine(ref.affine, voxel_coords[int(np.argmax(t_obs))])],
        "roi_mean_of_voxelwise_group_means": roi_mean, "roi_sd_across_voxelwise_group_means": roi_sd_vox,
        "roi_participant_mean": float(np.nanmean(roi_values)), "roi_participant_sd": float(np.nanstd(roi_values, ddof=1)),
        "roi_participant_95ci": [float(roi_ci[0]), float(roi_ci[1])], "roi_participant_t_descriptive": float(roi_t),
        "roi_participant_one_sided_p_uncorrected_descriptive": roi_p_one,
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": __import__("scipy").__version__,
                     "pandas": pd.__version__, "nibabel": nib.__version__, "nilearn": __import__("nilearn").__version__},
        "input_checksums_all_match": True, "all_maps_same_shape_affine_finite": True,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Figures: the primary map is unthresholded, with the anatomical ROI outlined;
    # corrected map is shown separately so absence of clusters stays visible.
    template = datasets.load_mni152_template(resolution=2)
    display = plotting.plot_stat_map(nib.Nifti1Image(t_img, ref.affine), bg_img=template,
                                     threshold=2.0, display_mode="ortho", cut_coords=(2, 52, -8),
                                     title="Group t map (display t>2); AAL3 vmPFC proxy outline",
                                     cmap="cold_hot", colorbar=True, vmin=0)
    display.add_contours(nib.Nifti1Image(roi_img_data, ref.affine), levels=[0.5], colors=["cyan"], linewidths=1.2)
    display.savefig(str(FIG / "group_t_map.png"), dpi=180)
    display.close()
    if sig.any():
        peak_idx = tuple(voxel_coords[int(np.argmax(t_obs))])
        peak_xyz = nib.affines.apply_affine(ref.affine, peak_idx)
        display = plotting.plot_stat_map(nib.Nifti1Image(np.where(sig_img, t_img, 0), ref.affine), bg_img=template,
                                         threshold=0.0, display_mode="ortho", cut_coords=tuple(float(x) for x in peak_xyz),
                                         title="Positive gain effects surviving whole-brain max-t FWE p<.05",
                                         cmap="cold_hot", colorbar=True, vmin=0)
    else:
        display = plotting.plot_anat(template, display_mode="ortho", cut_coords=(0, 40, -10),
                                     title="No voxels survive whole-brain max-t FWE p<.05")
    display.savefig(str(FIG / "group_fwe05.png"), dpi=180)
    display.close()
    plt.figure(figsize=(7.4, 4.6))
    plt.hist(roi_values, bins=12, color="#4c78a8", edgecolor="white")
    plt.axvline(0, color="black", lw=1)
    plt.axvline(np.nanmean(roi_values), color="#e45756", lw=2, label=f"mean = {np.nanmean(roi_values):.3g}")
    plt.xlabel("Mean participant effect in AAL3 bilateral medial OFC ROI")
    plt.ylabel("Participants")
    plt.title("Participant vmPFC proxy estimates (descriptive)")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG / "roi_participant_distribution.png", dpi=180)
    plt.close()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
