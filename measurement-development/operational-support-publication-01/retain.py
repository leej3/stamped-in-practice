"""Package closed Git-publication evidence without support payload duplication."""
from pathlib import Path
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile

OUT = Path(__file__).parent
BASE = OUT.parent
PUBLICATION = BASE / "operational-support-git-publication-01"
CLOSURE = BASE / "operational-support-git-publication-closure-01"
sys.path.insert(0, str(OUT / "methods"))
import package as method


def save(path, value):
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha(path):
    return method.sha(path)


def copy(source, target):
    before = sha(source)
    shutil.copy2(source, target)
    assert before == sha(source) == sha(target)


save(OUT / "command.json", {"started_at": datetime.now(timezone.utc).isoformat(),
     "argv": sys.argv, "python": sys.executable, "python_version": sys.version,
     "method_sha256": sha(Path(__file__)), "network_operations": False,
     "source_mutations": False, "scope": "Closed publication metadata only."})
index_path = CLOSURE / "index.json"
assert sha(index_path) == "67104128c74fb6449c7a037054d785a0dbcd70a31e336b6fb1bab15845cfe563"
index = json.loads(index_path.read_text())
excluded = [row["relative_path"] for row in index["excluded_caches"]]
assert len(excluded) == 22
before = method.inventory(PUBLICATION, excluded)
assert before == sorted(index["closed_files"], key=lambda row: row["path"])
assert len(before) == 11291
closure_before = method.inventory(CLOSURE, [])
rows = [{**row, "path": prefix + "/" + row["path"]}
        for prefix, entries in (("publication", before), ("closure", closure_before))
        for row in entries]
roots = {"publication": PUBLICATION, "closure": CLOSURE}
save(OUT / "source-manifest.json", {
    "schema": "operational-support-publication-retention-manifest-v1",
    "roots": {key: str(value) for key, value in roots.items()},
    "source_closure_sha256": sha(index_path), "entries": rows,
    "excluded_verified_git_caches": index["excluded_caches"],
    "publication_members": len(before), "external_closure_members": len(closure_before),
    "original_support_payloads": "Remain in their existing packages and linked annex paths; outside these closed source trees."})
archive = OUT / "publication-evidence.tar.gz"
with archive.open("xb") as file, gzip.GzipFile(fileobj=file, mode="wb", filename="",
        mtime=0, compresslevel=6) as compressed, tarfile.open(fileobj=compressed,
        mode="w|", format=tarfile.PAX_FORMAT) as stream:
    for row in rows:
        member = tarfile.TarInfo(row["path"])
        member.mode = row["mode"]
        member.uid = member.gid = member.mtime = 0
        if row["kind"] == "directory":
            member.type = tarfile.DIRTYPE
            stream.addfile(member)
        elif row["kind"] == "symlink":
            member.type = tarfile.SYMTYPE
            member.linkname = row["target"]
            stream.addfile(member)
        else:
            member.size = row["bytes"]
            prefix, relative = row["path"].split("/", 1)
            descriptor, name = method.safe._parent(roots[prefix], relative)
            try:
                payload, metadata = method.safe._file(descriptor, name)
                with payload:
                    stream.addfile(member, payload)
                    method.safe._stable(descriptor, name, metadata, payload)
            finally:
                os.close(descriptor)
verification = method.verify(archive, rows)
assert before == method.inventory(PUBLICATION, excluded)
assert closure_before == method.inventory(CLOSURE, [])
for source, target in ((PUBLICATION / "per-slot-map.json", "per-slot-map.json"),
                       (PUBLICATION / "result.json", "git-publication-result.json"),
                       (PUBLICATION / "handoff.json", "publication-handoff.json"),
                       (index_path, "publication-closure-index.json")):
    copy(source, OUT / target)
mapping = json.loads((OUT / "per-slot-map.json").read_text())
table = []
for row in mapping["slots"]:
    label = row["slot"].replace("narps-neutral-r1-", "")
    status = "Previously verified" if row["full_remote_completion"] else "Pending"
    table.append(f"| {label} | [Report]({row['report_url']}) | [Support]({row['support_url']}) | [Archive pointer]({row['archive_pointer_url']}) | {status} |")
(OUT / "README.md").write_text("""# Closed support-publication evidence

All 32 assessment slots have immutable Git links. Thirty support archives remain pending Hub upload and independent retrieval; slots 09-j01 and 13-j01 retain their earlier full verification.
The [slot map](per-slot-map.json) records each exact support commit, archive key, SHA256, size, and publication state.

The [publication evidence archive](publication-evidence.tar.gz) preserves all 11,291 closed publication members, including commands, ordinary-blob verification, source checks, the SSH timeout, and its successful bounded recovery.
The archive also retains the external closure index and its complete supporting records under `closure/`; publication members use `publication/`.
Only the 22 independently verified Git-recipient caches listed in the [source manifest](source-manifest.json) are excluded.
Their exact received commit and tree identities remain in the closure receipts.
Original support payloads remain at their linked annex paths.

The [package verification](package-verification.json) checks exact member sets, streamed file hashes, modes, literal links, gzip integrity, and unchanged sources before and after packaging.
The [Git publication result](git-publication-result.json) distinguishes readable Git evidence from pending Hub payload delivery.
No Hub operation, scientific execution, canonical reference, or gitlink update was performed for this retention package.

| Slot | Scientific report | Complete support | Archive identity | Hub state |
| --- | --- | --- | --- | --- |
""" + "\n".join(table) + "\n")
argv = ["snapper", "--in-place", "README.md"]
formatted = subprocess.run(argv, cwd=OUT, capture_output=True, text=True)
save(OUT / "format-command.json", {"argv": argv, "cwd": str(OUT),
     "returncode": formatted.returncode, "stdout": formatted.stdout, "stderr": formatted.stderr})
formatted.check_returncode()
save(OUT / "package-verification.json", {
    **verification, "completed_at": datetime.now(timezone.utc).isoformat(),
    "publication_members": len(before), "external_closure_members": len(closure_before),
    "publication_regular_file_bytes": sum(row.get("bytes", 0) for row in before),
    "source_before_after_equal": True, "external_closure_before_after_equal": True,
    "source_closed_index_exact": True, "source_closure_sha256": sha(index_path),
    "archive_sha256": sha(archive), "archive_bytes": archive.stat().st_size,
    "manifest_sha256": sha(OUT / "source-manifest.json"),
    "slot_map_sha256": sha(OUT / "per-slot-map.json"),
    "readme_sha256": sha(OUT / "README.md"),
    "git_discoverable_slots": 32, "pending_hub_slots": 30,
    "previously_full_remote_verified_slots": ["narps-neutral-r1-09-j01", "narps-neutral-r1-13-j01"],
    "original_support_archives_copied": 0, "excluded_verified_git_caches": 22,
    "hub_calls": False, "commits": 0, "canonical_refs_or_gitlinks_changed": False,
    "scope": "Verified local publication-metadata package; no remote payload completion claimed."})
print(json.dumps(json.loads((OUT / "package-verification.json").read_text())))
