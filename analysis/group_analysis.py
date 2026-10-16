#!/usr/bin/env python3
"""Group-level analysis of NARPS AO86 equal-indifference gain effect maps."""
from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".mplconfig"))
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets, image, plotting
from scipy import stats
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "input"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
SEED = 20261016
N_PERM = 4999


def main():
    participants = pd.read_csv(IN / "participants.tsv", sep="\t")
    files = sorted((IN / "data").glob("*_hypo1_cope.nii.gz"))
    map_ids = {f.name.split("_")[0] for f in files}
    table_ids = set(participants.participant_id)
    assert len(files) == len(participants) == 54
    assert map_ids == table_ids
    assert participants.group.eq("equalIndifference").all()

    imgs = [nib.load(str(f)) for f in files]
    ref = imgs[0]
    for f, im in zip(files, imgs):
        if im.shape != ref.shape or not np.allclose(im.affine, ref.affine):
            raise ValueError(f"Geometry mismatch: {f}")
    arrays = np.stack([im.get_fdata(dtype=np.float32) for im in imgs], axis=0)
    finite = np.isfinite(arrays).all(axis=0)
    coverage = np.mean(arrays != 0, axis=0)
    # Retain voxels in the supplied participant brain support for at least 90%.
    # This avoids analyzing the zero-filled exterior and limits edge dropout.
    mask = finite & (coverage >= 0.90)
    Y = arrays[:, mask].astype(np.float64)
    n, p = Y.shape
    if n != 54 or p == 0:
        raise RuntimeError("Unexpected participant count or empty analysis mask")

    mean = Y.mean(axis=0)
    sd = Y.std(axis=0, ddof=1)
    se = sd / np.sqrt(n)
    t_obs = mean / se
    p_unc = stats.t.sf(t_obs, df=n - 1)
    p_two = 2 * stats.t.sf(np.abs(t_obs), df=n - 1)

    # One-sided positive sign-flip max-t permutation inference over every voxel
    # in the brain support. Subject signs are independently randomized under
    # the null of exchangeable, symmetric participant-level effect estimates.
    rng = np.random.default_rng(SEED)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n))
    ss = np.sum(Y * Y, axis=0)
    max_t = np.full(N_PERM, -np.inf, dtype=float)
    chunk = 2500
    for start in range(0, p, chunk):
        stop = min(start + chunk, p)
        yc = Y[:, start:stop]
        signed_sums = signs @ yc
        # t = sum(x) / sqrt((n*sum(x^2)-sum(x)^2)/(n-1))
        denom2 = (n * ss[start:stop][None, :] - signed_sums**2) / (n - 1)
        t_perm = signed_sums / np.sqrt(np.maximum(denom2, np.finfo(float).tiny))
        max_t = np.maximum(max_t, np.max(t_perm, axis=1))
    p_fwe = (1 + np.sum(max_t[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)
    crit = np.quantile(max_t, 0.95, method="higher")

    def volume(vec, name, dtype=np.float32):
        d = np.zeros(ref.shape, dtype=dtype)
        d[mask] = vec
        return nib.Nifti1Image(d, ref.affine, ref.header)

    mean_img = volume(mean, "mean")
    t_img = volume(t_obs, "t")
    pfwe_img = volume(p_fwe, "p_fwe")
    mask_img = nib.Nifti1Image(mask.astype(np.uint8), ref.affine, ref.header)
    nib.save(mean_img, OUT / "group_mean_effect.nii.gz")
    nib.save(t_img, OUT / "group_t.nii.gz")
    nib.save(pfwe_img, OUT / "group_p_fwe.nii.gz")
    nib.save(mask_img, OUT / "analysis_mask.nii.gz")

    # Predeclared anatomical localization: Harvard–Oxford cortical labels for
    # Frontal Medial and Subcallosal Cortex, restricted to the anterior,
    # ventral midline (y > 0, z <= 20 mm, |x| <= 20 mm). Descriptive only.
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    atlas_img = image.resample_to_img(atlas.maps, ref, interpolation="nearest")
    atlas_data = atlas_img.get_fdata().astype(int)
    labels = list(atlas.labels)
    medial_ids = [labels.index(x) for x in ("Frontal Medial Cortex", "Subcallosal Cortex")]
    coords = nib.affines.apply_affine(ref.affine, np.column_stack(np.where(mask)))
    vm_mask = np.isin(atlas_data[mask], medial_ids) & (np.abs(coords[:, 0]) <= 20) & (coords[:, 1] > 0) & (coords[:, 2] <= 20)
    vm_y = Y[:, vm_mask]
    vm_mean = float(vm_y.mean())
    vm_sd = float(vm_y.std(ddof=1))
    vm_se = vm_sd / np.sqrt(n)
    vm_ci = stats.t.interval(0.95, n - 1, loc=vm_mean, scale=vm_se)
    vm_t = vm_mean / vm_se
    vm_p = float(stats.t.sf(vm_t, n - 1))
    vm_volume = int(vm_mask.sum())
    fwe_hits = p_fwe <= 0.05
    vm_fwe_hits = int(np.sum(fwe_hits & vm_mask))

    # Describe suprathreshold clusters under corrected voxelwise inference.
    from scipy.ndimage import label
    hit_vol = np.zeros(ref.shape, dtype=bool)
    hit_vol[mask] = fwe_hits
    labs, nlab = label(hit_vol, structure=np.ones((3, 3, 3), dtype=int))
    voxvol = abs(np.linalg.det(ref.affine[:3, :3]))
    cluster_rows = []
    for lab_id in range(1, nlab + 1):
        idx = np.where(labs[mask] == lab_id)[0]
        if not len(idx):
            continue
        peak_i = idx[np.argmax(t_obs[idx])]
        ijk = np.column_stack(np.where(mask))[peak_i]
        xyz = nib.affines.apply_affine(ref.affine, ijk)
        cluster_rows.append({"cluster": lab_id, "voxels": len(idx), "volume_mm3": len(idx) * voxvol,
                             "peak_t": float(t_obs[peak_i]), "peak_p_fwe": float(p_fwe[peak_i]),
                             "peak_x": float(xyz[0]), "peak_y": float(xyz[1]), "peak_z": float(xyz[2]),
                             "peak_in_vmPFC_mask": bool(vm_mask[peak_i])})
    pd.DataFrame(cluster_rows, columns=["cluster", "voxels", "volume_mm3", "peak_t", "peak_p_fwe", "peak_x", "peak_y", "peak_z", "peak_in_vmPFC_mask"]).to_csv(OUT / "significant_clusters.csv", index=False)

    qc = {
        "n_maps": len(files), "n_metadata": len(participants), "n_excluded": 0,
        "geometry": {"shape": list(ref.shape), "zooms_mm": [float(x) for x in ref.header.get_zooms()[:3]], "affine": ref.affine.tolist()},
        "finite_all_voxels": bool(finite.all()), "analysis_mask_coverage_threshold": 0.90,
        "analysis_voxels": int(p), "analysis_mask_coverage_min": float(coverage[mask].min()),
        "analysis_mask_coverage_median": float(np.median(coverage[mask])),
        "mean_within_subject_nonzero_fraction": float(np.mean(np.mean(arrays != 0, axis=(1,2,3)))),
        "maps_and_metadata_match": True,
        "age_mean_sd": [float(participants.age.mean()), float(participants.age.std(ddof=1))],
        "gender_counts": participants.gender.value_counts().to_dict(),
        "effect_outlier_counts_abs_gt_5": int(np.sum(np.abs(Y) > 5)),
    }
    (OUT / "quality_checks.json").write_text(json.dumps(qc, indent=2))
    summary = {
        "n": n, "n_voxels": p, "permutations": N_PERM, "seed": SEED,
        "test": "one-sided positive one-sample sign-flip max-t; whole-brain voxelwise FWE",
        "max_t_95_percentile": float(crit), "largest_observed_t": float(np.max(t_obs)),
        "smallest_uncorrected_one_sided_p": float(np.min(p_unc)),
        "smallest_parametric_two_sided_p": float(np.min(p_two)),
        "smallest_permutation_fwe_p": float(np.min(p_fwe)),
        "significant_voxels_fwe_0.05": int(fwe_hits.sum()),
        "significant_clusters": int(nlab),
        "vmPFC_mask_definition": "Harvard-Oxford Frontal Medial + Subcallosal Cortex; |x|<=20, y>0, z<=20 mm MNI",
        "vmPFC_voxels": vm_volume, "vmPFC_mean_effect": vm_mean, "vmPFC_sd": vm_sd,
        "vmPFC_mean_ci95": [float(vm_ci[0]), float(vm_ci[1])], "vmPFC_t": float(vm_t),
        "vmPFC_descriptive_one_sided_p_uncorrected": vm_p,
        "vmPFC_voxels_whole_brain_fwe_significant": vm_fwe_hits,
    }
    (OUT / "analysis_summary.json").write_text(json.dumps(summary, indent=2))

    # Figures: group mean effect; whole-brain corrected statistical map.
    template = datasets.load_mni152_template()
    display = plotting.plot_stat_map(mean_img, bg_img=template, display_mode="ortho", cut_coords=(0, 0, 0),
                                    title="Mean gain-effect estimate (N=54)",
                                    threshold=0, cmap="cold_hot", colorbar=True,
                                    vmin=-0.45, vmax=0.45, draw_cross=True)
    display.savefig(FIG / "mean_effect.png", dpi=160)
    display.close()
    logp = np.zeros(ref.shape, dtype=np.float32)
    logp[mask] = -np.log10(np.maximum(p_fwe, 1e-6))
    corrected_img = nib.Nifti1Image(logp, ref.affine, ref.header)
    display = plotting.plot_stat_map(corrected_img, bg_img=template, display_mode="ortho",
                                    cut_coords=(26, -98, -8),
                                    title="Whole-brain sign-flip max-T corrected p-values",
                                    threshold=-np.log10(0.05), cmap="inferno", colorbar=True,
                                    vmin=-np.log10(0.05), vmax=-np.log10(max(1/(N_PERM+1),1e-4)))
    roi_data = np.zeros(ref.shape, dtype=np.uint8)
    roi_data[mask] = vm_mask
    display.add_contours(nib.Nifti1Image(roi_data, ref.affine, ref.header),
                         levels=[0.5], colors="cyan", linewidths=0.8)
    display.savefig(FIG / "whole_brain_fwe.png", dpi=160)
    display.close()

    # vmPFC ROI distribution, explicitly descriptive rather than an inferential gate.
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.hist(vm_y.mean(axis=1), bins=12, color="#4477AA", edgecolor="white")
    ax.axvline(vm_mean, color="#AA3377", lw=2, label=f"mean = {vm_mean:.3f}")
    ax.axvline(0, color="black", lw=1, ls="--")
    ax.set(xlabel="Participant mean vmPFC gain-effect estimate", ylabel="Participants",
           title="Descriptive vmPFC effect distribution")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "vmPFC_distribution.png", dpi=160)
    plt.close(fig)

    print(json.dumps(summary, indent=2))
    print("QC:", json.dumps(qc))


if __name__ == "__main__":
    main()
