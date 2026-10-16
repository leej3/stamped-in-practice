#!/usr/bin/env python3
"""Prepare one existing checkout before native launch; never publish or fabricate capture.

Caller serializes this operation. Unknown hook changes and explicit denials fail.
The receipt proves installation/trust only; a real native probe is still required.
"""
import argparse
import fcntl
import hashlib
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run(argv, cwd):
    result = subprocess.run([str(x) for x in argv], cwd=cwd, capture_output=True, text=True)
    print(json.dumps({"argv": [str(x) for x in argv], "returncode": result.returncode,
                      "stdout": result.stdout, "stderr": result.stderr}))
    result.check_returncode()
    return result.stdout.strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", required=True, type=Path)
    parser.add_argument("--approved-hooks", type=Path)
    parser.add_argument("--trust-sync", type=Path)
    parser.add_argument("--resolver", required=True, type=Path)
    parser.add_argument("--checkpoint-repo")
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--provenance-only", action="store_true",
                        help="Install Git provenance chain in a replay clone; no native session/trust setup")
    args = parser.parse_args()
    checkout = args.checkout.expanduser().resolve()
    receipt = args.receipt.expanduser().resolve()
    if receipt.exists():
        raise SystemExit("Receipt already exists; preserve prior attempt")
    head = run(["git", "rev-parse", "HEAD"], checkout)
    hook_helper = Path(__file__).resolve().with_name("commit_provenance_hook.py")
    if not args.resolver.is_file() or not hook_helper.is_file():
        raise SystemExit("Missing explicit provenance prerequisite")
    if not args.provenance_only and not all((args.approved_hooks, args.trust_sync, args.checkpoint_repo)):
        parser.error("Native setup requires --approved-hooks, --trust-sync and --checkpoint-repo")
    hook = Path(run(["git", "rev-parse", "--git-path", "hooks/prepare-commit-msg"], checkout))
    if not hook.is_absolute():
        hook = checkout / hook
    hook = hook.resolve()
    previous = hook.with_name("prepare-commit-msg.before-stamped")
    native_previous = hook.with_name("prepare-commit-msg.pre-entire")
    marker = "# STAMPED provenance chain v1"
    target_hook = hook
    old = hook.read_text() if hook.exists() else ""
    if "# Entire CLI hooks" in old and "prepare-commit-msg.pre-entire" in old:
        if not native_previous.is_file() or marker not in native_previous.read_text():
            raise SystemExit("Existing native chain is not owned by this initializer; preserve and review")
        target_hook = native_previous
    elif old and marker not in old:
        if previous.exists() and previous.read_text() != old:
            raise SystemExit("Previous hook backup exists with different bytes; preserve and review")
        previous.write_bytes(hook.read_bytes())
        previous.chmod(hook.stat().st_mode)
    wrapper = "#!/bin/sh\nset -e\n" + marker + "\n"
    # Native Entire will wrap this hook itself. Do not call an older Entire hook
    # from its own chain. Preserve that old file as evidence, without executing it.
    if previous.exists() and "# Entire CLI hooks" not in previous.read_text():
        wrapper += shlex.quote(str(previous)) + ' "$@"\n'
    wrapper += 'repo_root=$(git rev-parse --show-toplevel)\n'
    wrapper += 'helper="$repo_root/scripts/commit_provenance_hook.py"\n'
    wrapper += '[ -f "$helper" ] || helper=' + shlex.quote(str(hook_helper)) + '\n'
    wrapper += "exec " + shlex.quote(sys.executable) + ' "$helper" --resolver ' + \
        shlex.quote(str(args.resolver.resolve())) + ' "$1"\n'
    hook.parent.mkdir(parents=True, exist_ok=True)
    if not target_hook.exists() or target_hook.read_text() != wrapper:
        target_hook.write_text(wrapper)
    if target_hook.stat().st_mode & 0o777 != 0o755:
        target_hook.chmod(0o755)
    if not args.provenance_only:
        run(["entire", "enable", "--agent", "codex", "--no-init-repo", "--local",
             "--checkpoint-backend", "refs", "--checkpoint-remote", "github:" + args.checkpoint_repo,
             "--skip-push-sessions", "--telemetry=false", "--absolute-git-hook-path"], checkout)
        target = checkout / ".codex/hooks.json"
        if target.read_bytes() != args.approved_hooks.read_bytes():
            raise SystemExit("Native hooks differ from approved source; native review required")
        lock = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "stamped-trust-sync.lock"
        with lock.open("a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            command = [sys.executable, args.trust_sync, "--worktree", checkout,
                       "--source", args.approved_hooks]
            run(command + ["--dry-run"], checkout)
            run(command, checkout)
    result = {"schema_version": 1, "prepared_at": datetime.now(timezone.utc).isoformat(),
              "checkout": str(checkout), "head": head, "provenance_only": args.provenance_only,
              "native_capture_verified": False, "publication_enabled": False,
              "provenance_hook_sha256": sha(hook), "resolver_sha256": sha(args.resolver),
              "checkpoint_repo": args.checkpoint_repo}
    if not args.provenance_only:
        result["native_hooks_sha256"] = sha(checkout / ".codex/hooks.json")
        result["settings"] = json.loads((checkout / ".entire/settings.local.json").read_text())
        result["entire_status"] = json.loads(run(["entire", "status", "--json"], checkout))
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "prepared", "receipt": str(receipt), "native_probe_required": True}))


if __name__ == "__main__":
    main()
