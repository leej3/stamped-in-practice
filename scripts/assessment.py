#!/usr/bin/env python3
"""Run the pinned assessment helpers in their recorded Pixi environment."""
import argparse
from contextlib import chdir, nullcontext
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import assessment_procedure as procedure

ROOT = Path(__file__).resolve().parents[1]


def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd)


def runtime_context():
    """Read only the role projection; full seals remain coordinator inputs."""
    if os.environ.get("STAMPED_PROCEDURE") or os.environ.get("STAMPED_PROCEDURE_SHA256"):
        raise SystemExit("Full coordinator procedures are not judge runtime inputs")
    path = os.environ.get("STAMPED_JUDGE_RUNTIME")
    if not path:
        return None
    runtime = procedure.load_judge_runtime(path, os.environ.get("STAMPED_JUDGE_RUNTIME_SHA256"), os.environ)
    procedure.require_equal(procedure.sha256(Path(__file__).read_bytes()),
                            runtime["fixed_files"]["scripts/assessment.py"], "assessment runner source")
    return runtime


def dispatch_directory(frozen):
    """Keep v4 relative helper paths inside its existing judgment workspace."""
    if not frozen or frozen.get("version") != 4:
        return ROOT
    value = os.environ.get("STAMPED_JUDGE_OUTPUT")
    if not value or not Path(value).is_absolute() or not Path(value).is_dir():
        raise SystemExit("Version 4 requires an existing absolute STAMPED_JUDGE_OUTPUT directory")
    output = Path(value).resolve()
    if output == ROOT.resolve():
        raise SystemExit("Version 4 judgment output must be separate from the coordinator root")
    target = os.environ.get("STAMPED_JUDGE_TARGET")
    if target:
        target = Path(target).resolve()
        if output.is_relative_to(target) or target.is_relative_to(output):
            raise SystemExit("Version 4 judgment output must be separate from the assessed target")
    return output


def validate_response_identity(response, frozen):
    """Read-only formal identity checks; leave scientific verdicts to the assessor."""
    if not isinstance(response, dict):
        raise SystemExit("Formal response must be an object")
    for section, expected in frozen["response_identity"].items():
        supplied = response.get(section, {})
        if not isinstance(supplied, dict):
            raise SystemExit("Formal response " + section + " must be an object")
        for key, value in expected.items():
            if key not in supplied:
                raise SystemExit("Formal response missing " + section + "." + key)
            procedure.require_equal(supplied[key], value, "formal response " + section + "." + key)


def response_template(arguments, frozen, command, cwd):
    """Initialize known metadata on the frozen helper's unchanged blank verdicts."""
    parser = argparse.ArgumentParser(description=response_template.__doc__, allow_abbrev=False)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(arguments)
    target = cwd / args.output if args.output else None
    if target and (not target.resolve().is_relative_to(cwd.resolve()) or os.path.lexists(target)):
        raise SystemExit("Formal template output must be a new file inside the judgment workspace")
    result = subprocess.run([*command, "template"], cwd=cwd, capture_output=True, text=True)
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode:
        print(result.stdout, end="")
        raise SystemExit(result.returncode)
    response = json.loads(result.stdout)
    for section, fields in frozen["response_identity"].items():
        response.setdefault(section, {}).update(fields)
    content = json.dumps(response, indent=2) + "\n"
    if target:
        with target.open("x") as stream:
            stream.write(content)
        print("wrote " + str(target))
    else:
        print(content, end="")
    return 0


def captured_replay(arguments, helper, operational=False):
    """Replay documented outputs from a verified complete copy, never from HEAD."""
    import importlib.util
    import signal
    import time
    from delivery_snapshot import materialize_capture, validate_capture

    parser = argparse.ArgumentParser(description=captured_replay.__doc__, allow_abbrev=False)
    parser.add_argument("--path", type=Path, required=True)
    parser.add_argument("--entry", required=True)
    parser.add_argument("--outputs", nargs="+", required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--rtol", type=float, default=1e-6)
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--max-get-gb", type=float, default=5.0)
    parser.add_argument("--in-container")
    args = parser.parse_args(arguments)
    manifest_path = Path(os.environ["STAMPED_DELIVERY_MANIFEST"])
    receipt = json.loads(Path(os.environ["STAMPED_WORKER_STOP_RECEIPT"]).read_bytes())
    identity = validate_capture(manifest_path, receipt["capture"]["sha256"])
    manifest = json.loads(manifest_path.read_bytes())
    original = manifest_path.parent / manifest["workspace"]
    declared = Path(os.environ["STAMPED_JUDGE_TARGET"]) if operational else original
    procedure.require_equal(args.path.resolve(), declared.resolve(), "captured replay source")
    report = {"probe": "fresh-rerun", "source": str(original), "capture": identity["capture"],
              "commit": identity["commit"], "captured_at": identity["captured_at"],
              "scope": "Complete stopped delivery copy; existing environment/cache bytes retained. "
                       "One documented entrypoint, no repair or automatic retrieval; selected outputs only.",
              "entry": args.entry, "outputs": args.outputs, "rtol": args.rtol}
    if operational:
        report["retrieval_scope"] = {
            "adapter_input_retrieval": "none; uses captured inputs",
            "entrypoint_network_byte_limit": None,
            "entrypoint_downloads": "Documented dependency installs/downloads are not byte-metered",
            "max_get_gb": args.max_get_gb,
            "max_get_gb_scope": "Frozen helper-prefetch compatibility parameter; this adapter performs no prefetch",
        }
    def finish(status, reason):
        report.update(status=status, reason=reason)
        validate_capture(manifest_path, identity["capture"]["sha256"])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
        print(json.dumps(report))
        return 0
    observations = [row["path"] for row in manifest.get("declared_artifacts", [])
                    if isinstance(row.get("declaration"), dict) and
                    row["declaration"].get("kind") == "native-session-skill-directory"]
    # Skills installed in the native profile are retained observation evidence,
    # not scientific execution dependencies. A workspace link to one opts it in.
    referenced = set()
    for row in manifest["entries"]:
        if row["path"].startswith("content/workspace/") and row["kind"] == "symlink":
            try:
                target = (manifest_path.parent / row["path"]).resolve()
                referenced.update(prefix for prefix in observations
                                  if target.is_relative_to(manifest_path.parent / prefix))
            except (OSError, RuntimeError):
                pass
    observations = [prefix for prefix in observations if prefix not in referenced]
    def execution_evidence(row):
        return not any(row["path"] == prefix or row["path"].startswith(prefix + "/")
                       for prefix in observations)
    issues = manifest.get("errors", []) + manifest.get("omissions", [])
    report["observation_only_capture_issues"] = [row for row in issues if not execution_evidence(row)]
    if any(execution_evidence(row) for row in issues):
        return finish("not-checked", "Scientific execution capture has explicit omissions or errors; no replay executed.")
    if args.in_container:
        return finish("not-checked", "This bounded adapter does not relocate container bindings.")
    if not args.entry.strip() or any(not value.strip() or Path(value).is_absolute() or
                                   ".." in Path(value).parts for value in args.outputs):
        return finish("not-checked", "Entrypoint and repository-relative generated output patterns are required.")
    if any(execution_evidence(row) for row in manifest.get("git_dependencies", [])):
        return finish("not-checked", "Original external Git pointers are retained as evidence, not relocated for execution.")
    for row in manifest["entries"]:
        if row["kind"] == "symlink" and execution_evidence(row):
            link = manifest_path.parent / row["path"]
            try:
                inside = link.resolve().is_relative_to(manifest_path.parent.resolve())
            except (OSError, RuntimeError):
                inside = False
            if not inside or Path(os.readlink(link)).is_absolute():
                return finish("not-checked", "Original links outside the captured copy cannot be safely replayed without relocation.")
    materialized = materialize_capture(manifest_path, args.workdir)
    clone = Path(materialized["target"])
    report["workdir"] = str(clone)
    # Comparison semantics come from the exact frozen assessor, in its runtime.
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("frozen_fresh_rerun", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    protected = {row["path"] for row in receipt.get("seed_identities", {}).get("supplied_files", [])}
    before = module._collect(clone, args.outputs)
    code_suffixes = {".py", ".sh", ".r", ".m", ".ipynb", ".jl", ".toml", ".lock", ".yaml", ".yml"}
    for path in before:
        selected = clone / path
        if (path in protected or Path(path).parts[0] in ("input", ".git", ".codex", ".entire", ".agents") or
                selected.suffix.lower() in code_suffixes or selected.name in ("Makefile", "Dockerfile") or
                not selected.resolve().is_relative_to(clone.resolve())):
            return finish("not-checked", "Output selection includes supplied inputs, code/configuration, or external content: " + path)
    if not before or any(digest is None for digest in before.values()):
        return finish("not-checked", "No complete generated output payload matches the explicit selection.")
    report["original_output_sha256"] = before
    for path in before:
        (clone / path).unlink()
    report["removed_outputs"] = sorted(before)
    command = ["sh", "-c", args.entry]
    started = time.monotonic()
    with (args.workdir / "replay.stdout").open("xb") as stdout, (args.workdir / "replay.stderr").open("xb") as stderr:
        environment = os.environ.copy()
        if operational:
            environment = procedure.git_config_overlay(procedure.operational_environment(environment),
                                                        {"core.hooksPath": os.devnull})
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
        else:
            environment.update(GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1",
                               GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.hooksPath", GIT_CONFIG_VALUE_0=os.devnull)
        report["replay_git_overlay"] = {"core.hooksPath": os.devnull,
            "reason": "Disable original checkout hooks in the replay copy; captured config bytes unchanged"}
        process = subprocess.Popen(command, cwd=clone, env=environment, stdout=stdout, stderr=stderr,
                                   start_new_session=True)
        try:
            code = process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            code = 124
            report["timed_out"] = True
    report.update(returncode=code, elapsed_seconds=time.monotonic() - started,
                  stdout=str(args.workdir / "replay.stdout"), stderr=str(args.workdir / "replay.stderr"))
    if report.get("timed_out"):
        return finish("not-checked", "Frozen replay time limit reached; evidence retained, replay incomplete.")
    if code:
        return finish("unmet", "Documented entrypoint failed in the complete delivery copy; interpret within the recorded environment scope.")
    after = module._collect(clone, args.outputs)
    identical, close, differing, missing = [], [], [], []
    for path, digest in before.items():
        if after.get(path) is None:
            missing.append(path)
        elif after[path] == digest:
            identical.append(path)
        elif path.endswith(module.TABLE_SUFFIXES) and module._numeric_close(original / path, clone / path, args.rtol):
            close.append(path)
        else:
            differing.append(path)
    report["comparison"] = {"identical": identical, "within_tolerance": close,
                            "differing": differing, "missing_after_rerun": missing}
    if differing or missing:
        return finish("partial" if identical or close else "unmet", "Some selected generated outputs did not reproduce.")
    return finish("met", "All selected generated outputs were recreated within the frozen comparison tolerance.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "probes", "response", "validate", "template", "fresh-rerun"))
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    remaining = args.arguments
    pin_path = Path(os.environ.get("STAMPED_ASSESSMENT_PIN", ROOT / "assessment-version.json"))
    pin = json.loads(pin_path.read_text())
    frozen = runtime_context()
    if frozen:
        procedure.require_equal(pin, frozen["assessment"], "assessment runner pin")
    operational = bool(frozen and frozen.get("version") == 4)
    dispatch_cwd = dispatch_directory(frozen)
    formal_response = bool(frozen and "response_identity" in frozen)
    if args.action == "template" and not formal_response:
        parser.error("template requires a projected captured-delivery judge runtime")
    validation = (remaining if args.action == "validate" else remaining[1:]
                  if args.action == "response" and remaining[:1] == ["validate"] else None)
    if formal_response and validation is not None and not any(flag in validation for flag in ("--help", "-h")):
        check = argparse.ArgumentParser(allow_abbrev=False)
        check.add_argument("response", type=Path)
        response_path = check.parse_args(validation).response
        validate_response_identity(json.loads((dispatch_cwd / response_path).read_bytes()), frozen)
    source = Path(os.environ.get("STAMPED_ASSESSMENT_SOURCE", ROOT / "assessment"))
    if operational:
        source = source.resolve()
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
    if operational:
        manifest = manifest.resolve()
    subprocess.run(["pixi", "install", "--locked", "--manifest-path", manifest], check=True)
    if args.action == "check":
        if remaining:
            parser.error("check takes no additional arguments")
        print(json.dumps(pin, indent=2))
        return
    scripts = source / "skills" / "assess-alignment-with-stamped-principles" / "scripts"
    if args.action in ("response", "validate", "template"):
        helper = source / "skills" / "stamped-conventions" / "scripts" / "encode_response.py"
        if args.action == "validate":
            remaining.insert(0, "validate")
    else:
        helper = scripts / {"probes": "run_probes.py", "fresh-rerun": "fresh_rerun.py"}[args.action]
    if args.action == "template":
        raise SystemExit(response_template(remaining, frozen,
            ["pixi", "run", "--locked", "--manifest-path", manifest, "python", helper], dispatch_cwd))
    if frozen and args.action == "fresh-rerun":
        target = Path(os.environ["STAMPED_JUDGE_TARGET"])
        if procedure.is_neutral(frozen):
            # Validate relative replay paths in the same directory the adapter
            # will use, even when the runner was invoked from the target.
            with chdir(dispatch_cwd) if operational else nullcontext():
                remaining = procedure.replay_arguments(frozen, remaining, target,
                                                       Path(os.environ["STAMPED_JUDGE_OUTPUT"]))
            result = subprocess.run(["pixi", "run", "--locked", "--manifest-path", manifest,
                "python", Path(__file__).resolve(), "--captured-replay", str(helper),
                procedure.sha256(helper.read_bytes()), *remaining], cwd=dispatch_cwd)
            raise SystemExit(result.returncode)
        procedure.require_equal(procedure.git(target, "rev-parse", "HEAD"),
                                os.environ["STAMPED_JUDGE_COMMIT"], "replay target commit")
        remaining = procedure.replay_arguments(frozen, remaining, target,
                                               Path(os.environ["STAMPED_JUDGE_OUTPUT"]))
    result = subprocess.run(["pixi", "run", "--locked", "--manifest-path", manifest,
                             "python", helper, *remaining], cwd=dispatch_cwd)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--captured-replay"]:
        frozen = runtime_context()
        if frozen is None:
            raise SystemExit("Captured replay requires a judge runtime projection")
        helper = Path(sys.argv[2])
        procedure.require_equal(procedure.sha256(helper.read_bytes()), sys.argv[3], "frozen replay helper")
        raise SystemExit(captured_replay(sys.argv[4:], helper, frozen.get("version") == 4))
    main()
