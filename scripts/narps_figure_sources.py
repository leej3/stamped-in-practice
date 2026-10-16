#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Bind figure inputs to original scientific commits in retained research objects."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SYNTHESIS = ROOT / "iterations/narps-v1/synthesis"
EXPERIMENT = ROOT / "experiments/narps-poster"
REPOSITORY = "https://github.com/leej3/stamped-in-practice"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def verify_annex_payload(path: Path, key: str) -> None:
    """Check bytes, not merely a clean Git pointer, for supported hash backends."""
    match = re.fullmatch(r"(SHA256|SHA512)(E?)-s([0-9]+)--([0-9a-f]+)(.*)", key)
    if not match:
        raise ValueError(f"Unsupported annex content key; cannot verify payload: {key}")
    backend, extension_backend, size, expected, suffix = match.groups()
    algorithm = backend.lower()
    expected_length = hashlib.new(algorithm).digest_size * 2
    if len(expected) != expected_length or (suffix and (not extension_backend or not suffix.startswith("."))):
        raise ValueError(f"Invalid annex content key: {key}")
    payload = path.read_bytes()
    if len(payload) != int(size) or hashlib.new(algorithm, payload).hexdigest() != expected:
        raise ValueError(f"Annex payload does not match its content-addressed key: {path}")


def verified_retained_file(worker: Path, relative: str):
    """Require a committed, clean file and validate the retained bytes."""
    path = worker / relative
    if not path.is_file():
        raise FileNotFoundError(f"Retrieve the selected retained input first: {path}")
    if git(worker, "status", "--porcelain", "--", relative):
        raise ValueError(f"Uncommitted source: {path}")
    object_id = git(worker, "rev-parse", f"HEAD:{relative}")
    committed = subprocess.check_output(["git", "-C", str(worker), "cat-file", "blob", object_id])
    if path.is_symlink():
        if str(path.readlink()).encode() != committed:
            raise ValueError(f"Annex pointer differs from its committed Git object: {path}")
        verify_annex_payload(path, path.readlink().name)
    elif path.read_bytes() != committed:
        raise ValueError(f"Retained bytes differ from their committed Git object: {path}")
    return path, object_id


def add_arguments(parser):
    parser.add_argument("--results-root", type=Path, default=ROOT / "studies/narps/results")
    parser.add_argument("--index", type=Path, default=SYNTHESIS / "index.json")
    parser.add_argument("--allocation", type=Path, default=ROOT / "iterations/narps-v1/allocation.json")


class Sources:
    """Read retained files while keeping scientific and retention identities separate."""

    def __init__(self, args):
        self.results_root = args.results_root.resolve()
        self.index = {r["run_id"]: r for r in json.loads(args.index.read_text())["runs"]}
        self.allocation = {
            r["run"]: r["condition"]
            for round_ in json.loads(args.allocation.read_text())["rounds"]
            for r in round_["launch_order"]
        }
        self.records = {}
        self.binding = {
            "index_sha256": sha256(args.index),
            "allocation_sha256": sha256(args.allocation),
        }

    def worker(self, run: str) -> Path:
        return self.results_root / run

    def read(self, worker: Path, relative: str) -> Path:
        path, retained_object = verified_retained_file(worker, relative)
        row = self.index[worker.name]
        scientific = row["result_commit"]
        if not scientific or row["worker_completion"] != "completed":
            raise ValueError(f"No completed scientific result in the index: {worker.name}")
        available = subprocess.run(
            ["git", "-C", str(worker), "cat-file", "-e", f"{scientific}^{{commit}}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        if available.returncode:
            raise ValueError(
                f"Original scientific commit is not available in {worker}. "
                f"Retrieve it before capture: git -C {worker} fetch origin {scientific}"
            )
        expected_object = git(worker, "rev-parse", f"{scientific}:{relative}")
        if expected_object != retained_object:
            raise ValueError(f"Retained file differs from original scientific result: {path}")
        branch = f"codex/{worker.name}"
        record = {
            "sha256": sha256(path), "bytes": path.stat().st_size,
            "repository": REPOSITORY, "branch": branch,
            "revision": scientific, "scientific_result_revision": scientific,
            "retention_revision": git(worker, "rev-parse", "HEAD"),
            "indexed_retention_revision": row.get("retention_commit"),
            "git_object": expected_object, "path": relative,
            "benchmark_path": f"studies/narps/results/{worker.name}/{relative}",
            "url": f"{REPOSITORY}/blob/{branch}/{relative}",
        }
        if path.is_symlink():
            record["annex_key"] = path.readlink().name
        self.records[f"{worker.name}/{relative}"] = record
        return path

    def assignment(self, worker: Path):
        relative = "coordinator/retention-01/indexable/launch/native/condition-assignment.json"
        path, object_id = verified_retained_file(worker, relative)
        data = json.loads(path.read_text())
        if data["condition"] != self.allocation[worker.name]:
            raise ValueError(f"Retained assignment differs from registered allocation: {worker.name}")
        branch = f"codex/{worker.name}-retained"
        return data, {
            "sha256": sha256(path),
            "repository": REPOSITORY, "branch": branch,
            "git_object": object_id,
            "benchmark_path": f"studies/narps/results/{worker.name}/{relative}",
            "retention_revision": git(worker, "rev-parse", "HEAD"),
            "url": f"{REPOSITORY}/blob/{branch}/{relative}",
        }
