"""Disposable Git fixtures for the judge/target repository boundary."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import judge_workspace as judge


def git(repo, *args, check=True):
    return subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *map(str, args)],
                          check=check, capture_output=True, text=True).stdout.strip()


def commit(repo, message="test: update synthetic target"):
    git(repo, "add", "--all")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repositories(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    configuration = tmp_path / "global.gitconfig"
    configuration.write_text("")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(configuration))
    for role in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{role}_NAME", "Judge fixture")
        monkeypatch.setenv(f"GIT_{role}_EMAIL", "fixture@example.invalid")
    target = tmp_path / "research"
    target.mkdir()
    git(target, "init", "--template=", "-b", "main")
    (target / "findings.txt").write_text("Synthetic scientific result\n")
    (target / ".gitignore").write_text("cache/\n")
    commit(target)
    (target / "findings.txt").write_text("Final synthetic scientific result\n")
    commit(target)
    resolver = tmp_path / "provenance"
    resolver.write_text(
        '#!/bin/sh\nprintf "%s\\n" '
        '"Co-Authored-By: Synthetic judge fixture <fixture@example.invalid>" '
        '"Codex-Reasoning-Effort: high"\n')
    resolver.chmod(0o755)
    return target, tmp_path / "judge", resolver


def snapshot(target):
    metadata = Path(git(target, "rev-parse", "--absolute-git-dir"))
    return {"head": git(target, "rev-parse", "HEAD"),
            "tree": git(target, "rev-parse", "HEAD^{tree}"),
            "status": git(target, "status", "--porcelain=v1", "--untracked-files=all"),
            "index": (metadata / "index").read_bytes()}


def test_initialize_creates_independent_seed_without_mutating_target(repositories):
    target, workspace, resolver = repositories
    before = snapshot(target)
    receipt = judge.initialize(workspace, target, resolver)
    assert receipt == {"schema_version": 1, "target_path": str(target.resolve()),
                       "target_commit": before["head"], "target_tree": before["tree"]}
    assert json.loads((workspace / "judge-target.json").read_text()) == receipt
    assert set(git(workspace, "ls-tree", "-r", "--name-only", "HEAD").splitlines()) == judge.SEED_FILES
    assert len(git(workspace, "rev-list", "--parents", "HEAD").split()) == 1
    assert git(workspace, "branch", "--show-current") == "codex/judgment"
    assert git(workspace, "config", "core.hooksPath") == str(workspace / ".git/hooks")
    assert git(workspace, "remote") == ""
    assert "Co-Authored-By: Synthetic judge fixture" in git(workspace, "log", "-1", "--format=%B")
    assert "Codex-Reasoning-Effort: high" in git(workspace, "log", "-1", "--format=%B")
    target_objects = set(git(target, "rev-list", "--objects", "--all").splitlines())
    workspace_objects = set(git(workspace, "rev-list", "--objects", "--all").splitlines())
    assert not target_objects & workspace_objects
    assert subprocess.run(["git", "-C", str(workspace), "cat-file", "-e", before["head"]],
                          capture_output=True).returncode != 0
    assert not (workspace / ".git/objects/info/alternates").exists()
    assert judge.validate(workspace, target) == receipt
    assert snapshot(target) == before


def test_initialize_uses_fresh_provenance_for_each_seed(repositories):
    target, workspace, resolver = repositories
    judge.initialize(workspace, target, resolver)
    resolver.write_text('#!/bin/sh\nprintf "%s\\n" "Co-Authored-By: Updated fixture <new@example.invalid>"\n')
    second = workspace.with_name("second-judge")
    judge.initialize(second, target, resolver)
    assert "Updated fixture" in git(second, "log", "-1", "--format=%B")
    assert "Updated fixture" not in git(workspace, "log", "-1", "--format=%B")


def test_initialize_does_not_run_global_or_template_hooks(repositories, tmp_path, monkeypatch):
    target, workspace, resolver = repositories
    marker = tmp_path / "unexpected-hook"
    for folder in (tmp_path / "global-hooks", tmp_path / "template/hooks"):
        folder.mkdir(parents=True)
        hook = folder / "pre-commit"
        hook.write_text(f'#!/bin/sh\ntouch "{marker}"\nexit 1\n')
        hook.chmod(0o755)
    configuration = tmp_path / "hooks.gitconfig"
    configuration.write_text(
        f'[core]\n\thooksPath = {tmp_path / "global-hooks"}\n'
        f'[init]\n\ttemplateDir = {tmp_path / "template"}\n')
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(configuration))
    judge.initialize(workspace, target, resolver)
    assert not marker.exists()
    assert not list((workspace / ".git/hooks").iterdir())


@pytest.mark.parametrize("relationship", ["same", "inside-target", "contains-target", "symlink"])
def test_workspace_and_target_cannot_overlap(repositories, relationship):
    target, workspace, resolver = repositories
    if relationship == "same":
        workspace = target
    elif relationship == "inside-target":
        workspace = target / "judge"
    elif relationship == "contains-target":
        workspace = target.parent
    else:
        workspace.symlink_to(target, target_is_directory=True)
    before = snapshot(target)
    with pytest.raises(SystemExit):
        judge.initialize(workspace, target, resolver)
    with pytest.raises(SystemExit, match="overlap"):
        judge.validate(workspace, target)
    assert snapshot(target) == before


def test_existing_workspace_is_preserved(repositories):
    target, workspace, resolver = repositories
    workspace.mkdir()
    (workspace / "keep.txt").write_text("Preserve existing work")
    with pytest.raises(SystemExit, match="already exists"):
        judge.initialize(workspace, target, resolver)
    assert (workspace / "keep.txt").read_text() == "Preserve existing work"
    assert not (workspace / ".git").exists()


@pytest.mark.parametrize("change", ["tracked", "staged", "untracked"])
def test_dirty_target_is_rejected_without_changes(repositories, change):
    target, workspace, resolver = repositories
    receipt = judge.initialize(workspace, target, resolver)
    if change == "untracked":
        (target / "new.txt").write_text("Uncommitted work")
    else:
        (target / "findings.txt").write_text("Uncommitted change")
        if change == "staged":
            git(target, "add", "findings.txt")
    before = snapshot(target)
    with pytest.raises(SystemExit, match="Judge target must have no"):
        judge.validate(workspace, target)
    with pytest.raises(SystemExit, match="Judge target must have no"):
        judge.validate_target(target, receipt)
    with pytest.raises(SystemExit, match="Judge target must have no"):
        judge.initialize(workspace.with_name("another-judge"), target, resolver)
    assert snapshot(target) == before
    assert not workspace.with_name("another-judge").exists()


def test_committed_target_change_is_stale(repositories):
    target, workspace, resolver = repositories
    receipt = judge.initialize(workspace, target, resolver)
    (target / "findings.txt").write_text("New committed scientific result")
    commit(target)
    with pytest.raises(SystemExit, match="identity changed"):
        judge.validate(workspace, target)
    with pytest.raises(SystemExit, match="identity changed"):
        judge.validate_target(target, receipt)


@pytest.mark.parametrize("change", ["receipt", "ignore", "untracked", "staged", "extra-commit"])
def test_dirty_or_evolved_workspace_is_rejected(repositories, change):
    target, workspace, resolver = repositories
    receipt = judge.initialize(workspace, target, resolver)
    if change == "receipt":
        (workspace / "judge-target.json").write_text("{}\n")
    elif change == "ignore":
        (workspace / ".gitignore").write_text("*\n")
    else:
        (workspace / "assessment.json").write_text("{}\n")
        if change == "staged":
            git(workspace, "add", "assessment.json")
        elif change == "extra-commit":
            commit(workspace, "test: add judgment output")
    with pytest.raises(SystemExit):
        judge.validate(workspace, target)
    # A final target-only check remains possible after legitimate judge output.
    judge.validate_target(target, receipt)


@pytest.mark.parametrize("field", ["target_path", "target_commit", "target_tree", "schema_version"])
def test_committed_tampered_identity_is_rejected(repositories, field):
    target, workspace, resolver = repositories
    receipt = judge.initialize(workspace, target, resolver)
    receipt[field] = True if field == "schema_version" else "tampered"
    (workspace / "judge-target.json").write_text(json.dumps(receipt) + "\n")
    git(workspace, "add", "judge-target.json")
    git(workspace, "commit", "--amend", "--no-edit")
    with pytest.raises(SystemExit, match="[Ii]dentity"):
        judge.validate(workspace, target)


def test_ignored_runtime_files_and_local_hook_configuration_are_allowed(repositories):
    target, workspace, resolver = repositories
    receipt = judge.initialize(workspace, target, resolver)
    for name in (".codex", ".entire", ".pixi", "__pycache__"):
        (workspace / name).mkdir()
        (workspace / name / "runtime.json").write_text("{}\n")
    (workspace / ".git/hooks/post-commit").write_text("#!/bin/sh\nexit 0\n")
    git(workspace, "config", "entire.enabled", "true")
    # Ignored cache/annex-style metadata is not a research tree change.
    (target / "cache").mkdir()
    (target / "cache/payload").write_text("Ignored runtime data")
    (target / ".git/annex").mkdir()
    (target / ".git/annex/local-state").write_text("Annex metadata")
    before = snapshot(target)
    assert judge.validate(workspace, target) == receipt
    assert snapshot(target) == before


@pytest.mark.parametrize("kind", ["nested", "worktree", "alternate", "symlinked-metadata", "symlinked-objects"])
def test_shared_or_nested_git_metadata_is_rejected(repositories, kind):
    target, workspace, resolver = repositories
    judge.initialize(workspace, target, resolver)
    if kind == "nested":
        workspace = workspace / "nested"
        workspace.mkdir()
    elif kind == "worktree":
        linked = workspace.with_name("linked-judge")
        git(workspace, "worktree", "add", "--detach", linked)
        workspace = linked
    elif kind == "alternate":
        (workspace / ".git/objects/info/alternates").write_text(str(target / ".git/objects") + "\n")
    else:
        original = workspace / (".git" if kind == "symlinked-metadata" else ".git/objects")
        moved = workspace.with_name("moved-git-storage")
        original.rename(moved)
        original.symlink_to(moved, target_is_directory=True)
    with pytest.raises(SystemExit):
        judge.validate(workspace, target)


def test_imported_unreachable_target_commit_is_rejected(repositories):
    target, workspace, resolver = repositories
    judge.initialize(workspace, target, resolver)
    git(workspace, "fetch", "--no-write-fetch-head", target, "HEAD")
    assert git(target, "rev-parse", "HEAD") not in git(workspace, "rev-list", "--all")
    with pytest.raises(SystemExit, match="research target's Git history"):
        judge.validate(workspace, target)


def test_shallow_boundary_does_not_hide_seed_parents(repositories):
    target, workspace, resolver = repositories
    judge.initialize(workspace, target, resolver)
    git(workspace, "commit", "--allow-empty", "-m", "test: add a second commit")
    head = git(workspace, "rev-parse", "HEAD")
    (workspace / ".git/shallow").write_text(head + "\n")
    assert git(workspace, "rev-list", "--parents", "HEAD") == head
    with pytest.raises(SystemExit, match="parentless"):
        judge.validate(workspace, target)


def test_hardlinked_target_blob_is_not_an_independent_object_store(repositories):
    target, workspace, resolver = repositories
    judge.initialize(workspace, target, resolver)
    oid = git(target, "rev-parse", "HEAD:findings.txt")
    source = target / ".git/objects" / oid[:2] / oid[2:]
    destination = workspace / ".git/objects" / oid[:2] / oid[2:]
    destination.parent.mkdir(exist_ok=True)
    os.link(source, destination)
    with pytest.raises(SystemExit, match="linked Git objects"):
        judge.validate(workspace, target)


def test_complete_no_git_delivery_has_capture_identity_without_borrowed_commit(repositories, tmp_path):
    from delivery_snapshot import save_delivery, materialize_capture, validate_capture
    parent, workspace, resolver = repositories
    original = parent / "ordinary-delivery"
    original.mkdir()
    (original / "untracked-result.csv").write_text("x\n1\n")
    pointer = save_delivery(original, tmp_path / "capture", {})
    copied = materialize_capture(pointer["capture"]["uri"], tmp_path / "delivery-copy")
    target = Path(copied["target"])
    identity = judge.initialize(workspace, target, resolver, Path(copied["manifest"]))
    assert identity["schema_version"] == 2
    assert identity["target_commit"] is None
    assert identity["capture"]["sha256"] == pointer["capture"]["sha256"]
    judge.validate(workspace, target)
    judge.validate_target(target, identity)
    validate_capture(copied["manifest"])
    assert not (target / ".git").exists()
