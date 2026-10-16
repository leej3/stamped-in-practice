"""Synthetic coordinator fixtures; never read formal worker results."""
import json
import os
from pathlib import Path
import sys
import uuid

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import aggregate_comparison as agg

RESULT = "a" * 40
SEED = "e" * 40
HEAD = "d" * 40
PIN = {"source_commit": "f" * 40, "environment_commit": "c" * 40,
       "environment_repository": "fixture", "sha256": {"pixi.toml": "1" * 64, "pixi.lock": "2" * 64}}


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
    return agg.Contract(items, schema, lock, PIN)


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


def authority(tmp_path, allocation):
    stop = artifact(tmp_path, "worker-stop.json", {
        "schema_version": 1, "kind": "worker-end-state", "capture_status": "complete",
        "errors": [], "head_commit": HEAD})
    original = {"version": 1, "status": "sealed", "comparison_id": "fixture-comparison",
        "conditions": allocation["conditions"], "assessment": dict(PIN, source_commit="b" * 40),
        "fixed_files": {"pixi.toml": "3" * 64, "judge-prompt.md": "4" * 64,
                        "scripts/assessment_procedure.py": "5" * 64},
        "study": {"input_tree": "6" * 40}, "resources": {}, "starting_environment": {},
        "host_identity": {}, "settings": {}, "replay": {}, "gitmodules_sha256": "7" * 64}
    original_bytes = json.dumps(original).encode()
    seal = dict(original, version=2, assessment=PIN, assessment_amendment={
        "scope": "assessment-only", "research_procedure_json": original_bytes.decode(),
        "research_procedure_sha256": agg.sha256(original_bytes), "retained_objects": [{
            "run": allocation["rounds"][0]["duplicate_judgments"][0], "seed_commit": SEED,
            "result_commit": RESULT, "worker_end_state_sha256": stop["sha256"]}]})
    selection = {"assessment_seal": artifact(tmp_path, "seal.json", seal),
                 "research_procedure_sha256": agg.sha256(original_bytes)}
    return original_bytes, selection, stop


def native(tmp_path, allocation, identity, *, excluded=False):
    original, selection, stop = authority(tmp_path, allocation)
    status = {"version": 1, "status": "formal-verified", "comparison_id": "fixture-comparison",
        "procedure_sha256": agg.sha256(original) if excluded else selection["assessment_seal"]["sha256"],
        "worker_end_state_sha256": stop["sha256"]}
    if not excluded:
        status["research_procedure_sha256"] = agg.sha256(original)
    result = {"procedure": status, "role": "judge", "condition": None, "assessment_pin": (
        json.loads(original)["assessment"] if excluded else PIN), "target_unchanged": True,
        "target": {"schema_version": 1, "target_path": "/fixture/result", "target_commit": RESULT,
                   "target_tree": "8" * 40}, "returncode": 0, "finished_at": "2026-01-01T01:00:00Z",
        "native_session_ids": [str(uuid.uuid5(uuid.NAMESPACE_URL, identity))]}
    return {"procedure_status": artifact(tmp_path, identity + "-procedure.json", status),
            "result": artifact(tmp_path, identity + "-result.json", result)}


def indexed_run(tmp_path, allocation, contract, duplicate=False):
    run_id = allocation["rounds"][0]["duplicate_judgments"][0]
    _, _, stop = authority(tmp_path, allocation)
    record = {"run_id": run_id, "result_commit": RESULT, "seed_commit": SEED, "worker_end_state": stop,
              "judgments": {"primary": {"judgment_id": "fixture-primary",
                  "native": native(tmp_path, allocation, "primary"),
                  "response": artifact(tmp_path, "primary.json", response(contract))}}}
    if duplicate:
        record["judgments"]["duplicate"] = {
            "judgment_id": "fixture-duplicate",
            "native": native(tmp_path, allocation, "duplicate"),
            "response": artifact(tmp_path, "duplicate.json", response(contract))}
    for judgment in record["judgments"].values():
        bind_outputs(tmp_path, judgment)
    return record


def bind_outputs(tmp_path, judgment):
    result = agg.parse_json((tmp_path / judgment["native"]["result"]["path"]).read_bytes())
    judgment["output_binding"] = artifact(tmp_path, judgment["judgment_id"] + "-outputs.json", {
        "schema_version": 1, "kind": "coordinator-assessment-output-binding",
        "native_result_sha256": judgment["native"]["result"]["sha256"],
        "native_session_ids": result["native_session_ids"],
        "outputs": {k: judgment[k] for k in ("response", "report") if k in judgment}})


def collect(allocation, contract, tmp_path, *records):
    original, selection, _ = authority(tmp_path, allocation)
    for record in records:
        for judgment in record.get("judgments", {}).values():
            if "native" in judgment:
                bind_outputs(tmp_path, judgment)
    return agg.aggregate(allocation, {"schema_version": 2, "comparison_provenance": selection,
        "runs": list(records)}, tmp_path, contract, original, selection["assessment_seal"]["sha256"])


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
    original_primary = record["judgments"].pop("primary")
    result = collect(allocation, contract, tmp_path, record)
    assert all(c["n_valid_primary"] == 0 for c in result["cells"])
    assert result["disagreement"] == []
    record["judgments"]["primary"] = dict(original_primary,
        response=artifact(tmp_path, "primary.json", response(contract, "partial")))
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


def gate_bundle(tmp_path, allocation, contract):
    record = indexed_run(tmp_path, allocation, contract)
    judgment = record["judgments"]["primary"]
    judgment["report"] = artifact(tmp_path, "report.md", "Scientific adequacy: qualified.\nNull finding.")
    judgment["adequacy"] = {"extraction_status": "explicit", "category": "qualified",
        "excerpt": {"quote": "Scientific adequacy: qualified.", "start_line": 1, "end_line": 1}}
    judgment["conclusion"] = {"quote": "Null finding.", "start_line": 2, "end_line": 2}
    bind_outputs(tmp_path, judgment)
    original, selection, _ = authority(tmp_path, allocation)
    return {"schema_version": 2, "comparison_provenance": selection, "runs": [record]}, original


def from_bundle(allocation, contract, tmp_path, index, original, digest=None):
    return agg.aggregate(allocation, index, tmp_path, contract, original,
        digest or index.get("comparison_provenance", {}).get("assessment_seal", {}).get("sha256"))


def rewrite(tmp_path, reference, mutation):
    value = agg.parse_json((tmp_path / reference["path"]).read_bytes())
    mutation(value)
    reference.update(artifact(tmp_path, reference["path"], value))


def assert_outcomes_blocked(result):
    assert len(result["runs"]) == 36 and len(result["judgments"]) == 48
    assert result["items"] == result["counts"] == result["disagreement"] == []
    actual = next(j for j in result["judgments"] if j["judgment_id"] == "fixture-primary")
    assert actual["inclusion_status"] == actual["response_status"] == "invalid"
    assert actual["adequacy"] is actual["conclusion"] is None
    assert actual["extraction_status"] == "invalid"
    assert all(c["n_valid_primary"] == 0 and c["n_assigned"] == 3 for c in result["cells"])
    assert any(i["area"] == "provenance" for i in result["issues"])


def test_pending_index_needs_no_new_seal(allocation, contract, tmp_path):
    result = agg.aggregate(allocation, {"schema_version": 2, "runs": []}, tmp_path, contract)
    assert len(result["runs"]) == 36 and not result["issues"]
    assert all(j["inclusion_status"] == "pending" for j in result["judgments"])


@pytest.mark.parametrize("field,mutation", [
    ("procedure_status", lambda v: v.update(procedure_sha256="0" * 64)),
    ("procedure_status", lambda v: v.pop("research_procedure_sha256")),
    ("procedure_status", lambda v: v.update(research_procedure_sha256="0" * 64)),
    ("procedure_status", lambda v: v.update(worker_end_state_sha256="0" * 64)),
    ("procedure_status", lambda v: v.update(comparison_id="different")),
    ("procedure_status", lambda v: v.update(status="development-unsealed")),
    ("result", lambda v: v["assessment_pin"].update(source_commit="0" * 40)),
    ("result", lambda v: v["assessment_pin"].update(environment_commit="0" * 40)),
    ("result", lambda v: v["target"].update(target_commit="0" * 40)),
    ("result", lambda v: v.update(target_unchanged=False)),
    ("result", lambda v: v.pop("target_unchanged")),
    ("result", lambda v: v.update(role="research")),
    ("result", lambda v: v.update(condition="baseline")),
    ("result", lambda v: v.update(finished_at="not-finalized")),
    ("result", lambda v: v.update(native_session_ids=[])),
    ("result", lambda v: v["procedure"].update(worker_end_state_sha256="0" * 64)),
])
def test_native_identity_failures_block_items_and_narrative(
        allocation, contract, tmp_path, field, mutation):
    index, original = gate_bundle(tmp_path, allocation, contract)
    rewrite(tmp_path, index["runs"][0]["judgments"]["primary"]["native"][field], mutation)
    assert_outcomes_blocked(from_bundle(allocation, contract, tmp_path, index, original))


@pytest.mark.parametrize("missing", ["native", "comparison_provenance", "worker_end_state", "seed_commit",
                                     "result", "output_binding"])
def test_missing_provenance_never_falls_back_to_checklist_only(allocation, contract, tmp_path, missing):
    index, original = gate_bundle(tmp_path, allocation, contract)
    owner = index if missing == "comparison_provenance" else index["runs"][0]
    if missing in ("native", "output_binding", "result"):
        owner = owner["judgments"]["primary"]
    if missing == "result":
        owner = owner["native"]
    owner.pop(missing)
    assert_outcomes_blocked(from_bundle(allocation, contract, tmp_path, index, original))


@pytest.mark.parametrize("mutation", [
    lambda v: v.update(version=1),
    lambda v: v["assessment_amendment"].update(scope="research-and-assessment"),
    lambda v: v["assessment_amendment"].update(research_procedure_json="{}"),
    lambda v: v["assessment_amendment"]["retained_objects"][0].update(seed_commit="0" * 40),
    lambda v: v["assessment_amendment"]["retained_objects"][0].update(result_commit="0" * 40),
    lambda v: v["assessment_amendment"]["retained_objects"][0].update(worker_end_state_sha256="0" * 64),
    lambda v: v["assessment"].update(source_commit="0" * 40),
    lambda v: v["assessment"]["sha256"].update({"pixi.lock": "0" * 64}),
    lambda v: v["study"].update(input_tree="0" * 40),
    lambda v: v["settings"].update(model="different"),
    lambda v: v["replay"].update(maximum_attempts=99),
    lambda v: v["fixed_files"].update({"judge-prompt.md": "0" * 64}),
])
def test_seal_and_retained_identity_failures_are_not_silently_repaired(allocation, contract, tmp_path, mutation):
    index, original = gate_bundle(tmp_path, allocation, contract)
    reference = index["comparison_provenance"]["assessment_seal"]
    rewrite(tmp_path, reference, mutation)
    # Rehashing the synthetic seal and both native receipts must not bypass the checks.
    for kind in ("procedure_status", "result"):
        native_ref = index["runs"][0]["judgments"]["primary"]["native"][kind]
        rewrite(tmp_path, native_ref, lambda v: (v if kind == "procedure_status" else v["procedure"]).update(
            procedure_sha256=reference["sha256"]))
    assert_outcomes_blocked(from_bundle(allocation, contract, tmp_path, index, original))


def test_approved_digest_is_independent_and_receipt_bytes_are_hashed(allocation, contract, tmp_path):
    index, original = gate_bundle(tmp_path, allocation, contract)
    assert_outcomes_blocked(agg.aggregate(allocation, index, tmp_path, contract, original))
    assert_outcomes_blocked(from_bundle(allocation, contract, tmp_path, index, original, digest="0" * 64))
    reference = index["runs"][0]["judgments"]["primary"]["native"]["result"]
    (tmp_path / reference["path"]).write_text("{}")
    assert_outcomes_blocked(from_bundle(allocation, contract, tmp_path, index, original))


def test_nonzero_exit_preserves_assigned_primary_with_valid_outcomes(allocation, contract, tmp_path):
    index, original = gate_bundle(tmp_path, allocation, contract)
    rewrite(tmp_path, index["runs"][0]["judgments"]["primary"]["native"]["result"],
            lambda v: v.update(returncode=1))
    bind_outputs(tmp_path, index["runs"][0]["judgments"]["primary"])
    result = from_bundle(allocation, contract, tmp_path, index, original)
    assert len(result["items"]) == 31 and not result["issues"]
    actual = next(j for j in result["judgments"] if j["judgment_id"] == "fixture-primary")
    assert actual["returncode"] == 1 and actual["adequacy"] == "qualified"


def test_reused_sessions_cannot_create_duplicate_agreement(allocation, contract, tmp_path):
    record = indexed_run(tmp_path, allocation, contract, duplicate=True)
    record["judgments"]["duplicate"]["native"] = record["judgments"]["primary"]["native"]
    result = collect(allocation, contract, tmp_path, record)
    assert_outcomes_blocked(result)
    assert sum(p["item_pair_complete"] for p in result["pairs"]) == 0


def test_original_attempts_remain_excluded_and_costs_separate(allocation, contract, tmp_path):
    index, original = gate_bundle(tmp_path, allocation, contract)
    record = index["runs"][0]
    old = {"judgment_id": "old-attempt", "reason": "Original assessment infrastructure failure",
           "native": native(tmp_path, allocation, "old", excluded=True),
           "response": artifact(tmp_path, "old-response.json", response(contract, "unmet")),
           "report": artifact(tmp_path, "old-report.md", "Scientific adequacy: not supported.")}
    record["excluded_attempts"] = [old]
    record["operations"] = [{"operation_id": "old-time", "stage": "judging", "actor": "judge",
        "status": "failed", "scope": "Session wall time", "duration_s": 600,
        "excluded_attempt_id": "old-attempt", "evidence": [old["native"]["result"]]}]
    result = from_bundle(allocation, contract, tmp_path, index, original)
    assert len(result["items"]) == 31 and {i["status"] for i in result["items"]} == {"met"}
    assert result["excluded_attempts"][0]["comparison_outcomes_included"] is False
    assert result["effort"][0]["assessment_scope"] == "excluded infrastructure attempt"
    assert result["excluded_attempts"][0]["evidence_status"] == "valid"
    record["judgments"]["primary"]["report"] = old["report"]
    assert_outcomes_blocked(from_bundle(allocation, contract, tmp_path, index, original))
    record["judgments"] = {}
    index.pop("comparison_provenance")
    result = agg.aggregate(allocation, index, tmp_path, contract, original)
    assert not result["items"] and len(result["effort"]) == 1 and not result["issues"]
    rewrite(tmp_path, old["native"]["result"], lambda v: v.pop("native_session_ids"))
    record["operations"][0]["evidence"] = [old["native"]["result"]]
    result = agg.aggregate(allocation, index, tmp_path, contract, original)
    assert result["excluded_attempts"][0]["evidence_status"] == "invalid"
    assert not result["effort"] and not result["items"]


def test_registration_binds_allocation_and_original_bytes():
    allocation_bytes, original = b'{"fixture":1}', b'{"comparison_id":"fixture"}'
    registration = {"comparison_id": "fixture", "allocation": {"sha256": agg.sha256(allocation_bytes)},
                    "procedure": {"sha256": agg.sha256(original)}}
    reg = json.dumps(registration).encode()
    agg.registered_inputs(allocation_bytes, original, reg)
    with pytest.raises(ValueError, match="allocation"):
        agg.registered_inputs(b'{"fixture":2}', original, reg)
    with pytest.raises(ValueError, match="original procedure"):
        agg.registered_inputs(allocation_bytes, original + b"\n", reg)


def future_bundle(tmp_path, allocation, contract, amended_worker=False):
    index, original = gate_bundle(tmp_path, allocation, contract)
    run = index["runs"][0]
    assigned = next(r for r in allocation["rounds"][0]["launch_order"] if r["run"] != run["run_id"])
    run.update(run_id=assigned["run"], seed_commit="0" * 40, result_commit="9" * 40)
    judgment = run["judgments"]["primary"]
    rewrite(tmp_path, judgment["response"], lambda v: v["object"].update(commit=run["result_commit"]))
    rewrite(tmp_path, judgment["native"]["result"], lambda v: v["target"].update(target_commit=run["result_commit"]))
    worker_status = {"version": 1, "status": "formal-verified", "comparison_id": "fixture-comparison",
                     "procedure_sha256": agg.sha256(original)}
    if amended_worker:
        worker_status.update(procedure_sha256=index["comparison_provenance"]["assessment_seal"]["sha256"],
                             research_procedure_sha256=agg.sha256(original))
    worker_result = {"role": "research", "procedure": worker_status, "starting_commit": run["seed_commit"],
        "condition": assigned["condition"], "worker_end_state": {"sha256": run["worker_end_state"]["sha256"],
            "head_commit": HEAD, "capture_status": "complete"}, "returncode": 1,
        "finished_at": "2026-01-01T00:00:00Z", "native_session_ids": [str(uuid.uuid4())]}
    run["worker_native"] = {"procedure_status": artifact(tmp_path, "worker-procedure.json", worker_status),
                            "result": artifact(tmp_path, "worker-result.json", worker_result)}
    run["worker_input"] = artifact(tmp_path, "worker-input.json", {"version": 2,
        "run": run["run_id"], "condition": assigned["condition"], "study_input_tree": "6" * 40,
        "source_manifest_sha256": "3" * 64})
    bind_outputs(tmp_path, judgment)
    return index, original


@pytest.mark.parametrize("amended_worker", [False, True])
def test_future_worker_uses_original_research_and_own_stop(allocation, contract, tmp_path, amended_worker):
    index, original = future_bundle(tmp_path, allocation, contract, amended_worker)
    result = from_bundle(allocation, contract, tmp_path, index, original)
    if amended_worker:
        assert_outcomes_blocked(result)
        return
    assert len(result["items"]) == 31 and not result["issues"]
    index["runs"][0].pop("worker_native")
    assert_outcomes_blocked(from_bundle(allocation, contract, tmp_path, index, original))


@pytest.mark.parametrize("field,mutation", [
    ("result", lambda v: v.update(starting_commit="1" * 40)),
    ("result", lambda v: v.update(condition="not-assigned")),
    ("result", lambda v: v["worker_end_state"].update(sha256="0" * 64)),
    ("result", lambda v: v["worker_end_state"].update(head_commit="0" * 40)),
    ("procedure_status", lambda v: v.update(procedure_sha256="0" * 64)),
    ("worker_input", lambda v: v.update(run="different-run")),
    ("worker_input", lambda v: v.update(study_input_tree="0" * 40)),
])
def test_future_worker_identity_cannot_be_relabelled(allocation, contract, tmp_path, field, mutation):
    index, original = future_bundle(tmp_path, allocation, contract)
    run = index["runs"][0]
    ref = run[field] if field == "worker_input" else run["worker_native"][field]
    rewrite(tmp_path, ref, mutation)
    assert_outcomes_blocked(from_bundle(allocation, contract, tmp_path, index, original))


@pytest.mark.parametrize("mutation", [
    lambda v: v.update(native_result_sha256="0" * 64),
    lambda v: v.update(native_session_ids=[str(uuid.uuid4())]),
    lambda v: v["outputs"]["response"].update(sha256="0" * 64),
    lambda v: v["outputs"].pop("report"),
])
def test_output_binding_requires_exact_session_and_artifact_hashes(allocation, contract, tmp_path, mutation):
    index, original = gate_bundle(tmp_path, allocation, contract)
    rewrite(tmp_path, index["runs"][0]["judgments"]["primary"]["output_binding"], mutation)
    assert_outcomes_blocked(from_bundle(allocation, contract, tmp_path, index, original))


def test_incomplete_excluded_attempt_is_retained_without_assigned_outcomes(allocation, contract, tmp_path):
    run_id = allocation["rounds"][0]["launch_order"][0]["run"]
    record = {"run_id": run_id, "excluded_attempts": [
        {"judgment_id": "preflight-failure", "reason": "Stopped before native completion"}]}
    result = agg.aggregate(allocation, {"schema_version": 2, "runs": [record]}, tmp_path, contract)
    assert len(result["excluded_attempts"]) == 1 and result["excluded_attempts"][0]["evidence_status"] == "invalid"
    assert len(result["judgments"]) == 48 and all(j["inclusion_status"] == "pending" for j in result["judgments"])
    assert not result["items"] and not result["effort"]
