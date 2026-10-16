#!/usr/bin/env python3
"""Group inference for the NARPS equal-indifference gain-effect maps."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import nilearn
import numpy as np
import pandas as pd
import scipy
from nilearn.glm.second_level import non_parametric_inference
from nilearn.image import new_img_like
from nilearn.plotting import plot_glass_brain
from scipy import stats
from scipy import ndimage


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUTPUT = ROOT / "results"
FIGURES = OUTPUT / "figures"
N_PERM = 10_000
SEED = 20261015
ROI_CENTER_MNI = np.array([0.0, 46.0, -6.0])
ROI_RADIUS_MM = 10.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    metadata = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    manifest = json.loads((INPUT / "sources.json").read_text())
    listed = manifest["files"]
    rows = metadata.sort_values("participant_id").to_dict("records")
    if len(rows) != 54 or len(listed) != 57:
        raise ValueError(f"Expected 54 subjects and 57 manifest entries; got {len(rows)} and {len(listed)}")

    images: list[nib.spatialimages.SpatialImage] = []
    maps: list[np.ndarray] = []
    qc_rows: list[dict[str, object]] = []
    reference_affine = None
    reference_shape = None
    for row in rows:
        participant = row["participant_id"]
        rel = f"data/{participant}_hypo1_cope.nii.gz"
        record = listed.get(rel)
        if record is None or record.get("participant_id") != participant:
            raise ValueError(f"Missing/mismatched manifest record for {participant}")
        path = INPUT / rel
        if not path.exists():
            raise FileNotFoundError(path)
        digest = sha256(path)
        if digest != record["sha256"] or path.stat().st_size != record["bytes"]:
            raise ValueError(f"Input checksum/size mismatch: {path}")
        image = nib.load(str(path))
        data = np.asarray(image.dataobj, dtype=np.float32)
        if reference_shape is None:
            reference_shape, reference_affine = data.shape, image.affine.copy()
        if data.shape != reference_shape or not np.allclose(image.affine, reference_affine):
            raise ValueError(f"Image grid mismatch for {participant}")
        finite = np.isfinite(data)
        if not finite.all():
            raise ValueError(f"Non-finite voxels in {participant}")
        nonzero = data != 0
        if nonzero.sum() == 0 or np.std(data[nonzero]) == 0:
            raise ValueError(f"Empty or constant effect map for {participant}")
        images.append(image)
        maps.append(data)
        qc_rows.append(
            {
                "participant_id": participant,
                "group": row["group"],
                "age": row["age"],
                "gender": row["gender"],
                "sha256_verified": digest,
                "file_bytes": path.stat().st_size,
                "finite_fraction": float(finite.mean()),
                "nonzero_fraction": float(nonzero.mean()),
                "map_mean_nonzero": float(data[nonzero].mean()),
                "map_sd_nonzero": float(data[nonzero].std(ddof=1)),
            }
        )
    if len({r["participant_id"] for r in rows}) != 54:
        raise ValueError("Duplicate participant IDs")
    if set(listed) - {"participants.tsv", "study-task.md", "upstream-methods.md"} != {
        f"data/{r['participant_id']}_hypo1_cope.nii.gz" for r in rows
    }:
        raise ValueError("Image manifest and metadata participant lists differ")

    stack = np.stack(maps, axis=0)
    # A shared nonzero support avoids treating voxels outside any participant's
    # acquired/modelled brain as observed zeros in the group test.
    mask = np.all(stack != 0, axis=0)
    if mask.sum() < 1000:
        raise ValueError(f"Unreasonably small common mask: {mask.sum()} voxels")
    affine = images[0].affine
    ijk = np.indices(mask.shape).reshape(3, -1).T
    xyz = nib.affines.apply_affine(affine, ijk)
    roi = np.linalg.norm(xyz - ROI_CENTER_MNI, axis=1).reshape(mask.shape) <= ROI_RADIUS_MM
    roi &= mask
    if roi.sum() < 10:
        raise ValueError(f"vmPFC sphere does not overlap group mask: {roi.sum()} voxels")

    # One-sample intercept-only group model. The tested direction is positive.
    # Nilearn returns max-t permutation FWER-corrected p values over the full mask.
    permutation = non_parametric_inference(
        second_level_input=images,
        design_matrix=pd.DataFrame({"intercept": np.ones(len(images))}),
        second_level_contrast="intercept",
        mask=new_img_like(images[0], mask.astype(np.uint8)),
        model_intercept=False,
        n_perm=N_PERM,
        two_sided_test=False,
        random_state=SEED,
        n_jobs=1,
        verbose=1,
    )
    if isinstance(permutation, dict):
        raise RuntimeError("Expected max-t image output when no cluster threshold/TFCE is requested")
    logp_fwe = np.asarray(permutation.get_fdata(), dtype=np.float32)

    roi_values = stack[:, roi].mean(axis=1)
    roi_mean = float(roi_values.mean())
    roi_sd = float(roi_values.std(ddof=1))
    roi_se = roi_sd / np.sqrt(len(roi_values))
    t_roi, p_two = stats.ttest_1samp(roi_values, 0)
    ci = stats.t.interval(0.95, len(roi_values) - 1, loc=roi_mean, scale=roi_se)
    voxel_sd = stack.std(axis=0, ddof=1)
    tmap = np.divide(
        stack.mean(axis=0), voxel_sd / np.sqrt(len(rows)),
        out=np.zeros_like(voxel_sd), where=mask & (voxel_sd > 0),
    )
    meanmap = np.where(mask, stack.mean(axis=0), 0.0)
    raw_p = stats.t.sf(tmap[mask], len(rows) - 1)
    fwe_threshold = -np.log10(0.05)
    significant = mask & (logp_fwe >= fwe_threshold)
    logp_fwe_max = float(np.nanmax(logp_fwe[mask]))
    max_idx = np.unravel_index(np.nanargmax(np.where(mask, tmap, -np.inf)), mask.shape)
    peak_xyz = nib.affines.apply_affine(affine, np.array(max_idx))
    roi_peak_idx_flat = np.argmax(np.where(roi, tmap, -np.inf))
    roi_peak_idx = np.unravel_index(roi_peak_idx_flat, mask.shape)
    roi_peak_xyz = nib.affines.apply_affine(affine, np.array(roi_peak_idx))
    roi_peak_logp = float(logp_fwe[roi_peak_idx])
    roi_peak_fwe_p = min(1.0, 10.0 ** (-roi_peak_logp))
    components, n_components = ndimage.label(significant, structure=np.ones((3, 3, 3)))
    foci: list[dict[str, object]] = []
    for component in range(1, n_components + 1):
        component_mask = components == component
        peak = np.unravel_index(np.argmax(np.where(component_mask, tmap, -np.inf)), tmap.shape)
        xyz = nib.affines.apply_affine(affine, np.asarray(peak))
        foci.append(
            {
                "cluster_id": component,
                "voxels": int(component_mask.sum()),
                "peak_t": float(tmap[peak]),
                "peak_fwe_p": min(1.0, 10.0 ** (-float(logp_fwe[peak]))),
                "peak_x_mni": float(xyz[0]),
                "peak_y_mni": float(xyz[1]),
                "peak_z_mni": float(xyz[2]),
            }
        )
    pd.DataFrame(foci).to_csv(OUTPUT / "whole_brain_fwe_peaks.tsv", sep="\t", index=False)

    def save_map(name: str, data: np.ndarray) -> None:
        image = new_img_like(images[0], data.astype(np.float32))
        nib.save(image, OUTPUT / name)

    save_map("group_mean_effect.nii.gz", meanmap)
    save_map("group_tstat.nii.gz", tmap)
    save_map("group_log10p_fwe_max_t.nii.gz", logp_fwe)
    save_map("common_brain_mask.nii.gz", mask.astype(np.uint8))
    save_map("vmPFC_independent_sphere.nii.gz", roi.astype(np.uint8))

    qc = pd.DataFrame(qc_rows)
    qc.to_csv(OUTPUT / "participant_qc.tsv", sep="\t", index=False)
    pd.DataFrame(
        {
            "participant_id": [r["participant_id"] for r in rows],
            "vmPFC_mean_effect": roi_values,
        }
    ).to_csv(OUTPUT / "vmPFC_subject_effects.tsv", sep="\t", index=False)
    summary = {
        "analysis": "One-sample intercept-only group model of participant gain-effect maps",
        "n_participants_input": len(rows),
        "n_participants_included": len(rows),
        "exclusions": [],
        "image_shape": list(reference_shape),
        "voxel_size_mm": [float(x) for x in nib.affines.voxel_sizes(affine)],
        "mask_voxels_common_nonzero": int(mask.sum()),
        "vmPFC_roi_definition": {
            "type": "independent spherical ROI in MNI space",
            "center_mni_mm": ROI_CENTER_MNI.tolist(),
            "radius_mm": ROI_RADIUS_MM,
            "source": "Bartra, McGuire & Kable (2013) valuation meta-analysis-informed canonical vmPFC location; see report",
            "voxels_in_common_mask": int(roi.sum()),
        },
        "test": {
            "direction": "positive one-sided",
            "method": "Nilearn non_parametric_inference; max-t permutation FWER across common whole-brain mask",
            "permutations": N_PERM,
            "random_seed": SEED,
            "alpha": 0.05,
            "hypothesis_supported_in_vmPFC": bool(np.any(roi & significant)),
            "positive_whole_brain_effect_anywhere": bool(significant.any()),
            "positive_whole_brain_fwe_significant_voxels": int(significant.sum()),
            "positive_whole_brain_fwe_clusters_26_connected": int(n_components),
            "positive_whole_brain_fwe_peaks": foci,
            "max_group_t": float(tmap[max_idx]),
            "max_group_t_mni_mm": [float(x) for x in peak_xyz],
            "max_voxel_fwe_p": min(1.0, 10.0 ** (-logp_fwe_max)),
            "vmPFC_max_t": float(tmap[roi_peak_idx]),
            "vmPFC_peak_mni_mm": [float(x) for x in roi_peak_xyz],
            "vmPFC_peak_whole_brain_fwe_p": roi_peak_fwe_p,
            "roi_mean_effect": roi_mean,
            "roi_sd_between_subjects": roi_sd,
            "roi_mean_effect_95pct_t_ci": [float(ci[0]), float(ci[1])],
            "roi_one_sample_t_descriptive": float(t_roi),
            "roi_one_sample_p_two_sided_descriptive_not_support_test": float(p_two),
            "uncorrected_voxels_p_lt_0_001": int((raw_p < 0.001).sum()),
        },
        "software": {
            "python": platform.python_version(),
            "nilearn": nilearn.__version__,
            "nibabel": nib.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "pandas": pd.__version__,
        },
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": sha256(Path(__file__)),
        "platform": platform.platform(),
        "python_executable": sys.executable,
    }
    (OUTPUT / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Figure 1: effect estimate distribution within the independent vmPFC ROI.
    fig, ax = plt.subplots(figsize=(7.4, 4.6), constrained_layout=True)
    ax.axvline(0, color="#666666", lw=1, ls="--")
    jitter = np.linspace(-0.11, 0.11, len(roi_values))
    ax.scatter(roi_values, np.full_like(roi_values, 0.82) + jitter, s=32, alpha=0.72,
               color="#275D8C", edgecolor="white", linewidth=0.35, label="Participants (n=54)")
    ax.errorbar(roi_mean, 1.18, xerr=[[roi_mean-ci[0]], [ci[1]-roi_mean]], fmt="D",
                color="#B24732", capsize=5, lw=2, label="Mean and 95% CI")
    ax.set_yticks([])
    ax.set_ylim(0.52, 1.48)
    ax.set_xlabel("Mean gain-effect estimate within vmPFC sphere (arbitrary model units)")
    ax.set_title("Equal-indifference group: vmPFC gain-effect estimates")
    ax.legend(frameon=False, loc="upper right")
    ax.spines[["left", "right", "top"]].set_visible(False)
    fig.savefig(FIGURES / "vmPFC_subject_effects.png", dpi=180)
    plt.close(fig)

    # Figure 2: whole-brain positive group effect and max-t FWER-corrected support.
    display_img = new_img_like(images[0], np.where(significant, tmap, 0).astype(np.float32))
    display = plot_glass_brain(
        display_img,
        display_mode="lyrz",
        threshold=0,
        cmap="inferno",
        colorbar=True,
        plot_abs=False,
        title="Positive group t; max-t FWER p < .05 (cyan: vmPFC center)",
        vmax=max(float(np.nanmax(tmap[significant])) if significant.any() else 1, 1),
    )
    display.add_markers(
        [ROI_CENTER_MNI], marker_color="#00A6D6", marker_size=80,
    )
    display.savefig(FIGURES / "whole_brain_fwe_map.png", dpi=180)
    display.close()

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
