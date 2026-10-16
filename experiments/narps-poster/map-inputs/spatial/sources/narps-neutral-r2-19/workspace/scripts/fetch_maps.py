"""Restore the exact participant effect maps referenced by input/sources.json."""
from __future__ import annotations

import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "input" / "sources.json"
DEST = ROOT / "work" / "maps"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    DEST.mkdir(parents=True, exist_ok=True)
    specs = [(rel, spec) for rel, spec in manifest["files"].items() if rel.endswith(".nii.gz")]

    def fetch(item):
        rel, spec = item
        target = DEST / Path(rel).name
        if target.exists() and sha256(target) != spec["sha256"]:
            target.unlink()
        if not target.exists():
            subprocess.run(["curl", "-fsSL", "--retry", "4", "--retry-delay", "1", "-A", "Mozilla/5.0 (compatible; NARPS-group-analysis/1.0)", "-o", str(target), spec["url"]], check=True)
        digest = sha256(target)
        if digest != spec["sha256"]:
            raise ValueError(f"Checksum mismatch for {rel}: {digest}")
        return {"participant_id": spec["participant_id"], "file": str(target.relative_to(ROOT)), "bytes": target.stat().st_size, "sha256": digest}

    rows = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(fetch, item) for item in specs]
        for future in as_completed(futures):
            rows.append(future.result())
            print(f"Verified {len(rows)}/{len(specs)} maps", flush=True)
    rows.sort(key=lambda x: x["participant_id"])
    if len(rows) != 54:
        raise ValueError(f"Expected 54 maps, found {len(rows)}")
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "input-integrity.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(f"Verified {len(rows)} maps ({sum(x['bytes'] for x in rows):,} bytes).")


if __name__ == "__main__":
    main()
