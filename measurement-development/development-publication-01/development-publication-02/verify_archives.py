"""Verify complete archive members from the independently downloaded payloads."""
from pathlib import Path
import hashlib
import json
import tarfile

ROOT = Path(__file__).resolve().parent
recipient = ROOT / "fresh-recipient"
publication = json.loads((ROOT / "publication-result.json").read_bytes())
assert publication["verified"]
rows = []
for name in ["measurement-development/assessment-operational-live-trial-01",
             "skill-reflection/research-skill-revision-01"]:
    directory = recipient / name
    manifest = json.loads((directory / "manifest.json").read_bytes())
    expected = {row["path"]: row for row in manifest["entries"]}
    seen = set()
    with tarfile.open(directory / "trial-and-runtime.tar.gz", "r:gz") as archive:
        for member in archive:
            assert member.name in expected and member.name not in seen
            seen.add(member.name)
            row = expected[member.name]
            assert member.mode == row["mode"]
            if row["type"] == "directory":
                assert member.isdir()
            elif row["type"] == "symlink":
                assert member.issym() and member.linkname == row["target"]
            else:
                assert member.isfile() or member.islnk()
                with archive.extractfile(member) as stream:
                    assert hashlib.file_digest(stream, "sha256").hexdigest() == row["sha256"]
    assert seen == set(expected)
    rows.append({"path": name, "entries_verified": len(seen),
        "manifest_sha256": hashlib.sha256((directory / "manifest.json").read_bytes()).hexdigest(),
        "member_bytes_modes_links_exact": True})
result = {"verified": True, "publication_commit": publication["commit"],
          "independent_recipient": str(recipient), "archives": rows,
          "scientific_execution": False}
(ROOT / "archive-member-verification.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
