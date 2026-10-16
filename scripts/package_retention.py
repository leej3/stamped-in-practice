#!/usr/bin/env python3
"""Copy stopped coordinator evidence with explicit, evidenced cache exclusions."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(2 ** 20), b""):
            h.update(block)
    return h.hexdigest()


def relative(value):
    p = PurePosixPath(value)
    if not value or p.is_absolute() or ".." in p.parts or str(p) == ".":
        raise ValueError("Evidence paths must be nonempty relative paths")
    return str(p)


def excluded(path, exclusions):
    return any(path == p or path.startswith(p + "/") for p in exclusions)


def inventory(root, exclusions):
    records = []
    def fail(error):
        raise error
    for directory, directories, files in os.walk(root, followlinks=False, onerror=fail):
        directories.sort()
        for name in sorted(directories + files):
            path = Path(directory) / name
            rel = path.relative_to(root).as_posix()
            if excluded(rel, exclusions):
                if name in directories:
                    directories.remove(name)
                continue
            mode = path.lstat().st_mode
            record = {"path": rel}
            if stat.S_ISLNK(mode):
                record.update(kind="symlink", target=os.readlink(path))
            elif stat.S_ISDIR(mode):
                record.update(kind="directory")
            elif stat.S_ISREG(mode):
                record.update(kind="file", size=path.stat().st_size,
                              mode=stat.S_IMODE(mode), sha256=digest(path))
            else:
                raise ValueError(f"Unsupported special file: {rel}")
            records.append(record)
    return sorted(records, key=lambda item: item["path"])


def package(plan_path, output):
    plan_path = Path(plan_path).resolve()
    plan = json.loads(plan_path.read_bytes())
    if plan.get("version") != 1:
        raise ValueError("Expected version 1 retention plan")
    source = Path(plan["source"]).resolve(strict=True)
    output = Path(output).resolve()
    if not source.is_dir() or output == source or source in output.parents:
        raise ValueError("Output must be outside the evidence source")
    if output.exists():
        raise ValueError("Output must be a new directory; failed packages are retained")
    exclusions = {}
    for item in plan.get("exclude", []):
        path = relative(item["path"])
        if path in exclusions or not item.get("reason") or not item.get("reconstruct_from"):
            raise ValueError("Each unique exclusion needs a reason and reconstruction record")
        if not (source / path).exists() and not (source / path).is_symlink():
            raise ValueError(f"Excluded path does not exist: {path}")
        if not item.get("evidence"):
            raise ValueError(f"Exclusion requires retained proof: {path}")
        exclusions[path] = item
    for item in exclusions.values():
        for name in item["evidence"]:
            name = relative(name)
            if (excluded(name, exclusions) or not (source / name).is_file() or
                    (source / name).is_symlink()):
                raise ValueError("Exclusion proof must remain in the evidence package")
    stop_path = relative(plan["worker_stop"])
    if excluded(stop_path, exclusions):
        raise ValueError("Original worker stop receipt cannot be excluded")
    if (source / stop_path).is_symlink():
        raise ValueError("Original worker stop receipt must have materialized bytes")
    stop = json.loads((source / stop_path).read_bytes())
    result = plan["scientific_result"]
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", result):
        raise ValueError("Scientific result requires an exact Git object ID")
    if (stop.get("capture_status") != "complete" or stop.get("errors") or
            stop.get("head_commit") != result):
        raise ValueError("Original complete worker stop receipt must match the result")
    before = inventory(source, exclusions)
    included_files = {item["path"] for item in before if item["kind"] == "file"}
    required = {stop_path} | {relative(name) for item in exclusions.values()
                              for name in item["evidence"]}
    if not required <= included_files:
        raise ValueError("Stop receipt and exclusion proofs must be included regular files, without symlink ancestors")
    output.mkdir(parents=True)
    destination = output / "evidence"
    destination.mkdir()
    try:
        for item in before:
            src, dst = source / item["path"], destination / item["path"]
            if item["kind"] == "directory":
                dst.mkdir(parents=True, exist_ok=True)
            elif item["kind"] == "symlink":
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.symlink_to(item["target"])
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
                dst.chmod(item["mode"])
        if inventory(destination, {}) != before:
            raise ValueError("Copied evidence differs from the initial source inventory")
        if inventory(source, exclusions) != before:
            raise ValueError("Evidence source changed during packaging")
        shutil.copyfile(plan_path, output / "package-plan.json")
        shutil.copyfile(Path(__file__), output / "package_retention.py")
        manifest = {
            "version": 1, "status": "verified", "source": str(source),
            "plan_sha256": digest(output / "package-plan.json"),
            "packager_sha256": digest(output / "package_retention.py"),
            "scientific_object": {
                "result_commit": result,
                "original_worker_stop": "evidence/" + stop_path,
                "original_worker_stop_sha256": digest(destination / stop_path),
                "artifact_inventory_field": "worktree",
                "artifact_count": len(stop.get("worktree", [])),
                "scope": "Scientific files, annex keys and duct logs remain in the experiment; the original stop receipt inventories them. This package adds coordinator evidence without altering that result."
            },
            "exclusions": list(exclusions.values()),
            "exclusion_review": "The coordinator selects and justifies reconstructable caches; the packager verifies proof inclusion, not the semantic sufficiency of those proofs.",
            "symlink_scope": "Link text is preserved, including dangling pointers from failed attempts. Link targets are not silently dereferenced or claimed to be available.",
            "files": [{**item, "package_path": "evidence/" + item["path"]}
                      for item in before],
        }
        (output / "package-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        return manifest
    except Exception as error:
        (output / "package-failure.json").write_text(json.dumps({
            "status": "failed", "error": str(error), "source": str(source)
        }, indent=2) + "\n")
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = package(args.plan, args.output)
    print(json.dumps({"status": result["status"], "entries": len(result["files"]),
                      "manifest": str(args.output / "package-manifest.json")}))


if __name__ == "__main__":
    main()
