#!/usr/bin/env python3
"""Group analysis of the supplied NARPS equal-indifference gain cope maps."""
from pathlib import Path
import os
import json
import hashlib
import numpy as np
import pandas as pd
import nibabel as nib
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "input" / "data"
OUT = ROOT / "results"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
# Keep fetched standard-space reference images task-local for reproducibility.
os.environ["NILEARN_DATA"] = str(OUT / "nilearn_data")
from nilearn import datasets, image, plotting
from scipy.stats import t as t_dist
import matplotlib.pyplot as plt

N_PERM = 5000
SEED = 20261016


def main():
    meta = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
    manifest = json.loads((ROOT / "input" / "sources.json").read_text())
    rows = []
    imgs = []
    ref = None
    for _, row in meta.iterrows():
        pid = row.participant_id
        rel = f"data/{pid}_hypo1_cope.nii.gz"
        path = DATA / f"{pid}_hypo1_cope.nii.gz"
        if not path.exists():
            raise FileNotFoundError(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        expected = manifest["files"][rel]["sha256"]
        if digest != expected:
            raise ValueError(f"checksum mismatch: {pid}")
        img = nib.load(path)
        if ref is None:
            ref = img
        elif img.shape != ref.shape or not np.allclose(img.affine, ref.affine):
            raise ValueError(f"image grid mismatch: {pid}")
        data = img.get_fdata(dtype=np.float32)
        if not np.isfinite(data).all():
            raise ValueError(f"non-finite data: {pid}")
        imgs.append(data)
        rows.append({"participant_id": pid, "age": int(row.age), "gender": row.gender,
                     "nonzero_voxels": int(np.count_nonzero(data)),
                     "mean_nonzero_cope": float(data[data != 0].mean()),
                     "sd_nonzero_cope": float(data[data != 0].std()),
                     "max_abs_cope": float(np.abs(data).max()), "sha256_verified": True})

    xvol = np.stack(imgs, axis=0)
    n = xvol.shape[0]
    # Use the standard MNI152 brain mask, nearest-neighbor resampled to map grid,
    # and restrict to voxels represented by all participants.
    mask_path = OUT / "standard_mni152_brain_mask.nii.gz"
    if mask_path.exists():
        standard_mask = nib.load(mask_path)
    else:
        standard_mask = datasets.load_mni152_brain_mask(resolution=2)
        nib.save(standard_mask, mask_path)
    mask_img = image.resample_to_img(standard_mask, ref, interpolation="nearest")
    brain = mask_img.get_fdata() > 0
    coverage = np.all(xvol != 0, axis=0)
    mask = brain & coverage
    if mask.sum() == 0:
        raise RuntimeError("empty analysis mask")
    x = xvol[:, mask].astype(np.float64, copy=False)
    # Positive one-sample t-test of equal-weight participant cope estimates.
    mean = x.mean(axis=0)
    sd = x.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = t_dist.sf(t_obs, df=n-1)
    # Sign-flip max-T family-wise error control across the full brain mask.
    # The sign-flip null preserves each participant's spatial map and jointly
    # tests the one-sided positive hypothesis over all tested voxels.
    rng = np.random.default_rng(SEED)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n))
    sumsq = np.sum(x*x, axis=0)
    max_t = np.empty(N_PERM, dtype=np.float32)
    batch = 100
    for start in range(0, N_PERM, batch):
        ss = signs[start:start+batch] @ x
        denom = np.sqrt(np.maximum((sumsq[None, :] - ss*ss/n) / (n-1), 0) / n)
        tt = np.divide(ss/n, denom, out=np.zeros_like(ss), where=denom > 0)
        max_t[start:start+batch] = np.max(tt, axis=1)
    p_fwe = (1 + np.sum(max_t[:, None] >= t_obs[None, :], axis=0)) / (N_PERM + 1)

    # Anatomical localization aid, specified in MNI coordinates before looking
    # at results: a bilateral medial prefrontal envelope (x +/-20, y 20..65,
    # z -25..15 mm). Statistical inference remains whole-brain max-T.
    ijk = np.array(np.where(mask)).T
    xyz = nib.affines.apply_affine(ref.affine, ijk)
    vm_roi = (np.abs(xyz[:, 0]) <= 20) & (xyz[:, 1] >= 20) & (xyz[:, 1] <= 65) & (xyz[:, 2] >= -25) & (xyz[:, 2] <= 15)
    roi_t = t_obs[vm_roi]
    roi_p_fwe = p_fwe[vm_roi]
    roi_mean = mean[vm_roi]

    # Group-level maps saved on original grid, zero outside common analysis mask.
    maps = {}
    for name, vals in [("mean_cope", mean), ("t_positive", t_obs), ("p_uncorrected", p_unc), ("p_fwe_maxT", p_fwe)]:
        # For p maps use 1 outside the tested mask; for estimates/statistics use
        # NaN so untested voxels cannot be mistaken for observed zeros.
        fill = 1.0 if name.startswith("p_") else np.nan
        arr = np.full(ref.shape, fill, dtype=np.float32)
        arr[mask] = vals.astype(np.float32)
        maps[name] = nib.Nifti1Image(arr, ref.affine, ref.header)
        nib.save(maps[name], OUT / f"{name}.nii.gz")

    # Voxel and ROI summaries, with bootstrap CI for the mean ROI effect.
    roi_x = x[:, vm_roi]
    subject_roi = roi_x.mean(axis=1)
    boot_rng = np.random.default_rng(SEED + 1)
    bidx = boot_rng.integers(0, n, size=(20000, n))
    boot = subject_roi[bidx].mean(axis=1)
    sig = p_fwe <= .05
    sig_roi = sig & vm_roi
    sig_ijk = ijk[sig]
    sig_xyz = nib.affines.apply_affine(ref.affine, sig_ijk) if len(sig_ijk) else np.empty((0, 3))
    if sig.any():
        sig_idx = np.flatnonzero(sig)
        peaks = sorted(sig_idx, key=lambda j: t_obs[j], reverse=True)[:10]
        peak_rows = [{"rank": k+1, "x_mm": float(xyz[j,0]), "y_mm": float(xyz[j,1]), "z_mm": float(xyz[j,2]),
                      "t": float(t_obs[j]), "p_fwe": float(p_fwe[j]), "mean_cope": float(mean[j])}
                     for k,j in enumerate(peaks)]
    else:
        peak_rows = []
    summary = {
        "n_participants": n, "n_excluded": 0, "n_permutations": N_PERM,
        "seed": SEED, "analysis_mask_voxels": int(mask.sum()),
        "mask_definition": "MNI152 standard brain mask, nearest-neighbor resampled to input grid, intersected with voxels nonzero in all 54 maps",
        "model": "equal-weight one-sample group t model on participant gain cope estimates; positive direction",
        "correction": "one-sided sign-flip permutation max-T FWE across all analysis-mask voxels; plus-one p estimate",
        "df": n-1, "max_observed_t": float(t_obs.max()), "max_observed_p_fwe": float(p_fwe.min()),
        "n_fwe_voxels_p05": int(sig.sum()), "n_fwe_vmpfc_envelope_voxels_p05": int(sig_roi.sum()),
        "n_vmpfc_envelope_voxels": int(vm_roi.sum()), "vmpfc_envelope_mean_cope": float(roi_mean.mean()),
        "vmpfc_envelope_subject_mean": float(subject_roi.mean()),
        "vmpfc_envelope_subject_sd": float(subject_roi.std(ddof=1)),
        "vmpfc_envelope_bootstrap_95ci": [float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],
        "vmpfc_envelope_max_t": float(roi_t.max()), "vmpfc_envelope_min_p_fwe": float(roi_p_fwe.min()),
        "vmpfc_envelope_definition": "MNI coordinates |x|<=20, 20<=y<=65, -25<=z<=15 mm; localization only, not a separately corrected ROI test",
        "significant_peaks": peak_rows,
        "qc": {"all_checksums_match": True, "all_grids_match": True, "all_values_finite": True,
               "participant_file_count": len(rows), "all_maps_have_nonzero_voxels": bool(all(r['nonzero_voxels'] > 0 for r in rows)),
               "participant_mean_cope_range": [float(min(r['mean_nonzero_cope'] for r in rows)), float(max(r['mean_nonzero_cope'] for r in rows))],
               "participant_max_abs_cope_range": [float(min(r['max_abs_cope'] for r in rows)), float(max(r['max_abs_cope'] for r in rows))]},
        "software": {"python": "3.13", "numpy": np.__version__, "pandas": pd.__version__, "nibabel": nib.__version__},
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    pd.DataFrame(rows).to_csv(OUT / "participant_qc.csv", index=False)
    pd.DataFrame(peak_rows).to_csv(OUT / "significant_peaks.csv", index=False)

    # Figure: effect estimate map and whole-brain FWE-significant t map.
    template_path = OUT / "mni152_template.nii.gz"
    if template_path.exists():
        template = nib.load(template_path)
    else:
        template = datasets.load_mni152_template(resolution=2)
        nib.save(template, template_path)
    visual_mean = np.zeros(ref.shape, dtype=np.float32)
    visual_mean[mask] = mean.astype(np.float32)
    mean_img = nib.Nifti1Image(visual_mean, ref.affine, ref.header)
    plot_mean = image.resample_to_img(mean_img, template, interpolation="continuous")
    t_img = maps["t_positive"]
    # Mask t map by corrected significance for clear rendering.
    sig_arr = np.zeros(ref.shape, dtype=np.float32); sig_arr[mask] = np.where(sig, t_obs, 0)
    sig_img = nib.Nifti1Image(sig_arr, ref.affine, ref.header)
    sig_plot = image.resample_to_img(sig_img, template, interpolation="continuous")
    roi_img_arr = np.zeros(ref.shape, dtype=np.uint8); roi_img_arr[tuple(ijk[vm_roi].T)] = 1
    roi_img = image.resample_to_img(nib.Nifti1Image(roi_img_arr, ref.affine, ref.header), template, interpolation="nearest")
    mean_path = FIG / "mean_gain_cope.png"
    d = plotting.plot_stat_map(plot_mean, bg_img=template, display_mode="z", cut_coords=[-16,-8,0,8],
                               threshold=0, cmap="cold_hot", colorbar=True, black_bg=False,
                               title="Mean gain cope (unthresholded)")
    d.savefig(mean_path, dpi=160)
    d.close()
    fwe_path = FIG / "wholebrain_maxT_fwe.png"
    d = plotting.plot_stat_map(sig_plot, bg_img=template, display_mode="z", cut_coords=[-16,-8,0,8],
                               threshold=4.0, cmap="hot", colorbar=True, black_bg=False,
                               title=f"Positive t; max-T FWE p ≤ .05 (n={int(sig.sum())})")
    d.add_contours(roi_img, levels=[.5], colors="cyan", linewidths=1)
    d.savefig(fwe_path, dpi=160)
    d.close()
    # Combine standalone Nilearn displays into a convenient report figure.
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    for ax, pth in zip(axes, [mean_path, fwe_path]):
        ax.imshow(plt.imread(pth)); ax.axis("off")
    fig.suptitle("NARPS equal-indifference group: gain effect", fontsize=15)
    fig.tight_layout()
    fig.savefig(FIG / "group_gain_maps.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # ROI subject means, preserving individual variability.
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.hist(subject_roi, bins=12, color="#4978a8", edgecolor="white")
    ax.axvline(0, color="black", lw=1)
    ax.axvline(subject_roi.mean(), color="#c43b3b", lw=2, label=f"mean = {subject_roi.mean():.4g}")
    ax.text(.02, .97, f"bootstrap 95% CI [{np.quantile(boot,.025):.3g}, {np.quantile(boot,.975):.3g}]",
            transform=ax.transAxes, va="top", ha="left", fontsize=10)
    ax.set(xlabel="Participant mean gain cope within vmPFC envelope", ylabel="Participants",
           title="Between-participant distribution of vmPFC-envelope effects")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "vmpfc_participant_distribution.png", dpi=180)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
