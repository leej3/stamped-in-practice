#!/usr/bin/env python3
"""Group inference for NARPS equal-indifference gain effect maps."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets, image, plotting
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
RESULTS = OUT / "results"
FIGURES = OUT / "figures"
RESULTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)
N_PERM = 9999
SEED = 20261016
VM_CENTER = (4.0, 42.0, -8.0)  # MNI; independent mixed-gamble value literature
VM_RADIUS_MM = 10.0


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
    manifest = json.loads((ROOT / "input/sources.json").read_text())
    paths = [ROOT / "input" / p for p in manifest["files"] if p.endswith("_hypo1_cope.nii.gz")]
    paths = sorted(paths, key=lambda p: p.name)
    assert len(paths) == 54 == len(participants)
    by_id = {p.name.split("_")[0]: p for p in paths}
    assert set(by_id) == set(participants.participant_id)

    imgs, data, qc = [], [], []
    reference = None
    for row in participants.itertuples(index=False):
        p = by_id[row.participant_id]
        img = nib.load(p)
        if reference is None:
            reference = img
        same_grid = img.shape == reference.shape and np.allclose(img.affine, reference.affine, atol=1e-5)
        arr = np.asarray(img.dataobj, dtype=np.float32)
        finite = np.isfinite(arr).all()
        imgs.append(img)
        data.append(arr)
        qc.append({"participant_id": row.participant_id, "sha256_verified": digest(p) == manifest["files"][f"data/{p.name}"]["sha256"],
                   "same_grid": bool(same_grid), "all_finite": bool(finite), "nonzero_voxels": int(np.count_nonzero(arr)),
                   "min": float(np.nanmin(arr)), "max": float(np.nanmax(arr))})
    X = np.stack(data, axis=0)
    assert all(r["sha256_verified"] and r["same_grid"] and r["all_finite"] for r in qc)

    # Explicit template brain mask (not derived from the observed effect maps).
    tpl_mask = datasets.load_mni152_brain_mask(resolution=2)
    mask_img = image.resample_to_img(tpl_mask, reference, interpolation="nearest")
    mask = np.asarray(mask_img.dataobj) > 0
    n, *shape = X.shape
    Y = X[:, mask].astype(np.float64)
    assert Y.shape[0] == 54 and np.isfinite(Y).all()
    nvox = Y.shape[1]

    # Primary: one-sample, positive-direction group t statistic; sign-flip max-T
    # controls voxelwise familywise error over the entire template brain mask.
    mean = Y.mean(axis=0)
    sd = Y.std(axis=0, ddof=1)
    se = sd / np.sqrt(n)
    # Template mask can include zero-filled voxels outside the signal support;
    # all-zero/zero-variance locations carry no evidence and receive t=0.
    t_obs = np.divide(mean, se, out=np.zeros_like(mean), where=se > 0)
    rng = np.random.default_rng(SEED)
    max_t = np.empty(N_PERM, dtype=np.float32)
    denom_sq_const = np.square(Y).sum(axis=0)
    # Batched matrix products keep memory modest; two-sided signs are randomized
    # under the one-sample null. The maximum is taken only in the hypothesized
    # positive direction, matching the preregistered directional hypothesis.
    batch = 128
    for start in range(0, N_PERM, batch):
        stop = min(start + batch, N_PERM)
        signs = rng.choice(np.array([-1.0, 1.0], dtype=np.float64), size=(stop - start, n))
        sums = signs @ Y
        denom = np.sqrt(np.maximum(n * denom_sq_const[None, :] - sums * sums, 1e-16) / (n - 1))
        perm_t = sums / denom
        max_t[start:stop] = np.max(perm_t, axis=1).astype(np.float32)
    p_fwe = (1 + (max_t[:, None] >= t_obs[None, :]).sum(axis=0)) / (N_PERM + 1)

    # Descriptive vmPFC sphere defined independently of these maps from the
    # mixed-gamble valuation literature; no small-volume correction is used.
    ijk = np.indices(tuple(shape), dtype=np.float32).reshape(3, -1).T
    xyz = nib.affines.apply_affine(reference.affine, ijk)
    vm = (np.linalg.norm(xyz - np.asarray(VM_CENTER), axis=1) <= VM_RADIUS_MM).reshape(shape) & mask
    vm_vec = vm[mask]
    assert vm_vec.sum() > 0
    roi_values = X[:, vm].mean(axis=1)
    roi_t = stats.ttest_1samp(roi_values, 0, alternative="greater")
    roi_mean = float(roi_values.mean())
    roi_se = float(stats.sem(roi_values))
    roi_ci = stats.t.interval(0.95, df=n - 1, loc=roi_mean, scale=roi_se)

    # Save full maps on the supplied grid. FWE p values are 1 outside mask.
    def volume(vals: np.ndarray, outside: float = 0.0) -> nib.Nifti1Image:
        out = np.full(shape, outside, dtype=np.float32)
        out[mask] = vals.astype(np.float32)
        return nib.Nifti1Image(out, reference.affine, reference.header)

    for name, vals, outside in [("group_mean_effect", mean, 0), ("group_t_positive", t_obs, 0),
                                ("group_p_fwe_positive", p_fwe, 1)]:
        nib.save(volume(vals, outside), RESULTS / f"{name}.nii.gz")
    nib.save(nib.Nifti1Image(vm.astype(np.uint8), reference.affine, reference.header), RESULTS / "vmPFC_sphere_mask.nii.gz")
    pd.DataFrame(qc).to_csv(RESULTS / "image_qc.csv", index=False)
    pd.DataFrame({"participant_id": participants.participant_id, "vmPFC_sphere_mean": roi_values}).to_csv(RESULTS / "vmPFC_participant_effects.csv", index=False)

    summary = {
        "n_participants": n, "excluded": [], "mask_voxels": int(mask.sum()), "vmPFC_sphere_voxels": int(vm.sum()),
        "vmPFC_definition": {"center_mni_mm": VM_CENTER, "radius_mm": VM_RADIUS_MM,
                             "basis": "independent mixed-gamble vmPFC coordinate; Tom et al. 2007 / Neurosynth-based prior coordinates"},
        "roi_mean_effect": roi_mean, "roi_sd": float(np.std(roi_values, ddof=1)),
        "roi_ci95_t": [float(roi_ci[0]), float(roi_ci[1])], "roi_one_sample_t": float(roi_t.statistic),
        "roi_one_sided_p_uncorrected_descriptive": float(roi_t.pvalue),
        "roi_positive_participants": int((roi_values > 0).sum()),
        "n_permutations": N_PERM, "seed": SEED, "maxT_q95": float(np.quantile(max_t, .95)),
        "n_voxels_fwe_p_lt_05": int((p_fwe < .05).sum()),
        "n_vmPFC_voxels_fwe_p_lt_05": int(((p_fwe < .05) & vm_vec).sum()),
        "max_t_in_vmPFC": float(t_obs[vm_vec].max()),
        "min_fwe_p_in_vmPFC": float(p_fwe[vm_vec].min()),
        "max_t_whole_brain": float(t_obs.max()), "min_fwe_p_whole_brain": float(p_fwe.min()),
        "wholebrain_peak_mni_mm": [float(v) for v in nib.affines.apply_affine(reference.affine,
                                             np.array(np.unravel_index(np.argmax(np.where(mask, volume(t_obs).get_fdata(), -np.inf)), shape)))],
        "qc_all_sha256_verified": all(r["sha256_verified"] for r in qc),
        "qc_all_same_grid": all(r["same_grid"] for r in qc), "qc_all_finite": all(r["all_finite"] for r in qc),
        "inference": "one-sided one-sample t; sign-flip max-T permutation FWER over explicit template brain mask; Monte Carlo plus-one p values",
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Figure 1: only voxels passing positive whole-brain max-T FWE correction.
    corrected = np.where(p_fwe < .05, t_obs, 0.0)
    stat_img = volume(corrected)
    peak_flat = int(np.argmax(volume(t_obs).get_fdata()))
    peak_idx = np.asarray(np.unravel_index(peak_flat, shape))
    peak_xyz = nib.affines.apply_affine(reference.affine, peak_idx)
    fig = plt.figure(figsize=(11, 4.8))
    display = plotting.plot_stat_map(stat_img, bg_img=datasets.load_mni152_template(resolution=2),
                                     threshold=0, display_mode="ortho", cut_coords=tuple(peak_xyz),
                                     cmap="hot", black_bg=False, colorbar=True, figure=fig,
                                     title="Positive gain effect: whole-brain max-T FWE p < .05")
    fig.savefig(FIGURES / "whole_brain_t_map.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: participant vmPFC sphere means, plus mean and t-based interval.
    fig, ax = plt.subplots(figsize=(7.4, 4.5))
    jitter = rng.normal(0, 0.035, size=n)
    ax.scatter(roi_values, np.arange(n) + jitter, s=22, color="#376996", alpha=.8, edgecolor="white", linewidth=.3)
    ax.axvline(0, color="#555555", linewidth=1, linestyle="--")
    ax.axvline(roi_mean, color="#c53d2f", linewidth=2, label=f"Mean {roi_mean:.3f}")
    ax.axvspan(roi_ci[0], roi_ci[1], color="#c53d2f", alpha=.12, label="95% t interval for mean")
    ax.set(xlabel="Participant mean gain-effect estimate in vmPFC sphere (arbitrary model units)", ylabel="Participants (ordered by input table)",
           title="vmPFC sphere estimates; descriptive, uncorrected")
    ax.set_yticks([])
    ax.legend(frameon=False, loc="best")
    fig.tight_layout()
    fig.savefig(FIGURES / "vmPFC_participant_estimates.png", dpi=180)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
