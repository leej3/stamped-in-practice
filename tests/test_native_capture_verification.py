"""Synthetic native event verification; no sessions or hosted jobs are started."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import verify_native_capture as verify


def command_event(root, script="cat > proof.md <<'EOF'\nsynthetic proof\nEOF\n"):
    return {"type": "CommandExecution", "id": "native-exec-fixture",
            "command": ["/bin/bash", "-lc", script], "cwd": root.as_uri(),
            "status": "completed", "exit_code": 0, "aggregated_output": ""}


def transcript(root, event):
    return b"\n".join(json.dumps(item).encode() for item in [
        {"type": "session_meta", "payload": {"id": "fixture-session", "cwd": str(root), "source": "exec"}},
        {"type": "response_item", "payload": {"type": "reasoning", "text": "PRIVATE_REASONING_SENTINEL"}},
        {"type": "event_msg", "payload": {"type": "item_completed", "item": event}},
    ])


def test_literal_shell_write_has_hashes_without_exposing_command_or_content(tmp_path):
    event = command_event(tmp_path)
    evidence = verify.literal_heredoc_write(event, tmp_path / "proof.md")
    assert evidence["written_content_sha256"] == hashlib.sha256(b"synthetic proof\n").hexdigest()
    assert evidence["written_content_bytes"] == len(b"synthetic proof\n")
    assert evidence["command_cwd"] == str(tmp_path)
    assert evidence["following_git_status_verified"] is False
    assert "synthetic proof" not in json.dumps(evidence)


def test_observed_formatter_and_status_tail_requires_captured_file_status(tmp_path):
    event = command_event(tmp_path, "cat > proof.md <<'EOF'\nproof\nEOF\n"
                          "/Users/fixture/.local/bin/snapper --in-place proof.md\n\ngit status --short")
    event["aggregated_output"] = "?? proof.md\n"
    assert verify.literal_heredoc_write(event, tmp_path / "proof.md")["following_git_status_verified"]
    event["aggregated_output"] = "bash: proof.md: Permission denied\n?? proof.md\n"
    assert verify.literal_heredoc_write(event, tmp_path / "proof.md") is None


@pytest.mark.parametrize("script", [
    "cat proof.md", "printf 'cat > proof.md'", "cat > proof.md <<EOF\n$SECRET\nEOF\n",
    "cat > different.md <<'EOF'\nproof\nEOF\n",
    "cat > proof.md <<'EOF'\nproof\nEOF\nfalse; true",
    "cat > proof.md <<'EOF'\nproof\nEOF\nfalse\ngit status --short",
    "cat > proof.md <<'EOF'\nproof\nEOF\nrm proof.md\ngit status --short",
    "cat > proof.md <<'EOF'\nproof\nEOF\ncat > proof.md <<'EOF'\nchanged\nEOF\n",
])
def test_read_mentions_expansion_and_unverified_compound_commands_are_not_write_proof(tmp_path, script):
    event = command_event(tmp_path, script)
    event["aggregated_output"] = "?? proof.md\n"
    assert verify.literal_heredoc_write(event, tmp_path / "proof.md") is None


@pytest.mark.parametrize("change", [{"status": "failed"}, {"exit_code": 1},
                                    {"cwd": "file://remote.example/checkout"}, {"cwd": "relative"}])
def test_native_completion_and_local_cwd_are_required(tmp_path, change):
    event = command_event(tmp_path)
    event.update(change)
    assert verify.literal_heredoc_write(event, tmp_path / "proof.md") is None


def test_file_urls_decode_and_child_relative_writes_use_actual_command_cwd(tmp_path):
    child = tmp_path / "child with spaces"
    child.mkdir()
    event = command_event(child)
    identities, events = verify.native_evidence(transcript(tmp_path, event), "fixture-session", tmp_path, child, "proof.md")
    assert identities[0]["cwd"] == str(tmp_path)
    assert events[0]["command_cwd"] == str(child)
    assert verify.literal_heredoc_write(event, tmp_path / "proof.md") is None


def test_existing_native_file_change_events_still_verify(tmp_path):
    event = {"type": "FileChange", "id": "patch-fixture", "status": "completed",
             "changes": {"proof.md": {"type": "add"}}}
    _, events = verify.native_evidence(transcript(tmp_path, event), "fixture-session", tmp_path, tmp_path, "proof.md")
    assert events == [{"line": 3, "item_id": "patch-fixture", "file": "proof.md",
                       "evidence_kind": "completed-file-change"}]


@pytest.mark.parametrize("committed_path", ["proof.md", "unrelated.md"])
def test_verifier_requires_linked_commit_change_and_retains_only_metadata(tmp_path, monkeypatch, capsys, committed_path):
    commit = "a" * 40
    checkpoint = "fixture-checkpoint"
    raw = transcript(tmp_path, command_event(tmp_path))
    def run(argv, cwd):
        if argv[0] == "entire":
            if "--transcript" in argv:
                return raw
            return json.dumps({"checkpoint_id": checkpoint, "sessions": [{
                "session_id": "fixture-session", "agent": "Codex", "files_touched": ["proof.md"], "index": 0,
            }]}).encode()
        if argv[1] == "rev-parse":
            return commit.encode()
        if argv[1] == "merge-base":
            return b""
        if argv[1] == "show" and "-s" in argv:
            return b"test: fixture\n\nCo-Authored-By: Codex Desktop fixture\nCodex-Reasoning-Effort: high\n"
        if argv[1] == "show":
            return b"final formatted synthetic proof\n"
        if argv[1] == "diff-tree":
            return committed_path.encode() + b"\0"
        if argv[1] == "for-each-ref":
            return f"refs/entire/checkpoints/{checkpoint} {commit}\n".encode()
        raise AssertionError(argv)
    monkeypatch.setattr(verify, "run", run)
    receipt = tmp_path / "receipt.json"
    monkeypatch.setattr(sys, "argv", ["verify", "--checkout", str(tmp_path), "--commit", commit,
        "--session", "fixture-session", "--file", "proof.md", "--output", str(receipt),
        "--code-ref", "refs/heads/fixture"])
    if committed_path != "proof.md":
        with pytest.raises(SystemExit, match="linked commit"):
            verify.main()
        assert not receipt.exists()
        return
    verify.main()
    result = json.loads(receipt.read_text())
    assert result["native_capture_verified"] is True
    assert result["file_events"][0]["evidence_kind"] == "completed-literal-heredoc-write"
    assert result["committed_file_sha256"] == hashlib.sha256(b"final formatted synthetic proof\n").hexdigest()
    assert result["file_events"][0]["written_content_sha256"] != result["committed_file_sha256"]
    assert "PRIVATE_REASONING_SENTINEL" not in receipt.read_text() + capsys.readouterr().out
