"""Package an already stopped delivery for coordinator retention, without extraction.

This is a bounded before/after observation, not an atomic snapshot or a worker
publication. Only the frozen original-delivery capture and stop receipt are read;
live workers, Git commands, replay, credentials and publication are out of scope.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tarfile
import types


# The validator in sealed launch source cfeccf4fd14c1f1ef2fe6e27500c3ea139df986e.
VALIDATOR_SHA256 = "4929694dbeccfe546689b29886e2f9da6da7ecb90c50ea7f61ad91f15f72b111"
SCHEMA = "coordinator-delivery-package-v1"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _signature(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns)


def _relative(value):
    path = PurePosixPath(value)
    if (not value or not path.parts or "\x00" in value or path.is_absolute() or
            path.as_posix() != value or any(p in (".", "..") for p in path.parts)):
        raise ValueError("Unsafe package member: " + repr(value))
    return path


def _parent(root, relative):
    parts = _relative(relative).parts
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor, parts[-1]
    except BaseException:
        os.close(descriptor)
        raise


def _file(parent, name):
    before = os.stat(name, dir_fd=parent, follow_symlinks=False)
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    stream = os.fdopen(descriptor, "rb")
    opened = os.fstat(stream.fileno())
    if not stat.S_ISREG(opened.st_mode) or _signature(before) != _signature(opened):
        stream.close()
        raise ValueError("Not a stable regular file: " + name)
    return stream, before


def _stable(parent, name, before, stream):
    if (_signature(before) != _signature(os.fstat(stream.fileno())) or
            _signature(before) != _signature(os.stat(name, dir_fd=parent, follow_symlinks=False))):
        raise ValueError("File changed while packaging: " + name)


def _bytes(path):
    parent, name = _parent(path.parent, path.name)
    try:
        stream, metadata = _file(parent, name)
        with stream:
            content = stream.read()
            _stable(parent, name, metadata, stream)
        return content, stat.S_IMODE(metadata.st_mode)
    finally:
        os.close(parent)


def _digest(stream):
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def inventory_capture(root):
    """Independent literal tree inventory; no ignore rules or link traversal."""
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    rows = []

    def visit(parent, name, relative):
        metadata = os.stat(name, dir_fd=parent, follow_symlinks=False)
        row = {"path": "original-delivery/" + relative,
               "mode": stat.S_IMODE(metadata.st_mode)}
        if stat.S_ISDIR(metadata.st_mode):
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            try:
                if _signature(metadata) != _signature(os.fstat(child)):
                    raise ValueError("Directory changed before inventory")
                rows.append(dict(row, kind="directory"))
                for entry in sorted(os.listdir(child)):
                    visit(child, entry, relative + "/" + entry)
                if _signature(metadata) != _signature(os.fstat(child)):
                    raise ValueError("Directory changed during inventory")
            finally:
                os.close(child)
        elif stat.S_ISLNK(metadata.st_mode):
            target = os.readlink(name, dir_fd=parent)
            rows.append(dict(row, kind="symlink", link_target=target,
                             sha256=_hash(os.fsencode(target))))
        elif stat.S_ISREG(metadata.st_mode):
            stream, before = _file(parent, name)
            with stream:
                digest = _digest(stream)
                _stable(parent, name, before, stream)
            rows.append(dict(row, kind="file", size=metadata.st_size, sha256=digest))
        else:
            raise ValueError("Unsupported retained entry: " + relative)

    try:
        before = os.fstat(descriptor)
        rows.append({"path": "original-delivery", "mode": stat.S_IMODE(before.st_mode),
                     "kind": "directory"})
        for entry in sorted(os.listdir(descriptor)):
            visit(descriptor, entry, entry)
        if _signature(before) != _signature(os.fstat(descriptor)):
            raise ValueError("Capture root changed during inventory")
    finally:
        os.close(descriptor)
    return sorted(rows, key=lambda row: row["path"])


def write_archive(path, capture_root, rows, receipt_bytes):
    """Write explicit members; tarfile never recurses or follows captured links."""
    with path.open("xb") as output, gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode="w|", format=tarfile.PAX_FORMAT) as archive:
            for row in rows:
                item = tarfile.TarInfo(row["path"])
                item.mode = row["mode"]
                # The capture promises bytes/modes/links, not ownership/timestamps.
                item.uid = item.gid = item.mtime = 0
                if row["kind"] == "directory":
                    item.type = tarfile.DIRTYPE
                    archive.addfile(item)
                elif row["kind"] == "symlink":
                    item.type = tarfile.SYMTYPE
                    item.linkname = row["link_target"]
                    archive.addfile(item)
                else:
                    item.size = row["size"]
                    if row["path"] == "worker-end-state.json":
                        archive.addfile(item, io.BytesIO(receipt_bytes))
                        continue
                    relative = row["path"].removeprefix("original-delivery/")
                    parent, name = _parent(capture_root, relative)
                    try:
                        stream, metadata = _file(parent, name)
                        with stream:
                            archive.addfile(item, stream)
                            _stable(parent, name, metadata, stream)
                    finally:
                        os.close(parent)


def verify_archive(path, rows, manifest_sha256, receipt_sha256):
    """Stream each member and compare its exact set, type, mode, bytes or link.

    No extraction and no link dereferencing occur, including for external or
    dangling links. Hard links, duplicate members and unexpected members fail.
    """
    expected = {row["path"]: row for row in rows}
    if len(expected) != len(rows):
        raise ValueError("Duplicate expected archive members")
    observed = set()
    manifest_bytes = receipt_bytes = None
    total_bytes = 0
    with gzip.open(path, "rb") as zipped, tarfile.open(
            fileobj=zipped, mode="r|", ignore_zeros=True) as archive:
        for member in archive:
            name = str(_relative(member.name))
            if name in observed or name not in expected:
                raise ValueError("Duplicate or unexpected archive member: " + name)
            observed.add(name)
            row = expected[name]
            if member.mode != row["mode"]:
                raise ValueError("Archive mode mismatch: " + name)
            if row["kind"] == "directory" and member.isdir():
                continue
            if row["kind"] == "symlink" and member.issym():
                if (member.linkname != row["link_target"] or
                        _hash(os.fsencode(member.linkname)) != row["sha256"]):
                    raise ValueError("Archive link mismatch: " + name)
                continue
            if row["kind"] != "file" or not member.isfile() or member.islnk():
                raise ValueError("Archive kind mismatch: " + name)
            if member.size != row["size"]:
                raise ValueError("Archive size mismatch: " + name)
            stream = archive.extractfile(member)  # Regular bytes only; never extract a path.
            with stream:
                if name in ("original-delivery/manifest.json", "worker-end-state.json"):
                    content = stream.read()
                    digest = _hash(content)
                    if name.endswith("manifest.json"):
                        manifest_bytes = content
                    else:
                        receipt_bytes = content
                else:
                    digest = _digest(stream)
            if digest != row["sha256"]:
                raise ValueError("Archive content mismatch: " + name)
            total_bytes += member.size
    if observed != set(expected):
        raise ValueError("Archive member set differs from capture inventory")
    if manifest_bytes is None or _hash(manifest_bytes) != manifest_sha256:
        raise ValueError("Archive manifest identity mismatch")
    if receipt_bytes is None or _hash(receipt_bytes) != receipt_sha256:
        raise ValueError("Archive stop receipt identity mismatch")
    manifest = json.loads(manifest_bytes)
    manifest_members = {"original-delivery", "original-delivery/manifest.json",
                        "original-delivery/content", "original-delivery/content/external",
                        "worker-end-state.json"}
    manifest_members.update("original-delivery/" + row["path"] for row in manifest["entries"])
    if observed != manifest_members:
        raise ValueError("Archive member set differs from frozen capture manifest")
    return {"verified": True, "member_count": len(observed), "regular_file_bytes": total_bytes,
            "checks": ["exact member set", "entry kinds", "modes", "streamed SHA256",
                       "literal link targets", "manifest identity", "stop receipt identity"],
            "extracted": False}


def _bind_receipt(receipt, manifest, identity):
    if receipt.get("schema_version") != 2 or receipt.get("kind") != "worker-end-state":
        raise ValueError("Expected the original complete-delivery stop receipt")
    comparisons = {
        "head_commit": identity["commit"], "capture_status": identity["capture_status"],
        "captured_at": manifest["captured_at"],
        "capture_finished_at": manifest["capture_finished_at"],
        "errors": manifest["errors"], "omissions": manifest["omissions"],
    }
    for key, value in comparisons.items():
        if receipt.get(key) != value:
            raise ValueError("Stop receipt differs from capture: " + key)
    if receipt.get("capture", {}).get("sha256") != identity["capture"]["sha256"]:
        raise ValueError("Stop receipt capture identity mismatch")


def package_delivery(capture, end_state, expected_capture_sha256, expected_end_state_sha256,
                     output, command=None):
    """Retain success, partial-capture and failure records in a fresh output dir.

    Missing/invalid captures return status=error; an archive interrupted after
    creation is retained and clearly unverified. Existing outputs are untouched.
    No coordinator commit is fabricated; later publication must bind this index.
    """
    capture, end_state, output = map(lambda p: Path(p).absolute(), (capture, end_state, output))
    if output.resolve().is_relative_to(capture.parent.resolve()):
        raise ValueError("Package output must be outside the capture")
    output.mkdir(parents=True, exist_ok=False)
    result = {"schema": SCHEMA, "started_at": _now(), "status": "error",
              "capture_status": None, "worker_head_commit": None,
              "capture_sha256": None, "end_state_sha256": None,
              "coordinator_retention_commit": None, "archive_verified": False,
              "complete_delivery_available": False, "ready_for_annex": False,
              "expected_capture_sha256": expected_capture_sha256,
              "expected_end_state_sha256": expected_end_state_sha256,
              "scope": "Coordinator retention only; no worker credit, publication or replay",
              "consistency": "Bounded before/after validation; not an atomic filesystem snapshot",
              "errors": []}
    _json(output / "command.json", {"argv": command, "capture": str(capture),
                                    "end_state": str(end_state), "output": str(output),
                                    "expected_capture_sha256": expected_capture_sha256,
                                    "expected_end_state_sha256": expected_end_state_sha256})
    stage = "source retention"
    try:
        sources = output / "sources"
        sources.mkdir()
        for name in ("package_delivery.py", "delivery_snapshot.py"):
            source = Path(__file__).with_name(name)
            content, _ = _bytes(source)
            (sources / name).write_bytes(content)
        validator_bytes = (sources / "delivery_snapshot.py").read_bytes()
        if _hash(validator_bytes) != VALIDATOR_SHA256:
            raise ValueError("Frozen capture validator source SHA256 mismatch")
        validator = types.ModuleType("frozen_delivery_validator")
        exec(compile(validator_bytes, str(sources / "delivery_snapshot.py"), "exec"), validator.__dict__)
        stage = "input identity"
        for digest in (expected_capture_sha256, expected_end_state_sha256):
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("Expected SHA256 identities are required")
        receipt_bytes, receipt_mode = _bytes(end_state)
        (output / "worker-end-state.json").write_bytes(receipt_bytes)
        if _hash(receipt_bytes) != expected_end_state_sha256:
            raise ValueError("Original stop receipt SHA256 mismatch")
        result["end_state_sha256"] = expected_end_state_sha256
        receipt = json.loads(receipt_bytes)
        stage = "frozen capture validation"
        identity = validator.validate_capture(capture, expected_capture_sha256)
        manifest_bytes, _ = _bytes(capture)
        manifest = json.loads(manifest_bytes)
        _bind_receipt(receipt, manifest, identity)
        result.update(capture_status=identity["capture_status"], worker_head_commit=identity["commit"],
                      capture_sha256=identity["capture"]["sha256"])
        stage = "capture inventory"
        rows = inventory_capture(capture.parent)
        rows.append({"path": "worker-end-state.json", "kind": "file", "mode": receipt_mode,
                     "size": len(receipt_bytes), "sha256": expected_end_state_sha256})
        _json(output / "archive-inventory.json", rows)
        stage = "archive creation"
        archive_path = output / "delivery.tar.gz"
        write_archive(archive_path, capture.parent, rows, receipt_bytes)
        stage = "independent archive verification"
        verification = verify_archive(archive_path, rows, expected_capture_sha256, expected_end_state_sha256)
        stage = "final source verification"
        validator.validate_capture(capture, expected_capture_sha256)
        if inventory_capture(capture.parent) != rows[:-1]:
            raise ValueError("Capture changed during packaging")
        if _hash(_bytes(end_state)[0]) != expected_end_state_sha256:
            raise ValueError("Stop receipt changed during packaging")
        verification["source_revalidated"] = True
        _json(output / "verification.json", verification)
        result.update(status="packaged", archive_verified=True, ready_for_annex=True,
                      complete_delivery_available=identity["capture_status"] == "complete")
    except (OSError, ValueError, KeyError, TypeError, tarfile.TarError, EOFError) as exc:
        result["errors"].append({"stage": stage, "type": type(exc).__name__, "message": str(exc)})
        _json(output / "verification.json", {"verified": False, "stage": stage,
                                              "errors": result["errors"], "extracted": False})
    result["finished_at"] = _now()
    _json(output / "result.json", result)
    files = []
    for path in sorted(output.rglob("*")):
        if path.is_file():
            with path.open("rb") as stream:
                digest = _digest(stream)
            files.append({"path": str(path.relative_to(output)), "bytes": path.stat().st_size,
                          "sha256": digest})
            path.chmod(0o444)
    _json(output / "index.json", {"schema": SCHEMA, "status": result["status"],
                                   "capture_status": result["capture_status"],
                                   "worker_head_commit": result["worker_head_commit"],
                                   "capture_sha256": result["capture_sha256"],
                                   "end_state_sha256": result["end_state_sha256"],
                                   "expected_capture_sha256": expected_capture_sha256,
                                   "expected_end_state_sha256": expected_end_state_sha256,
                                   "coordinator_retention_commit": None, "files": files,
                                   "publication": "Not published; external ledger must bind this index",
                                   "read_only": "File modes 0444; owner can change them"})
    (output / "index.json").chmod(0o444)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True, help="Stopped original-delivery/manifest.json")
    parser.add_argument("--end-state", type=Path, required=True, help="Original worker-end-state.json")
    parser.add_argument("--expected-capture-sha256", required=True)
    parser.add_argument("--expected-end-state-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True, help="New coordinator retention directory")
    args = parser.parse_args()
    result = package_delivery(**vars(args), command=[sys.executable, *sys.argv])
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "packaged" else 1


if __name__ == "__main__":
    raise SystemExit(main())
