#!/usr/bin/env python3
"""Run explicitly requested resource checks and retain a receipt for every outcome."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import time


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate(requirements, host):
    """Reject ambiguous plans before executing any command."""
    for name, value, keys in (
        ("requirements", requirements, {"schema_version", "requirements"}),
        ("host config", host, {"schema_version", "checks"}),
    ):
        if (not isinstance(value, dict) or set(value) != keys
                or type(value["schema_version"]) is not int or value["schema_version"] != 1):
            raise ValueError(f"{name} must have schema_version 1 and {sorted(keys - {'schema_version'})}")
    rows = requirements["requirements"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("requirements must be a nonempty list")
    if not isinstance(host["checks"], dict):
        raise ValueError("host checks must be an object keyed by requirement ID")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "description", "source"}:
            raise ValueError("Each requirement needs exactly id, description and source")
        if not all(isinstance(value, str) and value.strip() for value in row.values()):
            raise ValueError("Requirement fields must be nonempty strings")
        identifier = row["id"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", identifier) or identifier in seen:
            raise ValueError(f"Invalid or duplicate requirement ID: {identifier}")
        seen.add(identifier)
        if identifier not in host["checks"]:
            continue
        check = host["checks"][identifier]
        if (not isinstance(check, dict) or not {"argv", "cwd"} <= set(check)
                or set(check) - {"argv", "cwd", "timeout_seconds", "artifacts"}):
            raise ValueError(f"{identifier}: check needs argv and cwd; optional timeout_seconds and artifacts")
        argv = check["argv"]
        if (not isinstance(argv, list) or not argv
                or not all(isinstance(arg, str) and "\0" not in arg for arg in argv)
                or not argv[0]):
            raise ValueError(f"{identifier}: argv must be a nonempty string array")
        if not isinstance(check["cwd"], str) or not check["cwd"] or "\0" in check["cwd"]:
            raise ValueError(f"{identifier}: cwd must be a nonempty path")
        timeout = check.get("timeout_seconds", 60)
        if (type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0):
            raise ValueError(f"{identifier}: timeout_seconds must be positive and finite")
        artifacts = check.get("artifacts", [])
        if not isinstance(artifacts, list):
            raise ValueError(f"{identifier}: artifacts must be an array of relative file paths")
        for artifact in artifacts:
            if (not isinstance(artifact, str) or not artifact or "\0" in artifact
                    or Path(artifact).is_absolute() or ".." in Path(artifact).parts
                    or artifact == "."):
                raise ValueError(f"{identifier}: artifact paths must stay within the check's artifact directory")
        if len(artifacts) != len(set(artifacts)):
            raise ValueError(f"{identifier}: duplicate artifact paths")


def validate_requirements(requirements):
    """Validate a public requirements document without accessing host settings."""
    validate(requirements, {"schema_version": 1, "checks": {}})


def stop(process):
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        process.kill()
    process.wait()


def execute(requirement, check, config_dir, evidence):
    started = time.monotonic()
    receipt = dict(requirement, started_at=timestamp(), status="missing", argv=None,
                   cwd=None, returncode=None, artifacts=[])
    directory = evidence / requirement["id"]
    directory.mkdir(mode=0o700)
    if check is None:
        receipt["error"] = "No host check configured for this requirement"
    else:
        cwd = Path(check["cwd"]).expanduser()
        cwd = (config_dir / cwd).resolve() if not cwd.is_absolute() else cwd.resolve()
        artifacts = directory / "artifacts"
        artifacts.mkdir(mode=0o700)
        timeout = check.get("timeout_seconds", 60)
        receipt.update(argv=check["argv"], cwd=str(cwd), timeout_seconds=timeout,
                       artifact_directory=str(artifacts))
        environment = dict(os.environ, READINESS_ARTIFACT_DIR=str(artifacts))
        with (directory / "stdout.txt").open("wb") as stdout, (directory / "stderr.txt").open("wb") as stderr:
            try:
                process = subprocess.Popen(check["argv"], cwd=cwd, env=environment,
                                           stdout=stdout, stderr=stderr,
                                           start_new_session=os.name == "posix")
                try:
                    receipt["returncode"] = process.wait(timeout=timeout)
                    receipt["status"] = "passed" if process.returncode == 0 else "failed"
                except subprocess.TimeoutExpired:
                    stop(process)
                    receipt.update(status="timeout", returncode=process.returncode,
                                   error=f"Check exceeded {timeout} seconds")
                except BaseException:
                    stop(process)
                    raise
            except OSError as error:
                receipt.update(status="error", error=str(error))
        for name in ("stdout.txt", "stderr.txt"):
            path = directory / name
            receipt[name.removesuffix(".txt")] = {
                "path": str(path.relative_to(evidence)), "sha256": digest(path),
                "bytes": path.stat().st_size,
            }
        for name in check.get("artifacts", []):
            path = artifacts / name
            item = {"path": str(path.relative_to(evidence))}
            try:
                if not path.resolve().is_relative_to(artifacts) or not path.is_file():
                    raise ValueError("Artifact missing, not a file, or resolves outside artifact directory")
                item.update(sha256=digest(path), bytes=path.stat().st_size, status="retained")
            except (OSError, ValueError) as error:
                item.update(status="missing", error=str(error))
                if receipt["status"] == "passed":
                    receipt["status"] = "failed"
            receipt["artifacts"].append(item)
    receipt.update(finished_at=timestamp(), elapsed_seconds=time.monotonic() - started)
    write_json(directory / "receipt.json", receipt)
    return receipt


def run(requirements_path, host_path, evidence):
    requirements_path = requirements_path.expanduser().resolve()
    host_path = host_path.expanduser().resolve()
    evidence = evidence.expanduser().resolve()
    content = requirements_path.read_bytes()
    requirements = json.loads(content)
    host = json.loads(host_path.read_bytes()) if host_path.exists() else {"schema_version": 1, "checks": {}}
    validate(requirements, host)
    evidence.mkdir(parents=True, mode=0o700, exist_ok=False)
    (evidence / "requirements.json").write_bytes(content)
    started = time.monotonic()
    report = {"schema_version": 1, "started_at": timestamp(), "ready": False,
              "complete": False, "requirements_source": str(requirements_path),
              "requirements_sha256": hashlib.sha256(content).hexdigest(),
              "host_config": str(host_path), "checks": []}
    write_json(evidence / "result.json", report)
    for requirement in requirements["requirements"]:
        report["checks"].append(execute(requirement, host["checks"].get(requirement["id"]),
                                        host_path.parent, evidence))
        write_json(evidence / "result.json", report)
    report.update(ready=all(row["status"] == "passed" for row in report["checks"]),
                  complete=True, finished_at=timestamp(), elapsed_seconds=time.monotonic() - started,
                  unmet_requirements=[row["id"] for row in report["checks"] if row["status"] != "passed"])
    write_json(evidence / "result.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", type=Path, required=True,
                        help="Explicit capabilities selected from the user's instructions")
    parser.add_argument("--host-config", type=Path, default=Path.home() /
                        ".config" / Path(__file__).resolve().parents[1].name / "readiness.json")
    parser.add_argument("--evidence", type=Path, required=True, help="New directory for this attempt")
    args = parser.parse_args()
    try:
        report = run(args.requirements, args.host_config, args.evidence)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Readiness configuration/evidence error: {error}\n")
    print(json.dumps({"ready": report["ready"], "unmet_requirements": report["unmet_requirements"],
                      "receipt": str(args.evidence.expanduser().resolve() / "result.json")}))
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
