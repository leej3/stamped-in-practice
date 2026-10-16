"""Archive closed trial and its observed interpreter environment without exclusions."""
from pathlib import Path
import hashlib
import json
import os
import stat
import tarfile
import time

OUT = Path(__file__).resolve().parent
SOURCES = {
    "trial": OUT.parent / "research-skill-revision-01",
    "coordinator-runtime": Path("/Users/johnlee/code/CON/stamped-in-practice/.pixi/envs/default"),
    "coordinator-pixi.toml": Path("/Users/johnlee/code/CON/stamped-in-practice/pixi.toml"),
    "coordinator-pixi.lock": Path("/Users/johnlee/code/CON/stamped-in-practice/pixi.lock"),
}


def digest(stream):
    result = hashlib.sha256()
    while block := stream.read(1024 * 1024):
        result.update(block)
    return result.hexdigest()


def inventory():
    result = []
    for prefix, source in SOURCES.items():
        def visit(path):
            metadata = path.lstat()
            relative = path.relative_to(source)
            name = prefix if str(relative) == "." else prefix + "/" + str(relative)
            row = {"path": name, "mode": stat.S_IMODE(metadata.st_mode)}
            if stat.S_ISLNK(metadata.st_mode):
                row.update(type="symlink", target=os.readlink(path))
            elif stat.S_ISDIR(metadata.st_mode):
                row.update(type="directory")
            elif stat.S_ISREG(metadata.st_mode):
                with path.open("rb") as stream:
                    row.update(type="file", size=metadata.st_size, sha256=digest(stream))
            else:
                raise ValueError("Unsupported special file: " + str(path))
            result.append(row)
            if row["type"] == "directory":
                for child in sorted(path.iterdir()):
                    visit(child)
        visit(source)
    return result


def save(name, value):
    with (OUT / name).open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


start = time.time()
before = inventory()
save("manifest.json", {"schema_version": 1,
    "scope": "Complete closed research-guidance revision evidence and exact coordinator runtime used by its fresh-venv replay. No exclusions, scientific edits or replay.",
    "sources": {k: str(v) for k, v in SOURCES.items()}, "entries": before})
print(json.dumps({"state": "inventoried", "entries": len(before)}), flush=True)
archive = OUT / "trial-and-runtime.tar.gz"
with tarfile.open(archive, "x:gz", compresslevel=3, dereference=False) as tar:
    for row in before:
        parts = Path(row["path"]).parts
        path = SOURCES[parts[0]].joinpath(*parts[1:])
        tar.add(path, arcname=row["path"], recursive=False)
print(json.dumps({"state": "archived", "bytes": archive.stat().st_size}), flush=True)
expected = {row["path"]: row for row in before}
seen = set()
with tarfile.open(archive, "r:gz") as tar:
    for member in tar:
        assert member.name in expected and member.name not in seen, member.name
        seen.add(member.name)
        row = expected[member.name]
        assert member.mode == row["mode"], member.name
        if row["type"] == "directory":
            assert member.isdir(), member.name
        elif row["type"] == "symlink":
            assert member.issym() and member.linkname == row["target"], member.name
        else:
            assert member.isfile() or member.islnk(), member.name
            with tar.extractfile(member) as stream:
                assert digest(stream) == row["sha256"], member.name
assert seen == set(expected)
after = inventory()
assert before == after, "A source changed during packaging"
with archive.open("rb") as stream:
    archive_hash = digest(stream)
save("verification.json", {"verified": True, "archive": archive.name,
    "archive_sha256": archive_hash, "archive_bytes": archive.stat().st_size,
    "entries": len(before), "regular_files": sum(r["type"] == "file" for r in before),
    "regular_bytes": sum(r.get("size", 0) for r in before),
    "symlinks": sum(r["type"] == "symlink" for r in before),
    "manifest_sha256": hashlib.sha256((OUT / "manifest.json").read_bytes()).hexdigest(),
    "all_member_bytes_modes_links_verified": True, "sources_before_after_equal": True,
    "exclusions": [], "elapsed_seconds": time.time() - start,
    "limitation": "Literal absolute links retain provenance and may require relocation; no claim of another-host executability. Host OS and CLI are identified by the trial receipts, not included in the runtime member set."})
print(json.dumps(read := json.loads((OUT / "verification.json").read_bytes())), flush=True)
