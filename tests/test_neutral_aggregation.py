"""Synthetic neutral receipts only; no workers, judges or scientific execution."""
import copy
import json
import uuid

import pytest

from test_aggregate_comparison import (
    agg, artifact, bind_outputs, contract, overlay, response, rewrite,
    synthetic_allocation, HEAD, PIN, SEED,
)


@pytest.fixture
def allocation():
    return synthetic_allocation(6, 2, prospective=True)


def bundle(tmp_path, allocation, contract, *, head=None, partial=False):
    assigned = allocation["rounds"][0]["launch_order"][0]
    procedure = {"version": 3, "protocol": "neutral-v1", "status": "sealed",
        "comparison_id": allocation["comparison_id"], "conditions": allocation["conditions"],
        "assessment": PIN, "coordinator_commit": "1" * 40,
        "study": {"input_tree": "2" * 40}, "common_resources_sha256": "3" * 64,
        "fixed_files": {"prompts/neutral-worker-common.md": "4" * 64}}
    seal = artifact(tmp_path, "procedure.json", procedure)
    original = agg.artifact(seal, tmp_path)
    seed = {"version": 3, "protocol": "neutral-v1", "run": assigned["run"],
        "condition": assigned["condition"], "seed_commit": SEED,
        "coordinator_commit": procedure["coordinator_commit"],
        "study_input_tree": procedure["study"]["input_tree"],
        "common_resources_sha256": procedure["common_resources_sha256"],
        "common_prompt_sha256": procedure["fixed_files"]["prompts/neutral-worker-common.md"]}
    omissions = [{"path": "content/external/unavailable", "reason": "Synthetic missing reference"}] if partial else []
    manifest = {"schema": "original-delivery-v1", "kind": "original-delivery",
        "workspace": "content/workspace", "head_commit": head,
        "capture_status": "partial" if partial else "complete", "errors": [], "omissions": omissions}
    capture = artifact(tmp_path, "manifest.json", manifest)
    identity = {"uri": "/original/host/original-delivery/manifest.json", "sha256": capture["sha256"]}
    stop = {"schema_version": 2, "kind": "worker-end-state", "capture": identity,
        "seed_identities": {key: seed[key] for key in (
            "seed_commit", "study_input_tree", "common_prompt_sha256", "common_resources_sha256")},
        **{key: manifest[key] for key in ("head_commit", "capture_status", "errors", "omissions")}}
    stop_ref = artifact(tmp_path, "worker-stop.json", stop)
    status = {"version": 1, "status": "formal-verified", "comparison_id": procedure["comparison_id"],
              "procedure_sha256": seal["sha256"]}
    completion = {"returncode": 1, "finished_at": "2026-01-01T00:00:00Z",
                  "native_session_ids": [str(uuid.uuid4())]}
    worker = {"role": "research", "procedure": status, "starting_commit": SEED,
        "condition": assigned["condition"], "worker_end_state": {
            **stop_ref, "head_commit": head, "capture_status": stop["capture_status"], "capture": identity},
        **completion}
    judge_status = dict(status, worker_end_state_sha256=stop_ref["sha256"])
    judge = {"role": "judge", "condition": None, "procedure": judge_status, "assessment_pin": PIN,
        "target_unchanged": True, "target": {"schema_version": 2, "target_path": "/relocated/workspace",
            "target_commit": head, "capture": dict(identity, uri="/relocated/manifest.json")},
        **dict(completion, native_session_ids=[str(uuid.uuid4())])}
    answer = response(contract, "not-checked")
    answer["object"] = {"commit": head, "capture": judge["target"]["capture"]}
    text = "Scientific adequacy: qualified. The positive hypothesis is not supported."
    judgment = {"judgment_id": assigned["run"] + "-j01",
        "native": {"procedure_status": artifact(tmp_path, "judge-status.json", judge_status),
                   "result": artifact(tmp_path, "judge-result.json", judge)},
        "response": artifact(tmp_path, "response.json", answer),
        "scientific_report": artifact(tmp_path, "science.md", text),
        "adequacy": {"extraction_status": "explicit", "category": "qualified",
                     "excerpt": {"quote": text, "start_line": 1, "end_line": 1}}}
    bind_outputs(tmp_path, judgment)
    run = {"run_id": assigned["run"], "result_commit": head, "worker_head": head,
        "seed_commit": SEED, "retention_commit": "9" * 40, "worker_end_state": stop_ref,
        "delivery_capture": capture, "worker_input": artifact(tmp_path, "external-seed.json", seed),
        "worker_native": {"procedure_status": artifact(tmp_path, "worker-status.json", status),
                          "result": artifact(tmp_path, "worker-result.json", worker)},
        "judgments": {"primary": judgment}}
    return {"schema_version": 3, "comparison_provenance": {
        "assessment_seal": seal, "research_procedure_sha256": seal["sha256"]}, "runs": [run]}, original


def collect(tmp_path, allocation, contract, index, original, **kwargs):
    return agg.aggregate(allocation, index, tmp_path, contract, original,
        index["comparison_provenance"]["assessment_seal"]["sha256"], **kwargs)


@pytest.mark.parametrize("head", [None, HEAD, SEED])
@pytest.mark.parametrize("partial", [False, True])
def test_original_capture_identity_is_independent_of_retention(tmp_path, allocation, contract, head, partial):
    index, original = bundle(tmp_path, allocation, contract, head=head, partial=partial)
    tables = collect(tmp_path, allocation, contract, index, original)
    assert tables["issues"] == []
    assert len(tables["runs"]) == 72 and len(tables["judgments"]) == 96 and len(tables["pairs"]) == 24
    observed = next(j for j in tables["judgments"] if j["response_status"] == "valid")
    assert observed["result_commit"] == observed["worker_head"] == observed["object"]["commit"] == head
    assert observed["retention_commit"] == "9" * 40
    assert observed["original_delivery"]["capture_status"] == ("partial" if partial else "complete")
    assert observed["adequacy"] == "qualified" and observed["returncode"] == 1
    assert len(tables["items"]) == 31 and all(i["status"] == "not-checked" for i in tables["items"])
    assert not tables["effort"] and not tables["measure_validity"]
    assert all(j["judgment_id"] and j["dispatch_order"] for j in tables["judgments"])
    assert all(r["wave"] and r["launch_position"] for r in tables["runs"])
    assert all(c["n_assigned"] == 6 for c in tables["cells"])


@pytest.mark.parametrize("failure", [
    "retention-as-result", "capture-as-result", "worker-head", "manifest-hash", "manifest-head",
    "native-capture", "native-target", "response-capture", "response-commit", "seed", "condition",
    "worker-procedure", "worker-capture", "stop-seed", "missing-capture", "missing-worker-head",
])
def test_neutral_rejects_substituted_identities(tmp_path, allocation, contract, failure):
    index, original = bundle(tmp_path, allocation, contract)
    run = index["runs"][0]
    judgment = run["judgments"]["primary"]
    if failure == "retention-as-result":
        run["result_commit"] = run["retention_commit"]
    elif failure == "capture-as-result":
        run["result_commit"] = run["delivery_capture"]["sha256"]
    elif failure == "worker-head":
        run["worker_head"] = HEAD
    elif failure == "manifest-hash":
        run["delivery_capture"]["sha256"] = "0" * 64
    elif failure == "manifest-head":
        (tmp_path / "manifest.json").write_text("changed bytes")
    elif failure in {"native-capture", "native-target"}:
        rewrite(tmp_path, judgment["native"]["result"], lambda v: (
            v["target"]["capture"].update(sha256="0" * 64) if failure == "native-capture" else
            v["target"].update(target_commit=HEAD)))
        bind_outputs(tmp_path, judgment)
    elif failure.startswith("response-"):
        rewrite(tmp_path, judgment["response"], lambda v: (
            v["object"].update(capture={"uri": "different", "sha256": "0" * 64})
            if failure == "response-capture" else v["object"].update(commit=HEAD)))
        bind_outputs(tmp_path, judgment)
    elif failure in {"seed", "condition"}:
        rewrite(tmp_path, run["worker_input"], lambda v: v.update(
            {"seed_commit": HEAD} if failure == "seed" else {"condition": "different"}))
    elif failure == "worker-procedure":
        rewrite(tmp_path, run["worker_native"]["procedure_status"], lambda v: v.update(procedure_sha256="0" * 64))
    elif failure == "worker-capture":
        rewrite(tmp_path, run["worker_native"]["result"], lambda v: v["worker_end_state"]["capture"].update(sha256="0" * 64))
    elif failure == "stop-seed":
        rewrite(tmp_path, run["worker_end_state"], lambda v: v["seed_identities"].update(seed_commit=HEAD))
    else:
        run.pop("delivery_capture" if failure == "missing-capture" else "worker_head")
    tables = collect(tmp_path, allocation, contract, index, original)
    assert len(tables["judgments"]) == 96 and tables["items"] == [] and tables["issues"]
    assert all(r["worker_completion"] != "failed" for r in tables["runs"])


def test_flat_registration_is_hash_bound(tmp_path, allocation, contract):
    _, original = bundle(tmp_path, allocation, contract)
    allocation_bytes = json.dumps(allocation).encode()
    registration = {"comparison_id": allocation["comparison_id"],
        "allocation_sha256": agg.sha256(allocation_bytes), "procedure_sha256": agg.sha256(original)}
    agg.registered_inputs(allocation_bytes, original, json.dumps(registration).encode())
    for name in ("allocation", "procedure"):
        changed = dict(registration, **{name + "_sha256": "0" * 64})
        with pytest.raises(ValueError, match="registered"):
            agg.registered_inputs(allocation_bytes, original, json.dumps(changed).encode())
        changed = dict(registration, **{name: {"sha256": "0" * 64}})
        with pytest.raises(ValueError, match="registered"):
            agg.registered_inputs(allocation_bytes, original, json.dumps(changed).encode())


def test_single_neutral_version_and_unavailable_measure_keep_raw_verdicts(tmp_path, allocation, contract):
    index, original = bundle(tmp_path, allocation, contract)
    run = index["runs"][0]
    judgment = run["judgments"]["primary"]
    digest = agg.sha256(original)
    disposition = {"version": 1, "comparison_id": allocation["comparison_id"], "allocation_sha256": "5" * 64,
        "research_procedure_sha256": digest, "assessment_procedure_sha256": digest,
        "judgments": [{"run_id": run["run_id"], "role": "primary", "judgment_id": judgment["judgment_id"],
            "procedure_sha256": digest, "native_result_sha256": judgment["native"]["result"]["sha256"],
            "output_binding_sha256": judgment["output_binding"]["sha256"],
            "measure_validity": [overlay(tmp_path, "stamped-checklist:should/004")]}]}
    run["excluded_attempts"] = [{"judgment_id": "fixture-incomplete-attempt", "reason": "Fixture launch failure"}]
    run["operations"] = [{"operation_id": "coordinator-retention", "actor": "coordinator", "stage": "publication",
        "status": "succeeded", "scope": "coordinator preservation", "duration_s": 2,
        "evidence": [artifact(tmp_path, "preservation.txt", "Synthetic preservation receipt")]}]
    tables = collect(tmp_path, allocation, contract, index, original,
                     disposition=disposition, allocation_sha256="5" * 64)
    assert len(tables["version_strata"]) == 12
    assert sum(s["n_assigned_version"] for s in tables["version_strata"]) == 72
    assert len(tables["items"]) == 31 and len(tables["comparable_items"]) == 30
    assert all(i["status"] == "not-checked" for i in tables["items"])
    assert len(tables["excluded_attempts"]) == 1 and len(tables["judgments"]) == 96
    assert tables["effort"][0]["actor"] == "coordinator"
    assert all(p["item_disagreements"] is None for p in tables["pairs"])


def test_pending_assignment_cannot_be_swapped_or_replaced_by_duplicate(tmp_path, allocation, contract):
    index, original = bundle(tmp_path, allocation, contract)
    run = index["runs"][0]
    judgment = run["judgments"].pop("primary")
    run["judgments"]["duplicate"] = judgment
    with pytest.raises(ValueError, match="allocated judgment identity"):
        collect(tmp_path, allocation, contract, index, original)
    judgment["judgment_id"] = run["run_id"] + "-j02"
    tables = collect(tmp_path, allocation, contract, index, original)
    primary = next(j for j in tables["judgments"] if j["judgment_id"] == run["run_id"] + "-j01")
    assert primary["response_status"] == primary["inclusion_status"] == "pending"
    assert len(tables["items"]) == 31 and all(i["role"] == "duplicate" for i in tables["items"])


def test_pending_and_failed_workers_need_no_invented_delivery(tmp_path, allocation, contract):
    index, original = bundle(tmp_path, allocation, contract)
    run_id = index["runs"][0]["run_id"]
    index["runs"] = [{"run_id": run_id, "worker_completion": "failed", "judgments": {
        "primary": {"judgment_id": run_id + "-j01"}}}]
    tables = collect(tmp_path, allocation, contract, index, original)
    assert len(tables["judgments"]) == 96 and len(tables["runs"]) == 72
    assert tables["issues"] == tables["items"] == tables["effort"] == []
    assert all(j["response_status"] == "pending" for j in tables["judgments"])
    assert all(j["result_commit"] is None and j["adequacy"] is None for j in tables["judgments"])
    assert next(r for r in tables["runs"] if r["run_id"] == run_id)["worker_completion"] == "failed"


def test_capture_identity_requires_v3_index(tmp_path, allocation, contract):
    index, _ = bundle(tmp_path, allocation, contract)
    assert agg.schema_errors(index, agg.INDEX_SCHEMA) == []
    index["schema_version"] = 2
    assert agg.schema_errors(index, agg.INDEX_SCHEMA)


@pytest.mark.parametrize("collection", ["excluded_attempts", "supplementary_attempts"])
def test_allocated_identity_cannot_move_outside_its_slot(tmp_path, allocation, contract, collection):
    index, original = bundle(tmp_path, allocation, contract)
    run = index["runs"][0]
    run["judgments"] = {}
    run[collection] = [{"judgment_id": run["run_id"] + "-j01", "reason": "Synthetic attempted reassignment"}]
    with pytest.raises(ValueError, match="remain in its assigned slot"):
        collect(tmp_path, allocation, contract, index, original)


def test_neutral_cli_writes_separate_provenance_and_all_slots(tmp_path, allocation, contract, monkeypatch):
    index, original = bundle(tmp_path, allocation, contract)
    allocation_ref = artifact(tmp_path, "allocation.json", allocation)
    artifact(tmp_path, "index.json", index)
    artifact(tmp_path, "assessment-pin.json", PIN)
    artifact(tmp_path, "registration.json", {"comparison_id": allocation["comparison_id"],
        "allocation_sha256": allocation_ref["sha256"], "procedure_sha256": agg.sha256(original)})
    monkeypatch.setattr(agg, "load_contract", lambda *_: contract)
    output = tmp_path / "synthetic-output"
    assert agg.main(["--allocation", str(tmp_path / "allocation.json"),
        "--index", str(tmp_path / "index.json"), "--assessment-pin", str(tmp_path / "assessment-pin.json"),
        "--assessment-procedure-sha256", agg.sha256(original), "--output", str(output)]) == 0
    metadata = json.loads((output / "aggregation.json").read_bytes())
    assert metadata["schema_version"] == 3 and metadata["protocol"] == "neutral-v1"
    assert metadata["comparison_id"] == allocation["comparison_id"]
    assert metadata["assigned_workers"] == 72 and metadata["assigned_judgments"] == 96
    judgments = [json.loads(line) for line in (output / "judgments.jsonl").read_text().splitlines()]
    assert len(judgments) == 96 and all(j["judgment_id"] for j in judgments)
    assert (tmp_path / "procedure.json").read_bytes() == original


@pytest.mark.parametrize("failure", ["comparison", "schema", "assessor", "seal", "allocation-slots"])
def test_development_and_other_procedures_cannot_mix_with_neutral(tmp_path, allocation, contract, failure):
    index, original = bundle(tmp_path, allocation, contract)
    if failure == "comparison":
        allocation["comparison_id"] = "historical-development"
    elif failure == "schema":
        procedure = json.loads(original)
        procedure.update(version=1)
        original = json.dumps(procedure).encode()
    elif failure == "assessor":
        contract = copy.deepcopy(contract)
        contract.assessment_pin["source_commit"] = "0" * 40
    elif failure == "seal":
        index["comparison_provenance"]["assessment_seal"]["sha256"] = "0" * 64
    else:
        allocation["rounds"][0]["judgment_dispatch_order"].pop()
        with pytest.raises(ValueError, match="allocated judgment"):
            collect(tmp_path, allocation, contract, index, original)
        return
    tables = collect(tmp_path, allocation, contract, index, original)
    assert tables["items"] == [] and tables["issues"]
