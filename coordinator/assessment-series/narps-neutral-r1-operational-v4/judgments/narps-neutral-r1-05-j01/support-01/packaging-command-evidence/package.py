"""Archive an exact closed Git-stage support set, without remote completion.

Adapted from operational-support-tools-01/package.py. The immutable external
closure index supplies the exact source members and only permitted exclusions.
Its own bytes and every hash-bound method snapshot are archived separately.
No scientific execution, Git command, source mutation, or network operation.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
import shutil
import stat
import sys
import tarfile
import package_delivery as safe

SCHEMA = "operational-native-git-closed-local-bundle-v1"
SERIES = "narps-neutral-r1-operational-v4"
SEAL = "6f25ebbec5310442e8fd3fd20bd20682ecb5653b350362119af3e825a2668084"


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with path.open("rb") as stream:
        return safe._digest(stream)


def save(path, value):
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def now():
    return datetime.now(timezone.utc).isoformat()


def inventory(root, excluded):
    """Inventory literal names without following links or applying ignore rules."""
    rows = []
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)

    def visit(parent, name, relative):
        if relative in excluded:
            return
        safe._relative(relative)
        before = os.stat(name, dir_fd=parent, follow_symlinks=False)
        row = {"path": relative, "mode": stat.S_IMODE(before.st_mode)}
        if stat.S_ISDIR(before.st_mode):
            row["kind"] = "directory"
            rows.append(row)
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=parent)
            try:
                require(safe._signature(before) == safe._signature(os.fstat(child)),
                        "Directory changed before inventory: " + relative)
                for entry in sorted(os.listdir(child)):
                    visit(child, entry, relative + "/" + entry)
                require(safe._signature(before) == safe._signature(os.fstat(child)),
                        "Directory changed during inventory: " + relative)
                require(safe._signature(before) == safe._signature(os.stat(
                    name, dir_fd=parent, follow_symlinks=False)),
                    "Directory replaced during inventory: " + relative)
            finally:
                os.close(child)
        elif stat.S_ISLNK(before.st_mode):
            target = os.readlink(name, dir_fd=parent)
            row.update(kind="symlink", target=target,
                       sha256=hashlib.sha256(os.fsencode(target)).hexdigest())
            require(safe._signature(before) == safe._signature(os.stat(
                name, dir_fd=parent, follow_symlinks=False)),
                "Link changed during inventory: " + relative)
            rows.append(row)
        elif stat.S_ISREG(before.st_mode):
            stream, opened = safe._file(parent, name)
            require(safe._signature(before) == safe._signature(opened),
                    "File changed before inventory: " + relative)
            with stream:
                digest = safe._digest(stream)
                safe._stable(parent, name, opened, stream)
            row.update(kind="file", bytes=before.st_size, sha256=digest)
            rows.append(row)
        else:
            raise ValueError("Unsupported retained entry: " + relative)

    try:
        initial = os.fstat(descriptor)
        for entry in sorted(os.listdir(descriptor)):
            visit(descriptor, entry, entry)
        require(safe._signature(initial) == safe._signature(os.fstat(descriptor)),
                "Root changed during inventory")
    finally:
        os.close(descriptor)
    return sorted(rows, key=lambda row: row["path"])


def verify(archive, rows):
    expected = {row["path"]: row for row in rows}
    require(len(expected) == len(rows), "Duplicate expected archive member")
    seen = set()
    count = 0
    with gzip.open(archive, "rb") as compressed, tarfile.open(
            fileobj=compressed, mode="r|", ignore_zeros=True) as stream:
        for member in stream:
            safe._relative(member.name)
            require(member.name not in seen and member.name in expected,
                    "Unexpected or duplicate archive member: " + member.name)
            seen.add(member.name)
            row = expected[member.name]
            require(member.mode == row["mode"], "Mode differs: " + member.name)
            if row["kind"] == "directory":
                require(member.isdir() and not member.size,
                        "Directory differs: " + member.name)
            elif row["kind"] == "symlink":
                require(member.issym() and member.linkname == row["target"]
                        and not member.size, "Link differs: " + member.name)
            else:
                require(member.isfile() and not member.islnk()
                        and member.size == row["bytes"],
                        "File metadata differs: " + member.name)
                with stream.extractfile(member) as payload:
                    require(safe._digest(payload) == row["sha256"],
                            "File hash differs: " + member.name)
                count += member.size
        # Read to gzip EOF so its CRC/size trailer is checked even if tar parsing
        # has finished. Nothing is extracted or executed.
        require(not compressed.read(1), "Unexpected unconsumed gzip content")
    require(seen == set(expected), "Missing archive members")
    return {"verified": True, "members": len(seen),
            "regular_file_bytes": count, "extracted": False,
            "checks": ["exact member set", "kinds", "modes", "streamed SHA256",
                       "literal links", "gzip integrity"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("closure_index", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected-index-sha256", required=True)
    parser.add_argument("--expected-proof-commit", required=True)
    args = parser.parse_args()
    src, idx, out = args.source, args.closure_index, args.output
    out.mkdir(parents=True, exist_ok=False)
    save(out / "command.json", {
        "started_at": now(), "argv": sys.argv, "cwd": os.getcwd(),
        "python": sys.executable, "python_version": sys.version,
        "package_method_sha256": sha(Path(__file__)),
        "safe_file_method_sha256": sha(Path(safe.__file__)),
        "network_operations": False, "source_mutations": False,
        "remote_completion": False})
    raw, index_mode = safe._bytes(idx)
    require(hashlib.sha256(raw).hexdigest() == args.expected_index_sha256,
            "External closure index differs from final reconciliation")
    index = json.loads(raw)
    require(index["schema"] == SCHEMA and index["source_closed_for_coordinator"],
            "Expected closed Git-stage local bundle")
    require(index["series_id"] == SERIES
            and index["assessment_procedure_sha256"] == SEAL,
            "Series or procedure differs")
    require(index["slot"] == src.name == idx.parent.name,
            "Source, closure and slot names differ")
    require(index["fully_verified_hub_publication"] is False
            and index["hub_transfers_held"] is True,
            "Expected explicit pending Hub stage")
    require(index["git_proof_commit"] == args.expected_proof_commit,
            "Proof commit differs from final reconciliation")
    excluded = [Path(row["path"]).relative_to(src).as_posix()
                for row in index["excluded_caches"]]
    require(len(set(excluded)) == len(excluded), "Duplicate exclusion")
    for relative in excluded:
        safe._relative(relative)
        require(relative.startswith("native-publication-01/"),
                "Excluded entry is not a publication cache")
    before = inventory(src, excluded)
    expected = sorted(index["closed_files"], key=lambda row: row["path"])
    require(before == expected,
            "Closed source changed or has unindexed entries")
    closure_before = inventory(idx.parent, [])
    expected_external_files = {
        idx.name: {"bytes": len(raw), "sha256": args.expected_index_sha256}}
    for row in index["method_snapshots"]:
        relative = Path(row["path"]).relative_to(idx.parent).as_posix()
        safe._relative(relative)
        require(relative not in expected_external_files,
                "Duplicate external closure member")
        expected_external_files[relative] = row
    observed_files = {row["path"]: row for row in closure_before
                      if row["kind"] != "directory"}
    require(set(observed_files) == set(expected_external_files),
            "External closure has missing or unindexed files")
    expected_dirs = {str(parent) for relative in expected_external_files
                     for parent in Path(relative).parents if str(parent) != "."}
    require({row["path"] for row in closure_before if row["kind"] == "directory"}
            == expected_dirs, "External closure has unindexed directories")
    for relative, record in expected_external_files.items():
        observed = observed_files[relative]
        require(observed["kind"] == "file"
                and observed["bytes"] == record["bytes"]
                and observed["sha256"] == record["sha256"],
                "External closure file differs: " + relative)
    require(observed_files[idx.name]["mode"] == index_mode,
            "External index mode changed")
    roots = {"evidence": src, "closure": idx.parent}
    rows = [{**row, "path": prefix + "/" + row["path"]}
            for prefix, entries in (("evidence", before),
                                    ("closure", closure_before)) for row in entries]
    save(out / "member-manifest.json", {
        "schema": "operational-support-local-package-v2",
        "roots": {key: str(value) for key, value in roots.items()},
        "source_closed_index_sha256": args.expected_index_sha256,
        "excluded_verified_caches": index["excluded_caches"], "entries": rows})
    archive = out / "support.tar.gz"
    with archive.open("xb") as file, gzip.GzipFile(
            fileobj=file, mode="wb", filename="", mtime=0, compresslevel=6
            ) as compressed, tarfile.open(fileobj=compressed, mode="w|",
                                        format=tarfile.PAX_FORMAT) as stream:
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
                descriptor, name = safe._parent(roots[prefix], relative)
                try:
                    payload, metadata = safe._file(descriptor, name)
                    with payload:
                        stream.addfile(member, payload)
                        safe._stable(descriptor, name, metadata, payload)
                finally:
                    os.close(descriptor)
    verification = verify(archive, rows)
    require(before == inventory(src, excluded), "Source changed after archive")
    require(closure_before == inventory(idx.parent, []),
            "External closure changed after archive")
    require(safe._bytes(idx) == (raw, index_mode), "External index changed")
    shutil.copy2(idx, out / "git-closure-index.json")
    require(sha(out / "git-closure-index.json") == args.expected_index_sha256,
            "Copied closure index differs")
    for path in [Path(__file__), Path(safe.__file__)]:
        shutil.copy2(path, out / path.name)
    result = {
        **verification, "completed_at": now(),
        "source_before_after_equal": True, "source_closed_index_exact": True,
        "external_closure_before_after_equal": True,
        "external_index_and_methods_exact": True,
        "slot": index["slot"], "series_id": index["series_id"],
        "native_publication_base": index["git_proof_commit"],
        "source_members": len(before), "external_closure_members": len(closure_before),
        "source_regular_file_bytes": sum(row.get("bytes", 0) for row in before),
        "archive_sha256": sha(archive), "archive_bytes": archive.stat().st_size,
        "manifest_sha256": sha(out / "member-manifest.json"),
        "closed_index_sha256": args.expected_index_sha256,
        "excluded_caches": index["excluded_caches"],
        "remote_completion": False, "hub_transfers_held": True,
        "omissions": "Only exact publisher/recipient caches listed in the immutable "
                     "closed source index; every closed file and external method retained.",
        "scope": "Verified local archive; no Hub upload or independent remote "
                 "retrieval. This does not alter the pending publication stage."}
    save(out / "package-verification.json", result)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
