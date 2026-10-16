#!/usr/bin/env python3
"""Group inference for fixed NARPS AO86 participant gain effects."""
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from nilearn import datasets, image, plotting
from scipy import ndimage, stats

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = OUT / "figures"
MAPS = INPUT / "data"
SEED = 20261016
N_PERM = 9999
ALPHA = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_map(data: np.ndarray, ref: nib.spatialimages.SpatialImage, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    hdr = ref.header.copy()
    hdr.set_data_dtype(np.float32)
    nib.save(nib.Nifti1Image(data.astype(np.float32), ref.affine, hdr), path)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    meta = pd.read_csv(INPUT / "participants.tsv", sep="\t", dtype={"participant_id": str})
    sources = json.loads((INPUT / "sources.json").read_text())
    if set(meta["group"]) != {"equalIndifference"}:
        raise ValueError("Metadata includes participants outside the requested equal-indifference cohort")
    paths = sorted(MAPS.glob("sub-*_hypo1_cope.nii.gz"))
    image_ids = [p.name.split("_")[0] for p in paths]
    if meta.participant_id.duplicated().any() or len(set(image_ids)) != len(image_ids):
        raise ValueError("Duplicate participant identifiers")
    if set(meta.participant_id) != set(image_ids) or len(paths) != 54:
        raise ValueError("Supplied image IDs do not exactly match the 54-person cohort")
    meta = meta.set_index("participant_id").loc[image_ids].reset_index()

    ref = nib.load(str(paths[0]))
    arrs, image_qc = [], []
    for p in paths:
        img = nib.load(str(p))
        if img.shape != ref.shape or not np.allclose(img.affine, ref.affine, atol=1e-4):
            raise ValueError(f"Image grid mismatch: {p}")
        arr = img.get_fdata(dtype=np.float32)
        finite = np.isfinite(arr)
        if not finite.all():
            raise ValueError(f"Nonfinite image values: {p}")
        arrs.append(arr)
        checksum = sha256(p)
        expected = sources["files"][f"data/{p.name}"]["sha256"]
        if checksum != expected:
            raise ValueError(f"Source checksum mismatch: {p}")
        image_qc.append({
            "participant_id": p.name.split("_")[0],
            "bytes": p.stat().st_size,
            "sha256": checksum,
            "shape": list(img.shape),
            "zooms_mm": [float(z) for z in img.header.get_zooms()[:3]],
            "zero_fraction": float(np.mean(arr == 0)),
            "minimum": float(arr.min()),
            "maximum": float(arr.max()),
            "mean_all_voxels": float(arr.mean()),
        })
    stack = np.stack(arrs, axis=0)

    # Exact zero indicates no map support. Use the complete intersection of
    # all participant supports inside an independent standard brain mask, so
    # each voxelwise test has the same n and no absent estimate is set to zero.
    coverage_fraction = np.mean(stack != 0, axis=0)
    brain_mask_source = datasets.load_mni152_brain_mask(resolution=2)
    brain_mask_on_ref = image.resample_to_img(brain_mask_source, ref, interpolation="nearest")
    brain_mask = np.asarray(brain_mask_on_ref.dataobj) > 0
    mask = (coverage_fraction == 1.0) & brain_mask

    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    atlas_img = atlas.maps
    atlas_on_ref = image.resample_to_img(atlas_img, ref, interpolation="nearest")
    atlas_labels = np.asarray(atlas_on_ref.dataobj, dtype=np.int16)
    label_map = {name: i for i, name in enumerate(atlas.labels)}
    roi = np.isin(atlas_labels, [label_map["Subcallosal Cortex"], label_map["Frontal Orbital Cortex"]])
    x_coords = nib.affines.apply_affine(ref.affine, np.indices(ref.shape).reshape(3, -1).T)[:, 0].reshape(ref.shape)
    roi &= np.abs(x_coords) <= 20
    roi &= mask
    if not mask.any() or not roi.any():
        raise ValueError("Empty analysis or vmPFC proxy mask")

    n = stack.shape[0]
    y = stack[:, mask].astype(np.float64)
    mean = y.mean(axis=0)
    sd = y.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = stats.t.sf(t_obs, df=n - 1)
    check_idx = np.unique(np.linspace(0, len(t_obs) - 1, num=min(12, len(t_obs)), dtype=int))
    t_reference = stats.ttest_1samp(y[:, check_idx], popmean=0, axis=0).statistic
    if not np.allclose(t_obs[check_idx], t_reference, rtol=1e-12, atol=1e-12):
        raise AssertionError("Independent observed voxelwise t check failed")

    # Sign-flip max-T: sign symmetry under the zero-mean null, with positive
    # one-sided statistic and FWE over every voxel in the declared group mask.
    rng = np.random.default_rng(SEED)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n), replace=True)
    signs = np.vstack([signs, np.ones((1, n), dtype=np.float64)])
    max_null = np.full(len(signs), -np.inf, dtype=np.float64)
    sumsquares = np.sum(y * y, axis=0)
    denom_base = n * sumsquares
    chunk = 10000
    for start in range(0, y.shape[1], chunk):
        stop = min(start + chunk, y.shape[1])
        block = y[:, start:stop]
        sums = signs @ block
        # For a one-sample t statistic: t = sum(x) * sqrt(n-1) /
        # sqrt(n * sum(x^2) - sum(x)^2). Sign flips leave sum(x^2) fixed.
        denom_sq = (n * sumsquares[start:stop][None, :] - sums * sums) / (n - 1)
        t_null = np.divide(sums, np.sqrt(np.maximum(denom_sq, 1e-30)), out=np.zeros_like(sums), where=denom_sq > 0)
        max_null = np.maximum(max_null, np.max(t_null, axis=1))
    # Independently verify the sign-flipped t calculation at sampled voxels.
    null_reference = stats.ttest_1samp(signs[0, :, None] * y[:, check_idx], popmean=0, axis=0).statistic
    null_sums = signs[0] @ y[:, check_idx]
    null_sq = np.sum(y[:, check_idx] ** 2, axis=0)
    null_formula = null_sums / np.sqrt((n * null_sq - null_sums**2) / (n - 1))
    if not np.allclose(null_formula, null_reference, rtol=1e-12, atol=1e-12):
        raise AssertionError("Independent sign-flip t check failed")
    p_fwe = np.sum(max_null[:, None] >= t_obs[None, :], axis=0) / len(max_null)
    sig = p_fwe <= ALPHA

    mean_map = np.zeros(ref.shape, np.float32)
    t_map = np.zeros(ref.shape, np.float32)
    p_map = np.ones(ref.shape, np.float32)
    fwe_map = np.ones(ref.shape, np.float32)
    mean_map[mask], t_map[mask], p_map[mask], fwe_map[mask] = mean, t_obs, p_unc, p_fwe
    coverage_img = nib.Nifti1Image(coverage_fraction.astype(np.float32), ref.affine, ref.header)
    save_map(mean_map, ref, OUT / "mean_effect.nii.gz")
    save_map(t_map, ref, OUT / "t_statistic.nii.gz")
    save_map(fwe_map, ref, OUT / "fwe_pvalue.nii.gz")
    save_map(mask.astype(np.float32), ref, OUT / "analysis_mask.nii.gz")
    save_map(brain_mask.astype(np.float32), ref, OUT / "mni152_brain_mask_on_map_grid.nii.gz")
    save_map(roi.astype(np.float32), ref, OUT / "vmPFC_proxy_mask.nii.gz")
    save_map(coverage_fraction, ref, OUT / "coverage_fraction.nii.gz")

    roi_y = stack[:, roi].astype(np.float64).mean(axis=1)
    roi_t, roi_p_two = stats.ttest_1samp(roi_y, popmean=0)
    roi_p_one = stats.t.sf(roi_t, n - 1)
    roi_se = stats.sem(roi_y)
    roi_ci = stats.t.interval(0.95, df=n - 1, loc=roi_y.mean(), scale=roi_se)
    indep_t = np.mean(roi_y) / (np.std(roi_y, ddof=1) / np.sqrt(n))
    if not np.isclose(roi_t, indep_t, rtol=1e-12, atol=1e-12):
        raise AssertionError("Independent ROI t statistic check failed")
    roi_voxel_p = p_fwe[roi[mask]]
    sig_roi_vox = int(np.sum(roi_voxel_p <= ALPHA))
    sig_volume = np.zeros(ref.shape, dtype=bool)
    sig_volume[mask] = sig
    labels, n_clusters = ndimage.label(sig_volume, structure=ndimage.generate_binary_structure(3, 3))
    voxvol = float(abs(np.linalg.det(ref.affine[:3, :3])))
    cluster_rows = []
    for cluster_id in range(1, n_clusters + 1):
        coords = np.argwhere(labels == cluster_id)
        cluster_t = t_map[labels == cluster_id]
        peak = coords[int(np.argmax(cluster_t))]
        xyz = nib.affines.apply_affine(ref.affine, peak)
        cluster_rows.append({
            "cluster": cluster_id,
            "voxels_26connected": len(coords),
            "volume_mm3": len(coords) * voxvol,
            "peak_t": float(t_map[tuple(peak)]),
            "peak_fwe_p": float(fwe_map[tuple(peak)]),
            "peak_x_mm": float(xyz[0]), "peak_y_mm": float(xyz[1]), "peak_z_mm": float(xyz[2]),
            "overlaps_vmPFC_proxy": bool(np.any(roi[labels == cluster_id])),
        })
    pd.DataFrame(cluster_rows, columns=["cluster", "voxels_26connected", "volume_mm3", "peak_t", "peak_fwe_p", "peak_x_mm", "peak_y_mm", "peak_z_mm", "overlaps_vmPFC_proxy"]).to_csv(OUT / "cluster_summary.tsv", sep="\t", index=False)
    roi_value = {
        "n": n,
        "roi_voxels": int(roi.sum()),
        "roi_mean_effect": float(roi_y.mean()),
        "roi_sd_between_participants": float(roi_y.std(ddof=1)),
        "roi_ci95_low": float(roi_ci[0]),
        "roi_ci95_high": float(roi_ci[1]),
        "roi_t": float(roi_t),
        "roi_p_one_sided_uncorrected_descriptive": float(roi_p_one),
        "roi_p_two_sided_descriptive": float(roi_p_two),
        "roi_participant_mean_effects": [float(v) for v in roi_y],
        "whole_brain_fwe_significant_voxels": int(sig.sum()),
        "whole_brain_fwe_significant_roi_voxels": sig_roi_vox,
        "max_t_observed": float(np.max(t_obs)),
        "max_t_null_95pct": float(np.quantile(max_null, 0.95)),
        "max_t_global_fwe_p": float(np.sum(max_null >= np.max(t_obs)) / len(max_null)),
        "support_hypothesis_by_preregistered_rule": bool(sig_roi_vox > 0),
        "n_analysis_voxels": int(mask.sum()),
        "mni152_brain_mask_voxels": int(brain_mask.sum()),
        "brain_mask_voxels_lost_to_incomplete_map_coverage": int(np.sum(brain_mask & (coverage_fraction < 1.0))),
        "full_coverage_voxels_excluded_outside_brain_mask": int(np.sum((coverage_fraction == 1.0) & ~brain_mask)),
        "analysis_coverage_threshold": 1.0,
        "permutations": N_PERM,
        "permutation_arrangements_including_observed": int(len(max_null)),
        "seed": SEED,
        "alpha_fwe_one_sided": ALPHA,
        "maxT_null_min": float(max_null.min()),
        "maxT_null_median": float(np.median(max_null)),
        "maxT_null_max": float(max_null.max()),
    }
    (OUT / "summary.json").write_text(json.dumps(roi_value, indent=2) + "\n")
    pd.DataFrame(image_qc).to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)
    pd.DataFrame({"participant_id": image_ids, "vmPFC_proxy_mean_effect": roi_y}).to_csv(OUT / "roi_participant_effects.tsv", sep="\t", index=False)

    # A compact distribution plot that shows participant heterogeneity and
    # the t-based confidence interval for the across-participant mean.
    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    order = np.argsort(roi_y)
    ax.scatter(np.arange(n), roi_y[order], s=26, color="#355C7D", alpha=.82, edgecolor="white", linewidth=.4)
    ax.axhline(0, color="0.4", lw=1, ls="--")
    ax.axhline(roi_y.mean(), color="#C44536", lw=2, label=f"Mean = {roi_y.mean():.3g}")
    ax.axhspan(roi_ci[0], roi_ci[1], color="#C44536", alpha=.14, label="95% t interval")
    ax.set(xlabel="Participants (ordered by ROI estimate)", ylabel="Mean gain contrast estimate in vmPFC proxy", title="Participant effects in the anatomical vmPFC proxy")
    ax.legend(frameon=False, loc="best")
    fig.savefig(FIG / "roi_participant_effects.png", dpi=180)
    plt.close(fig)

    mean_img = nib.Nifti1Image(mean_map, ref.affine, ref.header)
    display = plotting.plot_stat_map(
        mean_img, bg_img=datasets.load_mni152_template(resolution=2),
        display_mode="z", cut_coords=[-16, -8, 0, 8, 16],
        threshold=0, cmap="cold_hot", colorbar=True,
        title="Mean gain contrast estimate (uncorrected descriptive map)",
        black_bg=False, dim=0.5,
    )
    display.savefig(FIG / "mean_effect_slices.png", dpi=180)
    display.close()
    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    ax.hist(max_null, bins=35, color="#9BB7D4", edgecolor="white")
    ax.axvline(np.max(t_obs), color="#C44536", lw=2.2, label=f"Observed maximum t = {np.max(t_obs):.2f}")
    ax.axvline(np.quantile(max_null, .95), color="#355C7D", lw=1.6, ls="--", label=f"95th percentile null max t = {np.quantile(max_null, .95):.2f}")
    ax.set(xlabel="Maximum positive t across the whole-brain mask", ylabel="Sign-flip permutations", title="Whole-brain family-wise correction (max-T)")
    ax.legend(frameon=False)
    ax.text(.02, .97, f"{int(sig.sum()):,} voxels survive FWE at .05", transform=ax.transAxes, va="top", ha="left", fontsize=10)
    fig.savefig(FIG / "whole_brain_fwe.png", dpi=180)
    plt.close(fig)

    manifest = {
        "protocol": "protocol.md",
        "input_metadata_sha256": sha256(INPUT / "participants.tsv"),
        "map_checksums": image_qc,
        "atlas": "Harvard-Oxford cortical atlas, maxprob-thr25-2mm; nilearn.datasets.fetch_atlas_harvard_oxford",
        "atlas_file": str(atlas.maps),
        "atlas_sha256": sha256(Path(atlas.filename)),
        "brain_mask": "nilearn.datasets.load_mni152_brain_mask(resolution=2), nearest-neighbor resampled to supplied map grid; saved as results/mni152_brain_mask_on_map_grid.nii.gz",
        "brain_mask_sha256": sha256(OUT / "mni152_brain_mask_on_map_grid.nii.gz"),
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "pandas": pd.__version__, "nibabel": nib.__version__, "nilearn": __import__("nilearn").__version__, "matplotlib": plt.matplotlib.__version__},
        "permutation_details": "Random participant sign flips plus observed arrangement; one-sided voxelwise t; maximum t over the common-support brain mask; empirical tail fraction.",
    }
    (OUT / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(roi_value, indent=2))


if __name__ == "__main__":
    main()
