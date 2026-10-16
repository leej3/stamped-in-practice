#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Freeze spatial evidence from the twelve completed NARPS round-one workers.

Read-only with respect to worker checkouts. The compact NPZ stores each native
analysis mask and corrected-positive decision, plus lossless deduplicated t
values on shared support. These suffice to regenerate the spatial figure and
its numerical summary offline. Original file identities and branches are
recorded in provenance.json; no participant images are copied.

Full refresh is currently unsupported because run 11 did not retain the exact
template-mask identity needed to prove equivalent reconstructed coverage.
The frozen NPZ remains sufficient for verified offline figure rendering.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import nibabel as nib
import nilearn
from nilearn import datasets, image
import numpy as np

from narps_figure_sources import Sources, EXPERIMENT, REPOSITORY as REPO, add_arguments

OUT = EXPERIMENT / "map-inputs/spatial"
# Final primary analysis only: baseline 01/02 use Bonferroni, not their max-T
# sensitivity analysis. Other workers use native participant sign-flip max-T.
RUNS = {
    1: ("group_t_positive", "group_p_fwe_bonferroni", "whole_brain_search_mask", "analysis_summary.json", "scripts/group_gain.py"),
    2: ("group_tstat", "group_bonferroni_fwe_p", "analysis_mask", "results.json", "scripts/analyze.py"),
    3: ("group_t", "p_fwer_maxT", "analysis_mask", "summary.json", "analyze.py"),
    4: ("t_gain", "p_fwe_gain", "group_coverage_mask", "group_results.json", "analysis/run_group_analysis.py"),
    5: ("group_tstat", "group_log10p_fwe_max_t", "common_brain_mask", "run_summary.json", "analysis/run_group_analysis.py"),
    6: ("maps/group_t_unthresholded", "maps/group_p_fwe_maxT", None, "analysis_results.json", "scripts/group_analysis.py"),
    7: ("maps/group_tstat", "maps/group_positive_maxT_pFWE", None, "analysis_results.json", "scripts/group_analysis.py"),
    8: ("group_t_positive", "group_p_fwe_positive", "group_mask_90pct_coverage", "analysis_summary.json", "scripts/analyze_gain.py"),
    9: ("one_sample_t", "max_t_log10_fwe_p", "common_brain_mask", "results.json", "scripts/analyze_gain.py"),
    10: ("final-v3/group-t", "final-v3/group-fwe-p", None, "final-v3/summary.json", "code/analyze.py"),
    11: ("t_unthresholded", "p_fwe", None, "summary.json", "scripts/group_analysis.py"),
    12: ("group-analysis/group_t", "group-analysis/p_fwe_maxT", None, "group-analysis/summary.json", "analysis/group_analysis.py"),
}
CONDITIONS = [
    ("baseline", "No supplied skills"),
    ("discover-general", "Find useful skills"),
    ("discover-science", "Find research skills"),
    ("stamped-explicit", "Use STAMPED skills"),
]
EXPECTED_MASK = [186400, 192333, 210968, 198029, 198029, 186192,
                 198029, 210968, 198029, 198029, 196120, 198029]
EXPECTED_POSITIVE = [11, 11, 24, 24, 24, 24, 24, 24, 24, 24, 23, 24]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    if 11 in RUNS:
        parser.error(
            "Unsupported spatial refresh: run narps-r1-11 has no retained native "
            "mask or exact source-template/mask hash in frozen provenance. A mask "
            "reconstructed with the installed Nilearn cannot prove scientific "
            "equivalence from voxel count alone. Retain the exact mask provenance "
            "and add a voxelwise comparison before enabling refresh. Use "
            "'pixi run poster-spatial-map' to replay the verified frozen inputs."
        )
    OUT = args.output.resolve()
    binding = Sources(args)
    OUT.mkdir(parents=True, exist_ok=True)
    sources, records = {}, []
    t_maps, p_maps, masks = [], [], []
    ref = None
    source_cohort = None
    common54 = None

    def source(worker, relative):
        path = binding.read(worker, relative)
        sources.update(binding.records)
        return path

    # This saved mask uses every participant's finite, nonzero map support.
    worker09 = binding.worker("narps-r1-09")
    common54 = nib.load(source(worker09, "results/common_brain_mask.nii.gz")).get_fdata() > 0
    for n, (t_name, p_name, mask_name, summary_name, script_name) in RUNS.items():
        run = f"narps-r1-{n:02}"
        worker = binding.worker(run)
        cohort = json.loads(source(worker, "input/sources.json").read_text())
        cohort_hashes = {k: v["sha256"] for k, v in cohort["files"].items() if k.endswith(".nii.gz")}
        if source_cohort is None:
            source_cohort = cohort_hashes
        if cohort_hashes != source_cohort or len(cohort_hashes) != 54:
            raise ValueError(f"Participant map identities differ in {run}")
        source(worker, f"results/{summary_name}")
        source(worker, script_name)
        t_img = nib.load(source(worker, f"results/{t_name}.nii.gz"))
        p_img = nib.load(source(worker, f"results/{p_name}.nii.gz"))
        if ref is None:
            ref = t_img
        for img in (t_img, p_img):
            if img.shape != ref.shape or not np.allclose(img.affine, ref.affine):
                raise ValueError(f"Grid mismatch in {run}")
        t = t_img.get_fdata()
        p = p_img.get_fdata()
        if n in (5, 9):
            p = np.power(10.0, -p)
        if mask_name:
            mask_img = nib.load(source(worker, f"results/{mask_name}.nii.gz"))
            if mask_img.shape != ref.shape or not np.allclose(mask_img.affine, ref.affine):
                raise ValueError(f"Mask grid mismatch in {run}")
            mask = mask_img.get_fdata() > 0
            mask_rule = "native saved analysis mask"
        elif n == 6:
            # The source script writes p=0 outside its support. All in-mask
            # Monte Carlo p values are strictly positive by construction.
            mask = p > 0
            mask_rule = "positive p values; source writes zero outside tested support"
        elif n == 7:
            mask = np.isfinite(p)
            mask_rule = "finite p values; source writes NaN outside tested support"
        elif n == 11:
            raise ValueError("Unsupported run-11 refresh: exact native-mask provenance is unavailable")
        else:
            mask = common54.copy()
            mask_rule = "54/54 finite nonzero participant support; same input identities and rule as saved run09 mask"
        if mask.sum() != EXPECTED_MASK[n - 1]:
            raise ValueError(f"Reconstructed support differs from {run} summary")
        positive = mask & np.isfinite(p) & (p <= .05) & (t > 0)
        if positive.sum() != EXPECTED_POSITIVE[n - 1]:
            raise ValueError(f"Primary corrected result differs from {run} summary")
        assignment, assignment_record = binding.assignment(worker)
        condition, label = CONDITIONS[(n - 1) // 3]
        if assignment["condition"] != condition:
            raise ValueError(f"Unexpected assigned condition for {run}")
        records.append({
            "run": run, "condition": condition, "label": label,
            "branch_url": f"{REPO}/tree/codex/{run}",
            "condition_assignment_sha256": assignment_record["sha256"],
            "condition_assignment": assignment_record,
            "condition_coordinator_revision": assignment["coordinator_commit"],
            "primary_correction": "Bonferroni" if n in (1, 2) else "permutation max-T",
            "mask_rule": mask_rule, "native_mask_voxels": int(mask.sum()),
            "native_positive_voxels": int(positive.sum()),
        })
        t_maps.append(t)
        p_maps.append(positive)
        masks.append(mask)

    shared = common54 & np.logical_and.reduce(masks)
    unique_t, t_indices, seen = [], [], {}
    for t in t_maps:
        values = t[shared].astype(np.float32)
        if not np.array_equal(values.astype(np.float64), t[shared]):
            raise ValueError("float32 storage would alter saved source values")
        h = hashlib.sha256(values.tobytes()).hexdigest()
        if h not in seen:
            seen[h] = len(unique_t)
            unique_t.append(values)
        t_indices.append(seen[h])
    anatomy = image.resample_to_img(
        datasets.load_mni152_template(resolution=2), ref,
        interpolation="continuous", force_resample=True, copy_header=True,
    ).get_fdata(dtype=np.float32)
    np.savez_compressed(
        OUT / "spatial-inputs.npz", affine=ref.affine,
        native_masks=np.stack(masks), native_positive=np.stack(p_maps),
        common_participant_support=common54, shared_support=shared,
        common_t_unique=np.stack(unique_t), common_t_index=np.array(t_indices),
        anatomy=anatomy,
    )
    meta = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "study": "NARPS AO86 equal-indifference potential-gain group analysis",
        "n_participants": 54, "runs_per_condition": 3, "records": records,
        "conditions": [{"id": c, "label": label} for c, label in CONDITIONS],
        "evaluation_support": "Intersection of all twelve native analysis masks and finite nonzero support in all 54 participant maps. Outside is not evaluated as a zero or negative result.",
        "frequency_definition": "For each condition, count the three saved native positive primary FWE decisions at each shared-support voxel; native correction/search-space choices are retained.",
        "t_variability_definition": "Sample SD (ddof=1) across the three saved unthresholded t values per condition, restricted to the same shared support; no new group inference.",
        "display": {"view": "posterior axial crops", "xlim_mni_mm": [-42, 42],
                    "ylim_mni_mm": [-110, -78], "z_cuts_mni_mm": [-8.4, -3.6, -1.2],
                    "orientation": "neurological: image left is participant left",
                    "slice_selection": "Three axial planes containing the observed posterior corrected loci; a descriptive result visualization, not an independent localization test."},
        "anatomy": {"description": "Nilearn bundled skull-stripped MNI152 anatomical context, continuously resampled to the native grid",
                    "url": "https://nilearn.github.io/stable/modules/generated/nilearn.datasets.load_mni152_template.html"},
        "software": {"numpy": np.__version__, "nibabel": nib.__version__, "nilearn": nilearn.__version__},
        "npz_sha256": digest(OUT / "spatial-inputs.npz"),
        "source_files": sources,
        "source_binding": binding.binding,
    }
    (OUT / "provenance.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Frozen 12 runs; shared support {shared.sum():,} voxels; {len(unique_t)} distinct saved t fields")


if __name__ == "__main__":
    main()
