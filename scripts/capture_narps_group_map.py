#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Capture the run-09 illustrative group map from its retained scientific object."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

import nibabel as nib
import nilearn
from nilearn import datasets, image

from narps_figure_sources import Sources, EXPERIMENT, add_arguments, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    parser.add_argument("--output", type=Path, default=EXPERIMENT / "map-inputs/example")
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    sources = Sources(args)
    worker = sources.worker("narps-r1-09")
    copied = {}
    files = {
        "summaries/narps-r1-09.json": "results/results.json",
        "participant-map-sources.json": "input/sources.json",
        "source-analysis-run09.py": "scripts/analyze_gain.py",
        **{f"maps/{name}": f"results/{name}" for name in (
            "one_sample_t.nii.gz", "common_brain_mask.nii.gz",
            "max_t_fwe_p05_mask.nii.gz", "vmPFC_AAL_medial_orbitofrontal_mask.nii.gz",
        )},
    }
    for destination, original in files.items():
        src = sources.read(worker, original)
        target = out / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        copied[destination] = {
            **sources.records[f"{worker.name}/{original}"],
            "transformation": "byte-for-byte copy; annex payload dereferenced",
        }
    ref = nib.load(out / "maps/one_sample_t.nii.gz")
    template = image.resample_to_img(
        datasets.load_mni152_template(resolution=2), ref,
        interpolation="continuous", force_resample=True, copy_header=True,
    )
    anatomical = out / "maps/anatomical-context.nii.gz"
    nib.save(template, anatomical)
    copied["maps/anatomical-context.nii.gz"] = {
        "sha256": sha256(anatomical), "bytes": anatomical.stat().st_size,
        "source_url": "https://nilearn.github.io/stable/modules/generated/nilearn.datasets.load_mni152_template.html",
        "source_description": "Nilearn bundled skull-stripped ICBM152 MNI template; anatomical context only",
        "nilearn_version": nilearn.__version__,
        "transformation": "load_mni152_template(resolution=2), continuous resampling to run09 t-map grid",
    }
    assignment, assignment_record = sources.assignment(worker)
    meta = {
        "snapshot_generated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Illustrative completed development run; not a condition-average map",
        "study": "NARPS Hypothesis 1, AO86 equal-indifference participant gain maps",
        "paper": "https://doi.org/10.1038/s41586-020-2314-9",
        "data": "https://doi.org/10.18112/openneuro.ds001734.v1.0.4",
        "participant_maps": "https://neurovault.org/collections/4932/",
        "n_participants": 54,
        "representative_map_run": worker.name,
        "source_binding": sources.binding,
        "records": [{"run": worker.name, "condition": assignment["condition"],
                     "summary": "summaries/narps-r1-09.json", "assignment": assignment_record}],
        "map_display": {
            "statistic": "unthresholded one-sample t; signed colors, clipped at +/-6",
            "mask": "common nonzero coverage across all 54 participants; no color outside coverage",
            "roi": "AAL SPM12 bilateral Frontal_Med_Orb parcels, intersected with common coverage; descriptive vmPFC localization",
            "corrected": "positive-direction permutation max-T, 10000 sign flips, whole-brain FWE p <= .05",
            "slice_centers_mni_mm": [-2, 24, -3.599997043609619],
            "orientation": "neurological: left hemisphere on image left in coronal and axial panels",
        },
        "sources": copied,
    }
    (out / "provenance.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Captured illustrative map from original scientific result: {worker.name}")


if __name__ == "__main__":
    main()
