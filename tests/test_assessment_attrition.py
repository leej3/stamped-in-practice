import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from render_assessment_attrition import CONDITIONS, classify, counts


def rows():
    return [{"judgment_id": f"{c}-{i}", "condition": c,
             "role": "primary" if i < 6 else "duplicate", "availability": "usable"}
            for c in CONDITIONS for i in range(8)]


def test_all_assigned_roles_and_missing_measurements_remain_in_denominators():
    data = rows()
    data[0]["availability"] = "metadata-unavailable"
    result = counts(data)
    assert result["baseline"] == {"usable": 7, "metadata-unavailable": 1}
    with pytest.raises(ValueError, match="32 distinct"):
        counts(data[:-1])
    data[0]["role"] = "duplicate"
    with pytest.raises(ValueError, match="denominators"):
        counts(data)


def test_metadata_label_requires_exact_bound_paths_and_does_not_change_admission():
    record = {"response_status": "invalid", "provenance_error":
              "Malformed provenance: target_unchanged: True was expected",
              "delivery_capture": {"sha256": "a" * 64}}
    delta = {"baseline_manifest_sha256": "a" * 64,
             "baseline_manifest_bytes_identical_to_original_worker_capture_manifest": True,
             "added": [], "missing": [],
             "modified": [{"path": "content/workspace/.git/annex/keysdb/db"}]}
    assert classify(record, delta) == "metadata-unavailable"
    assert record["response_status"] == "invalid"
    delta["added"].append({"path": "content/workspace/science.csv"})
    assert classify(record, delta) == "other-unavailable"
    delta["added"] = []
    delta["baseline_manifest_sha256"] = "b" * 64
    assert classify(record, delta) == "other-unavailable"


def test_pending_assessments_are_not_treated_as_failures():
    with pytest.raises(ValueError, match="not complete"):
        classify({"response_status": "pending"})
