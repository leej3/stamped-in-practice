"""Coordinator-only retention: synthetic captures, no native worker sessions."""
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tarfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import delivery_snapshot as delivery
import package_delivery as package


def hash_bytes(value):
    return hashlib.sha256(value).hexdigest()


def stopped(tmp_path, git=False, partial=False):
    worker = tmp_path / "worker"
    worker.mkdir()
    (worker / "result.txt").write_bytes(b"untracked final output\x00\xff")
    (worker / "script").write_text("#!/bin/sh\nexit 0\n")
    (worker / "script").chmod(0o751)
    (worker / ".gitignore").write_text("ignored/\n.pixi/\npixi.lock\n")
    (worker / "ignored").mkdir()
    (worker / "ignored/figure.bin").write_bytes(b"must not omit ignored data")
    (worker / ".pixi").mkdir()
    (worker / ".pixi/cached.bin").write_bytes(b"must not omit environment data")
    (worker / "pixi.lock").write_text("worker environment")
    (worker / "empty").mkdir(mode=0o700)
    (worker / "literal-link").symlink_to("ignored/figure.bin")
    (worker / "external-link").symlink_to("/outside/must/not/read")
    (worker / "dangling-link").symlink_to("../unavailable")
    (worker / "long-link").symlink_to("../" + "x" * 160)
    if git:
        # Minimal local metadata is sufficient for the frozen HEAD resolver.
        # Dirty and ignored bytes remain separate from this recorded identity.
        (worker / ".git/refs/heads").mkdir(parents=True)
        (worker / ".git/HEAD").write_text("ref: refs/heads/main\n")
        (worker / ".git/refs/heads/main").write_text("a" * 40 + "\n")
        (worker / ".git/index").write_bytes(b"staged index bytes\0\xff")
        (worker / ".git/config").write_text("[core]\n bare = false\n")
        (worker / "tracked-dirty.txt").write_text("dirty worktree bytes")
    if partial:
        (worker / ".ssh").mkdir()
        (worker / ".ssh/synthetic-secret").write_text("excluded fixture")
    evidence = tmp_path / "stopped"
    pointer = delivery.save_delivery(worker, evidence, {"returncode": 0, "stop_reason": "natural"})
    return worker, evidence, pointer


def retain(tmp_path, evidence, pointer, name="package"):
    return package.package_delivery(
        evidence / "original-delivery/manifest.json", evidence / "worker-end-state.json",
        pointer["capture"]["sha256"], pointer["sha256"], tmp_path / name,
        command=["synthetic-test", name])


def test_complete_dirty_untracked_ignored_git_bytes_and_modes(tmp_path):
    worker, evidence, pointer = stopped(tmp_path, git=True)
    before = package.inventory_capture(evidence / "original-delivery")
    result = retain(tmp_path, evidence, pointer)
    assert result["status"] == "packaged", result
    assert result["capture_status"] == "complete"
    assert result["complete_delivery_available"] is True
    assert result["worker_head_commit"] == "a" * 40
    assert result["coordinator_retention_commit"] is None
    assert package.inventory_capture(evidence / "original-delivery") == before
    output = tmp_path / "package"
    with tarfile.open(output / "delivery.tar.gz", "r:gz") as archive:
        assert archive.extractfile("original-delivery/content/workspace/.git/index").read() == (worker / ".git/index").read_bytes()
        assert archive.extractfile("original-delivery/content/workspace/tracked-dirty.txt").read() == b"dirty worktree bytes"
        assert archive.extractfile("original-delivery/content/workspace/ignored/figure.bin").read() == b"must not omit ignored data"
        assert archive.extractfile("original-delivery/content/workspace/.pixi/cached.bin").read() == b"must not omit environment data"
        assert archive.extractfile("original-delivery/manifest.json").read() == (evidence / "original-delivery/manifest.json").read_bytes()
        assert archive.extractfile("worker-end-state.json").read() == (evidence / "worker-end-state.json").read_bytes()
        assert archive.getmember("original-delivery/content/workspace/script").mode == 0o751
        assert archive.getmember("original-delivery/content/workspace/empty").mode == 0o700
    index = json.loads((output / "index.json").read_text())
    assert index["worker_head_commit"] == "a" * 40
    assert index["capture_sha256"] == pointer["capture"]["sha256"]
    assert index["coordinator_retention_commit"] is None
    names = {row["path"] for row in index["files"]}
    assert {"command.json", "result.json", "sources/package_delivery.py",
            "sources/delivery_snapshot.py", "verification.json", "delivery.tar.gz"} <= names
    for row in index["files"]:
        path = output / row["path"]
        assert hash_bytes(path.read_bytes()) == row["sha256"]
        assert path.stat().st_size == row["bytes"]
        assert stat.S_IMODE(path.stat().st_mode) == 0o444
    assert stat.S_IMODE((output / "index.json").stat().st_mode) == 0o444


def test_non_git_and_symlink_headers_remain_literal_without_extraction(tmp_path, monkeypatch):
    worker, evidence, pointer = stopped(tmp_path)
    def forbidden(*args, **kwargs):
        raise AssertionError("Archive verification must not extract paths")
    monkeypatch.setattr(tarfile.TarFile, "extract", forbidden)
    monkeypatch.setattr(tarfile.TarFile, "extractall", forbidden)
    result = retain(tmp_path, evidence, pointer)
    assert result["status"] == "packaged", result
    assert result["worker_head_commit"] is None
    with tarfile.open(tmp_path / "package/delivery.tar.gz", "r:gz") as archive:
        for name in ("literal-link", "external-link", "dangling-link", "long-link"):
            member = archive.getmember("original-delivery/content/workspace/" + name)
            assert member.issym()
            assert member.linkname == os.readlink(worker / name)
            assert member.mode == stat.S_IMODE((worker / name).lstat().st_mode)
    assert json.loads((tmp_path / "package/verification.json").read_text())["extracted"] is False


def test_partial_capture_is_packaged_but_never_claimed_complete(tmp_path):
    _, evidence, pointer = stopped(tmp_path, partial=True)
    assert pointer["capture_status"] == "partial"
    result = retain(tmp_path, evidence, pointer)
    assert result["status"] == "packaged", result
    assert result["capture_status"] == "partial"
    assert result["archive_verified"] is True
    assert result["complete_delivery_available"] is False
    assert result["ready_for_annex"] is True
    with tarfile.open(tmp_path / "package/delivery.tar.gz", "r:gz") as archive:
        assert not any("synthetic-secret" in item.name for item in archive)
        assert json.load(archive.extractfile("original-delivery/manifest.json"))["omissions"]


@pytest.mark.parametrize("change", ["bytes", "mode", "link", "extra", "missing", "receipt", "manifest"])
def test_tampered_sources_retain_error_record_and_no_archive(tmp_path, change):
    _, evidence, pointer = stopped(tmp_path)
    root = evidence / "original-delivery/content/workspace"
    if change == "bytes":
        (root / "result.txt").write_bytes(b"changed")
    elif change == "mode":
        (root / "script").chmod(0o700)
    elif change == "link":
        (root / "literal-link").unlink()
        (root / "literal-link").symlink_to("changed")
    elif change == "extra":
        (root / "extra").write_text("unexpected")
    elif change == "missing":
        (root / "result.txt").unlink()
    elif change == "receipt":
        (evidence / "worker-end-state.json").write_text("{}")
    else:
        (evidence / "original-delivery/manifest.json").write_text("{}")
    result = retain(tmp_path, evidence, pointer)
    assert result["status"] == "error"
    assert result["errors"]
    assert result["archive_verified"] is False
    assert result["complete_delivery_available"] is False
    assert result["ready_for_annex"] is False
    assert not (tmp_path / "package/delivery.tar.gz").exists()
    assert (tmp_path / "package/index.json").exists()


def test_absent_capture_preserves_error_and_stop_receipt(tmp_path):
    evidence = tmp_path / "absent"
    evidence.mkdir()
    (evidence / "worker-end-state.json").write_text("{}")
    pointer = {"capture": {"sha256": "0" * 64}, "sha256": hash_bytes(b"{}")}
    result = retain(tmp_path, evidence, pointer)
    assert result["status"] == "error"
    assert result["errors"][0]["stage"] == "frozen capture validation"
    assert (tmp_path / "package/worker-end-state.json").read_bytes() == b"{}"
    index = json.loads((tmp_path / "package/index.json").read_text())
    assert index["capture_sha256"] is None
    assert index["expected_capture_sha256"] == "0" * 64


def test_receipt_must_bind_original_head_and_capture(tmp_path):
    _, evidence, pointer = stopped(tmp_path)
    receipt_path = evidence / "worker-end-state.json"
    receipt = json.loads(receipt_path.read_text())
    receipt["head_commit"] = "b" * 40
    receipt_path.write_text(json.dumps(receipt))
    pointer["sha256"] = hash_bytes(receipt_path.read_bytes())
    result = retain(tmp_path, evidence, pointer)
    assert result["status"] == "error"
    assert "head_commit" in result["errors"][0]["message"]


def test_frozen_validator_identity_is_required(tmp_path, monkeypatch):
    _, evidence, pointer = stopped(tmp_path)
    monkeypatch.setattr(package, "VALIDATOR_SHA256", "0" * 64)
    result = retain(tmp_path, evidence, pointer)
    assert result["status"] == "error"
    assert "validator source SHA256" in result["errors"][0]["message"]


def test_existing_output_is_not_overwritten(tmp_path):
    _, evidence, pointer = stopped(tmp_path)
    retain(tmp_path, evidence, pointer)
    before = (tmp_path / "package/index.json").read_bytes()
    with pytest.raises(FileExistsError):
        retain(tmp_path, evidence, pointer)
    assert (tmp_path / "package/index.json").read_bytes() == before


@pytest.mark.parametrize("change", ["bytes", "mode", "link", "extra", "missing", "duplicate", "hardlink", "escape"])
def test_independent_verifier_rejects_archive_tampering(tmp_path, change):
    _, evidence, pointer = stopped(tmp_path)
    result = retain(tmp_path, evidence, pointer)
    assert result["status"] == "packaged", result
    output = tmp_path / "package"
    rows = json.loads((output / "archive-inventory.json").read_text())
    path = tmp_path / "tampered.tar.gz"
    selected = "original-delivery/content/workspace/result.txt"
    with tarfile.open(output / "delivery.tar.gz", "r:gz") as original, tarfile.open(path, "w:gz") as altered:
        for member in original:
            data = original.extractfile(member).read() if member.isfile() else None
            if member.name == selected:
                if change == "missing":
                    continue
                if change == "bytes":
                    data = b"x" * len(data)
                elif change == "mode":
                    member.mode ^= 0o100
                elif change == "hardlink":
                    member.type, member.linkname, member.size = tarfile.LNKTYPE, "outside", 0
                    data = None
                elif change == "escape":
                    member.name = "../escaped"
            if change == "link" and member.issym():
                member.linkname = "changed"
            altered.addfile(member, io.BytesIO(data) if data is not None else None)
            if change == "duplicate" and member.name == selected:
                altered.addfile(member, io.BytesIO(data))
        if change == "extra":
            altered.addfile(tarfile.TarInfo("extra"), io.BytesIO(b""))
    with pytest.raises(ValueError, match="mismatch|member"):
        package.verify_archive(path, rows, pointer["capture"]["sha256"], pointer["sha256"])


def test_partial_archive_is_retained_after_write_failure(tmp_path, monkeypatch):
    _, evidence, pointer = stopped(tmp_path)
    def interrupted(path, *args):
        path.write_bytes(b"interrupted archive")
        raise OSError("synthetic disk failure")
    monkeypatch.setattr(package, "write_archive", interrupted)
    result = retain(tmp_path, evidence, pointer)
    assert result["status"] == "error"
    assert result["archive_verified"] is False
    assert (tmp_path / "package/delivery.tar.gz").read_bytes() == b"interrupted archive"
    assert result["errors"][0]["stage"] == "archive creation"


def test_gzip_footer_is_verified(tmp_path):
    _, evidence, pointer = stopped(tmp_path)
    assert retain(tmp_path, evidence, pointer)["status"] == "packaged"
    output = tmp_path / "package"
    content = bytearray((output / "delivery.tar.gz").read_bytes())
    content[-8] ^= 0x01  # Change gzip CRC while preserving the complete tar body.
    damaged = tmp_path / "bad-crc.tar.gz"
    damaged.write_bytes(content)
    with pytest.raises(OSError, match="CRC"):
        package.verify_archive(damaged, json.loads((output / "archive-inventory.json").read_text()),
                               pointer["capture"]["sha256"], pointer["sha256"])


def test_source_change_after_archive_write_cannot_claim_verified_package(tmp_path, monkeypatch):
    _, evidence, pointer = stopped(tmp_path)
    original = package.write_archive
    def mutate_after_write(*args):
        original(*args)
        (evidence / "original-delivery/content/workspace/result.txt").write_bytes(b"late change")
    monkeypatch.setattr(package, "write_archive", mutate_after_write)
    result = retain(tmp_path, evidence, pointer)
    assert result["status"] == "error"
    assert result["archive_verified"] is False
    assert result["errors"][0]["stage"] == "final source verification"
    assert (tmp_path / "package/delivery.tar.gz").exists()


def test_cli_success_and_retained_error_exit_codes(tmp_path):
    _, evidence, pointer = stopped(tmp_path)
    command = [sys.executable, str(Path(package.__file__)), "--capture",
               str(evidence / "original-delivery/manifest.json"), "--end-state",
               str(evidence / "worker-end-state.json"), "--expected-capture-sha256",
               pointer["capture"]["sha256"], "--expected-end-state-sha256", pointer["sha256"]]
    good = subprocess.run(command + ["--output", str(tmp_path / "cli-good")], capture_output=True, text=True)
    assert good.returncode == 0, good.stderr
    assert json.loads(good.stdout)["status"] == "packaged"
    (evidence / "original-delivery/content/workspace/result.txt").unlink()
    bad = subprocess.run(command + ["--output", str(tmp_path / "cli-error")], capture_output=True, text=True)
    assert bad.returncode == 1, bad.stderr
    assert json.loads(bad.stdout)["status"] == "error"
    assert (tmp_path / "cli-error/index.json").exists()
