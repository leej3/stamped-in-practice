"""Launcher checks with disposable Git/annex fixtures; no live research agent."""
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import threading
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import launch_native_probe as launch
import prepare_launch as prepare
import study_seed as seed
import research_conditions as conditions
import judge_workspace


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *map(str, args)], text=True).strip()


def init(path):
    path.mkdir(parents=True)
    git(path, "init", "-b", "main")
    git(path, "config", "user.name", "Launcher fixture")
    git(path, "config", "user.email", "fixture@example.invalid")
    git(path, "config", "core.hooksPath", str(path / ".git/empty-hooks"))
    return path


def commit(path, message):
    git(path, "add", "--all")
    git(path, "commit", "-m", message)
    return git(path, "rev-parse", "HEAD")


@pytest.fixture
def source_repositories(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "file")
    # make_seed's commit uses real caller attribution in production; fixtures
    # provide a deterministic resolver and synthetic authorship in temp repos.
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Launcher fixture")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "fixture@example.invalid")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "Launcher fixture")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "fixture@example.invalid")
    coordinator = init(tmp_path / "coordinator")
    (coordinator / "conditions.json").write_bytes((ROOT / "conditions.json").read_bytes())
    (coordinator / "pixi.toml").write_text('''[workspace]
name = "fixture"
channels = ["conda-forge"]
platforms = ["osx-arm64", "linux-64"]
[dependencies]
python = ">=3.11"
[tasks]
launch = "python scripts/prepare_launch.py"
[feature.extra.dependencies]
numpy = "*"
[feature.extra.tasks]
assessment = "python private-coordinator.py"
''')
    (coordinator / "reference.txt").write_text("COORDINATOR_ANSWER_SENTINEL")
    (coordinator / "previous-output.txt").write_text("PRIOR_OUTPUT_SENTINEL")
    old = commit(coordinator, "test: add forbidden coordinator history")
    (coordinator / "reference.txt").unlink()
    commit(coordinator, "test: remove answer from current tree")
    study = init(coordinator / "studies/example")
    (study / "input/data").mkdir(parents=True)
    (study / "input/study-task.md").write_text("Answer the scientific question with these observations.\n")
    (study / "input/sources.json").write_text('{"source": "synthetic fixture"}\n')
    (study / "input/data/observations.csv").write_text("x,y\n1,2\n2,3\n")
    (study / "coordinator-guidance").mkdir()
    (study / "coordinator-guidance/answer.txt").write_text("STUDY_REFERENCE_SENTINEL")
    (study / "results/previous").mkdir(parents=True)
    (study / "results/previous/output.txt").write_text("STUDY_PREVIOUS_OUTPUT_SENTINEL")
    (study / "removed-answer.txt").write_text("REMOVED_STUDY_ANSWER_SENTINEL")
    study_old = commit(study, "test: retain previous study evidence")
    (study / "removed-answer.txt").unlink()
    git(study, "annex", "init", "input-fixture")
    payload = study / "input/data/annexed.bin"
    payload.write_bytes(b"synthetic observations\n" * 100)
    git(study, "annex", "add", "--force", "--", "input/data/annexed.bin")
    key = git(study, "annex", "lookupkey", "input/data/annexed.bin")
    study_ref = commit(study, "test: commit selected study inputs")
    git(study, "remote", "add", "origin", "git@github.com:example/studies.git")
    git(study, "config", "remote.origin.annex-ignore", "true")
    skills = init(tmp_path / "skills-source")
    for name in seed.RESEARCH_SKILLS + ("assess-alignment-with-stamped-principles",):
        path = skills / "skills" / name / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(f"---\nname: {name}\ndescription: Fixture guidance.\n---\nSkill text.\n")
    evaluations = init(tmp_path / "evals-source")
    (evaluations / "calibration.txt").write_text("Optional development fixtures.\n")
    eval_ref = commit(evaluations, "test: retain optional evaluation fixtures")
    (skills / ".gitmodules").write_text(
        '[submodule "evals"]\n\tpath = evals\n\turl = ' + str(evaluations) + '\n')
    (skills / "evals").mkdir()
    git(skills, "add", "--all")
    git(skills, "update-index", "--add", "--cacheinfo", f"160000,{eval_ref},evals")
    skill_ref = commit(skills, "test: pin fixture skills")
    # The frozen-judge fixture needs this dependency; research clones do not.
    git(skills, "submodule", "update", "--init", "--", "evals")
    (coordinator / ".gitmodules").write_text(
        '[submodule "studies/example"]\n\tpath = studies/example\n\turl = ' + str(study) +
        '\n[submodule "skills"]\n\tpath = skills\n\turl = ' + str(skills) + '\n')
    (coordinator / "skills").mkdir()
    git(coordinator, "add", "--all")
    git(coordinator, "update-index", "--add", "--cacheinfo", f"160000,{skill_ref},skills")
    git(coordinator, "commit", "-m", "test: pin study and skills")
    base = git(coordinator, "rev-parse", "HEAD")
    git(coordinator, "remote", "add", "origin", "git@github.com:example/coordinator.git")
    resolver = tmp_path / "resolver"
    resolver.write_text('#!/bin/sh\nprintf "%s\\n" "Co-Authored-By: Synthetic fixture <fixture@example.invalid>"\n')
    resolver.chmod(0o755)
    forbidden = [git(coordinator, "rev-parse", old + ":reference.txt"),
                 git(coordinator, "rev-parse", base + ":previous-output.txt"),
                 git(study, "rev-parse", study_ref + ":coordinator-guidance/answer.txt"),
                 git(study, "rev-parse", study_ref + ":results/previous/output.txt"),
                 git(study, "rev-parse", study_old + ":removed-answer.txt")]
    return coordinator, study, base, resolver, key, forbidden, skills


def make_worker(tmp_path, sources, condition="baseline"):
    coordinator, study, base, resolver, *_ = sources
    checkout = tmp_path / ("worker-" + condition)
    receipt = seed.make_seed(coordinator, base, study, checkout, "codex/fixture-" + condition,
                             condition, resolver)
    return checkout, receipt


@pytest.mark.parametrize("condition", conditions.CONDITION_CHOICES)
def test_input_boundary_excludes_tree_history_objects_and_unassigned_skills(tmp_path, source_repositories, condition):
    worker, receipt = make_worker(tmp_path, source_repositories, condition)
    coordinator, study, base, resolver, key, forbidden, _ = source_repositories
    assert receipt["study_commit"] == git(study, "rev-parse", "HEAD")
    assert receipt["study_input_tree"] == git(study, "rev-parse", "HEAD:input")
    assert len(git(worker, "rev-list", "--parents", "HEAD").split()) == 1
    assert not (worker / ".git/objects/info/alternates").exists()
    assert not (worker / "assessment").exists()
    assert not (worker / "coordinator-guidance").exists()
    assert not (worker / "results").exists()
    assert not (worker / "AGENTS.md").exists()
    for oid in forbidden:
        assert subprocess.run(["git", "-C", str(worker), "cat-file", "-e", oid],
                              capture_output=True).returncode != 0
    reachable = git(worker, "rev-list", "--objects", "--all")
    assert not any(oid in reachable for oid in forbidden)
    if conditions.canonical_condition(condition) != "stamped-explicit":
        assert not (worker / "skills").exists()
        assert not (worker / ".agents").exists()
    else:
        assert (worker / "skills/.git").is_file()
        assert not (worker / "skills/evals/calibration.txt").exists()
        assert git(worker / "skills", "submodule", "status", "evals").startswith("-")
        assert {p.name for p in (worker / ".agents/skills").iterdir()} == set(seed.RESEARCH_SKILLS)
    manifest = seed.tomlkit.loads((worker / "pixi.toml").read_text())
    assert "tasks" not in manifest
    assert "tasks" not in manifest["feature"]["extra"]
    assert manifest["dependencies"]["python"] == ">=3.11"
    assert manifest["feature"]["extra"]["dependencies"]["numpy"] == "*"
    assert key in json.dumps(receipt)
    assert "*" not in git(worker, "config", "remote.origin.fetch")
    # Recover real annex payloads without fetching the source's Git history.
    git(worker, "annex", "init", "worker-fixture")
    git(worker, "remote", "add", "input-source", study)
    git(worker, "annex", "get", "--from", "input-source", "--", "input")
    assert git(worker, "annex", "lookupkey", "input/data/annexed.bin") == key
    assert (worker / "input/data/annexed.bin").read_bytes() == (study / "input/data/annexed.bin").read_bytes()
    assert not git(worker, "status", "--porcelain")
    seed.audit_seed(worker)
    for oid in forbidden:
        assert subprocess.run(["git", "-C", str(worker), "cat-file", "-e", oid],
                              capture_output=True).returncode != 0


def test_baseline_rejects_readable_skills_even_without_catalog_entry(tmp_path, source_repositories):
    worker, _ = make_worker(tmp_path, source_repositories)
    (worker / "skills").mkdir()
    (worker / "skills/leak.md").write_text("STAMPED guidance")
    with pytest.raises(SystemExit, match="readable study skills"):
        seed.audit_seed(worker)


def test_execution_logging_requires_explicit_request(tmp_path):
    (tmp_path / "input").mkdir()
    (tmp_path / "input/study-task.md").write_text("Investigate the question.\n")
    ordinary = seed.research_prompt(tmp_path).decode()
    requested = seed.research_prompt(tmp_path, capture_execution=True).decode()
    assert "duct" not in ordinary
    assert "duct under `logs/`" in requested
    assert ordinary.startswith("Investigate the question.")
    assert "`results/`" in ordinary


def test_all_conditions_receive_the_same_environment_and_publication_policy(tmp_path):
    (tmp_path / "input").mkdir()
    (tmp_path / "input/study-task.md").write_text("Investigate the question.\n")
    policy_prompts = []
    for condition in ("baseline", "discover-general", "discover-science", "stamped-explicit"):
        assigned = conditions.assignment((ROOT / "conditions.json").read_bytes(), condition)
        (tmp_path / "worker-input.json").write_text(json.dumps({"assignment": assigned}))
        prompt = seed.research_prompt(tmp_path).decode()
        addition = assigned["additional_prompt"]
        common = prompt.removesuffix("\n" + addition + "\n") if addition else prompt
        policy_prompts.append(common)
    assert len(set(policy_prompts)) == 1
    assert "Keep the working `pixi.lock` ignored" in common
    assert "one commit above the final task commit" in common
    assert "return to the task branch" in common
    assert "artifacts through the configured remotes is authorized" in common


def test_condition_is_pinned_and_observations_are_not_invented(tmp_path, source_repositories):
    coordinator = source_repositories[0]
    original = (coordinator / "conditions.json").read_bytes()
    (coordinator / "conditions.json").write_text("Uncommitted replacement")
    worker, receipt = make_worker(tmp_path, source_repositories, "discover-general")
    assigned = receipt["assignment"]
    assert receipt["version"] == 2
    assert assigned["config_sha256"] == seed.hashlib.sha256(original).hexdigest()
    assert assigned["additional_prompt"] == (
        "Find and install skills you consider useful for completing this task, "
        "and use them where appropriate.")
    assert seed.research_prompt(worker).decode().endswith(assigned["additional_prompt"] + "\n")
    profile = tmp_path / "unused-profile"
    observed = launch.skill_observations(worker, profile)
    assert observed["status"] == "not-reviewed"
    assert observed["queries"] is None
    assert observed["loaded_instructions"] is None
    assert observed["application_evidence"] is None
    assert observed["installed_entrypoints"] == []


@pytest.mark.parametrize("condition", ["baseline", "skills"])
def test_legacy_snapshots_keep_their_prompt(tmp_path, source_repositories, condition):
    coordinator, study, _, resolver, *_ = source_repositories
    (coordinator / "conditions.json").unlink()
    base = commit(coordinator, "test: emulate pre-condition coordinator")
    worker = tmp_path / "legacy-worker"
    receipt = seed.make_seed(coordinator, base, study, worker, "codex/legacy", condition, resolver)
    assert receipt["version"] == 1
    assert receipt["condition"] == condition
    assert "assignment" not in receipt
    prompt = seed.research_prompt(worker).decode()
    assert prompt == (worker / "input/study-task.md").read_text() + (
        "\nCommon execution resources\n\n"
        "Use the root Pixi environment; add dependencies as needed. "
        "Keep analysis outputs under `results/` in this experiment repository. "
        "Retain failed attempts and annex large outputs/logs.\n")
    with pytest.raises(SystemExit, match="predates the four-condition"):
        seed.make_seed(coordinator, base, study, tmp_path / "bad-new-condition",
                       "codex/new", "discover-science", resolver)


def test_baseline_has_no_discovery_addition_and_explicit_has_named_invocation():
    content = (ROOT / "conditions.json").read_bytes()
    baseline = conditions.assignment(content, "baseline")
    assert baseline["additional_prompt"] == ""
    assert baseline["supplied_skills"] == []
    for name in ("discover-general", "discover-science"):
        assert conditions.assignment(content, name)["supplied_skills"] == []
    explicit = conditions.assignment(content, "stamped-explicit")
    assert "do-full-research-loop" in explicit["additional_prompt"]
    assert explicit["supplied_skills"] == list(seed.RESEARCH_SKILLS)
    assert conditions.assignment(content, "skills")["condition"] == "stamped-explicit"


def test_input_boundary_rejects_links_to_coordinator_material(tmp_path, source_repositories):
    coordinator, study, base, resolver, *_ = source_repositories
    (study / "input/answer-link").symlink_to("../coordinator-guidance/answer.txt")
    commit(study, "test: add forbidden source link")
    base = commit(coordinator, "test: update fixture study pin")
    with pytest.raises(SystemExit, match="Only annex payload links"):
        seed.make_seed(coordinator, base, study, tmp_path / "bad-worker", "codex/bad", "baseline", resolver)


def test_judge_receives_original_brief_and_separate_optional_reference(tmp_path):
    study = tmp_path / "study.md"
    study.write_text("Check the original scientific target.\n")
    reference = tmp_path / "reference.md"
    reference.write_text("A reference is comparison evidence, not the required answer.\n")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    template = tmp_path / "judge-prompt.md"
    template.write_text("Inspect $TARGET_COMMIT.\n")
    rendered = prepare.render_judge_prompt(template, study, "a" * 40, evidence, reference)
    study.write_text("Later edits must not redefine the task.\n")
    assert "Check the original scientific target." in rendered.read_text()
    assert "Optional coordinator evaluation guidance" in rendered.read_text()
    assert (evidence / "study.md").read_text() == "Check the original scientific target.\n"
    assert json.loads((evidence / "study.json").read_text())["sha256"] == prepare.hashlib.sha256(
        (evidence / "study.md").read_bytes()).hexdigest()


def test_roles_do_not_leak_stamped_guidance():
    assert launch.selected_skills("research", "baseline") == set()
    assert launch.selected_skills("research", "discover-general") == set()
    assert launch.selected_skills("research", "discover-science") == set()
    assert "assess-alignment-with-stamped-principles" not in launch.selected_skills("research", "skills")
    assert launch.selected_skills("judge", "baseline") == {
        "assess-alignment-with-stamped-principles", "stamped-conventions"}


def test_review_does_not_terminate_worker(tmp_path):
    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(.15)"])
    try:
        assert not launch.wait_for_worker(process, tmp_path, 0, .01)
        assert process.returncode == 0
        assert json.loads((tmp_path / "review.json").read_text())["terminated"] is False
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()


def test_explicit_limit_remains_available(tmp_path):
    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        assert launch.wait_for_worker(process, tmp_path, .01, 0)
        assert not (tmp_path / "review.json").exists()
    finally:
        process.kill()
        process.wait()


def test_changed_external_assessor_is_rejected(tmp_path, source_repositories):
    skills = source_repositories[-1]
    pin = tmp_path / "pin.json"
    pin.write_text(json.dumps({"source_commit": "0" * 40}))
    with pytest.raises(SystemExit, match="wrong revision"):
        launch.check_assessment(skills, pin)


def test_uninitialized_assessment_dependency_is_rejected(tmp_path, monkeypatch):
    pin = tmp_path / "pin.json"
    pin.write_text(json.dumps({"source_commit": "a" * 40}))
    def output(argv, **kwargs):
        if "rev-parse" in argv:
            return "a" * 40 + "\n"
        return b"-abc rules\n" if "submodule" in argv else b""
    monkeypatch.setattr(launch.subprocess, "check_output", output)
    with pytest.raises(SystemExit, match="dependencies differ"):
        launch.check_assessment(tmp_path, pin)


@pytest.fixture
def fake_cli(tmp_path):
    cli = tmp_path / "fake-codex"
    cli.write_text(f"#!{sys.executable}\n" + '''
import json, os, pathlib, sys, tomllib
args = sys.argv[1:]
assert "CODEX_THREAD_ID" not in os.environ
assert "PIXI_PROJECT_MANIFEST" not in os.environ
assert "PIXI_IN_SHELL" not in os.environ
assert "project_doc_max_bytes=0" in args
if "debug" in args:
    config = next(x for x in args if x.startswith("skills.config="))
    entries = tomllib.loads(config)["skills"]["config"]
    for item in entries:
        if item["enabled"]:
            assert pathlib.Path(item["path"]).is_file()
            print("- " + pathlib.Path(item["path"]).parent.name + ": fixture skill (file: " + item["path"] + ")")
    if os.environ.get("FAKE_UNEXPECTED_SKILL"):
        print("- unrelated-skill: Host guidance (file: /unexpected/SKILL.md)")
else:
    if "STAMPED_ASSESSMENT_SOURCE" in os.environ:
        source = pathlib.Path(os.environ["STAMPED_ASSESSMENT_SOURCE"])
        pin = json.loads(pathlib.Path(os.environ["STAMPED_ASSESSMENT_PIN"]).read_text())
        assert (source / "skills/assess-alignment-with-stamped-principles/SKILL.md").is_file()
        assert pin["source_commit"]
        workspace = pathlib.Path(os.environ["STAMPED_JUDGE_OUTPUT"])
        target = pathlib.Path(os.environ["STAMPED_JUDGE_TARGET"])
        assert workspace == pathlib.Path.cwd() != target
        assert pathlib.Path(args[args.index("-C") + 1]) == workspace
        assert (workspace / ".git").is_dir()
        (workspace / "assessment.txt").write_text("Fixture assessment artifact.\\n")
        if os.environ.get("FAKE_CHANGE_TARGET"):
            (target / "input/study-task.md").write_text("Unauthorized target edit.\\n")
    sys.stdin.read()
    pathlib.Path(args[args.index("-o") + 1]).write_text("Fixture report, not a live judgment.\\n")
    print(json.dumps({"type": "thread.started", "thread_id": "fake-test-session"}))
    print("fixture stderr", file=sys.stderr)
''')
    cli.chmod(0o755)
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "config.toml").write_text("")
    return cli, profile


@pytest.mark.parametrize("role,condition,capture_execution", [
    ("research", "baseline", False), ("research", "skills", False),
    ("research", "discover-general", False), ("research", "discover-science", False),
    ("research", "stamped-explicit", True),
    ("research", "baseline", True), ("judge", "baseline", False),
])
def test_fixture_launch_retains_evidence_and_judges_without_worker_assessor(
        tmp_path, fake_cli, source_repositories, role, condition, capture_execution):
    cli, profile = fake_cli
    worker, _ = make_worker(tmp_path, source_repositories, condition)
    prompt = tmp_path / "research-prompt.md"
    prompt.write_bytes(seed.research_prompt(worker, capture_execution))
    output = tmp_path / "evidence"
    assessor = source_repositories[-1]
    pin = tmp_path / "pin.json"
    pin.write_text(json.dumps({"source_commit": git(assessor, "rev-parse", "HEAD")}))
    environment = dict(os.environ, CODEX_HOME=str(profile), CODEX_THREAD_ID="must-be-removed",
                       PIXI_PROJECT_MANIFEST="/wrong/coordinator/pixi.toml", PIXI_IN_SHELL="1")
    workspace = tmp_path / "judgment"
    target_before = (git(worker, "rev-parse", "HEAD"), git(worker, "status", "--porcelain"))
    if role == "judge":
        judge_workspace.initialize(workspace, worker, source_repositories[3])
    result = subprocess.run([
        sys.executable, str(ROOT / "scripts/launch_native_probe.py"),
        "--checkout", str(worker), "--prompt", str(prompt), "--output", str(output),
        "--cli", str(cli), "--role", role, "--condition", condition,
        "--assessment-source", str(assessor), "--assessment-pin", str(pin),
        "--review-seconds", "0"] + (["--capture-execution"] if capture_execution else []) +
        (["--judge-workspace", str(workspace)] if role == "judge" else []),
        env=environment, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    preflight = json.loads((output / "prompt-preflight.json").read_text())
    assert set(preflight["visible_study_skills"]) == launch.selected_skills(role, condition)
    assert preflight["project_instructions_present"] is False
    record = json.loads((output / "result.json").read_text())
    assert record["timeout_seconds"] == 0
    assert record["timed_out"] is False
    assert record["native_session_ids"] == ["fake-test-session"]
    assert (output / "stderr.txt").read_text() == "fixture stderr\n"
    assert (output / "prompt.txt").read_bytes() == prompt.read_bytes()
    assert not (worker / "assessment").exists()
    assert not (worker / "assessment-version.json").exists()
    assert Path(record["codex_home"]) != profile
    assert not Path(record["codex_home"]).is_relative_to(worker)
    assert not Path(record["codex_home"]).is_relative_to(output)
    assert {"PIXI_PROJECT_MANIFEST", "PIXI_IN_SHELL"}.issubset(record["inherited_pixi_variables_removed"])
    if role == "research":
        assigned = json.loads((output / "condition-assignment.json").read_text())
        assert assigned["condition"] == conditions.canonical_condition(condition)
        assert assigned["prompt_sha256"] == record["prompt_sha256"]
        observed = json.loads((output / "skill-observations.json").read_text())
        assert observed["loaded_instructions"] is None
        assert observed["application_evidence"] is None
        if condition in ("baseline", "discover-general", "discover-science"):
            config_argument = next(arg for arg in record["command"] if arg.startswith("skills.config="))
            assert str(worker / ".agents/skills") not in config_argument
    if role == "judge":
        assert record["condition"] is None
        assert record["assessment_pin"]["source_commit"]
        assert Path(record["cwd"]) == workspace
        assert Path(record["judge_workspace"]) == workspace
        assert record["starting_commit"] == git(workspace, "rev-parse", "HEAD")
        assert record["target"]["target_commit"] == target_before[0]
        assert record["target_unchanged"] is True
        assert (workspace / "assessment.txt").read_text() == "Fixture assessment artifact.\n"
        assert "assessment.txt" in git(workspace, "status", "--porcelain")
        assert (git(worker, "rev-parse", "HEAD"), git(worker, "status", "--porcelain")) == target_before
        assert not (worker / ".codex").exists()
        assert not (worker / ".entire").exists()
        assert all(Path(p).resolve().is_relative_to(assessor) for p in record["study_skill_paths"])
        assert Path(record["codex_home"]).parent == profile.parent
        assert Path(record["codex_home"]) != profile
        assert not Path(record["codex_home"]).is_relative_to(worker)
        assert not Path(record["codex_home"]).is_relative_to(output)


def test_native_judge_retains_failure_when_target_is_modified(tmp_path, fake_cli, source_repositories):
    cli, profile = fake_cli
    target, _ = make_worker(tmp_path, source_repositories)
    workspace = tmp_path / "judgment"
    judge_workspace.initialize(workspace, target, source_repositories[3])
    prompt = tmp_path / "prompt.md"
    prompt.write_text("Synthetic target mutation regression.\n")
    pin = tmp_path / "pin.json"
    assessor = source_repositories[-1]
    pin.write_text(json.dumps({"source_commit": git(assessor, "rev-parse", "HEAD")}))
    output = tmp_path / "native"
    result = subprocess.run([
        sys.executable, str(ROOT / "scripts/launch_native_probe.py"),
        "--checkout", str(target), "--judge-workspace", str(workspace),
        "--prompt", str(prompt), "--output", str(output), "--cli", str(cli),
        "--role", "judge", "--assessment-source", str(assessor), "--assessment-pin", str(pin),
        "--review-seconds", "0"], env=dict(os.environ, CODEX_HOME=str(profile), FAKE_CHANGE_TARGET="1"),
        capture_output=True, text=True)
    assert result.returncode != 0
    assert "Judge changed the assessed target" in result.stderr
    receipt = json.loads((output / "result.json").read_text())
    assert receipt["target_unchanged"] is False
    assert receipt["native_session_ids"] == ["fake-test-session"]
    assert (workspace / "assessment.txt").is_file()


@pytest.mark.parametrize("change", ["command-error", "wrong-key", "partial-result", "exit-code", "invalid-json"])
def test_annex_locations_does_not_hide_query_failures(tmp_path, monkeypatch, change):
    key = "SHA256E-s4--" + "0" * 64
    record = {"command": "whereis", "key": key, "note": "0 copies",
              "success": False, "whereis": [], "error-messages": []}
    if change == "command-error":
        record["error-messages"] = ["annex metadata unavailable"]
    elif change == "wrong-key":
        record["key"] = "different-key"
    elif change == "partial-result":
        record["whereis"] = [{"uuid": "partial-location"}]
    result = subprocess.CompletedProcess(
        ["git", "annex", "whereis"], 2 if change == "exit-code" else 1,
        stdout="invalid" if change == "invalid-json" else json.dumps(record),
        stderr="query failed")
    monkeypatch.setattr(seed.subprocess, "run", lambda *args, **kwargs: result)
    with pytest.raises(subprocess.CalledProcessError):
        seed.annex_locations(tmp_path, key)


@pytest.mark.parametrize("publish_annex_metadata", [False, True])
def test_fresh_selected_study_initializes_only_annex_metadata_for_export(
        tmp_path, source_repositories, publish_annex_metadata):
    coordinator, study, _, resolver, key, *_ = source_repositories
    urls = ["https://example.invalid/primary/observations.bin",
            "https://example.invalid/mirror/observations.bin"]
    for url in urls:
        git(study, "annex", "registerurl", key, url)
    # An experiment gitlink must remain uninitialized throughout study export.
    experiment = init(tmp_path / "historical-experiment")
    (experiment / "result.txt").write_text("Historical output, never worker input")
    experiment_ref = commit(experiment, "test: retain historical experiment fixture")
    (study / ".gitmodules").write_text(
        '[submodule "results/nested"]\n\tpath = results/nested\n\turl = ' + str(experiment) + '\n')
    git(study, "update-index", "--add", "--cacheinfo", f"160000,{experiment_ref},results/nested")
    # Git add would remove an absent gitlink, so keep its empty working directory.
    (study / "results/nested").mkdir()
    commit(study, "test: pin optional historical experiment")
    published = tmp_path / "published-study.git"
    git(tmp_path, "clone", "--bare", "--single-branch", "--branch", "main", study, published)
    if publish_annex_metadata:
        git(published, "fetch", study, "refs/heads/git-annex:refs/heads/git-annex")
    git(coordinator, "config", "-f", ".gitmodules", "submodule.studies/example.url", published)
    base = commit(coordinator, "test: pin study with annex metadata and experiment")

    fresh = tmp_path / "cold-coordinator"
    git(tmp_path, "clone", "--no-local", coordinator, fresh)
    git(fresh, "remote", "set-url", "--push", "origin", "git@github.com:example/coordinator.git")
    git(fresh, "submodule", "update", "--init", "--", "studies/example")
    selected = fresh / "studies/example"
    absent = subprocess.run(["git", "-C", str(selected), "config", "--get", "annex.uuid"],
                            capture_output=True, text=True)
    assert absent.returncode == 1 and not absent.stdout
    before = {"head": git(selected, "rev-parse", "HEAD"),
              "tree": git(selected, "rev-parse", "HEAD:input"),
              "status": git(selected, "status", "--porcelain"),
              "submodules": git(selected, "submodule", "status", "--recursive")}
    assert before["submodules"].startswith("-")
    assert not (selected / "input/data/annexed.bin").exists()

    worker = tmp_path / "cold-worker"
    receipt = seed.make_seed(fresh, base, selected, worker, "codex/cold-fixture", "baseline", resolver)

    assert git(selected, "config", "--get", "annex.uuid")
    item = next(item for item in receipt["inputs"] if item.get("annex_key") == key)
    assert item["urls"] == (sorted(urls) if publish_annex_metadata else [])
    assert receipt["study_commit"] == before["head"]
    assert receipt["study_input_tree"] == before["tree"]
    assert git(selected, "rev-parse", "HEAD") == before["head"]
    assert git(selected, "status", "--porcelain") == before["status"]
    assert git(selected, "submodule", "status", "--recursive") == before["submodules"]
    assert not (selected / "input/data/annexed.bin").exists()
    assert not (worker / "input/data/annexed.bin").exists()
    assert not (selected / "results/nested/.git").exists()
    assert not (fresh / "skills/.git").exists()
    assert not git(fresh, "config", "--get", "--default", "", "annex.uuid")
    assert not git(worker, "config", "--get", "--default", "", "annex.uuid")


def test_public_annex_urls_survive_export_and_retrieve_without_source_history(tmp_path, source_repositories):
    study = source_repositories[1]
    key = source_repositories[4]
    handler = partial(SimpleHTTPRequestHandler, directory=str(study / "input/data"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    serving = threading.Thread(target=server.serve_forever, daemon=True)
    serving.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/annexed.bin"
        git(study, "annex", "registerurl", key, url)
        worker, receipt = make_worker(tmp_path, source_repositories)
        item = next(row for row in receipt["inputs"] if row.get("annex_key") == key)
        assert url in item["urls"]
        git(worker, "config", "remote.origin.annex-ignore", "true")
        git(worker, "annex", "init", "public-url-fixture")
        git(worker, "config", "annex.security.allowed-ip-addresses", "127.0.0.1")
        for public_url in item["urls"]:
            git(worker, "annex", "registerurl", key, public_url)
        git(worker, "annex", "get", "--", "input")
        assert (worker / "input/data/annexed.bin").read_bytes() == (study / "input/data/annexed.bin").read_bytes()
        for oid in source_repositories[5]:
            assert subprocess.run(["git", "-C", str(worker), "cat-file", "-e", oid],
                                  capture_output=True).returncode != 0
    finally:
        server.shutdown()
        server.server_close()
        serving.join()


@pytest.mark.parametrize("change", ["tracked-input", "extra-reference"])
def test_boundary_rejects_changes_after_seed(tmp_path, source_repositories, change):
    worker, _ = make_worker(tmp_path, source_repositories)
    if change == "tracked-input":
        (worker / "input/study-task.md").write_text("Answer supplied by a later edit.")
        message = "changed after the committed seed"
    else:
        (worker / "input/reference.txt").write_text("Uncommitted reference answer.")
        message = "extra untracked files"
    with pytest.raises(SystemExit, match=message):
        seed.audit_seed(worker)


def test_input_helper_retrieves_annex_key_without_importing_location_history(tmp_path, source_repositories):
    worker, receipt = make_worker(tmp_path, source_repositories)
    study = source_repositories[1]
    key = source_repositories[4]
    git(worker, "config", "remote.origin.annex-ignore", "true")
    git(worker, "annex", "init", "no-location-history-fixture")
    git(worker, "remote", "add", "payload-store", study)
    location_check = subprocess.run([
        "git", "-C", str(worker), "annex", "whereis", "--json", "--key", key,
    ], capture_output=True, text=True)
    locations = json.loads(location_check.stdout)
    assert locations["whereis"] == []
    assert not (worker / "input/data/annexed.bin").exists()
    assert not any(item.get("urls") for item in receipt["inputs"])
    assert git(worker, "for-each-ref", "refs/remotes") == ""

    prepare.retrieve_inputs(["git", "-C", str(worker)], worker,
                            receipt["inputs"], "payload-store")

    assert (worker / "input/data/annexed.bin").is_file()
    assert (worker / "input/data/annexed.bin").read_bytes() == (study / "input/data/annexed.bin").read_bytes()
    assert git(worker, "annex", "lookupkey", "input/data/annexed.bin") == key
    assert git(worker, "for-each-ref", "refs/remotes") == ""
    for oid in source_repositories[5]:
        assert subprocess.run(["git", "-C", str(worker), "cat-file", "-e", oid],
                              capture_output=True).returncode != 0
    assert not git(worker, "status", "--porcelain")
    # The ordinary annex get used by a later judge/replay must also work;
    # transferkey alone records only the local copy, not the supplying remote.
    recipient = tmp_path / "recipient"
    git(tmp_path, "clone", "--no-local", worker, recipient)
    git(recipient, "annex", "init", "recipient-fixture")
    git(recipient, "remote", "add", "payload-store", study)
    git(recipient, "annex", "get", "--from", "payload-store", "--", "input/data/annexed.bin")
    assert (recipient / "input/data/annexed.bin").read_bytes() == (study / "input/data/annexed.bin").read_bytes()


def test_judge_catalog_preserves_existing_trust_and_links_host_auth_outside_target(tmp_path, source_repositories):
    profile = tmp_path / "prepared-profile"
    profile.mkdir()
    config = '[hooks.state."/exact/target/.codex/hooks.json:stop:0:0"]\ntrusted_hash = "sha256:fixture"\n'
    (profile / "config.toml").write_text(config)
    (profile / "auth.json").write_text('{"synthetic": "fixture, not a credential"}\n')
    assessor = source_repositories[-1]
    isolated = launch.judge_profile(profile, assessor)
    assert (isolated / "config.toml").read_bytes() == (profile / "config.toml").read_bytes()
    assert not (isolated / "config.toml").is_symlink()
    assert (isolated / "auth.json").is_symlink()
    assert (isolated / "auth.json").resolve() == (profile / "auth.json").resolve()
    assert isolated.stat().st_mode & 0o777 == 0o700
    assert (isolated / "config.toml").stat().st_mode & 0o777 == 0o600
    assert {p.name for p in (isolated / "skills").iterdir()} == launch.JUDGE_SKILLS
    assert all((isolated / "skills" / name).resolve() == assessor / "skills" / name
               for name in launch.JUDGE_SKILLS)
    assert not (profile / "skills").exists()


def test_research_profiles_do_not_share_installs_history_or_model_cache(tmp_path):
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    config = '[hooks.state."/exact/.codex/hooks.json:stop:0:0"]\ntrusted_hash = "sha256:fixture"\n'
    (prepared / "config.toml").write_text(config)
    (prepared / "auth.json").write_text('{"synthetic": "not a credential"}')
    (prepared / "models_cache.json").write_text('{"models": []}')
    (prepared / "sessions").mkdir()
    (prepared / "sessions/old.jsonl").write_text("Prior research")
    (prepared / "skills").mkdir()
    (prepared / "skills/leaked.md").write_text("Prior install")
    first = launch.launch_profile(prepared)
    (first / "skills/new-skill").mkdir()
    (first / "skills/new-skill/SKILL.md").write_text("A discovered skill")
    (first / "models_cache.json").write_text("Changed locally")
    second = launch.launch_profile(prepared)
    for profile in (first, second):
        assert (profile / "config.toml").read_text() == config
        assert (profile / "auth.json").resolve() == prepared / "auth.json"
        assert not (profile / "sessions").exists()
        assert not (profile / "skills/leaked.md").exists()
    assert not (second / "skills/new-skill").exists()
    assert not (prepared / "skills/new-skill").exists()
    assert (second / "models_cache.json").read_bytes() == (prepared / "models_cache.json").read_bytes()


def test_catalog_preserves_non_stamped_skill_identity():
    preview = b"- unrelated-skill: Useful guidance (file: /host/SKILL.md)\n"
    assert launch.skill_catalog(preview) == [{"name": "unrelated-skill", "path": "/host/SKILL.md"}]


def test_preflight_rejects_unexpected_host_skill_before_execution(tmp_path, fake_cli, source_repositories):
    cli, profile = fake_cli
    worker, _ = make_worker(tmp_path, source_repositories)
    prompt = tmp_path / "prompt.md"
    prompt.write_bytes(seed.research_prompt(worker))
    output = tmp_path / "unexpected-catalog"
    completed = subprocess.run([
        sys.executable, str(ROOT / "scripts/launch_native_probe.py"),
        "--checkout", str(worker), "--prompt", str(prompt), "--output", str(output),
        "--cli", str(cli), "--preflight-only",
    ], env=dict(os.environ, CODEX_HOME=str(profile), FAKE_UNEXPECTED_SKILL="1"),
        capture_output=True, text=True)
    assert completed.returncode != 0
    assert "skill visibility preflight" in completed.stderr
    receipt = json.loads((output / "prompt-preflight.json").read_text())
    assert receipt["unexpected_skill_catalog"] == [
        {"name": "unrelated-skill", "path": "/unexpected/SKILL.md"}]
    assert not (output / "launch.json").exists()


def test_native_json_catalog_expands_aliases_and_ignores_user_quoted_skills(tmp_path):
    root = tmp_path / "system"
    (root / "fixture").mkdir(parents=True)
    (root / "fixture/SKILL.md").write_text("Installed instruction bytes")
    block = ("<skills_instructions>\n### Skill roots\n- `r0` = `" + str(root) + "`\n"
             "### Available skills\n- fixture: Description. (file: r0/fixture/SKILL.md)\n"
             "</skills_instructions>")
    preview = json.dumps([
        {"role": "developer", "content": [{"type": "input_text", "text": block}]},
        {"role": "user", "content": [{"type": "input_text", "text": block.replace("fixture:", "quoted:")}]},
    ]).encode()
    assert launch.skill_catalog(preview) == [{
        "name": "fixture", "path": str(root / "fixture/SKILL.md"),
        "sha256": seed.hashlib.sha256(b"Installed instruction bytes").hexdigest(),
    }]
    with pytest.raises(SystemExit, match="Unresolved advertised"):
        launch.skill_catalog(b"- fixture: Description. (file: missing/fixture/SKILL.md)\n")
    with pytest.raises(SystemExit, match="Unparsed advertised"):
        launch.skill_catalog(b"### Available skills\n- fixture: Missing the source path\n")


def test_pinned_unready_study_stops_before_worker_creation(tmp_path, source_repositories):
    coordinator, study, _, resolver, *_ = source_repositories
    readiness = study / "coordinator-guidance/readiness.json"
    readiness.write_text(json.dumps({"ready": False, "reason": "Participant inputs are missing"}))
    commit(study, "test: record missing scientific inputs")
    base = commit(coordinator, "test: pin blocked study")
    # An uncommitted status change cannot override the selected study revision.
    readiness.write_text(json.dumps({"ready": True}))
    checkout = tmp_path / "blocked-worker"
    with pytest.raises(SystemExit, match="Participant inputs are missing"):
        seed.make_seed(coordinator, base, study, checkout, "codex/blocked", "baseline", resolver)
    assert not checkout.exists()


def test_worker_snapshot_retains_large_ignored_lock_as_regular_git(tmp_path, source_repositories):
    worker, _ = make_worker(tmp_path, source_repositories)
    git(worker, "config", "remote.origin.annex-ignore", "true")
    git(worker, "annex", "init", "snapshot-fixture")
    task_commit = git(worker, "rev-parse", "HEAD")
    lock = b"# Exact synthetic environment snapshot\n" * 6000
    (worker / "pixi.lock").write_bytes(lock)
    assert git(worker, "check-ignore", "pixi.lock") == "pixi.lock"
    git(worker, "add", "--all")
    assert not git(worker, "diff", "--cached", "--name-only")
    git(worker, "switch", "-c", "codex/env-fixture")
    git(worker, "add", "-f", "pixi.lock")
    git(worker, "commit", "-m", "test: retain exact environment snapshot")
    snapshot = git(worker, "rev-parse", "HEAD")
    assert git(worker, "rev-parse", snapshot + "^") == task_commit
    assert subprocess.check_output(["git", "-C", str(worker), "show", snapshot + ":pixi.lock"]) == lock
    assert git(worker, "ls-tree", snapshot, "pixi.lock").startswith("100644 blob ")
    assert not git(worker, "ls-tree", task_commit, "pixi.lock")
    assert subprocess.run(["git", "-C", str(worker), "annex", "lookupkey", "pixi.lock"],
                          capture_output=True).returncode != 0
