#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference gain effect maps.

The primary test is a positive one-sample group effect with whole-brain
family-wise error control from sign-flip max-T permutation.
"""
from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

import nibabel as nib
import nilearn
import numpy as np
import pandas as pd
from scipy import stats, ndimage
from nilearn import datasets, image, plotting
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "input" / "data"
OUT = ROOT / "results"
FIG = ROOT / "output" / "figures"
ATLAS_DIR = ROOT / ".cache" / "nilearn"
N_PERM = 10_000
SEED = 20261016
MASK_FRACTION = 0.90
ALPHA = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def t_from_sum(sum_x: np.ndarray, sum_sq: np.ndarray, n: int) -> np.ndarray:
    den = np.maximum(n * sum_sq - sum_x * sum_x, 0.0)
    return sum_x * np.sqrt(n - 1) / np.sqrt(np.maximum(den, 1e-24))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    metadata = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
    files = [DATA / f"{pid}_hypo1_cope.nii.gz" for pid in metadata.participant_id]
    if len(files) != 54 or not all(p.exists() for p in files):
        raise RuntimeError("Expected exactly 54 available participant maps.")
    manifest = json.loads((ROOT / "input" / "sources.json").read_text())
    manifest_ids = {entry["participant_id"] for name, entry in manifest["files"].items()
                    if name.startswith("data/")}
    if set(metadata.participant_id) != manifest_ids:
        raise RuntimeError("Participant metadata and source manifest do not match.")
    for path in files:
        entry = manifest["files"][f"data/{path.name}"]
        if path.stat().st_size != entry["bytes"] or sha256(path) != entry["sha256"]:
            raise RuntimeError(f"Source checksum/size mismatch: {path.name}")

    imgs = [nib.load(str(p)) for p in files]
    ref = imgs[0]
    shape, affine = ref.shape, ref.affine
    if len(shape) != 3:
        raise RuntimeError(f"Expected 3D maps, got {shape}")
    arrays = []
    qc = []
    for pid, path, im in zip(metadata.participant_id, files, imgs):
        if im.shape != shape or not np.allclose(im.affine, affine, atol=1e-5):
            raise RuntimeError(f"Geometry mismatch in {path.name}")
        a = im.get_fdata(dtype=np.float32)
        finite = np.isfinite(a)
        if not finite.all():
            raise RuntimeError(f"Non-finite values in {path.name}")
        supported = finite & (a != 0)
        arrays.append(a)
        qc.append({
            "participant_id": pid,
            "n_finite": int(finite.sum()),
            "n_nonzero": int(supported.sum()),
            "coverage_fraction": float(supported.mean()),
            "mean_supported": float(np.mean(a[supported])),
            "sd_supported": float(np.std(a[supported], ddof=1)),
            "min_supported": float(np.min(a[supported])),
            "max_supported": float(np.max(a[supported])),
        })
    data = np.stack(arrays, axis=0)
    support = np.isfinite(data) & (data != 0)
    mask = support.sum(axis=0) >= int(np.ceil(MASK_FRACTION * len(files)))
    if not np.any(mask):
        raise RuntimeError("No voxels passed the coverage mask.")
    X = data[:, mask].astype(np.float64, copy=False)
    n, p = X.shape

    # One-sample t estimate and one-sided parametric p values, for description.
    sum_x = X.sum(axis=0)
    sum_sq = np.einsum("ij,ij->j", X, X)
    t_obs = t_from_sum(sum_x, sum_sq, n)
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    se = sd / np.sqrt(n)
    p_unc = stats.t.sf(t_obs, df=n - 1)

    # Sign-flip max-T controls FWER over every voxel in the coverage mask.
    rng = np.random.default_rng(SEED)
    max_null = np.empty(N_PERM, dtype=np.float32)
    batch = 64
    for start in range(0, N_PERM, batch):
        stop = min(start + batch, N_PERM)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(stop - start, n))
        perm_sum = signs @ X
        perm_t = t_from_sum(perm_sum, sum_sq[None, :], n)
        max_null[start:stop] = np.max(perm_t, axis=1)
    p_fwe = (1 + (max_null[:, None] >= t_obs[None, :]).sum(axis=0)) / (N_PERM + 1)
    significant = p_fwe <= ALPHA

    # Anatomical localization only: AAL3v2 medial orbitofrontal/rectus labels.
    atlas = datasets.fetch_atlas_aal(version="3v2", data_dir=ATLAS_DIR, verbose=0)
    aal = image.resample_to_img(atlas.maps, ref, interpolation="nearest")
    aal_data = aal.get_fdata().astype(int)
    labels = list(atlas.labels)
    label_to_id = {str(row.name): int(row.index) for row in atlas.lut.itertuples()}
    vm_labels = ["Frontal_Med_Orb_L", "Frontal_Med_Orb_R", "Rectus_L", "Rectus_R",
                 "OFCmed_L", "OFCmed_R"]
    vm_values = [label_to_id[k] for k in vm_labels]
    roi = np.isin(aal_data, vm_values) & mask
    roi_n = int(roi.sum())
    if roi_n < 1:
        raise RuntimeError("AAL3 vmPFC approximation did not overlap the group mask.")
    roi_X = data[:, roi]
    roi_person = roi_X.mean(axis=1)
    roi_mean = float(roi_person.mean())
    roi_sd = float(roi_person.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_t = float(roi_mean / roi_se)
    roi_p = float(stats.t.sf(roi_t, df=n - 1))
    roi_ci = [float(roi_mean - stats.t.ppf(0.975, n - 1) * roi_se),
              float(roi_mean + stats.t.ppf(0.975, n - 1) * roi_se)]

    # Components are descriptive only; inferential correction is voxelwise max-T.
    sig_full = np.zeros(shape, dtype=bool)
    sig_full[mask] = significant
    component_map, n_components = ndimage.label(sig_full, structure=np.ones((3, 3, 3)))
    clusters = []
    for component in range(1, n_components + 1):
        coords = np.column_stack(np.where(component_map == component))
        xyz = nib.affines.apply_affine(affine, coords.mean(axis=0))
        submask = component_map[mask] == component
        clusters.append({
            "cluster_id": component,
            "extent_voxels": int(len(coords)),
            "centroid_mni_x": float(xyz[0]), "centroid_mni_y": float(xyz[1]),
            "centroid_mni_z": float(xyz[2]),
            "peak_t": float(np.max(t_obs[submask])),
        })
    pd.DataFrame(clusters).to_csv(OUT / "significant_components.tsv", sep="\t", index=False)

    def full_image(values: np.ndarray, name: str) -> nib.Nifti1Image:
        arr = np.zeros(shape, dtype=np.float32)
        arr[mask] = values.astype(np.float32)
        out = nib.Nifti1Image(arr, affine, header=ref.header.copy())
        out.set_data_dtype(np.float32)
        nib.save(out, str(OUT / name))
        return out

    mean_img = full_image(mean, "group_mean_effect.nii.gz")
    t_img = full_image(t_obs, "group_tstat.nii.gz")
    pfwe_img = full_image(-np.log10(p_fwe), "neglog10_p_fwe.nii.gz")
    sig_img = full_image(significant.astype(np.float64), "significant_fwe_mask.nii.gz")
    nib.save(nib.Nifti1Image(mask.astype(np.uint8), affine, header=ref.header.copy()),
             str(OUT / "group_coverage_mask.nii.gz"))
    nib.save(nib.Nifti1Image(roi.astype(np.uint8), affine, header=ref.header.copy()),
             str(OUT / "aal3_vmPFC_localization_mask.nii.gz"))

    pd.DataFrame(qc).to_csv(OUT / "participant_map_qc.tsv", sep="\t", index=False)
    roi_df = pd.DataFrame({"participant_id": metadata.participant_id,
                           "vmPFC_mean_effect": roi_person})
    roi_df.to_csv(OUT / "participant_vmPFC_effects.tsv", sep="\t", index=False)

    max_t = float(np.max(t_obs))
    max_t_idx = int(np.argmax(t_obs))
    max_ijk = np.array(np.unravel_index(np.flatnonzero(mask)[max_t_idx], shape))
    max_xyz = nib.affines.apply_affine(affine, max_ijk).tolist()
    results = {
        "n_participants": n,
        "n_excluded": 0,
        "shape": list(shape),
        "voxel_size_mm": [float(abs(affine[i, i])) for i in range(3)],
        "mask_rule": f"Nonzero finite map support in at least {MASK_FRACTION:.0%} of participants",
        "n_search_voxels": p,
        "n_roi_voxels": roi_n,
        "vmPFC_localization_atlas": "AAL3v2; Frontal_Med_Orb, Rectus, OFCmed, bilateral",
        "primary_test": "One-sample positive group mean; sign-flip permutation max-T whole-brain FWER",
        "n_permutations": N_PERM,
        "random_seed": SEED,
        "alpha_fwe": ALPHA,
        "n_significant_voxels_fwe": int(significant.sum()),
        "max_t": max_t,
        "max_t_voxel_mni": [float(v) for v in max_xyz],
        "max_t_p_fwe": float((1 + np.sum(max_null >= max_t)) / (N_PERM + 1)),
        "max_t_p_uncorrected_one_sided": float(stats.t.sf(max_t, n - 1)),
        "max_null_95_percentile": float(np.quantile(max_null, .95)),
        "vmPFC_mean_effect": roi_mean,
        "vmPFC_mean_effect_ci95_t_interval": roi_ci,
        "vmPFC_roi_t": roi_t,
        "vmPFC_roi_p_uncorrected_one_sided": roi_p,
        "vmPFC_roi_mean_participant_sd": roi_sd,
        "vmPFC_roi_effect_mean": float(np.mean(roi_person)),
        "vmPFC_roi_effect_median": float(np.median(roi_person)),
        "metadata_gender_counts": metadata.gender.value_counts().to_dict(),
        "metadata_age_mean_sd": [float(metadata.age.mean()), float(metadata.age.std(ddof=1))],
        "map_qc_summary": {
            "coverage_min_voxels": int(min(q["n_nonzero"] for q in qc)),
            "coverage_median_voxels": float(np.median([q["n_nonzero"] for q in qc])),
            "coverage_max_voxels": int(max(q["n_nonzero"] for q in qc)),
            "coefficient_mean_min_max": [float(min(q["mean_supported"] for q in qc)),
                                         float(max(q["mean_supported"] for q in qc))],
            "coefficient_sd_min_max": [float(min(q["sd_supported"] for q in qc)),
                                       float(max(q["sd_supported"] for q in qc))],
        },
        "map_sha256": {p.name: sha256(p) for p in files},
        "atlas_version": "AAL3v2",
        "software": {"python": sys.version.split()[0], "numpy": np.__version__,
                     "nibabel": nib.__version__, "nilearn": nilearn.__version__},
        "checksums_verified_against_sources_json": True,
    }
    (OUT / "group_results.json").write_text(json.dumps(results, indent=2) + "\n")
    np.save(OUT / "max_t_null.npy", max_null)

    # Whole-brain means with voxelwise significant locations and the
    # independently defined anatomical region for orientation.
    fig = plt.figure(figsize=(13, 5.6))
    disp1 = plotting.plot_stat_map(mean_img, display_mode="z", cut_coords=[-12, -4, 4, 12],
        cmap="RdBu_r", threshold=None, colorbar=True, black_bg=False,
        title="Group mean gain-effect estimate (all participants)", figure=fig,
        axes=(0.04, 0.08, 0.44, 0.82), vmax=np.nanpercentile(np.abs(mean), 98))
    if significant.any():
        disp1.add_contours(sig_img, levels=[0.5], colors="yellow", linewidths=1.2)
    disp1.add_contours(nib.Nifti1Image(roi.astype(np.uint8), affine), levels=[0.5],
                       colors="black", linewidths=0.6)
    disp2 = plotting.plot_stat_map(t_img, display_mode="x", cut_coords=[-28, -26, -24],
        cmap="hot", threshold=float(np.quantile(max_null, 0.95)), colorbar=True, black_bg=False,
        title="t statistic above whole-brain max-T FWE cutoff", figure=fig,
        axes=(0.53, 0.08, 0.44, 0.82),
        vmax=float(np.max(t_obs)))
    if significant.any():
        disp2.add_contours(sig_img, levels=[0.5], colors="cyan", linewidths=1.2)
    disp2.add_contours(nib.Nifti1Image(roi.astype(np.uint8), affine), levels=[0.5],
                       colors="white", linewidths=0.6)
    fig.savefig(FIG / "group_gain_maps.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
    ax.hist(roi_person, bins=12, color="#4677a8", edgecolor="white")
    ax.axvline(0, color="black", linewidth=1, linestyle="--")
    ax.axvline(roi_mean, color="#b33c2e", linewidth=2,
               label=f"Mean = {roi_mean:.3g}; 95% CI [{roi_ci[0]:.3g}, {roi_ci[1]:.3g}]")
    ax.set(xlabel="Participant mean effect within AAL3 vmPFC approximation",
           ylabel="Participants", title="Participant effects in anatomical vmPFC approximation")
    ax.legend(frameon=False, fontsize=9)
    fig.savefig(FIG / "vmPFC_participant_effects.png", dpi=180)
    plt.close(fig)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
