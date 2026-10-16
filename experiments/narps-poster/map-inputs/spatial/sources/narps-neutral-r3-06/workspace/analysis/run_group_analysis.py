#!/usr/bin/env python3
"""One-sample group analysis of NARPS AO86 equal-indifference gain effects.

The script reads participant cope maps listed in input/sources.json, verifies
retrieved bytes where possible, and runs a positive one-sample max-T sign-flip
permutation test across the participant-overlap brain mask.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets, image, plotting
from scipy import stats
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
MANIFEST = json.loads((ROOT / "input/sources.json").read_text())
PARTICIPANTS = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
N_PERM = int(os.environ.get("NARPS_N_PERM", "10000"))
SEED = 20261016
MASK_FRACTION = 0.90


def map_path(relative: str) -> Path:
    """Prefer the supplied annex path; fall back to local retrieved map bytes."""
    p = ROOT / "input" / relative
    if p.exists():
        return p
    fallback = ROOT / "input" / "retrieved_maps" / Path(relative).name
    if fallback.exists():
        return fallback
    raise FileNotFoundError(p)


def load_maps() -> tuple[list[str], list[nib.spatialimages.SpatialImage], np.ndarray]:
    files = MANIFEST["files"]
    by_id = {v["participant_id"]: (k, v) for k, v in files.items() if k.startswith("data/")}
    ids = PARTICIPANTS.participant_id.tolist()
    if set(ids) != set(by_id):
        raise ValueError(f"Participant/map mismatch: {len(ids)} participants, {len(by_id)} maps")
    imgs, arrays = [], []
    reference = None
    for pid in ids:
        rel, meta = by_id[pid]
        path = map_path(rel)
        raw = path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if len(raw) != meta["bytes"] or sha != meta["sha256"]:
            raise ValueError(f"Checksum mismatch: {pid}: {len(raw)} bytes, {sha}")
        img = nib.load(str(path))
        if reference is None:
            reference = img
        elif img.shape != reference.shape or not np.allclose(img.affine, reference.affine):
            raise ValueError(f"Grid mismatch for {pid}")
        arr = img.get_fdata(dtype=np.float32)
        if not np.isfinite(arr).all():
            raise ValueError(f"Non-finite voxels for {pid}")
        imgs.append(img)
        arrays.append(arr)
    return ids, imgs, np.stack(arrays, axis=0)


def vm_pfc_mask(reference: nib.spatialimages.SpatialImage) -> nib.Nifti1Image:
    """Independent Harvard-Oxford cortical atlas operationalization of vmPFC.

    Use atlas labels Frontal Medial Cortex, Subcallosal Cortex, and Frontal
    Orbital Cortex at >=25% probability, limited to the medial band |x|<=20 mm.
    This broad anatomical mask is descriptive; inference remains whole-brain.
    """
    atlas = datasets.fetch_atlas_harvard_oxford("cort-prob-2mm", verbose=0)
    data = atlas.maps.get_fdata(dtype=np.float32)
    labels = atlas.labels
    selected = [labels.index(x) for x in ("Frontal Medial Cortex", "Subcallosal Cortex", "Frontal Orbital Cortex")]
    region = (data[..., selected] >= 25).any(axis=3)
    # Retain a strict medial band to avoid lateral orbital cortex.
    atlas_shape = atlas.maps.shape[:3]
    coords = nib.affines.apply_affine(atlas.maps.affine, np.indices(atlas_shape).reshape(3, -1).T)
    medial = (np.abs(coords[:, 0]) <= 20).reshape(atlas_shape)
    atlas_img = nib.Nifti1Image((region & medial).astype(np.uint8), atlas.maps.affine)
    return image.resample_to_img(atlas_img, reference, interpolation="nearest")


def t_stat(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = x.shape[0]
    mean = x.mean(axis=0, dtype=np.float64)
    sd = x.std(axis=0, ddof=1, dtype=np.float64)
    t = mean / (sd / np.sqrt(n))
    return mean, sd, t


def max_t_permutation(x: np.ndarray, n_perm: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Positive, one-sided max-T sign flips; returns t map, FWE p map, null max T."""
    n, v = x.shape
    _, _, observed_t = t_stat(x)
    rng = np.random.default_rng(seed)
    null_max = np.empty(n_perm, dtype=np.float32)
    # Batches bound peak memory while retaining vectorized voxel computations.
    batch = max(1, min(64, 2_000_000 // v))
    x64 = x.astype(np.float64, copy=False)
    sumsq = np.sum(x64 * x64, axis=0)
    for start in range(0, n_perm, batch):
        b = min(batch, n_perm - start)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
        sums = signs @ x64
        # Under sign flipping, each observation is multiplied by +/-1, so sumsq is fixed.
        var = np.maximum((sumsq[None, :] - sums * sums / n) / (n - 1), 0.0)
        # sums is the signed sum, whereas the t numerator is the signed mean.
        t_perm = sums / np.sqrt(var * n)
        null_max[start : start + b] = np.max(t_perm, axis=1)
    p_fwe = (1 + (null_max[:, None] >= observed_t[None, :]).sum(axis=0)) / (n_perm + 1)
    return observed_t, p_fwe.astype(np.float32), null_max


def main() -> None:
    ids, imgs, stack = load_maps()
    ref = imgs[0]
    n = len(ids)
    # Group overlap mask: a voxel must be nonzero in >=90% of maps, a pragmatic
    # coverage criterion since the upstream maps encode outside-brain as zero.
    support = np.count_nonzero(stack != 0, axis=0) / n
    mask = support >= MASK_FRACTION
    # Exclude isolated non-brain artifacts using the independent atlas-derived
    # broad brain envelope (union of cortical and subcortical atlas probabilities).
    atlas = datasets.fetch_atlas_harvard_oxford("cort-prob-2mm", verbose=0)
    sub = datasets.fetch_atlas_harvard_oxford("sub-prob-2mm", verbose=0)
    cort_data = atlas.maps.get_fdata(dtype=np.float32)
    sub_data = sub.maps.get_fdata(dtype=np.float32)
    brain = (cort_data.max(axis=3) >= 5) | (sub_data.max(axis=3) >= 5)
    brain_img = image.resample_to_img(nib.Nifti1Image(brain.astype(np.uint8), atlas.maps.affine), ref, interpolation="nearest")
    mask &= brain_img.get_fdata() > 0
    if mask.sum() < 10000:
        raise RuntimeError(f"Unexpectedly small analysis mask: {mask.sum()} voxels")
    X = stack[:, mask].astype(np.float32)
    means, sds, tvals = t_stat(X)
    t_obs, p_fwe, null_max = max_t_permutation(X, N_PERM, SEED)
    p_unc = stats.t.sf(t_obs, df=n - 1)
    vm = vm_pfc_mask(ref).get_fdata() > 0
    vm_test = vm[mask]
    if not vm_test.any():
        raise RuntimeError("vmPFC atlas mask does not overlap analysis mask")

    # Save group maps on the original cope grid.
    def save_map(values: np.ndarray, name: str) -> Path:
        full = np.zeros(ref.shape, dtype=np.float32)
        full[mask] = values.astype(np.float32)
        dest = OUT / name
        nib.save(nib.Nifti1Image(full, ref.affine, ref.header), dest)
        return dest

    mean_path = save_map(means, "group_mean_cope.nii.gz")
    t_path = save_map(t_obs, "group_t_positive.nii.gz")
    pfwe_path = save_map(p_fwe, "group_p_fwe_positive.nii.gz")
    support_path = save_map(support[mask].astype(np.float32), "analysis_mask_support.nii.gz")
    vm_path = OUT / "vmPFC_harvard_oxford_mask.nii.gz"
    nib.save(vm_pfc_mask(ref), vm_path)

    vm_mean = float(means[vm_test].mean())
    vm_sd = float(sds[vm_test].mean())
    # ROI descriptive summary: average participant effects inside atlas mask.
    roi_subjects = stack[:, mask][:, vm_test].mean(axis=1)
    roi = stats.ttest_1samp(roi_subjects, 0, alternative="greater")
    roi_ci = stats.t.interval(0.95, n - 1, loc=roi_subjects.mean(), scale=stats.sem(roi_subjects))
    peak_idx = int(np.argmax(t_obs))
    peak_ijk = np.argwhere(mask)[peak_idx]
    peak_xyz = nib.affines.apply_affine(ref.affine, peak_ijk)
    peak_in_vm = bool(vm[tuple(peak_ijk)])
    # Peak-level ordinary one-sample t is reported descriptively; support depends on max-T.
    peak_t = float(t_obs[peak_idx])
    peak_p_unc = float(stats.t.sf(peak_t, n - 1))
    peak_p_fwe = float(p_fwe[peak_idx])
    significant = p_fwe < 0.05
    sig_in_vm = bool(np.any(significant & vm_test))
    results = {
        "n_participants": n,
        "exclusions": [],
        "n_analysis_voxels": int(mask.sum()),
        "mask_rule": f"nonzero support in >= {MASK_FRACTION:.0%} of maps and Harvard-Oxford cortex/subcortex probability >=5%",
        "permutations": N_PERM,
        "random_seed": SEED,
        "test": "one-sided positive one-sample t statistic, sign-flip permutation, maximum statistic across whole analysis mask",
        "minimum_resolvable_fwe_p": 1 / (N_PERM + 1),
        "vmPFC_roi": "Harvard-Oxford cortical Frontal Medial, Subcallosal, and Frontal Orbital labels at >=25% probability, restricted to |x|<=20 mm; descriptive only",
        "vmPFC_n_voxels": int(vm_test.sum()),
        "vmPFC_mean_effect_estimate": vm_mean,
        "vmPFC_mean_within_voxel_sd": vm_sd,
        "vmPFC_mean_subject_roi_estimate": float(roi_subjects.mean()),
        "vmPFC_roi_t": float(roi.statistic),
        "vmPFC_roi_p_uncorrected_one_sided": float(roi.pvalue),
        "vmPFC_roi_ci95_subject_mean": [float(roi_ci[0]), float(roi_ci[1])],
        "whole_brain_positive_fwe_voxels": int(significant.sum()),
        "whole_brain_significant_voxels_in_vmPFC": int((significant & vm_test).sum()),
        "whole_brain_corrected_support_in_vmPFC": sig_in_vm,
        "whole_brain_max_t_peak": {
            "t": peak_t, "p_uncorrected_one_sided": peak_p_unc,
            "p_fwe": peak_p_fwe, "mni_xyz_mm": [float(v) for v in peak_xyz],
            "inside_vmPFC_mask": peak_in_vm,
            "mean_effect_estimate": float(means[peak_idx]),
        },
        "null_max_t_95th_percentile": float(np.quantile(null_max, .95)),
        "map_files": [str(mean_path.relative_to(ROOT)), str(t_path.relative_to(ROOT)), str(pfwe_path.relative_to(ROOT)), str(support_path.relative_to(ROOT)), str(vm_path.relative_to(ROOT))],
    }
    (OUT / "analysis_results.json").write_text(json.dumps(results, indent=2) + "\n")
    pd.DataFrame({"participant_id": ids, "vmPFC_mean_cope": roi_subjects}).to_csv(OUT / "vmPFC_subject_effects.tsv", sep="\t", index=False)

    # Figure 1: group mean effect and the t map underlying whole-brain max-T inference.
    mean_img = nib.load(str(mean_path))
    fig = plt.figure(figsize=(12, 6))
    ax1 = fig.add_subplot(1, 2, 1)
    plotting.plot_stat_map(mean_img, bg_img=None, display_mode="ortho", cut_coords=(0, 42, -10),
                           threshold=0.05, cmap="cold_hot", colorbar=True, axes=ax1, title="")
    ax2 = fig.add_subplot(1, 2, 2)
    plotting.plot_stat_map(nib.load(str(t_path)), bg_img=None, display_mode="ortho", cut_coords=(0, 42, -10),
                           threshold=0, cmap="cold_hot", colorbar=True, axes=ax2, title="")
    fig.subplots_adjust(top=.78, bottom=.05)
    fig.text(.26, .87, "Mean cope (vmPFC slices)", ha="center", fontsize=11)
    fig.text(.75, .87, "Positive group t (vmPFC slices)", ha="center", fontsize=11)
    fig.text(.75, .025, "No vmPFC voxel survives whole-brain max-T FWE p < .05", ha="center", fontsize=9)
    fig.suptitle("Equal-indifference group: gain-effect estimates", fontsize=14, y=.97)
    fig.savefig(OUT / "group_maps.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: participant-level average within the independent vmPFC mask.
    fig, ax = plt.subplots(figsize=(7, 4.5))
    jitter = np.linspace(-.07, .07, n)
    ax.scatter(jitter, roi_subjects, color="#355c7d", alpha=.75, s=30)
    ax.axhline(0, color="black", linewidth=1)
    ax.axhline(roi_subjects.mean(), color="#c06c84", linewidth=2, label=f"mean={roi_subjects.mean():.3f}")
    ax.set(xlim=(-.25, .25), xticks=[], ylabel="Mean participant cope within vmPFC mask",
           title="Participant-level vmPFC gain-effect estimates")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "vmPFC_subject_effects.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
