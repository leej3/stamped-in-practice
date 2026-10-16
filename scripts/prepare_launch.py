#!/usr/bin/env python3
"""Create, prepare and launch a fresh native session using existing host tools.

Never pushes. All generated evidence belongs outside the new worker checkout.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from study_seed import audit_seed, blob, make_seed, research_prompt, worker_manifest
from research_conditions import CONDITION_CHOICES
import assessment_procedure as procedure
import judge_workspace


def run(argv, cwd, capture=False):
    result = subprocess.run([str(x) for x in argv], cwd=cwd, check=True,
                            stdout=subprocess.PIPE if capture else None, text=True)
    return result.stdout.strip() if capture else None



def retrieve_inputs(git_command, checkout, inventory, remote):
    """Retrieve selected keys without importing source annex location history."""
    for item in inventory:
        if "annex_key" not in item or (checkout / item["path"]).exists():
            continue
        # get --from silently skips keys with no location record. transferkey
        # contacts the configured mirror directly and retains the original key.
        result = subprocess.run(git_command + ["annex", "transferkey", item["annex_key"],
                                "--from", remote], cwd=checkout,
                                capture_output=True, text=True)
        if result.returncode:
            if not item.get("urls"):
                sys.stderr.write(result.stdout + result.stderr)
                result.check_returncode()
            run(git_command + ["annex", "get", "--", item["path"]], checkout)
        else:
            # transferkey records the local copy, not the remote location.
            # Record the mirror that just supplied these bytes for later clones.
            uuid = run(git_command + ["config", "--get", "remote." + remote + ".annex-uuid"],
                       checkout, True)
            run(git_command + ["annex", "setpresentkey", item["annex_key"], uuid, "1"], checkout)
        if not (checkout / item["path"]).is_file():
            raise SystemExit("Input content was not retrieved: " + item["path"])


def materialize_retained_files(git_command, checkout, receipt, remote, evidence=None):
    """Recover annex bytes needed to compare stop-time regular files."""
    record = {"schema_version": 1, "target": str(checkout.resolve()), "remote": remote,
              "target_commit": run(["git", "rev-parse", "HEAD"], checkout, True),
              "paths": [], "commands": [], "commands_succeeded": False,
              "verification": "requires-worker-retention-check"}

    def retain():
        if evidence:
            evidence.write_text(json.dumps(record, indent=2) + "\n")

    def invoke(arguments):
        command = [str(value) for value in git_command + arguments]
        result = subprocess.run(command, cwd=checkout, capture_output=True, text=True)
        record["commands"].append({"argv": command, "returncode": result.returncode,
                                   "stdout": result.stdout, "stderr": result.stderr})
        retain()
        if result.returncode:
            sys.stderr.write(result.stdout + result.stderr)
            result.check_returncode()
        return result.stdout

    regular = {item["path"] for item in receipt.get("worktree", []) if item["kind"] == "file"}
    inventory = invoke(["annex", "find", "--anything", "--json", "--", "."])
    paths = sorted({item["file"] for item in map(json.loads, inventory.splitlines())
                    if item["file"] in regular})
    record["paths"] = paths
    if paths:
        # Unlocked annex pointers are regular existing files in a fresh clone.
        # Existence does not establish that their payloads are materialized.
        invoke(["annex", "get", "--from", remote, "--", *paths])
    record["commands_succeeded"] = True
    retain()
    return paths


def render_judge_prompt(template, study, target_commit, evidence, reference=None, rubric=None):
    """Retain the coordinator's scientific brief independently of the target."""
    content = study.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    (evidence / "study.md").write_bytes(content)
    (evidence / "study.json").write_text(json.dumps({
        "source": str(study.resolve()), "sha256": digest,
    }, indent=2) + "\n")
    prompt = template.read_text().replace("$TARGET_COMMIT", target_commit)
    prompt += ("\nScientific task supplied by the coordinator (SHA-256 " + digest + ").\n"
               "Use this retained brief, not a worker-edited replacement.\n"
               "Relative source links refer to input/ in the assessed object.\n\n"
               + content.decode())
    for label, source in (("rubric", rubric), ("reference", reference)):
        if not source:
            continue
        material = source.read_bytes()
        (evidence / (label + ".md")).write_bytes(material)
        (evidence / (label + ".json")).write_text(json.dumps({
            "source": str(source.resolve()),
            "sha256": hashlib.sha256(material).hexdigest(),
        }, indent=2) + "\n")
        heading = ("Coordinator scientific rubric" if label == "rubric" else
                   "Optional coordinator evaluation guidance")
        prompt += ("\n" + heading + ", separate from the scientific task.\n"
                   "Alternative scientifically defensible methods are allowed.\n"
                   "Relative links resolve from " + str(source.resolve().parent) + ".\n\n"
                   + material.decode())
    destination = evidence / "judge-prompt.md"
    destination.write_text(prompt)
    return destination


def main():
    defaults_parser = argparse.ArgumentParser(add_help=False)
    defaults_parser.add_argument("--host-config", type=Path, default=procedure.default_host_config())
    preliminary, _ = defaults_parser.parse_known_args()
    defaults = json.loads(preliminary.host_config.read_text()) if preliminary.host_config.is_file() else {}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host-config", type=Path, default=preliminary.host_config)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--branch", required=True)
    parser.add_argument("--base", required=True,
                        help="Coordinator revision pinning study/resources/skills; result revision for judges")
    parser.add_argument("--kind", choices=["worktree", "clone"], default="clone")
    parser.add_argument("--clone-path", type=Path)
    parser.add_argument("--judge-workspace", type=Path,
                        help="Separate judge session/output repository; default: EVIDENCE/judgment")
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--env-manifest", type=Path)
    parser.add_argument("--approved-hooks", type=Path)
    parser.add_argument("--trust-sync", type=Path)
    parser.add_argument("--resolver", type=Path)
    parser.add_argument("--checkpoint-repo")
    parser.add_argument("--annex-remote", default="con-hub")
    parser.add_argument("--annex-git-url")
    parser.add_argument("--annex-url")
    parser.add_argument("--study", type=Path,
                        help="Installed study submodule; workers receive only its committed input/ tree")
    parser.add_argument("--reference", type=Path,
                        help="Optional coordinator evaluation guidance file, judges only")
    parser.add_argument("--cli", type=Path)
    parser.add_argument("--seconds", type=int, default=0,
                        help="Explicit hard limit; 0 waits for completion")
    parser.add_argument("--review-seconds", type=int, default=5400)
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--role", choices=["research", "judge"], default="research")
    parser.add_argument("--codex-home", type=Path,
                        help="Prepared isolated public profile, without private global instructions")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--capture-execution", action="store_true",
                        help="Request duct execution records in the worker; use only when authorized")
    parser.add_argument("--condition", choices=CONDITION_CHOICES, default="baseline")
    parser.add_argument("--run-mode", choices=("development", "formal"), default="development")
    parser.add_argument("--procedure", type=Path, help="Sealed comparison procedure, formal runs only")
    parser.add_argument("--procedure-sha256", help="Registered SHA-256 of the sealed procedure")
    parser.add_argument("--resource-readiness", type=Path, help="Completed readiness result.json, formal runs only")
    parser.add_argument("--worker-end-state", type=Path,
                        help="External worker-stop receipt; required for formal judges")
    # Paths/resources are host choices; the coordinator is this checkout, not
    # an old absolute repository path retained in a host configuration.
    parser.set_defaults(**{key: value for key, value in defaults.items() if key != "repo"})
    args = parser.parse_args()
    if args.seconds < 0 or args.review_seconds < 0:
        parser.error("Time settings must be nonnegative")
    if not args.study or not args.study.is_dir():
        parser.error("--study requires an installed study submodule")
    if args.kind != "clone":
        parser.error("Launch requires --kind clone for an independent Git object store")
    if args.role == "research" and args.reference:
        parser.error("Reference guidance is for judges only")
    if args.role == "research" and args.worker_end_state:
        parser.error("--worker-end-state is for judges only")
    if args.role == "research" and args.judge_workspace:
        parser.error("--judge-workspace is for judges only")
    if args.role == "judge" and args.condition != "baseline":
        parser.error("Judges use the fixed template; omit --condition")
    for name in ("repo", "env_manifest", "approved_hooks", "trust_sync", "resolver", "cli", "codex_home"):
        value = getattr(args, name)
        if not value:
            parser.error("Missing --" + name.replace("_", "-") + "; configure host defaults once")
        setattr(args, name, Path(value).expanduser().resolve())
    if not args.checkpoint_repo:
        parser.error("Missing --checkpoint-repo; configure host defaults once")
    if not args.annex_git_url or not args.annex_url:
        parser.error("Missing annex remote URLs; configure host defaults once")
    repo = args.repo.resolve()
    base_commit = run(["git", "rev-parse", "--verify", args.base + "^{commit}"], repo, True)
    coordinator = Path(__file__).resolve().parents[1]
    frozen = None
    if args.run_mode == "formal":
        if not args.procedure or args.reference:
            parser.error("Formal mode requires --procedure and uses only its frozen rubric/reference")
        if args.role == "judge" and not args.worker_end_state:
            parser.error("Formal judges require --worker-end-state from the research launch")
        frozen = procedure.load_procedure(args.procedure, args.procedure_sha256)
        procedure.check_sources(frozen, coordinator, args.study,
                                base_commit if args.role == "research" else None)
        procedure.check_host(frozen, args)
        procedure.check_settings(frozen, args)
        procedure.check_readiness(frozen, args.resource_readiness)
    elif args.procedure or args.procedure_sha256 or args.resource_readiness:
        parser.error("Procedure/readiness flags require --run-mode formal")
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    procedure_receipt = {"version": 1, "status": "development-unsealed"}
    if frozen:
        retained = procedure.retain_inputs(frozen, coordinator, args.study, evidence / "frozen-inputs")
        (evidence / "procedure.json").write_bytes(args.procedure.read_bytes())
        (evidence / "resource-readiness.json").write_bytes(args.resource_readiness.read_bytes())
        procedure_receipt.update(status="formal-verified", procedure_sha256=args.procedure_sha256,
                                 comparison_id=frozen["comparison_id"])
        if frozen["version"] == 2:
            procedure_receipt["research_procedure_sha256"] = frozen["assessment_amendment"]["research_procedure_sha256"]
    (evidence / "procedure-status.json").write_text(json.dumps(procedure_receipt, indent=2) + "\n")
    if not args.branch.startswith("codex/"):
        parser.error("Use a codex/ branch")
    checkout = (args.clone_path.resolve() if args.clone_path else
                repo.parent / (repo.name + "-workers") / args.branch)
    if checkout.exists():
        parser.error("Worker destination exists; choose a fresh --branch or --clone-path")
    if args.role == "research":
        seed = make_seed(repo, base_commit, args.study, checkout, args.branch,
                         args.condition, args.resolver)
        if frozen:
            procedure.check_seed(frozen, seed)
        args.condition = seed["condition"]
        args.prompt = evidence / "research-prompt.md"
        args.prompt.write_bytes(research_prompt(checkout, args.capture_execution))
        (evidence / "input-boundary.json").write_text(json.dumps(seed, indent=2) + "\n")
    else:
        # Fetch only the exact research-object revision. It must itself descend
        # from an input-only seed, not the coordinator repository's history.
        checkout.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "-b", args.branch, checkout], repo)
        run(["git", "fetch", "--no-tags", repo, base_commit], checkout)
        run(["git", "reset", "--hard", "FETCH_HEAD"], checkout)
        # Annex location/URL records belong to the submitted research object.
        # Retain just that metadata branch, without fetching other trial refs.
        annex_ref = subprocess.run(["git", "rev-parse", "--verify", "git-annex^{commit}"],
                                   cwd=repo, capture_output=True, text=True)
        if annex_ref.returncode == 0:
            annex_commit = annex_ref.stdout.strip()
            run(["git", "fetch", "--no-tags", repo, annex_commit + ":refs/heads/git-annex"], checkout)
            (evidence / "annex-source.json").write_text(json.dumps({
                "repository": str(repo), "commit": annex_commit,
            }, indent=2) + "\n")
        roots = run(["git", "rev-list", "--max-parents=0", "HEAD"], checkout, True).splitlines()
        if len(roots) != 1 or subprocess.run(
                ["git", "cat-file", "-e", roots[0] + ":worker-input.json"],
                cwd=checkout, capture_output=True).returncode:
            raise SystemExit("Judge target must descend from a research input seed")
        remote = run(["git", "remote", "get-url", "--push", "origin"], repo, True)
        run(["git", "remote", "add", "origin", remote], checkout)
        run(["git", "config", "remote.origin.fetch",
             f"+refs/heads/{args.branch}:refs/remotes/origin/{args.branch}"], checkout)
        origin_seed = json.loads(blob(checkout, roots[0], "worker-input.json"))
        if frozen:
            procedure.check_seed(frozen, origin_seed)
            procedure.check_worker_sources(frozen, coordinator, args.study, origin_seed["coordinator_commit"])
            procedure.check_retained_target(frozen, origin_seed, roots[0], base_commit, args.worker_end_state)
        study_commit = origin_seed["study_commit"]
        original_brief = blob(args.study, study_commit, "input/study-task.md")
        if original_brief != blob(checkout, roots[0], "input/study-task.md"):
            raise SystemExit("Selected study does not match the worker's original scientific brief")
        if args.worker_end_state:
            content = args.worker_end_state.read_bytes()
            args.worker_end_state = evidence / "worker-end-state.json"
            args.worker_end_state.write_bytes(content)
        (evidence / "study-source.json").write_text(json.dumps({
            "path": str(args.study.resolve()), "commit": study_commit,
            "input_tree": run(["git", "rev-parse", study_commit + ":input"], args.study, True),
        }, indent=2) + "\n")
        template = Path(__file__).resolve().parents[1] / "judge-prompt.md"
        # Recover the exact brief from the worker's immutable starting commit;
        # later worker edits do not redefine the task.
        study = evidence / "original-study-prompt.md"
        study.write_bytes(blob(checkout, roots[0], "input/study-task.md"))
        rubric = None
        if frozen:
            template = retained / "judge-prompt.md"
            rubric = retained / frozen["study"]["rubric"]
            args.reference = retained / frozen["study"]["reference"] if frozen["study"]["reference"] else None
        args.prompt = render_judge_prompt(template, study, base_commit, evidence, args.reference, rubric)
        if frozen:
            with args.prompt.open("a") as stream:
                stream.write(procedure.replay_instruction(frozen))
        if args.worker_end_state:
            with args.prompt.open("a") as stream:
                stream.write(procedure.worker_credit_instruction(args.worker_end_state))
    (evidence / "checkout.json").write_text(json.dumps({"checkout": str(checkout),
        "kind": "independent-repository", "branch": args.branch, "base": args.base,
        "base_commit": base_commit, "worker_commit": run(["git", "rev-parse", "HEAD"], checkout, True),
        "role": args.role}, indent=2) + "\n")
    lock = args.env_manifest.resolve().with_name("pixi.lock")
    # Judges use prepared operational tools; the target's environment is tested
    # only by the separately authorized replay, never repaired during judging.
    manifest_path = args.env_manifest if args.role == "judge" else checkout / "pixi.toml"
    worker_lock = lock if args.role == "judge" else checkout / "pixi.lock"
    if args.role != "judge" and manifest_path.read_bytes() != worker_manifest(args.env_manifest.read_bytes()):
        raise SystemExit("Worker manifest differs from the supplied lock's source manifest")
    if worker_lock.exists() and worker_lock.read_bytes() != lock.read_bytes():
        raise SystemExit("Existing worker lock differs; preserve and review")
    if lock != worker_lock:
        shutil.copy2(lock, worker_lock)
    run(["pixi", "install", "--locked", "--manifest-path", manifest_path], checkout)
    git = ["pixi", "run", "--manifest-path", manifest_path, "git", "-C", checkout]
    run(["git", "config", "remote.origin.annex-ignore", "true"], checkout)
    run(git + ["annex", "init"], checkout)
    remotes = run(["git", "remote"], checkout, True).splitlines()
    if args.annex_remote in remotes:
        actual_url = run(["git", "remote", "get-url", args.annex_remote], checkout, True)
        if actual_url != args.annex_git_url:
            raise SystemExit("Existing annex Git URL differs; preserve and review")
    else:
        run(["git", "remote", "add", args.annex_remote, args.annex_git_url], checkout)
    run(["git", "config", "remote." + args.annex_remote + ".fetch",
         f"+refs/heads/{args.branch}:refs/remotes/{args.annex_remote}/{args.branch}"], checkout)
    run(["git", "config", "remote." + args.annex_remote + ".skipFetchAll", "true"], checkout)
    key = "remote." + args.annex_remote + ".annexurl"
    actual_annex = subprocess.run(["git", "config", "--get", key], cwd=checkout,
                                  capture_output=True, text=True)
    if actual_annex.returncode not in (0, 1) or (actual_annex.returncode == 0 and
            actual_annex.stdout.strip() != args.annex_url):
        raise SystemExit("Existing annex endpoint differs; preserve and review")
    run(["git", "config", key, args.annex_url], checkout)
    annex_info = run(git + ["annex", "info", args.annex_remote, "--json"], checkout, True)
    (evidence / "annex-remote.json").write_text(annex_info + "\n")
    if args.role == "research":
        for item in seed["inputs"]:
            for url in item.get("urls", []):
                run(git + ["annex", "registerurl", item["annex_key"], url], checkout)
        retrieve_inputs(git, checkout, seed["inputs"], args.annex_remote)
        audit_seed(checkout)
    elif args.worker_end_state:
        from worker_end_state import validate_retained_artifacts
        receipt = json.loads(args.worker_end_state.read_bytes())
        materialized = materialize_retained_files(git, checkout, receipt, args.annex_remote,
                                                 evidence / "judge-annex-materialization.json")
        try:
            retained_state = validate_retained_artifacts(receipt, checkout)
        except ValueError as error:
            (evidence / "worker-retention-check.json").write_text(json.dumps({
                "artifacts_match": False, "error": str(error),
                "annex_materialization_paths": materialized}, indent=2) + "\n")
            raise SystemExit("Worker-stop evidence failed: " + str(error))
        retained_state["annex_materialization_paths"] = materialized
        (evidence / "worker-retention-check.json").write_text(json.dumps(retained_state, indent=2) + "\n")

    (evidence / "environment.json").write_text(json.dumps({"source_manifest": str(args.env_manifest.resolve()),
        "worker_manifest": str(manifest_path), "worker_lock": str(worker_lock),
        "worker_environment_installed": True,
        "manifest_sha256": hashlib.sha256(args.env_manifest.read_bytes()).hexdigest(),
        "lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest()}, indent=2) + "\n")
    scripts = Path(__file__).resolve().parent
    session_checkout = checkout
    if args.role == "judge":
        session_checkout = (args.judge_workspace.resolve() if args.judge_workspace else
                            evidence / "judgment")
        workspace = judge_workspace.initialize(session_checkout, checkout, args.resolver)
        (evidence / "judge-workspace.json").write_text(json.dumps(
            {"workspace": str(session_checkout), "target": workspace}, indent=2) + "\n")
    # Seed attribution belongs to the active coordinator; native setup and
    # execution use the isolated public profile only after that commit exists.
    os.environ["CODEX_HOME"] = str(args.codex_home.resolve())
    run([sys.executable, scripts / "prepare_checkout.py", "--checkout", session_checkout,
         "--approved-hooks", args.approved_hooks, "--trust-sync", args.trust_sync,
         "--resolver", args.resolver, "--checkpoint-repo", args.checkpoint_repo,
         "--receipt", evidence / "preparation.json"], repo)
    run([sys.executable, scripts / "launch_native_probe.py", "--checkout", checkout,
         "--prompt", args.prompt.resolve(), "--output", evidence / "native",
         "--cli", args.cli, "--seconds", str(args.seconds), "--condition", args.condition,
         "--review-seconds", str(args.review_seconds), "--role", args.role,
         "--assessment-pin", retained / "assessment-version.json" if frozen else scripts.parent / "assessment-version.json",
         "--assessment-source", scripts.parent / "assessment",
         "--model", args.model, "--effort", args.effort] +
         (["--run-mode", "formal", "--procedure", evidence / "procedure.json",
           "--procedure-sha256", args.procedure_sha256, "--procedure-study", args.study.resolve(),
           "--resource-readiness", evidence / "resource-readiness.json"] if frozen else []) +
         (["--worker-end-state", args.worker_end_state] if args.worker_end_state else []) +
         (["--judge-workspace", session_checkout] if args.role == "judge" else []) +
         (["--capture-execution"] if args.capture_execution else []) +
         (["--preflight-only"] if args.prepare_only else []), repo)


if __name__ == "__main__":
    main()
