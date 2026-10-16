#!/usr/bin/env python3
"""Group inference for the supplied NARPS equal-indifference gain effects."""
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from nilearn import datasets, image, plotting

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
SEED = 20261016
N_PERM = 9999
ALPHA = 0.05
ROI_CENTER = (0.0, 40.0, -8.0)
ROI_RADIUS_MM = 10.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def one_sample_t(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = x.shape[1]
    s = x.sum(axis=1)
    ss = np.square(x).sum(axis=1)
    den = n * ss - s * s
    t = np.divide(s * np.sqrt(n - 1), np.sqrt(den), out=np.zeros_like(s), where=den > 0)
    mean = s / n
    sd = np.sqrt(np.maximum(den / (n * (n - 1)), 0.0))
    return t, mean, sd


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    sources = json.loads((INPUT / "sources.json").read_text())
    meta = pd.read_csv(INPUT / "participants.tsv", sep="\t", dtype={"participant_id": str})
    if meta.participant_id.duplicated().any():
        raise ValueError("Duplicate participant IDs in metadata")
    declared = sources["files"]
    map_ids = {v["participant_id"] for k, v in declared.items() if k.endswith("_cope.nii.gz")}
    meta_ids = set(meta.participant_id)
    if map_ids != meta_ids or len(map_ids) != 54:
        raise ValueError(f"Map/metadata mismatch: {len(map_ids)} maps, {len(meta_ids)} metadata IDs")
    if not (meta.group == "equalIndifference").all():
        raise ValueError("Unexpected group in participant table")

    imgs = []
    records = []
    for rel, record in declared.items():
        if not rel.endswith("_cope.nii.gz"):
            continue
        path = INPUT / rel
        got = sha256(path)
        if got != record["sha256"]:
            raise ValueError(f"SHA256 mismatch: {rel}")
        img = nib.load(path)
        if img.ndim != 3:
            raise ValueError(f"Not a 3D image: {rel}")
        data = img.get_fdata(dtype=np.float32)
        if not np.isfinite(data).all():
            raise ValueError(f"Nonfinite data: {rel}")
        imgs.append((record["participant_id"], img, data))
        records.append({"participant_id": record["participant_id"], "path": rel,
                        "bytes": path.stat().st_size, "sha256": got,
                        "shape": list(img.shape), "nonzero_voxels": int(np.count_nonzero(data))})
    imgs.sort(key=lambda z: z[0])
    ref = imgs[0][1]
    for pid, img, data in imgs[1:]:
        if img.shape != ref.shape or not np.allclose(img.affine, ref.affine, atol=1e-5):
            raise ValueError(f"Grid mismatch: {pid}")
    stack = np.stack([x[2] for x in imgs], axis=-1)
    coverage = np.count_nonzero(stack, axis=-1)
    # The common nonzero coverage mask gives every voxel the same N and avoids treating
    # unmodeled/out-of-brain zero fill as a measured zero effect.
    mask = coverage == len(imgs)
    if mask.sum() < 10000:
        raise ValueError(f"Unexpectedly small common coverage mask: {mask.sum()}")
    arr = stack[mask].astype(np.float64)
    n = arr.shape[1]
    t_obs, mean, sd = one_sample_t(arr)

    # Participant-level sign flips; max positive t controls whole-brain one-sided FWE.
    rng = np.random.default_rng(SEED)
    max_t = np.empty(N_PERM, dtype=np.float32)
    nvox = arr.shape[0]
    batch = 128
    sqrt_nm1 = np.sqrt(n - 1)
    for start in range(0, N_PERM, batch):
        stop = min(start + batch, N_PERM)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(n, stop - start))
        sums = arr @ signs
        den = np.maximum(n * np.square(arr).sum(axis=1, keepdims=True) - np.square(sums), 0.0)
        perm_t = sums * sqrt_nm1 / np.sqrt(den, where=den > 0, out=np.full_like(den, np.inf))
        max_t[start:stop] = np.max(perm_t, axis=0)
    sorted_max_t = np.sort(max_t)
    p_fwe = (1 + N_PERM - np.searchsorted(sorted_max_t, t_obs, side="left")) / (N_PERM + 1)
    threshold = float(np.quantile(max_t, 1 - ALPHA, method="higher"))
    significant = t_obs > threshold

    def full_map(values: np.ndarray) -> np.ndarray:
        out = np.zeros(ref.shape, dtype=np.float32)
        out[mask] = values.astype(np.float32)
        return out

    mean_img = nib.Nifti1Image(full_map(mean), ref.affine, ref.header)
    t_img = nib.Nifti1Image(full_map(t_obs), ref.affine, ref.header)
    p_values = np.full(ref.shape, np.nan, dtype=np.float32)
    p_values[mask] = p_fwe.astype(np.float32)
    p_img = nib.Nifti1Image(p_values, ref.affine, ref.header)
    sig_img = nib.Nifti1Image(full_map(np.where(significant, t_obs, 0)), ref.affine, ref.header)
    nib.save(mean_img, RESULTS / "group_mean_effect.nii.gz")
    nib.save(t_img, RESULTS / "group_t_unthresholded.nii.gz")
    nib.save(p_img, RESULTS / "group_p_fwe.nii.gz")
    nib.save(sig_img, RESULTS / "group_t_fwe05.nii.gz")

    # Independent anatomical coordinate ROI, used only to localize/descriptively summarize.
    ijk = np.indices(ref.shape).reshape(3, -1).T
    xyz = nib.affines.apply_affine(ref.affine, ijk)
    sphere = np.linalg.norm(xyz - np.asarray(ROI_CENTER), axis=1) <= ROI_RADIUS_MM
    sphere = sphere.reshape(ref.shape) & mask
    if sphere.sum() == 0:
        raise ValueError("ROI does not overlap analysis mask")
    per_person_roi = stack[sphere].mean(axis=0).astype(float)
    roi_mean = float(per_person_roi.mean())
    roi_sd = float(per_person_roi.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_ci = stats.t.interval(0.95, n - 1, loc=roi_mean, scale=roi_se)
    roi_t, roi_p_two = stats.ttest_1samp(per_person_roi, 0.0)
    roi_p_one = float(stats.t.sf(roi_t, n - 1))
    overlap = int(np.count_nonzero(significant & sphere[mask]))
    max_idx = int(np.argmax(t_obs))

    roi_df = pd.DataFrame({"participant_id": [p[0] for p in imgs], "mean_effect_in_vmPFC_sphere": per_person_roi})
    roi_df.to_csv(RESULTS / "vmPFC_participant_summary.tsv", sep="\t", index=False)
    pd.DataFrame(records).to_csv(RESULTS / "input_qc.tsv", sep="\t", index=False)
    pd.DataFrame({"permutation": np.arange(1, N_PERM + 1), "max_positive_t": max_t}).to_csv(
        RESULTS / "permutation_max_t.tsv", sep="\t", index=False)

    summary = {
        "n_participants": n, "n_excluded": 0, "excluded": [],
        "shape": list(ref.shape), "affine": ref.affine.tolist(),
        "common_nonzero_mask_voxels": int(mask.sum()), "common_mask_fraction_of_grid": float(mask.mean()),
        "roi": {"definition": "10-mm radius sphere centered at MNI [0, 40, -8] mm; descriptive localization only",
                "voxels": int(sphere.sum()), "mean_effect": roi_mean, "sd": roi_sd, "se": float(roi_se),
                "ci95_t": [float(roi_ci[0]), float(roi_ci[1])], "t": float(roi_t),
                "p_one_sided_uncorrected": roi_p_one, "p_two_sided_uncorrected": float(roi_p_two)},
        "primary": {"test": "one-sample t statistic with participant-level sign-flip max-t FWE",
                    "direction": "positive", "alpha": ALPHA, "permutations": N_PERM, "seed": SEED,
                    "fwe_t_threshold": threshold, "max_observed_t": float(t_obs[max_idx]),
                    "max_t_mni_mm": nib.affines.apply_affine(ref.affine, np.argwhere(mask)[max_idx]).tolist(),
                    "max_voxel_p_fwe": float(p_fwe[max_idx]), "significant_voxels": int(significant.sum()),
                    "significant_voxels_in_vmPFC_sphere": overlap},
        "assumptions": ["Independent participants", "Null sign symmetry for sign-flip inference",
                        "Equal weighting because participant variance maps are unavailable"],
        "software": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                     "nibabel": nib.__version__},
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Figure 1: participant-level ROI values with cohort mean and t interval.
    fig, ax = plt.subplots(figsize=(7.0, 4.4), constrained_layout=True)
    xj = np.random.default_rng(SEED).normal(0, 0.035, size=n)
    ax.scatter(xj, per_person_roi, s=27, alpha=.72, color="#315a7d", edgecolor="white", linewidth=.35)
    ax.errorbar(0.17, roi_mean, yerr=[[roi_mean - roi_ci[0]], [roi_ci[1] - roi_mean]], fmt="D",
                color="#b23a48", capsize=5, markersize=7, label="Mean and 95% t interval")
    ax.axhline(0, color="black", linewidth=.8, linestyle="--")
    ax.set(xlim=(-.12, .34), xticks=[0], xticklabels=["vmPFC sphere"], ylabel="Participant gain effect estimate",
           title="Gain effect estimates in the a priori vmPFC coordinate region")
    ax.legend(frameon=False, loc="best")
    fig.savefig(FIGURES / "vmPFC_participant_effects.png", dpi=180)
    plt.close(fig)

    # Figure 2: unthresholded group t map for context, with the sphere coordinate marked.
    disp = plotting.plot_stat_map(t_img, display_mode="ortho", cut_coords=ROI_CENTER,
                                  threshold=2.0, colorbar=True, cmap="cold_hot", vmin=-5, vmax=5,
                                  title="Unthresholded group t map (display threshold |t| > 2)",
                                  black_bg=False, annotate=True)
    disp.add_markers([ROI_CENTER], marker_color="lime", marker_size=55)
    disp.savefig(FIGURES / "group_t_map.png", dpi=160)
    plotting.plot_stat_map(sig_img, display_mode="z", cut_coords=[-8, -4, 0], threshold=0,
                           colorbar=True, cmap="Reds", title="Positive whole-brain FWE-corrected t map",
                           black_bg=False, annotate=True).savefig(FIGURES / "group_t_fwe05.png", dpi=160)
    (RESULTS / "run_record.txt").write_text(
        "Command: /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/run_analysis.py\n"
        f"Seed: {SEED}; permutations: {N_PERM}; batch: {batch}; alpha: {ALPHA}\n"
        f"Python: {platform.python_version()}; NumPy: {np.__version__}; SciPy: {stats.__version__ if hasattr(stats, '__version__') else 'see environment'}; Nilearn: {__import__('nilearn').__version__}; NiBabel: {nib.__version__}\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
