from pathlib import Path
import json
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from render_round_summary import read_skill_observations, select_round, token_rows


def test_round_selection_keeps_assigned_missing_slots_and_exact_grades():
    tables = {"runs": [{"run_id": "a", "round": 1}, {"run_id": "b", "round": 2}],
              "judgments": [{"run_id": "a", "response_status": "missing"}, {"run_id": "b"}],
              "items": [{"run_id": "a", "status": "unmet"}, {"run_id": "b", "status": "met"}],
              "cells": [{"round": 1, "count": 0}, {"round": 2, "count": 1}]}
    selected = select_round(tables, 1)
    assert selected["judgments"] == [{"run_id": "a", "response_status": "missing"}]
    assert selected["items"] == [{"run_id": "a", "status": "unmet"}]
    assert selected["cells"] == [{"round": 1, "count": 0}]
    assert len(tables["runs"]) == 2


def test_unscoped_nonempty_rows_are_not_silently_pooled():
    with pytest.raises(ValueError, match="Cannot scope"):
        select_round({"runs": [{"run_id": "a", "round": 1}], "other": [{"count": 9}]}, 1)


def operation():
    return {"run_id": "a", "condition": "baseline", "stage": "worker", "evidence_status": "valid",
            "operation_id": "a-native", "evidence": [], "metrics": [
                {"name": key, "value": value, "unit": "tokens", "scope": "parent only"}
                for key, value in [("input_tokens", 100), ("cached_input_tokens", 80),
                                   ("output_tokens", 20), ("reasoning_output_tokens", 10)]]}


def test_subsets_are_preserved_without_addition_and_missing_metrics_omitted():
    row = operation()
    assert token_rows({"operations": [row]})[0]["values"]["input_tokens"] == 100
    row["metrics"].pop()
    assert token_rows({"operations": [row]}) == []


def test_invalid_subsets_and_duplicate_sessions_reject():
    row = operation()
    with pytest.raises(ValueError, match="Multiple worker"):
        token_rows({"operations": [row, row]})
    row["metrics"][1]["value"] = 101
    with pytest.raises(ValueError, match="Invalid subset"):
        token_rows({"operations": [row]})


def test_skill_records_exclude_inventory_and_bind_condition(tmp_path):
    record = {"kind": "coordinator-skill-use-observations", "run_id": "a",
              "assigned_condition": "baseline", "observations": {
                  "discovery": False, "installation": False, "loaded": False}}
    path = tmp_path / "a.json"
    path.write_text(json.dumps(record))
    (tmp_path / "manifest.json").write_text('{"files": []}')
    tables = {"runs": [{"run_id": "a", "condition": "baseline"}]}
    rows = read_skill_observations(tmp_path, tables)
    assert len(rows) == 1 and rows[0]["observations"]["loaded"] is False
    record["assigned_condition"] = "stamped-explicit"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="mismatched"):
        read_skill_observations(tmp_path, tables)
