"""Formal freeze checks with synthetic Git objects and a fake native client."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import assessment_procedure as procedure
import prepare_launch as prepare
import study_seed as seed
import judge_workspace
from test_launch import fake_cli, git, init, commit
from test_assessment_runner import frozen_runner


@pytest.fixture
def comparison(tmp_path, fake_cli, monkeypatch):
    for role in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv("GIT_" + role + "_NAME", "Procedure fixture")
        monkeypatch.setenv("GIT_" + role + "_EMAIL", "fixture@example.invalid")
    coordinator = init(tmp_path / "coordinator")
    study = init(coordinator / "studies/example")
    (study / "input").mkdir()
    (study / "input/study-task.md").write_text("Estimate the relationship and its uncertainty.\n")
    (study / "input/sources.json").write_text('{"source":"synthetic"}\n')
    (study / "input/data.csv").write_text("x,y\n1,2\n2,3\n")
    (study / "coordinator-guidance").mkdir()
    (study / "coordinator-guidance/rubric.md").write_text("Check design, uncertainty and conclusions.\n")
    (study / "coordinator-guidance/reference.md").write_text("Consider [details](details.txt).\n")
    (study / "coordinator-guidance/details.txt").write_text("Immutable comparison evidence.\n")
    commit(study, "test: create scientific fixture")
    git(study, "remote", "add", "origin", "git@github.com:example/study.git")
    assessor = init(coordinator / "assessment")
    for name in ("assess-alignment-with-stamped-principles", "stamped-conventions"):
        skill = assessor / "skills" / name / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("Synthetic assessor instruction.\n")
    assessor_commit = commit(assessor, "test: create assessor fixture")
    for name in procedure.FIXED_FILES:
        target = coordinator / name
        target.parent.mkdir(parents=True, exist_ok=True)
        source = ROOT / name
        # Readiness is integrated independently; its fixed source identity is
        # exercised here without running host checks.
        target.write_bytes(source.read_bytes() if source.is_file() else b"# fixture readiness\n")
    (coordinator / "pixi.toml").write_text(
        '[workspace]\nname="fixture"\nchannels=["conda-forge"]\nplatforms=["linux-64"]\n'
        '[dependencies]\npython=">=3.11"\n[tasks]\nlaunch="python scripts/prepare_launch.py"\n')
    (coordinator / "pixi.lock").write_text("Synthetic immutable runtime lock\n")
    (coordinator / ".gitmodules").write_text(
        '[submodule "studies/example"]\npath = studies/example\nurl = git@github.com:example/study.git\n'
        '[submodule "assessment"]\npath = assessment\nurl = git@github.com:example/assessor.git\n')
    requirements = coordinator / "requirements.json"
    requirements.write_text(json.dumps({"schema_version": 1, "requirements": [
        {"id": "inputs", "description": "Retrieve required inputs", "source": "Study task"}]}))
    environment_commit = commit(coordinator, "test: snapshot starting environment")
    pin = {"version": 1, "source_commit": assessor_commit, "environment_commit": environment_commit,
           "sha256": {name: procedure.sha256((coordinator / name).read_bytes())
                      for name in ("pixi.toml", "pixi.lock")}}
    (coordinator / "assessment-version.json").write_text(json.dumps(pin))
    base = commit(coordinator, "test: pin assessor runtime")
    git(coordinator, "remote", "add", "origin", "git@github.com:example/coordinator.git")
    cli, profile = fake_cli
    (profile / "models_cache.json").write_text(json.dumps({
        "fetched_at": "2026-01-01T00:00:00Z", "etag": "initial", "identity": "synthetic-account",
        "models": [{"slug": "gpt-6-luna", "display_name": "Fixture", "description": "UI text",
                    "context_window": 1000, "model_messages": {"persistent_instructions": "Stable instructions"},
                    "supported_reasoning_levels": [{"effort": "high", "description": "UI text"}],
                    "input_modalities": ["text", "image"], "shell_type": "shell_command"},
                   {"slug": "unselected-model", "context_window": 2000}]}))
    hooks = tmp_path / "hooks.json"
    hooks.write_text('{"hooks":{}}')
    sync = tmp_path / "trust-sync.py"
    sync.write_text("# synthetic trust sync\n")
    resolver = tmp_path / "resolver"
    resolver.write_text('#!/bin/sh\nprintf "%s\\n" "Co-Authored-By: Synthetic fixture <fixture@example.invalid>"\n')
    resolver.chmod(0o755)
    args = argparse.Namespace(repo=coordinator, base=base, study=study, resources="requirements.json",
        rubric="coordinator-guidance/rubric.md", reference="coordinator-guidance/reference.md",
        guidance_dependency=["coordinator-guidance/details.txt"],
        environment_commit=environment_commit, env_manifest=coordinator / "pixi.toml",
        cli=cli, codex_home=profile, approved_hooks=hooks, trust_sync=sync, resolver=resolver,
        model="gpt-6-luna", effort="high", seconds=0, review_seconds=0, capture_execution=False,
        output=tmp_path / "seal/procedure.json", comparison_id="synthetic-comparison", role="research")
    procedure.seal(args)
    digest = procedure.sha256(args.output.read_bytes())
    manifest = procedure.load_procedure(args.output, digest)
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps({"schema_version": 1, "ready": True, "complete": True,
                                    "requirements_sha256": manifest["resources"]["sha256"]}))
    args.procedure_sha256 = digest
    args.resource_readiness = readiness
    return args, manifest


def test_seal_is_portable_and_covers_complete_fixed_procedure(comparison):
    args, manifest = comparison
    assert str(args.repo.parent) not in args.output.read_text()
    assert manifest["assessment"]["source_commit"] == git(args.repo / "assessment", "rev-parse", "HEAD")
    assert manifest["study"]["input_tree"] == git(args.study, "rev-parse", "HEAD:input")
    assert len(manifest["conditions"]) == 4
    assert manifest["study"]["rubric"] == args.rubric
    assert manifest["study"]["reference"] == args.reference
    procedure.check_sources(manifest, args.repo, args.study, args.base)
    procedure.check_host(manifest, args)
    procedure.check_readiness(manifest, args.resource_readiness)
    with pytest.raises(SystemExit, match="manifest SHA-256"):
        procedure.load_procedure(args.output, "0" * 64)


def test_depth_one_clone_fetches_only_pinned_procedure_and_runtime_objects(comparison, tmp_path):
    args, _ = comparison
    runtime = init(tmp_path / "external-runtime")
    for name in ("pixi.toml", "pixi.lock"):
        (runtime / name).write_bytes((args.repo / name).read_bytes())
    runtime_commit = commit(runtime, "test: publish external runtime")
    pin_path = args.repo / "assessment-version.json"
    pin = json.loads(pin_path.read_text())
    pin.update(environment_commit=runtime_commit, environment_repository=runtime.as_uri())
    pin_path.write_text(json.dumps(pin))
    args.base = commit(args.repo, "test: declare externally hosted runtime")
    args.output = tmp_path / "external-procedure.json"
    # Sealing itself retrieves the separately hosted assessor object.
    procedure.seal(args)
    manifest = procedure.load_procedure(args.output, procedure.sha256(args.output.read_bytes()))
    (args.study / "later-registration.json").write_text("{}\n")
    commit(args.study, "test: retain later study registration")
    (args.repo / "procedure.json").write_bytes(args.output.read_bytes())
    commit(args.repo, "test: register the sealed procedure")
    shallow = tmp_path / "shallow"
    subprocess.run(["git", "clone", "--depth", "1", args.repo.as_uri(), str(shallow)], check=True)
    selected_study = shallow / manifest["study"]["path"]
    subprocess.run(["git", "clone", "--depth", "1", args.study.as_uri(), str(selected_study)], check=True)
    for repo, revision in ((shallow, manifest["coordinator_commit"]),
                           (shallow, manifest["starting_environment"]["commit"]),
                           (shallow, runtime_commit),
                           (selected_study, manifest["study"]["commit"])):
        assert subprocess.run(["git", "cat-file", "-e", revision], cwd=repo,
                              capture_output=True).returncode != 0
    procedure.check_sources(manifest, shallow, selected_study, "HEAD")
    assert git(shallow, "rev-parse", "--is-shallow-repository") == "true"
    for repo, revision in ((shallow, manifest["coordinator_commit"]),
                           (shallow, manifest["starting_environment"]["commit"]),
                           (shallow, runtime_commit),
                           (selected_study, manifest["study"]["commit"])):
        assert git(repo, "rev-list", "--count", revision) == "1"
    assert git(shallow, "status", "--porcelain") == ""


def test_external_starting_snapshot_can_be_selected_without_local_history(comparison, tmp_path):
    args, _ = comparison
    runtime = init(tmp_path / "starting-runtime")
    for name in ("pixi.toml", "pixi.lock"):
        (runtime / name).write_bytes((args.repo / name).read_bytes())
    args.environment_commit = commit(runtime, "test: publish external starting snapshot")
    args.environment_repository = runtime.as_uri()
    args.output = tmp_path / "external-starting-procedure.json"
    procedure.seal(args)
    manifest = procedure.load_procedure(args.output, procedure.sha256(args.output.read_bytes()))
    assert manifest["starting_environment"]["repository"] == runtime.as_uri()
    assert manifest["starting_environment"]["commit"] == args.environment_commit
    procedure.check_sources(manifest, args.repo, args.study, args.base)


@pytest.mark.parametrize("name", ["judge-prompt.md", "assessment-version.json", "conditions.json",
                                 "scripts/assessment.py", "scripts/study_seed.py",
                                 "scripts/judge_workspace.py", "requirements.json"])
def test_dirty_control_or_assessment_bytes_cannot_enter_formal_run(comparison, name):
    args, manifest = comparison
    with (args.repo / name).open("a") as stream:
        stream.write("\nchanged\n")
    with pytest.raises(SystemExit, match="Formal procedure drift"):
        procedure.check_sources(manifest, args.repo, args.study, args.base)


@pytest.mark.parametrize("name", ["input/study-task.md", "input/data.csv",
                                 "coordinator-guidance/rubric.md", "coordinator-guidance/reference.md",
                                 "coordinator-guidance/details.txt"])
def test_new_study_revision_with_changed_scientific_inputs_or_guidance_is_rejected(comparison, name):
    args, manifest = comparison
    (args.study / name).write_text("Changed scientific material\n")
    commit(args.study, "test: change scientific material")
    base = commit(args.repo, "test: select changed study")
    with pytest.raises(SystemExit, match="scientific"):
        procedure.check_sources(manifest, args.repo, args.study, base)


def test_skill_revisions_and_retained_study_results_can_evolve_between_rounds(comparison):
    args, manifest = comparison
    git(args.repo, "update-index", "--add", "--cacheinfo", "160000," + "1" * 40 + ",skills")
    git(args.repo, "commit", "-m", "test: select next skill revision")
    base = git(args.repo, "rev-parse", "HEAD")
    procedure.check_sources(manifest, args.repo, args.study, base)
    (args.study / "results").mkdir()
    (args.study / "results/receipt.json").write_text("{}\n")
    commit(args.study, "test: retain previous result")
    git(args.repo, "add", "studies/example")
    git(args.repo, "commit", "-m", "test: retain study results")
    procedure.check_sources(manifest, args.repo, args.study, git(args.repo, "rev-parse", "HEAD"))


def test_skills_branch_hint_can_change_but_source_urls_remain_fixed(comparison):
    args, manifest = comparison
    modules = args.repo / ".gitmodules"
    with modules.open("a") as stream:
        stream.write('[submodule "skills"]\nbranch = con/skills-next-round\n')
    base = commit(args.repo, "test: update working skills branch hint")
    procedure.check_sources(manifest, args.repo, args.study, base)
    modules.write_text(modules.read_text().replace("example/assessor.git", "example/replacement.git"))
    with pytest.raises(SystemExit, match="submodule source configuration"):
        procedure.check_sources(manifest, args.repo, args.study, base)


def test_unrelated_guidance_artifacts_are_neither_frozen_nor_exposed_to_judges(comparison):
    args, manifest = comparison
    guidance = args.study / "coordinator-guidance"
    (guidance / "old-judgment.json").write_text('{"prior_grade":"never expose"}\n')
    (guidance / "old-preparation.bin").symlink_to("../.git/annex/objects/unavailable-key/unavailable-key")
    commit(args.study, "test: retain unrelated historical preparation")
    args.base = commit(args.repo, "test: select study with historical preparation")
    procedure.check_sources(manifest, args.repo, args.study, args.base)
    args.output = args.output.with_name("selected-only.json")
    procedure.seal(args)
    selected = procedure.load_procedure(args.output, procedure.sha256(args.output.read_bytes()))
    assert set(selected["study"]["guidance_objects"]) == {args.rubric, args.reference, *args.guidance_dependency}
    retained = procedure.retain_inputs(selected, args.repo, args.study, args.output.parent / "selected-inputs")
    assert not (retained / "coordinator-guidance/old-judgment.json").exists()
    assert not (retained / "coordinator-guidance/old-preparation.bin").is_symlink()


def test_selected_annex_dependency_is_pinned_by_key_and_materialized_only_when_needed(comparison):
    args, manifest = comparison
    dependency = "coordinator-guidance/reference-data.bin"
    payload = args.study / dependency
    content = b"synthetic reference content\n" * 200
    payload.write_bytes(content)
    git(args.study, "annex", "init", "selected-guidance-fixture")
    git(args.study, "annex", "add", "--force", "--", dependency)
    key = git(args.study, "annex", "lookupkey", dependency)
    commit(args.study, "test: add selected annex guidance")
    args.base = commit(args.repo, "test: select annex guidance")
    args.guidance_dependency.append(dependency)
    args.output = args.output.with_name("annex-procedure.json")
    procedure.seal(args)
    selected = procedure.load_procedure(args.output, procedure.sha256(args.output.read_bytes()))
    record = selected["study"]["guidance_objects"][dependency]
    assert record["annex_key"] == key
    assert record["sha256"] == procedure.sha256(content)
    retained = procedure.retain_inputs(selected, args.repo, args.study, args.output.parent / "annex-inputs")
    assert (retained / dependency).read_bytes() == content
    assert not (retained / dependency).is_symlink()
    git(args.study, "annex", "drop", "--force", "--", dependency)
    procedure.check_sources(selected, args.repo, args.study, args.base)
    args.output = args.output.with_name("unavailable-annex-procedure.json")
    procedure.seal(args)
    with pytest.raises(SystemExit, match="Selected annex guidance is unavailable"):
        procedure.retain_inputs(selected, args.repo, args.study, args.output.parent / "missing-annex-inputs")


@pytest.mark.parametrize("setting,value", [("model", "other"), ("effort", "low"), ("seconds", 90),
                                           ("review_seconds", 30), ("capture_execution", True)])
def test_common_launch_settings_cannot_drift(comparison, setting, value):
    args, manifest = comparison
    setattr(args, setting, value)
    with pytest.raises(SystemExit, match="research settings"):
        procedure.check_settings(manifest, args)


def test_host_trust_paths_can_change_but_common_runtime_and_profile_cannot(comparison):
    args, manifest = comparison
    config = args.codex_home / "config.toml"
    config.write_text('[hooks.state."/fresh/clone/hook:0"]\ntrusted_hash="same-approved-bytes"\n')
    procedure.check_host(manifest, args)
    config.write_text('[skills]\n[[skills.config]]\npath="/host/disabled/SKILL.md"\nenabled=false\n')
    procedure.check_host(manifest, args)
    config.write_text('[skills]\n[[skills.config]]\npath="/other/disabled/SKILL.md"\nenabled=false\n')
    procedure.check_host(manifest, args)
    config.write_text('[features]\nweb_search=false\n')
    with pytest.raises(SystemExit, match="native runtime"):
        procedure.check_host(manifest, args)
    config.write_text('[skills]\n')
    args.cli.write_text("Changed client executable\n")
    with pytest.raises(SystemExit, match="native runtime"):
        procedure.check_host(manifest, args)


def test_model_cache_refresh_and_other_model_changes_do_not_change_selected_contract(comparison):
    args, manifest = comparison
    cache = args.codex_home / "models_cache.json"
    contents = json.loads(cache.read_text())
    contents.update(fetched_at="2026-10-15T00:00:00Z", etag="refreshed", identity="changed-account-metadata")
    contents["models"][0].update(description="New UI text", display_name="New label", priority=99)
    contents["models"][0]["supported_reasoning_levels"][0]["description"] = "Updated explanation"
    contents["models"][0]["input_modalities"].reverse()
    contents["models"][1]["context_window"] = 99999
    cache.write_text(json.dumps(contents, indent=4))
    procedure.check_host(manifest, args)
    procedure.check_native(manifest, args.cli, args.codex_home)


def test_fresh_checkout_project_trust_does_not_change_formal_profile(comparison):
    args, manifest = comparison
    config = args.codex_home / "config.toml"
    for path in ("/fresh/clone", "/another/fresh/clone"):
        with config.open("a") as stream:
            stream.write(f'\n[projects."{path}"]\ntrust_level="trusted"\n')
        procedure.check_host(manifest, args)
        procedure.check_native(manifest, args.cli, args.codex_home)


@pytest.mark.parametrize("project", [
    '[projects."/fresh/clone"]\ntrust_level="untrusted"\n',
    '[projects."/fresh/clone"]\ntrust_level="trusted"\nmodel="other"\n',
    '[projects."relative/clone"]\ntrust_level="trusted"\n',
])
def test_project_denial_or_other_settings_cannot_bypass_profile_freeze(comparison, project):
    args, manifest = comparison
    with (args.codex_home / "config.toml").open("a") as stream:
        stream.write("\n" + project)
    with pytest.raises(SystemExit, match="native runtime/profile"):
        procedure.check_host(manifest, args)
    with pytest.raises(SystemExit, match="native profile settings"):
        procedure.check_native(manifest, args.cli, args.codex_home)


@pytest.mark.parametrize("field,value", [("context_window", 2000), ("shell_type", "new_shell"),
    ("model_messages", {"persistent_instructions": "Changed instructions"}),
    ("supported_reasoning_levels", [{"effort": "low", "description": "New UI text"}])])
def test_selected_model_semantic_changes_fail_the_freeze(comparison, field, value):
    args, manifest = comparison
    cache = args.codex_home / "models_cache.json"
    contents = json.loads(cache.read_text())
    contents["models"][0][field] = value
    cache.write_text(json.dumps(contents))
    with pytest.raises(SystemExit, match="native runtime"):
        procedure.check_host(manifest, args)
    with pytest.raises(SystemExit, match="native model contract"):
        procedure.check_native(manifest, args.cli, args.codex_home)


def test_formal_readiness_requires_matching_complete_success(comparison):
    args, manifest = comparison
    receipt = json.loads(args.resource_readiness.read_text())
    receipt["ready"] = False
    args.resource_readiness.write_text(json.dumps(receipt))
    with pytest.raises(SystemExit, match="not ready"):
        procedure.check_readiness(manifest, args.resource_readiness)
    receipt.update(ready=True, requirements_sha256="0" * 64)
    args.resource_readiness.write_text(json.dumps(receipt))
    with pytest.raises(SystemExit, match="readiness requirements"):
        procedure.check_readiness(manifest, args.resource_readiness)


def test_retained_guidance_uses_git_blobs_even_after_worktree_edit(comparison):
    args, manifest = comparison
    (args.study / args.reference).write_text("Mutable replacement\n")
    destination = procedure.retain_inputs(manifest, args.repo, args.study, args.output.parent / "frozen-inputs")
    assert (destination / args.reference).read_text() == "Consider [details](details.txt).\n"
    assert (destination / "coordinator-guidance/details.txt").read_text() == "Immutable comparison evidence.\n"


@pytest.mark.parametrize("role", ["research", "judge"])
def test_formal_native_launch_checks_frozen_inputs_and_records_status(comparison, tmp_path, role):
    args, manifest = comparison
    worker = tmp_path / "worker"
    seed.make_seed(args.repo, args.base, args.study, worker, "codex/fixture", "baseline", args.resolver)
    prompt = tmp_path / "prompt.md"
    if role == "research":
        prompt.write_bytes(seed.research_prompt(worker))
    else:
        # Completed research objects are allowed to evolve their own environment.
        with (worker / "pixi.toml").open("a") as stream:
            stream.write('\n[pypi-dependencies]\nnew-library="*"\n')
        result = commit(worker, "test: record evolved scientific environment")
        retained = procedure.retain_inputs(manifest, args.repo, args.study, args.output.parent / "frozen-inputs")
        rendered = prepare.render_judge_prompt(retained / "judge-prompt.md", worker / "input/study-task.md",
            result, tmp_path, retained / args.reference, retained / args.rubric)
        from worker_end_state import capture_worker_end_state
        stop_receipt = tmp_path / "worker-end-state.json"
        stop_receipt.write_text(json.dumps(capture_worker_end_state(worker)))
        prompt.write_text(rendered.read_text() + procedure.replay_instruction(manifest) +
                          procedure.worker_credit_instruction(stop_receipt))
    command = [sys.executable, str(args.repo / "scripts/launch_native_probe.py"),
        "--checkout", str(worker), "--prompt", str(prompt), "--output", str(tmp_path / "native"),
        "--cli", str(args.cli), "--role", role, "--review-seconds", "0",
        "--assessment-source", str(args.repo / "assessment"),
        "--assessment-pin", str(args.repo / "assessment-version.json"),
        "--run-mode", "formal", "--procedure", str(args.output),
        "--procedure-sha256", args.procedure_sha256, "--procedure-study", str(args.study),
        "--resource-readiness", str(args.resource_readiness)]
    if role == "judge":
        workspace = tmp_path / "judgment"
        judge_workspace.initialize(workspace, worker, args.resolver)
        command += ["--worker-end-state", str(stop_receipt), "--judge-workspace", str(workspace)]
    result = subprocess.run(command, env=dict(os.environ, CODEX_HOME=str(args.codex_home)),
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    receipt = json.loads((tmp_path / "native/result.json").read_text())
    assert receipt["procedure"]["status"] == "formal-verified"
    assert receipt["procedure"]["procedure_sha256"] == args.procedure_sha256
    if role == "judge":
        assert receipt["cwd"] == str(workspace)
        assert receipt["target_unchanged"] is True
        # A second attempt receives a fresh session repository.
        workspace = tmp_path / "changed-judgment"
        judge_workspace.initialize(workspace, worker, args.resolver)
        command[command.index("--judge-workspace") + 1] = str(workspace)
        prompt.write_text(prompt.read_text() + "\nChanged judging instruction\n")
        command[command.index("--output") + 1] = str(tmp_path / "changed-native")
        result = subprocess.run(command, env=dict(os.environ, CODEX_HOME=str(args.codex_home)),
                                capture_output=True, text=True)
        assert result.returncode != 0
        assert "rendered judge instructions" in result.stderr
        assert not (tmp_path / "changed-native").exists()


def test_replay_is_exact_target_single_attempt_and_uses_fixed_comparison_settings(comparison, tmp_path):
    args, manifest = comparison
    output = tmp_path / "judge-output"
    output.mkdir()
    arguments = ["--path", str(args.study), "--entry", "pixi run reproduce",
                 "--outputs", "results/*.tsv",
                 "--workdir", str(output / "replay"), "--output", str(output / "replay.json")]
    with pytest.raises(SystemExit, match="replay rtol"):
        procedure.replay_arguments(manifest, arguments + ["--rtol", "0.5"], args.study, output)
    with pytest.raises(SystemExit, match="exact target"):
        procedure.replay_arguments(manifest, arguments, args.repo, output)
    assert not (output / "formal-replay-attempt.json").exists()
    assert procedure.replay_arguments(manifest, arguments, args.study, output) == arguments
    with pytest.raises(SystemExit, match="already consumed"):
        procedure.replay_arguments(manifest, arguments, args.study, output)
    assert procedure.replay_arguments(manifest, ["--help"], args.study, output) == ["--help"]


def test_missing_output_selection_keeps_allowance_and_participant_input(comparison, tmp_path, capsys):
    args, manifest = comparison
    participant = args.study / "input/participants.tsv"
    participant.write_text("participant_id\tvalue\nsub-01\t2\n")
    generated = args.study / "results/summary.tsv"
    generated.parent.mkdir()
    generated.write_text("mean\n2\n")
    output = tmp_path / "judge-output"
    output.mkdir()
    workdir = output / "replay"
    arguments = ["--path", str(args.study), "--entry", "python analysis.py",
                 "--workdir", str(workdir), "--output", str(output / "replay.json")]
    before = {path: path.read_bytes() for path in (participant, generated)}
    with pytest.raises(SystemExit) as error:
        procedure.replay_arguments(manifest, arguments, args.study, output)
    assert error.value.code == 2
    assert "--outputs" in capsys.readouterr().err
    assert not (output / "formal-replay-attempt.json").exists()
    assert not workdir.exists()
    assert all(path.read_bytes() == content for path, content in before.items())
    selected = arguments + ["--outputs", "results/summary.tsv"]
    assert procedure.replay_arguments(manifest, selected, args.study, output) == selected
    receipt = json.loads((output / "formal-replay-attempt.json").read_text())
    assert receipt["arguments"] == selected


def test_prepare_routes_judge_setup_and_execution_to_separate_repository(comparison, tmp_path, monkeypatch):
    args, _ = comparison
    result_repo = tmp_path / "submitted-result"
    seed.make_seed(args.repo, args.base, args.study, result_repo, "codex/result", "baseline", args.resolver)
    target_commit = git(result_repo, "rev-parse", "HEAD")
    target = tmp_path / "exact-target"
    evidence = tmp_path / "judge-evidence"
    prepared = []
    actual_run = prepare.run

    def host_run(argv, cwd, capture=False):
        command = [str(value) for value in argv]
        if command[0] == "pixi":
            # The host runtime/annex transport is orthogonal to session routing.
            return "{}" if capture else None
        if len(command) > 1 and command[1].endswith("/prepare_checkout.py"):
            prepared.append(Path(command[command.index("--checkout") + 1]))
            return None
        return actual_run(argv, cwd, capture)

    monkeypatch.setattr(prepare, "run", host_run)
    monkeypatch.setattr(prepare, "__file__", str(args.repo / "scripts/prepare_launch.py"))
    coordinator_profile = tmp_path / "coordinator-profile"
    coordinator_profile.mkdir()
    monkeypatch.setenv("CODEX_HOME", str(coordinator_profile))
    args.resolver.write_text(f"#!{sys.executable}\nimport os\n"
        f"assert os.environ['CODEX_HOME'] == {str(coordinator_profile)!r}\n"
        "print('Co-Authored-By: Synthetic fixture <fixture@example.invalid>')\n")
    monkeypatch.setattr(sys, "argv", ["prepare_launch.py", "--role", "judge",
        "--host-config", str(tmp_path / "no-defaults.json"), "--repo", str(result_repo),
        "--base", target_commit, "--branch", "codex/judge-fixture", "--clone-path", str(target),
        "--evidence", str(evidence), "--study", str(args.study), "--env-manifest", str(args.env_manifest),
        "--approved-hooks", str(args.approved_hooks), "--trust-sync", str(args.trust_sync),
        "--resolver", str(args.resolver), "--checkpoint-repo", "example/checkpoints",
        "--annex-git-url", str(args.study), "--annex-url", "fixture://annex",
        "--cli", str(args.cli), "--codex-home", str(args.codex_home), "--review-seconds", "0"])
    prepare.main()

    workspace = evidence / "judgment"
    assert prepared == [workspace]
    native = json.loads((evidence / "native/result.json").read_text())
    assert native["cwd"] == str(workspace)
    assert native["target"]["target_path"] == str(target)
    assert native["target"]["target_commit"] == target_commit
    assert native["target_unchanged"] is True
    assert git(target, "rev-parse", "HEAD") == target_commit
    assert git(target, "status", "--porcelain") == ""
    assert (workspace / "assessment.txt").is_file()
    assert not (target / "assessment.txt").exists()
    assert not (target / ".codex").exists()
    assert not (target / ".entire").exists()


@pytest.mark.parametrize("extra", [["--keep-outputs"], ["--url", "https://example.invalid/object"]])
def test_replay_cannot_keep_old_outputs_or_clone_an_unpinned_remote(comparison, tmp_path, extra):
    args, manifest = comparison
    with pytest.raises(SystemExit):
        procedure.replay_arguments(manifest, ["--path", str(args.study), "--entry", "make",
            "--outputs", "results/*.tsv",
            "--workdir", str(tmp_path / "replay"), "--output", str(tmp_path / "result.json"), *extra],
            args.study, tmp_path)
    assert not (tmp_path / "formal-replay-attempt.json").exists()


def test_optional_evals_can_stay_absent_but_required_or_initialized_modules_must_match():
    assert procedure.assessment_modules_match(b"-aaaa evals\n bbbb rules\n")
    assert not procedure.assessment_modules_match(b"+aaaa evals\n")
    assert not procedure.assessment_modules_match(b"-bbbb rules\n")


def test_host_configuration_defaults_follow_repository_name():
    assert procedure.default_host_config(Path("/work/stamped-in-practice")) == (
        Path.home() / ".config/stamped-in-practice/launch.json")
    assert procedure.default_host_config(Path("/work/stamped-ai-research-next")) == (
        Path.home() / ".config/stamped-ai-research-next/launch.json")


def test_prepare_refuses_drift_before_creating_a_worker_or_launch_evidence(comparison, tmp_path):
    args, manifest = comparison
    (args.repo / "judge-prompt.md").write_text("Changed judge instruction\n")
    command = [sys.executable, str(args.repo / "scripts/prepare_launch.py"),
        "--host-config", str(tmp_path / "absent-host-config.json"),
        "--repo", str(args.repo), "--base", args.base, "--study", str(args.study),
        "--branch", "codex/should-not-start", "--clone-path", str(tmp_path / "worker"),
        "--evidence", str(tmp_path / "launch-evidence"), "--prepare-only",
        "--checkpoint-repo", "example/checkpoints", "--annex-git-url", "git@example.invalid:objects",
        "--annex-url", "file:///unused-fixture", "--run-mode", "formal",
        "--procedure", str(args.output), "--procedure-sha256", args.procedure_sha256,
        "--resource-readiness", str(args.resource_readiness)]
    for name in ("env_manifest", "cli", "codex_home", "approved_hooks", "trust_sync", "resolver"):
        command += ["--" + name.replace("_", "-"), str(getattr(args, name))]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0
    assert "working judge-prompt.md" in result.stderr
    assert not (tmp_path / "worker").exists()
    assert not (tmp_path / "launch-evidence").exists()


def test_worker_credit_rule_binds_the_exact_external_receipt(tmp_path):
    receipt = tmp_path / "worker-end-state.json"
    receipt.write_text('{"head_commit":"fixture"}\n')
    first = procedure.worker_credit_instruction(receipt)
    assert procedure.sha256(receipt.read_bytes()) in first
    assert "recorded worker stop" in first
    assert "do not establish worker compliance" in first
    receipt.write_text('{"head_commit":"replacement"}\n')
    assert procedure.worker_credit_instruction(receipt) != first


def test_formal_runner_applies_replay_constraints_before_dispatch(frozen_runner, monkeypatch, tmp_path):
    import assessment
    calls, source, runtime = frozen_runner
    pin = json.loads(Path(os.environ["STAMPED_ASSESSMENT_PIN"]).read_text())
    manifest = {"assessment": pin, "fixed_files": {
        "scripts/assessment.py": procedure.sha256(Path(assessment.__file__).read_bytes())}}
    monkeypatch.setenv("STAMPED_PROCEDURE", str(tmp_path / "procedure.json"))
    monkeypatch.setenv("STAMPED_PROCEDURE_SHA256", "registered-seal")
    monkeypatch.setenv("STAMPED_JUDGE_TARGET", str(tmp_path / "target"))
    monkeypatch.setenv("STAMPED_JUDGE_COMMIT", "exact-result")
    monkeypatch.setenv("STAMPED_JUDGE_OUTPUT", str(tmp_path / "judgment"))
    monkeypatch.setattr(procedure, "load_procedure", lambda path, digest: manifest)
    monkeypatch.setattr(procedure, "git", lambda *args: "exact-result")
    checked = []
    def constrained(frozen, arguments, target, output):
        checked.append((frozen, arguments, target, output))
        return ["--path", str(target), "--entry", "documented-entry"]
    monkeypatch.setattr(procedure, "replay_arguments", constrained)
    monkeypatch.setattr(sys, "argv", ["assessment.py", "fresh-rerun", "requested-arguments"])
    with pytest.raises(SystemExit) as result:
        assessment.main()
    assert result.value.code == 7
    assert checked == [(manifest, ["requested-arguments"], tmp_path / "target", tmp_path / "judgment")]
    assert calls[-1][0][-4:] == ["--path", str(tmp_path / "target"), "--entry", "documented-entry"]
