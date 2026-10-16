"""Seed and verify an independent repository for a judge's execution evidence."""
import json
import os
from pathlib import Path
import subprocess


IGNORE = ".codex/\n.entire/\n.pixi/\n__pycache__/\n"
SEED_FILES = {".gitignore", "judge-target.json"}


def _git(repo, *args, check=True):
    # Repository selectors inherited from a caller must not redirect operations
    # into the research target or supply a shared index/object store.
    environment = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                 "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                 "GIT_NAMESPACE"):
        environment.pop(name, None)
    return subprocess.run(
        ["git", "--no-optional-locks", "--no-replace-objects", "-C", str(repo),
         *map(str, args)], env=environment, check=check,
        capture_output=True, text=True)


def _output(repo, *args):
    return _git(repo, *args).stdout.strip()


def _paths(workspace, target):
    workspace, target = Path(workspace).resolve(), Path(target).resolve()
    if workspace.is_relative_to(target) or target.is_relative_to(workspace):
        raise SystemExit("Judge workspace and target must not overlap")
    return workspace, target


def _clean(repo, label):
    if _output(repo, "status", "--porcelain=v1", "--untracked-files=all",
               "--ignore-submodules=none"):
        raise SystemExit(label + " must have no tracked changes or untracked files")


def _target_identity(target):
    target = Path(target).resolve()
    if Path(_output(target, "rev-parse", "--show-toplevel")).resolve() != target:
        raise SystemExit("Judge target must be a Git repository root")
    identity = {"schema_version": 1, "target_path": str(target),
                "target_commit": _output(target, "rev-parse", "HEAD^{commit}"),
                "target_tree": _output(target, "rev-parse", "HEAD^{tree}")}
    _clean(target, "Judge target")
    return identity


def validate_target(target: Path, identity: dict) -> None:
    """Recheck the pinned research object without refreshing its Git index."""
    if not isinstance(identity, dict) or type(identity.get("schema_version")) is not int:
        raise SystemExit("Invalid judge target identity")
    if _target_identity(target) != identity:
        raise SystemExit("Judge target identity changed")


def _independent_repository(workspace):
    metadata = workspace / ".git"
    objects = metadata / "objects"
    if not metadata.is_dir() or metadata.is_symlink():
        raise SystemExit("Judge workspace must own its Git metadata directory")
    if Path(_output(workspace, "rev-parse", "--show-toplevel")).resolve() != workspace:
        raise SystemExit("Judge workspace must be a Git repository root")
    for option in ("--absolute-git-dir", "--git-common-dir"):
        actual = _output(workspace, "rev-parse", "--path-format=absolute", option)
        if Path(actual).resolve() != metadata:
            raise SystemExit("Judge workspace must not share Git metadata")
    actual_objects = _output(workspace, "rev-parse", "--path-format=absolute",
                             "--git-path", "objects")
    if not objects.is_dir() or objects.is_symlink() or Path(actual_objects).resolve() != objects:
        raise SystemExit("Judge workspace must own its Git object store")
    if any((objects / "info" / name).exists() or (objects / "info" / name).is_symlink()
           for name in ("alternates", "http-alternates")):
        raise SystemExit("Judge workspace must not use alternate Git object stores")
    # Links can share storage even without an alternates file.
    for path in objects.rglob("*"):
        if path.is_symlink() or (path.is_file() and path.stat().st_nlink > 1):
            raise SystemExit("Judge workspace must not use linked Git objects")


def validate(workspace: Path, target: Path) -> dict:
    """Require the pristine independent seed before launching a judge."""
    workspace, target = _paths(workspace, target)
    _independent_repository(workspace)
    if _output(workspace, "symbolic-ref", "--short", "HEAD") != "codex/judgment":
        raise SystemExit("Judge workspace must use the codex/judgment branch")
    # Read actual commit headers: shallow boundaries can hide parents from
    # rev-list, but do not make a descendant an independent seed.
    headers = _git(workspace, "cat-file", "commit", "HEAD").stdout.split("\n\n", 1)[0]
    if any(line.startswith("parent ") for line in headers.splitlines()):
        raise SystemExit("Judge workspace must start at one parentless seed commit")
    records = _git(workspace, "ls-tree", "-rz", "HEAD").stdout.split("\0")
    files = {}
    for record in filter(None, records):
        metadata, path = record.split("\t", 1)
        mode, kind, _ = metadata.split()
        files[path] = (mode, kind)
    if set(files) != SEED_FILES or any(value != ("100644", "blob") for value in files.values()):
        raise SystemExit("Judge workspace seed must contain only its target receipt and ignore file")
    if _git(workspace, "show", "HEAD:.gitignore").stdout != IGNORE:
        raise SystemExit("Judge workspace ignore rules differ from its seed")
    try:
        identity = json.loads(_git(workspace, "show", "HEAD:judge-target.json").stdout)
    except json.JSONDecodeError as error:
        raise SystemExit("Invalid judge target receipt") from error
    _clean(workspace, "Judge workspace")
    validate_target(target, identity)
    if _git(workspace, "cat-file", "-e", identity["target_commit"], check=False).returncode == 0:
        raise SystemExit("Judge workspace contains the research target's Git history")
    return identity


def initialize(workspace: Path, target: Path, provenance: Path) -> dict:
    """Create a fresh seed without copying or fetching the research history."""
    if Path(workspace).is_symlink():
        raise SystemExit("Judge workspace must be a new directory")
    workspace, target = _paths(workspace, target)
    if workspace.exists():
        raise SystemExit("Judge workspace already exists; choose a new directory")
    identity = _target_identity(target)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    # Empty templates and a local hooks path prevent inherited commit hooks from
    # executing before the coordinator explicitly prepares judge capture.
    _git(workspace.parent, "init", "--template=", "-b", "codex/judgment", workspace)
    hooks = workspace / ".git/hooks"
    hooks.mkdir()
    _git(workspace, "config", "core.hooksPath", hooks)
    (workspace / ".gitignore").write_text(IGNORE)
    (workspace / "judge-target.json").write_text(json.dumps(identity, indent=2) + "\n")
    _git(workspace, "add", "--", ".gitignore", "judge-target.json")
    # Resolve for this commit, as for research seeds; never reuse old trailers.
    trailers = subprocess.check_output([str(provenance)], text=True).strip()
    _git(workspace, "commit", "-m", "chore(judge): seed independent execution workspace\n\n" + trailers)
    return validate(workspace, target)
