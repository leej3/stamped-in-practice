"""Check response dispatch without installing environments or accessing remotes."""
import hashlib
import json
import os
from pathlib import Path
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
