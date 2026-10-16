"""Independent fixtures for the opt-in original-delivery capture protocol."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import delivery_snapshot as delivery


def git(root, *arguments):
    return subprocess.check_output(["git", "-C", str(root), *map(str, arguments)],
                                   env=dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)).strip()


def repository(root):
    root.mkdir()
    git(root, "init", "-b", "main")
    git(root, "config", "user.name", "Delivery fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "core.hooksPath", "/dev/null")
    (root / "tracked.txt").write_text("original")
    (root / ".gitignore").write_text("ignored/\n.pixi/\npixi.lock\n")
    git(root, "add", ".")
    git(root, "commit", "-m", "test: create delivery fixture")
    return root


def snapshot(root):
    """Independent recursive inventory, including Git, ignored files and links."""
    rows = {}
    for parent, directories, files in os.walk(root, followlinks=False):
        for name in directories + files:
            path = Path(parent) / name
            metadata = path.lstat()
            kind = stat.S_IFMT(metadata.st_mode)
            content = os.readlink(path) if path.is_symlink() else path.read_bytes() if path.is_file() else None
            rows[str(path.relative_to(root))] = (kind, stat.S_IMODE(metadata.st_mode), content)
    return rows


def capture(root, output, **arguments):
    pointer = delivery.save_delivery(root, output, {"returncode": 0}, **arguments)
    manifest_path = Path(pointer["capture"]["uri"])
    manifest = json.loads(manifest_path.read_text())
    return pointer, manifest_path, manifest


def test_dirty_git_ignored_environment_and_metadata_survive_exactly(tmp_path):
    root = repository(tmp_path / "worker")
    head = git(root, "rev-parse", "HEAD").decode()
    (root / "tracked.txt").write_text("staged")
    git(root, "add", "tracked.txt")
    (root / "tracked.txt").write_text("dirty final bytes")
    (root / "ignored").mkdir()
    (root / "ignored/scientific-result.bin").write_bytes(b"\x00important\xff")
    (root / ".pixi/envs/default").mkdir(parents=True)
    (root / ".pixi/envs/default/interpreter").write_bytes(b"reconstructable environment")
    (root / ".pixi/envs/default/interpreter").chmod(0o751)
    (root / "pixi.lock").write_text("the exact stopped lock")
    (root / "untracked.txt").write_text("retained output")
    (root / "empty").mkdir()
    before = snapshot(root)
    pointer, manifest_path, manifest = capture(root, tmp_path / "evidence")
    assert pointer["capture_status"] == "complete", manifest
    assert pointer["head_commit"] == head
    assert manifest["git_metadata"]["local_metadata_complete"] is True
    assert manifest["git_metadata"]["index"]["sha256"] == hashlib.sha256((root / ".git/index").read_bytes()).hexdigest()
    assert json.loads((tmp_path / "evidence/worker-end-state.json").read_text())["schema_version"] == 2
    assert snapshot(root) == before
    assert hashlib.sha256((tmp_path / "evidence/worker-end-state.json").read_bytes()).hexdigest() == pointer["sha256"]
    identity = delivery.validate_capture(manifest_path, pointer["capture"]["sha256"])
    assert identity["commit"] == head
    restored = delivery.materialize_capture(manifest_path, tmp_path / "judge")
    assert snapshot(Path(restored["target"])) == before
    assert git(restored["target"], "show", ":tracked.txt") == b"staged"
    assert git(restored["target"], "rev-parse", "HEAD").decode() == head
    assert restored["identity"]["capture"]["sha256"] == identity["capture"]["sha256"]


def test_no_git_directory_inside_parent_repository_borrows_no_head(tmp_path):
    parent = repository(tmp_path / "parent")
    root = parent / "ordinary-delivery"
    root.mkdir()
    (root / "data.txt").write_text("not a repository")
    pointer, manifest_path, manifest = capture(root, tmp_path / "evidence")
    assert pointer["head_commit"] is None
    assert delivery.validate_capture(manifest_path)["commit"] is None
    restored = delivery.materialize_capture(manifest_path, tmp_path / "judge")
    assert not (Path(restored["target"]) / ".git").exists()
    assert (Path(restored["target"]) / "data.txt").read_text() == "not a repository"
    assert manifest["capture_status"] == "complete"


def test_declared_external_artifacts_have_provenance_and_exact_bytes(tmp_path):
    root = tmp_path / "worker"
    root.mkdir()
    external = tmp_path / "external-result.bin"
    external.write_bytes(b"external scientific output")
    directory = tmp_path / "artifact-directory"
    directory.mkdir()
    (directory / "payload").write_bytes(b"directory output")
    pointer, manifest_path, manifest = capture(root, tmp_path / "evidence", declared_artifacts=[
        {"path": str(external), "declaration": {"role": "worker-produced-result"}},
        {"path": str(directory), "provenance": "explicitly supplied output directory"},
    ])
    rows = manifest["declared_artifacts"]
    assert rows[0]["source"] == str(external)
    assert rows[0]["declaration"] == {"role": "worker-produced-result"}
    assert (manifest_path.parent / rows[0]["path"]).read_bytes() == external.read_bytes()
    restored = delivery.materialize_capture(manifest_path, tmp_path / "judge")
    assert (Path(restored["manifest"]).parent / rows[1]["path"] / "payload").read_bytes() == b"directory output"
    assert pointer["capture_status"] == "complete"


def test_symlinks_preserved_without_reading_external_or_missing_targets(tmp_path):
    root = tmp_path / "worker"
    root.mkdir()
    external = tmp_path / "not-declared"
    external.mkdir()
    (external / "secret.txt").write_text("must not be copied")
    (root / "outside").symlink_to(external, target_is_directory=True)
    (root / "dangling").symlink_to("missing")
    _, manifest_path, manifest = capture(root, tmp_path / "evidence")
    assert all("secret.txt" not in row["path"] for row in manifest["entries"])
    restored = delivery.materialize_capture(manifest_path, tmp_path / "judge")
    assert os.readlink(Path(restored["target"]) / "outside") == str(external)
    assert os.readlink(Path(restored["target"]) / "dangling") == "missing"
    assert manifest["capture_status"] == "complete"


@pytest.mark.parametrize("change", ["bytes", "mode", "extra", "link", "missing"])
def test_validation_rejects_modified_retained_material(tmp_path, change):
    root = tmp_path / "worker"
    root.mkdir()
    (root / "result").write_text("original")
    (root / "link").symlink_to("result")
    _, path, _ = capture(root, tmp_path / "evidence")
    retained = path.parent / "content/workspace"
    if change == "bytes":
        (retained / "result").write_text("altered")
    elif change == "mode":
        (retained / "result").chmod(0o700)
    elif change == "extra":
        (retained / "invented-result").write_text("coordinator contribution")
    elif change == "link":
        (retained / "link").unlink()
        (retained / "link").symlink_to("changed")
    else:
        (retained / "result").unlink()
    with pytest.raises(ValueError, match="mismatch|file list"):
        delivery.validate_capture(path)
    with pytest.raises(ValueError):
        delivery.materialize_capture(path, tmp_path / "judge")


def test_manifest_hash_and_unsafe_manifest_paths_rejected(tmp_path):
    root = tmp_path / "worker"
    root.mkdir()
    (root / "result").write_text("original")
    pointer, path, manifest = capture(root, tmp_path / "evidence")
    manifest["entries"][1]["path"] = "../escaped"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="SHA256"):
        delivery.validate_capture(path, pointer["capture"]["sha256"])
    with pytest.raises(ValueError, match="Unsafe"):
        delivery.validate_capture(path)


def test_credential_exclusions_are_disclosed_and_caches_remain(tmp_path):
    root = tmp_path / "worker"
    root.mkdir()
    (root / ".codex").mkdir()
    (root / ".codex/auth.json").write_text("synthetic credential")
    (root / ".codex/hooks.json").write_text("scientific execution hooks")
    (root / ".ssh").mkdir()
    (root / ".ssh/id_ed25519").write_text("synthetic private key")
    (root / ".cache").mkdir()
    (root / ".cache/reconstruction.bin").write_text("must retain")
    pointer, path, manifest = capture(root, tmp_path / "evidence")
    assert pointer["capture_status"] == "partial"
    assert {row["path"] for row in manifest["omissions"]} == {
        "content/workspace/.codex/auth.json", "content/workspace/.ssh"}
    assert all(row["reason"] for row in manifest["omissions"])
    assert not (path.parent / "content/workspace/.codex/auth.json").exists()
    assert not (path.parent / "content/workspace/.ssh").exists()
    assert (path.parent / "content/workspace/.cache/reconstruction.bin").read_text() == "must retain"
    assert delivery.validate_capture(path)["capture_status"] == "partial"


def test_changing_source_retains_partial_capture_with_error(tmp_path, monkeypatch):
    root = tmp_path / "worker"
    root.mkdir()
    changing = root / "result"
    changing.write_text("initial")
    original = delivery._read_file
    def mutate(parent, name, before, destination=None):
        digest = original(parent, name, before, destination)
        if destination is not None and name == "result":
            changing.write_text("modified after copy")
        return digest
    monkeypatch.setattr(delivery, "_read_file", mutate)
    pointer, path, manifest = capture(root, tmp_path / "evidence")
    assert pointer["capture_status"] == "partial"
    assert any(row["operation"] == "consistency" for row in manifest["errors"])
    assert (path.parent / "content/workspace/result").read_text() == "initial"
    assert delivery.validate_capture(path)["capture_status"] == "partial"


def test_external_gitdir_pointer_retained_without_reading_other_repository(tmp_path):
    root = tmp_path / "worker"
    root.mkdir()
    other = repository(tmp_path / "other")
    (root / ".git").write_text(f"gitdir: {other / '.git'}\n")
    _, path, manifest = capture(root, tmp_path / "evidence")
    assert manifest["head_commit"] is None
    assert manifest["capture_status"] == "partial"
    assert any(row["kind"] == "git-dependency" for row in manifest["omissions"])
    assert (path.parent / "content/workspace/.git").read_bytes() == (root / ".git").read_bytes()
    assert all("objects" not in row["path"] for row in manifest["entries"])
    assert delivery.validate_capture(path)["commit"] is None


def test_explicit_git_dependency_declaration_retains_original_pointer_bytes(tmp_path):
    root = tmp_path / "worker"
    root.mkdir()
    other = repository(tmp_path / "other")
    (root / ".git").write_text(f"gitdir: {other / '.git'}\n")
    _, path, manifest = capture(root, tmp_path / "evidence", declared_artifacts=[
        {"path": str(other / ".git"), "provenance": "explicit fixture Git dependency"}])
    assert manifest["capture_status"] == "complete"
    assert manifest["git_dependencies"] == [{"path": "content/workspace/.git", "covered_by_retained_sources": True,
                                             "retained_targets": ["content/external/0000"]}]
    assert delivery.validate_capture(path)["commit"] == git(other, "rev-parse", "HEAD").decode()
    assert (path.parent / "content/workspace/.git").read_bytes() == (root / ".git").read_bytes()


def test_capture_validation_rejects_symlink_container(tmp_path):
    root = tmp_path / "worker"
    root.mkdir()
    _, path, _ = capture(root, tmp_path / "evidence")
    container = path.parent / "content/external"
    container.rmdir()
    container.symlink_to(tmp_path / "absent")
    with pytest.raises(ValueError, match="Unsafe capture container"):
        delivery.validate_capture(path)


def test_unsupported_fifo_is_disclosed_without_hanging(tmp_path):
    root = tmp_path / "worker"
    root.mkdir()
    os.mkfifo(root / "socket-like-result")
    _, path, manifest = capture(root, tmp_path / "evidence")
    assert manifest["capture_status"] == "partial"
    assert manifest["errors"] and manifest["omissions"]
    assert delivery.validate_capture(path)["capture_status"] == "partial"


def test_seed_receipt_exports_only_allowlisted_condition_free_identities(tmp_path):
    root = tmp_path / "worker"
    root.mkdir()
    seed = {"seed_commit": "1" * 40, "condition": "treatment", "assignment": {"secret": True},
            "source": "/private/coordinator", "coordinator_commit": "2" * 40,
            "study_input_tree": "2" * 40, "common_prompt_sha256": "3" * 64,
            "supplied_files": [{"path": ".codex/hooks.json", "sha256": "4" * 64,
                                "source": "coordinator-native-preparation", "bytes": 42},
                               {"path": "/private/source", "sha256": "5" * 64}]}
    pointer, _, _ = capture(root, tmp_path / "evidence", seed_receipt=seed)
    receipt = json.loads((tmp_path / "evidence" / pointer["path"]).read_text())
    assert receipt["seed_identities"] == {
        "seed_commit": "1" * 40, "study_input_tree": "2" * 40, "common_prompt_sha256": "3" * 64,
        "supplied_files": [{"path": ".codex/hooks.json", "sha256": "4" * 64, "bytes": 42}]}
    assert "/private/coordinator" not in json.dumps(receipt)
    assert "/private/source" not in json.dumps(receipt)
    assert "treatment" not in json.dumps(receipt)


def test_capture_cannot_recurse_into_its_own_output(tmp_path):
    root = tmp_path / "worker"
    root.mkdir()
    with pytest.raises(ValueError, match="outside"):
        capture(root, root / "evidence")
    artifact = tmp_path / "artifact"
    artifact.mkdir()
    with pytest.raises(ValueError, match="outside"):
        capture(root, artifact / "evidence", declared_artifacts=[{"path": str(artifact), "provenance": "fixture"}])


def test_external_admin_missing_common_dir_is_partial(tmp_path):
    worker = tmp_path / "worker"
    worker.mkdir()
    admin = tmp_path / "admin"
    admin.mkdir()
    (worker / ".git").write_text(f"gitdir: {admin}\n")
    (admin / "HEAD").write_text("f" * 40 + "\n")
    (admin / "commondir").write_text("../unretained\n")
    _, path, manifest = capture(worker, tmp_path / "evidence", declared_artifacts=[{
        "path": str(admin), "declaration": "Original Git worktree admin directory"}])
    assert manifest["capture_status"] == "partial"
    assert any(row["path"] == "content/external/0000/commondir" for row in manifest["omissions"])
    assert delivery.validate_capture(path)["commit"] == "f" * 40


def test_scientific_files_named_like_git_dependencies_are_not_pointers(tmp_path):
    worker = tmp_path / "worker"
    (worker / "node_modules/commondir").mkdir(parents=True)
    (worker / "alternates").write_text("scientific label")
    _, _, manifest = capture(worker, tmp_path / "evidence")
    assert manifest["capture_status"] == "complete"
    assert manifest["git_dependencies"] == []
