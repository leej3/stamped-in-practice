#!/usr/bin/env python3
"""Run the pinned assessment helpers in their recorded Pixi environment."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

import assessment_procedure as procedure

ROOT = Path(__file__).resolve().parents[1]


def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "probes", "response", "validate", "fresh-rerun"))
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    remaining = args.arguments
    pin_path = Path(os.environ.get("STAMPED_ASSESSMENT_PIN", ROOT / "assessment-version.json"))
    pin = json.loads(pin_path.read_text())
    frozen_path = os.environ.get("STAMPED_PROCEDURE")
    frozen = None
    if frozen_path:
        frozen = procedure.load_procedure(frozen_path, os.environ.get("STAMPED_PROCEDURE_SHA256"))
        procedure.require_equal(pin, frozen["assessment"], "assessment runner pin")
        procedure.require_equal(procedure.sha256(Path(__file__).read_bytes()),
                                frozen["fixed_files"]["scripts/assessment.py"], "assessment runner source")
    source = Path(os.environ.get("STAMPED_ASSESSMENT_SOURCE", ROOT / "assessment"))
    if git("rev-parse", "HEAD", cwd=source).decode().strip() != pin["source_commit"]:
        raise SystemExit("Assessment checkout differs from the frozen version")
    if git("status", "--porcelain", cwd=source).strip():
        raise SystemExit("Assessment checkout has local changes")
    if not procedure.assessment_modules_match(git("submodule", "status", "--recursive", cwd=source)):
        raise SystemExit("Assessment submodules are not at their recorded revisions")
    revision = pin["environment_commit"]
    repository = pin.get("environment_repository", "origin")
    if not isinstance(repository, str) or not repository.strip():
        raise SystemExit("Assessment environment_repository must name a Git repository or remote")
    if subprocess.run(["git", "cat-file", "-e", revision], cwd=ROOT, capture_output=True).returncode:
        subprocess.run(["git", "fetch", "--no-tags", "--depth", "1", repository, revision],
                       cwd=ROOT, check=True)
    runtime = ROOT / ".pixi" / "assessment-runtime" / revision
    runtime.mkdir(parents=True, exist_ok=True)
    for name in ("pixi.toml", "pixi.lock"):
        content = git("show", f"{revision}:{name}")
        if hashlib.sha256(content).hexdigest() != pin["sha256"][name]:
            raise SystemExit(f"Frozen {name} hash differs")
        target = runtime / name
        if target.exists() and target.read_bytes() != content:
            raise SystemExit(f"Recorded environment was changed locally: {target}")
        target.write_bytes(content)
    manifest = runtime / "pixi.toml"
    subprocess.run(["pixi", "install", "--locked", "--manifest-path", manifest], check=True)
    if args.action == "check":
        if remaining:
            parser.error("check takes no additional arguments")
        print(json.dumps(pin, indent=2))
        return
    scripts = source / "skills" / "assess-alignment-with-stamped-principles" / "scripts"
    if args.action in ("response", "validate"):
        helper = source / "skills" / "stamped-conventions" / "scripts" / "encode_response.py"
        if args.action == "validate":
            remaining.insert(0, "validate")
    else:
        helper = scripts / {"probes": "run_probes.py", "fresh-rerun": "fresh_rerun.py"}[args.action]
    if frozen and args.action == "fresh-rerun":
        target = Path(os.environ["STAMPED_JUDGE_TARGET"])
        procedure.require_equal(procedure.git(target, "rev-parse", "HEAD"),
                                os.environ["STAMPED_JUDGE_COMMIT"], "replay target commit")
        remaining = procedure.replay_arguments(frozen, remaining, target,
                                               Path(os.environ["STAMPED_JUDGE_OUTPUT"]))
    result = subprocess.run(["pixi", "run", "--locked", "--manifest-path", manifest,
                             "python", helper, *remaining], cwd=ROOT)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
