#!/usr/bin/env python3
"""Group analysis of fixed NARPS AO86 equal-indifference gain COPE maps.

The sole inferential contrast is a one-sample, positive-direction group test.
Whole-brain family-wise error is controlled by the permutation maximum-t
distribution over the common map-coverage mask. No participant is excluded.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import nilearn
from nilearn import datasets, image, plotting
import scipy
from scipy.stats import t as t_dist
from scipy import ndimage


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
N_PERM = 5000
SEED = 20261016


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def save_map(values: np.ndarray, mask: np.ndarray, ref: nib.spatialimages.SpatialImage,
             filename: str, dtype=np.float32, outside=0) -> None:
    full = np.full(mask.shape, outside, dtype=dtype)
    full[mask] = values.astype(dtype)
    hdr = ref.header.copy()
    hdr.set_data_dtype(dtype)
    nib.save(nib.Nifti1Image(full, ref.affine, hdr), OUT / filename)


def main() -> None:
    meta = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
    sources = json.loads((ROOT / "input/sources.json").read_text())
    rows = []
    imgs, arrays = [], []
    expected = sources["files"]
    for row in meta.itertuples(index=False):
        rel = f"data/{row.participant_id}_hypo1_cope.nii.gz"
        path = ROOT / "input" / rel
        assert rel in expected, f"No source record for {rel}"
        digest = sha256(path)
        assert digest == expected[rel]["sha256"], f"SHA256 mismatch: {rel}"
        img = nib.load(str(path))
        arr = img.get_fdata(dtype=np.float32)
        if imgs:
            assert arr.shape == imgs[0].shape and np.allclose(img.affine, imgs[0].affine), f"Geometry mismatch: {rel}"
        imgs.append(img)
        arrays.append(arr)
        rows.append({"participant_id": row.participant_id, "sha256_verified": True,
                     "n_voxels_zero": int(np.sum(arr == 0)),
                     "n_voxels_nonfinite": int(np.sum(~np.isfinite(arr))),
                     "cope_mean_nonzero": float(arr[arr != 0].mean()),
                     "cope_sd_nonzero": float(arr[arr != 0].std(ddof=1))})

    Xall = np.stack(arrays)
    assert len(meta) == 54 and meta.participant_id.is_unique
    assert set(meta.group) == {"equalIndifference"}
    assert np.isfinite(Xall).all(), "Non-finite map values found"
    # Zero-valued voxels represent outside-map support; use voxels observed in
    # every participant to ensure a common spatial denominator for max-T FWER.
    common_support = np.all(Xall != 0, axis=0)
    brain_img = datasets.load_mni152_brain_mask(resolution=2)
    brain_resampled = image.resample_to_img(brain_img, imgs[0], interpolation="nearest")
    brain_mask = np.asarray(brain_resampled.dataobj) > 0
    mask = common_support & brain_mask
    assert mask.sum() > 0
    X = Xall[:, mask].astype(np.float64)
    n, v = X.shape
    mean = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    t_obs = mean / (sd / np.sqrt(n))
    p_unc = t_dist.sf(t_obs, n - 1)

    # One-sided sign-flip permutation test. Under the null, participant effect
    # estimates are assumed exchangeable about zero (symmetric errors).
    rng = np.random.default_rng(SEED)
    sumsq = np.einsum("ij,ij->j", X, X)
    max_t = np.empty(N_PERM, dtype=np.float32)
    batch = 20
    for start in range(0, N_PERM, batch):
        b = min(batch, N_PERM - start)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
        sums = signs @ X
        # t = sum / sqrt((n*sum(x^2) - sum(x)^2)/(n-1))
        denom = np.sqrt(np.maximum((n * sumsq[None, :] - sums * sums) / (n - 1), 1e-30))
        max_t[start:start+b] = np.max(sums / denom, axis=1)
    sorted_max_t = np.sort(max_t)
    p_fwer = (1 + N_PERM - np.searchsorted(sorted_max_t, t_obs, side="left")) / (N_PERM + 1)
    cutoff = float(np.quantile(max_t, 0.95, method="higher"))
    sig = p_fwer <= 0.05
    save_map(mean, mask, imgs[0], "group_mean_cope.nii.gz")
    save_map(t_obs, mask, imgs[0], "group_t.nii.gz")
    save_map(p_fwer, mask, imgs[0], "group_p_fwer.nii.gz", outside=np.nan)
    save_map(sig.astype(float), mask, imgs[0], "group_fwer05_mask.nii.gz")

    # Independent anatomical locator for vmPFC: Harvard-Oxford cortical
    # Frontal Medial Cortex + Subcallosal Cortex (25% threshold). Resample
    # nearest-neighbour to the supplied MNI152NLin2009cAsym map grid.
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm",
                                               data_dir=ROOT / "references/nilearn", verbose=0)
    labels = list(atlas.labels)
    wanted = [labels.index("Frontal Medial Cortex"), labels.index("Subcallosal Cortex")]
    atlas_data = np.asarray(atlas.maps.dataobj)
    roi_img = nib.Nifti1Image(np.isin(atlas_data, wanted).astype(np.uint8), atlas.maps.affine)
    roi_resampled = image.resample_to_img(roi_img, imgs[0], interpolation="nearest")
    roi = (np.asarray(roi_resampled.dataobj) > 0) & mask
    assert roi.sum() > 0
    roi_person = Xall[:, roi].mean(axis=1)
    roi_mean = float(roi_person.mean())
    roi_sd = float(roi_person.std(ddof=1))
    roi_se = roi_sd / np.sqrt(n)
    roi_t = roi_mean / roi_se
    roi_p = float(t_dist.sf(roi_t, n - 1))
    roi_ci = [float(roi_mean - t_dist.ppf(.975, n-1)*roi_se),
              float(roi_mean + t_dist.ppf(.975, n-1)*roi_se)]
    roi_perm = np.empty(N_PERM)
    for i in range(N_PERM):
        s = rng.choice(np.array([-1., 1.]), size=n)
        roi_perm[i] = s @ roi_person / (roi_person.std(ddof=1) * np.sqrt(n))
    roi_p_perm = float((1 + np.sum(roi_perm >= roi_t)) / (N_PERM + 1))
    nib.save(nib.Nifti1Image(roi.astype(np.uint8), imgs[0].affine, imgs[0].header),
             OUT / "vmPFC_proxy_roi.nii.gz")

    # Subject-level ROI distribution with mean and 95% t interval.
    fig, ax = plt.subplots(figsize=(6.8, 4.2), constrained_layout=True)
    jitter = rng.normal(0, .045, size=n)
    ax.scatter(jitter, roi_person, s=24, alpha=.72, color="#345995", edgecolor="white", linewidth=.35)
    ax.axhline(0, color="#555555", linewidth=1, linestyle="--")
    ax.errorbar([.28], [roi_mean], yerr=[[roi_mean-roi_ci[0]], [roi_ci[1]-roi_mean]],
                fmt="D", color="#c3423f", capsize=4, markersize=6, label="Mean and 95% CI")
    ax.set_xlim(-.18, .48)
    ax.set_xticks([0, .28], ["Participants", "Group mean"])
    ax.set_ylabel("Mean gain-effect COPE in vmPFC proxy (model units)")
    ax.set_title("vmPFC anatomical summary (not the whole-brain decision test)")
    ax.legend(frameon=False, loc="best")
    fig.savefig(OUT / "vmPFC_roi.png", dpi=180)
    plt.close(fig)

    # Display the positive t field for context, with whole-brain FWER
    # significant voxels and ROI contour marked.
    full_t = np.zeros(mask.shape, dtype=np.float32); full_t[mask] = t_obs
    full_sig = np.zeros(mask.shape, dtype=np.uint8); full_sig[mask] = sig
    t_img = nib.Nifti1Image(full_t, imgs[0].affine, imgs[0].header)
    sig_img = nib.Nifti1Image(full_sig, imgs[0].affine, imgs[0].header)
    roi_img2 = nib.Nifti1Image(roi.astype(np.uint8), imgs[0].affine, imgs[0].header)
    positive_t = nib.Nifti1Image(np.where(full_t > 0, full_t, 0), imgs[0].affine, imgs[0].header)
    disp = plotting.plot_stat_map(positive_t, threshold=2.0, display_mode="z", cut_coords=[-10, 0, 10, 20, 30],
                                  cmap="hot", symmetric_cbar=False, colorbar=True,
                                  title="Positive gain effect: uncorrected t > 2; green outline = vmPFC proxy",
                                  dim=-0.3, black_bg=False, annotate=True)
    disp.add_contours(roi_img2, levels=[.5], colors=["#21a179"], linewidths=1.2)
    disp.savefig(OUT / "wholebrain_t_and_fwer.png", dpi=180)
    disp.close()
    # Separate corrected-result figure prevents the very small significant
    # occipital clusters from being visually lost in the unthresholded field.
    glass = plotting.plot_glass_brain(sig_img, display_mode="lyrz", threshold=.5,
                                     colorbar=False, plot_abs=False, cmap="Reds",
                                     title="Positive whole-brain voxelwise FWER p <= .05 (max-T permutations)")
    glass.savefig(OUT / "wholebrain_fwer_clusters.png", dpi=180)
    glass.close()

    pd.DataFrame(rows).to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)
    # Selected whole-brain peak/cluster summary.
    if sig.any():
        vals = np.where(sig, t_obs, -np.inf)
        peak_flat = int(vals.argmax())
        peak_ijk = np.argwhere(mask)[peak_flat]
        peak_xyz = nib.affines.apply_affine(imgs[0].affine, peak_ijk).tolist()
        max_sig_t = float(t_obs[peak_flat])
        peak_pfwer = float(p_fwer[peak_flat])
    else:
        peak_xyz, max_sig_t, peak_pfwer = None, None, None
    components, n_components = ndimage.label(full_sig)
    masked_index = np.full(mask.shape, -1, dtype=np.int32)
    masked_index[mask] = np.arange(v)
    clusters = []
    for label_id in range(1, n_components + 1):
        vox_ijk = np.argwhere(components == label_id)
        local_t = t_obs[masked_index[tuple(vox_ijk.T)]]
        peak_ijk = vox_ijk[int(local_t.argmax())]
        clusters.append({"cluster_id": label_id, "n_voxels_6conn": int(len(vox_ijk)),
                         "peak_t": float(local_t.max()),
                         "peak_mni_mm": nib.affines.apply_affine(imgs[0].affine, peak_ijk).tolist()})
    pd.DataFrame(clusters).to_csv(OUT / "fwer_positive_clusters.tsv", sep="\t", index=False)
    roi_fwer_vox = int(full_sig[roi].sum())
    result = {
        "n_participants": n, "excluded": [], "n_input_maps": len(imgs),
        "n_common_coverage_voxels": int(v),
        "mask_rule": "intersection of nonzero support in every participant map and resampled MNI152 2-mm brain mask",
        "permutation_method": "one-sample sign-flip max-t, positive one-sided, whole-brain voxelwise FWER",
        "n_permutations": N_PERM, "seed": SEED, "max_t_95_cutoff": cutoff,
        "n_fwer_positive_voxels": int(sig.sum()), "smallest_reportable_fwer_p": 1/(N_PERM+1),
        "n_fwer_clusters_6conn": len(clusters), "n_fwer_voxels_overlapping_vmPFC_proxy": roi_fwer_vox,
        "peak_sig_mni_mm": peak_xyz, "peak_sig_t": max_sig_t, "peak_sig_p_fwer": peak_pfwer,
        "peak_unthresholded_t": float(t_obs.max()),
        "n_uncorrected_p_lt_0_001": int(np.sum(p_unc < .001)),
        "vmPFC_roi": {
            "definition": "Harvard-Oxford cortical Frontal Medial Cortex + Subcallosal Cortex, 25% maximum-probability atlas, nearest-neighbour resampled",
            "n_voxels": int(roi.sum()), "mean_cope": roi_mean, "sd_between_participants": roi_sd,
            "ci95_t": roi_ci, "t": float(roi_t), "p_one_sided_parametric": roi_p,
            "p_one_sided_signflip": roi_p_perm,
        },
        "software": {"python": sys.version.split()[0], "nibabel": nib.__version__,
                     "numpy": np.__version__, "pandas": pd.__version__,
                     "scipy": scipy.__version__, "nilearn": nilearn.__version__,
                     "matplotlib": mpl.__version__},
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
