"""Compare a fresh group-analysis replay with the accepted saved outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("expected", type=Path)
    parser.add_argument("replayed", type=Path)
    args = parser.parse_args()

    checks: dict[str, object] = {}
    for name in ("group_t.nii.gz", "p_fwe_maxT.nii.gz", "mean_effect.nii.gz"):
        expected = nib.load(str(args.expected / name))
        replayed = nib.load(str(args.replayed / name))
        same_geometry = expected.shape == replayed.shape and np.array_equal(expected.affine, replayed.affine)
        same_values = same_geometry and np.array_equal(
            np.asarray(expected.dataobj), np.asarray(replayed.dataobj), equal_nan=True
        )
        checks[name] = {"same_geometry": bool(same_geometry), "same_values": bool(same_values)}
        if not same_values:
            raise AssertionError(f"Replay differs from accepted NIfTI output: {name}")

    for name in ("null_max_t.tsv", "vmPFC_subject_effects.tsv"):
        checks[name] = {"same_values": bool(pd.read_csv(args.expected / name, sep="\t").equals(
            pd.read_csv(args.replayed / name, sep="\t")
        ))}
        if not checks[name]["same_values"]:
            raise AssertionError(f"Replay differs from accepted table: {name}")

    expected_summary = json.loads((args.expected / "summary.json").read_text())
    replayed_summary = json.loads((args.replayed / "summary.json").read_text())
    expected_summary.pop("runtime_seconds", None)
    replayed_summary.pop("runtime_seconds", None)
    checks["summary.json"] = {"same_values_except_runtime": expected_summary == replayed_summary}
    if not checks["summary.json"]["same_values_except_runtime"]:
        raise AssertionError("Replay summary differs from accepted summary")

    for name in ("vmPFC_effects.png", "whole_brain_fwe.png"):
        same_bytes = (args.expected / name).read_bytes() == (args.replayed / name).read_bytes()
        checks[name] = {"same_bytes": same_bytes}
        if not same_bytes:
            raise AssertionError(f"Replay differs from accepted figure: {name}")

    print(json.dumps({"status": "passed", "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
