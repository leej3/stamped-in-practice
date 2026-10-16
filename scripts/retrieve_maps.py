#!/usr/bin/env python3
"""Retrieve manifest-listed participant maps and verify source byte identities."""
import concurrent.futures
import hashlib
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "input/sources.json").read_text())
items = [(p, d) for p, d in manifest["files"].items() if p.endswith(".nii.gz")]

def fetch(item):
    rel, info = item
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        payload = out.read_bytes()
    else:
        req = urllib.request.Request(info["url"], headers={"User-Agent": "NARPS-group-study/1.0"})
        with urllib.request.urlopen(req, timeout=90) as response:
            payload = response.read()
        out.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    ok = len(payload) == info["bytes"] and digest == info["sha256"]
    if not ok:
        raise ValueError(f"{rel}: bytes={len(payload)} sha256={digest}; manifest mismatch")
    return rel, len(payload), digest

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    results = list(pool.map(fetch, items))
for row in results:
    print(*row)
print(f"verified {len(results)} maps; {sum(row[1] for row in results)} bytes")
