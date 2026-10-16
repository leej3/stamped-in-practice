#!/usr/bin/env python3
"""Group inference for NARPS AO86 equal-indifference gain effect maps.

Inputs are fixed participant COPE images; this script does not model scans.
Run with the prepared Python environment, e.g. python analysis/analyze.py.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from scipy import ndimage
from nilearn import plotting

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
N_PERM = 4999
SEED = 20261016
BLOCK = 128


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_nifti(values: np.ndarray, reference: nib.Nifti1Image, path: Path) -> None:
    img = nib.Nifti1Image(values.astype(np.float32).reshape(reference.shape), reference.affine, reference.header)
    img.set_data_dtype(np.float32)
    nib.save(img, str(path))


def main() -> None:
    manifest = json.loads((INPUT / "sources.json").read_text())
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    files = manifest["files"]
    expected_ids = participants.participant_id.tolist()
    assert len(expected_ids) == 54 and participants.group.eq("equalIndifference").all()
    assert len(files) == 57  # 54 images plus 3 metadata files

    imgs: list[nib.Nifti1Image] = []
    data: list[np.ndarray] = []
    qc_rows = []
    for participant_id in expected_ids:
        rel = f"data/{participant_id}_hypo1_cope.nii.gz"
        path = INPUT / rel
        info = files[rel]
        digest = sha256(path)
        if path.stat().st_size != info["bytes"] or digest != info["sha256"]:
            raise ValueError(f"Input integrity check failed: {rel}")
        img = nib.load(str(path))
        arr = np.asarray(img.dataobj, dtype=np.float32)
        if imgs and (img.shape != imgs[0].shape or not np.allclose(img.affine, imgs[0].affine)):
            raise ValueError(f"Image grid differs: {rel}")
        if not np.isfinite(arr).all():
            raise ValueError(f"Non-finite voxel values: {rel}")
        imgs.append(img)
        data.append(arr)
        nonzero = arr != 0
        qc_rows.append({
            "participant_id": participant_id,
            "sha256_verified": True,
            "shape": "x".join(map(str, img.shape)),
            "voxel_size_mm": "x".join(f"{x:g}" for x in img.header.get_zooms()[:3]),
            "nonzero_voxels": int(nonzero.sum()),
            "nonzero_fraction": float(nonzero.mean()),
            "nonzero_value_sd": float(arr[nonzero].std(ddof=1)),
            "nonzero_value_min": float(arr[nonzero].min()),
            "nonzero_value_max": float(arr[nonzero].max()),
        })
    x3 = np.stack(data, axis=0)
    # All-participant common support: maps encode outside-coverage voxels as 0.
    # This avoids changing n across voxels and excludes the zero-filled background.
    mask = np.all(x3 != 0, axis=0)
    if mask.sum() < 100_000:
        raise ValueError(f"Unexpectedly small common support ({mask.sum()} voxels)")
    X = x3[:, mask].astype(np.float64, copy=False)
    n, nvox = X.shape
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    df = n - 1
    p_unc = stats.t.sf(t_obs, df)
    ci_low, ci_high = mean - stats.t.ppf(.975, df) * sd / np.sqrt(n), mean + stats.t.ppf(.975, df) * sd / np.sqrt(n)

    # One-sided whole-brain max-t sign-flip permutation. Under the one-sample
    # null, participant effects are independently sign-flipped; the maximum
    # positive t over common brain support controls family-wise error.
    rng = np.random.default_rng(SEED)
    max_t = np.empty(N_PERM, dtype=np.float32)
    sumsq = np.einsum("ij,ij->j", X, X, optimize=True)
    denom_const = np.sqrt((n - 1) / (n * sumsq))
    for start in range(0, N_PERM, BLOCK):
        b = min(BLOCK, N_PERM - start)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
        signed_sum = signs @ X
        denom = np.sqrt(np.maximum(1.0 - signed_sum * signed_sum / (n * sumsq), 1e-15))
        perm_t = signed_sum * denom_const / denom
        max_t[start:start + b] = perm_t.max(axis=1)
    p_fwe = (1 + (max_t[:, None] >= t_obs[None, :]).sum(axis=0)) / (N_PERM + 1)
    tcrit = float(np.quantile(max_t, .95, method="higher"))
    sig = p_fwe <= .05

    # Independent, compact vmPFC ROI for a transparent effect-size summary.
    # Sphere centered at MNI (0, 40, -12), radius 10 mm; defined in anatomy,
    # not selected from these maps. ROI p-value is descriptive, not the test
    # of support (which requires whole-brain FWE control above).
    ijk = np.indices(imgs[0].shape, dtype=np.float32).reshape(3, -1).T
    xyz = nib.affines.apply_affine(imgs[0].affine, ijk)
    roi_full = (np.sum((xyz - np.array([0, 40, -12], dtype=np.float32)) ** 2, axis=1) <= 10**2).reshape(imgs[0].shape)
    roi = roi_full & mask
    if roi.sum() < 10:
        raise ValueError(f"ROI intersection unexpectedly small ({roi.sum()} voxels)")
    roi_subject = x3[:, roi].mean(axis=1)
    roi_mean = float(roi_subject.mean())
    roi_sd = float(roi_subject.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_ci = stats.t.interval(.95, df, loc=roi_mean, scale=roi_se)
    roi_t = float(roi_mean / roi_se)
    roi_p_one = float(stats.t.sf(roi_t, df))
    roi_tmax = float(t_obs[roi[mask]].max())
    roi_peak_p_fwe = float(p_fwe[roi[mask]][np.argmax(t_obs[roi[mask]])])

    # Save reproducible tabular QC and statistical outputs.
    qc = pd.DataFrame(qc_rows)
    qc.to_csv(OUT / "input_qc.tsv", sep="\t", index=False)
    pd.DataFrame({"participant_id": expected_ids, "vmPFC_sphere_mean_effect": roi_subject}).to_csv(
        OUT / "vmPFC_participant_effects.tsv", sep="\t", index=False
    )
    pd.DataFrame([{
        "n": n, "common_support_voxels": int(nvox), "roi_voxels": int(roi.sum()),
        "roi_center_mni_mm": "0,40,-12", "roi_radius_mm": 10,
        "roi_mean_effect": roi_mean, "roi_sd": roi_sd, "roi_ci95_low": roi_ci[0],
        "roi_ci95_high": roi_ci[1], "roi_t": roi_t, "roi_df": df,
        "roi_one_sided_p_uncorrected": roi_p_one,
        "vmPFC_peak_t": roi_tmax, "vmPFC_peak_p_fwe": roi_peak_p_fwe,
        "whole_brain_positive_voxels_fwe05": int(sig.sum()),
        "maxT_critical_t_fwe05": tcrit, "permutations": N_PERM,
        "random_seed": SEED, "direction": "one-sided positive",
    }]).to_csv(OUT / "summary.tsv", sep="\t", index=False)

    ref = imgs[0]
    for name, values in [("mean_effect.nii.gz", mean), ("t_stat.nii.gz", t_obs),
                         ("p_uncorrected.nii.gz", p_unc), ("p_fwe_maxT.nii.gz", p_fwe),
                         ("ci95_low.nii.gz", ci_low), ("ci95_high.nii.gz", ci_high)]:
        full = np.zeros(ref.shape, dtype=np.float32)
        full[mask] = values
        write_nifti(full, ref, OUT / name)
    full_sig = np.zeros(ref.shape, dtype=np.uint8)
    full_sig[mask] = sig.astype(np.uint8)
    nib.save(nib.Nifti1Image(full_sig, ref.affine, ref.header), str(OUT / "significant_fwe05.nii.gz"))
    np.save(OUT / "max_t_null.npy", max_t)

    # Connected components at the voxelwise whole-brain FWE threshold.
    sig_full = np.zeros(ref.shape, dtype=bool)
    sig_full[mask] = sig
    labels, n_labels = ndimage.label(sig_full, structure=np.ones((3, 3, 3), dtype=bool))
    cluster_rows = []
    t_full = np.zeros(ref.shape, dtype=np.float32)
    p_full = np.ones(ref.shape, dtype=np.float32)
    t_full[mask], p_full[mask] = t_obs, p_fwe
    for label in range(1, n_labels + 1):
        vox = labels == label
        ijk_peak = np.argwhere(vox)[np.argmax(t_full[vox])]
        xyz_peak = nib.affines.apply_affine(ref.affine, ijk_peak)
        cluster_rows.append({
            "cluster": label, "voxels_26connected": int(vox.sum()),
            "peak_x_mni": float(xyz_peak[0]), "peak_y_mni": float(xyz_peak[1]),
            "peak_z_mni": float(xyz_peak[2]), "peak_t": float(t_full[vox].max()),
            "peak_p_fwe": float(p_full[vox].min()),
        })
    pd.DataFrame(cluster_rows).to_csv(OUT / "fwe_clusters.tsv", sep="\t", index=False)

    # Display uncorrected t only as a descriptive map; significance is judged
    # exclusively with the whole-brain FWE-corrected max-t result.
    t_img = nib.load(str(OUT / "t_stat.nii.gz"))
    display = plotting.plot_stat_map(
        t_img, threshold=2.0, display_mode="ortho", cut_coords=(0, 40, -12),
        title="Uncorrected t map (display only; inference uses FWE map)",
        cmap="cold_hot", symmetric_cbar=True, colorbar=True,
        black_bg=False, annotate=True, draw_cross=True,
    )
    display.savefig(FIG / "group_t_map.png", dpi=180)
    display.close()
    display = plotting.plot_glass_brain(
        t_img, threshold=tcrit, plot_abs=False, display_mode="lyrz",
        title="Positive clusters: one-sided whole-brain max-t FWE p <= .05",
        cmap="hot", colorbar=True, black_bg=False, annotate=True,
    )
    display.savefig(FIG / "group_t_map_fwe.png", dpi=180)
    display.close()

    fig, ax = plt.subplots(figsize=(8.3, 4.8), constrained_layout=True)
    rng_plot = np.random.default_rng(SEED)
    jitter = rng_plot.normal(0, .035, size=n)
    ax.scatter(jitter, roi_subject, s=28, alpha=.72, color="#2b6f8a", edgecolor="white", linewidth=.35)
    ax.errorbar(0, roi_mean, yerr=[[roi_mean - roi_ci[0]], [roi_ci[1] - roi_mean]],
                fmt="D", color="#bd4b35", capsize=5, markersize=7, linewidth=2,
                label="Mean and 95% t interval")
    ax.axhline(0, color="0.35", linewidth=1, linestyle="--")
    ax.set(xlim=(-.28, .28), xticks=[], ylabel="Participant mean gain effect (COPE units)",
           title="vmPFC anatomical sphere: participant effects")
    ax.legend(frameon=False, loc="best")
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    fig.savefig(FIG / "vmPFC_effects.png", dpi=180)
    plt.close(fig)

    print(f"n={n}; common-support voxels={nvox}; vmPFC voxels={roi.sum()}")
    print(f"vmPFC mean={roi_mean:.6g}, 95% CI [{roi_ci[0]:.6g}, {roi_ci[1]:.6g}], t({df})={roi_t:.3f}, one-sided p={roi_p_one:.4g}")
    print(f"max-t critical t={tcrit:.3f}; whole-brain FWE-positive voxels={sig.sum()}")
    print(f"input checksums verified={qc.sha256_verified.all()}, nonfinite voxels={int((~np.isfinite(x3)).sum())}")


if __name__ == "__main__":
    main()
