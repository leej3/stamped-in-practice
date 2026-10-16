#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference gain cope maps.

Runs a one-sample, positive-direction group test and max-T sign-flip
permutation correction over the common brain mask. No first-level data are
reconstructed here.
"""
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
INPUT = ROOT / "input"
OUT = ROOT / "analysis" / "results"
FIG = ROOT / "analysis" / "figures"
ATLAS_DIR = ROOT / "analysis" / "atlases"
N_PERM = 10_000
SEED = 20261016
ALPHA = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    ATLAS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((INPUT / "sources.json").read_text())
    meta = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    meta = meta.loc[meta.group.eq("equalIndifference")].copy()
    expected = {x["participant_id"]: (k, x) for k, x in manifest["files"].items() if k.startswith("data/")}
    if set(meta.participant_id) != set(expected) or len(meta) != 54:
        raise ValueError("Metadata/map cohort mismatch")

    arrays, imgs, qc_rows = [], [], []
    for pid in meta.participant_id:
        rel, record = expected[pid]
        path = INPUT / rel
        digest = sha256(path)
        if digest != record["sha256"] or path.stat().st_size != record["bytes"]:
            raise ValueError(f"Checksum/size mismatch: {path}")
        img = nib.load(path)
        dat = img.get_fdata(dtype=np.float32)
        if not np.isfinite(dat).all():
            raise ValueError(f"Non-finite values: {path}")
        imgs.append(img)
        arrays.append(dat)
        qc_rows.append({"participant_id": pid, "bytes": path.stat().st_size,
                        "sha256_ok": True, "shape": list(img.shape),
                        "nonzero_voxels": int(np.count_nonzero(dat)),
                        "min": float(dat.min()), "max": float(dat.max()),
                        "mean_all_voxels": float(dat.mean())})

    ref = imgs[0]
    if any(im.shape != ref.shape or not np.allclose(im.affine, ref.affine, atol=1e-5) for im in imgs):
        raise ValueError("Map geometry mismatch")
    stack = np.stack(arrays, axis=0)
    # These maps encode voxels outside each participant's acquisition/model mask as zero.
    # The intersection gives a conservative common-coverage group mask.
    mask = np.all(stack != 0, axis=0)
    nvox = int(mask.sum())
    if nvox == 0:
        raise ValueError("Empty common brain mask")
    Y = stack[:, mask].astype(np.float64, copy=False)
    n = len(meta)

    mean = Y.mean(axis=0)
    sd = Y.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = stats.t.sf(t_obs, df=n - 1)

    # Sign-flipping subjects is a nonparametric one-sample test under a symmetric
    # null for participant effects. The maximum statistic controls voxelwise FWE.
    rng = np.random.default_rng(SEED)
    sumsq = np.sum(Y * Y, axis=0)
    maxima = np.empty(N_PERM, dtype=np.float32)
    step = 100
    factor = np.sqrt((n - 1) / n)
    for start in range(0, N_PERM, step):
        b = min(step, N_PERM - start)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
        sums = signs @ Y
        # Studentized sign-flip statistic; signs leave the sum of squares fixed.
        denom2 = np.maximum(sumsq[None, :] - (sums * sums / n), np.finfo(float).tiny)
        t_perm = sums * factor / np.sqrt(denom2)
        maxima[start:start + b] = np.max(t_perm, axis=1)
    fwe_p = (1 + (maxima[:, None] >= t_obs[None, :]).sum(axis=0)) / (N_PERM + 1)
    threshold = float(np.quantile(maxima, 1 - ALPHA, method="higher"))
    sig = t_obs >= threshold

    # Independent anatomical localization: Harvard-Oxford cortical atlas in MNI
    # space. vmPFC is operationalized broadly as Frontal Medial + Subcallosal
    # cortex plus the medial (|x| <= 10 mm) portion of Frontal Orbital Cortex.
    atlas = datasets.fetch_atlas_harvard_oxford(
        "cort-maxprob-thr25-2mm", data_dir=ATLAS_DIR, verbose=0)
    atlas_img = image.resample_to_img(atlas.maps, ref, interpolation="nearest")
    atlas_arr = atlas_img.get_fdata().astype(int)
    labels = list(atlas.labels)
    indices = {name: labels.index(name) for name in
               ("Frontal Medial Cortex", "Subcallosal Cortex", "Frontal Orbital Cortex")}
    world_x = nib.affines.apply_affine(ref.affine, np.column_stack([
        np.arange(ref.shape[0]), np.zeros(ref.shape[0]), np.zeros(ref.shape[0])]))[:, 0]
    xgrid = np.broadcast_to(world_x[:, None, None], ref.shape)
    vm_mask = mask & np.isin(atlas_arr, list(indices.values()))
    vm_mask &= ~((atlas_arr == indices["Frontal Orbital Cortex"]) & (np.abs(xgrid) > 10))
    roi_count = int(vm_mask.sum())
    if not roi_count:
        raise ValueError("Anatomical vmPFC mask did not intersect common brain mask")
    roi_Y = stack[:, vm_mask].astype(np.float64)
    roi_vals = roi_Y.mean(axis=1)
    roi_mean = float(roi_vals.mean())
    roi_sd = float(roi_vals.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_ci = stats.t.interval(0.95, df=n - 1, loc=roi_mean, scale=roi_se)
    roi_t = float(roi_mean / roi_se)
    roi_p = float(stats.t.sf(roi_t, n - 1))
    roi_fwe_p_min = float(fwe_p[vm_mask[mask]].min())
    roi_sig_vox = int(np.sum(sig & vm_mask[mask]))
    peak_flat = int(np.argmax(np.where(vm_mask[mask], t_obs, -np.inf)))
    # map flat index in masked vector back to 3D coordinate
    masked_indices = np.flatnonzero(mask)
    peak_ijk = np.unravel_index(masked_indices[peak_flat], ref.shape)
    peak_xyz = nib.affines.apply_affine(ref.affine, peak_ijk).tolist()
    peak_t = float(t_obs[peak_flat])
    peak_fwe = float(fwe_p[peak_flat])

    # Summarize suprathreshold islands for transparent whole-brain reporting.
    from scipy import ndimage
    sig_vol_bool = np.zeros(ref.shape, dtype=bool)
    sig_vol_bool[mask] = sig
    components, n_components = ndimage.label(sig_vol_bool, structure=np.ones((3, 3, 3), dtype=int))
    clusters = []
    mask_linear = np.flatnonzero(mask)
    for cluster_id in range(1, n_components + 1):
        vox = np.argwhere(components == cluster_id)
        masked_positions = np.searchsorted(mask_linear, np.ravel_multi_index(vox.T, ref.shape))
        local_t = t_obs[masked_positions]
        peak_pos = int(masked_positions[int(np.argmax(local_t))])
        peak_ijk_c = vox[int(np.argmax(local_t))]
        peak_xyz_c = nib.affines.apply_affine(ref.affine, peak_ijk_c)
        label_val = int(atlas_arr[tuple(peak_ijk_c)])
        clusters.append({
            "cluster": cluster_id, "voxels": int(len(vox)),
            "volume_mm3": float(len(vox) * np.prod(ref.header.get_zooms()[:3])),
            "peak_t": float(np.max(local_t)),
            "peak_fwe_p": float(fwe_p[peak_pos]),
            "peak_mni_x": float(peak_xyz_c[0]), "peak_mni_y": float(peak_xyz_c[1]),
            "peak_mni_z": float(peak_xyz_c[2]),
            "peak_atlas_label": labels[label_val] if 0 <= label_val < len(labels) else "Unknown",
        })

    # Save maps with the source geometry.
    t_vol = np.zeros(ref.shape, dtype=np.float32)
    p_vol = np.ones(ref.shape, dtype=np.float32)
    t_vol[mask] = t_obs.astype(np.float32)
    p_vol[mask] = fwe_p.astype(np.float32)
    nib.save(nib.Nifti1Image(t_vol, ref.affine, ref.header), OUT / "group_t_map.nii.gz")
    nib.save(nib.Nifti1Image(p_vol, ref.affine, ref.header), OUT / "group_fwe_p_map.nii.gz")
    sig_vol = np.zeros(ref.shape, dtype=np.uint8)
    sig_vol[mask] = sig.astype(np.uint8)
    nib.save(nib.Nifti1Image(sig_vol, ref.affine, ref.header), OUT / "group_fwe_significant_mask.nii.gz")

    # Summary statistics and provenance.
    age = pd.to_numeric(meta.age, errors="coerce")
    gender_counts = meta.gender.value_counts().sort_index().to_dict()
    results = {
        "analysis": "one-sample positive gain cope; whole-brain max-T sign-flip permutation",
        "n": n, "n_excluded": 0, "age_mean_years": float(age.mean()),
        "age_sd_years": float(age.std(ddof=1)), "gender_counts": gender_counts,
        "n_common_mask_voxels": nvox, "common_mask_definition": "nonzero in all 54 participant maps",
        "n_permutations": N_PERM, "seed": SEED,
        "fwe_alpha": ALPHA, "max_t_fwe_threshold": threshold,
        "whole_brain_fwe_significant_voxels": int(sig.sum()),
        "whole_brain_max_t": float(t_obs.max()), "whole_brain_peak_fwe_p": float(fwe_p[np.argmax(t_obs)]),
        "vmPFC_definition": "Harvard-Oxford Frontal Medial + Subcallosal + medial (|x|<=10 mm) Frontal Orbital Cortex; intersect common mask",
        "vmPFC_voxels": roi_count, "vmPFC_mean_cope": roi_mean,
        "vmPFC_sd_between_subjects": roi_sd, "vmPFC_mean_95ci": [float(roi_ci[0]), float(roi_ci[1])],
        "vmPFC_t_df53": roi_t, "vmPFC_positive_one_sided_uncorrected_p": roi_p,
        "vmPFC_min_voxelwise_fwe_p": roi_fwe_p_min,
        "vmPFC_fwe_significant_voxels": roi_sig_vox,
        "vmPFC_peak_t": peak_t, "vmPFC_peak_fwe_p": peak_fwe,
        "vmPFC_peak_mni_mm": [float(x) for x in peak_xyz],
        "vmPFC_leave_one_out_mean_range": [
            float(min((roi_vals.sum() - roi_vals[i]) / (n - 1) for i in range(n))),
            float(max((roi_vals.sum() - roi_vals[i]) / (n - 1) for i in range(n)))],
        "vmPFC_leave_one_out_positive_means": int(sum(
            (roi_vals.sum() - roi_vals[i]) / (n - 1) > 0 for i in range(n))),
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    pd.DataFrame(qc_rows).to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)
    pd.DataFrame({"max_t": maxima}).to_csv(OUT / "permutation_max_t.tsv", sep="\t", index=False)
    pd.DataFrame(clusters).to_csv(OUT / "whole_brain_fwe_clusters.tsv", sep="\t", index=False)
    pd.DataFrame({"participant_id": meta.participant_id, "vmPFC_mean_cope": roi_vals}).to_csv(
        OUT / "vmPFC_participant_values.tsv", sep="\t", index=False)

    # Figures
    fig, ax = plt.subplots(figsize=(6.6, 4.6), constrained_layout=True)
    ax.scatter(np.arange(1, n + 1), roi_vals, s=24, color="#315a7d", alpha=.8,
               edgecolor="white", linewidth=.35)
    ax.axhline(0, color="#555555", linewidth=1, linestyle="--")
    ax.axhline(roi_mean, color="#c45134", linewidth=2,
               label=f"Mean {roi_mean:.3f}; 95% CI [{roi_ci[0]:.3f}, {roi_ci[1]:.3f}]")
    ax.fill_between([0, n + 1], roi_ci[0], roi_ci[1], color="#c45134", alpha=.12)
    ax.set(xlim=(0, n + 1), xlabel="Participant (ordered by source table)",
           ylabel="Mean gain cope in anatomical vmPFC mask",
           title="Participant-level vmPFC gain-effect estimates")
    ax.legend(frameon=False, loc="best")
    fig.savefig(FIG / "vmPFC_participant_effects.png", dpi=180)
    plt.close(fig)

    display = np.zeros(ref.shape, dtype=np.float32)
    display[mask] = np.where(sig, t_obs, 0).astype(np.float32)
    disp_img = nib.Nifti1Image(display, ref.affine)
    disp_img = image.resample_to_img(disp_img, atlas_img, interpolation="nearest")
    fig = plt.figure(figsize=(9, 4.7))
    plotting.plot_glass_brain(disp_img, display_mode="lyrz", colorbar=True,
                              plot_abs=False, threshold=0.01,
                              title="Positive gain effect: whole-brain max-T FWE, p < .05",
                              cmap="cold_hot", figure=fig)
    fig.savefig(FIG / "whole_brain_fwe_glass.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Axial/coronal/sagittal slices through the vmPFC peak, for anatomical context.
    if roi_sig_vox:
        centers = peak_xyz
    else:
        centers = [0.0, 35.0, -10.0]
    plot_img = image.resample_to_img(disp_img, atlas_img, interpolation="nearest")
    display_obj = plotting.plot_stat_map(
        plot_img, display_mode="ortho", cut_coords=centers,
        threshold=0.01, cmap="cold_hot", colorbar=True,
        title="FWE-significant positive clusters; slices at vmPFC peak" if roi_sig_vox else
              "No FWE-significant vmPFC voxels; reference slices at [0, 35, -10] mm")
    display_obj.savefig(FIG / "vmPFC_localization.png", dpi=180)
    display_obj.close()

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
