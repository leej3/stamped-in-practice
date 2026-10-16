#!/usr/bin/env python3
"""Verify/unpack retained inputs and rerun reporting with all admission gates.

This runs only deterministic reporting, never research, judges, or replay. A
nonzero reporter status and every output are retained, not silently treated as
a successful result.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from package_retained_reporting import read, sha, unpack, verify_package

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--archive-sha256", required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--aggregator", type=Path, default=ROOT / "scripts/aggregate_comparison.py")
    parser.add_argument("--assessor", type=Path, default=ROOT / "assessment")
    parser.add_argument("--source-repository", type=Path, default=ROOT)
    parser.add_argument("--round-bindings", type=Path)
    parser.add_argument("--round-bindings-sha256")
    args = parser.parse_args()
    if bool(args.round_bindings) != bool(args.round_bindings_sha256):
        parser.error("Round binding path and independent digest must be supplied together")
    if args.output.exists():
        parser.error("--output must not exist")
    verified = unpack(args.archive, args.archive_sha256, args.scratch)
    scratch = args.scratch.resolve()
    snapshot = read(scratch / "snapshot.json")
    original = scratch / "original/index.json"
    if sha(original.read_bytes()) != snapshot["index"]["sha256"]:
        raise ValueError("Retained original index does not match its closed snapshot")
    registration = scratch / "registration"
    command = [sys.executable, str(args.aggregator.resolve()),
        "--allocation", str(registration / "original-allocation.json"),
        "--registration", str(registration / "original-registration.json"),
        "--research-procedure", str(registration / "original-procedure.json"),
        "--assessment-procedure-sha256", snapshot["assessment_procedure_sha256"],
        "--assessor", str(args.assessor.resolve()),
        "--assessment-pin", str(registration / "assessment-version.json"),
        "--index", str(scratch / "index.json"),
        "--source-manifest", str(scratch / "source-manifest.json"),
        "--source-repository", str(args.source_repository.resolve()),
        "--output", str(args.output.resolve())]
    if args.round_bindings:
        command.extend(["--round-bindings", str(args.round_bindings.resolve()),
                        "--round-bindings-sha256", args.round_bindings_sha256])
    receipts = args.output.with_name(args.output.name + "-execution")
    receipts.mkdir(parents=True, exist_ok=False)
    (receipts / "command.json").write_text(json.dumps({"argv": command,
        "archive_sha256": args.archive_sha256, "verified_inputs": verified,
        "aggregator_sha256": sha(args.aggregator.read_bytes()),
        "runner_sha256": sha(Path(__file__).read_bytes())}, indent=2) + "\n")
    with (receipts / "stdout.txt").open("xb") as stdout, (receipts / "stderr.txt").open("xb") as stderr:
        result = subprocess.run(command, stdout=stdout, stderr=stderr)
    unchanged = verify_package(scratch)
    record = {"exit_code": result.returncode, "inputs_still_verified": unchanged,
        "scope": "Deterministic reporting only; all original evidence and admission failures retained.",
        "output": str(args.output.resolve())}
    (receipts / "result.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
