"""Exercise real disposable commands without contacting hosted resources."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import readiness


def requirement(identifier):
    return {"id": identifier, "description": f"Demonstrate {identifier}",
            "source": "Synthetic user instruction"}


def command(tmp_path, code, **settings):
    return {"argv": [sys.executable, "-c", code], "cwd": str(tmp_path), **settings}


def files(tmp_path, identifiers, checks):
    requirements = tmp_path / "requirements.json"
    requirements.write_text(json.dumps({"schema_version": 1,
                                       "requirements": [requirement(name) for name in identifiers]}))
    host = tmp_path / "host.json"
    host.write_text(json.dumps({"schema_version": 1, "checks": checks}))
    return requirements, host, tmp_path / "evidence"


def test_retains_command_timing_outputs_artifacts_and_exact_requirements(tmp_path):
    code = ("import os, pathlib, sys; "
            "pathlib.Path(os.environ['READINESS_ARTIFACT_DIR'], 'probe.json').write_text('{}'); "
            "print('verified fixture'); print('diagnostic', file=sys.stderr)")
    check = command(tmp_path, code, artifacts=["probe.json"])
    paths = files(tmp_path, ["fixture"], {"fixture": check})
    report = readiness.run(*paths)
    evidence = paths[-1]
    row = report["checks"][0]
    assert report["ready"] is True and report["complete"] is True
    assert report["unmet_requirements"] == []
    assert row["argv"] == check["argv"] and row["cwd"] == str(tmp_path)
    assert row["returncode"] == 0 and row["status"] == "passed"
    assert row["started_at"] <= row["finished_at"] and row["elapsed_seconds"] >= 0
    assert (evidence / row["stdout"]["path"]).read_text() == "verified fixture\n"
    assert (evidence / row["stderr"]["path"]).read_text() == "diagnostic\n"
    artifact = row["artifacts"][0]
    assert artifact["status"] == "retained" and artifact["bytes"] == 2
    assert artifact["sha256"] == hashlib.sha256(b"{}").hexdigest()
    assert (evidence / "requirements.json").read_bytes() == paths[0].read_bytes()
    assert report["requirements_sha256"] == hashlib.sha256(paths[0].read_bytes()).hexdigest()
    assert json.loads((evidence / "fixture/receipt.json").read_text()) == row
    assert json.loads((evidence / "result.json").read_text()) == report
    assert evidence.stat().st_mode & 0o777 == 0o700
    assert not (evidence / "host.json").exists()


def test_all_requested_outcomes_reported_and_unrequested_checks_never_run(tmp_path):
    unwanted = tmp_path / "unwanted"
    checks = {
        "failure": command(tmp_path, "raise SystemExit(7)"),
        "success": command(tmp_path, "print('done')"),
        "absent-executable": {"argv": [str(tmp_path / "missing-command")], "cwd": str(tmp_path)},
        "unrequested": command(tmp_path, f"open({str(unwanted)!r}, 'w').close()"),
    }
    paths = files(tmp_path, ["missing", "failure", "absent-executable", "success"], checks)
    report = readiness.run(*paths)
    assert report["ready"] is False and report["complete"] is True
    assert report["unmet_requirements"] == ["missing", "failure", "absent-executable"]
    assert [row["status"] for row in report["checks"]] == ["missing", "failed", "error", "passed"]
    assert report["checks"][1]["returncode"] == 7
    assert not unwanted.exists()


def test_missing_host_file_reports_missing_requirements(tmp_path):
    paths = files(tmp_path, ["needed"], {})
    paths[1].unlink()
    assert readiness.run(*paths)["checks"][0]["status"] == "missing"


@pytest.mark.parametrize("artifact_code", ["pass", "out.symlink_to(source)"])
def test_missing_or_external_artifacts_fail_even_when_command_succeeds(tmp_path, artifact_code):
    source = tmp_path / "outside"
    source.write_text("Must not be copied or hashed")
    code = ("import os, pathlib; "
            "out=pathlib.Path(os.environ['READINESS_ARTIFACT_DIR'], 'receipt.txt'); "
            f"source=pathlib.Path({str(source)!r}); {artifact_code}")
    paths = files(tmp_path, ["probe"], {"probe": command(tmp_path, code, artifacts=["receipt.txt"])})
    row = readiness.run(*paths)["checks"][0]
    assert row["status"] == "failed" and row["returncode"] == 0
    assert row["artifacts"][0]["status"] == "missing"
    assert "sha256" not in row["artifacts"][0]


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group cleanup")
def test_timeout_stops_child_processes_and_retains_output(tmp_path):
    sentinel = tmp_path / "child-survived"
    child = f"import time, pathlib; time.sleep(.5); pathlib.Path({str(sentinel)!r}).touch()"
    code = (f"import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', {child!r}]); "
            "print('started', flush=True); time.sleep(5)")
    paths = files(tmp_path, ["slow"], {"slow": command(tmp_path, code, timeout_seconds=.15)})
    row = readiness.run(*paths)["checks"][0]
    assert row["status"] == "timeout" and row["returncode"] != 0
    assert (paths[-1] / row["stdout"]["path"]).read_text() == "started\n"
    time.sleep(.6)
    assert not sentinel.exists()


def test_arguments_are_literal_and_relative_cwd_uses_host_config_directory(tmp_path):
    working = tmp_path / "work"
    working.mkdir()
    literal = "$(touch unexpected); *"
    check = {"cwd": "work", "argv": [sys.executable, "-c", "import sys; print(sys.argv[1])", literal]}
    paths = files(tmp_path, ["literal"], {"literal": check})
    row = readiness.run(*paths)["checks"][0]
    assert row["cwd"] == str(working)
    assert (paths[-1] / row["stdout"]["path"]).read_text() == literal + "\n"
    assert not (working / "unexpected").exists()


def test_existing_evidence_is_never_overwritten(tmp_path):
    paths = files(tmp_path, ["probe"], {})
    readiness.run(*paths)
    retained = (paths[-1] / "result.json").read_bytes()
    with pytest.raises(FileExistsError):
        readiness.run(*paths)
    assert (paths[-1] / "result.json").read_bytes() == retained


@pytest.mark.parametrize("mutation", [
    lambda plan, host: plan.update(requirements=[]),
    lambda plan, host: plan["requirements"].append(plan["requirements"][0]),
    lambda plan, host: plan["requirements"][0].update(id="../escape"),
    lambda plan, host: plan["requirements"][0].update(source=""),
    lambda plan, host: host["checks"]["probe"].update(argv="echo misleading"),
    lambda plan, host: host["checks"]["probe"].update(timeout_seconds=0),
    lambda plan, host: host["checks"]["probe"].update(timeout_seconds=float("inf")),
    lambda plan, host: host["checks"]["probe"].update(artifacts=["../outside"]),
    lambda plan, host: host["checks"]["probe"].update(artifact=["misspelled"]),
])
def test_invalid_plan_fails_before_execution(tmp_path, mutation):
    paths = files(tmp_path, ["probe"], {"probe": command(tmp_path, "raise Exception('must not execute')")})
    plan, host = (json.loads(path.read_text()) for path in paths[:2])
    mutation(plan, host)
    paths[0].write_text(json.dumps(plan))
    paths[1].write_text(json.dumps(host))
    with pytest.raises(ValueError):
        readiness.run(*paths)
    assert not paths[-1].exists()


@pytest.mark.parametrize("configured,exit_code", [(True, 0), (False, 1)])
def test_cli_exit_status_and_receipt_location(tmp_path, configured, exit_code):
    checks = {"probe": command(tmp_path, "print('ready')")} if configured else {}
    requirements, host, evidence = files(tmp_path, ["probe"], checks)
    result = subprocess.run([sys.executable, str(ROOT / "scripts/readiness.py"),
                             "--requirements", str(requirements), "--host-config", str(host),
                             "--evidence", str(evidence)], text=True, capture_output=True)
    assert result.returncode == exit_code, result.stderr
    assert json.loads(result.stdout)["receipt"] == str(evidence / "result.json")
