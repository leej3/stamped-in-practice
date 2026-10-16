#!/usr/bin/env python3
"""Whole-brain group analysis of NARPS AO86 equal-indifference gain maps."""
from pathlib import Path
import json
import hashlib
import warnings

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from nilearn.glm.second_level import non_parametric_inference
from nilearn.image import new_img_like, resample_to_img
from nilearn import datasets

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "input" / "data"
OUT = ROOT / "results"
FIG = ROOT / "figures"
N_PERM = 5_000
SEED = 20261016


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    participants = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
    source = json.loads((ROOT / "input" / "sources.json").read_text())
    expected = sorted(source["files"][k]["participant_id"] for k in source["files"] if k.endswith(".nii.gz"))
    paths = {p.name.split("_")[0]: p for p in DATA.glob("*_hypo1_cope.nii.gz")}
    assert len(paths) == 54 and sorted(paths) == expected
    assert participants.participant_id.tolist() == expected

    expected_file_meta = {source["files"][k]["participant_id"]: source["files"][k] for k in source["files"] if k.endswith(".nii.gz")}
    for participant_id, path in paths.items():
        meta = expected_file_meta[participant_id]
        assert path.stat().st_size == meta["bytes"], f"Byte count mismatch: {participant_id}"
        assert sha256(path) == meta["sha256"], f"SHA256 mismatch: {participant_id}"
    imgs = [nib.load(str(paths[s])) for s in participants.participant_id]
    ref = imgs[0]
    arrays = np.stack([im.get_fdata(dtype=np.float32) for im in imgs], axis=0)
    same_grid = all(im.shape == ref.shape and np.allclose(im.affine, ref.affine, atol=1e-5) for im in imgs)
    assert same_grid, "Input maps differ in shape or affine; no implicit resampling allowed."
    finite = np.isfinite(arrays)
    nz_frac = np.mean(arrays != 0, axis=0)
    # Strict common support: every participant map must have a finite, nonzero estimate.
    # Exact zero may be a true coefficient, so this remains an operational support proxy.
    mask = (nz_frac == 1.0) & np.all(finite, axis=0)
    if mask.sum() < 10_000:
        raise RuntimeError(f"Unexpectedly small analysis mask: {mask.sum()} voxels")
    # Summaries and QC: preserve all supplied cases unless a predeclared technical check fails.
    rows = []
    for i, row in participants.iterrows():
        a = arrays[i]
        vals = a[mask]
        rows.append({
            "participant_id": row.participant_id,
            "age": row.age,
            "gender": row.gender,
            "finite_fraction": float(finite[i].mean()),
            "nonzero_fraction": float(np.mean(a != 0)),
            "mask_mean": float(np.mean(vals)),
            "mask_sd": float(np.std(vals, ddof=1)),
            "mask_median": float(np.median(vals)),
            "mask_iqr": float(np.subtract(*np.percentile(vals, [75, 25]))),
            "sha256": sha256(paths[row.participant_id]),
        })
    qc = pd.DataFrame(rows)
    qc.to_csv(OUT / "participant_qc.tsv", sep="\t", index=False)

    # One-sample group model: intercept only; hypothesis is a positive mean effect.
    mask_img = new_img_like(ref, mask.astype(np.uint8))
    design = pd.DataFrame({"intercept": np.ones(len(imgs))})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        perm = non_parametric_inference(
            imgs, design_matrix=design, second_level_contrast="intercept",
            mask=mask_img, n_perm=N_PERM, two_sided_test=False,
            random_state=SEED, n_jobs=1, verbose=1,
        )
    if isinstance(perm, nib.Nifti1Image):
        perm = {"logp_max_t": perm}
    available = list(perm)
    if "logp_max_t" not in perm:
        raise RuntimeError(f"Expected max-T corrected log p map; got {available}")
    logp_img = perm["logp_max_t"]
    logp = logp_img.get_fdata()
    fwe_p = np.power(10.0, -logp)
    mean = arrays.mean(axis=0)
    sd = arrays.std(axis=0, ddof=1)
    tmap = np.zeros_like(mean)
    np.divide(mean, sd / np.sqrt(len(imgs)), out=tmap, where=sd > 0)
    for name, arr in [("group_mean_gain_effect.nii.gz", mean), ("group_t_one_sample.nii.gz", tmap),
                      ("group_fwe_p_maxT.nii.gz", fwe_p), ("group_log10p_fwe_maxT.nii.gz", logp),
                      ("group_mask.nii.gz", mask.astype(np.uint8))]:
        nib.save(new_img_like(ref, arr.astype(np.float32)), OUT / name)

    # Anatomical localization is descriptive and does not define the inferential search space.
    # Harvard-Oxford cortical labels provide a transparent vmPFC proxy: medial frontal and subcallosal cortex.
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    atlas_img = atlas.maps if isinstance(atlas.maps, nib.spatialimages.SpatialImage) else nib.load(atlas.maps)
    labels = [x.decode() if isinstance(x, bytes) else str(x) for x in atlas.labels]
    selected_names = ["Frontal Medial Cortex", "Subcallosal Cortex"]
    selected_ids = [i for i, label in enumerate(labels) if label in selected_names]
    if not selected_ids:
        raise RuntimeError(f"Could not identify vmPFC proxy labels in atlas: {labels}")
    atlas_res = resample_to_img(atlas_img, ref, interpolation="nearest")
    atlas_arr = atlas_res.get_fdata().astype(int)
    ijk = np.indices(ref.shape).reshape(3, -1).T
    xyz_grid = nib.affines.apply_affine(ref.affine, ijk).reshape(*ref.shape, 3)
    vm_mask = (np.isin(atlas_arr, selected_ids) & mask
               & (np.abs(xyz_grid[..., 0]) <= 20)
               & (xyz_grid[..., 1] > 0)
               & (xyz_grid[..., 2] <= 15))
    vm_mask_img = new_img_like(ref, vm_mask.astype(np.uint8))
    nib.save(vm_mask_img, OUT / "vmPFC_proxy_mask.nii.gz")
    vm_vals = arrays[:, vm_mask]
    if vm_vals.shape[1] == 0:
        raise RuntimeError("vmPFC proxy has no covered voxels")
    vm_subj = vm_vals.mean(axis=1)
    vm_mean = float(vm_subj.mean())
    vm_se = float(stats.sem(vm_subj))
    vm_ci = stats.t.interval(.95, len(vm_subj)-1, loc=vm_mean, scale=vm_se)

    # Whole-brain correction and vmPFC overlap.
    sig = (fwe_p < .05) & mask
    # For reporting peaks, use local maxima of positive t map among corrected significant voxels.
    peak_rows = []
    if sig.any():
        coords = np.argwhere(sig)
        vals = tmap[sig]
        order = np.argsort(vals)[::-1]
        affine = ref.affine
        for ix in order[:10]:
            ijk = coords[ix]
            xyz = nib.affines.apply_affine(affine, ijk)
            peak_rows.append({"i": int(ijk[0]), "j": int(ijk[1]), "k": int(ijk[2]),
                              "x_mm": float(xyz[0]), "y_mm": float(xyz[1]), "z_mm": float(xyz[2]),
                              "t": float(tmap[tuple(ijk)]), "mean_effect": float(mean[tuple(ijk)]),
                              "p_fwe_maxT": float(fwe_p[tuple(ijk)]),
                              "in_vmPFC_proxy": bool(vm_mask[tuple(ijk)])})
    pd.DataFrame(peak_rows).to_csv(OUT / "significant_peak_voxels.tsv", sep="\t", index=False)

    # Save the actual max-T permutation p-values/summary and audit information.
    result = {
        "n_participants": len(imgs), "n_excluded": 0, "participant_ids": participants.participant_id.tolist(),
        "n_perm": N_PERM, "seed": SEED, "test": "one-sample intercept; positive one-sided; voxelwise max-T sign-flip permutation",
        "whole_brain_mask_voxels": int(mask.sum()), "mask_rule": "finite and nonzero in all participant maps",
        "mask_voxel_volume_mm3": float(np.prod(ref.header.get_zooms()[:3])), "map_shape": list(ref.shape),
        "map_zooms_mm": [float(x) for x in ref.header.get_zooms()[:3]], "permutation_outputs": available,
        "significant_voxels_p_fwe_lt_0_05": int(sig.sum()),
        "significant_vmPFC_proxy_voxels_p_fwe_lt_0_05": int(np.sum(sig & vm_mask)),
        "vmPFC_proxy_labels": selected_names, "vmPFC_proxy_coordinate_clip": "|x| <= 20 mm, y > 0 mm, z <= 15 mm",
        "vmPFC_proxy_voxels": int(vm_mask.sum()),
        "vmPFC_proxy_mean_subject_effect": vm_mean, "vmPFC_proxy_mean_subject_effect_ci95": [float(vm_ci[0]), float(vm_ci[1])],
        "vmPFC_proxy_subject_effect_sd": float(np.std(vm_subj, ddof=1)),
        "whole_mask_subject_mean_effect": float(np.mean(arrays[:, mask].mean(axis=1))),
        "whole_mask_subject_mean_sd": float(np.std(arrays[:, mask].mean(axis=1), ddof=1)),
        "smallest_fwe_p": float(np.min(fwe_p[mask])),
        "peak_t": float(np.max(tmap[mask])),
        "peak_coordinate_mni_mm": [float(v) for v in nib.affines.apply_affine(ref.affine, np.unravel_index(np.argmax(np.where(mask, tmap, -np.inf)), ref.shape))],
        "excluded_ids": [], "atlas_name": "Harvard-Oxford cortical atlas, max-probability threshold 25%",
        "python_version": __import__("sys").version.split()[0],
        "numpy_version": np.__version__, "nibabel_version": nib.__version__,
        "nilearn_version": __import__("nilearn").__version__,
    }
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
