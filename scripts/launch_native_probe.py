#!/usr/bin/env python3
"""Launch one fresh research worker or independent judge with retained evidence."""
import argparse
import hashlib
import json
import os
import re
import signal
import shutil
import tempfile
import subprocess
import sys
import threading
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from study_seed import (audit_seed, research_prompt, NEUTRAL_PROTOCOL,
                        audit_neutral_seed, neutral_research_prompt)
from research_conditions import CONDITION_CHOICES, RESEARCH_SKILLS, canonical_condition
import assessment_procedure as procedure
import judge_workspace
from worker_end_state import save_worker_end_state, validate_retained_artifacts

STUDY_SKILLS = ("assess-alignment-with-stamped-principles",) + RESEARCH_SKILLS
JUDGE_SKILLS = {"assess-alignment-with-stamped-principles", "stamped-conventions"}


def selected_skills(role, condition):
    if role == "judge":
        return JUDGE_SKILLS
    return set(RESEARCH_SKILLS) if canonical_condition(condition) == "stamped-explicit" else set()


def check_assessment(source, expected_pin):
    """Check external coordinator sources, never a worker-supplied assessor."""
    pin = json.loads(expected_pin.read_text())
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"])
    if head != pin["source_commit"] or dirty:
        raise SystemExit("Judge assessment source is changed or at the wrong revision")
    modules = subprocess.check_output(["git", "-C", str(source), "submodule", "status", "--recursive"])
    if not procedure.assessment_modules_match(modules):
        raise SystemExit("Judge assessment dependencies differ from their recorded revisions")
    if any(not (source / "skills" / name / "SKILL.md").is_file() for name in JUDGE_SKILLS):
        raise SystemExit("Frozen assessment skill entrypoint is missing")
    return pin


def launch_profile(prepared_profile, assessment_source=None):
    """Isolate each session's installs/history; reuse only host auth and trust.

    Keep host authentication links outside retained evidence. The copied public
    config carries existing exact-path hook approvals; no new trust is granted.
    """
    role = "judge" if assessment_source else "research"
    profile = Path(tempfile.mkdtemp(prefix="stamped-" + role + "-", dir=prepared_profile.parent))
    shutil.copyfile(prepared_profile / "config.toml", profile / "config.toml")
    (profile / "config.toml").chmod(0o600)
    auth = prepared_profile / "auth.json"
    if auth.exists():
        (profile / "auth.json").symlink_to(auth.resolve())
    cache = prepared_profile / "models_cache.json"
    if cache.is_file():
        shutil.copy2(cache, profile / "models_cache.json")
    skills = profile / "skills"
    skills.mkdir()
    if assessment_source:
        for name in sorted(JUDGE_SKILLS):
            (skills / name).symlink_to(assessment_source.resolve() / "skills" / name)
    return profile


def judge_profile(prepared_profile, assessment_source):
    return launch_profile(prepared_profile, assessment_source)


def skill_catalog(preview):
    """Read the native developer catalog, expanding its per-block path aliases."""
    text = preview.decode()
    try:
        messages = json.loads(text)
    except json.JSONDecodeError:
        blocks = [text]  # Plain-text previews from older runtimes/fixtures.
    else:
        if not isinstance(messages, list) or not all(isinstance(message, dict) for message in messages):
            raise SystemExit("Unsupported native prompt preview format")
        blocks = []
        for message in messages:
            if message.get("role") == "developer":
                for item in message.get("content", []):
                    blocks += re.findall(r"<skills_instructions>(.*?)</skills_instructions>",
                                         item.get("text", ""), re.DOTALL)
        if not blocks:
            raise SystemExit("Native preview lacks an inspectable skill catalog")
    catalog = []
    for block in blocks:
        roots = dict(re.findall(r"^- `([^`]+)` = `([^`]+)`\s*$", block, re.MULTILINE))
        entries = re.findall(r"^- ([\w:-]+): .+ \(file: (.+)\)\s*$", block, re.MULTILINE)
        declared = [line for line in block.split("### Available skills")[-1].splitlines()
                    if line.startswith("- ") and not line.startswith("- `")]
        if len(entries) != len(declared):
            raise SystemExit("Unparsed advertised skill entry in native preview")
        for name, raw in entries:
            path = Path(raw)
            if not path.is_absolute() and path.parts and path.parts[0] in roots:
                path = Path(roots[path.parts[0]]).joinpath(*path.parts[1:])
            if not path.is_absolute():
                raise SystemExit("Unresolved advertised skill path: " + raw)
            item = {"name": name, "path": str(path.resolve())}
            if path.is_file():
                item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            catalog.append(item)
    return catalog


def host_skill_paths(prepared_profile):
    """Refresh exclusions; an old public profile may predate a host install."""
    roots = (Path.home() / ".agents/skills", Path.home() / ".codex/skills",
             Path("/etc/codex/skills"), prepared_profile / "skills")
    return {path for root in roots for path in root.glob("*/SKILL.md")}


def skill_observations(checkout, profile):
    """Inventory installed entrypoints; installation does not establish use."""
    files = []
    for root in (checkout / ".agents/skills", checkout / ".codex/skills", profile / "skills"):
        # Include normal nested installs plus top-level symlinked skill folders.
        for path in sorted(set(root.rglob("SKILL.md")) | set(root.glob("*/SKILL.md"))):
            if path.is_file():
                files.append({"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return {
        "status": "not-reviewed",
        "evidence": {"events": "events.jsonl", "initial_catalog": "prompt-preflight.json"},
        "installed_entrypoints": files,
        "queries": None, "candidates": None, "selection_rationale": None,
        "source_revisions": None, "installation_cost_and_outcome": None,
        "loaded_instructions": None, "application_evidence": None,
    }


def wait_for_worker(process, output, hard_limit, review_after):
    """A review notification does not terminate useful work; limits are opt-in."""
    started = time.monotonic()
    deadline = started + hard_limit if hard_limit else None
    review = started + review_after if review_after else None
    while True:
        now = time.monotonic()
        pending = [t for t in (deadline, review) if t is not None]
        timeout = max(0, min(pending) - now) if pending else None
        try:
            process.wait(timeout=timeout)
            return False
        except subprocess.TimeoutExpired:
            now = time.monotonic()
            if review is not None and now >= review:
                receipt = {"event": "review_due", "elapsed_seconds": now - started,
                           "pid": process.pid, "terminated": False}
                (output / "review.json").write_text(json.dumps(receipt, indent=2) + "\n")
                print(json.dumps(receipt), file=sys.stderr, flush=True)
                review = None
            if deadline is not None and now >= deadline:
                return True


def signal_worker_group(process, signum):
    """Reap an exited leader but still signal any surviving group members."""
    process.poll()
    try:
        os.killpg(process.pid, signum)
    except ProcessLookupError:
        pass
    except PermissionError:
        # macOS can report EPERM for a group containing only its zombie leader.
        # The leader may have exited just after poll(); reap and retry once.
        # Do not suppress denial for a live leader or a still-existing group.
        if process.poll() is None:
            raise
        try:
            os.killpg(process.pid, signum)
        except ProcessLookupError:
            pass


def terminate_worker_group(process):
    """Stop a timed-out/interrupted process group before observing its state."""
    signal_worker_group(process, signal.SIGTERM)
    time.sleep(5)
    # The leader may exit before descendants stop writing artifacts.
    signal_worker_group(process, signal.SIGKILL)
    process.wait()


def wait_and_capture_worker(process, prompt, output, checkout, record, role,
                            hard_limit, review_after, delivery_seed=None, declared_artifacts=None):
    """Retain research state immediately after stop, even on a failed worker."""
    started = time.monotonic()
    timed_out = False
    reason = "exited"
    try:
        try:
            process.stdin.write(prompt)
            process.stdin.close()
        except BrokenPipeError:
            # A worker can exit before consuming the prompt; still retain it.
            pass
        timed_out = wait_for_worker(process, output, hard_limit, review_after)
        if timed_out:
            reason = "timeout"
            terminate_worker_group(process)
    except BaseException:
        reason = "launcher-interrupted"
        if process.poll() is None:
            terminate_worker_group(process)
        raise
    finally:
        record.update({"finished_at": datetime.now(timezone.utc).isoformat(),
                       "elapsed_seconds": time.monotonic() - started,
                       "timed_out": timed_out, "returncode": process.returncode,
                       "limitation": "Detached descendants outside the process group are not forcibly contained."})
        if role == "research":
            worker = {"pid": process.pid, "returncode": process.returncode,
                      "timed_out": timed_out, "stop_reason": reason,
                      "stopped_at": record["finished_at"]}
            if delivery_seed is None:
                record["worker_end_state"] = save_worker_end_state(checkout, output, worker)
            else:
                from delivery_snapshot import save_delivery
                try:
                    record["worker_end_state"] = save_delivery(
                        checkout, output, worker, delivery_seed, declared_artifacts)
                except (OSError, ValueError) as error:
                    # Loss of the source still belongs to this stopped attempt.
                    failure = {"schema_version": 2, "kind": "worker-end-state",
                               "capture_status": "failed", "worker": worker, "error": str(error)}
                    (output / "worker-end-state-failure.json").write_text(json.dumps(failure, indent=2) + "\n")
                    record["worker_end_state"] = {"path": "worker-end-state-failure.json",
                                                  "capture_status": "failed", "error": str(error)}
        # Save this before stream joins, session parsing or skill inventory fail.
        (output / "result.json").write_text(json.dumps(record, indent=2) + "\n")
    return timed_out


def judge_environment(environment, args, session_checkout, profile, workspace, frozen):
    """Replace inherited role metadata with this judge's explicit bindings."""
    environment = {key: value for key, value in environment.items() if not key.startswith("STAMPED_")}
    neutral = args.protocol == NEUTRAL_PROTOCOL
    operational = bool(frozen and frozen["version"] == 4)
    environment.update(GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
    if operational:
        environment = procedure.operational_environment(environment)
    environment["STAMPED_JUDGE_OUTPUT"] = str(session_checkout)
    environment["STAMPED_JUDGE_TARGET"] = str(args.checkout.resolve())
    environment["STAMPED_ASSESSMENT_RUNNER"] = str(Path(__file__).resolve().with_name("assessment.py"))
    environment["STAMPED_ASSESSMENT_PYTHON"] = sys.executable
    environment["STAMPED_ASSESSMENT_SOURCE"] = str(args.assessment_source.resolve())
    environment["STAMPED_ASSESSMENT_PIN"] = str(args.assessment_pin.resolve())
    if neutral:
        environment["STAMPED_DELIVERY_MANIFEST"] = str(
            (args.canonical_capture if operational else args.delivery_capture).resolve())
        if operational:
            environment["STAMPED_OPERATIONAL_MANIFEST"] = str(args.delivery_capture.resolve())
            environment["STAMPED_SCIENTIFIC_JUDGMENT_VALIDATOR"] = str(
                Path(__file__).resolve().with_name("scientific_judgment.py"))
        environment["STAMPED_WORKER_STOP_RECEIPT"] = str(args.worker_end_state.resolve())
        environment["STAMPED_ASSESSMENT_VERSION"] = str(args.assessment_pin.resolve())
    if frozen:
        environment["STAMPED_WORKER_STOP_RECEIPT"] = str(args.worker_end_state.resolve())
        environment["STAMPED_JUDGE_COMMIT"] = (workspace["target_commit"] or "" if neutral else
                                               procedure.git(args.checkout, "rev-parse", "HEAD"))
        # Keep the role-facing pin beside the projection, away from seal records.
        pin_path = profile / "assessment-version.json"
        environment["STAMPED_ASSESSMENT_PIN"] = str(pin_path)
        if neutral:
            environment["STAMPED_ASSESSMENT_VERSION"] = str(pin_path)
        runtime = procedure.judge_runtime_projection(frozen, environment)
        pin_path.write_text(json.dumps(runtime["assessment"], indent=2) + "\n")
        path = profile / "judge-runtime.json"
        content = (json.dumps(runtime, indent=2, sort_keys=True) + "\n").encode()
        path.write_bytes(content)
        environment["STAMPED_JUDGE_RUNTIME"] = str(path)
        environment["STAMPED_JUDGE_RUNTIME_SHA256"] = procedure.sha256(content)
    return environment


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--judge-workspace", type=Path,
                        help="Prepared independent judge session/output repository")
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--seconds", type=int, default=0,
                        help="Explicit hard limit; 0 (default) waits for completion")
    parser.add_argument("--review-seconds", type=int, default=5400,
                        help="Emit a progress-review receipt without stopping; 0 disables")
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--role", choices=["research", "judge"], default="research")
    parser.add_argument("--assessment-pin", type=Path,
                        default=Path(__file__).resolve().parents[1] / "assessment-version.json")
    parser.add_argument("--assessment-source", type=Path,
                        default=Path(__file__).resolve().parents[1] / "assessment")
    parser.add_argument("--condition", choices=CONDITION_CHOICES, default="baseline")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--capture-execution", action="store_true")
    parser.add_argument("--env-manifest", type=Path)
    parser.add_argument("--duct-executable", type=Path)
    parser.add_argument("--run-mode", choices=("development", "formal"), default="development")
    parser.add_argument("--procedure", type=Path)
    parser.add_argument("--procedure-sha256")
    parser.add_argument("--procedure-study", type=Path)
    parser.add_argument("--resource-readiness", type=Path)
    parser.add_argument("--worker-end-state", type=Path)
    parser.add_argument("--protocol", choices=("legacy", NEUTRAL_PROTOCOL), default="legacy")
    parser.add_argument("--seed-receipt", type=Path)
    parser.add_argument("--delivery-capture", type=Path)
    parser.add_argument("--canonical-capture", type=Path)
    parser.add_argument("--declared-artifacts", type=Path)
    args = parser.parse_args()
    neutral = args.protocol == NEUTRAL_PROTOCOL
    if neutral and (not args.seed_receipt or not args.env_manifest):
        parser.error("Neutral sessions require external seed receipt and common environment")
    if neutral and args.role == "judge" and not all((args.delivery_capture, args.worker_end_state)):
        parser.error("Neutral judges require the original delivery capture and stop receipt")
    if not neutral and any((args.seed_receipt, args.delivery_capture, args.declared_artifacts)):
        parser.error("Delivery/seed flags require --protocol neutral-v1")
    if args.declared_artifacts and args.role != "research":
        parser.error("External worker artifact declarations are for research only")
    if neutral:
        if args.seed_receipt.resolve().is_relative_to(args.checkout.resolve()):
            parser.error("Assignment metadata must stay outside the worker/target")
        seed = json.loads(args.seed_receipt.read_bytes())
        if seed.get("protocol") != NEUTRAL_PROTOCOL:
            parser.error("Unsupported neutral seed receipt")
    if args.seconds < 0 or args.review_seconds < 0:
        parser.error("Time settings must be nonnegative")
    session_checkout = args.checkout.resolve()
    workspace = None
    if args.role == "judge":
        if not args.judge_workspace:
            parser.error("Judges require a separate --judge-workspace")
        session_checkout = args.judge_workspace.resolve()
        workspace = judge_workspace.validate(session_checkout, args.checkout.resolve())
    elif args.judge_workspace:
        parser.error("--judge-workspace is for judges only")
    pin = check_assessment(args.assessment_source.resolve(), args.assessment_pin) if args.role == "judge" else None
    if args.role == "research":
        seed = (audit_neutral_seed(args.checkout.resolve(), args.seed_receipt) if neutral else
                audit_seed(args.checkout.resolve()))
        if not neutral and canonical_condition(seed["condition"]) != canonical_condition(args.condition):
            raise SystemExit("Requested condition differs from the worker seed")
        args.condition = seed["condition"]
        expected_prompt = (neutral_research_prompt(args.checkout, args.seed_receipt) if neutral else
                           research_prompt(args.checkout, args.capture_execution))
        if args.prompt.read_bytes() != expected_prompt:
            raise SystemExit("Research prompt differs from committed input and common execution guidance")
    worker_validation = None
    if args.worker_end_state:
        if args.role != "judge":
            parser.error("Worker-stop evidence is for judges only")
        receipt = json.loads(args.worker_end_state.read_bytes())
        if neutral:
            from delivery_snapshot import validate_capture
            if not args.delivery_capture or receipt.get("schema_version") != 2:
                parser.error("Neutral judges require an original complete-delivery capture and stop receipt")
            worker_validation = validate_capture(args.delivery_capture, receipt["capture"]["sha256"])
            procedure.require_equal(receipt.get("seed_identities", {}).get("seed_commit"),
                                    seed["seed_commit"], "original supplied seed")
        else:
            worker_validation = validate_retained_artifacts(receipt, args.checkout.resolve())
    frozen = None
    status = {"version": 1, "status": "development-unsealed"}
    if args.run_mode == "formal":
        if not args.procedure or not args.procedure_study:
            parser.error("Formal native launch requires --procedure and --procedure-study")
        if args.role == "judge" and not args.worker_end_state:
            parser.error("Formal judges require --worker-end-state")
        frozen = procedure.load_procedure(args.procedure, args.procedure_sha256)
        procedure.require_equal(procedure.is_neutral(frozen), neutral, "selected native protocol")
        if args.role == "judge" and not neutral:
            roots = procedure.git(args.checkout, "rev-list", "--max-parents=0", "HEAD").splitlines()
            if len(roots) != 1:
                raise SystemExit("Formal judge target must have one input-seed root")
            seed = json.loads(procedure.blob(args.checkout, roots[0], "worker-input.json"))
        procedure.check_seed(frozen, seed)
        coordinator = Path(__file__).resolve().parents[1]
        procedure.check_sources(frozen, coordinator, args.procedure_study)
        procedure.check_worker_sources(frozen, coordinator, args.procedure_study,
                                       seed["coordinator_commit"])
        if args.role == "judge" and not neutral:
            procedure.check_retained_target(frozen, seed, roots[0],
                                            procedure.git(args.checkout, "rev-parse", "HEAD"),
                                            args.worker_end_state)
        if args.role == "judge" and frozen["version"] == 4:
            procedure.check_retained_target(frozen, seed, seed["seed_commit"],
                workspace["target_commit"], args.worker_end_state, workspace["capture"]["sha256"])
        procedure.check_settings(frozen, args)
        procedure.check_readiness(frozen, args.resource_readiness)
        if args.role == "judge":
            procedure.require_equal(pin, frozen["assessment"], "native assessor pin")
            # Reconstruct the prompt from immutable blobs. The retained guidance
            # directory supplies stable relative link locations, not authority.
            from prepare_launch import render_judge_prompt
            retained = args.procedure.resolve().parent / "frozen-inputs"
            for name, digest in frozen["study"]["guidance_files"].items():
                procedure.require_equal(procedure.sha256((retained / name).read_bytes()), digest,
                                        "retained guidance " + name)
            template = procedure.judge_template_name(frozen)
            procedure.require_equal(procedure.sha256((retained / template).read_bytes()),
                                    frozen["fixed_files"][template], "retained judge prompt")
            with tempfile.TemporaryDirectory() as temporary:
                scratch = Path(temporary)
                brief = scratch / "original-study-prompt.md"
                brief.write_bytes(procedure.blob(args.procedure_study, seed["study_commit"], "input/study-task.md")
                                  if neutral else procedure.blob(args.checkout, roots[0], "input/study-task.md"))
                procedure.require_equal(procedure.sha256(brief.read_bytes()), frozen["study"]["task_sha256"],
                                        "judge scientific task")
                reference = frozen["study"]["reference"]
                target_commit = workspace["target_commit"] if neutral else procedure.git(args.checkout, "rev-parse", "HEAD")
                expected = render_judge_prompt(retained / template, brief,
                    target_commit or "none", scratch,
                    retained / reference if reference else None, retained / frozen["study"]["rubric"])
                procedure.require_equal(args.prompt.read_text(), expected.read_text() +
                                        procedure.replay_instruction(frozen) +
                                        procedure.worker_credit_instruction(args.worker_end_state),
                                        "rendered judge instructions")
        status.update(status="formal-verified", procedure_sha256=args.procedure_sha256,
                      comparison_id=frozen["comparison_id"])
        if frozen["version"] in (2, 4):
            status["research_procedure_sha256"] = frozen["assessment_amendment"]["research_procedure_sha256"]
    elif args.procedure or args.procedure_sha256 or args.procedure_study or args.resource_readiness:
        parser.error("Procedure flags require --run-mode formal")
    operational = bool(frozen and frozen["version"] == 4 and args.role == "judge")
    if args.canonical_capture and not operational:
        parser.error("Canonical/operational judging requires a version 4 assessment seal")
    if args.role == "judge":
        procedure.require_equal(workspace["schema_version"], 3 if operational else 2 if neutral else 1,
                                "judge target schema for assessment version")
    if operational:
        if not args.canonical_capture:
            parser.error("Version 4 assessment requires --canonical-capture")
        procedure.require_equal(str(args.canonical_capture.resolve()), workspace["capture"]["uri"],
                                "canonical capture path")
        procedure.require_equal(str(args.delivery_capture.resolve()), workspace["operational_capture"]["uri"],
                                "operational capture path")
        status["operational_runtime"] = frozen["operational_runtime"]
    output = args.output.resolve()
    if operational:
        for manifest in (args.canonical_capture, args.delivery_capture):
            bundle = manifest.resolve().parent
            if output.is_relative_to(bundle) or bundle.is_relative_to(output):
                parser.error("Native evidence must be separate from canonical and operational capture bundles")
    if output.is_relative_to(args.checkout.resolve()):
        parser.error("Launch evidence must be outside the assessed or research checkout")
    if args.role == "judge" and (output.is_relative_to(session_checkout) or
                                 session_checkout.is_relative_to(output)):
        parser.error("Native evidence and judge workspace must be separate directories")
    output.mkdir(parents=True, exist_ok=False)
    if args.worker_end_state:
        status["worker_end_state_sha256"] = procedure.sha256(args.worker_end_state.read_bytes())
        (output / "worker-end-state.json").write_bytes(args.worker_end_state.read_bytes())
        (output / "worker-artifact-validation.json").write_text(json.dumps(worker_validation, indent=2) + "\n")
    (output / "procedure-status.json").write_text(json.dumps(status, indent=2) + "\n")
    prompt = args.prompt.read_bytes()
    (output / "prompt.txt").write_bytes(prompt)
    if args.role == "research":
        assigned = dict(seed.get("assignment", {"condition": seed["condition"],
                        "additional_prompt": "", "legacy_input_version": seed["version"]}))
        assigned.update(prompt_sha256=hashlib.sha256(prompt).hexdigest(),
                        coordinator_commit=seed["coordinator_commit"],
                        supplied_skills_commit=seed.get("skills_commit"),
                        capture_execution=args.capture_execution)
        (output / "condition-assignment.json").write_text(json.dumps(assigned, indent=2) + "\n")
    prepared_profile = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    if frozen:
        procedure.check_native(frozen, args.cli, prepared_profile, args.role)
        if neutral:
            for name in ("pixi.toml", "pixi.lock"):
                procedure.require_equal(procedure.sha256(args.env_manifest.with_name(name).read_bytes()),
                    frozen["role_hosts"][args.role]["environment"][name], "native common environment " + name)
            procedure.require_equal(frozen["role_hosts"][args.role]["thread_environment"],
                                    procedure.NEUTRAL_THREAD_ENV, "native thread environment")
    profile = launch_profile(prepared_profile, args.assessment_source if args.role == "judge" else None)
    if neutral and args.role == "research" and seed.get("skills_directory"):
        # Preserve sibling references while advertising only assigned entrypoints.
        for directory in sorted(Path(seed["skills_directory"]).iterdir()):
            if directory.is_dir():
                (profile / "skills" / directory.name).symlink_to(directory)
    config = tomllib.loads((profile / "config.toml").read_text())
    overrides = {item["path"]: item["enabled"] for item in config.get("skills", {}).get("config", [])}
    overrides.update({str(path): False for path in host_skill_paths(prepared_profile)})
    study_skills = ([profile / "skills" / name / "SKILL.md"
                     for name in sorted(JUDGE_SKILLS)] if args.role == "judge" else
                    [profile / "skills" / name / "SKILL.md" for name in STUDY_SKILLS] if neutral else
                    [args.checkout.resolve() / ".agents/skills" / name / "SKILL.md"
                     for name in STUDY_SKILLS])
    selected = selected_skills(args.role, args.condition)
    if neutral and args.role == "research":
        overrides.update({str(path): path.parent.name in selected
                          for path in (profile / "skills").glob("*/SKILL.md")})
    if any(not path.is_file() for path in study_skills if path.parent.name in selected):
        raise SystemExit("Selected role requires installed skill entrypoints")
    # Do not disable nonexistent local skill paths in discovery/baseline arms:
    # a worker may spontaneously discover and install them after launch.
    overrides.update({str(path): path.parent.name in selected for path in study_skills if path.is_file()})
    project_skills = set(study_skills)
    if args.role == "judge":
        for directory in (".agents/skills", ".codex/skills"):
            project_skills.update((args.checkout.resolve() / directory).glob("*/SKILL.md"))
        frozen_entries = {p for p in study_skills if p.parent.name in JUDGE_SKILLS}
        overrides.update({str(path): False for path in project_skills - frozen_entries})
    skill_config = "skills.config=[" + ",".join("{path=" + json.dumps(s["path"]) +
                    ",enabled=" + str(s["enabled"]).lower() + "}" for s in
                    ({"path": path, "enabled": enabled} for path, enabled in sorted(overrides.items()))) + "]"
    command = [str(args.cli), "--no-daemon", "-a", "never", "-s", "danger-full-access",
               "-m", args.model, "-c", 'model_reasoning_effort="' + args.effort + '"',
               "-c", skill_config, "-c", "project_doc_max_bytes=0",
               "exec", "--json", "--color", "never", "-C", str(session_checkout),
               "-o", str(output / "final.txt"), "-"]
    environment = (procedure.neutral_environment(args.env_manifest, os.environ, args.role)
                   if neutral else os.environ.copy())
    environment["CODEX_HOME"] = str(profile)
    if args.role == "judge":
        environment = judge_environment(environment, args, session_checkout, profile, workspace, frozen)
        if frozen:
            (output / "judge-runtime.json").write_bytes(Path(environment["STAMPED_JUDGE_RUNTIME"]).read_bytes())
    removed = [key for key in ("CODEX_THREAD_ID", "CODEX_PARENT_THREAD_ID", "CODEX_SESSION_ID")
               if environment.pop(key, None) is not None]
    pixi_removed = [key for key in ("PIXI_PROJECT_MANIFEST", "PIXI_IN_SHELL", "PIXI_PROJECT_ROOT",
                    "PIXI_PROJECT_NAME", "PIXI_PROJECT_VERSION", "PIXI_ENVIRONMENT_NAME",
                    "PIXI_ENVIRONMENT_PLATFORMS", "PIXI_PROMPT")
                    if environment.pop(key, None) is not None]
    preview_command = command[:command.index("exec")] + ["-C", str(session_checkout),
                      "debug", "prompt-input", prompt.decode()]
    preview = subprocess.run(preview_command, cwd=session_checkout, env=environment,
                             capture_output=True, check=True)
    forbidden = [marker for marker in (b"memory/transport.json", b"sensitive transport configuration",
                b"Hub token file", b"- private-workshop-memory:", b"- workshop-feedback:")
                 if marker in preview.stdout]
    project_instructions = b"# AGENTS.md instructions" in preview.stdout
    catalog = skill_catalog(preview.stdout)
    visible = sorted({item["name"] for item in catalog if item["name"] in STUDY_SKILLS})
    allowed_paths = {str(path.resolve()) for path in study_skills if path.parent.name in selected}
    unexpected = [item for item in catalog if item["path"] not in allowed_paths and
                  not Path(item["path"]).is_relative_to((profile / "skills/.system").resolve())]
    preflight = {"effective_prompt_sha256": hashlib.sha256(preview.stdout).hexdigest(),
                 "private_marker_count": len(forbidden), "condition": args.condition,
                 "role": args.role, "codex_home": str(profile),
                 "project_instructions_present": project_instructions,
                 "visible_study_skills": visible, "advertised_skill_catalog": catalog,
                 "unexpected_skill_catalog": unexpected,
                 "profile_config_sha256": hashlib.sha256((profile / "config.toml").read_bytes()).hexdigest(),
                 "inherited_pixi_variables_removed": pixi_removed,
                 "resource_path": environment["PATH"] if neutral else None,
                 "thread_environment": procedure.NEUTRAL_THREAD_ENV if neutral else None}
    (output / "prompt-preflight.json").write_text(json.dumps(preflight, indent=2) + "\n")
    if forbidden or project_instructions or unexpected or set(visible) != selected:
        raise SystemExit("Effective prompt failed instruction or study-skill visibility preflight")
    if args.preflight_only:
        print(json.dumps(preflight))
        return
    duct = None
    if neutral and args.capture_execution:
        duct = procedure.duct_identity(args.duct_executable)
        if frozen:
            procedure.require_equal(duct, frozen["role_hosts"][args.role]["duct"], "native outer capture")
        command = [str(args.duct_executable.resolve()), "--mode", "current-session",
                   "--output-prefix", str(output / "execution/run_"), "--fail-time", "0",
                   "--capture-outputs", "all", "--outputs", "all", "--sample-interval", "1",
                   "--report-interval", "60", "--log-level", "WARNING", *command]
    record = {"command": command, "outer_capture": duct,
              "resource_path": environment["PATH"] if neutral else None,
              "thread_environment": procedure.NEUTRAL_THREAD_ENV if neutral else None, "cwd": str(session_checkout),
              "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
              "inherited_session_variables_removed": removed,
              "inherited_pixi_variables_removed": pixi_removed,
              "started_at": datetime.now(timezone.utc).isoformat(), "timeout_seconds": args.seconds,
              "review_seconds": args.review_seconds, "role": args.role,
              "assessment_pin": pin}
    record["procedure"] = status
    record["condition"] = args.condition if args.role == "research" else None
    record["codex_home"] = str(profile)
    record["study_skill_paths"] = [str(p) for p in study_skills]
    record["starting_commit"] = subprocess.check_output(
        ["git", "-C", str(session_checkout), "rev-parse", "HEAD"], text=True).strip()
    if args.role == "judge":
        record["judge_workspace"] = str(session_checkout)
        record["target"] = workspace
        if operational:
            record["operational_runtime"] = frozen["operational_runtime"]
            record["git_config_overlay"] = {"inherited_count": int(os.environ.get("GIT_CONFIG_COUNT", "0")),
                "effective_count": int(environment["GIT_CONFIG_COUNT"]),
                "appended": frozen["operational_runtime"]["git_config"], "GIT_OPTIONAL_LOCKS": "0"}
        if frozen:
            record["judge_runtime_sha256"] = environment["STAMPED_JUDGE_RUNTIME_SHA256"]
        runner = Path(environment["STAMPED_ASSESSMENT_RUNNER"])
        record["assessment_runner_sha256"] = hashlib.sha256(runner.read_bytes()).hexdigest()
    (output / "launch.json").write_text(json.dumps(record, indent=2) + "\n")
    process = subprocess.Popen(command, cwd=session_checkout, env=environment,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               **({"start_new_session": True} if duct else {"process_group": 0}))
    def relay():
        with (output / "events.jsonl").open("xb") as events:
            for line in process.stdout:
                events.write(line)
                events.flush()
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()
    reader = threading.Thread(target=relay)
    def relay_errors():
        with (output / "stderr.txt").open("xb") as errors:
            for line in process.stderr:
                errors.write(line)
                errors.flush()
                sys.stderr.buffer.write(line)
                sys.stderr.buffer.flush()
    error_reader = threading.Thread(target=relay_errors)
    reader.start()
    error_reader.start()
    declarations = json.loads(args.declared_artifacts.read_bytes()) if args.declared_artifacts else []
    if neutral and args.role == "research":
        declarations.append({"path": str(profile / "skills"), "declaration": {
            "kind": "native-session-skill-directory", "initial_catalog": catalog,
            "attribution": "Initial supplied guidance is coordinator material; newly installed contents are worker discoveries. Native auth/history excluded."}})
    timed_out = wait_and_capture_worker(process, prompt, output, args.checkout,
                                        record, args.role, args.seconds, args.review_seconds,
                                        seed if neutral and args.role == "research" else None,
                                        declarations)
    reader.join(timeout=10)
    error_reader.join(timeout=10)
    if reader.is_alive() or error_reader.is_alive():
        raise SystemExit("A descendant retained the output pipe; inspect retained process logs")
    sessions = []
    for line in (output / "events.jsonl").read_text().splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("type") == "thread.started":
            sessions.append(item.get("thread_id"))
    record["native_session_ids"] = sessions
    target_error = None
    if args.role == "judge":
        try:
            if operational:
                integrity = judge_workspace.retain_operational_target(args.checkout.resolve(), workspace,
                    output / "operational-retention")
                record["operational_integrity"] = integrity
                for name in ("target_unchanged", "canonical_unchanged", "operational_metadata_changed"):
                    record[name] = integrity[name]
                if not integrity["protected_unchanged"]:
                    raise ValueError("Protected operational content changed or retention is incomplete")
            else:
                judge_workspace.validate_target(args.checkout.resolve(), workspace)
                record["target_unchanged"] = True
        except (OSError, ValueError, SystemExit, subprocess.CalledProcessError) as error:
            record["target_unchanged"] = False
            if operational:
                record.setdefault("canonical_unchanged", False)
                # A failed canonical check must not discard the operational
                # bytes. These failure captures never make a result eligible.
                if "operational_integrity" not in record:
                    from delivery_snapshot import save_delivery
                    record["failed_integrity_captures"] = {}
                    for label, manifest in (("canonical", args.canonical_capture),
                                            ("operational", args.delivery_capture)):
                        try:
                            record["failed_integrity_captures"][label] = save_delivery(
                                manifest.absolute().parent, output / (label + "-as-found"),
                                {"kind": "failed-assessment-integrity"})
                        except (OSError, ValueError) as retention_error:
                            record["failed_integrity_captures"][label] = {"error": str(retention_error)}
            target_error = str(error)
            record["target_validation_error"] = target_error
    (output / "result.json").write_text(json.dumps(record, indent=2) + "\n")
    if args.role == "research":
        (output / "skill-observations.json").write_text(json.dumps(
            skill_observations(args.checkout.resolve(), profile), indent=2) + "\n")
    if target_error:
        raise SystemExit("Judge changed the assessed target: " + target_error)
    raise SystemExit(124 if timed_out else process.returncode)


if __name__ == "__main__":
    main()
