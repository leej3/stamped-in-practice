#!/usr/bin/env python3
"""Read actual stored native evidence, optionally uploaded and hosted identities.

Raw transcripts are inspected in memory and hashed, never printed or copied.
"""
import argparse
import hashlib
import json
import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse


def run(argv, cwd):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"Read-only command failed: {argv[0]} (exit {result.returncode})")
    return result.stdout


def native_path(value):
    """Native command cwd is sometimes a file URL rather than a path."""
    if not isinstance(value, str):
        return None
    if value.startswith("file:"):
        parsed = urlparse(value)
        if parsed.scheme != "file" or parsed.netloc not in ("", "localhost"):
            return None
        value = unquote(parsed.path)
    path = Path(value)
    return path.resolve() if path.is_absolute() else None


def literal_heredoc_write(event, target):
    """Recognize one literal shell write without interpreting arbitrary code.

    Require a quoted delimiter, literal path and exact cwd/path identity.
    Allow only the observed optional Snapper/status tail, with captured status
    output and no error text. Arbitrary compound commands are not proof.
    """
    if (event.get("type") not in ("CommandExecution", "command_execution") or
            event.get("status") != "completed" or event.get("exit_code") != 0):
        return None
    argv = event.get("command")
    if (not isinstance(argv, list) or len(argv) != 3 or
            not all(isinstance(value, str) for value in argv) or
            Path(argv[0]).name not in ("bash", "sh", "zsh") or argv[1] not in ("-c", "-lc")):
        return None
    cwd = native_path(event.get("cwd"))
    if cwd is None:
        return None
    lines = argv[2].splitlines(keepends=True)
    if len(lines) < 2:
        return None
    header = re.fullmatch(
        r"cat[ \t]+>[ \t]*(?P<path>[A-Za-z0-9_./-]+)[ \t]+<<[ \t]*"
        r"(?P<quote>['\"])(?P<delimiter>[A-Za-z_][A-Za-z0-9_]*)(?P=quote)[ \t]*\n",
        lines[0])
    if not header or (cwd / header["path"]).resolve() != target.resolve():
        return None
    delimiter = header["delimiter"]
    ends = [index for index, line in enumerate(lines[1:], 1)
            if line in (delimiter, delimiter + "\n")]
    if not ends:
        return None
    end = ends[0]
    tail = [line.strip() for line in lines[end + 1:] if line.strip()]
    status_proof = False
    if tail:
        if tail[-1] != "git status --short" or len(tail) > 2:
            return None
        if len(tail) == 2:
            try:
                formatter = shlex.split(tail[0])
            except ValueError:
                return None
            if (len(formatter) != 3 or Path(formatter[0]).name != "snapper" or
                    formatter[1] != "--in-place" or formatter[2] != header["path"]):
                return None
        output = event.get("aggregated_output", "")
        allowed_status = {prefix + " " + header["path"] for prefix in ("??", " M", "A ", "AM")}
        status_lines = output.splitlines() if isinstance(output, str) else []
        if len(status_lines) != 1 or status_lines[0] not in allowed_status:
            return None
        status_proof = True
    if len(ends) != 1:
        return None
    content = "".join(lines[1:end]).encode()
    return {"evidence_kind": "completed-literal-heredoc-write", "command_cwd": str(cwd),
            "following_git_status_verified": status_proof,
            "command_sha256": hashlib.sha256(json.dumps(argv, separators=(",", ":")).encode()).hexdigest(),
            "written_content_sha256": hashlib.sha256(content).hexdigest(),
            "written_content_bytes": len(content)}


def native_evidence(transcript, identity_id, root, event_root, file):
    """Extract identity and completed file-write metadata, never reasoning."""
    identities, events = [], []
    names = {str(event_root / file)}
    if event_root == root:
        names.add(file)
    for number, raw in enumerate(transcript.splitlines(), 1):
        try:
            item = json.loads(raw)
        except json.JSONDecodeError:
            continue
        payload = item.get("payload", {})
        if item.get("type") == "session_meta" and payload.get("id") == identity_id:
            identities.append({"session_id": payload["id"], "cwd": payload.get("cwd"),
                               "source": payload.get("source")})
        event = payload.get("item", {})
        if item.get("type") != "event_msg" or payload.get("type") != "item_completed" or not isinstance(event, dict):
            continue
        proof = None
        if event.get("type") in ("FileChange", "file_change") and event.get("status") == "completed":
            changes = event.get("changes", {})
            paths = set(changes) if isinstance(changes, dict) else {c.get("path") for c in changes if isinstance(c, dict)}
            if paths & names:
                proof = {"evidence_kind": "completed-file-change"}
        else:
            proof = literal_heredoc_write(event, event_root / file)
        if proof:
            events.append({"line": number, "item_id": event.get("id"), "file": file, **proof})
    return identities, events


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkout", type=Path, required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--session", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--code-ref", required=True)
    p.add_argument("--hosted-repo")
    p.add_argument("--require-uploaded", action="store_true")
    p.add_argument("--task", help="Native child agent ID stored under the parent checkpoint")
    p.add_argument("--event-checkout", type=Path,
                   help="Explicit child-owned checkout when the native session cwd remains the parent's")
    p.add_argument("--event-commit", help="Actual child commit in --event-checkout")
    args = p.parse_args()
    root = args.checkout.resolve()
    event_root = args.event_checkout.resolve() if args.event_checkout else root
    if args.output.exists():
        raise SystemExit("Receipt exists; preserve it")
    commit = run(["git", "rev-parse", args.commit], root).decode().strip()
    code_ref_oid = run(["git", "rev-parse", args.code_ref], root).decode().strip()
    run(["git", "merge-base", "--is-ancestor", commit, code_ref_oid], root)
    message = run(["git", "show", "-s", "--format=%B", commit], root).decode()
    if "Co-Authored-By: Codex Desktop " not in message or "Codex-Reasoning-Effort: " not in message or "unavailable" in message:
        raise SystemExit("Exact Codex commit provenance missing")
    metadata = json.loads(run(["entire", "checkpoint", "explain", "--commit", commit, "--json"], root))
    sessions = [s for s in metadata["sessions"] if s["session_id"] == args.session]
    if len(sessions) != 1:
        raise SystemExit("Expected unique native session missing from checkpoint")
    session = sessions[0]
    if session.get("agent", "").lower() != "codex" or (not args.task and args.file not in session.get("files_touched", [])):
        raise SystemExit("Expected Codex file event absent from metadata")
    transcript_args = ["entire", "checkpoint", "explain", "--commit", commit, "--transcript",
                       "--session-index", str(session["index"])]
    identity_id = args.session
    if args.task:
        tasks = [t for t in metadata.get("tasks", []) if t.get("agent_id") == args.task]
        if len(tasks) != 1 or not tasks[0].get("transcript_stored"):
            raise SystemExit("Native child task/transcript metadata missing")
        # Cross-worktree tasks can omit the summary file list. Require the
        # actual completed native file event below in every case.
        if tasks[0].get("files") and args.file not in tasks[0]["files"]:
            raise SystemExit("Native task file summary contradicts expected file")
        # The native CLI makes --task and --session-index mutually exclusive.
        transcript_args = ["entire", "checkpoint", "explain", "--commit", commit,
                           "--transcript", "--task", args.task]
        identity_id = args.task
    transcript = run(transcript_args, root)
    identities, events = native_evidence(transcript, identity_id, root, event_root, args.file)
    if not identities or not any(native_path(i["cwd"]) == root for i in identities) or not events:
        raise SystemExit("Stored native session/cwd/completed file-write evidence missing")
    child_commit = None
    if args.event_commit:
        child_commit = run(["git", "rev-parse", args.event_commit], event_root).decode().strip()
        changed = run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", child_commit], event_root).decode().splitlines()
        child_message = run(["git", "show", "-s", "--format=%B", child_commit], event_root).decode()
        if changed != [args.file] or "Co-Authored-By: Codex Desktop " not in child_message or "unavailable" in child_message:
            raise SystemExit("Child commit changed unexpected paths or lacks exact provenance")
    event_commit = child_commit or commit
    changed = run(["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-z", "-r", event_commit], event_root).split(b"\0")
    if args.file.encode() not in changed:
        raise SystemExit("Recorded file-write is absent from the linked commit changes")
    committed_blob = run(["git", "show", event_commit + ":" + args.file], event_root)
    refrows = run(["git", "for-each-ref", "--format=%(refname) %(objectname)", "refs/entire/checkpoints"], root).decode().splitlines()
    matches = [r.split() for r in refrows if r.split()[0].endswith("/" + metadata["checkpoint_id"])]
    if len(matches) != 1:
        raise SystemExit("Checkpoint ref identity ambiguous")
    ref, oid = matches[0]
    result = {"verified_at": datetime.now(timezone.utc).isoformat(), "checkout": str(root),
              "commit": commit, "code_ref": args.code_ref, "checkpoint_id": metadata["checkpoint_id"],
              "code_ref_oid": code_ref_oid, "child_task_id": args.task,
              "event_checkout": str(event_root), "event_commit": child_commit,
              "checkpoint_ref": ref, "checkpoint_oid": oid, "branch": metadata.get("branch"),
              "session_id": args.session, "all_checkpoint_session_ids": [s["session_id"] for s in metadata["sessions"]],
              "native_capture_verified": True, "identities": identities, "file_events": events,
              "committed_file_sha256": hashlib.sha256(committed_blob).hexdigest(),
              "transcript_sha256": hashlib.sha256(transcript).hexdigest(), "transcript_bytes": len(transcript),
              "private_guidance_marker_hits": [s for s in ("memory/transport.json", "sensitive transport configuration",
                 "private overlay", "Hub token file") if s.encode() in transcript],
              "raw_transcript_saved": False, "uploaded_refs_verified": False, "hosted_verified": False}
    if args.require_uploaded:
        remote = run(["git", "remote", "get-url", "--push", "origin"], root).decode().strip()
        if not remote.startswith("git@github.com:"):
            raise SystemExit("Expected configured SSH push remote")
        refs = {args.code_ref: code_ref_oid, ref: oid}
        actual = dict(reversed(row.split()) for row in run(["git", "ls-remote", "--refs", remote, *refs], root).decode().splitlines())
        if actual != refs:
            raise SystemExit("Uploaded refs differ from expected exact OIDs")
        result["uploaded_refs_verified"] = True
    if args.hosted_repo:
        hosted = json.loads(run(["entire", "checkpoint", "explain", metadata["checkpoint_id"],
                                "--repo", args.hosted_repo, "--json"], root))
        ids = [s["session_id"] for s in hosted.get("sessions", [])]
        result["hosted_verified"] = hosted.get("checkpoint_id") == metadata["checkpoint_id"] and args.session in ids
        result["hosted_session_ids"] = ids
        if args.task:
            result["hosted_child_task_verified"] = any(t.get("agent_id") == args.task and t.get("transcript_stored")
                for t in hosted.get("tasks", []))
            result["hosted_verified"] = result["hosted_verified"] and result["hosted_child_task_verified"]
        if not result["hosted_verified"]:
            raise SystemExit("Hosted metadata did not match")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
