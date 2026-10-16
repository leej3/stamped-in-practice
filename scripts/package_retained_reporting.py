#!/usr/bin/env python3
"""Package a closed reporting snapshot without changing its original evidence.

No scientific computation, grading, retrieval, or source-workspace writes occur.
The package preserves raw receipts and resolves their original paths through the
reporter's hash-checked source manifest. Only explicitly selected whitespace
link repairs add output references; their file bytes come from a closed capture.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import gzip
import tarfile
from urllib.parse import unquote


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def refs(value):
    if isinstance(value, dict):
        if set(value) == {"path", "sha256"}:
            yield value
        else:
            for child in value.values():
                yield from refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from refs(child)


class Package:
    def __init__(self, snapshot, output, prior=None):
        self.snapshot, self.output = snapshot.resolve(), output.resolve()
        self.output.mkdir(parents=True, exist_ok=False)
        self.aliases, self.sources, self.files, self.captured = {}, {}, {}, {}
        self.prior = prior.resolve() if prior else None
        self.prior_aliases, self.fallbacks = {}, []
        if prior:
            verify_package(prior)
            self.prior_aliases = {row["source_path"]: row for row in read(prior / "source-manifest.json")}
        for row in read(snapshot / "source-manifest.json"):
            original = row["source_path"]
            previous = self.aliases.get(original)
            if previous and previous["sha256"] != row["sha256"]:
                raise ValueError("Conflicting original source identity: " + original)
            self.aliases[original] = row

    def write(self, name, raw):
        path = self.output / name
        if path.resolve().is_relative_to(self.output) is False:
            raise ValueError("Package destination escapes output")
        path.parent.mkdir(parents=True, exist_ok=True)
        digest = sha(raw)
        if path.exists():
            if sha(path.read_bytes()) != digest:
                raise ValueError("Conflicting package path: " + name)
        else:
            # Only package-internal hard links; never link to mutable originals.
            peer = next((self.output / p for p, d in self.files.items() if d == digest), None)
            if peer is not None:
                os.link(peer, path)
            else:
                with path.open("xb") as stream:
                    stream.write(raw)
        self.files[name] = digest
        return {"path": name, "sha256": digest}

    def capture(self, source, name=None, expected=None):
        source = Path(source).absolute()
        # A local annex link is acceptable only when already materialized. Bytes
        # are copied and checked; no command initializes or retrieves content.
        actual = source
        if not source.is_file() and str(source) in self.prior_aliases:
            previous = self.prior_aliases[str(source)]
            actual = self.prior / previous["copy"]["path"]
            expected = expected or previous["sha256"]
            self.fallbacks.append({"original_source_path": str(source),
                "sha256": previous["sha256"], "prior_package_copy": previous["copy"],
                "prior_package_manifest_sha256": sha((self.prior / "package.json").read_bytes())})
        raw = actual.read_bytes()
        digest = sha(raw)
        if expected is not None and digest != expected:
            raise ValueError("Source hash mismatch: " + str(source))
        name = name or f"objects/{digest}{source.suffix}"
        ref = self.write(name, raw)
        self.sources[str(source)] = {"source_path": str(source), "sha256": digest,
                                     "copy": ref, "bytes": len(raw)}
        self.captured[actual] = digest
        return ref

    def reference(self, ref):
        original = Path(ref["path"])
        if original.is_absolute():
            mapping = self.aliases.get(str(original))
            if mapping:
                if mapping["sha256"] != ref["sha256"]:
                    raise ValueError("Snapshot mapping hash mismatch")
                source = self.snapshot / mapping["copy"]["path"]
            else:
                source = original
            copied = self.capture(source, expected=ref["sha256"])
            self.sources[str(original)] = {"source_path": str(original),
                "sha256": ref["sha256"], "copy": copied}
        else:
            # Receipt-relative paths use the index's root, as in the frozen tool.
            if ".." in original.parts:
                raise ValueError("Escaping relative artifact reference")
            copied = self.capture(self.snapshot / original, original.as_posix(),
                                  ref["sha256"])
        return copied

    def finish(self, metadata):
        # Every original source alias must still bind its exact copied bytes.
        for original, row in self.aliases.items():
            name = row["copy"]["path"]
            if self.files.get(name) != row["sha256"] or row["copy"]["sha256"] != row["sha256"]:
                raise ValueError("Original snapshot source mapping no longer matches: " + name)
            self.sources[original] = {"source_path": original,
                "sha256": row["sha256"], "copy": row["copy"]}
        for source, digest in self.captured.items():
            if sha(source.read_bytes()) != digest:
                raise ValueError("Source changed while packaging: " + str(source))
        self.write("source-manifest.json", encoded(sorted(self.sources.values(), key=lambda x: x["source_path"])))
        # Validate all copied bytes after writing, including package-internal links.
        for name, digest in self.files.items():
            if sha((self.output / name).read_bytes()) != digest:
                raise ValueError("Packaged evidence changed: " + name)
        metadata.update(retained_source_fallbacks=self.fallbacks,
                        files=[{"path": p, "sha256": d,
                                "bytes": (self.output / p).stat().st_size}
                               for p, d in sorted(self.files.items())],
                        package_tool_sha256=sha(Path(__file__).read_bytes()),
                        scope="Retained reporting evidence only; no regrading, replay or research; original bytes unchanged.")
        self.write("package.json", encoded(metadata))


def normalize_output_link(raw_target, workspace):
    """Normalize a file target for future intake; bind capture hashes separately."""
    target = unquote(raw_target.strip().strip("<>").strip())
    if "://" in target:
        raise ValueError("Expected a retained workspace file, not a URL")
    path = Path(target)
    relative = path.relative_to(workspace) if path.is_absolute() else path
    if ".." in relative.parts:
        raise ValueError("Output link escapes recorded judge workspace")
    return relative, target


def selected_link(text, workspace, word, suffix):
    found = []
    for number, line in enumerate(text.splitlines(), 1):
        for match in re.finditer(r"\[([^\]]+)\]\((<?[^\n)]+>?)\)", line):
            if word not in match[1].casefold():
                continue
            raw_target = match[2]
            relative, target = normalize_output_link(raw_target, workspace)
            if relative.suffix != suffix:
                continue
            found.append((relative, {"start_line": number, "end_line": number,
                "quote": match[0], "original_target": raw_target,
                "normalized_target": target,
                "normalization": "surrounding whitespace/angle delimiters and URL decoding only"}))
    unique = {str(path) for path, _ in found}
    if len(unique) != 1:
        raise ValueError(f"Expected unique exact {word} link, found {len(unique)}")
    return found[0]


def recover_links(package, index, repairs, capture_index):
    if not repairs:
        return []
    capture_index_ref = package.capture(capture_index, "corrections/original-capture-index.json")
    rows = {row["slot"]: row for row in read(capture_index)["records"]}
    judgments = {j["judgment_id"]: j for run in index["runs"]
                 for j in run.get("judgments", {}).values()}
    receipts = []
    for identity in repairs:
        judgment = judgments[identity]
        prefix = f"evidence/judgments/{identity}"
        native_ref = judgment["native"]["result"]
        native = read(package.output / package.reference(native_ref)["path"])
        if not native.get("finished_at") or native.get("role") != "judge":
            raise ValueError("Only a finalized judgment may receive additive extraction")
        workspace = Path(native["judge_workspace"])
        final_ref = package.capture(package.snapshot / prefix / "native-final.txt", prefix + "/native-final.txt")
        final = (package.output / final_ref["path"]).read_text()
        row = rows[identity]
        manifest_source = Path(row["capture_manifest"]["path"])
        manifest_ref = package.capture(manifest_source, f"corrections/{identity}/retention-manifest.json",
                                       row["capture_manifest"]["sha256"])
        members = {entry["path"]: entry for entry in read(manifest_source)["files"]}
        final_member = members["content/attempt-01/native/final.txt"]
        if final_member["sha256"] != final_ref["sha256"]:
            raise ValueError("Native final differs from closed retention capture")
        before = copy.deepcopy(judgment)
        added, links = {}, {}
        for key, suffix in (("report", ".md"), ("response", ".json")):
            if key in judgment:
                continue
            relative, receipt = selected_link(final, workspace, key, suffix)
            if receipt["original_target"] == receipt["original_target"].strip():
                raise ValueError("Requested repair is not a surrounding-whitespace extraction failure")
            member_name = "content/attempt-01/judgment/" + relative.as_posix()
            member = members[member_name]
            if member["kind"] != "file":
                raise ValueError("Selected retained output is not a regular file")
            ref = package.capture(manifest_source.parent / member_name,
                f"corrections/{identity}/{key}{suffix}", member["sha256"])
            added[key], links[key] = ref, dict(receipt, capture_member=member_name,
                                              output_sha256=ref["sha256"])
            judgment[key] = ref
        if not added:
            raise ValueError("No missing output to recover for " + identity)
        binding_ref = package.reference(before["output_binding"])
        binding = read(package.output / binding_ref["path"])
        binding["outputs"].update(added)
        judgment["output_binding"] = package.write(f"corrections/{identity}/output-binding.json", encoded(binding))
        receipt = {"kind": "additive-whitespace-link-extraction", "judgment_id": identity,
            "original_judgment": before, "native_result": native_ref, "native_final": final_ref,
            "original_output_binding": binding_ref, "retention_index": capture_index_ref,
            "retention_manifest": manifest_ref, "links": links, "added_outputs": added,
            "raw_judgments_modified": False, "categories_or_item_answers_changed": False,
            "purpose": "Recover uniquely linked original output files; all admission/schema checks remain required."}
        receipts.append(package.write(f"corrections/{identity}/receipt.json", encoded(receipt)))
    return receipts


def verify_package(directory):
    manifest = read(directory / "package.json")
    for row in manifest["files"]:
        path = directory / row["path"]
        if not path.resolve().is_relative_to(directory.resolve()) or sha(path.read_bytes()) != row["sha256"]:
            raise ValueError("Package verification failed: " + row["path"])
    return {"verified": True, "files": len(manifest["files"]),
            "index_sha256": sha((directory / "index.json").read_bytes())}


def unpack(archive, expected, output):
    if sha(archive.read_bytes()) != expected:
        raise ValueError("Archive hash mismatch")
    output.mkdir(parents=True, exist_ok=False)
    with tarfile.open(archive, "r:gz") as source:
        for member in source:
            name = Path(member.name)
            if not member.isfile() or name.is_absolute() or ".." in name.parts:
                raise ValueError("Unexpected archive member: " + member.name)
            target = output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as destination:
                destination.write(source.extractfile(member).read())
    return verify_package(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--recover-whitespace-links", action="append", default=[])
    parser.add_argument("--capture-index", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--supplement", type=Path, action="append", default=[])
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--unpack", type=Path)
    parser.add_argument("--archive-sha256")
    parser.add_argument("--reporting-registration", type=Path)
    parser.add_argument("--assessment-pin", type=Path)
    parser.add_argument("--prior-package", type=Path)
    args = parser.parse_args()
    if args.verify:
        print(json.dumps(verify_package(args.verify)))
        return
    if args.unpack:
        if not args.archive_sha256 or not args.output:
            parser.error("--unpack requires --archive-sha256 and --output")
        print(json.dumps(unpack(args.unpack, args.archive_sha256, args.output)))
        return
    if not args.snapshot or not args.output:
        parser.error("--snapshot and --output are required")
    if not args.reporting_registration or not args.assessment_pin:
        parser.error("--reporting-registration and --assessment-pin are required")
    snapshot = read(args.snapshot / "snapshot.json")
    if snapshot["closed_current_series_launchers"] != 32 or snapshot["pending_current_series_slots"] != 0:
        raise ValueError("Only a complete closed 32-slot snapshot may be packaged")
    if args.recover_whitespace_links and not args.capture_index:
        parser.error("--capture-index is required for extraction corrections")
    package = Package(args.snapshot, args.output, args.prior_package)
    if args.prior_package:
        package.capture(args.prior_package / "package.json", "original/prior-package-manifest.json")
    original = package.capture(args.snapshot / "index.json", "original/index.json", snapshot["index"]["sha256"])
    index = read(args.snapshot / "index.json")
    # Keep the entire closed extraction, including its failed reporting outputs.
    # Do not recursively interpret arbitrary path/hash metadata inside judgments:
    # those paths can be relative to the original judge workspace, not this index.
    for path in sorted(args.snapshot.rglob("*")):
        if path.is_file():
            name = path.relative_to(args.snapshot).as_posix()
            if name in ("index.json", "source-manifest.json"):
                name = "original/" + name
            package.capture(path, name)
    for ref in refs(index):
        package.reference(ref)
    supplements = []
    for source in args.supplement:
        if source.is_dir():
            for path in sorted(source.rglob("*")):
                if path.is_file():
                    supplements.append(package.capture(path,
                        "supplements/" + source.name + "/" + path.relative_to(source).as_posix()))
        else:
            supplements.append(package.capture(source, "supplements/" + source.name))
    # Readable frozen extraction/provenance stays separate from the new index.
    for name in ("snapshot.json", "source-manifest.json", "extraction-failures.json",
                 "extraction-decisions.json", "processing-result.json", "supporting-records.json"):
        if (args.snapshot / name).is_file():
            package.capture(args.snapshot / name, "original/" + name)
    for path in sorted((args.snapshot / "registration").glob("*.json")):
        package.capture(path, "registration/" + path.name)
    package.capture(args.reporting_registration, "registration/original-registration.json")
    package.capture(args.assessment_pin, "registration/assessment-version.json")
    # Final texts and source attributions explain selections, even for unchanged
    # judgments. They are evidence, not instructions or replacement grades.
    for path in sorted((args.snapshot / "evidence/judgments").glob("*/*")):
        if path.name in ("native-final.txt", "source-binding-evidence.json", "completion.json", "dispatch.json"):
            package.capture(path, path.relative_to(args.snapshot).as_posix())
    corrections = recover_links(package, index, args.recover_whitespace_links, args.capture_index)
    package.write("index.json", encoded(index))
    package.capture(Path(__file__), "processing-code/package_retained_reporting.py")
    package.finish({"schema_version": 1, "kind": "portable-retained-reporting-inputs",
        "series_id": snapshot["series_id"], "original_index": original,
        "assessment_procedure_sha256": snapshot["assessment_procedure_sha256"],
        "corrections": corrections, "supplements": supplements, "closed_judgments": 32,
        "bulk_payload_scope": "Complete closed extraction, including native judgment event records, retained; scientific images and environments remain in original captures."})
    result = verify_package(args.output)
    if args.archive:
        # Stable gzip/tar metadata; archive members are independent regular bytes.
        with args.archive.open("xb") as raw:
            with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w", dereference=True) as archive:
                    for path in sorted(args.output.rglob("*")):
                        if path.is_file():
                            info = archive.gettarinfo(str(path), path.relative_to(args.output).as_posix())
                            info.uid = info.gid = info.mtime = 0
                            info.uname = info.gname = ""
                            info.mode = 0o644
                            with path.open("rb") as stream:
                                archive.addfile(info, stream)
        result["archive"] = {"path": str(args.archive),
            "sha256": sha(args.archive.read_bytes()), "bytes": args.archive.stat().st_size}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
