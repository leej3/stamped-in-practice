"""Verify all original prefix files and content keys after structural migration."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--dataset", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
root = a.dataset.resolve()
manifest = root / "migration/original-manifest.json"
m = json.loads(manifest.read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
records = []
for row in m["records"]:
    target = root / row["path"]
    if "annex_key" in row:
        assert target.is_symlink(), row["path"]
        link = os.readlink(target)
        assert Path(link).name == row["annex_key"], row["path"]
        data = target.read_bytes()
        assert len(data) == row["payload_bytes"], row["path"]
        assert sha(data) == row["payload_sha256"], row["path"]
        records.append({"path": row["path"], "annex_key": row["annex_key"],
                        "new_link": link, "payload_sha256": sha(data)})
    else:
        data = os.readlink(target).encode() if target.is_symlink() else target.read_bytes()
        assert sha(data) == row["git_blob_sha256"], row["path"]
        assert row["mode"] != "100755" or os.access(target, os.X_OK), row["path"]
        records.append({"path": row["path"], "git_blob_sha256": sha(data)})
tracked = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"]).decode().split("\0")
original = {r["path"] for r in m["records"]}
assert original <= set(tracked)
result = {"success": True, "original_manifest_sha256": sha(manifest.read_bytes()),
          "source_commit": m["source_commit"], "original_paths": len(records),
          "annex_paths": len([r for r in records if "annex_key" in r]),
          "unique_annex_keys": len({r["annex_key"] for r in records if "annex_key" in r}),
          "original_path_and_keyset_preserved": True,
          "added_paths": sorted(set(tracked) - original - {""}), "records": records}
a.output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k not in ("records", "added_paths")}, indent=2))
