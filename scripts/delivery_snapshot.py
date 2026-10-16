"""Opt-in, read-only preservation of the actual stopped delivery.

This bounded observation is not an atomic filesystem snapshot. Every retained
entry is verified; changes, unsupported files, and explicit credential omissions
make the receipt partial. Git ignore rules never select or exclude content.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat


SCHEMA = "original-delivery-v1"
OPAQUE_GIT_POLICY = "original-dependencies-retained-without-reinterpretation"
# These are credential/personal stores, not scientific caches. Do not exclude
# .pixi, .venv, .cache, lockfiles, or other reconstructable environment bytes.
CREDENTIAL_NAMES = frozenset({
    ".ssh", ".aws", ".azure", ".gnupg", ".git-credentials", ".netrc",
    "_netrc", ".npmrc", ".pypirc", ".dockercfg", ".claude.json",
})
CREDENTIAL_PARTS = (
    (".codex", "auth.json"), (".codex", "auth"),
    (".claude", ".credentials.json"), (".config", "gh"),
    (".config", "gcloud"), (".config", "agent-vault"),
    (".config", "skills-workshop", "credentials"),
    (".local", "state", "agent-vault"), (".local", "share", "agent-vault"),
    (".local", "share", "keyrings"), (".docker", "config.json"),
    ("Library", "Keychains"), ("Library", "Application Support", "com.apple.Passwords"),
)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _signature(metadata):
    return (metadata.st_dev, metadata.st_ino, metadata.st_mode, metadata.st_size,
            metadata.st_mtime_ns, metadata.st_ctime_ns)


def _credential_path(path):
    parts = Path(path).parts
    if any(part in CREDENTIAL_NAMES for part in parts):
        return True
    return any(tuple(parts[i:i + len(pattern)]) == pattern
               for pattern in CREDENTIAL_PARTS for i in range(len(parts)))


def _relative(value):
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ValueError("Invalid capture-relative path")
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or value != path.as_posix() or any(p in (".", "..") for p in path.parts):
        raise ValueError("Unsafe capture-relative path")
    return path


def _open_parent(root, relative):
    """Open each directory without following a symlink, including during races."""
    parts = _relative(relative).parts
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            next_descriptor = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                      dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor, parts[-1]
    except BaseException:
        os.close(descriptor)
        raise


def _read_file(parent, name, before, destination=None):
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    digest = hashlib.sha256()
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or _signature(before) != _signature(opened):
            raise ValueError("File changed before reading")
        output = destination.open("xb") if destination is not None else None
        try:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                if output is not None:
                    output.write(chunk)
        finally:
            if output is not None:
                output.close()
        after = os.fstat(stream.fileno())
    current = os.stat(name, dir_fd=parent, follow_symlinks=False)
    if _signature(opened) != _signature(after) or _signature(after) != _signature(current):
        raise ValueError("File changed during capture")
    return digest.hexdigest()


def _retained_bytes(bundle, relative):
    parent, name = _open_parent(bundle, relative)
    try:
        before = os.stat(name, dir_fd=parent, follow_symlinks=False)
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or _signature(before) != _signature(opened):
                raise ValueError("Metadata file changed before reading")
            content = stream.read()
            after = os.fstat(stream.fileno())
        if (_signature(opened) != _signature(after) or
                _signature(after) != _signature(os.stat(name, dir_fd=parent, follow_symlinks=False))):
            raise ValueError("Metadata file changed while reading")
        return content
    finally:
        os.close(parent)


def _safe_seed(receipt):
    """Only condition-free content identities cross the coordinator boundary."""
    receipt = receipt or {}
    result = {}
    for key in ("seed_commit", "study_input_tree", "common_prompt_sha256", "common_resources_sha256"):
        value = receipt.get(key)
        if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
            result[key] = value
    for key in ("inputs", "supplied_files"):
        selected = []
        for row in receipt.get(key, []):
            if not isinstance(row, dict):
                continue
            try:
                path = str(_relative(row.get("path")))
            except ValueError:
                continue
            clean = {"path": path}
            for name in ("sha256", "git_blob"):
                value = row.get(name)
                if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
                    clean[name] = value
            for name in ("bytes", "mode", "source_mode"):
                value = row.get(name)
                if isinstance(value, int) or (isinstance(value, str) and re.fullmatch(r"[0-7]{3,6}", value)):
                    clean[name] = value
            value = row.get("annex_key")
            if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+_=:%-]*", value):
                clean["annex_key"] = value
            selected.append(clean)
        if selected:
            result[key] = selected
    return result


def _local_head(bundle, entries, dependencies=()):
    """Resolve HEAD from retained local metadata only; never discover parent Git."""
    rows = {row["path"]: row for row in entries}
    mappings = {item["path"]: item.get("retained_targets", []) for item in dependencies}
    root = "content/workspace/.git"
    if rows.get(root, {}).get("kind") != "directory":
        targets = mappings.get(root, [])
        if len(targets) != 1 or not targets[0]:
            return None
        root = targets[0]
    common = mappings.get(root + "/commondir", [])
    prefixes = [root + "/"] + ([common[0] + "/"] if len(common) == 1 and common[0] else [])
    def read(name):
        for prefix in prefixes:
            row = rows.get(prefix + name)
            if row and row["kind"] == "file":
                return _retained_bytes(bundle, prefix + name).decode().strip()
        return None
    value = read("HEAD")
    visited = set()
    while value and value.startswith("ref: "):
        reference = value[5:]
        if reference in visited or not reference.startswith("refs/"):
            return None
        _relative(reference)
        visited.add(reference)
        value = read(reference)
        if value is None:
            for line in (read("packed-refs") or "").splitlines():
                if line and not line.startswith(("#", "^")):
                    fields = line.split(" ", 1)
                    if len(fields) == 2 and fields[1] == reference:
                        value = fields[0]
                        break
    return value if value and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value) else None


def save_delivery(workspace, output, worker, seed_receipt=None, declared_artifacts=None,
                  *, inspect_git_dependencies=True):
    """Retain workspace and explicitly declared external artifacts outside it.

    A declaration is {path: absolute path, declaration: JSON provenance} (the
    spelling provenance is also accepted). Symlinks are retained, never followed.
    Known credential roots are excluded with a reason. Partial bundles remain
    inspectable and verifiable; consumers decide whether partial is admissible.
    For an already captured container, inspect_git_dependencies=False preserves
    its bytes without reinterpreting relocated pointers. Its original manifest
    remains the authority for dependencies; this does not permit traversal.
    """
    root = Path(workspace).absolute()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Workspace must be a real directory")
    root = root.resolve()
    home = Path.home().resolve()
    if root == home or root in home.parents:
        raise ValueError("A personal home or filesystem root is not a workspace")
    destination = Path(output).resolve()
    if destination == root or destination.is_relative_to(root):
        raise ValueError("Delivery capture must be outside the workspace")
    declarations = []
    for declaration in declared_artifacts or []:
        if not isinstance(declaration, dict) or not declaration.get("path"):
            raise ValueError("External artifacts require a path and provenance declaration")
        provenance = declaration.get("declaration", declaration.get("provenance"))
        if provenance is None:
            raise ValueError("External artifacts require a provenance declaration")
        _json_bytes(provenance)
        source = Path(declaration["path"])
        if not source.is_absolute():
            raise ValueError("Declared artifact paths must be absolute")
        # Resolve only the parent; a declared link itself is preserved as a link.
        source = source.parent.resolve() / source.name
        if source == home or source in home.parents:
            raise ValueError("Broad personal or filesystem roots cannot be artifacts")
        if destination == source or destination.is_relative_to(source):
            raise ValueError("Delivery capture must be outside every declared artifact")
        declarations.append((source, provenance))
    destination.mkdir(parents=True, exist_ok=True)
    bundle = destination / "original-delivery"
    bundle.mkdir()
    content = bundle / "content"
    content.mkdir()
    (content / "external").mkdir()
    entries, omissions, errors, checks = [], [], [], []
    source_roots = {}
    manifest = {"schema": SCHEMA, "kind": "original-delivery", "captured_at": _now(),
                "workspace": "content/workspace", "entries": entries,
                "declared_artifacts": [], "omissions": omissions, "errors": errors,
                "policy": {"ignored_files": "included", "environment_and_cache_bytes": "included",
                           "symlinks": "preserved without following", "credentials": "excluded with reason"}}
    if not inspect_git_dependencies:
        manifest["kind"] = "retained-container"
        manifest["policy"]["git_dependencies"] = OPAQUE_GIT_POLICY

    def fail(path, operation, error):
        errors.append({"path": path, "operation": operation, "error": str(error)})

    def capture(parent, name, source, relative):
        target = bundle / relative
        try:
            before = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if _credential_path(source):
                omissions.append({"path": relative, "kind": "exclusion",
                                  "reason": "Known credential or native authentication store"})
                return
            row = {"path": relative, "mode": stat.S_IMODE(before.st_mode)}
            if stat.S_ISDIR(before.st_mode):
                descriptor = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                try:
                    if _signature(before) != _signature(os.fstat(descriptor)):
                        raise ValueError("Directory changed before reading")
                    target.mkdir()
                    entries.append(dict(row, kind="directory"))
                    for child in sorted(os.listdir(descriptor)):
                        capture(descriptor, child, source / child, relative + "/" + child)
                    if _signature(before) != _signature(os.fstat(descriptor)):
                        fail(relative, "consistency", "Directory changed during capture")
                    os.chmod(target, row["mode"])
                finally:
                    os.close(descriptor)
            elif stat.S_ISREG(before.st_mode):
                try:
                    digest = _read_file(parent, name, before, target)
                except (OSError, ValueError):
                    target.unlink(missing_ok=True)
                    raise
                os.chmod(target, row["mode"])
                entries.append(dict(row, kind="file", size=before.st_size, sha256=digest))
            elif stat.S_ISLNK(before.st_mode):
                link = os.readlink(name, dir_fd=parent)
                os.symlink(link, target)
                if hasattr(os, "lchmod"):
                    os.lchmod(target, row["mode"])
                entries.append(dict(row, kind="symlink", link_target=link, sha256=_hash(os.fsencode(link))))
            else:
                omissions.append({"path": relative, "kind": "unsupported",
                                  "reason": "Special file cannot be copied safely", "mode": before.st_mode})
                fail(relative, "capture", "Unsupported special file")
                return
            checks.append((source, relative, _signature(before)))
        except (OSError, ValueError) as exc:
            fail(relative, "capture", exc)

    def source_capture(source, relative):
        source_roots[relative] = source
        try:
            parent = os.open(source.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                capture(parent, source.name, source, relative)
            finally:
                os.close(parent)
        except OSError as exc:
            fail(relative, "capture", exc)

    source_capture(root, "content/workspace")
    for number, (source, provenance) in enumerate(declarations):
        relative = f"content/external/{number:04d}"
        manifest["declared_artifacts"].append({"source": str(source), "path": relative,
                                               "declaration": provenance})
        source_capture(source, relative)
    # Recheck every original path without following a replaced parent directory.
    for source, relative, signature in checks:
        try:
            anchor = next(original for prefix, original in source_roots.items()
                          if relative == prefix or relative.startswith(prefix + "/"))
            local = str(source.relative_to(anchor))
            if local == ".":
                anchor, local = source.parent, source.name
            descriptor, name = _open_parent(anchor, local)
            try:
                current = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                if signature != _signature(current):
                    raise ValueError("Source changed during capture")
            finally:
                os.close(descriptor)
        except (OSError, ValueError) as exc:
            fail(relative, "consistency", exc)
    # Pointers outside the retained tree must not pull in other repositories.
    # An approved declaration may independently retain such a dependency.
    retained_sources = ({relative: source for source, relative, _ in checks}
                        if inspect_git_dependencies else {})
    retained_kinds = {row["path"]: row["kind"] for row in entries}
    git_roots = {source for path, source in retained_sources.items()
                 if PurePosixPath(path).name == ".git" and retained_kinds.get(path) == "directory"}
    for path, source in retained_sources.items():
        if PurePosixPath(path).name == ".git" and retained_kinds.get(path) == "symlink":
            git_roots.add(Path(os.path.abspath(source.parent / os.readlink(bundle / path))))
        if PurePosixPath(path).name == ".git" and retained_kinds.get(path) == "file":
            try:
                value = _retained_bytes(bundle, path).decode().strip()
                if value.startswith("gitdir: "):
                    git_roots.add(Path(os.path.abspath(source.parent / value[8:])))
            except (OSError, UnicodeError, ValueError):
                pass  # The dependency inventory below records the failed pointer.
    # A declared worktree admin directory can refer to a declared common dir.
    # Discover only metadata roots named by retained pointers; never traverse them.
    while True:
        added = set()
        for path, source in retained_sources.items():
            if source.name == "commondir" and source.parent in git_roots and retained_kinds.get(path) == "file":
                try:
                    value = _retained_bytes(bundle, path).decode().strip()
                    added.add(Path(os.path.abspath(source.parent / value)))
                except (OSError, UnicodeError, ValueError):
                    pass
        if added <= git_roots:
            break
        git_roots.update(added)
    manifest["git_dependencies"] = []
    for row in (entries if inspect_git_dependencies else ()):
        path = row["path"]
        parts = PurePosixPath(path).parts
        source = retained_sources.get(path)
        metadata_pointer = source is not None and any(
            source.is_relative_to(root) and str(source.relative_to(root)) in
            ("commondir", "objects/info/alternates", "objects/info/http-alternates") for root in git_roots)
        dependency = ((parts[-1] == ".git" and row["kind"] != "directory") or
                      (metadata_pointer and row["kind"] != "directory"))
        if dependency:
            targets = []
            original = retained_sources.get(path)
            if original is not None and row["kind"] == "file":
                try:
                    values = _retained_bytes(bundle, path).decode().strip().splitlines()
                    if parts[-1] == ".git":
                        values = [values[0][8:]] if values and values[0].startswith("gitdir: ") else []
                    base = original.parent.parent if parts[-1] in ("alternates", "http-alternates") else original.parent
                    targets = [Path(os.path.abspath(base / value)) for value in values if value]
                except (OSError, UnicodeError, ValueError) as exc:
                    fail(path, "Git dependency", exc)
            if original is not None and row["kind"] == "symlink":
                targets = [Path(os.path.abspath(original.parent / os.readlink(bundle / path)))]
            mapping = {str(source): relative for relative, source in retained_sources.items()}
            retained_targets = [mapping.get(str(target)) for target in targets]
            covered = bool(targets) and all(target and retained_kinds.get(target) == "directory"
                                            for target in retained_targets)
            manifest["git_dependencies"].append({"path": path, "covered_by_retained_sources": covered,
                                                  "retained_targets": retained_targets})
            if not covered:
                omissions.append({"path": path, "kind": "git-dependency",
                                  "reason": "Git dependency pointer retained; target not automatically traversed"})
    try:
        head = (_local_head(bundle, entries, manifest["git_dependencies"])
                if inspect_git_dependencies else None)
    except (OSError, ValueError, UnicodeError) as exc:
        head = None
        fail("content/workspace/.git", "HEAD", exc)
    git_prefix = "content/workspace/.git"
    git_rows = [row for row in entries if row["path"] == git_prefix or row["path"].startswith(git_prefix + "/")]
    manifest["git_metadata"] = {
        "root": git_prefix if git_rows else None,
        "root_kind": retained_kinds.get(git_prefix, "absent"),
        "coverage": "Exact workspace-resident Git bytes, modes and links; explicit dependencies separately declared",
        "retained_entries": len(git_rows),
        "local_metadata_complete": not any(row["path"] == git_prefix or row["path"].startswith(git_prefix + "/")
                                           for row in errors + omissions),
        "index": next((row for row in git_rows if row["path"] == git_prefix + "/index"), None),
    }
    manifest.update(head_commit=head, capture_finished_at=_now(),
                    capture_status="partial" if errors or omissions else "complete")
    manifest_path = bundle / "manifest.json"
    manifest_bytes = _json_bytes(manifest)
    manifest_path.write_bytes(manifest_bytes)
    capture_identity = {"uri": str(manifest_path), "sha256": _hash(manifest_bytes)}
    receipt = {"schema_version": 2, "kind": "worker-end-state", "captured_at": manifest["captured_at"],
               "capture_finished_at": manifest["capture_finished_at"],
               "worker": {key: value for key, value in (worker or {}).items()
                          if key in {"pid", "returncode", "timed_out", "stop_reason", "stopped_at"}},
               "head_commit": head, "capture_status": manifest["capture_status"],
               "capture": capture_identity, "errors": errors, "omissions": omissions,
               "seed_identities": _safe_seed(seed_receipt)}
    receipt_bytes = _json_bytes(receipt)
    with (destination / "worker-end-state.json").open("xb") as stream:
        stream.write(receipt_bytes)
    return {"path": "worker-end-state.json", "sha256": _hash(receipt_bytes),
            "capture_status": receipt["capture_status"], "head_commit": head, "capture": capture_identity}


def _validate_tree(bundle, manifest):
    expected = {"manifest.json", "content", "content/external"}
    rows = {}
    if not isinstance(manifest.get("entries"), list):
        raise ValueError("Invalid capture entry list")
    for row in manifest["entries"]:
        if not isinstance(row, dict) or not isinstance(row.get("mode"), int):
            raise ValueError("Invalid capture entry")
        relative = str(_relative(row["path"]))
        if not (relative == "content/workspace" or relative.startswith("content/workspace/") or
                relative.startswith("content/external/")) or relative in rows:
            raise ValueError("Invalid or duplicate capture entry")
        rows[relative] = row
        expected.add(relative)
    actual = set()
    def inventory(parent, prefix=""):
        for name in os.listdir(parent):
            relative = prefix + name
            actual.add(relative)
            metadata = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if stat.S_ISDIR(metadata.st_mode):
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                try:
                    inventory(child, relative + "/")
                finally:
                    os.close(child)
    descriptor = os.open(bundle, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        inventory(descriptor)
    finally:
        os.close(descriptor)
    if actual != expected:
        raise ValueError("Capture file list differs (missing or unexpected entries)")
    for relative in ("content", "content/external"):
        parent, name = _open_parent(bundle, relative)
        try:
            if not stat.S_ISDIR(os.stat(name, dir_fd=parent, follow_symlinks=False).st_mode):
                raise ValueError("Unsafe capture container")
        finally:
            os.close(parent)
    for relative, row in rows.items():
        parent, name = _open_parent(bundle, relative)
        try:
            metadata = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if stat.S_IMODE(metadata.st_mode) != row["mode"]:
                raise ValueError("Capture mode mismatch: " + relative)
            kind = row["kind"]
            if kind == "file" and stat.S_ISREG(metadata.st_mode):
                if metadata.st_size != row["size"] or _read_file(parent, name, metadata) != row["sha256"]:
                    raise ValueError("Capture content mismatch: " + relative)
            elif kind == "directory" and stat.S_ISDIR(metadata.st_mode):
                continue
            elif kind == "symlink" and stat.S_ISLNK(metadata.st_mode):
                link = os.readlink(name, dir_fd=parent)
                if link != row["link_target"] or _hash(os.fsencode(link)) != row["sha256"]:
                    raise ValueError("Capture link mismatch: " + relative)
            else:
                raise ValueError("Capture kind mismatch: " + relative)
        finally:
            os.close(parent)


def validate_capture(manifest_path, expected_sha256=None):
    """Validate bytes, modes, links and the exact file list, even for partial captures."""
    path = Path(manifest_path).absolute()
    if path.name != "manifest.json" or path.is_symlink():
        raise ValueError("Expected a regular retained manifest.json")
    content = _retained_bytes(path.parent, path.name)
    digest = _hash(content)
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("Capture manifest SHA256 mismatch")
    manifest = json.loads(content)
    if manifest.get("schema") != SCHEMA or manifest.get("workspace") != "content/workspace":
        raise ValueError("Unsupported delivery capture")
    if manifest.get("capture_status") not in ("complete", "partial"):
        raise ValueError("Invalid capture status")
    if manifest["capture_status"] == "complete" and (manifest.get("errors") or manifest.get("omissions")):
        raise ValueError("Complete capture has undisclosed omissions or errors")
    _validate_tree(path.parent, manifest)
    if _local_head(path.parent, manifest["entries"], manifest.get("git_dependencies", [])) != manifest.get("head_commit"):
        raise ValueError("Retained original Git HEAD mismatch")
    if _hash(_retained_bytes(path.parent, path.name)) != digest:
        raise ValueError("Capture manifest changed during validation")
    return {"commit": manifest.get("head_commit"), "captured_at": manifest["captured_at"],
            "capture_status": manifest["capture_status"],
            "capture": {"uri": str(path), "sha256": digest}}


def capture_reference_limits(manifest_path):
    """Identify retained pointers that must not be followed into live source state."""
    path = Path(manifest_path).resolve()
    manifest = json.loads(path.read_bytes())
    limits = [{"path": row["path"], "reason": "original Git dependency pointer; inspect retained bytes only"}
              for row in manifest.get("git_dependencies", [])]
    for row in manifest["entries"]:
        if row["kind"] != "symlink":
            continue
        link = path.parent / row["path"]
        try:
            outside = not link.resolve().is_relative_to(path.parent)
        except (OSError, RuntimeError):
            outside = True
        if outside or Path(os.readlink(link)).is_absolute():
            limits.append({"path": row["path"], "reason": "original absolute/external link; do not follow"})
    return limits


def materialize_capture(manifest_path, destination):
    """Copy a verified retained bundle into a new directory without Git writes."""
    identity = validate_capture(manifest_path)
    source = Path(manifest_path).absolute()
    target = Path(destination).absolute()
    if target.exists() or target.is_symlink():
        raise ValueError("Materialization requires a new destination")
    if target.resolve().is_relative_to(source.parent.resolve()):
        raise ValueError("Materialization must be outside the retained bundle")
    manifest_bytes = _retained_bytes(source.parent, source.name)
    if _hash(manifest_bytes) != identity["capture"]["sha256"]:
        raise ValueError("Capture manifest changed before materialization")
    manifest = json.loads(manifest_bytes)
    target.mkdir(parents=True)
    (target / "content").mkdir()
    (target / "content/external").mkdir()
    directories = []
    for row in sorted(manifest["entries"], key=lambda item: (len(PurePosixPath(item["path"]).parts), item["path"])):
        relative = str(_relative(row["path"]))
        result = target / relative
        if row["kind"] == "directory":
            result.mkdir()
            directories.append((result, row["mode"]))
        elif row["kind"] == "symlink":
            os.symlink(row["link_target"], result)
            if hasattr(os, "lchmod"):
                os.lchmod(result, row["mode"])
        else:
            parent, name = _open_parent(source.parent, relative)
            try:
                metadata = os.stat(name, dir_fd=parent, follow_symlinks=False)
                digest = _read_file(parent, name, metadata, result)
                if digest != row["sha256"]:
                    raise ValueError("Capture changed while materializing")
            finally:
                os.close(parent)
            os.chmod(result, row["mode"])
    for directory, mode in reversed(directories):
        os.chmod(directory, mode)
    copied_manifest = target / "manifest.json"
    copied_manifest.write_bytes(manifest_bytes)
    validate_capture(source, identity["capture"]["sha256"])
    copied_identity = validate_capture(copied_manifest, identity["capture"]["sha256"])
    return {"manifest": str(copied_manifest), "target": str(target / manifest["workspace"]),
            "identity": copied_identity}


OPERATIONAL_METADATA = frozenset("content/workspace/.git/annex/keysdb/" + name
                                 for name in ("db", "db-shm", "db-wal"))


def capture_container_modes(manifest_path):
    """Bind materialization wrappers outside the original manifest entry rows."""
    bundle = Path(manifest_path).absolute().parent
    modes = {}
    for name in (".", "content", "content/external", "manifest.json"):
        metadata = (bundle / name).lstat()
        expected = stat.S_ISREG if name == "manifest.json" else stat.S_ISDIR
        if not expected(metadata.st_mode):
            raise ValueError("Unsafe capture wrapper: " + name)
        modes[name] = stat.S_IMODE(metadata.st_mode)
    return modes


def operational_delta(original_bytes, retained, container_modes):
    """Pure inventory comparison; aggregation can verify it without target I/O."""
    if set(container_modes) != {".", "content", "content/external", "manifest.json"}:
        raise ValueError("Incomplete operational wrapper identity")
    baseline = json.loads(original_bytes)
    prefix = "content/workspace/"
    actual = {}
    for row in retained["entries"]:
        if row["path"] == "content/workspace":
            name = "."
        elif row["path"].startswith(prefix):
            name = row["path"][len(prefix):]
        else:
            raise ValueError("Unexpected operational retention root")
        if name in actual:
            raise ValueError("Duplicate operational inventory entry")
        actual[name] = dict(row, path=name)
    expected = {row["path"]: row for row in baseline["entries"]}
    if len(expected) != len(baseline["entries"]):
        raise ValueError("Duplicate canonical inventory entry")
    expected.update({name: {"path": name, "kind": "directory", "mode": mode}
                     for name, mode in container_modes.items() if name != "manifest.json"})
    expected["manifest.json"] = {"path": "manifest.json", "kind": "file",
        "mode": container_modes["manifest.json"], "size": len(original_bytes),
        "sha256": _hash(original_bytes)}
    delta = {
        "added": [actual[k] for k in sorted(actual.keys() - expected.keys())],
        "missing": [expected[k] for k in sorted(expected.keys() - actual.keys())],
        "modified": [{"path": k, "before": expected[k], "after": actual[k]}
                     for k in sorted(actual.keys() & expected.keys()) if actual[k] != expected[k]],
    }
    allowed, rejected = [], []
    for change, rows in delta.items():
        for row in rows:
            path = row["path"]
            versions = (row["before"], row["after"]) if change == "modified" else (row,)
            regular = all(v["kind"] == "file" for v in versions)
            same_mode = change != "modified" or row["before"]["mode"] == row["after"]["mode"]
            (allowed if path in OPERATIONAL_METADATA and regular and same_mode else rejected).append(
                {"change": change, "path": path})
    return delta, allowed, rejected


def retain_operational_delta(canonical_manifest, operational_manifest, container_modes, output):
    """Retain every final byte, then classify only three SQLite paths separately.

    The canonical validator remains strict. This does not claim logical database
    equivalence, ignore changes, repair targets, or admit arbitrary Git metadata.
    """
    canonical_manifest, operational_manifest = map(Path, (canonical_manifest, operational_manifest))
    original_bytes = _retained_bytes(canonical_manifest.parent, canonical_manifest.name)
    canonical = validate_capture(canonical_manifest, _hash(original_bytes))
    # Retain the entire operational bundle, including external evidence and its
    # original manifest. The new outer capture records mutations without repair.
    receipt = save_delivery(operational_manifest.parent, output,
                            {"kind": "assessment-operational-as-found"},
                            inspect_git_dependencies=False)
    final_manifest = Path(receipt["capture"]["uri"])
    validate_capture(final_manifest, receipt["capture"]["sha256"])
    retained = json.loads(final_manifest.read_bytes())
    delta, allowed, rejected = operational_delta(original_bytes, retained, container_modes)
    canonical_after = validate_capture(canonical_manifest, canonical["capture"]["sha256"])
    if canonical_after != canonical:
        raise ValueError("Canonical capture identity changed during assessment retention")
    delta_path = Path(output) / "operational-delta.json"
    # The outer capture lives below output; the additive delta is outside it.
    delta_bytes = _json_bytes({"canonical_capture": canonical["capture"],
        "operational_initial_sha256": _hash(original_bytes), "delta": delta,
        "permitted_metadata_changes": allowed, "rejected_changes": rejected,
        "logical_database_equivalence": "not-claimed"})
    delta_path.write_bytes(delta_bytes)
    complete = receipt["capture_status"] == "complete"
    return {"schema_version": 1, "kind": "assessment-operational-integrity",
        "canonical_capture": canonical["capture"], "canonical_unchanged": True,
        "operational_initial_sha256": _hash(original_bytes),
        "target_unchanged": not any(delta.values()) and complete,
        "operational_metadata_changed": bool(allowed),
        "protected_unchanged": not rejected and complete,
        "permitted_metadata_paths": sorted(OPERATIONAL_METADATA),
        "permitted_metadata_changes": allowed, "rejected_changes": rejected,
        "logical_database_equivalence": "not-claimed",
        "final_capture": {"path": str(final_manifest), "sha256": receipt["capture"]["sha256"]},
        "delta": {"path": str(delta_path), "sha256": _hash(delta_bytes)},
        "capture_status": receipt["capture_status"], "errors": retained["errors"],
        "omissions": retained["omissions"]}
