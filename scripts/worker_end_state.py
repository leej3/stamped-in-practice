"""Read-only worker stop receipts; preservation is not worker versioning credit."""
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _safe_path(root, relative):
    """Never follow a parent symlink outside the inventoried repository."""
    parts = Path(relative).parts
    if not parts or Path(relative).is_absolute() or ".." in parts:
        raise ValueError("Invalid repository-relative path")
    path = root
    for component in parts[:-1]:
        path = path / component
        if not stat.S_ISDIR(path.lstat().st_mode):
            raise ValueError("A parent component is not a directory")
    return root / relative


def _file_state(root, relative, tracked):
    item = {"path": relative, "tracked": tracked}
    try:
        path = _safe_path(root, relative)
        metadata = path.lstat()
    except FileNotFoundError:
        return dict(item, kind="missing")
    if stat.S_ISLNK(metadata.st_mode):
        target = os.readlink(os.fsencode(path))
        return dict(item, kind="symlink", link_target=os.fsdecode(target),
                    sha256=_digest(target))
    if stat.S_ISDIR(metadata.st_mode):
        return dict(item, kind="directory")
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError("Unsupported special file; content was not read")
    # O_NONBLOCK also prevents a concurrent replacement with a FIFO from hanging.
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("File type changed during capture")
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
        after = os.fstat(stream.fileno())
    signature = lambda st: (st.st_dev, st.st_ino, st.st_mode, st.st_size,
                           st.st_mtime_ns, st.st_ctime_ns)
    if signature(metadata) != signature(before) or signature(before) != signature(after):
        raise ValueError("File changed during capture")
    if signature(after) != signature(path.lstat()):
        raise ValueError("File was replaced during capture")
    return dict(item, kind="file", size=after.st_size,
                executable=bool(after.st_mode & stat.S_IXUSR), sha256=digest.hexdigest())


def _annex_content(directory, path, item, common_dir):
    """Inspect only an annex object named by a link, never arbitrary link targets."""
    if item["kind"] != "symlink" or not common_dir:
        return
    objects = common_dir / "annex/objects"
    target = Path(os.path.abspath(directory / Path(path).parent / item["link_target"]))
    if not target.is_relative_to(objects) or target.name != target.parent.name:
        return
    relative = str(target.relative_to(objects))
    # Require the conventional two hash directories plus key/key structure.
    if len(Path(relative).parts) != 4:
        return
    item["annex_key"] = target.name
    try:
        content = _file_state(common_dir, "annex/objects/" + relative, False)
    except FileNotFoundError:
        content = {"kind": "missing"}
    if content["kind"] == "missing":
        item["annex_content"] = {"available": False}
    elif content["kind"] == "file":
        item["annex_content"] = {"available": True, "sha256": content["sha256"],
                                 "size": content["size"]}
    else:
        raise ValueError("Annex object is not a regular file; target was not followed")


def capture_worker_end_state(checkout, worker=None):
    """Inventory Git and nonignored files without staging, committing or fetching.

    Git optional locks, fsmonitor and the untracked cache are disabled. A failed
    inspection produces a partial receipt instead of losing the stopped state.
    This is a bounded-in-time observation, not an atomic filesystem snapshot.
    """
    root = Path(checkout).resolve()
    errors = []

    def fail(repository, operation, error):
        errors.append({"repository": repository, "operation": operation, "error": str(error)})

    def git(directory, relative, *args, optional=False):
        try:
            result = subprocess.run([
                "git", "--no-optional-locks", "-c", "core.fsmonitor=false",
                "-c", "core.untrackedCache=false", "-C", str(directory), *args,
            ], capture_output=True, timeout=60,
                env=dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0"))
            if result.returncode and not optional:
                fail(relative, "git " + " ".join(args),
                     result.stderr.decode("utf-8", "replace").strip() or
                     "exit " + str(result.returncode))
            return result.stdout if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired) as exc:
            fail(relative, "git " + " ".join(args), exc)
            return None

    def repository(directory, relative):
        top = git(directory, relative, "rev-parse", "--show-toplevel")
        if not top or Path(os.fsdecode(top.removesuffix(b"\n"))).resolve() != directory.resolve():
            fail(relative, "repository boundary", "Checkout is not an independent repository root")
            return {"head_commit": None}
        head = git(directory, relative, "rev-parse", "--verify", "HEAD")
        status_args = ("status", "--porcelain=v1", "-z", "--untracked-files=all",
                       "--ignore-submodules=none")
        status = git(directory, relative, *status_args)
        staged = git(directory, relative, "ls-files", "--stage", "-z")
        untracked = git(directory, relative, "ls-files", "--others", "--exclude-standard", "-z")
        branch = git(directory, relative, "symbolic-ref", "-q", "HEAD", optional=True)
        refs = git(directory, relative, "for-each-ref", "--format=%(refname) %(objectname)")
        common = git(directory, relative, "rev-parse", "--path-format=absolute", "--git-common-dir")
        common_dir = Path(os.fsdecode(common.removesuffix(b"\n"))) if common else None
        state = {
            "head_commit": head.decode().strip() if head else None,
            "head_ref": os.fsdecode(branch).strip() if branch else None,
            "status_porcelain_v1_z_base64": base64.b64encode(status).decode() if status is not None else None,
            "refs": [{"name": os.fsdecode(name), "object_id": oid.decode()}
                     for name, oid in (line.split(b" ", 1) for line in (refs or b"").splitlines())],
            "index": [], "worktree": [], "submodules": [], "embedded_repositories": [],
        }
        tracked = set()
        gitlinks = {}
        for entry in (staged or b"").split(b"\0"):
            if not entry:
                continue
            metadata, path = entry.split(b"\t", 1)
            mode, oid, stage = metadata.split()
            path = os.fsdecode(path)
            state["index"].append({"path": path, "mode": mode.decode(),
                                   "object_id": oid.decode(), "stage": int(stage)})
            tracked.add(path)
            if mode == b"160000":
                gitlinks[path] = oid.decode()
        others = {os.fsdecode(path).rstrip("/") for path in (untracked or b"").split(b"\0") if path}
        for path in sorted(tracked | others):
            try:
                item = _file_state(directory, path, path in tracked)
                state["worktree"].append(item)
                _annex_content(directory, path, item, common_dir)
                if item["kind"] == "missing" and path not in tracked:
                    fail(relative, "inventory " + path, "Untracked file disappeared during capture")
                if path in gitlinks or item["kind"] == "directory":
                    nested = {"path": path, "initialized": False}
                    if path in gitlinks:
                        nested["index_commit"] = gitlinks[path]
                        state["submodules"].append(nested)
                    else:
                        state["embedded_repositories"].append(nested)
                    if item["kind"] == "directory":
                        child = _safe_path(directory, path)
                        top = git(child, relative + "/" + path, "rev-parse", "--show-toplevel", optional=True)
                        if top and Path(os.fsdecode(top.removesuffix(b"\n"))).resolve() == child.resolve():
                            nested["initialized"] = True
                            nested["repository"] = repository(child, relative + "/" + path)
                        elif path not in gitlinks:
                            fail(relative, "inventory " + path, "Untracked directory is not an inspectable repository")
            except (OSError, ValueError) as exc:
                fail(relative, "inventory " + path, exc)
        # Detect common concurrent changes without writing Git's index refresh.
        if (head != git(directory, relative, "rev-parse", "--verify", "HEAD") or
                staged != git(directory, relative, "ls-files", "--stage", "-z") or
                status != git(directory, relative, *status_args)):
            fail(relative, "consistency", "Git state changed during capture")
        return state

    receipt = {"schema_version": 1, "kind": "worker-end-state", "captured_at": utc_now(),
               "checkout": str(root), "worker": worker, "errors": errors}
    try:
        receipt.update(repository(root, "."))
    except Exception as exc:
        # Keep the launch evidence even if an unusual repository defeats parsing.
        fail(".", "capture", exc)
    receipt["capture_finished_at"] = utc_now()
    receipt["capture_status"] = "partial" if errors else "complete"
    return receipt


def save_worker_end_state(checkout, output, worker):
    """Write the observation outside worker inputs and return its file identity."""
    destination = Path(output).resolve() / "worker-end-state.json"
    if destination.is_relative_to(Path(checkout).resolve()):
        raise ValueError("Worker end-state receipt must be outside the worker checkout")
    receipt = capture_worker_end_state(checkout, worker)
    content = (json.dumps(receipt, indent=2) + "\n").encode()
    with destination.open("xb") as stream:
        stream.write(content)
    return {"path": destination.name, "sha256": _digest(content),
            "capture_status": receipt["capture_status"], "head_commit": receipt.get("head_commit")}


def validate_retained_artifacts(receipt, result_checkout):
    """Reject a result checkout whose material differs from the stopped worker.

    The result must be the clean preservation commit, before adding coordinator
    evidence. Comparing hashes does not grant worker credit for that commit.
    No network, Git mutation, or annex materialization is performed here.
    """
    if receipt.get("schema_version") != 1 or receipt.get("kind") != "worker-end-state":
        raise ValueError("Unsupported worker end-state receipt")
    if receipt.get("capture_status") != "complete" or receipt.get("errors"):
        raise ValueError("Worker end-state receipt is incomplete")
    observed = capture_worker_end_state(result_checkout)
    if observed["capture_status"] != "complete":
        raise ValueError("Result checkout could not be completely inventoried")

    via_key, via_reference, via_commit = [], [], []

    def content(row, path):
        annex = row.get("annex_content", {})
        if annex.get("available"):
            return {"kind": "file", "executable": False,
                    "size": annex["size"], "sha256": annex["sha256"]}
        key = row.get("annex_key", "")
        match = re.fullmatch(r"SHA256(?:E)?-s([0-9]+)--([0-9a-f]{64})(?:\..*)?", key)
        if match:
            via_key.append(path)
            return {"kind": "file", "executable": False,
                    "size": int(match[1]), "sha256": match[2]}
        return {key: value for key, value in row.items() if key not in ("path", "tracked")}

    def material(state):
        rows = {row["path"]: row for row in state["worktree"] if row["kind"] != "missing"}
        nested = {row["path"]: row for row in state["submodules"] + state["embedded_repositories"]}
        rows.update({path: {"kind": "repository"} for path in nested})
        return rows, nested

    def equivalent(expected, actual, prefix=""):
        before, before_nested = material(expected)
        after, after_nested = material(actual)
        if before.keys() != after.keys():
            return False
        for path, row in before.items():
            name = prefix + path
            if row["kind"] != "repository":
                other = after[path]
                old_content, new_content = content(row, name), content(other, name)
                if (row["kind"] == other["kind"] == "symlink" and row.get("annex_key") and
                        row["annex_key"] == other.get("annex_key") and
                        row["link_target"] == other.get("link_target") and
                        not (row.get("annex_content", {}).get("available") and
                             other.get("annex_content", {}).get("available")) and
                        not (old_content["kind"] == new_content["kind"] == "file")):
                    # Unchanged MD5E/other backend pointers survive a fresh
                    # clone before annex materialization. This proves only the
                    # retained reference, and cannot override a SHA256 mismatch.
                    via_reference.append(name)
                    continue
                if old_content != new_content:
                    return False
                continue
            if path not in after_nested:
                return False
            old, new = before_nested[path], after_nested[path]
            old_repo = old.get("repository")
            clean_commit = old.get("index_commit") if not old["initialized"] else None
            if (old_repo and not old_repo["status_porcelain_v1_z_base64"] and
                    old_repo["head_commit"] == old.get("index_commit")):
                clean_commit = old["index_commit"]
            if clean_commit and new.get("index_commit") == clean_commit:
                # A matching Git tree proves identity without installing clean
                # optional dependencies. It does not prove payload retrieval.
                if not new["initialized"]:
                    via_commit.append(name)
                    continue
            if old_repo and new.get("repository"):
                if not equivalent(old_repo, new["repository"], name + "/"):
                    return False
            elif not (clean_commit and new.get("index_commit") == clean_commit):
                return False
        return True

    if observed["status_porcelain_v1_z_base64"]:
        raise ValueError("Result checkout must be clean before judging")
    if not equivalent(receipt, observed):
        raise ValueError("Result artifacts differ from the worker end-state inventory")
    ancestry = subprocess.run(["git", "--no-optional-locks", "-C", str(result_checkout),
                               "merge-base", "--is-ancestor", receipt["head_commit"],
                               observed["head_commit"]], capture_output=True, timeout=60)
    if ancestry.returncode:
        raise ValueError("Result commit does not retain the worker HEAD in its history")
    report = {"worker_head_commit": receipt["head_commit"],
              "result_commit": observed["head_commit"], "artifacts_match": True}
    if via_key:
        report["annex_identity_without_local_payload"] = sorted(set(via_key))
    if via_reference:
        report["annex_reference_identity_without_local_payload"] = sorted(set(via_reference))
    if via_commit:
        report["submodule_identity_without_checkout"] = sorted(set(via_commit))
    return report
