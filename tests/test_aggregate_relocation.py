"""Retained artifact copies must preserve identity without consulting old paths."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import aggregate_comparison as agg


@pytest.fixture
def retained(tmp_path):
    raw = b"original receipt\n"
    copy = tmp_path / "copy.json"
    copy.write_bytes(raw)
    original = tmp_path / "old-host" / "receipt.json"
    reference = {"path": str(original), "sha256": agg.sha256(raw)}
    rows = [{"source_path": str(original), "sha256": agg.sha256(raw),
             "bytes": len(raw), "copy": {"path": copy.name, "sha256": agg.sha256(raw)}}]
    manifest = tmp_path / "source-manifest.json"
    return raw, reference, rows, manifest


@pytest.mark.parametrize("old_path_exists", [False, True])
def test_relocation_uses_exact_copy_even_if_original_exists(retained, old_path_exists):
    raw, reference, rows, manifest = retained
    original = Path(reference["path"])
    if old_path_exists:
        original.parent.mkdir()
        original.write_bytes(b"unrelated bytes at the old location")
    manifest.write_text(json.dumps(rows + rows))
    locations, provenance = agg.source_locations(manifest)
    assert provenance["mapped_paths"] == 1
    assert provenance["manifest_sha256"] == agg.sha256(manifest.read_bytes())
    token = agg.ARTIFACT_LOCATIONS.set(locations)
    try:
        assert agg.artifact(reference, manifest.parent) == raw
        assert agg.artifact(rows[0]["copy"], manifest.parent) == raw
        with pytest.raises(ValueError, match="relocated artifact identity"):
            agg.artifact(dict(reference, sha256="0" * 64), manifest.parent)
        (manifest.parent / "copy.json").write_bytes(b"changed after manifest validation")
        with pytest.raises(ValueError, match="SHA-256 mismatch"):
            agg.artifact(reference, manifest.parent)
    finally:
        agg.ARTIFACT_LOCATIONS.reset(token)


@pytest.mark.parametrize("mutation,match", [
    (lambda rows: rows[0].update(source_path="relative.json"), "absolute original"),
    (lambda rows: rows[0]["copy"].update(path="/absolute-copy.json"), "relative retained-copy"),
    (lambda rows: rows[0].update(sha256="0" * 64), "retained copy identity"),
    (lambda rows: rows[0]["copy"].update(sha256="0" * 64), "retained copy identity"),
])
def test_invalid_manifest_rejected(retained, mutation, match):
    _, _, rows, manifest = retained
    mutation(rows)
    manifest.write_text(json.dumps(rows))
    with pytest.raises(ValueError, match=match):
        agg.source_locations(manifest)


def test_duplicate_source_cannot_select_different_bytes(retained):
    _, _, rows, manifest = retained
    other = b"other receipt"
    (manifest.parent / "other.json").write_bytes(other)
    rows.append(dict(rows[0], sha256=agg.sha256(other),
                     copy={"path": "other.json", "sha256": agg.sha256(other)}))
    manifest.write_text(json.dumps(rows))
    with pytest.raises(ValueError, match="unique source identity"):
        agg.source_locations(manifest)


def test_explicit_map_never_falls_back_to_existing_absolute_path(retained):
    raw, _, rows, manifest = retained
    reference = dict(rows[0]["copy"], path=str(manifest.parent / "copy.json"))
    assert agg.artifact(reference, manifest.parent) == raw
    token = agg.ARTIFACT_LOCATIONS.set({})
    try:
        with pytest.raises(ValueError, match="missing from source manifest"):
            agg.artifact(reference, manifest.parent)
    finally:
        agg.ARTIFACT_LOCATIONS.reset(token)


def test_main_restores_context_after_failure(retained):
    _, _, rows, manifest = retained
    manifest.write_text(json.dumps(rows))
    sentinel = {"outer-context": {}}
    token = agg.ARTIFACT_LOCATIONS.set(sentinel)
    try:
        with pytest.raises(SystemExit) as failure:
            agg.main(["--allocation", str(manifest.parent / "missing.json"),
                      "--index", str(manifest), "--output", str(manifest.parent / "output"),
                      "--source-manifest", str(manifest)])
        assert failure.value.code == 2
        assert agg.ARTIFACT_LOCATIONS.get() is sentinel
    finally:
        agg.ARTIFACT_LOCATIONS.reset(token)
