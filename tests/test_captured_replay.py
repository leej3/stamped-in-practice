"""Conditional replay must use stopped bytes, preserve originals, and scope limits."""
import json
import os
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import assessment
import delivery_snapshot as delivery

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "assessment/skills/assess-alignment-with-stamped-principles/scripts/fresh_rerun.py"


@pytest.fixture
def captured(tmp_path, monkeypatch):
    root = tmp_path / "worker"
    root.mkdir()
    (root / "input").mkdir()
    (root / "input/value.txt").write_text("1")
    (root / "result.csv").write_text("label,value\nx,1.0\n")
    (root / "analysis.py").write_text("from pathlib import Path\nPath('result.csv').write_text('label,value\\nx,1.0\\n')\n")
    pointer = delivery.save_delivery(root, tmp_path / "evidence", {},
        seed_receipt={"supplied_files": [{"path": "input/value.txt"}]})
    manifest = Path(pointer["capture"]["uri"])
    monkeypatch.setenv("STAMPED_DELIVERY_MANIFEST", str(manifest))
    monkeypatch.setenv("STAMPED_WORKER_STOP_RECEIPT", str(tmp_path / "evidence/worker-end-state.json"))
    args = ["--path", str(manifest.parent / "content/workspace"),
            "--entry", f"{sys.executable} analysis.py", "--outputs", "result.csv",
            "--workdir", str(tmp_path / "replay"), "--output", str(tmp_path / "report.json")]
    return root, manifest, args, tmp_path / "report.json"


def test_no_git_replay_uses_ignored_untracked_original_bytes(captured):
    _, manifest, args, output = captured
    assert HELPER.is_file(), "Initialize the pinned assessment submodule for launcher tests"
    before = manifest.read_bytes()
    assert assessment.captured_replay(args, HELPER) == 0
    report = json.loads(output.read_text())
    assert report["status"] == "met"
    assert report["commit"] is None
    assert report["comparison"]["identical"] == ["result.csv"]
    assert report["replay_git_overlay"]["core.hooksPath"] == os.devnull
    assert "retrieval_scope" not in report
    assert manifest.read_bytes() == before
    delivery.validate_capture(manifest)
    assert not (Path(report["workdir"]) / ".git").exists()


def test_v4_replay_report_describes_unmetered_entrypoint_downloads(captured, monkeypatch):
    _, manifest, args, output = captured
    monkeypatch.setenv("STAMPED_JUDGE_TARGET", str(manifest.parent / "content/workspace"))
    assert assessment.captured_replay(args, HELPER, operational=True) == 0
    report = json.loads(output.read_text())
    assert report["status"] == "met"
    assert report["retrieval_scope"] == {
        "adapter_input_retrieval": "none; uses captured inputs",
        "entrypoint_network_byte_limit": None,
        "entrypoint_downloads": "Documented dependency installs/downloads are not byte-metered",
        "max_get_gb": 5.0,
        "max_get_gb_scope": "Frozen helper-prefetch compatibility parameter; this adapter performs no prefetch",
    }


@pytest.mark.parametrize("selection", ["input/*", "analysis.py"])
def test_replay_protects_inputs_and_code(captured, selection):
    _, manifest, args, output = captured
    args[args.index("--outputs") + 1] = selection
    assessment.captured_replay(args, HELPER)
    assert json.loads(output.read_text())["status"] == "not-checked"
    assert (manifest.parent / "content/workspace/input/value.txt").read_text() == "1"
    delivery.validate_capture(manifest)


def test_replay_timeout_is_a_measurement_limit(captured):
    _, _, args, output = captured
    args[args.index("--entry") + 1] = f"{sys.executable} -c 'import time; time.sleep(5)'"
    assessment.captured_replay([*args, "--timeout", "1"], HELPER)
    report = json.loads(output.read_text())
    assert report["status"] == "not-checked"
    assert report["timed_out"] is True
    assert Path(report["stdout"]).exists()


def test_unsafe_original_absolute_link_is_not_executed(tmp_path, monkeypatch):
    root = tmp_path / "worker"
    root.mkdir()
    (root / "result.csv").write_text("x\n1\n")
    (root / "link").symlink_to(root / "result.csv")
    pointer = delivery.save_delivery(root, tmp_path / "evidence", {})
    manifest = Path(pointer["capture"]["uri"])
    monkeypatch.setenv("STAMPED_DELIVERY_MANIFEST", str(manifest))
    monkeypatch.setenv("STAMPED_WORKER_STOP_RECEIPT", str(tmp_path / "evidence/worker-end-state.json"))
    output = tmp_path / "report.json"
    assessment.captured_replay(["--path", str(manifest.parent / "content/workspace"),
        "--entry", "exit 99", "--outputs", "result.csv", "--workdir", str(tmp_path / "replay"),
        "--output", str(output)], HELPER)
    assert json.loads(output.read_text())["status"] == "not-checked"
    assert not (tmp_path / "replay").exists()


def test_external_skill_observations_do_not_disable_scientific_replay(tmp_path, monkeypatch):
    root = tmp_path / "worker"
    root.mkdir()
    (root / "result.csv").write_text("x\n1\n")
    skills = tmp_path / "profile-skills"
    skills.mkdir()
    supplied = tmp_path / "supplied-skill"
    supplied.mkdir()
    (supplied / "SKILL.md").write_text("Supplied guidance")
    (skills / "supplied").symlink_to(supplied)
    pointer = delivery.save_delivery(root, tmp_path / "evidence", {}, declared_artifacts=[{
        "path": str(skills), "declaration": {"kind": "native-session-skill-directory"}}])
    manifest = Path(pointer["capture"]["uri"])
    monkeypatch.setenv("STAMPED_DELIVERY_MANIFEST", str(manifest))
    monkeypatch.setenv("STAMPED_WORKER_STOP_RECEIPT", str(tmp_path / "evidence/worker-end-state.json"))
    output = tmp_path / "report.json"
    assessment.captured_replay(["--path", str(manifest.parent / "content/workspace"),
        "--entry", "printf 'x\\n1\\n' > result.csv", "--outputs", "result.csv",
        "--workdir", str(tmp_path / "replay"), "--output", str(output)], HELPER)
    assert json.loads(output.read_text())["status"] == "met"
    delivery.validate_capture(manifest)


def test_one_attempt_guard_accepts_no_git_capture_identity(captured, monkeypatch):
    _, _, args, output = captured
    manifest = {"version": 3, "replay": assessment.procedure.NEUTRAL_REPLAY}
    target = Path(args[args.index("--path") + 1])
    assessment.procedure.replay_arguments(manifest, args, target, output.parent)
    receipt = json.loads((output.parent / "formal-replay-attempt.json").read_text())
    assert receipt["target_commit"] is None
    assert len(receipt["capture"]["sha256"]) == 64
    with pytest.raises(SystemExit, match="already consumed"):
        assessment.procedure.replay_arguments(manifest, args, target, output.parent)
