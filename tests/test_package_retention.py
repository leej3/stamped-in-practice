import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "packager", Path(__file__).parents[1] / "scripts/package_retention.py")
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


@pytest.fixture
def fixture(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "stop.json").write_text(json.dumps({
        "capture_status": "complete", "errors": [], "head_commit": "a" * 40,
        "worktree": [{"path": "logs/runstdout", "sha256": "b" * 64}]}))
    (source / "failed-attempt").mkdir()
    (source / "failed-attempt/stderr").write_bytes(b"failed\n\x00raw")
    (source / "proof.json").write_text('{"matched":true}\n')
    (source / "recipient").mkdir()
    (source / "recipient/cache").write_bytes(b"reconstructable")
    plan = {"version": 1, "source": str(source), "worker_stop": "stop.json",
            "scientific_result": "a" * 40, "exclude": [{
                "path": "recipient", "reason": "Verified independent recipient",
                "reconstruct_from": {"result_commit": "a" * 40},
                "evidence": ["proof.json"]}]}
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan))
    return source, plan, plan_path, tmp_path / "package"


def test_preserves_failed_attempts_links_and_proofs(fixture):
    source, _, path, output = fixture
    (source / "missing-annex").symlink_to("/missing/annex/key")
    result = packager.package(path, output)
    assert result["status"] == "verified"
    assert (output / "evidence/failed-attempt/stderr").read_bytes() == b"failed\n\x00raw"
    assert not (output / "evidence/recipient").exists()
    assert (output / "evidence/proof.json").read_bytes() == (source / "proof.json").read_bytes()
    assert (output / "evidence/missing-annex").readlink() == Path("/missing/annex/key")
    assert result["scientific_object"]["artifact_count"] == 1
    assert (output / "package-plan.json").read_bytes() == path.read_bytes()


@pytest.mark.parametrize("mutation", ["no-proof", "excluded-proof", "wrong-result", "incomplete-stop", "traversal"])
def test_rejects_incomplete_or_inconsistent_plans(fixture, mutation):
    source, plan, path, output = fixture
    if mutation == "no-proof":
        plan["exclude"][0]["evidence"] = []
    elif mutation == "excluded-proof":
        plan["exclude"][0]["evidence"] = ["recipient/cache"]
    elif mutation == "wrong-result":
        plan["scientific_result"] = "b" * 40
    elif mutation == "incomplete-stop":
        stop = json.loads((source / "stop.json").read_text())
        stop["capture_status"] = "incomplete"
        (source / "stop.json").write_text(json.dumps(stop))
    else:
        plan["exclude"][0]["path"] = "../elsewhere"
    path.write_text(json.dumps(plan))
    with pytest.raises(ValueError):
        packager.package(path, output)
    assert not output.exists()


def test_detects_source_change_and_retains_failed_copy(fixture, monkeypatch):
    source, _, path, output = fixture
    original = packager.shutil.copyfile
    def change(src, dst):
        result = original(src, dst)
        if Path(src).name == "stderr":
            (source / "new-attempt.txt").write_text("arrived during copy")
        return result
    monkeypatch.setattr(packager.shutil, "copyfile", change)
    with pytest.raises(ValueError, match="changed during packaging"):
        packager.package(path, output)
    assert (output / "package-failure.json").is_file()
    assert not (output / "package-manifest.json").exists()


def test_rejects_in_place_output_and_preserves_existing_package(fixture):
    source, _, path, output = fixture
    with pytest.raises(ValueError, match="outside"):
        packager.package(path, source / "package")
    packager.package(path, output)
    with pytest.raises(ValueError, match="new directory"):
        packager.package(path, output)


def test_traversal_error_cannot_be_verified_as_missing_subtree(fixture, monkeypatch):
    source, _, path, output = fixture
    original = packager.os.scandir
    def denied(directory):
        if Path(directory).name == "failed-attempt":
            raise PermissionError("simulated unreadable evidence directory")
        return original(directory)
    monkeypatch.setattr(packager.os, "scandir", denied)
    with pytest.raises(PermissionError):
        packager.package(path, output)
    assert not output.exists()


@pytest.mark.parametrize("item", ["proof", "stop"])
def test_required_evidence_cannot_hide_behind_symlink_ancestor(fixture, item):
    source, plan, path, output = fixture
    external = source.parent / "external"
    external.mkdir()
    (external / "proof.json").write_text('{"matched":true}')
    (external / "stop.json").write_bytes((source / "stop.json").read_bytes())
    (source / "linked").symlink_to(external, target_is_directory=True)
    if item == "proof":
        plan["exclude"][0]["evidence"] = ["linked/proof.json"]
    else:
        plan["worker_stop"] = "linked/stop.json"
    path.write_text(json.dumps(plan))
    with pytest.raises(ValueError, match="included regular files"):
        packager.package(path, output)
    assert not output.exists()
