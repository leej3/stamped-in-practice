#!/usr/bin/env python3
"""Group analysis of NARPS AO86 participant gain-effect maps."""
from __future__ import annotations

import json
import os
import hashlib
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import matplotlib.pyplot as plt
import nibabel as nib
import nilearn
import numpy as np
import pandas as pd
from scipy.stats import t as t_dist
from scipy import ndimage
from nilearn import plotting

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
N_PERM = 5000
SEED = 20261016
ALPHA = 0.05


def save_map(data: np.ndarray, reference: nib.spatialimages.SpatialImage, name: str) -> None:
    img = nib.Nifti1Image(data.astype(np.float32), reference.affine, reference.header)
    nib.save(img, OUT / name)


def main() -> None:
    metadata = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    metadata = metadata.loc[metadata.group.eq("equalIndifference")].copy()
    files = sorted((INPUT / "data").glob("sub-*_hypo1_cope.nii.gz"))
    ids = [p.name.split("_")[0] for p in files]
    source_manifest = json.loads((INPUT / "sources.json").read_text())
    manifest_files = source_manifest["files"]
    assert len(files) == 54
    assert set(ids) == set(metadata.participant_id)
    for path in files:
        manifest = manifest_files[str(path.relative_to(INPUT))]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == manifest["sha256"], f"Checksum mismatch: {path.name}"
    metadata = metadata.set_index("participant_id").loc[ids].reset_index()

    imgs = [nib.load(str(p)) for p in files]
    ref = imgs[0]
    for img in imgs[1:]:
        assert img.shape == ref.shape and np.allclose(img.affine, ref.affine)
    data = np.stack([np.asarray(img.dataobj, dtype=np.float32) for img in imgs])
    assert np.isfinite(data).all()

    # Include voxels with nonzero estimates in at least 90% of participants.
    # This is a reproducible common coverage mask derived from map support.
    support = np.mean(data != 0, axis=0)
    mask = support >= 0.90
    X = data[:, mask].astype(np.float64)
    n, v = X.shape
    assert n == 54

    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = t_dist.sf(t_obs, n - 1)

    # One-sided participant-level sign-flip test. The maximum t across the
    # full analysis mask controls family-wise error over all tested voxels.
    rng = np.random.default_rng(SEED)
    sumsq = np.sum(X * X, axis=0)
    maxima = np.empty(N_PERM, dtype=np.float32)
    Xt = X.T
    for i in range(N_PERM):
        signs = rng.choice(np.array([-1.0, 1.0]), size=n)
        sums = Xt @ signs
        perm_sd2 = np.maximum((sumsq - (sums * sums) / n) / (n - 1), 0)
        denom = np.sqrt(perm_sd2 / n)
        t_perm = np.divide(sums / n, denom, out=np.zeros_like(sums), where=denom > 0)
        maxima[i] = np.max(t_perm)
    sorted_maxima = np.sort(maxima)
    n_at_least_as_large = N_PERM - np.searchsorted(sorted_maxima, t_obs, side="left")
    p_fwe = (1 + n_at_least_as_large) / (N_PERM + 1)
    sig = p_fwe <= ALPHA

    def unmask(vals: np.ndarray, fill: float = 0) -> np.ndarray:
        out = np.full(ref.shape, fill, dtype=np.float32)
        out[mask] = vals.astype(np.float32)
        return out

    save_map(unmask(mean), ref, "mean_effect.nii.gz")
    save_map(unmask(t_obs), ref, "t_statistic.nii.gz")
    save_map(unmask(p_fwe), ref, "p_fwe_maxT.nii.gz")
    save_map(unmask(np.where(sig, t_obs, 0)), ref, "t_fwe05.nii.gz")
    save_map(mask.astype(np.float32), ref, "analysis_mask.nii.gz")

    # Approximate vmPFC location is used for descriptive labeling only.
    # The whole-brain corrected test remains the sole confirmatory inference.
    ijk = np.array(np.where(mask)).T
    xyz = nib.affines.apply_affine(ref.affine, ijk)
    vm_box = (
        (xyz[:, 0] >= -20) & (xyz[:, 0] <= 20) &
        (xyz[:, 1] >= 20) & (xyz[:, 1] <= 60) &
        (xyz[:, 2] >= -20) & (xyz[:, 2] <= 10)
    )
    vm_values = X[:, vm_box]
    vm_sub_mean = vm_values.mean(axis=1)
    vm_t = t_obs[vm_box]
    vm_p_fwe = p_fwe[vm_box]
    vm_summary = {
        "operational_region": "MNI x[-20,20], y[20,60], z[-20,10] mm; descriptive approximation only",
        "voxels": int(vm_box.sum()),
        "mean_effect": float(vm_values.mean()),
        "sd_across_participants": float(vm_sub_mean.std(ddof=1)),
        "descriptive_mean_95pct_t_ci": [
            float(vm_sub_mean.mean() - t_dist.ppf(.975, n - 1) * vm_sub_mean.std(ddof=1) / np.sqrt(n)),
            float(vm_sub_mean.mean() + t_dist.ppf(.975, n - 1) * vm_sub_mean.std(ddof=1) / np.sqrt(n)),
        ],
        "whole_brain_fwe_significant_voxels_in_box": int(np.sum(sig[vm_box])),
        "largest_t_in_box": float(vm_t.max()),
        "fwe_p_at_largest_t_in_box": float(vm_p_fwe[np.argmax(vm_t)]),
    }
    # Most positive voxel, for unthresholded map description only.
    peak_i = int(np.argmax(t_obs))
    peak_vox = ijk[peak_i]
    peak_xyz = nib.affines.apply_affine(ref.affine, peak_vox)
    sig_volume = np.zeros(ref.shape, dtype=bool)
    sig_volume[mask] = sig
    mask_index_volume = np.full(ref.shape, -1, dtype=np.int32)
    mask_index_volume[mask] = np.arange(v, dtype=np.int32)
    labels, n_clusters = ndimage.label(sig_volume, structure=np.ones((3, 3, 3), dtype=bool))
    clusters = []
    for label in range(1, n_clusters + 1):
        cluster_ijk = np.array(np.where(labels == label)).T
        cluster_mask_indices = mask_index_volume[tuple(cluster_ijk.T)]
        cluster_xyz = nib.affines.apply_affine(ref.affine, cluster_ijk)
        cpeak = int(cluster_mask_indices[np.argmax(t_obs[cluster_mask_indices])])
        cpeak_ijk = ijk[cpeak]
        cpeak_xyz = nib.affines.apply_affine(ref.affine, cpeak_ijk)
        clusters.append({"voxels_26_connected": int(len(cluster_ijk)),
                         "mni_extent_mm": [[float(np.min(cluster_xyz[:, j])), float(np.max(cluster_xyz[:, j]))] for j in range(3)],
                         "peak_t": float(t_obs[cpeak]),
                         "peak_mni_xyz_mm": [float(x) for x in cpeak_xyz]})
    report = {
        "n_participants": n,
        "excluded": [],
        "source_map_checksums_verified": len(files),
        "analysis_mask_voxels": int(v),
        "mask_rule": "nonzero coverage in >=90% of participants",
        "permutations": N_PERM,
        "random_seed": SEED,
        "inference": "one-sided positive one-sample t; participant-level sign flips; voxelwise max-statistic FWE",
        "familywise_alpha": ALPHA,
        "significant_voxels": int(sig.sum()),
        "significant_clusters_26_connected": clusters,
        "peak_unthresholded": {
            "t": float(t_obs[peak_i]),
            "p_uncorrected": float(p_unc[peak_i]),
            "p_fwe": float(p_fwe[peak_i]),
            "mni_xyz_mm": [float(x) for x in peak_xyz],
        },
        "vmPFC_descriptive": vm_summary,
        "demographics": {
            "age_mean": float(metadata.age.mean()),
            "age_sd": float(metadata.age.std(ddof=1)),
            "gender_counts": metadata.gender.value_counts().to_dict(),
        },
        "software": {
            "python": os.sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "nibabel": nib.__version__,
            "nilearn": nilearn.__version__,
        },
    }
    (OUT / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    pd.DataFrame({
        "voxel_index": np.arange(v), "mean_effect": mean, "t": t_obs,
        "p_uncorrected_one_sided": p_unc, "p_fwe_maxT": p_fwe,
        "mni_x": xyz[:, 0], "mni_y": xyz[:, 1], "mni_z": xyz[:, 2],
    }).to_csv(OUT / "voxel_results.csv", index=False)
    metadata.to_csv(OUT / "included_participants.tsv", sep="\t", index=False)

    # Visualization emphasizes an unthresholded whole-brain map and makes
    # clear that no voxel survived the prespecified whole-brain correction.
    fig = plt.figure(figsize=(11, 4.7))
    ax1 = fig.add_subplot(1, 2, 1)
    display = plotting.plot_stat_map(
        nib.load(str(OUT / "t_fwe05.nii.gz")), display_mode="ortho",
        cut_coords=tuple(float(x) for x in peak_xyz), threshold=0,
        cmap="cold_hot", colorbar=True, title="Whole-brain FWE-corrected map\n(positive t, max-statistic p ≤ .05)",
        axes=ax1, annotate=True, black_bg=False,
    )
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.hist(vm_sub_mean, bins=12, color="#3b6f8f", edgecolor="white")
    ax2.axvline(0, color="black", linewidth=1)
    ax2.axvline(vm_sub_mean.mean(), color="#b23a48", linewidth=2,
                label=f"Mean = {vm_sub_mean.mean():.4f}")
    ax2.set_xlabel("Participant mean effect estimate\n(vmPFC coordinate box)")
    ax2.set_ylabel("Participants")
    ax2.set_title("Descriptive vmPFC summary\n(no ROI significance test)")
    ax2.legend(frameon=False)
    fig.suptitle("NARPS equal-indifference group: gain effect", fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / "gain_group_results.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
