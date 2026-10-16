"""Synthetic coordinator fixtures; never read formal worker results."""
import json
import os
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import aggregate_comparison as agg

RESULT = "a" * 40


@pytest.fixture
def allocation():
    return agg.parse_json((ROOT / "iterations/narps-v1/allocation.json").read_bytes())


@pytest.fixture
def contract():
    # Synthetic item text with the pinned mapping; no scientific answer fixtures.
    mapping = {
        "must": [("S.1",)] * 3 + [("T.1", "T.3", "T.5")] * 3 + [("A.1",)] * 2 +
                [("P.1",)] * 3 + [("P.2",)] + [("P.3",)] * 2 + [("D.1",)] * 3,
        "should": [("T.2",), ("A.2",), ("M.1",), ("E.1",), ("E.1",),
                   ("D.2",), ("D.2",), ("D.2",), ("M.4",)],
        "may": [("M.2",)] * 5,
    }
    items = [dict(id=f"stamped-checklist:{level}/{n:03d}", text="Synthetic item",
                  level=level, principle_codes=list(codes),
                  dimension=sorted({c[0] for c in codes}))
             for level, entries in mapping.items() for n, codes in enumerate(entries, 1)]
    schema = {"type": "object", "required": ["responses", "object", "checklist_source"],
              "properties": {
                  "responses": {"type": "object", "additionalProperties": {
                      "type": "object", "properties": {"evidence": {"type": "array",
                          "items": {"type": "object", "required": ["uri"]}}}}},
                  "object": {"type": "object"}, "checklist_source": {"type": "object"}}}
    lock = dict(checklist_version="0.3.1", schema_version="0.2.0", principles_version="0.2.0",
                source=dict(repo="fixture", tag="fixture", commit="b" * 40))
    return agg.Contract(items, schema, lock)


def response(contract, status="met"):
    result = {k: contract.lock[k] for k in ("checklist_version", "schema_version", "principles_version")}
    result.update(checklist_source=contract.lock["source"], object={"commit": RESULT},
        responses={i["id"]: {"status": status, "reason": "Synthetic evidence",
            "source": "judgement", "evidence": [{"uri": "fixture.txt"}], "flags": ["fixture"]}
                   for i in contract.items})
    return result


def artifact(tmp_path, name, content):
    raw = content.encode() if isinstance(content, str) else json.dumps(content).encode()
    path = tmp_path / name
    path.write_bytes(raw)
    return {"path": name, "sha256": agg.sha256(raw)}


def indexed_run(tmp_path, allocation, contract, duplicate=False):
    run_id = allocation["rounds"][0]["duplicate_judgments"][0]
    record = {"run_id": run_id, "result_commit": RESULT,
              "judgments": {"primary": {"judgment_id": "fixture-primary",
                  "response": artifact(tmp_path, "primary.json", response(contract))}}}
    if duplicate:
        record["judgments"]["duplicate"] = {
            "judgment_id": "fixture-duplicate",
            "response": artifact(tmp_path, "duplicate.json", response(contract))}
    return record


def collect(allocation, contract, tmp_path, *records):
    return agg.aggregate(allocation, {"schema_version": 1, "runs": list(records)}, tmp_path, contract)


def test_empty_index_retains_all_assignments_and_missing_denominators(allocation, contract, tmp_path):
    result = collect(allocation, contract, tmp_path)
    assert len(result["runs"]) == 36
    assert len(result["judgments"]) == 48
    assert len(result["pairs"]) == 12
    assert result["items"] == result["counts"] == result["issues"] == []
    assert all(j["response_status"] == "pending" for j in result["judgments"])
    assert all(c["n_assigned"] == 3 and c["n_valid_primary"] == 0 for c in result["cells"])
    assert all(c["median"] is None for c in result["cells"] if "median" in c)
    assert sum(c["count"] for c in result["cells"] if c["group"] == "missing") == 36


@pytest.mark.parametrize("text", ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":1e999}', '{'])
def test_json_rejects_ambiguous_or_nonfinite_data(text):
    with pytest.raises(ValueError):
        agg.parse_json(text)


def test_assignment_cannot_be_relabelled_or_duplicate_added(allocation, contract, tmp_path):
    record = indexed_run(tmp_path, allocation, contract)
    record["condition"] = "baseline"
    with pytest.raises(ValueError, match="Invalid extraction index"):
        collect(allocation, contract, tmp_path, record)
    del record["condition"]
    with pytest.raises(ValueError, match="repeated indexed run"):
        collect(allocation, contract, tmp_path, record, record)
    record["run_id"] = next(r["run"] for r in allocation["rounds"][0]["launch_order"]
                            if r["run"] not in allocation["rounds"][0]["duplicate_judgments"])
    record["judgments"]["duplicate"] = {"judgment_id": "not-selected"}
    with pytest.raises(ValueError, match="not preselected"):
        collect(allocation, contract, tmp_path, record)


@pytest.mark.parametrize("mutation", [
    lambda r: r["object"].update(commit="c" * 40),
    lambda r: r["responses"].pop("stamped-checklist:must/001"),
    lambda r: r["responses"].update({"unknown": {}}),
    lambda r: r["responses"]["stamped-checklist:must/001"].update(status="yes"),
    lambda r: r["responses"]["stamped-checklist:must/001"].update(value="no"),
    lambda r: r["responses"]["stamped-checklist:must/001"].update(evidence=[]),
    lambda r: r["responses"]["stamped-checklist:must/001"].update(reason="No probe covers this item"),
    lambda r: r.update(checklist_version="wrong"),
    lambda r: r.update(responses=[]),
])
def test_invalid_response_is_reported_without_fabricating_items(allocation, contract, tmp_path, mutation):
    record = indexed_run(tmp_path, allocation, contract)
    value = response(contract)
    mutation(value)
    record["judgments"]["primary"]["response"] = artifact(tmp_path, "primary.json", value)
    result = collect(allocation, contract, tmp_path, record)
    assert result["items"] == result["counts"] == []
    assert len(result["issues"]) == 1
    assert result["judgments"][next(i for i, j in enumerate(result["judgments"])
                                   if j["judgment_id"] == "fixture-primary")]["response_status"] == "invalid"


@pytest.mark.parametrize("value", [None, [], 1, "string"])
def test_malformed_response_roots_become_issues(allocation, contract, tmp_path, value):
    record = indexed_run(tmp_path, allocation, contract)
    record["judgments"]["primary"]["response"] = artifact(tmp_path, "bad.json", value)
    result = collect(allocation, contract, tmp_path, record)
    assert len(result["issues"]) == 1


def test_five_statuses_dimensions_and_na_are_kept(allocation, contract, tmp_path):
    record = indexed_run(tmp_path, allocation, contract)
    data = response(contract, "not-applicable")
    record["judgments"]["primary"]["response"] = artifact(tmp_path, "primary.json", data)
    result = collect(allocation, contract, tmp_path, record)
    assert len(result["items"]) == 31
    dimensions = {r["group"]: r["n_pinned"] for r in result["counts"] if r["group_type"] == "dimension"}
    assert dimensions == dict(zip("STAMPED", [3, 4, 3, 7, 6, 2, 6]))
    assert all(r["n_applicable"] == 0 for r in result["counts"])
    assert sum(r["not-applicable"] for r in result["counts"] if r["group_type"] == "level") == 31
    for n, answer in enumerate(data["responses"].values()):
        answer["status"] = agg.STATUSES[n % 5]
    record["judgments"]["primary"]["response"] = artifact(tmp_path, "primary.json", data)
    result = collect(allocation, contract, tmp_path, record)
    assert {r["status"] for r in result["items"]} == set(agg.STATUSES)
    assert all(sum(r[s] for s in agg.STATUSES) == r["n_pinned"] for r in result["counts"])
    assert all(r["flags"] == ["fixture"] for r in result["items"])


def test_duplicate_cannot_replace_pending_primary_and_disagreement_is_paired(allocation, contract, tmp_path):
    record = indexed_run(tmp_path, allocation, contract, duplicate=True)
    record["judgments"].pop("primary")
    result = collect(allocation, contract, tmp_path, record)
    assert all(c["n_valid_primary"] == 0 for c in result["cells"])
    assert result["disagreement"] == []
    record["judgments"]["primary"] = {"judgment_id": "fixture-primary",
        "response": artifact(tmp_path, "primary.json", response(contract, "partial"))}
    result = collect(allocation, contract, tmp_path, record)
    assert len(result["disagreement"]) == 31
    assert sum(p["item_pair_complete"] for p in result["pairs"]) == 1
    assert next(p for p in result["pairs"] if p["item_pair_complete"])["item_disagreements"] == 31


@pytest.mark.parametrize("category,quote,expected", [
    ("not supported", "Scientific adequacy: not supported.", "explicit"),
    ("supported", "Scientific adequacy: not supported.", "invalid"),
    ("supported", "Choose supported, qualified, not supported or unable to assess.", "invalid"),
    ("supported", "Scientific adequacy: supported.", "explicit"),
])
def test_adequacy_requires_literal_unambiguous_category(allocation, contract, tmp_path, category, quote, expected):
    record = indexed_run(tmp_path, allocation, contract)
    judgment = record["judgments"]["primary"]
    judgment["report"] = artifact(tmp_path, "report.md", "# Fixture\n" + quote + "\nNull finding.")
    judgment["adequacy"] = {"extraction_status": "explicit", "category": category,
        "excerpt": {"quote": quote, "start_line": 2, "end_line": 2}}
    result = collect(allocation, contract, tmp_path, record)
    actual = next(j for j in result["judgments"] if j["judgment_id"] == "fixture-primary")
    assert actual["extraction_status"] == expected
    assert actual["adequacy"] == (category if expected == "explicit" else None)


def test_quote_locator_and_stale_report_hash_fail(allocation, contract, tmp_path):
    record = indexed_run(tmp_path, allocation, contract)
    judgment = record["judgments"]["primary"]
    judgment["report"] = artifact(tmp_path, "report.md", "# Fixture\nScientific adequacy: qualified.")
    judgment["adequacy"] = {"extraction_status": "explicit", "category": "qualified",
        "excerpt": {"quote": "qualified", "start_line": 1, "end_line": 1}}
    assert collect(allocation, contract, tmp_path, record)["issues"]
    judgment["adequacy"]["excerpt"]["start_line"] = judgment["adequacy"]["excerpt"]["end_line"] = 2
    (tmp_path / "report.md").write_text("Changed report")
    assert "SHA-256 mismatch" in collect(allocation, contract, tmp_path, record)["issues"][0]["message"]


def test_clipped_negative_category_does_not_become_positive(allocation, contract, tmp_path):
    record = indexed_run(tmp_path, allocation, contract)
    judgment = record["judgments"]["primary"]
    judgment["report"] = artifact(tmp_path, "report.md", "Scientific adequacy: not **supported**.")
    judgment["adequacy"] = {"extraction_status": "explicit", "category": "supported",
        "excerpt": {"quote": "supported", "start_line": 1, "end_line": 1}}
    result = collect(allocation, contract, tmp_path, record)
    actual = next(j for j in result["judgments"] if j["judgment_id"] == "fixture-primary")
    assert actual["adequacy"] is None and actual["extraction_status"] == "invalid"


@pytest.mark.parametrize("bad_field", ["adequacy", "conclusion"])
def test_narrative_extractions_fail_independently(allocation, contract, tmp_path, bad_field):
    record = indexed_run(tmp_path, allocation, contract)
    judgment = record["judgments"]["primary"]
    judgment["report"] = artifact(tmp_path, "report.md", "Scientific adequacy: qualified.\nNull result.")
    judgment["adequacy"] = {"extraction_status": "explicit", "category": "qualified",
        "excerpt": {"quote": "Scientific adequacy: qualified.", "start_line": 1, "end_line": 1}}
    judgment["conclusion"] = {"quote": "Null result.", "start_line": 2, "end_line": 2}
    excerpt = judgment["adequacy"]["excerpt"] if bad_field == "adequacy" else judgment["conclusion"]
    excerpt["quote"] = "Absent text"
    result = collect(allocation, contract, tmp_path, record)
    actual = next(j for j in result["judgments"] if j["judgment_id"] == "fixture-primary")
    assert len(result["issues"]) == 1
    if bad_field == "adequacy":
        assert actual["adequacy"] is None and actual["conclusion"] == "Null result."
    else:
        assert actual["adequacy"] == "qualified" and actual["conclusion"] is None


def test_schema_permitted_extensions_cannot_replace_assignment(allocation, contract, tmp_path):
    record = indexed_run(tmp_path, allocation, contract)
    data = response(contract)
    data["responses"]["stamped-checklist:must/001"].update(run_id="wrong", dimension=["P"], level="may")
    record["judgments"]["primary"]["response"] = artifact(tmp_path, "primary.json", data)
    result = collect(allocation, contract, tmp_path, record)
    actual = result["items"][0]
    assert actual["run_id"] == record["run_id"] and actual["dimension"] == ["S"] and actual["level"] == "must"
    assert actual["answer_extensions"] == {"run_id": "wrong", "dimension": ["P"], "level": "may"}
    assert result["issues"] == []


def test_unverified_duration_stays_out_of_effort_and_retrieval_needs_coverage(allocation, contract, tmp_path):
    evidence = artifact(tmp_path, "retrieval.json", {"fixture": True})
    record = {"run_id": allocation["rounds"][0]["launch_order"][0]["run"],
              "operations": [{"operation_id": "fixture", "stage": "input-retrieval", "actor": "coordinator",
                  "scope": "Fixture only", "status": "succeeded", "duration_s": 12, "evidence": [evidence]}]}
    result = collect(allocation, contract, tmp_path, record)
    assert result["effort"] == [] and len(result["issues"]) == 1
    assert result["operations"][0]["evidence_status"] == "invalid"


@pytest.mark.parametrize("duration", [-1, True, "1"])
def test_effort_rejects_invalid_measurements(allocation, contract, tmp_path, duration):
    record = {"run_id": allocation["rounds"][0]["launch_order"][0]["run"],
              "operations": [{"operation_id": "worker", "stage": "worker", "actor": "worker",
                  "scope": "Total session wall time", "status": "succeeded", "duration_s": duration,
                  "evidence": [artifact(tmp_path, "time.json", {"elapsed": duration})]}]}
    with pytest.raises(ValueError, match="Invalid extraction index"):
        collect(allocation, contract, tmp_path, record)


def test_zero_duration_is_measured_and_missing_is_not_zero(allocation, contract, tmp_path):
    record = {"run_id": allocation["rounds"][0]["launch_order"][0]["run"],
              "operations": [{"operation_id": "fixture", "stage": "setup", "actor": "coordinator",
                  "scope": "Fixture wall time", "status": "succeeded", "duration_s": 0,
                  "evidence": [artifact(tmp_path, "time.json", {"elapsed": 0})]}]}
    result = collect(allocation, contract, tmp_path, record)
    assert len(result["effort"]) == 1 and result["effort"][0]["duration_s"] == 0
    record["operations"][0].pop("duration_s")
    assert collect(allocation, contract, tmp_path, record)["effort"] == []


def test_empty_tables_and_all_figures_render_without_fake_observations(allocation, contract, tmp_path):
    from comparison_figures import render
    result = collect(allocation, contract, tmp_path)
    output = tmp_path / "report"
    agg.write_tables(result, output)
    render(result, contract.items, output)
    assert len(list(output.glob("*.svg"))) == len(list(output.glob("*.png"))) == 5
    assert (output / "items.jsonl").read_text() == ""
    assert "assessment missing/invalid" in (output / "item-statuses.svg").read_text()
    assert "No verified duration measurements" in (output / "effort.svg").read_text()
    with pytest.raises(FileExistsError):
        agg.write_tables(result, output)


def test_frozen_assets_match_expected_dimensions_when_available():
    source = Path(os.environ.get("STAMPED_AGGREGATION_ASSESSOR", ROOT / "assessment"))
    if not (source / ".git").exists():
        pytest.skip("Initialize frozen assessment or set STAMPED_AGGREGATION_ASSESSOR")
    contract = agg.load_contract(source, ROOT / "assessment-version.json")
    assert len(contract.items) == 31
    assert {d: sum(d in i["dimension"] for i in contract.items) for d in "STAMPED"} == dict(
        zip("STAMPED", [3, 4, 3, 7, 6, 2, 6]))
