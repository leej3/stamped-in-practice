"""Scientific reporting invariants: missingness, primary labels and run weights."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("poster_outcomes", Path(__file__).parents[1] / "scripts/summarize_poster_outcomes.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def fixture():
    run = {"run_id": "r2-01", "round": 2, "condition": "baseline", "worker_completion": "completed", "delivery_capture": {"sha256": "a" * 64}}
    primary = {"run_id": "r2-01", "round": 2, "role": "primary", "judgment_id": "r2-01-j01", "inclusion_status": "eligible", "response_status": "valid", "adequacy": "qualified"}
    items = [{"run_id": "r2-01", "role": "primary", "judgment_id": "r2-01-j01", "item_id": str(i), "status": "met" if i < 10 else "not-checked"} for i in range(31)]
    audit = {"kind": "final-native-replay-evidence-audit", "interim": False, "helper_completions": [{"judgment_id": "r2-01-j01", "native_binding": "same-event", "helper_record": {"path": "helper.json", "sha256": "c" * 64}, "binding_receipt": {"path": "binding.json", "sha256": "d" * 64}, "capture_sha256": "a" * 64, "entrypoint_returncode": 0, "reported_comparison": {"identical": ["result.tsv"], "differing": [], "missing_after_rerun": []}}]}
    return run, primary, items, audit


def test_duplicate_never_replaces_unavailable_primary():
    run, primary, items, audit = fixture()
    primary["inclusion_status"] = "invalid"
    duplicate = {**primary, "judgment_id": "r2-01-j02", "role": "duplicate", "inclusion_status": "eligible", "adequacy": "supported"}
    rows = report.summarize_round(2, [run], [primary, duplicate], items, [audit])
    assert rows[0]["science"] is None
    assert rows[0]["checklist_met_fraction"] is None
    assert rows[0]["raw_native_replay_matched"]
    assert not rows[0]["native_replay_matched"]
    summary = report.summarize(rows)[0]
    assert summary["assigned_runs"] == 1
    assert summary["scientific_n"] == 0
    assert summary["scientific_unavailable"] == 1


def test_invalid_checklist_does_not_erase_valid_science():
    run, primary, items, audit = fixture()
    primary["response_status"] = "invalid"
    rows = report.summarize_round(2, [run], [primary], [], [audit])
    assert rows[0]["science"] == "qualified"
    assert rows[0]["checklist_met_fraction"] is None
    assert rows[0]["native_replay_matched"]


def test_equal_run_weights_and_unknown_items_not_scored_as_failures():
    run, primary, items, audit = fixture()
    first = report.summarize_round(2, [run], [primary], items, [audit])[0]
    assert first["checklist_evaluated_items"] == 10
    assert first["checklist_status_counts"]["not-checked"] == 21
    second = {**first, "run_id": "r2-02", "checklist_evaluated_items": 30, "checklist_met_fraction": 0.0}
    assert report.summarize([first, second])[0]["checklist_mean_met_percent"] == 50


def test_native_execution_is_not_automatically_an_output_match():
    run, primary, items, audit = fixture()
    audit["helper_completions"][0]["reported_comparison"]["differing"] = ["result.tsv"]
    row = report.summarize_round(2, [run], [primary], items, [audit])[0]
    assert row["native_replay_executed"]
    assert not row["native_replay_matched"]


def test_replay_from_another_delivery_is_rejected():
    run, primary, items, audit = fixture()
    audit["helper_completions"][0]["capture_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="different original capture"):
        report.summarize_round(2, [run], [primary], items, [audit])


def test_native_replay_requires_recorded_event_binding():
    run, primary, items, audit = fixture()
    audit["helper_completions"][0].pop("binding_receipt")
    with pytest.raises(ValueError, match="native binding"):
        report.summarize_round(2, [run], [primary], items, [audit])


def test_partial_output_matches_remain_distinct():
    run, primary, items, audit = fixture()
    audit["helper_completions"][0]["reported_comparison"]["differing"] = ["execution-time.txt"]
    rows = report.summarize_round(2, [run], [primary], items, [audit])
    summary = report.summarize(rows)[0]
    assert summary["replay_executed_n"] == 1
    assert summary["replay_matched_n"] == 0
    assert summary["replay_partial_selected_output_match_n"] == 1
    assert summary["checklist_evaluated_items_mean"] == 10


@pytest.mark.parametrize("audit_kind", ["final", "extraction"])
def test_failed_entrypoint_with_null_comparison_remains_observed(audit_kind):
    run, primary, items, audit = fixture()
    row = audit["helper_completions"][0]
    row.update(entrypoint_returncode=1, reported_comparison=None)
    if audit_kind == "extraction":
        audit = {"kind": "native-replay-evidence-extraction", "rows": [{
            "judgment_id": row["judgment_id"], "status": "native-helper-output-bound",
            "native_helper_completion_observed": True, "entrypoint_execution_observed": True,
            "entrypoint_returncode": 1, "literal_comparison": None,
            "supporting_record": {"judgment_id": row["judgment_id"],
                "capture_matches_original": True, "reported_capture_sha256": row["capture_sha256"]},
            "matched_native_events": [row["binding_receipt"]], "evidence": row["binding_receipt"],
        }]}
    rows = report.summarize_round(2, [run], [primary], items, [audit])
    assert rows[0]["native_replay_executed"]
    assert not rows[0]["native_replay_matched"]
    summary = report.summarize(rows)[0]
    assert summary["replay_executed_n"] == 1
    assert summary["replay_matched_n"] == 0
    assert summary["replay_partial_selected_output_match_n"] == 0
    assert summary["replay_execution_unobserved_or_unavailable"] == 0
    assert summary["scientific_n"] == 1


def test_malformed_comparison_is_not_silently_treated_as_missing():
    _, _, _, audit = fixture()
    audit["helper_completions"][0]["reported_comparison"] = []
    with pytest.raises(ValueError, match="comparison must be an object or null"):
        list(report.replay_records(audit))
