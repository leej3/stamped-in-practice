#!/usr/bin/env python3
"""Create an isolated native launch profile without private global instructions.

Reuse the existing host auth provider by symlink, without reading credentials.
Only already approved source hook hashes are copied. Target trust still requires
the byte-identical native hook sync and a real capture test.
"""
import argparse
import hashlib
import json
import os
import tomllib
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--profile", type=Path, required=True)
    p.add_argument("--source-home", type=Path, required=True)
    p.add_argument("--approved-hooks", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    args = p.parse_args()
    profile, source = args.profile.expanduser().resolve(), args.source_home.expanduser().resolve()
    if profile.exists() or args.receipt.exists():
        raise SystemExit("Profile/receipt exists; preserve previous attempt")
    config = tomllib.loads((source / "config.toml").read_text())
    hook_path = str(args.approved_hooks.expanduser().resolve())
    states = {k: v for k, v in config.get("hooks", {}).get("state", {}).items()
              if k.startswith(hook_path + ":")}
    if not states or any(v.get("disabled") or not v.get("trusted_hash") for v in states.values()):
        raise SystemExit("Source hook approvals absent or disabled")
    auth = source / "auth.json"
    if not auth.is_file():
        raise SystemExit("Existing host auth provider file unavailable; do not create credentials")
    profile.mkdir(parents=True, mode=0o700)
    # No global hooks, private AGENTS, memories, skill trees or MCP credentials.
    text = "[features]\nhooks = true\nmulti_agent = true\nskip_host_skill_discovery = true\n\n"
    for key, value in sorted(states.items()):
        text += "[hooks.state." + json.dumps(key) + "]\ntrusted_hash = " + json.dumps(value["trusted_hash"]) + "\n\n"
    # The installed runtime still advertises ~/.agents skills despite the
    # skip-host feature. Official per-skill controls close that observed gap.
    host_skills = sorted({str(p) for root in (Path.home() / ".agents/skills", source / "skills")
                          for p in root.glob("*/SKILL.md")})
    for skill in host_skills:
        text += "[[skills.config]]\npath = " + json.dumps(skill) + "\nenabled = false\n\n"
    (profile / "config.toml").write_text(text)
    (profile / "config.toml").chmod(0o600)
    os.symlink(auth, profile / "auth.json")
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps({"profile": str(profile), "source_hooks": hook_path,
        "approved_source_records": len(states), "config_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "disabled_host_skill_count": len(host_skills),
        "credential_contents_read": False, "credential_contents_copied": False,
        "auth_provider": "symlink to existing host auth.json", "global_instructions_copied": False,
        "target_capture_not_yet_verified": True}, indent=2) + "\n")


if __name__ == "__main__":
    main()
