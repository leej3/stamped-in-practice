"""Verify that linked checklist views retain the scored primary responses."""
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
from urllib.parse import parse_qs, urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import export_poster_checklists as exporter

EXPORT = ROOT / exporter.EXPORT


def test_response_bytes_scores_and_generated_links_match_originals():
    index = json.loads((EXPORT / "index.json").read_text())
    assert len(index["runs"]) == 72 and len({r["run_id"] for r in index["runs"]}) == 72
    assert sum(row["checklist_valid"] for row in index["runs"]) == 68
    expected = {"met": "yes", "partial": "no", "unmet": "no", "not-checked": None, "not-applicable": None}
    for number in (1, 2, 3):
        group = [row for row in index["runs"] if row["round"] == number]
        source = group[0]["source"]["archive"]
        archive_path = ROOT / source["path"]
        assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == source["sha256"]
        with tarfile.open(archive_path) as archive:
            for row in group:
                raw = (ROOT / row["raw_response_path"]).read_bytes()
                assert raw == archive.extractfile(row["source"]["member_path"]).read()
                assert hashlib.sha256(raw).hexdigest() == row["response_sha256"]
                response = json.loads(raw)
                counts = Counter(a["status"] for a in response["responses"].values())
                assert row["status_counts"] == dict(counts)
                if not row["checklist_valid"]:
                    assert row["app_url"] is row["evaluated_met_percent"] is row["app_all_items_met_percent"] is None
                    assert row["app_projection"] is None
                    assert row["exclusion_reasons"]
                    continue
                url = urlparse(row["app_url"])
                assert url.scheme == "https" and url.netloc == "checklist.stamped-principles.org"
                params = parse_qs(url.query)
                assert params["checklist"] == params["responses_version"] == ["0.3.1"]
                payload = json.loads(base64.b64decode(params["responses"][0]))
                assert len(payload["responses"]) == row["all_item_count"] == 31
                assert len(row["app_url"].encode()) <= exporter.MAX_APP_URL_BYTES
                for key, answer in response["responses"].items():
                    value = expected[answer["status"]]
                    reason = "" if row["app_projection"]["undisplayed_reasons_omitted"] and value != "no" else answer["reason"][:250]
                    assert payload["responses"][key] == {"value": value, "reason": reason}
                assert row["evaluated_met_percent"] == pytest.approx(100 * counts["met"] / (counts["met"] + counts["partial"] + counts["unmet"]))
                assert row["app_all_items_met_percent"] == pytest.approx(100 * counts["met"] / 31)
                # This original retained URL was stale; the canonical response is authoritative.
                if row["run_id"] == "narps-neutral-r1-08":
                    assert payload["responses"]["stamped-checklist:must/005"]["value"] == "no"
    assert [row["run_id"] for row in index["runs"] if row["app_projection"] and row["app_projection"]["undisplayed_reasons_omitted"]] == ["narps-neutral-r2-08"]
    for condition in index["conditions"]:
        valid = [r for r in index["runs"] if r["condition"] == condition["condition"] and r["checklist_valid"]]
        assert condition["checklist_n"] == len(valid)
        assert condition["app_all_items_mean_met_percent"] == pytest.approx(100 * sum(r["met_count"] for r in valid) / (31 * len(valid)))


def test_replay_retains_all_response_bytes_and_export_bindings(tmp_path):
    subprocess.run([sys.executable, str(ROOT / "scripts/export_poster_checklists.py"), "--output", str(tmp_path)], check=True)
    for path in EXPORT.rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (tmp_path / path.relative_to(EXPORT)).read_bytes()
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    for row in manifest["outputs"]:
        data = (ROOT / row["path"]).read_bytes()
        assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"]
    assert manifest["encoder"]["commit"] == exporter.ENCODER_COMMIT


def test_archive_mismatch_stops_before_export(tmp_path):
    reporting = tmp_path / "reporting"
    (reporting / "pooled").mkdir(parents=True)
    (reporting / "pooled/run-outcomes.json").symlink_to(ROOT / exporter.REPORTING / "pooled/run-outcomes.json")
    folder = reporting / "round-01"
    folder.mkdir()
    (folder / "input.tar.gz").symlink_to(ROOT / exporter.REPORTING / "round-01/input.tar.gz")
    identity = json.loads((ROOT / exporter.REPORTING / "round-01/input.json").read_text())
    identity["archive"]["sha256"] = "0" * 64
    (folder / "input.json").write_text(json.dumps(identity))
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="Archive identity mismatch"):
        exporter.export(reporting, ROOT / "assessment", output)
    assert not output.exists()
