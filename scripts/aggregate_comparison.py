#!/usr/bin/env python3
"""Aggregate coordinator extractions without evaluating or changing research objects."""
import argparse
from contextvars import ContextVar
import csv
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import subprocess

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_LOCATIONS = ContextVar("artifact_locations", default=None)
STATUSES = ("met", "partial", "unmet", "not-checked", "not-applicable")
ADEQUACY = ("supported", "qualified", "not supported", "unable to assess")
DIMENSIONS = tuple("STAMPED")
LEVELS = ("must", "should", "may")
VALUES = dict(zip(STATUSES, ("yes", "no", "no", None, None)))
SHA = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
COMMIT = {"type": "string", "pattern": "^[0-9a-f]{40}([0-9a-f]{24})?$"}
NULLABLE_COMMIT = {"anyOf": [COMMIT, {"type": "null"}]}
TEXT = {"type": "string", "minLength": 1}


def obj(properties, required=()):
    return {"type": "object", "properties": properties, "required": list(required),
            "additionalProperties": False}


ARTIFACT = obj({"path": TEXT, "sha256": SHA}, ("path", "sha256"))
ROUND_BINDINGS_SCHEMA = obj({
    "schema_version": {"const": 1}, "comparison_id": TEXT,
    "allocation_sha256": SHA, "research_procedure_sha256": SHA,
    "rounds": {"type": "array", "minItems": 1, "items": obj({
        "round": {"type": "integer", "minimum": 1},
        "coordinator_source_commit": COMMIT, "research_guidance_commit": COMMIT,
        "source_skill_binding": ARTIFACT,
        "authorization": {"type": "array", "minItems": 1, "items": ARTIFACT},
    }, ("round", "coordinator_source_commit", "research_guidance_commit",
        "source_skill_binding", "authorization"))},
}, ("schema_version", "comparison_id", "allocation_sha256",
    "research_procedure_sha256", "rounds"))
CAPTURE = obj({"uri": TEXT, "sha256": SHA}, ("uri", "sha256"))
EXCERPT = obj({"quote": TEXT, "start_line": {"type": "integer", "minimum": 1},
               "end_line": {"type": "integer", "minimum": 1}},
              ("quote", "start_line", "end_line"))
EXTRACTION = obj({"extraction_status": {"enum": ["explicit", "missing", "ambiguous"]},
                  "category": {"enum": [*ADEQUACY, None]}, "excerpt": EXCERPT},
                 ("extraction_status", "category"))
NATIVE = obj({"procedure_status": ARTIFACT, "result": ARTIFACT})
JUDGMENT = obj({"judgment_id": TEXT, "response": ARTIFACT, "report": ARTIFACT,
                "scientific_report": ARTIFACT,
                "structured_scientific": ARTIFACT,
                "native": NATIVE, "output_binding": ARTIFACT,
                "adequacy": EXTRACTION, "conclusion": EXCERPT}, ("judgment_id",))
SUPPLEMENTARY = obj(dict(JUDGMENT["properties"], reason=TEXT), ("judgment_id", "reason"))
EVIDENCED = {"reason": TEXT, "evidence": {"type": "array", "minItems": 1, "items": ARTIFACT}}
DISPOSITION_SCHEMA = obj({"version": {"const": 1}, "comparison_id": TEXT,
    "allocation_sha256": SHA, "research_procedure_sha256": SHA, "assessment_procedure_sha256": SHA,
    "judgments": {"type": "array", "items": obj({
        "run_id": TEXT, "role": {"enum": ["primary", "duplicate", "supplementary"]},
        "judgment_id": TEXT, "procedure_sha256": SHA, "native_result_sha256": SHA,
        "output_binding_sha256": SHA,
        "measure_validity": {"type": "array", "items": obj(dict(EVIDENCED,
            measure=TEXT, status={"enum": ["unavailable", "invalid"]}),
            ("measure", "status", "reason", "evidence"))},
        "scientific_dependency": obj(dict(EVIDENCED, status={"enum": ["independent", "uncertain"]}),
                                      ("status", "reason", "evidence")),
    }, ("run_id", "role", "judgment_id", "procedure_sha256"))}},
    ("version", "comparison_id", "allocation_sha256", "research_procedure_sha256",
     "assessment_procedure_sha256", "judgments"))
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
    "supplementary_attempt_id": TEXT,
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
INDEX_SCHEMA = obj({"schema_version": {"enum": [2, 3]},
    "comparison_provenance": obj({"assessment_seal": ARTIFACT, "research_procedure_sha256": SHA},
                                  ("assessment_seal", "research_procedure_sha256")),
    "runs": {"type": "array", "items": obj({
    "run_id": TEXT, "result_commit": NULLABLE_COMMIT, "worker_head": NULLABLE_COMMIT,
    "delivery_capture": ARTIFACT,
    "seed_commit": COMMIT, "worker_end_state": ARTIFACT,
    "worker_native": NATIVE, "worker_input": ARTIFACT,
    "retention_commit": COMMIT, "skill_commit": COMMIT,
    "worker_completion": {"enum": ["pending", "completed", "failed", "interrupted", "unknown"]},
    "judgments": obj({"primary": JUDGMENT, "duplicate": JUDGMENT}),
    "excluded_attempts": {"type": "array", "items": EXCLUDED},
    "supplementary_attempts": {"type": "array", "items": SUPPLEMENTARY},
    "operations": {"type": "array", "items": OPERATION},
}, ("run_id",))}}, ("schema_version", "runs"))
INDEX_SCHEMA["allOf"] = [{"if": {"properties": {"schema_version": {"const": 2}}},
    "then": {"properties": {"runs": {"items": {"properties": {
        "result_commit": COMMIT, "worker_head": COMMIT}, "not": {"required": ["delivery_capture"]}}}}}}]


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

    def validate(self, response, result_commit, capture=None):
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
        if "commit" not in response.get("object", {}) or response["object"]["commit"] != result_commit:
            errors.append("object.commit differs from the indexed scientific result")
        if capture is not None:
            identity = response.get("object", {}).get("capture")
            if schema_errors(identity, CAPTURE) or identity["sha256"] != capture["sha256"]:
                errors.append("object.capture differs from the original delivery capture")
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
            rows.append({"run_id": run["run"], "study": allocation.get("study"), "round": round_id,
                         "condition": run["condition"], "replicate": run["replicate"],
                         "launch_order": order, "duplicate_selected": run["run"] in selection,
                         **{k: run[k] for k in ("wave", "launch_position") if k in run}})
    for name, actual in (("total_workers", len(rows)), ("total_primary_judgments", len(rows)),
                         ("total_duplicate_judgments", duplicate_count)):
        if allocation.get(name) != actual:
            raise ValueError("Allocation total mismatch: " + name)
    if "total_judgments" in allocation and allocation["total_judgments"] != len(rows) + duplicate_count:
        raise ValueError("Allocation total mismatch: total_judgments")
    return rows


def allocated_judgments(allocation, runs):
    """Preserve prospective identities when the allocation names each judgment."""
    slots, identities = {}, set()
    for group in allocation["rounds"]:
        if "judgment_dispatch_order" not in group:
            continue
        expected = {(r["run_id"], role) for r in runs if r["round"] == group["round"]
                    for role in (("primary", "duplicate") if r["duplicate_selected"] else ("primary",))}
        found, orders = set(), set()
        for row in group["judgment_dispatch_order"]:
            required_fields(row, {"run": TEXT, "role": {"enum": ["primary", "duplicate"]},
                "judgment": TEXT, "dispatch_order": {"type": "integer", "minimum": 1}})
            key, identity = (row["run"], row["role"]), row["judgment"]
            if key not in expected or key in found or identity in identities or row["dispatch_order"] in orders:
                raise ValueError("Invalid allocated judgment identity or slot")
            found.add(key)
            orders.add(row["dispatch_order"])
            identities.add(identity)
            slots[key] = row
        if found != expected:
            raise ValueError("Incomplete allocated judgment slots")
    return slots


def artifact(reference, base):
    path = Path(reference["path"])
    locations = ARTIFACT_LOCATIONS.get()
    if path.is_absolute() and locations is not None:
        mapped = locations.get(os.path.abspath(path))
        if mapped is None:
            raise ValueError("Absolute artifact missing from source manifest: " + str(path))
        require_equal(reference["sha256"], mapped["sha256"], "relocated artifact identity")
        path = mapped["path"]
    path = (base / path).resolve() if not path.is_absolute() else path.resolve()
    raw = path.read_bytes()
    if sha256(raw) != reference["sha256"]:
        raise ValueError("Artifact SHA-256 mismatch: " + str(path))
    return raw


def source_locations(manifest):
    """Resolve retained copies by original path and digest, without rewriting receipts."""
    raw = manifest.read_bytes()
    rows = parse_json(raw)
    if not isinstance(rows, list):
        raise ValueError("Source manifest must be a list of retained artifact copies")
    locations = {}
    for row in rows:
        required_fields(row, {"source_path": TEXT, "sha256": SHA, "copy": ARTIFACT})
        if not Path(row["source_path"]).is_absolute():
            raise ValueError("Source manifest requires absolute original paths")
        if Path(row["copy"]["path"]).is_absolute():
            raise ValueError("Source manifest requires relative retained-copy paths")
        require_equal(row["sha256"], row["copy"]["sha256"], "retained copy identity")
        # Validate every supplied copy, including repeated identical references.
        artifact(row["copy"], manifest.resolve().parent)
        original = os.path.abspath(row["source_path"])
        location = {"path": manifest.resolve().parent / row["copy"]["path"],
                    "sha256": row["sha256"]}
        if original in locations:
            require_equal(locations[original]["sha256"], row["sha256"], "unique source identity")
        else:
            locations[original] = location
    return locations, {"manifest_sha256": sha256(raw), "mapped_paths": len(locations),
                       "scope": "Explicit byte-location map; original receipt bytes and required digests unchanged"}


def require_equal(actual, expected, label):
    if actual != expected:
        raise ValueError("Provenance mismatch: " + label)


def required_fields(value, properties):
    schema = obj(properties, properties)
    schema["additionalProperties"] = True
    errors = schema_errors(value, schema)
    if errors:
        raise ValueError("Malformed provenance: " + "; ".join(errors))


def round_bindings(config, base, research_bytes, allocation, allocation_sha256, repository):
    """Verify an explicit reporting correction; never rewrite a research seal."""
    if config is None:
        return {}
    errors = schema_errors(config, ROUND_BINDINGS_SCHEMA)
    if errors:
        raise ValueError("Invalid round bindings: " + "; ".join(errors))
    research = parse_json(research_bytes)
    require_equal(research["version"], 3, "round bindings require neutral research")
    for key, expected in (("comparison_id", research["comparison_id"]),
                          ("allocation_sha256", allocation_sha256),
                          ("research_procedure_sha256", sha256(research_bytes))):
        require_equal(config[key], expected, "round binding " + key)

    def git(*args):
        return subprocess.check_output(["git", "--no-replace-objects", "-C", str(repository),
                                        *args], stderr=subprocess.PIPE)

    def tree(revision):
        require_equal(git("cat-file", "-t", revision).strip(), b"commit", "source commit type")
        entries = {}
        for row in git("ls-tree", "-r", "-z", "--full-tree", revision).split(b"\0"):
            if row:
                identity, path = row.split(b"\t", 1)
                entries[path.decode()] = tuple(identity.decode().split())
        return entries

    def modules(revision, entries):
        require_equal(entries.get(".gitmodules", ())[:2], ("100644", "blob"),
                      "regular source .gitmodules")
        result = {}
        for row in git("config", "--blob", revision + ":.gitmodules", "--null", "--list").split(b"\0"):
            if row:
                key, value = row.decode().split("\n", 1)
                if key in result:
                    raise ValueError("Duplicate source .gitmodules key: " + key)
                result[key] = value
        return result

    original = research["coordinator_commit"]
    original_tree = tree(original)
    original_modules = modules(original, original_tree)
    from assessment_procedure import gitmodules_digest
    require_equal(gitmodules_digest(git("show", original + ":.gitmodules")),
                  research["gitmodules_sha256"], "original source .gitmodules digest")
    allocated = {r["round"]: r for r in allocation["rounds"]}
    bindings = {}
    for row in config["rounds"]:
        number = row["round"]
        if number not in allocated or number in bindings:
            raise ValueError("Unknown or duplicate bound round")
        for reference in row["authorization"]:
            if not artifact(reference, base).strip():
                raise ValueError("Empty round authorization artifact")
        receipt = parse_json(artifact(row["source_skill_binding"], base))
        for key, expected in (("round", number), ("comparison_id", research["comparison_id"]),
                ("original_allocation_sha256", allocation_sha256),
                ("research_procedure_sha256", sha256(research_bytes)),
                ("coordinator_source_commit", row["coordinator_source_commit"]),
                ("research_guidance_commit", row["research_guidance_commit"]),
                ("study_input_tree", research["study"]["input_tree"]),
                ("worker_assignments", allocated[number]["launch_order"]),
                ("assigned_judgments", allocated[number]["judgment_dispatch_order"])):
            require_equal(receipt.get(key), expected, "round source receipt " + key)
        source = row["coordinator_source_commit"]
        current_tree = tree(source)
        changed = {p for p in original_tree.keys() | current_tree.keys()
                   if original_tree.get(p) != current_tree.get(p)}
        if changed - {"skills", ".gitmodules"}:
            raise ValueError("Round source changes fixed paths: " + ", ".join(sorted(changed)))
        require_equal(current_tree.get("skills"),
                      ("160000", "commit", row["research_guidance_commit"]),
                      "round source skills gitlink")
        current_modules = modules(source, current_tree)
        branch_key = "submodule.skills.branch"
        require_equal({k: v for k, v in current_modules.items() if k != branch_key},
                      {k: v for k, v in original_modules.items() if k != branch_key},
                      "unchanged non-branch .gitmodules configuration")
        for key, expected in (("submodule.skills.path", "skills"),
                ("submodule.skills.url", receipt.get("research_guidance_repository")),
                (branch_key, receipt.get("research_guidance_branch"))):
            require_equal(current_modules.get(key), expected, "round skills " + key)
        for path, digest in research["fixed_files"].items():
            require_equal(sha256(git("show", source + ":" + path)), digest,
                          "round frozen file " + path)
        bindings[number] = row
    return bindings


@dataclass
class ProvenanceGate:
    """Bind extractions to a selected seal and independently retained registration."""
    research: dict
    research_sha256: str
    seal: dict = None
    seal_sha256: str = None
    rounds: dict = None

    @property
    def neutral(self):
        return self.research["version"] == 3

    @classmethod
    def load(cls, original_bytes, selection, allocation, base, contract, approved_digest=None, rounds=None):
        if original_bytes is None:
            raise ValueError("Original registered research procedure is required")
        research = parse_json(original_bytes)
        required_fields(research, {"version": {"enum": [1, 3]}, "status": {"const": "sealed"},
                                   "comparison_id": TEXT, "conditions": {"type": "array"},
                                   "assessment": {"type": "object"}})
        require_equal(research["conditions"], allocation["conditions"], "registered conditions")
        if "comparison_id" in allocation:
            require_equal(research["comparison_id"], allocation["comparison_id"], "allocated comparison")
        gate = cls(research, sha256(original_bytes), rounds=rounds)
        if selection is None:
            return gate
        if approved_digest is None:
            raise ValueError("Independent approved assessment procedure digest is required")
        require_equal(selection["assessment_seal"]["sha256"], approved_digest,
                      "approved assessment procedure digest")
        require_equal(selection["research_procedure_sha256"], gate.research_sha256,
                      "registered research digest")
        seal = parse_json(artifact(selection["assessment_seal"], base))
        if gate.neutral:
            required_fields(research, {"protocol": {"const": "neutral-v1"}})
            if seal.get("version") == 4:
                import assessment_procedure as procedure
                required_fields(seal, {"status": {"const": "sealed"},
                                      "protocol": {"const": "neutral-v1"}})
                try:
                    embedded = procedure.operational_research_procedure(seal)
                except SystemExit as error:
                    raise ValueError(str(error)) from error
                amendment = seal["assessment_amendment"]
                require_equal(amendment["research_procedure_json"].encode(), original_bytes,
                              "original neutral research bytes")
                require_equal(embedded, research, "original neutral research identity")
                require_equal(parse_json(amendment["allocation_json"]), allocation, "original allocation")
                require_equal(contract.assessment_pin, research["assessment"], "unchanged neutral assessor pin")
                gate.seal, gate.seal_sha256 = seal, selection["assessment_seal"]["sha256"]
                return gate
            require_equal(selection["assessment_seal"]["sha256"], gate.research_sha256,
                          "neutral original assessment seal")
            require_equal(contract.assessment_pin, research["assessment"], "loaded neutral assessor pin")
            gate.seal, gate.seal_sha256 = seal, gate.research_sha256
            return gate
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
                              ("head_commit", stop["head_commit"]),
                              ("capture_status", stop["capture_status"])):
            require_equal(result["worker_end_state"].get(key), expected, "worker stop " + key)
        seed = parse_json(artifact(run["worker_input"], base))
        if self.neutral:
            binding = self.rounds.get(assignment["round"]) if self.rounds else None
            source = binding["coordinator_source_commit"] if binding else self.research["coordinator_commit"]
            if binding:
                expected_skill = (binding["research_guidance_commit"]
                                  if assignment["condition"] == "stamped-explicit" else None)
                require_equal(seed.get("skills_commit"), expected_skill, "bound worker supplied skills")
                if expected_skill is not None and "skill_commit" in run:
                    require_equal(run["skill_commit"], expected_skill, "indexed supplied research skills")
            required_fields(seed, {"version": {"const": 3}, "protocol": {"const": "neutral-v1"},
                "run": TEXT, "condition": TEXT, "seed_commit": COMMIT,
                "coordinator_commit": COMMIT, "study_input_tree": COMMIT,
                "common_prompt_sha256": SHA, "common_resources_sha256": SHA})
            for key, expected in (("run", run["run_id"]), ("condition", assignment["condition"]),
                                  ("seed_commit", run["seed_commit"]),
                                  ("coordinator_commit", source),
                                  ("study_input_tree", self.research["study"]["input_tree"]),
                                  ("common_prompt_sha256", self.research["fixed_files"][
                                      "prompts/neutral-worker-common.md"]),
                                  ("common_resources_sha256", self.research["common_resources_sha256"])):
                require_equal(seed[key], expected, "neutral worker input " + key)
            for key in ("seed_commit", "study_input_tree", "common_prompt_sha256", "common_resources_sha256"):
                require_equal(stop["seed_identities"].get(key), seed[key], "captured seed " + key)
            require_equal(result["worker_end_state"].get("capture"), stop["capture"], "native worker capture")
            return
        required_fields(seed, {"version": {"const": 2}, "run": TEXT, "condition": TEXT,
                              "study_input_tree": COMMIT, "source_manifest_sha256": SHA})
        for key, expected in (("run", run["run_id"]), ("condition", assignment["condition"]),
                              ("study_input_tree", self.research["study"]["input_tree"]),
                              ("source_manifest_sha256", self.research["fixed_files"]["pixi.toml"])):
            require_equal(seed[key], expected, "worker input " + key)

    def validate(self, run, native, base, assignment, *, excluded=False, procedure_digest=None):
        if not excluded and self.seal is None:
            raise ValueError("Included judgment requires the approved assessment seal")
        for key in ("seed_commit", "result_commit", "worker_end_state"):
            if key not in run:
                raise ValueError("Judgment provenance requires run " + key)
        stop = parse_json(artifact(run["worker_end_state"], base))
        if self.neutral:
            self.validate_capture_identity(run, stop, base)
        else:
            required_fields(stop, {"schema_version": {"const": 1}, "kind": {"const": "worker-end-state"},
                "capture_status": {"const": "complete"}, "errors": {"const": []}, "head_commit": COMMIT})
        if "worker_head" in run:
            require_equal(stop["head_commit"], run["worker_head"], "original worker head")
        retained_match = False
        if self.neutral:
            self.validate_worker(run, stop, base, assignment)
        elif not excluded:
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
        digest = procedure_digest or (self.research_sha256 if excluded else self.seal_sha256)
        if digest not in (self.research_sha256, self.seal_sha256):
            raise ValueError("Judgment names an unapproved assessment version")
        original_version = digest == self.research_sha256
        operational = bool(not original_version and self.neutral and self.seal.get("version") == 4)
        require_equal(status["procedure_sha256"], digest, "assessment procedure digest")
        if not original_version or "research_procedure_sha256" in status:
            require_equal(status.get("research_procedure_sha256"), self.research_sha256,
                          "native original research digest")
        require_equal(status["worker_end_state_sha256"], run["worker_end_state"]["sha256"],
                      "native original worker stop")
        result = parse_json(artifact(native["result"], base))
        required_fields(result, {"role": {"const": "judge"}, "condition": {"type": "null"},
            "procedure": {"type": "object"},
            "assessment_pin": {"type": "object"}, "target": {"type": "object"},
            "target_unchanged": {"type": "boolean"} if operational else {"const": True},
            "returncode": {"type": "integer"},
            "finished_at": {"type": "string", "format": "date-time"},
            "native_session_ids": {"type": "array", "minItems": 1, "uniqueItems": True,
                                   "items": {"type": "string", "format": "uuid"}}})
        require_equal(result["procedure"], status, "result/procedure-status receipt identity")
        expected_pin = self.research["assessment"] if original_version else self.seal["assessment"]
        require_equal(result["assessment_pin"], expected_pin, "native assessor source/runtime pin")
        if self.neutral:
            required_fields(result["target"], {"schema_version": {"const": 3 if operational else 2}, "target_path": TEXT,
                                               "target_commit": NULLABLE_COMMIT, "capture": CAPTURE})
            require_equal(result["target"]["capture"]["sha256"], run["delivery_capture"]["sha256"],
                          "native original delivery capture")
            if operational:
                self.validate_operational(run, result, base)
        else:
            required_fields(result["target"], {"schema_version": {"const": 1}, "target_path": TEXT,
                                               "target_commit": COMMIT, "target_tree": COMMIT})
        require_equal(result["target"]["target_commit"], run["result_commit"], "native scientific target")
        return {"procedure_sha256": digest, "research_procedure_sha256": self.research_sha256,
                "worker_end_state_sha256": run["worker_end_state"]["sha256"],
                "assessment_pin": expected_pin, "native_session_ids": result["native_session_ids"],
                "target": result["target"], "returncode": result["returncode"],
                "finished_at": result["finished_at"], **({"original_delivery": {
                    key: stop[key] for key in ("capture", "capture_status", "head_commit", "errors", "omissions")
                }} if self.neutral else {}), **({"assessment_version": 4,
                    "operational_integrity": result["operational_integrity"]} if operational else {})}

    def validate_operational(self, run, result, base):
        """Admit v4 explicitly; the original v3 exact-target gate is unchanged."""
        from delivery_snapshot import operational_delta, OPERATIONAL_METADATA, OPAQUE_GIT_POLICY
        import assessment_procedure as procedure
        matches = [row for row in self.seal["assessment_amendment"]["retained_objects"]
                   if row["run"] == run["run_id"]]
        if len(matches) != 1:
            raise ValueError("Operational judgment requires its prebound original retained object")
        retained = matches[0]
        for key in ("seed_commit", "result_commit"):
            require_equal(run[key], retained[key], "operational retained " + key)
        for key in ("worker_end_state", "delivery_capture"):
            require_equal(run[key]["sha256"], retained[key + "_sha256"], "operational retained " + key)
        required_fields(result, {"canonical_unchanged": {"const": True},
            "operational_metadata_changed": {"type": "boolean"}, "operational_integrity": {"type": "object"},
            "operational_runtime": {"type": "object"}, "git_config_overlay": {"type": "object"}})
        require_equal(result["operational_runtime"], procedure.OPERATIONAL_RUNTIME, "native operational runtime")
        require_equal(result["procedure"].get("operational_runtime"), procedure.OPERATIONAL_RUNTIME,
                      "procedure operational runtime")
        overlay = result["git_config_overlay"]
        required_fields(overlay, {"inherited_count": {"type": "integer", "minimum": 0},
            "effective_count": {"type": "integer", "minimum": 2}, "appended": {"type": "object"},
            "GIT_OPTIONAL_LOCKS": {"const": "0"}})
        require_equal(overlay["appended"], procedure.OPERATIONAL_RUNTIME["git_config"], "native Git overlay")
        require_equal(overlay["effective_count"], overlay["inherited_count"] + 2, "preserved Git overlay")
        target = result["target"]
        required_fields(target, {"operational_capture": CAPTURE, "canonical_target_path": TEXT,
            "operational_container_modes": {"type": "object"}, "canonical_container_modes": {"type": "object"}})
        require_equal(target["operational_capture"]["sha256"], run["delivery_capture"]["sha256"],
                      "initial complete operational copy")
        if target["operational_capture"]["uri"] == target["capture"]["uri"]:
            raise ValueError("Operational and canonical capture must be separate")
        integrity = result["operational_integrity"]
        required_fields(integrity, {"schema_version": {"const": 1},
            "kind": {"const": "assessment-operational-integrity"},
            "canonical_unchanged": {"const": True}, "protected_unchanged": {"const": True},
            "canonical_capture": CAPTURE, "operational_initial_sha256": SHA,
            "capture_status": {"const": "complete"}, "errors": {"const": []}, "omissions": {"const": []},
            "final_capture": ARTIFACT, "delta": ARTIFACT})
        require_equal(integrity["canonical_capture"], target["capture"], "canonical identity at stop")
        require_equal(integrity["operational_initial_sha256"], run["delivery_capture"]["sha256"],
                      "operational baseline identity")
        final = parse_json(artifact(integrity["final_capture"], base))
        required_fields(final, {"schema": {"const": "original-delivery-v1"},
            "kind": {"const": "retained-container"},
            "policy": {"type": "object", "properties": {
                "git_dependencies": {"const": OPAQUE_GIT_POLICY}}, "required": ["git_dependencies"]},
            "workspace": {"const": "content/workspace"}, "capture_status": {"const": "complete"},
            "errors": {"const": []}, "omissions": {"const": []}, "entries": {"type": "array"}})
        delta, permitted, rejected = operational_delta(artifact(run["delivery_capture"], base), final,
                                                       target["operational_container_modes"])
        if rejected:
            raise ValueError("Protected operational content changed: " + str(rejected))
        expected = {"canonical_capture": target["capture"],
            "operational_initial_sha256": run["delivery_capture"]["sha256"], "delta": delta,
            "permitted_metadata_changes": permitted, "rejected_changes": [],
            "logical_database_equivalence": "not-claimed"}
        require_equal(parse_json(artifact(integrity["delta"], base)), expected, "full operational delta")
        for key, value in {"permitted_metadata_changes": permitted, "rejected_changes": [],
                "permitted_metadata_paths": sorted(OPERATIONAL_METADATA),
                "logical_database_equivalence": "not-claimed", "target_unchanged": not any(delta.values()),
                "operational_metadata_changed": bool(permitted)}.items():
            require_equal(integrity.get(key), value, "operational integrity " + key)
        for key in ("target_unchanged", "canonical_unchanged", "operational_metadata_changed"):
            require_equal(result[key], integrity[key], "native " + key)

    def validate_capture_identity(self, run, stop, base):
        """Bind retained manifest bytes without executing or rechecking worker files."""
        for key in ("worker_head", "delivery_capture"):
            if key not in run:
                raise ValueError("Neutral judgment provenance requires run " + key)
        required_fields(stop, {"schema_version": {"const": 2}, "kind": {"const": "worker-end-state"},
            "capture_status": {"enum": ["complete", "partial"]}, "head_commit": NULLABLE_COMMIT,
            "capture": CAPTURE, "seed_identities": {"type": "object"},
            "errors": {"type": "array"}, "omissions": {"type": "array"}})
        require_equal(run["result_commit"], stop["head_commit"], "original delivery Git identity")
        require_equal(run["delivery_capture"]["sha256"], stop["capture"]["sha256"], "original capture digest")
        manifest = parse_json(artifact(run["delivery_capture"], base))
        required_fields(manifest, {"schema": {"const": "original-delivery-v1"},
            "kind": {"const": "original-delivery"}, "workspace": {"const": "content/workspace"},
            "head_commit": NULLABLE_COMMIT, "capture_status": {"enum": ["complete", "partial"]},
            "errors": {"type": "array"}, "omissions": {"type": "array"}})
        for key in ("head_commit", "capture_status", "errors", "omissions"):
            require_equal(manifest[key], stop[key], "capture manifest " + key)
        if manifest["capture_status"] == "complete" and (manifest["errors"] or manifest["omissions"]):
            raise ValueError("Complete capture has errors or omissions")


def validate_output_binding(supplied, check, base):
    """Verify a retained coordinator attribution; native receipts do not hash outputs."""
    if not any(key in supplied for key in ("response", "report", "scientific_report", "structured_scientific", "adequacy", "conclusion")):
        return
    if "output_binding" not in supplied:
        raise ValueError("Outcome extraction requires a retained output_binding manifest")
    binding = parse_json(artifact(supplied["output_binding"], base))
    required_fields(binding, {"schema_version": {"const": 1},
        "kind": {"const": "coordinator-assessment-output-binding"},
        "native_result_sha256": SHA, "native_session_ids": {"type": "array"},
        "outputs": obj({"response": ARTIFACT, "report": ARTIFACT, "scientific_report": ARTIFACT,
                        "structured_scientific": ARTIFACT})})
    require_equal(binding["native_result_sha256"], supplied["native"]["result"]["sha256"],
                  "bound native result bytes")
    require_equal(binding["native_session_ids"], check["native_session_ids"], "bound native sessions")
    for key in ("response", "report", "scientific_report", "structured_scientific"):
        if key in supplied:
            require_equal(binding["outputs"].get(key, {}).get("sha256"), supplied[key]["sha256"],
                          "bound " + key + " bytes")


def validate_structured_scientific(supplied, check, base):
    """A v4 reporting-format failure affects scientific measures only."""
    from scientific_judgment import parse_record, validate_excerpt
    if "structured_scientific" not in supplied:
        raise ValueError("Version 4 scientific measures require scientific-judgment.json")
    # Original workspace validation uses validate_record. Retained objects may
    # be annex links or have different storage paths; bind their bytes without
    # claiming publication layout equivalence.
    structured = parse_record(artifact(supplied["structured_scientific"], base))
    require_equal(structured["delivery_capture_sha256"],
                  check["original_delivery"]["capture"]["sha256"], "structured original capture")
    require_equal(supplied.get("scientific_report", {}).get("sha256"),
                  structured["report"]["sha256"], "structured scientific report")
    report = artifact(supplied["scientific_report"], base).decode("utf-8")
    validate_excerpt(structured["adequacy_evidence"], report)
    if structured["hypothesis_conclusion"] is not None:
        validate_excerpt(structured["hypothesis_conclusion"], report)
    require_equal(supplied.get("adequacy"), {"extraction_status": "explicit",
        "category": structured["scientific_adequacy"], "excerpt": structured["adequacy_evidence"]},
        "explicit scientific category")
    require_equal(supplied.get("conclusion"), structured["hypothesis_conclusion"], "verbatim hypothesis conclusion")


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


def disposition_rows(disposition, allocation, allocation_digest, gate, contract):
    """Read the coordinator's analysis decisions; never infer validity from grades."""
    if disposition is None:
        return {}
    errors = schema_errors(disposition, DISPOSITION_SCHEMA)
    if errors:
        raise ValueError("Invalid measurement disposition: " + "; ".join(errors))
    if isinstance(gate, str) or gate.seal is None:
        raise ValueError("Measurement disposition requires the registered original and current seals")
    for key, expected in (("allocation_sha256", allocation_digest),
            ("comparison_id", gate.research["comparison_id"]),
            ("research_procedure_sha256", gate.research_sha256),
            ("assessment_procedure_sha256", gate.seal_sha256)):
        require_equal(disposition[key], expected, "measurement disposition " + key)
    assigned = {r["run_id"]: r for r in allocation_rows(allocation)}
    planned = allocated_judgments(allocation, assigned.values())
    rows, ids = {}, set()
    for row in disposition["judgments"]:
        run_id, role, identity = row["run_id"], row["role"], row["judgment_id"]
        if run_id not in assigned or (role == "duplicate" and not assigned[run_id]["duplicate_selected"]):
            raise ValueError("Disposition names an unassigned slot: " + run_id + "/" + role)
        if (run_id, role) in planned:
            require_equal(identity, planned[run_id, role]["judgment"], "disposition allocated judgment")
        key = (run_id, role, identity if role == "supplementary" else None)
        if key in rows or identity in ids:
            raise ValueError("Repeated disposition slot or judgment identity")
        if row["procedure_sha256"] not in (gate.research_sha256, gate.seal_sha256):
            raise ValueError("Disposition names an unapproved assessment version")
        measures = [v["measure"] for v in row.get("measure_validity", [])]
        if not set(measures) <= {"replay", *(i["id"] for i in contract.items)}:
            raise ValueError("Validity decision names an unknown pinned measure")
        if len(measures) != len(set(measures)):
            raise ValueError("Repeated measure validity decision")
        rows[key], ids = row, ids | {identity}
    return rows


def comparable_cell_summary(counts, items, identities, kind, group, status):
    """Status-count summaries require identical valid item identities, not just sizes."""
    selected = [c for c in counts if c["role"] == "primary" and c["judgment_id"] in identities
                and c["group_type"] == kind and c["group"] == group]
    masks = {frozenset(i["item_id"] for i in items if i["judgment_id"] == c["judgment_id"] and
                      (i["level"] == group if kind == "level" else group in i["dimension"]))
             for c in selected}
    comparable = len(masks) == 1 and bool(next(iter(masks)))
    values = [c[status] for c in selected] if comparable else []
    return dict(n_observed=len(selected), n_comparable=len(values),
        common_valid_item_ids=sorted(next(iter(masks))) if comparable else [],
        summary_status=("comparable" if comparable else "different or absent valid item sets"),
        median=statistics.median(values) if values else None,
        minimum=min(values) if values else None, maximum=max(values) if values else None)


def aggregate(allocation, index, base, contract, research_procedure=None, assessment_procedure_sha256=None,
              *, disposition=None, disposition_base=None, allocation_sha256=None,
              round_binding_config=None, round_binding_base=None, source_repository=ROOT):
    errors = schema_errors(index, INDEX_SCHEMA)
    if errors:
        raise ValueError("Invalid extraction index:\n" + "\n".join(errors))
    runs = allocation_rows(allocation)
    bound_rounds = round_bindings(round_binding_config, round_binding_base or base,
        research_procedure, allocation, allocation_sha256, source_repository)
    planned_judgments = allocated_judgments(allocation, runs)
    planned_ids = {row["judgment"] for row in planned_judgments.values()}
    assigned = {r["run_id"]: r for r in runs}
    indexed, judgment_ids, operation_ids = {}, set(), set()
    for run in index["runs"]:
        run_id = run["run_id"]
        if run_id not in assigned or run_id in indexed:
            raise ValueError("Unknown or repeated indexed run: " + run_id)
        indexed[run_id] = run
        if "duplicate" in run.get("judgments", {}) and not assigned[run_id]["duplicate_selected"]:
            raise ValueError("Duplicate judgment was not preselected: " + run_id)
        for role, judgment in run.get("judgments", {}).items():
            planned = planned_judgments.get((run_id, role))
            if planned:
                require_equal(judgment["judgment_id"], planned["judgment"], "allocated judgment identity")
        for judgment in [*run.get("excluded_attempts", []), *run.get("supplementary_attempts", [])]:
            if judgment["judgment_id"] in planned_ids:
                raise ValueError("Allocated judgment must remain in its assigned slot")
        for judgment in [*run.get("judgments", {}).values(), *run.get("excluded_attempts", []),
                         *run.get("supplementary_attempts", [])]:
            identity = judgment["judgment_id"]
            if identity in judgment_ids:
                raise ValueError("Repeated judgment ID: " + identity)
            judgment_ids.add(identity)
            if ("result_commit" not in run and set(judgment) != {"judgment_id"}
                    and judgment in run.get("judgments", {}).values()):
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
            if "supplementary_attempt_id" in op:
                if "judgment_role" in op or "excluded_attempt_id" in op:
                    raise ValueError("Supplementary operation cannot occupy another judgment role")
                if op["supplementary_attempt_id"] not in {j["judgment_id"] for j in run.get("supplementary_attempts", [])}:
                    raise ValueError("Unknown supplementary attempt operation reference")
    tables = {name: [] for name in ("runs", "judgments", "items", "counts", "operations",
        "effort", "issues", "disagreement", "pairs", "cells", "excluded_attempts",
        "supplementary_attempts", "supplementary_items", "measure_validity", "comparable_items",
        "comparable_counts", "version_strata", "version_cells")}
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
                assessment_procedure_sha256, rounds=bound_rounds)
            if gates[excluded].neutral != (index["schema_version"] == 3):
                raise ValueError("Neutral procedures require extraction index schema_version 3")
            if gates[excluded].neutral and len(planned_judgments) != len(runs) + sum(
                    r["duplicate_selected"] for r in runs):
                raise ValueError("Neutral allocation must name every assigned judgment slot")
        except (OSError, ValueError, TypeError, KeyError) as error:
            gates[excluded] = str(error)
    if "comparison_provenance" in index and isinstance(gates[False], str):
        issue("", "", "comparison-provenance", gates[False])
    decisions = disposition_rows(disposition, allocation, allocation_sha256, gates[False], contract)
    disposition_base = disposition_base or base

    def decision_for(run_id, role, identity=None):
        return decisions.get((run_id, role, identity if role == "supplementary" else None))

    for run_id, record in indexed.items():
        entries = [(role, j, False) for role, j in record.get("judgments", {}).items()]
        entries += [("excluded", j, True) for j in record.get("excluded_attempts", [])]
        entries += [("supplementary", j, False) for j in record.get("supplementary_attempts", [])]
        for role, supplied, excluded in entries:
            identity = supplied["judgment_id"]
            check = dict(inclusion_status="pending")
            checks[identity] = check
            decision = decision_for(run_id, role, identity)
            if decision:
                check["procedure_sha256"] = decision["procedure_sha256"]
            if not excluded and set(supplied) == {"judgment_id"}:
                if decision and decision["judgment_id"] != identity:
                    check.update(inclusion_status="invalid", provenance_error="Disposition judgment ID differs from slot")
                continue
            try:
                gate = gates[excluded]
                if isinstance(gate, str):
                    raise ValueError(gate)
                if "native" not in supplied:
                    raise ValueError("Judgment requires hashed native procedure-status and finalized result")
                if not excluded and disposition is not None:
                    if decision is None:
                        raise ValueError("Completed judgment has no exact disposition slot")
                    require_equal(identity, decision["judgment_id"], "disposition judgment ID")
                    require_equal(supplied["native"]["result"]["sha256"], decision.get("native_result_sha256"),
                                  "disposition finalized native result")
                    if any(k in supplied for k in ("response", "report", "scientific_report", "adequacy", "conclusion")):
                        require_equal(supplied.get("output_binding", {}).get("sha256"),
                                      decision.get("output_binding_sha256"), "disposition output binding")
                elif role == "supplementary":
                    raise ValueError("Supplementary attempt requires an explicit disposition")
                check.update(gate.validate(record, supplied["native"], base, assigned[run_id], excluded=excluded,
                    procedure_digest=decision["procedure_sha256"] if decision else None))
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
        for role, supplied in [*record.get("judgments", {}).items(),
                               *(("supplementary", j) for j in record.get("supplementary_attempts", []))]:
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
                     "worker_native", "worker_input", "delivery_capture", "retention_commit", "skill_commit")})
        tables["runs"].append(row)
        slots = [(role, record.get("judgments", {}).get(role, {})) for role in (
            ("primary", "duplicate") if assignment["duplicate_selected"] else ("primary",))]
        slots += [("supplementary", j) for j in record.get("supplementary_attempts", [])]
        for role, supplied in slots:
            planned = planned_judgments.get((run_id, role), {})
            decision = decision_for(run_id, role, supplied.get("judgment_id"))
            judgment = dict(assignment, role=role, judgment_id=supplied.get("judgment_id", planned.get("judgment")),
                            result_commit=record.get("result_commit"), response_status="pending",
                            adequacy=None, extraction_status="missing", conclusion=None)
            if planned:
                judgment["dispatch_order"] = planned["dispatch_order"]
            if "delivery_capture" in record:
                judgment.update(worker_head=record.get("worker_head"), delivery_capture=record["delivery_capture"],
                                retention_commit=record.get("retention_commit"))
            if disposition is not None:
                judgment["procedure_sha256"] = (decision["procedure_sha256"] if decision
                                                  else assessment_procedure_sha256)
                if not supplied and decision:
                    judgment["judgment_id"] = decision["judgment_id"]
            judgment.update({k: supplied.get(k) for k in ("response", "report", "native", "output_binding")})
            judgment.update(checks.get(supplied.get("judgment_id"), {"inclusion_status": "pending"}))
            if role == "supplementary":
                judgment.update(reason=supplied["reason"], comparison_outcomes_included=False)
                tables["supplementary_attempts"].append(judgment)
            else:
                tables["judgments"].append(judgment)
                judgments_by_slot[run_id, role] = judgment
            if decision:
                common = dict(run_id=run_id, role=role, judgment_id=decision["judgment_id"],
                              procedure_sha256=decision["procedure_sha256"])
                for overlay in decision.get("measure_validity", []):
                    validity = dict(common, item_id=overlay["measure"], validity=overlay["status"],
                                    reason=overlay["reason"], evidence=overlay["evidence"], evidence_status="valid")
                    try:
                        for evidence in overlay["evidence"]:
                            artifact(evidence, disposition_base)
                    except (OSError, ValueError) as error:
                        validity["evidence_status"] = "invalid"
                        issue(run_id, role, "measure-validity:" + overlay["measure"], error)
                    tables["measure_validity"].append(validity)
                if "scientific_dependency" in decision:
                    judgment["scientific_dependency"] = dict(decision["scientific_dependency"], evidence_status="valid")
                    try:
                        for evidence in decision["scientific_dependency"]["evidence"]:
                            artifact(evidence, disposition_base)
                    except (OSError, ValueError) as error:
                        judgment["scientific_dependency"]["evidence_status"] = "invalid"
                        issue(run_id, role, "scientific-dependency", error)
            if judgment["inclusion_status"] != "eligible":
                if judgment["inclusion_status"] == "invalid":
                    judgment.update(response_status="invalid", extraction_status="invalid")
                continue
            if "response" in supplied:
                try:
                    response = parse_json(artifact(supplied["response"], base))
                    problems = contract.validate(response, record["result_commit"], record.get("delivery_capture"))
                    if problems:
                        raise ValueError("; ".join(problems))
                except (OSError, ValueError, TypeError) as error:
                    judgment["response_status"] = "invalid"
                    issue(run_id, role, "response", error)
                else:
                    judgment["response_status"] = "valid"
                    judgment["object"] = response["object"]
                    if role != "supplementary":
                        answers_by_slot[run_id, role] = response["responses"]
                    for item in contract.items:
                        answer = response["responses"][item["id"]]
                        fields = ("status", "reason", "source", "evidence", "flags", "value")
                        normalized = dict(run_id=run_id, role=role,
                            judgment_id=supplied["judgment_id"], item_id=item["id"],
                            level=item["level"], principle_codes=item["principle_codes"],
                            dimension=item["dimension"])
                        normalized["procedure_sha256"] = judgment.get("procedure_sha256")
                        normalized.update({k: answer[k] for k in fields if k in answer})
                        extensions = {k: v for k, v in answer.items() if k not in fields}
                        if extensions:
                            normalized["answer_extensions"] = extensions
                        tables["supplementary_items" if role == "supplementary" else "items"].append(normalized)
                    for kind, groups in (("level", LEVELS), ("dimension", DIMENSIONS)):
                        for group in groups:
                            selected = [i for i in contract.items if
                                (i["level"] == group if kind == "level" else group in i["dimension"])]
                            counts = {s: sum(response["responses"][i["id"]]["status"] == s
                                             for i in selected) for s in STATUSES}
                            if role == "supplementary":
                                continue
                            tables["counts"].append(dict(run_id=run_id, role=role,
                                judgment_id=supplied["judgment_id"], group_type=kind, group=group,
                                procedure_sha256=judgment.get("procedure_sha256"),
                                n_pinned=len(selected),
                                n_applicable=len(selected) - counts["not-applicable"], **counts))
            extraction = supplied.get("adequacy", {"extraction_status": "missing", "category": None})
            report = None
            report_error = None
            structured_error = None
            if judgment.get("assessment_version") == 4:
                try:
                    validate_structured_scientific(supplied, judgment, base)
                except (OSError, ValueError, TypeError, KeyError) as error:
                    structured_error = str(error)
            try:
                reports = {key: artifact(supplied[key], base).decode()
                           for key in ("report", "scientific_report") if key in supplied}
                narrative_key = "scientific_report" if "scientific_report" in supplied else "report"
                report = reports.get(narrative_key)
                if report is not None:
                    judgment["narrative_source"] = dict(supplied[narrative_key])
            except (OSError, ValueError, UnicodeError) as error:
                report_error = str(error)
                issue(run_id, role, "report", error)
            try:
                status = extraction["extraction_status"]
                if structured_error:
                    raise ValueError(structured_error)
                if report_error:
                    raise ValueError("Report is invalid; narrative extraction cannot be verified")
                if status == "explicit":
                    if report is None or "excerpt" not in extraction or extraction["category"] is None:
                        raise ValueError("Explicit adequacy requires report, category and excerpt")
                    context = excerpt_context(extraction["excerpt"], report)
                    for text in (() if judgment.get("assessment_version") == 4 else
                                 (extraction["excerpt"]["quote"], context)):
                        # Inspect the complete cited lines too: quoting only "supported"
                        # from "not supported" must never reverse a judge's verdict.
                        plain = re.sub(r"[*_'\"\x60]", "", text.casefold())
                        # An explicit leading scientific-adequacy label identifies
                        # the verdict even if the same paragraph separately says
                        # that the study's positive hypothesis is not supported.
                        labels = set(re.findall(
                            r"^\s*(?:#+\s*)?scientific adequacy\s*:\s*"
                            r"(not supported|unable to assess|supported|qualified)(?!\w)", plain, re.M))
                        categories = (labels if labels else set(re.findall(
                            r"(?<!\w)(not supported|unable to assess|supported|qualified)(?!\w)", plain)))
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
                    if structured_error:
                        raise ValueError(structured_error)
                    if report is None:
                        raise ValueError("Conclusion requires a hashed report")
                    judgment["conclusion"] = excerpt_text(supplied["conclusion"], report)
                    judgment["conclusion_excerpt"] = supplied["conclusion"]
                except (OSError, ValueError, UnicodeError) as error:
                    issue(run_id, role, "conclusion", error)
        for operation in record.get("operations", []):
            excluded_id = operation.get("excluded_attempt_id")
            supplementary_id = operation.get("supplementary_attempt_id")
            scope = "excluded infrastructure attempt" if excluded_id else (
                "supplementary attempt" if supplementary_id else (
                "assigned comparison" if operation.get("judgment_role") else "other operations"))
            op = dict(assignment, **operation, evidence_status="valid", assessment_scope=scope)
            if supplementary_id or excluded_id:
                op["procedure_sha256"] = checks[supplementary_id or excluded_id].get("procedure_sha256")
            elif operation.get("judgment_role"):
                op["procedure_sha256"] = judgments_by_slot[run_id, operation["judgment_role"]].get("procedure_sha256")
            try:
                if excluded_id and checks[excluded_id]["inclusion_status"] != "excluded":
                    raise ValueError("Excluded attempt provenance is invalid; cost is unverified")
                if supplementary_id and checks[supplementary_id]["inclusion_status"] != "eligible":
                    raise ValueError("Supplementary attempt provenance is invalid; cost is unverified")
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
    invalid_measures = {(v["run_id"], v["role"], v["item_id"]): v
                        for v in tables["measure_validity"] if v["role"] != "supplementary"}
    tables["comparable_items"] = [dict(i) for i in tables["items"]
        if (i["run_id"], i["role"], i["item_id"]) not in invalid_measures]
    for count in tables["counts"]:
        items = [i for i in tables["items"] if i["judgment_id"] == count["judgment_id"] and (
            i["level"] == count["group"] if count["group_type"] == "level" else count["group"] in i["dimension"])]
        valid = [i for i in items if (i["run_id"], i["role"], i["item_id"]) not in invalid_measures]
        overlays = [invalid_measures[i["run_id"], i["role"], i["item_id"]] for i in items
                    if (i["run_id"], i["role"], i["item_id"]) in invalid_measures]
        values = {s: sum(i["status"] == s for i in valid) for s in STATUSES}
        tables["comparable_counts"].append(dict(count, **values, n_valid=len(valid),
            n_applicable=len(valid) - values["not-applicable"],
            n_unavailable=sum(v["validity"] == "unavailable" for v in overlays),
            n_invalid=sum(v["validity"] == "invalid" for v in overlays)))

    def scientific_comparable(judgment):
        dependency = judgment.get("scientific_dependency", {})
        return judgment["adequacy"] is not None and dependency.get("status") != "uncertain" and (
            dependency.get("evidence_status", "valid") == "valid")

    for assignment in runs:
        if not assignment["duplicate_selected"]:
            continue
        run_id = assignment["run_id"]
        primary = answers_by_slot.get((run_id, "primary"))
        duplicate = answers_by_slot.get((run_id, "duplicate"))
        first, second = (judgments_by_slot[run_id, role] for role in ("primary", "duplicate"))
        available = primary is not None and duplicate is not None
        same_version = first.get("procedure_sha256") == second.get("procedure_sha256")
        comparable = [item for item in contract.items if all(
            (run_id, role, item["id"]) not in invalid_measures for role in ("primary", "duplicate"))
            ] if available and same_version else []
        paired = available and same_version and len(comparable) == len(contract.items)
        scientific = same_version and scientific_comparable(first) and scientific_comparable(second)
        unavailable_reason = ("missing or invalid response" if not available else (
            "cross-version pair" if not same_version else (
            "one or more measures unavailable or invalid" if not paired else None)))
        pair = dict(assignment, item_pair_complete=paired, item_denominator=len(contract.items),
                    comparable_item_count=len(comparable), comparison_unavailable_reason=unavailable_reason,
                    procedure_sha256=first.get("procedure_sha256"),
                    duplicate_procedure_sha256=second.get("procedure_sha256"),
                    primary_id=first["judgment_id"], duplicate_id=second["judgment_id"],
                    item_disagreements=None, primary_adequacy=first["adequacy"],
                    duplicate_adequacy=second["adequacy"], adequacy_pair_complete=scientific,
                    adequacy_disagreement=(first["adequacy"] != second["adequacy"]) if scientific else None)
        if comparable:
            pair["item_disagreements"] = 0
            for item in comparable:
                a, b = primary[item["id"]]["status"], duplicate[item["id"]]["status"]
                mismatch = a != b
                pair["item_disagreements"] += mismatch
                tables["disagreement"].append(dict(run_id=run_id, item_id=item["id"],
                    procedure_sha256=first.get("procedure_sha256"),
                    primary_status=a, duplicate_status=b, exact_disagreement=mismatch))
        tables["pairs"].append(pair)
    for round_id in dict.fromkeys(r["round"] for r in runs):
        for condition in allocation["conditions"]:
            selected = [r for r in runs if r["round"] == round_id and r["condition"] == condition]
            ids = {r["run_id"] for r in selected}
            js = [judgments_by_slot[r["run_id"], "primary"] for r in selected]
            common = dict(study=allocation.get("study"), round=round_id, condition=condition,
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
    if disposition is not None:
        # Keep raw pooled tables for traceability; analysis/figures use explicit strata.
        for cell in tables["cells"]:
            cell["interpretation"] = "raw descriptive counts; versions are not exchangeable"
        versions = list(dict.fromkeys([disposition["research_procedure_sha256"],
                                      disposition["assessment_procedure_sha256"]]))
        for round_id in dict.fromkeys(r["round"] for r in runs):
            for condition in allocation["conditions"]:
                cell = [j for j in tables["judgments"] if j["role"] == "primary" and
                        j["round"] == round_id and j["condition"] == condition]
                for version in versions:
                    selected = [j for j in cell if j["procedure_sha256"] == version]
                    ids = {j["judgment_id"] for j in selected if j["judgment_id"]}
                    raw = [i for i in tables["items"] if i["role"] == "primary" and i["judgment_id"] in ids]
                    valid = [i for i in tables["comparable_items"] if i["role"] == "primary" and i["judgment_id"] in ids]
                    overlays = [invalid_measures[i["run_id"], i["role"], i["item_id"]] for i in raw
                                if (i["run_id"], i["role"], i["item_id"]) in invalid_measures]
                    common = dict(study=allocation.get("study"), round=round_id, condition=condition,
                        procedure_sha256=version, n_assigned_total=len(cell), n_assigned_version=len(selected),
                        n_response_available=sum(j["response_status"] == "valid" for j in selected),
                        n_pinned_items=len(selected) * len(contract.items), n_valid_items=len(valid),
                        n_response_invalid=sum(j["response_status"] == "invalid" for j in selected),
                        n_missing_items=sum(j["response_status"] == "pending" for j in selected) * len(contract.items),
                        n_unavailable_items=sum(v["validity"] == "unavailable" for v in overlays),
                        n_invalid_items=sum(v["validity"] == "invalid" for v in overlays) +
                            sum(j["response_status"] == "invalid" for j in selected) * len(contract.items),
                        n_scientific_dependency_uncertain=sum(
                            j.get("scientific_dependency", {}).get("status") == "uncertain" for j in selected))
                    tables["version_strata"].append(common)
                    for category in (*ADEQUACY, "missing", "ambiguous", "invalid"):
                        count = sum((j["adequacy"] == category if category in ADEQUACY else
                                     j["extraction_status"] == category) for j in selected)
                        tables["version_cells"].append(dict(common, metric="adequacy", group=category,
                                                           count=count, interpretation="raw scientific category"))
                    for kind, groups in (("level", LEVELS), ("dimension", DIMENSIONS)):
                        for group in groups:
                            for status in STATUSES:
                                tables["version_cells"].append(dict(common, metric=kind, group=group, status=status,
                                    **comparable_cell_summary(tables["comparable_counts"],
                                        tables["comparable_items"], ids, kind, group, status)))
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
    for name, raw in (("allocation", allocation_bytes), ("procedure", research_bytes)):
        digests = [registration[name]["sha256"]] if name in registration else []
        if name + "_sha256" in registration:
            digests.append(registration[name + "_sha256"])
        if not digests:
            raise ValueError("Registration requires " + name + " digest")
        for digest in digests:
            label = "original procedure" if name == "procedure" else name
            require_equal(digest, sha256(raw), "registered " + label + " bytes")
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
                        help="Independently approved assessment seal digest (original for neutral-v1)")
    parser.add_argument("--disposition", type=Path, help="Coordinator measurement disposition (analysis record)")
    parser.add_argument("--disposition-sha256", help="Expected exact measurement disposition bytes")
    parser.add_argument("--source-manifest", type=Path,
                        help="Retained source-path/copy manifest for relocated evidence; every copy is hash-checked")
    parser.add_argument("--round-bindings", type=Path,
                        help="Explicit authorized source/skill bindings; does not change the original seal")
    parser.add_argument("--round-bindings-sha256",
                        help="Required independent digest when --round-bindings is supplied")
    parser.add_argument("--source-repository", type=Path, default=ROOT,
                        help="Local Git object store containing original and bound coordinator commits")
    args = parser.parse_args(argv)
    location_token = ARTIFACT_LOCATIONS.set(None)
    try:
        resolution = None
        if args.source_manifest:
            locations, resolution = source_locations(args.source_manifest)
            ARTIFACT_LOCATIONS.set(locations)
        allocation_bytes, index_bytes = args.allocation.read_bytes(), args.index.read_bytes()
        research_bytes = (args.research_procedure or args.allocation.with_name("procedure.json")).read_bytes()
        registration_bytes = (args.registration or args.allocation.with_name("registration.json")).read_bytes()
        registered_inputs(allocation_bytes, research_bytes, registration_bytes)
        allocation = parse_json(allocation_bytes)
        index = parse_json(index_bytes)
        contract = load_contract(args.assessor, args.assessment_pin)
        binding_bytes = args.round_bindings.read_bytes() if args.round_bindings else None
        if bool(args.round_bindings) != bool(args.round_bindings_sha256):
            raise ValueError("--round-bindings and --round-bindings-sha256 must be supplied together")
        if binding_bytes is not None:
            require_equal(sha256(binding_bytes), args.round_bindings_sha256, "approved round binding bytes")
        binding_config = parse_json(binding_bytes) if binding_bytes is not None else None
        disposition_bytes = args.disposition.read_bytes() if args.disposition else None
        if args.disposition_sha256 and disposition_bytes is None:
            raise ValueError("--disposition-sha256 requires --disposition")
        if args.disposition_sha256:
            require_equal(sha256(disposition_bytes), args.disposition_sha256, "measurement disposition bytes")
        if disposition_bytes:
            # Both accepted versions must use the same pinned response contract.
            original_pin = parse_json(research_bytes)["assessment"]
            for name in ("checklist/lock.json", "references/response-schema.json",
                         "checklist/" + contract.lock["file"]):
                path = ":skills/stamped-conventions/" + name
                original_blob = subprocess.check_output(["git", "-C", str(args.assessor), "show",
                    original_pin["source_commit"] + path], stderr=subprocess.PIPE)
                current_blob = subprocess.check_output(["git", "-C", str(args.assessor), "show",
                    contract.assessment_pin["source_commit"] + path], stderr=subprocess.PIPE)
                require_equal(original_blob, current_blob, "shared response contract " + name)
        tables = aggregate(allocation, index, args.index.resolve().parent, contract,
                           research_bytes, args.assessment_procedure_sha256,
                           disposition=parse_json(disposition_bytes) if disposition_bytes else None,
                           disposition_base=args.disposition.resolve().parent if args.disposition else None,
                           allocation_sha256=sha256(allocation_bytes),
                           round_binding_config=binding_config,
                           round_binding_base=args.round_bindings.resolve().parent if args.round_bindings else None,
                           source_repository=args.source_repository)
        write_tables(tables, args.output)
        from comparison_figures import render
        render(tables, contract.items, args.output)
        provenance = {"schema_version": index["schema_version"], "allocation_sha256": sha256(allocation_bytes),
                      "comparison_id": parse_json(research_bytes)["comparison_id"],
                      "protocol": parse_json(research_bytes).get("protocol", "legacy"),
                      "index_sha256": sha256(index_bytes),
                      "disposition_sha256": sha256(disposition_bytes) if disposition_bytes else None,
                      "registration_sha256": sha256(registration_bytes),
                      "research_procedure_sha256": sha256(research_bytes),
                      "approved_assessment_procedure_sha256": args.assessment_procedure_sha256,
                      "comparison_provenance": index.get("comparison_provenance"),
                      "tool_sha256": sha256(Path(__file__).read_bytes()),
                      "figures_sha256": sha256(Path(__file__).with_name("comparison_figures.py").read_bytes()),
                      "assessment_pin": parse_json(args.assessment_pin.read_bytes()),
                      "checklist": contract.lock, "assigned_workers": len(tables["runs"]),
                      "assigned_judgments": len(tables["judgments"]),
                      "issues": len(tables["issues"]),
                      "interpretation": "Descriptive only; primary judgments determine worker summaries. "
                      "Duplicates compare same-version mutually valid items; supplementary attempts never "
                      "replace slots. Raw grades remain retained; version strata and evidence-based validity "
                      "are separate. Missing observations are not verdicts; replay success is not required."}
        if resolution is not None:
            provenance["artifact_resolution"] = resolution
        if binding_config is not None:
            provenance["round_bindings"] = {"sha256": sha256(binding_bytes), "record": binding_config,
                "scope": "Authorized research source/skill bindings only; original seals and all downstream checks retained"}
        (args.output / "aggregation.json").write_text(json.dumps(provenance, indent=2) + "\n")
        print(f"{len(tables['runs'])} assigned workers; {len(tables['issues'])} issues; {args.output}")
        return 2 if tables["issues"] else 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(2, f"Aggregation failed: {error}\n")
    finally:
        ARTIFACT_LOCATIONS.reset(location_token)


if __name__ == "__main__":
    raise SystemExit(main())
