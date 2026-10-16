"""Judge retention checks materialize preserved outputs using local annex stores."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import prepare_launch as prepare
import study_seed as seed
import worker_end_state as state
from test_assessment_procedure import comparison
from test_launch import commit, fake_cli, git, init


OUTPUT = "outputs/retained result.bin"
INPUT = "input/locked-reference.nii.gz"
PAYLOAD = b"stopped worker's scientific output\n" * 32768


def preserve_unlocked_output(repo):
    """Record real stopped bytes, then preserve them as an unlocked annex file."""
    git(repo, "config", "remote.origin.annex-ignore", "true")
    git(repo, "annex", "init", "worker-materialization-fixture")
    (repo / INPUT).parent.mkdir(parents=True, exist_ok=True)
    (repo / INPUT).write_bytes(b"unchanged optional input\n" * 256)
    git(repo, "annex", "add", "--backend=MD5E", "--force", "--", INPUT)
    assert (repo / INPUT).is_symlink()
    (repo / "notes.txt").write_text("Ordinary Git content must remain unchanged.\n")
    commit(repo, "test: retain locked input and ordinary Git content")
    (repo / OUTPUT).parent.mkdir()
    (repo / OUTPUT).write_bytes(PAYLOAD)
    receipt = state.capture_worker_end_state(repo)
    assert receipt["capture_status"] == "complete"
    git(repo, "annex", "add", "--backend=SHA256E", "--force", "--", OUTPUT)
    git(repo, "annex", "unlock", "--", OUTPUT)
    result_commit = commit(repo, "test: preserve worker output in unlocked annex")
    pointer = git(repo, "show", "HEAD:" + OUTPUT)
    assert pointer.startswith("/annex/objects/SHA256E-")
    return receipt, result_commit


def exact_clone(source, destination):
    """Fetch exact Git objects without sharing the source's annex object store."""
    init(destination)
    for ref in ("HEAD", "git-annex"):
        revision = git(source, "rev-parse", ref)
        git(destination, "fetch", "--no-tags", source,
            revision if ref == "HEAD" else revision + ":refs/heads/git-annex")
        if ref == "HEAD":
            git(destination, "reset", "--hard", "FETCH_HEAD")
    assert not (destination / ".git/annex/objects").exists()
    assert (destination / OUTPUT).is_file()
    assert (destination / OUTPUT).read_bytes().startswith(b"/annex/objects/SHA256E-")
    assert not (destination / INPUT).exists()
    git(destination, "annex", "init", "judge-materialization-fixture")
    git(destination, "remote", "add", "payload-store", source)
    return ["git", "-C", str(destination)]


@pytest.fixture
def preserved_result(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "file")
    worker = init(tmp_path / "worker")
    receipt, result_commit = preserve_unlocked_output(worker)
    judge = tmp_path / "judge"
    git_command = exact_clone(worker, judge)
    return worker, judge, receipt, result_commit, git_command


def test_unlocked_output_materializes_before_strict_retention_check(preserved_result, tmp_path):
    _, judge, receipt, result_commit, git_command = preserved_result
    tree = git(judge, "rev-parse", "HEAD^{tree}")
    with pytest.raises(ValueError, match="artifacts differ"):
        state.validate_retained_artifacts(receipt, judge)

    evidence = tmp_path / "materialization.json"
    retrieved = prepare.materialize_retained_files(git_command, judge, receipt, "payload-store", evidence)

    assert retrieved == [OUTPUT]
    assert (judge / OUTPUT).read_bytes() == PAYLOAD
    assert not (judge / INPUT).exists()
    report = state.validate_retained_artifacts(receipt, judge)
    assert report["artifacts_match"] is True
    assert report["annex_reference_identity_without_local_payload"] == [INPUT]
    assert git(judge, "rev-parse", "HEAD") == result_commit
    assert git(judge, "rev-parse", "HEAD^{tree}") == tree
    assert git(judge, "status", "--porcelain") == ""
    materialization = json.loads(evidence.read_text())
    assert materialization["paths"] == [OUTPUT]
    assert materialization["commands_succeeded"] is True
    assert materialization["verification"] == "requires-worker-retention-check"
    assert [command["returncode"] for command in materialization["commands"]] == [0, 0]


def test_no_original_regular_annex_paths_does_not_fetch_locked_inputs(preserved_result):
    _, judge, receipt, _, git_command = preserved_result
    original_files = [row for row in receipt["worktree"] if row["path"] != OUTPUT]
    selection = dict(receipt, worktree=original_files)

    assert prepare.materialize_retained_files(git_command, judge, selection, "payload-store") == []

    assert not (judge / INPUT).exists()
    assert (judge / OUTPUT).read_bytes().startswith(b"/annex/objects/SHA256E-")
    assert git(judge, "status", "--porcelain") == ""


def test_unavailable_preserved_output_fails_closed(preserved_result, tmp_path):
    worker, judge, receipt, _, git_command = preserved_result
    git(worker, "annex", "drop", "--force", "--", OUTPUT)

    evidence = tmp_path / "materialization.json"
    with pytest.raises(subprocess.CalledProcessError):
        prepare.materialize_retained_files(git_command, judge, receipt, "payload-store", evidence)

    with pytest.raises(ValueError, match="artifacts differ"):
        state.validate_retained_artifacts(receipt, judge)
    assert not (judge / INPUT).exists()
    assert git(judge, "status", "--porcelain") == ""
    failure = json.loads(evidence.read_text())
    assert failure["paths"] == [OUTPUT]
    assert failure["commands_succeeded"] is False
    assert failure["commands"][0]["returncode"] == 0
    assert failure["commands"][1]["returncode"] != 0
    assert failure["commands"][1]["argv"][-5:] == ["get", "--from", "payload-store", "--", OUTPUT]
    assert failure["commands"][1]["stdout"] or failure["commands"][1]["stderr"]


@pytest.mark.parametrize("available", [True, False])
def test_prepare_materializes_before_validation_and_judge_launch(comparison, tmp_path, monkeypatch, available):
    args, _ = comparison
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "file")
    result_repo = tmp_path / "submitted-result"
    seed.make_seed(args.repo, args.base, args.study, result_repo,
                   "codex/result", "baseline", args.resolver)
    receipt, target_commit = preserve_unlocked_output(result_repo)
    if not available:
        git(result_repo, "annex", "drop", "--force", "--", OUTPUT)
    stop_receipt = tmp_path / "worker-end-state.json"
    receipt_bytes = (json.dumps(receipt, indent=2) + "\n").encode()
    stop_receipt.write_bytes(receipt_bytes)
    target = tmp_path / "exact-target"
    evidence = tmp_path / "judge-evidence"
    prepared = []
    actual_run = prepare.run
    actual_materialize = prepare.materialize_retained_files

    def materialize_from_prepared_runtime(git_command, checkout, receipt, remote, evidence=None):
        command = [str(value) for value in git_command]
        return actual_materialize(command[command.index("git"):], checkout, receipt, remote, evidence)

    def host_run(argv, cwd, capture=False):
        command = [str(value) for value in argv]
        if command[:2] == ["pixi", "install"]:
            # The synthetic host manifest is only a fixture; annex is real and
            # comes from the prepared Pixi environment running this test.
            assert (target / OUTPUT).read_bytes().startswith(b"/annex/objects/SHA256E-")
            return None
        if command[:2] == ["pixi", "run"]:
            return actual_run(command[command.index("git"):], cwd, capture)
        if len(command) > 1 and command[1].endswith("/prepare_checkout.py"):
            assert (target / OUTPUT).read_bytes() == PAYLOAD
            check = json.loads((evidence / "worker-retention-check.json").read_text())
            assert check["artifacts_match"] is True
            prepared.append(Path(command[command.index("--checkout") + 1]))
            return None
        return actual_run(argv, cwd, capture)

    monkeypatch.setattr(prepare, "run", host_run)
    monkeypatch.setattr(prepare, "materialize_retained_files", materialize_from_prepared_runtime)
    monkeypatch.setattr(prepare, "__file__", str(args.repo / "scripts/prepare_launch.py"))
    monkeypatch.setattr(sys, "argv", ["prepare_launch.py", "--role", "judge",
        "--host-config", str(tmp_path / "no-defaults.json"), "--repo", str(result_repo),
        "--base", target_commit, "--branch", "codex/judge-fixture", "--clone-path", str(target),
        "--evidence", str(evidence), "--study", str(args.study), "--env-manifest", str(args.env_manifest),
        "--approved-hooks", str(args.approved_hooks), "--trust-sync", str(args.trust_sync),
        "--resolver", str(args.resolver), "--checkpoint-repo", "example/checkpoints",
        "--annex-git-url", str(result_repo), "--annex-url", str(result_repo),
        "--cli", str(args.cli), "--codex-home", str(args.codex_home), "--review-seconds", "0",
        "--worker-end-state", str(stop_receipt)])

    if not available:
        with pytest.raises((subprocess.CalledProcessError, SystemExit)) as failure:
            prepare.main()
        assert (evidence / "worker-end-state.json").read_bytes() == receipt_bytes
        assert prepared == []
        assert not (evidence / "judgment").exists()
        assert not (evidence / "native").exists()
        materialization = json.loads((evidence / "judge-annex-materialization.json").read_text())
        assert materialization["paths"] == [OUTPUT]
        if isinstance(failure.value, SystemExit):
            # Fresh location metadata can make annex get skip absent content
            # with exit zero; the unchanged validator must still stop judging.
            assert "Worker-stop evidence failed" in str(failure.value)
            assert materialization["commands_succeeded"] is True
            retention = json.loads((evidence / "worker-retention-check.json").read_text())
            assert retention["artifacts_match"] is False
            assert "artifacts differ" in retention["error"]
        else:
            assert materialization["commands_succeeded"] is False
            assert not (evidence / "worker-retention-check.json").exists()
        return

    prepare.main()

    workspace = evidence / "judgment"
    assert prepared == [workspace]
    assert (evidence / "worker-end-state.json").read_bytes() == receipt_bytes
    assert (target / OUTPUT).read_bytes() == PAYLOAD
    assert not (target / INPUT).exists()
    assert git(target, "rev-parse", "HEAD") == target_commit
    assert git(target, "rev-parse", "HEAD^{tree}") == git(result_repo, "rev-parse", "HEAD^{tree}")
    assert git(target, "status", "--porcelain") == ""
    native = json.loads((evidence / "native/result.json").read_text())
    assert native["cwd"] == str(workspace)
    assert native["target_unchanged"] is True
    assert not (target / "assessment.txt").exists()
