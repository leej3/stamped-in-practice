#!/usr/bin/env python3
"""Append freshly resolved active-turn provenance; preserve DataLad records."""
import argparse
import re
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resolver", type=Path, required=True)
    parser.add_argument("message", type=Path)
    args = parser.parse_args()
    text = args.message.read_text()
    native_record = text.startswith(("[DATALAD RUNCMD] ", "[DATALAD] "))
    # Native run records must begin with this exact marker for DataLad rerun.
    if not native_record and not re.match(r"^[a-z][a-z0-9-]*(?:\([^\r\n()]+\))?!?: [^\r\n]+", text):
        raise SystemExit("Commit subject must use Conventional Commits")
    resolved = subprocess.run([str(args.resolver)], check=True, capture_output=True, text=True)
    trailers = resolved.stdout.strip().splitlines()
    if any("unavailable" in line.lower() for line in trailers):
        raise SystemExit("Exact active-turn provenance unavailable; coordinator review required")
    if not any(line.startswith("Co-Authored-By: Codex Desktop ") for line in trailers):
        raise SystemExit("Fresh resolver omitted Codex provenance")
    if not any(line.startswith("Codex-Reasoning-Effort: ") for line in trailers):
        raise SystemExit("Fresh resolver omitted reasoning effort")
    # DataLad rerun may inherit the previous message. Replace only Codex-owned
    # provenance lines; keep other coauthors, Entire and DataLad records intact.
    lines = [line for line in text.splitlines()
             if not line.startswith(("Co-Authored-By: Codex Desktop ", "Codex-Reasoning-Effort:",
                                     "Codex-Thread-Id:", "Codex-Turn-Id:",
                                     "Codex-Provenance-Source:", "Codex-Provenance-Reference:",
                                     "Codex-Model-Unavailable:", "Codex-Effort-Unavailable:"))]
    args.message.write_text("\n".join(lines).rstrip() + "\n\n" + "\n".join(trailers) + "\n")


if __name__ == "__main__":
    main()
