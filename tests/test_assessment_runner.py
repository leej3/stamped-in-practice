"""Check response dispatch without installing environments or accessing remotes."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import assessment


@pytest.fixture
def frozen_runner(tmp_path, monkeypatch):
    source = tmp_path / "frozen source"
    source.mkdir()
    environment = {"pixi.toml": b"[workspace]\nname = 'fixture'\n", "pixi.lock": b"fixture lock\n"}
    pin = {"source_commit": "a" * 40, "environment_commit": "b" * 40,
           "sha256": {name: hashlib.sha256(content).hexdigest()
                      for name, content in environment.items()}}
    pin_path = tmp_path / "pin.json"
    pin_path.write_text(json.dumps(pin))
    monkeypatch.setattr(assessment, "ROOT", tmp_path)
    monkeypatch.setenv("STAMPED_ASSESSMENT_SOURCE", str(source))
    monkeypatch.setenv("STAMPED_ASSESSMENT_PIN", str(pin_path))

    def git(*args, **kwargs):
        if args == ("rev-parse", "HEAD"):
            assert kwargs["cwd"] == source
            return (pin["source_commit"] + "\n").encode()
        if args == ("status", "--porcelain"):
            return b""
        if args == ("submodule", "status", "--recursive"):
            return b" ccccccc evals\n"
        assert args[0] == "show"
        revision, filename = args[1].split(":")
        assert revision == pin["environment_commit"]
        return environment[filename]

    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        assert command[:2] in (["git", "cat-file"], ["pixi", "install"], ["pixi", "run"])
        return subprocess.CompletedProcess(command, 7 if command[:2] == ["pixi", "run"] else 0)

    monkeypatch.setattr(assessment, "git", git)
    monkeypatch.setattr(assessment.subprocess, "run", run)
    return calls, source, tmp_path / ".pixi/assessment-runtime" / pin["environment_commit"]


@pytest.mark.parametrize("arguments", [
    ["items", "--json"],
    ["template", "-o", "output with spaces.json"],
    ["set", "response.json", "--item", "must/001", "--status", "met",
     "--reason", "A reason with spaces; $(not-a-shell-command)", "--evidence", "file=description"],
    ["stamp", "response.json", "--harness", "native session"],
    ["table", "response.json", "-o", "table.md"],
    ["encode", "response.json", "--base-url", "https://example.invalid/?x=1&y=2"],
    ["decode", "https://example.invalid/?responses=abc+def==", "-o", "decoded.json"],
    ["validate", "response.json"],
    ["--help"],
])
def test_response_forwards_every_argument_through_frozen_runtime(frozen_runner, monkeypatch, arguments):
    calls, source, runtime = frozen_runner
    monkeypatch.setattr(sys, "argv", ["assessment.py", "response", *arguments])
    with pytest.raises(SystemExit) as exit_status:
        assessment.main()
    assert exit_status.value.code == 7
    assert calls[-1] == ([
        "pixi", "run", "--locked", "--manifest-path", runtime / "pixi.toml", "python",
        source / "skills/stamped-conventions/scripts/encode_response.py", *arguments,
    ], {"cwd": assessment.ROOT})
    assert calls[-2][0] == ["pixi", "install", "--locked", "--manifest-path", runtime / "pixi.toml"]


def test_validate_shortcut_remains_compatible(frozen_runner, monkeypatch):
    calls, source, runtime = frozen_runner
    monkeypatch.setattr(sys, "argv", ["assessment.py", "validate", "response with spaces.json"])
    with pytest.raises(SystemExit) as exit_status:
        assessment.main()
    assert exit_status.value.code == 7
    assert calls[-1][0] == [
        "pixi", "run", "--locked", "--manifest-path", runtime / "pixi.toml", "python",
        source / "skills/stamped-conventions/scripts/encode_response.py",
        "validate", "response with spaces.json",
    ]


@pytest.mark.parametrize("repository", [None, "git@github.com:example/recorded-runtime.git"])
def test_missing_runtime_is_fetched_from_declared_repository_or_legacy_origin(
        frozen_runner, monkeypatch, repository):
    calls, source, runtime = frozen_runner
    pin_path = Path(os.environ["STAMPED_ASSESSMENT_PIN"])
    pin = json.loads(pin_path.read_text())
    if repository is not None:
        pin["environment_repository"] = repository
        pin_path.write_text(json.dumps(pin))
    original_run = assessment.subprocess.run

    def missing_runtime(command, **kwargs):
        if command[:2] == ["git", "cat-file"]:
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 1)
        if command[:2] == ["git", "fetch"]:
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 0)
        return original_run(command, **kwargs)

    monkeypatch.setattr(assessment.subprocess, "run", missing_runtime)
    monkeypatch.setattr(sys, "argv", ["assessment.py", "check"])
    assessment.main()
    assert calls[1] == (["git", "fetch", "--no-tags", "--depth", "1",
                         repository or "origin", pin["environment_commit"]],
                        {"cwd": assessment.ROOT, "check": True})
    assert (runtime / "pixi.lock").read_text() == "fixture lock\n"


def test_available_runtime_does_not_contact_declared_repository(frozen_runner, monkeypatch):
    calls, source, runtime = frozen_runner
    pin_path = Path(os.environ["STAMPED_ASSESSMENT_PIN"])
    pin = json.loads(pin_path.read_text())
    pin["environment_repository"] = "git@github.com:example/recorded-runtime.git"
    pin_path.write_text(json.dumps(pin))
    monkeypatch.setattr(sys, "argv", ["assessment.py", "check"])
    assessment.main()
    assert not any(command[:2] == ["git", "fetch"] for command, kwargs in calls)


def formal_runner(monkeypatch, version):
    pin = json.loads(Path(os.environ["STAMPED_ASSESSMENT_PIN"]).read_text())
    frozen = {"version": version, "assessment": pin,
              "replay": assessment.procedure.NEUTRAL_REPLAY,
              "fixed_files": {"scripts/assessment.py":
                  assessment.procedure.sha256(Path(assessment.__file__).read_bytes())}}
    monkeypatch.setenv("STAMPED_PROCEDURE", "synthetic-procedure.json")
    monkeypatch.setenv("STAMPED_PROCEDURE_SHA256", "synthetic-seal")
    monkeypatch.setattr(assessment.procedure, "load_procedure", lambda *args: frozen)
    return frozen


@pytest.mark.parametrize("version", [1, 2, 3])
def test_legacy_formal_helper_dispatch_keeps_coordinator_cwd(frozen_runner, monkeypatch, tmp_path, version):
    calls, _, _ = frozen_runner
    formal_runner(monkeypatch, version)
    caller = tmp_path / "caller"
    caller.mkdir()
    monkeypatch.chdir(caller)
    monkeypatch.delenv("STAMPED_JUDGE_OUTPUT", raising=False)
    monkeypatch.setattr(sys, "argv", ["assessment.py", "response", "template", "-o", "response.json"])
    with pytest.raises(SystemExit) as result:
        assessment.main()
    assert result.value.code == 7
    assert calls[-1][1] == {"cwd": assessment.ROOT}
    assert Path.cwd() == caller


@pytest.mark.parametrize("invalid", ["missing-env", "relative", "missing-directory", "file", "coordinator", "target"])
def test_v4_requires_existing_separate_output_before_writing_runtime(
        frozen_runner, monkeypatch, tmp_path, invalid):
    calls, _, runtime = frozen_runner
    formal_runner(monkeypatch, 4)
    target = tmp_path / "target"
    target.mkdir()
    file = tmp_path / "file"
    file.write_text("fixture")
    monkeypatch.setenv("STAMPED_JUDGE_TARGET", str(target))
    selected = {"relative": "judgment", "missing-directory": str(tmp_path / "missing"),
                "file": str(file), "coordinator": str(tmp_path), "target": str(target)}
    if invalid == "missing-env":
        monkeypatch.delenv("STAMPED_JUDGE_OUTPUT", raising=False)
    else:
        monkeypatch.setenv("STAMPED_JUDGE_OUTPUT", selected[invalid])
    monkeypatch.setattr(sys, "argv", ["assessment.py", "response", "template", "-o", "response.json"])
    with pytest.raises(SystemExit, match="Version 4"):
        assessment.main()
    assert calls == []
    assert not runtime.exists()
    assert not (tmp_path / "missing").exists()


def test_v4_concurrent_relative_responses_are_generated_and_read_in_each_judgment(
        frozen_runner, monkeypatch, tmp_path):
    calls, source, _ = frozen_runner
    formal_runner(monkeypatch, 4)
    actual_skill = Path(__file__).resolve().parents[1] / "assessment/skills/stamped-conventions"
    assert (actual_skill / "scripts/encode_response.py").is_file(), "Initialize the pinned assessment helper"
    shutil.copytree(actual_skill, source / "skills/stamped-conventions")
    target = tmp_path / "operational-target"
    target.mkdir()
    monkeypatch.setenv("STAMPED_JUDGE_TARGET", str(target))
    monkeypatch.chdir(target)
    workspaces = [tmp_path / name for name in ("judge-a", "judge-b")]
    for workspace in workspaces:
        workspace.mkdir()

    def dispatch(workspace, arguments):
        monkeypatch.setenv("STAMPED_JUDGE_OUTPUT", str(workspace))
        monkeypatch.setattr(sys, "argv", ["assessment.py", *arguments])
        with pytest.raises(SystemExit) as result:
            assessment.main()
        assert result.value.code == 7
        command, kwargs = calls[-1]
        assert Path(command[4]).is_absolute() and Path(command[6]).is_absolute()
        # Source/runtime verification is stubbed; execute the frozen response
        # helper in a real process using the dispatcher's exact argv and cwd.
        return subprocess.Popen([sys.executable, *map(str, command[6:])],
                                **kwargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for action in ("template", "stamp", "validate"):
        processes = []
        for workspace in workspaces:
            arguments = ({"template": ["response", "template", "-o", "response.json"],
                          "stamp": ["response", "stamp", "response.json", "--harness", workspace.name],
                          "validate": ["validate", "response.json"]})[action]
            processes.append(dispatch(workspace, arguments))
        for process in processes:
            stdout, stderr = process.communicate(timeout=30)
            assert process.returncode == 0, (stdout, stderr)
        if action == "template":
            for workspace in workspaces:
                path = workspace / "response.json"
                response = json.loads(path.read_text())
                response["scope"] = "Synthetic path-isolation validation"
                response["object"].update(commit="a" * 40,
                    captured_at="2026-01-01T00:00:00Z", kind="study")
                response["assessor"].update(skill="synthetic", version="fixture",
                    model="no-model-run", date="2026-01-01", dependencies=["frozen-helper"])
                path.write_text(json.dumps(response))
    for workspace in workspaces:
        response = json.loads((workspace / "response.json").read_text())
        assert response["assessor"]["harness"] == workspace.name
    assert not (assessment.ROOT / "response.json").exists()
    assert not (target / "response.json").exists()
    assert Path.cwd() == target


def test_v4_relative_replay_validation_and_dispatch_use_judgment_directory(
        frozen_runner, monkeypatch, tmp_path):
    import delivery_snapshot
    calls, source, runtime = frozen_runner
    formal_runner(monkeypatch, 4)
    worker = tmp_path / "worker"
    worker.mkdir()
    (worker / "result.csv").write_text("x\n1\n")
    receipt = delivery_snapshot.save_delivery(worker, tmp_path / "capture", {})
    canonical = Path(receipt["capture"]["uri"])
    target, output = tmp_path / "operational", tmp_path / "judgment"
    target.mkdir()
    output.mkdir()
    helper = source / "skills/assess-alignment-with-stamped-principles/scripts/fresh_rerun.py"
    helper.parent.mkdir(parents=True)
    helper.write_text("# Synthetic dispatch-only helper\n")
    monkeypatch.setenv("STAMPED_DELIVERY_MANIFEST", str(canonical))
    monkeypatch.setenv("STAMPED_JUDGE_TARGET", str(target))
    monkeypatch.setenv("STAMPED_JUDGE_OUTPUT", str(output))
    monkeypatch.chdir(target)
    arguments = ["--path", str(target), "--entry", "documented-entry", "--outputs", "result.csv",
                 "--workdir", "replay", "--output", "replay.json"]
    monkeypatch.setattr(sys, "argv", ["assessment.py", "fresh-rerun", *arguments])
    with pytest.raises(SystemExit) as result:
        assessment.main()
    assert result.value.code == 7
    command, kwargs = calls[-1]
    assert kwargs == {"cwd": output}
    assert command[4] == runtime / "pixi.toml"
    assert command[6] == Path(assessment.__file__).resolve()
    assert command[8] == str(helper)
    assert command[-len(arguments):] == arguments
    assert (output / "formal-replay-attempt.json").is_file()
    assert not (target / "formal-replay-attempt.json").exists()
    assert Path.cwd() == target
