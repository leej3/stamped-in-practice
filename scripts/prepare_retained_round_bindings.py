#!/usr/bin/env python3
"""Copy exact Git-retained round authorizations into a portable report binding.

The supplied iteration revision is an explicit immutable input. This creates no
authorization and changes no research allocation, source pin, or raw judgment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iteration-repository", type=Path, required=True)
    parser.add_argument("--iteration-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--round", type=int, choices=(2, 3), action="append", required=True)
    args = parser.parse_args()
    revision = subprocess.check_output(["git", "-C", str(args.iteration_repository),
        "rev-parse", args.iteration_commit + "^{commit}"], text=True).strip()
    args.output.mkdir(parents=True, exist_ok=False)
    receipts = []

    def capture(path):
        raw = subprocess.check_output(["git", "-C", str(args.iteration_repository),
            "show", revision + ":" + path])
        destination = args.output / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        ref = {"path": path, "sha256": hashlib.sha256(raw).hexdigest()}
        receipts.append(dict(ref, iteration_commit=revision))
        return ref, json.loads(raw) if path.endswith(".json") else None

    authorization, _ = capture("rounds/round-02/adoption-01/authorization.json")
    adoption, _ = capture("rounds/round-02/adoption-01/adoption.json")
    scope, _ = capture("rounds/round-02/adoption-01/scope.md")
    rows = []
    for number in sorted(set(args.round)):
        ref, binding = capture(f"rounds/round-{number:02}/preparation-01/source-skill-binding.json")
        evidence = [authorization, adoption, scope]
        if number == 3:
            transition, _ = capture("rounds/round-03/preparation-01/binding.json")
            evidence.append(transition)
        rows.append({"round": number,
            "coordinator_source_commit": binding["coordinator_source_commit"],
            "research_guidance_commit": binding["research_guidance_commit"],
            "source_skill_binding": ref, "authorization": evidence})
        values = (binding["comparison_id"], binding["original_allocation_sha256"],
                  binding["research_procedure_sha256"])
        if number == min(args.round):
            identity = values
        elif values != identity:
            raise ValueError("Round bindings do not share original allocation and research seal")
    document = {"schema_version": 1, "comparison_id": identity[0],
        "allocation_sha256": identity[1], "research_procedure_sha256": identity[2], "rounds": rows}
    raw = (json.dumps(document, indent=2) + "\n").encode()
    (args.output / "round-bindings.json").write_bytes(raw)
    (args.output / "retention-receipt.json").write_text(json.dumps({
        "kind": "exact-git-artifact-copy", "iteration_commit": revision,
        "files": receipts, "round_bindings_sha256": hashlib.sha256(raw).hexdigest(),
        "scope": "Reports existing authorization; does not authorize changed research or judgments."
    }, indent=2) + "\n")
    print(json.dumps({"path": str(args.output / "round-bindings.json"),
        "sha256": hashlib.sha256(raw).hexdigest(), "iteration_commit": revision}))


if __name__ == "__main__":
    main()
