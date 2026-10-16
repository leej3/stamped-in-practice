#!/usr/bin/env python3
"""Aggregate coordinator extractions without evaluating or changing research objects."""
import argparse
import csv
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import subprocess

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
STATUSES = ("met", "partial", "unmet", "not-checked", "not-applicable")
ADEQUACY = ("supported", "qualified", "not supported", "unable to assess")
DIMENSIONS = tuple("STAMPED")
LEVELS = ("must", "should", "may")
VALUES = dict(zip(STATUSES, ("yes", "no", "no", None, None)))
SHA = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
COMMIT = {"type": "string", "pattern": "^[0-9a-f]{40}([0-9a-f]{24})?$"}
TEXT = {"type": "string", "minLength": 1}


def obj(properties, required=()):
    return {"type": "object", "properties": properties, "required": list(required),
            "additionalProperties": False}


ARTIFACT = obj({"path": TEXT, "sha256": SHA}, ("path", "sha256"))
EXCERPT = obj({"quote": TEXT, "start_line": {"type": "integer", "minimum": 1},
               "end_line": {"type": "integer", "minimum": 1}},
              ("quote", "start_line", "end_line"))
EXTRACTION = obj({"extraction_status": {"enum": ["explicit", "missing", "ambiguous"]},
                  "category": {"enum": [*ADEQUACY, None]}, "excerpt": EXCERPT},
                 ("extraction_status", "category"))
NATIVE = obj({"procedure_status": ARTIFACT, "result": ARTIFACT})
JUDGMENT = obj({"judgment_id": TEXT, "response": ARTIFACT, "report": ARTIFACT,
                "native": NATIVE, "output_binding": ARTIFACT,
                "adequacy": EXTRACTION, "conclusion": EXCERPT}, ("judgment_id",))
EXCLUDED = obj({"judgment_id": TEXT, "reason": TEXT,
                "native": obj({"procedure_status": ARTIFACT, "result": ARTIFACT}),
                "response": ARTIFACT, "report": ARTIFACT}, ("judgment_id", "reason"))
OPERATION = obj({
    "operation_id": TEXT,
    "stage": {"enum": ["setup", "worker", "discovery", "installation", "computation",
                       "judging", "replay", "input-retrieval", "output-retrieval",
                       "environment-retrieval", "publication", "coordinator"]},
    "actor": {"enum": ["worker", "judge", "coordinator"]},
    "judgment_role": {"enum": ["primary", "duplicate"]},
    "excluded_attempt_id": TEXT,
    "status": {"enum": ["succeeded", "partial", "failed", "not-attempted",
                        "not-checked", "interrupted", "unknown"]},
    "scope": TEXT, "evidence": {"type": "array", "minItems": 1, "items": ARTIFACT},
    "duration_s": {"type": "number", "minimum": 0},
    "recipient": TEXT, "route": TEXT, "artifact_class": TEXT,
    "required_coverage": TEXT, "verified_coverage": TEXT, "host_scope": TEXT,
    "replay_attempt_observed": {"type": "boolean"},
    "helper_completed": {"type": "boolean"},
    "entrypoint_executed": {"type": "boolean"},
    "entrypoint_returncode": {"type": "integer"},
    "replay_status": {"enum": [*STATUSES, None]},
    "compared_outputs": {"type": "integer", "minimum": 0},
    "identical_outputs": {"type": "integer", "minimum": 0},
    "within_tolerance_outputs": {"type": "integer", "minimum": 0},
    "differing_outputs": {"type": "integer", "minimum": 0},
    "missing_outputs": {"type": "integer", "minimum": 0},
    "metrics": {"type": "array", "items": obj({
        "name": TEXT, "value": {"type": "number", "minimum": 0}, "unit": TEXT,
        "scope": TEXT}, ("name", "value", "unit", "scope"))},
}, ("operation_id", "stage", "actor", "status", "scope", "evidence"))
INDEX_SCHEMA = obj({"schema_version": {"const": 2},
    "comparison_provenance": obj({"assessment_seal": ARTIFACT, "research_procedure_sha256": SHA},
                                  ("assessment_seal", "research_procedure_sha256")),
    "runs": {"type": "array", "items": obj({
    "run_id": TEXT, "result_commit": COMMIT, "worker_head": COMMIT,
    "seed_commit": COMMIT, "worker_end_state": ARTIFACT,
    "worker_native": NATIVE, "worker_input": ARTIFACT,
    "retention_commit": COMMIT, "skill_commit": COMMIT,
    "worker_completion": {"enum": ["pending", "completed", "failed", "interrupted", "unknown"]},
    "judgments": obj({"primary": JUDGMENT, "duplicate": JUDGMENT}),
    "excluded_attempts": {"type": "array", "items": EXCLUDED},
    "operations": {"type": "array", "items": OPERATION},
}, ("run_id",))}}, ("schema_version", "runs"))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def parse_json(data):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("Nonfinite JSON number: " + value)

    def finite(value):
        number = float(value)
        return number if math.isfinite(number) else invalid(value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid, parse_float=finite)


def schema_errors(data, schema):
    return [f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
            for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data)]


@dataclass
class Contract:
    items: list
    schema: dict
    lock: dict
    assessment_pin: dict = None

    def validate(self, response, result_commit):
        errors = schema_errors(response, self.schema)
        if errors:
            return errors
        if not isinstance(response, dict) or not isinstance(response.get("responses"), dict):
            return ["Response must contain a responses object"]
        for name in ("checklist_version", "schema_version", "principles_version"):
            if response.get(name) != self.lock[name]:
                errors.append(name + " differs from the frozen checklist")
        for name in ("repo", "tag", "commit"):
            if response.get("checklist_source", {}).get(name) != self.lock["source"][name]:
                errors.append("checklist_source/" + name + " differs from the frozen checklist")
        if response.get("object", {}).get("commit") != result_commit:
            errors.append("object.commit differs from the indexed scientific result")
        answers = response["responses"]
        expected = {i["id"] for i in self.items}
        if set(answers) != expected:
            errors.append(f"Item identity mismatch: missing={sorted(expected - set(answers))}; "
                          f"unknown={sorted(set(answers) - expected)}")
        for item, answer in answers.items():
            if not isinstance(answer, dict):
                errors.append(item + ": answer must be an object")
                continue
            status, reason = answer.get("status"), answer.get("reason")
            if status not in STATUSES:
                errors.append(item + ": invalid status")
                continue
            if not isinstance(reason, str) or len(reason) > 250:
                errors.append(item + ": reason must be a string of at most 250 characters")
            elif "No probe covers this item" in reason:
                errors.append(item + ": unanswered probe placeholder")
            elif status != "met" and not reason.strip():
                errors.append(item + ": status requires a reason")
            if not isinstance(answer.get("source"), str) or not answer["source"].strip():
                errors.append(item + ": missing source")
            if status in ("met", "partial", "unmet") and not answer.get("evidence"):
                errors.append(item + ": status requires evidence")
            if "value" in answer and answer["value"] != VALUES[status]:
                errors.append(item + ": value contradicts status")
        return errors


def load_contract(assessor, pin):
    """Read immutable schema assets, never execute assessor or research code."""
    assessment_pin = parse_json(pin.read_bytes())
    revision = assessment_pin["source_commit"]
    if not re.fullmatch(r"[0-9a-f]{40}([0-9a-f]{24})?", revision):
        raise ValueError("Invalid assessor source commit")

    def blob(name):
        return subprocess.check_output(["git", "-C", str(assessor), "show",
            revision + ":skills/stamped-conventions/" + name], stderr=subprocess.PIPE)
    lock = parse_json(blob("checklist/lock.json"))
    raw = blob("checklist/" + lock["file"])
    if sha256(raw) != lock["sha256"]:
        raise ValueError("Frozen checklist content hash differs from lock")
    checklist = parse_json(raw)
    items = [dict(i, level=g["level"], principle_codes=e["principle_codes"],
                  dimension=sorted({p.split(".")[0] for p in e["principle_codes"]}))
             for g in checklist["data"] for e in g["entries"] for i in e["items"]]
    if len({i["id"] for i in items}) != len(items):
        raise ValueError("Duplicate canonical checklist item")
    return Contract(items, parse_json(blob("references/response-schema.json")), lock, assessment_pin)


def allocation_rows(allocation):
    rows, seen, duplicate_count = [], set(), 0
    conditions = allocation["conditions"]
    if len(set(conditions)) != len(conditions):
        raise ValueError("Duplicate allocation condition")
    seen_rounds = set()
    for group in allocation["rounds"]:
        round_id = group["round"]
        if round_id in seen_rounds:
            raise ValueError("Duplicate allocation round")
        seen_rounds.add(round_id)
        selection = group["duplicate_judgments"]
        runs = {r["run"] for r in group["launch_order"]}
        if len(set(selection)) != len(selection) or not set(selection) <= runs:
            raise ValueError("Invalid duplicate-judgment selection")
        duplicate_count += len(selection)
        cells = set()
        for order, run in enumerate(group["launch_order"], 1):
            cell = (run["condition"], run["replicate"])
            if run["run"] in seen or cell in cells or run["condition"] not in conditions:
                raise ValueError("Invalid or duplicate allocation assignment")
            cells.add(cell)
            seen.add(run["run"])
            rows.append({"run_id": run["run"], "study": allocation["study"], "round": round_id,
                         "condition": run["condition"], "replicate": run["replicate"],
                         "launch_order": order, "duplicate_selected": run["run"] in selection})
    for name, actual in (("total_workers", len(rows)), ("total_primary_judgments", len(rows)),
                         ("total_duplicate_judgments", duplicate_count)):
        if allocation.get(name) != actual:
            raise ValueError("Allocation total mismatch: " + name)
    return rows


def artifact(reference, base):
    path = Path(reference["path"])
    path = (base / path).resolve() if not path.is_absolute() else path.resolve()
    raw = path.read_bytes()
    if sha256(raw) != reference["sha256"]:
        raise ValueError("Artifact SHA-256 mismatch: " + str(path))
    return raw


def require_equal(actual, expected, label):
    if actual != expected:
        raise ValueError("Provenance mismatch: " + label)


def required_fields(value, properties):
    schema = obj(properties, properties)
    schema["additionalProperties"] = True
    errors = schema_errors(value, schema)
    if errors:
        raise ValueError("Malformed provenance: " + "; ".join(errors))


@dataclass
class ProvenanceGate:
    """Bind extractions to a selected seal and independently retained registration."""
    research: dict
    research_sha256: str
    seal: dict = None
    seal_sha256: str = None

    @classmethod
    def load(cls, original_bytes, selection, allocation, base, contract, approved_digest=None):
        if original_bytes is None:
            raise ValueError("Original registered research procedure is required")
        research = parse_json(original_bytes)
        required_fields(research, {"version": {"const": 1}, "status": {"const": "sealed"},
                                   "comparison_id": TEXT, "conditions": {"type": "array"},
                                   "assessment": {"type": "object"}})
        require_equal(research["conditions"], allocation["conditions"], "registered conditions")
        gate = cls(research, sha256(original_bytes))
        if selection is None:
            return gate
        if approved_digest is None:
            raise ValueError("Independent approved assessment procedure digest is required")
        require_equal(selection["assessment_seal"]["sha256"], approved_digest,
                      "approved assessment procedure digest")
        require_equal(selection["research_procedure_sha256"], gate.research_sha256,
                      "registered research digest")
        seal = parse_json(artifact(selection["assessment_seal"], base))
        required_fields(seal, {"version": {"const": 2}, "status": {"const": "sealed"},
            "comparison_id": TEXT, "conditions": {"type": "array"},
            "assessment": {"type": "object"}, "assessment_amendment": {"type": "object"}})
        amendment = seal["assessment_amendment"]
        required_fields(amendment, {"scope": {"const": "assessment-only"},
            "research_procedure_json": TEXT, "research_procedure_sha256": SHA,
            "retained_objects": {"type": "array", "minItems": 1, "items": obj({
                "run": TEXT, "seed_commit": COMMIT, "result_commit": COMMIT,
                "worker_end_state_sha256": SHA},
                ("run", "seed_commit", "result_commit", "worker_end_state_sha256"))}})
        original = amendment["research_procedure_json"].encode()
        require_equal(sha256(original), gate.research_sha256, "embedded original research bytes")
        require_equal(amendment["research_procedure_sha256"], gate.research_sha256,
                      "embedded research digest")
        for key in ("comparison_id", "conditions", "study", "resources", "starting_environment",
                    "host_identity", "settings", "replay", "gitmodules_sha256"):
            if key not in research or key not in seal:
                raise ValueError("Missing sealed design field: " + key)
            require_equal(seal[key], research[key], "amendment " + key)
        changed = {"assessment-version.json", "scripts/assessment_procedure.py",
                   "scripts/prepare_launch.py", "scripts/launch_native_probe.py"}
        require_equal(set(seal["fixed_files"]), set(research["fixed_files"]), "fixed-file boundary")
        for key in set(research["fixed_files"]) - changed:
            require_equal(seal["fixed_files"][key], research["fixed_files"][key], "fixed file " + key)
        for key in ("environment_commit", "environment_repository", "sha256"):
            require_equal(seal["assessment"].get(key), research["assessment"].get(key),
                          "preserved assessment environment " + key)
        require_equal(contract.assessment_pin, seal["assessment"], "loaded assessor pin")
        retained = amendment["retained_objects"]
        ids = [r["run"] for r in retained]
        assigned = {r["run_id"] for r in allocation_rows(allocation)}
        if len(ids) != len(set(ids)) or not set(ids) <= assigned:
            raise ValueError("Invalid retained run identities in assessment seal")
        gate.seal, gate.seal_sha256 = seal, selection["assessment_seal"]["sha256"]
        return gate

    def validate_worker(self, run, stop, base, assignment):
        if "worker_native" not in run or "worker_input" not in run:
            raise ValueError("Unlisted worker requires original worker_native and worker_input evidence")
        status = parse_json(artifact(run["worker_native"]["procedure_status"], base))
        required_fields(status, {"version": {"const": 1}, "status": {"const": "formal-verified"},
                                "comparison_id": TEXT, "procedure_sha256": SHA})
        require_equal(status["comparison_id"], self.research["comparison_id"], "worker comparison")
        require_equal(status["procedure_sha256"], self.research_sha256, "worker original launch procedure")
        if "research_procedure_sha256" in status:
            require_equal(status["research_procedure_sha256"], self.research_sha256,
                          "worker original research digest")
        result = parse_json(artifact(run["worker_native"]["result"], base))
        required_fields(result, {"role": {"const": "research"}, "procedure": {"type": "object"},
            "starting_commit": COMMIT, "condition": TEXT, "worker_end_state": {"type": "object"},
            "returncode": {"type": "integer"}, "finished_at": {"type": "string", "format": "date-time"},
            "native_session_ids": {"type": "array", "minItems": 1, "uniqueItems": True,
                                   "items": {"type": "string", "format": "uuid"}}})
        require_equal(result["procedure"], status, "worker procedure receipts")
        require_equal(result["starting_commit"], run["seed_commit"], "worker seed commit")
        require_equal(result["condition"], assignment["condition"], "worker assigned condition")
        for key, expected in (("sha256", run["worker_end_state"]["sha256"]),
                              ("head_commit", stop["head_commit"]), ("capture_status", "complete")):
            require_equal(result["worker_end_state"].get(key), expected, "worker stop " + key)
        seed = parse_json(artifact(run["worker_input"], base))
        required_fields(seed, {"version": {"const": 2}, "run": TEXT, "condition": TEXT,
                              "study_input_tree": COMMIT, "source_manifest_sha256": SHA})
        for key, expected in (("run", run["run_id"]), ("condition", assignment["condition"]),
                              ("study_input_tree", self.research["study"]["input_tree"]),
                              ("source_manifest_sha256", self.research["fixed_files"]["pixi.toml"])):
            require_equal(seed[key], expected, "worker input " + key)

    def validate(self, run, native, base, assignment, *, excluded=False):
        if not excluded and self.seal is None:
            raise ValueError("Included judgment requires the amended assessment seal")
        for key in ("seed_commit", "result_commit", "worker_end_state"):
            if key not in run:
                raise ValueError("Judgment provenance requires run " + key)
        stop = parse_json(artifact(run["worker_end_state"], base))
        required_fields(stop, {"schema_version": {"const": 1}, "kind": {"const": "worker-end-state"},
            "capture_status": {"const": "complete"}, "errors": {"const": []}, "head_commit": COMMIT})
        if "worker_head" in run:
            require_equal(stop["head_commit"], run["worker_head"], "original worker head")
        retained_match = False
        if not excluded:
            for retained in self.seal["assessment_amendment"]["retained_objects"]:
                if retained["run"] == run["run_id"]:
                    retained_match = True
                    for key in ("seed_commit", "result_commit"):
                        require_equal(run[key], retained[key], "retained " + key)
                    require_equal(run["worker_end_state"]["sha256"], retained["worker_end_state_sha256"],
                                  "retained original worker stop")
                elif (retained["seed_commit"] == run["seed_commit"] or
                      retained["result_commit"] == run["result_commit"]):
                    raise ValueError("Retained object was relabeled as another run")
            if not retained_match:
                self.validate_worker(run, stop, base, assignment)
        status = parse_json(artifact(native["procedure_status"], base))
        required_fields(status, {"version": {"const": 1}, "status": {"const": "formal-verified"},
            "comparison_id": TEXT, "procedure_sha256": SHA, "worker_end_state_sha256": SHA})
        require_equal(status["comparison_id"], self.research["comparison_id"], "comparison identity")
        digest = self.research_sha256 if excluded else self.seal_sha256
        require_equal(status["procedure_sha256"], digest, "assessment procedure digest")
        if not excluded or "research_procedure_sha256" in status:
            require_equal(status.get("research_procedure_sha256"), self.research_sha256,
                          "native original research digest")
        require_equal(status["worker_end_state_sha256"], run["worker_end_state"]["sha256"],
                      "native original worker stop")
        result = parse_json(artifact(native["result"], base))
        required_fields(result, {"role": {"const": "judge"}, "condition": {"type": "null"},
            "procedure": {"type": "object"},
            "assessment_pin": {"type": "object"}, "target": {"type": "object"},
            "target_unchanged": {"const": True}, "returncode": {"type": "integer"},
            "finished_at": {"type": "string", "format": "date-time"},
            "native_session_ids": {"type": "array", "minItems": 1, "uniqueItems": True,
                                   "items": {"type": "string", "format": "uuid"}}})
        require_equal(result["procedure"], status, "result/procedure-status receipt identity")
        expected_pin = self.research["assessment"] if excluded else self.seal["assessment"]
        require_equal(result["assessment_pin"], expected_pin, "native assessor source/runtime pin")
        required_fields(result["target"], {"schema_version": {"const": 1}, "target_path": TEXT,
                                           "target_commit": COMMIT, "target_tree": COMMIT})
        require_equal(result["target"]["target_commit"], run["result_commit"], "native scientific target")
        return {"procedure_sha256": digest, "research_procedure_sha256": self.research_sha256,
                "worker_end_state_sha256": run["worker_end_state"]["sha256"],
                "assessment_pin": expected_pin, "native_session_ids": result["native_session_ids"],
                "target": result["target"], "returncode": result["returncode"],
                "finished_at": result["finished_at"]}


def validate_output_binding(supplied, check, base):
    """Verify a retained coordinator attribution; native receipts do not hash outputs."""
    if not any(key in supplied for key in ("response", "report", "adequacy", "conclusion")):
        return
    if "output_binding" not in supplied:
        raise ValueError("Outcome extraction requires a retained output_binding manifest")
    binding = parse_json(artifact(supplied["output_binding"], base))
    required_fields(binding, {"schema_version": {"const": 1},
        "kind": {"const": "coordinator-assessment-output-binding"},
        "native_result_sha256": SHA, "native_session_ids": {"type": "array"},
        "outputs": obj({"response": ARTIFACT, "report": ARTIFACT})})
    require_equal(binding["native_result_sha256"], supplied["native"]["result"]["sha256"],
                  "bound native result bytes")
    require_equal(binding["native_session_ids"], check["native_session_ids"], "bound native sessions")
    for key in ("response", "report"):
        if key in supplied:
            require_equal(binding["outputs"].get(key, {}).get("sha256"), supplied[key]["sha256"],
                          "bound " + key + " bytes")


def excerpt_context(excerpt, report):
    lines = report.splitlines()
    start, end = excerpt["start_line"], excerpt["end_line"]
    if start > end or end > len(lines):
        raise ValueError("Excerpt line locator is outside the report")
    selected = "\n".join(lines[start - 1:end])
    if excerpt["quote"] not in selected:
        raise ValueError("Exact quotation is absent from the cited report lines")
    return selected


def excerpt_text(excerpt, report):
    excerpt_context(excerpt, report)
    return excerpt["quote"]


def aggregate(allocation, index, base, contract, research_procedure=None, assessment_procedure_sha256=None):
    errors = schema_errors(index, INDEX_SCHEMA)
    if errors:
        raise ValueError("Invalid extraction index:\n" + "\n".join(errors))
    runs = allocation_rows(allocation)
    assigned = {r["run_id"]: r for r in runs}
    indexed, judgment_ids, operation_ids = {}, set(), set()
    for run in index["runs"]:
        run_id = run["run_id"]
        if run_id not in assigned or run_id in indexed:
            raise ValueError("Unknown or repeated indexed run: " + run_id)
        indexed[run_id] = run
        if "duplicate" in run.get("judgments", {}) and not assigned[run_id]["duplicate_selected"]:
            raise ValueError("Duplicate judgment was not preselected: " + run_id)
        for judgment in [*run.get("judgments", {}).values(), *run.get("excluded_attempts", [])]:
            identity = judgment["judgment_id"]
            if identity in judgment_ids:
                raise ValueError("Repeated judgment ID: " + identity)
            judgment_ids.add(identity)
            if "result_commit" not in run and judgment in run.get("judgments", {}).values():
                raise ValueError("Judgment requires run result_commit: " + run_id)
        for op in run.get("operations", []):
            identity = (run_id, op["operation_id"])
            if identity in operation_ids:
                raise ValueError("Repeated operation ID: " + str(identity))
            operation_ids.add(identity)
            if op.get("judgment_role") == "duplicate" and not assigned[run_id]["duplicate_selected"]:
                raise ValueError("Operation names an unselected duplicate: " + run_id)
            if "excluded_attempt_id" in op:
                if "judgment_role" in op:
                    raise ValueError("Excluded attempt operation cannot occupy an assigned judgment role")
                if op["excluded_attempt_id"] not in {j["judgment_id"] for j in run.get("excluded_attempts", [])}:
                    raise ValueError("Unknown excluded attempt operation reference")
    tables = {name: [] for name in ("runs", "judgments", "items", "counts", "operations",
                                    "effort", "issues", "disagreement", "pairs", "cells", "excluded_attempts")}
    answers_by_slot = {}
    judgments_by_slot = {}

    def issue(run_id, role, area, message):
        tables["issues"].append(dict(run_id=run_id, role=role, area=area, message=str(message)))

    # Validate before extracting any outcomes, including narrative categories.
    checks, sessions, excluded_hashes = {}, {}, set()
    gates = {}
    for excluded in (False, True):
        try:
            gates[excluded] = ProvenanceGate.load(research_procedure,
                None if excluded else index.get("comparison_provenance"), allocation, base, contract,
                assessment_procedure_sha256)
        except (OSError, ValueError, TypeError, KeyError) as error:
            gates[excluded] = str(error)
    if "comparison_provenance" in index and isinstance(gates[False], str):
        issue("", "", "comparison-provenance", gates[False])
    for run_id, record in indexed.items():
        entries = [(role, j, False) for role, j in record.get("judgments", {}).items()]
        entries += [("excluded", j, True) for j in record.get("excluded_attempts", [])]
        for role, supplied, excluded in entries:
            identity = supplied["judgment_id"]
            check = dict(inclusion_status="pending")
            checks[identity] = check
            if not excluded and set(supplied) == {"judgment_id"}:
                continue
            try:
                gate = gates[excluded]
                if isinstance(gate, str):
                    raise ValueError(gate)
                if "native" not in supplied:
                    raise ValueError("Judgment requires hashed native procedure-status and finalized result")
                check.update(gate.validate(record, supplied["native"], base, assigned[run_id], excluded=excluded))
                if excluded:
                    for field in ("response", "report"):
                        if field in supplied:
                            artifact(supplied[field], base)
                else:
                    validate_output_binding(supplied, check, base)
                check["inclusion_status"] = "excluded" if excluded else "eligible"
                for session in check["native_session_ids"]:
                    sessions.setdefault(session, []).append(identity)
            except (OSError, ValueError, TypeError, KeyError) as error:
                check.update(inclusion_status="invalid", provenance_error=str(error))
            if excluded:
                excluded_hashes.update(supplied[k]["sha256"] for k in ("response", "report") if k in supplied)
    for identities in sessions.values():
        if len(identities) > 1:
            for identity in identities:
                checks[identity].update(inclusion_status="invalid",
                                        provenance_error="Native session reused across judgment attempts")
    for run_id, record in indexed.items():
        for role, supplied in record.get("judgments", {}).items():
            check = checks[supplied["judgment_id"]]
            if any(supplied[k]["sha256"] in excluded_hashes for k in ("response", "report") if k in supplied):
                check.update(inclusion_status="invalid",
                             provenance_error="Outcome artifact reused from an excluded original attempt")
            if check["inclusion_status"] == "invalid":
                issue(run_id, role, "provenance", check["provenance_error"])
        for supplied in record.get("excluded_attempts", []):
            check = checks[supplied["judgment_id"]]
            tables["excluded_attempts"].append(dict(assigned[run_id], **supplied, **check,
                comparison_outcomes_included=False, evidence_status=(
                    "valid" if check["inclusion_status"] == "excluded" else "invalid")))
            if check["inclusion_status"] == "invalid":
                issue(run_id, "excluded", "provenance", check["provenance_error"])

    for assignment in runs:
        run_id = assignment["run_id"]
        record = indexed.get(run_id, {})
        row = dict(assignment, worker_completion=record.get(
            "worker_completion", "unknown" if record else "pending"))
        row.update({k: record.get(k) for k in
                    ("result_commit", "seed_commit", "worker_head", "worker_end_state",
                     "worker_native", "worker_input", "retention_commit", "skill_commit")})
        tables["runs"].append(row)
        for role in ("primary", "duplicate") if assignment["duplicate_selected"] else ("primary",):
            supplied = record.get("judgments", {}).get(role, {})
            judgment = dict(assignment, role=role, judgment_id=supplied.get("judgment_id"),
                            result_commit=record.get("result_commit"), response_status="pending",
                            adequacy=None, extraction_status="missing", conclusion=None)
            judgment.update({k: supplied.get(k) for k in ("response", "report", "native", "output_binding")})
            judgment.update(checks.get(supplied.get("judgment_id"), {"inclusion_status": "pending"}))
            tables["judgments"].append(judgment)
            judgments_by_slot[run_id, role] = judgment
            if judgment["inclusion_status"] != "eligible":
                if judgment["inclusion_status"] == "invalid":
                    judgment.update(response_status="invalid", extraction_status="invalid")
                continue
            if "response" in supplied:
                try:
                    response = parse_json(artifact(supplied["response"], base))
                    problems = contract.validate(response, record["result_commit"])
                    if problems:
                        raise ValueError("; ".join(problems))
                except (OSError, ValueError, TypeError) as error:
                    judgment["response_status"] = "invalid"
                    issue(run_id, role, "response", error)
                else:
                    judgment["response_status"] = "valid"
                    answers_by_slot[run_id, role] = response["responses"]
                    for item in contract.items:
                        answer = response["responses"][item["id"]]
                        fields = ("status", "reason", "source", "evidence", "flags", "value")
                        normalized = dict(run_id=run_id, role=role,
                            judgment_id=supplied["judgment_id"], item_id=item["id"],
                            level=item["level"], principle_codes=item["principle_codes"],
                            dimension=item["dimension"])
                        normalized.update({k: answer[k] for k in fields if k in answer})
                        extensions = {k: v for k, v in answer.items() if k not in fields}
                        if extensions:
                            normalized["answer_extensions"] = extensions
                        tables["items"].append(normalized)
                    for kind, groups in (("level", LEVELS), ("dimension", DIMENSIONS)):
                        for group in groups:
                            selected = [i for i in contract.items if
                                (i["level"] == group if kind == "level" else group in i["dimension"])]
                            counts = {s: sum(response["responses"][i["id"]]["status"] == s
                                             for i in selected) for s in STATUSES}
                            tables["counts"].append(dict(run_id=run_id, role=role,
                                judgment_id=supplied["judgment_id"], group_type=kind, group=group,
                                n_pinned=len(selected),
                                n_applicable=len(selected) - counts["not-applicable"], **counts))
            extraction = supplied.get("adequacy", {"extraction_status": "missing", "category": None})
            report = None
            report_error = None
            try:
                report = artifact(supplied["report"], base).decode() if "report" in supplied else None
            except (OSError, ValueError, UnicodeError) as error:
                report_error = str(error)
                issue(run_id, role, "report", error)
            try:
                status = extraction["extraction_status"]
                if report_error:
                    raise ValueError("Report is invalid; narrative extraction cannot be verified")
                if status == "explicit":
                    if report is None or "excerpt" not in extraction or extraction["category"] is None:
                        raise ValueError("Explicit adequacy requires report, category and excerpt")
                    context = excerpt_context(extraction["excerpt"], report)
                    for text in (extraction["excerpt"]["quote"], context):
                        # Inspect the complete cited lines too: quoting only "supported"
                        # from "not supported" must never reverse a judge's verdict.
                        plain = re.sub(r"[*_'\"\x60]", "", text.casefold())
                        categories = set(re.findall(
                            r"(?<!\w)(not supported|unable to assess|supported|qualified)(?!\w)", plain))
                        if categories != {extraction["category"]}:
                            raise ValueError("Adequacy quote and cited context must name only its selected category")
                    judgment.update(adequacy=extraction["category"],
                                    adequacy_excerpt=extraction["excerpt"])
                elif extraction["category"] is not None:
                    raise ValueError("Missing/ambiguous adequacy must have null category")
                judgment["extraction_status"] = status
            except (OSError, ValueError, UnicodeError) as error:
                judgment.update(adequacy=None, extraction_status="invalid")
                issue(run_id, role, "adequacy", error)
            if "conclusion" in supplied:
                try:
                    if report is None:
                        raise ValueError("Conclusion requires a hashed report")
                    judgment["conclusion"] = excerpt_text(supplied["conclusion"], report)
                    judgment["conclusion_excerpt"] = supplied["conclusion"]
                except (OSError, ValueError, UnicodeError) as error:
                    issue(run_id, role, "conclusion", error)
        for operation in record.get("operations", []):
            excluded_id = operation.get("excluded_attempt_id")
            scope = "excluded infrastructure attempt" if excluded_id else (
                "assigned comparison" if operation.get("judgment_role") else "other operations")
            op = dict(assignment, **operation, evidence_status="valid", assessment_scope=scope)
            try:
                if excluded_id and checks[excluded_id]["inclusion_status"] != "excluded":
                    raise ValueError("Excluded attempt provenance is invalid; cost is unverified")
                for evidence in operation["evidence"]:
                    artifact(evidence, base)
                if operation["stage"].endswith("-retrieval"):
                    for key in ("recipient", "route", "artifact_class", "required_coverage",
                                "verified_coverage", "host_scope"):
                        if key not in operation:
                            raise ValueError("Retrieval observation requires " + key)
            except (OSError, ValueError) as error:
                op["evidence_status"] = "invalid"
                issue(run_id, "", "operation:" + operation["operation_id"], error)
            tables["operations"].append(op)
            if "duration_s" in operation and op["evidence_status"] == "valid":
                tables["effort"].append(op)
    for assignment in runs:
        if not assignment["duplicate_selected"]:
            continue
        run_id = assignment["run_id"]
        primary = answers_by_slot.get((run_id, "primary"))
        duplicate = answers_by_slot.get((run_id, "duplicate"))
        first, second = (judgments_by_slot[run_id, role] for role in ("primary", "duplicate"))
        paired = primary is not None and duplicate is not None
        scientific = first["adequacy"] is not None and second["adequacy"] is not None
        pair = dict(assignment, item_pair_complete=paired, item_denominator=len(contract.items),
                    primary_id=first["judgment_id"], duplicate_id=second["judgment_id"],
                    item_disagreements=None, primary_adequacy=first["adequacy"],
                    duplicate_adequacy=second["adequacy"], adequacy_pair_complete=scientific,
                    adequacy_disagreement=(first["adequacy"] != second["adequacy"]) if scientific else None)
        if paired:
            pair["item_disagreements"] = 0
            for item in contract.items:
                a, b = primary[item["id"]]["status"], duplicate[item["id"]]["status"]
                mismatch = a != b
                pair["item_disagreements"] += mismatch
                tables["disagreement"].append(dict(run_id=run_id, item_id=item["id"],
                    primary_status=a, duplicate_status=b, exact_disagreement=mismatch))
        tables["pairs"].append(pair)
    for round_id in dict.fromkeys(r["round"] for r in runs):
        for condition in allocation["conditions"]:
            selected = [r for r in runs if r["round"] == round_id and r["condition"] == condition]
            ids = {r["run_id"] for r in selected}
            js = [judgments_by_slot[r["run_id"], "primary"] for r in selected]
            common = dict(study=allocation["study"], round=round_id, condition=condition,
                          n_assigned=len(selected), n_valid_primary=sum(j["response_status"] == "valid" for j in js))
            for category in (*ADEQUACY, "missing", "ambiguous", "invalid"):
                count = sum((j["adequacy"] == category if category in ADEQUACY
                             else j["extraction_status"] == category) for j in js)
                tables["cells"].append(dict(common, metric="adequacy", group=category, count=count))
            for kind, groups in (("level", LEVELS), ("dimension", DIMENSIONS)):
                for group in groups:
                    for status in STATUSES:
                        values = [c[status] for c in tables["counts"] if c["run_id"] in ids and
                                  c["role"] == "primary" and c["group_type"] == kind and c["group"] == group]
                        tables["cells"].append(dict(common, metric=kind, group=group, status=status,
                            n_observed=len(values), median=statistics.median(values) if values else None,
                            minimum=min(values) if values else None, maximum=max(values) if values else None))
    return tables


def write_tables(tables, output):
    output.mkdir(parents=True, exist_ok=False)
    for name, rows in tables.items():
        with (output / (name + ".jsonl")).open("w") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        fields = list(dict.fromkeys(k for row in rows for k in row))
        # Empty tables still have a readable header, never fabricated data rows.
        if not fields:
            fields = {"items": ["run_id", "role", "item_id", "status"],
                      "counts": ["run_id", "role", "group_type", "group", *STATUSES],
                      "disagreement": ["run_id", "item_id", "primary_status", "duplicate_status"],
                      "issues": ["run_id", "role", "area", "message"]}.get(name, ["run_id"])
        with (output / (name + ".tsv")).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fields, delimiter="\t")
            writer.writeheader()
            for row in rows:
                writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict))
                                 else v for k, v in row.items()})


def registered_inputs(allocation_bytes, research_bytes, registration_bytes):
    """The index cannot nominate a different allocation or original research seal."""
    registration = parse_json(registration_bytes)
    require_equal(registration["allocation"]["sha256"], sha256(allocation_bytes), "registered allocation bytes")
    require_equal(registration["procedure"]["sha256"], sha256(research_bytes), "registered original procedure bytes")
    require_equal(registration["comparison_id"], parse_json(research_bytes)["comparison_id"],
                  "registration comparison identity")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allocation", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New output directory; never overwritten")
    parser.add_argument("--assessor", type=Path, default=ROOT / "assessment")
    parser.add_argument("--assessment-pin", type=Path, default=ROOT / "assessment-version.json")
    parser.add_argument("--registration", type=Path,
                        help="Independent original registration; default: allocation sibling registration.json")
    parser.add_argument("--research-procedure", type=Path,
                        help="Original seal; default: allocation sibling procedure.json")
    parser.add_argument("--assessment-procedure-sha256",
                        help="Approved amended seal digest from the independent amendment record")
    args = parser.parse_args(argv)
    try:
        allocation_bytes, index_bytes = args.allocation.read_bytes(), args.index.read_bytes()
        research_bytes = (args.research_procedure or args.allocation.with_name("procedure.json")).read_bytes()
        registration_bytes = (args.registration or args.allocation.with_name("registration.json")).read_bytes()
        registered_inputs(allocation_bytes, research_bytes, registration_bytes)
        allocation = parse_json(allocation_bytes)
        index = parse_json(index_bytes)
        contract = load_contract(args.assessor, args.assessment_pin)
        tables = aggregate(allocation, index, args.index.resolve().parent, contract,
                           research_bytes, args.assessment_procedure_sha256)
        write_tables(tables, args.output)
        from comparison_figures import render
        render(tables, contract.items, args.output)
        provenance = {"schema_version": 2, "allocation_sha256": sha256(allocation_bytes),
                      "index_sha256": sha256(index_bytes),
                      "registration_sha256": sha256(registration_bytes),
                      "research_procedure_sha256": sha256(research_bytes),
                      "approved_assessment_procedure_sha256": args.assessment_procedure_sha256,
                      "comparison_provenance": index.get("comparison_provenance"),
                      "tool_sha256": sha256(Path(__file__).read_bytes()),
                      "figures_sha256": sha256(Path(__file__).with_name("comparison_figures.py").read_bytes()),
                      "assessment_pin": parse_json(args.assessment_pin.read_bytes()),
                      "checklist": contract.lock, "assigned_workers": len(tables["runs"]),
                      "issues": len(tables["issues"]),
                      "interpretation": "Descriptive only; primary judgments determine worker summaries. "
                      "Duplicates quantify disagreement; missing observations are not verdicts."}
        (args.output / "aggregation.json").write_text(json.dumps(provenance, indent=2) + "\n")
        print(f"{len(tables['runs'])} assigned workers; {len(tables['issues'])} issues; {args.output}")
        return 2 if tables["issues"] else 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(2, f"Aggregation failed: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
