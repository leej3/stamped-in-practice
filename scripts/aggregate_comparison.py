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
JUDGMENT = obj({"judgment_id": TEXT, "response": ARTIFACT, "report": ARTIFACT,
                "adequacy": EXTRACTION, "conclusion": EXCERPT}, ("judgment_id",))
OPERATION = obj({
    "operation_id": TEXT,
    "stage": {"enum": ["setup", "worker", "discovery", "installation", "computation",
                       "judging", "replay", "input-retrieval", "output-retrieval",
                       "environment-retrieval", "publication", "coordinator"]},
    "actor": {"enum": ["worker", "judge", "coordinator"]},
    "judgment_role": {"enum": ["primary", "duplicate"]},
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
INDEX_SCHEMA = obj({"schema_version": {"const": 1}, "runs": {"type": "array", "items": obj({
    "run_id": TEXT, "result_commit": COMMIT, "worker_head": COMMIT,
    "retention_commit": COMMIT, "skill_commit": COMMIT,
    "worker_completion": {"enum": ["pending", "completed", "failed", "interrupted", "unknown"]},
    "judgments": obj({"primary": JUDGMENT, "duplicate": JUDGMENT}),
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
    revision = parse_json(pin.read_bytes())["source_commit"]
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
    return Contract(items, parse_json(blob("references/response-schema.json")), lock)


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


def aggregate(allocation, index, base, contract):
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
        for judgment in run.get("judgments", {}).values():
            identity = judgment["judgment_id"]
            if identity in judgment_ids:
                raise ValueError("Repeated judgment ID: " + identity)
            judgment_ids.add(identity)
            if "result_commit" not in run:
                raise ValueError("Judgment requires run result_commit: " + run_id)
        for op in run.get("operations", []):
            identity = (run_id, op["operation_id"])
            if identity in operation_ids:
                raise ValueError("Repeated operation ID: " + str(identity))
            operation_ids.add(identity)
            if op.get("judgment_role") == "duplicate" and not assigned[run_id]["duplicate_selected"]:
                raise ValueError("Operation names an unselected duplicate: " + run_id)
    tables = {name: [] for name in ("runs", "judgments", "items", "counts", "operations",
                                    "effort", "issues", "disagreement", "pairs", "cells")}
    answers_by_slot = {}
    judgments_by_slot = {}

    def issue(run_id, role, area, message):
        tables["issues"].append(dict(run_id=run_id, role=role, area=area, message=str(message)))

    for assignment in runs:
        run_id = assignment["run_id"]
        record = indexed.get(run_id, {})
        row = dict(assignment, worker_completion=record.get(
            "worker_completion", "unknown" if record else "pending"))
        row.update({k: record.get(k) for k in
                    ("result_commit", "worker_head", "retention_commit", "skill_commit")})
        tables["runs"].append(row)
        for role in ("primary", "duplicate") if assignment["duplicate_selected"] else ("primary",):
            supplied = record.get("judgments", {}).get(role, {})
            judgment = dict(assignment, role=role, judgment_id=supplied.get("judgment_id"),
                            result_commit=record.get("result_commit"), response_status="pending",
                            adequacy=None, extraction_status="missing", conclusion=None)
            judgment.update({k: supplied.get(k) for k in ("response", "report")})
            tables["judgments"].append(judgment)
            judgments_by_slot[run_id, role] = judgment
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
            op = dict(assignment, **operation, evidence_status="valid")
            try:
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allocation", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New output directory; never overwritten")
    parser.add_argument("--assessor", type=Path, default=ROOT / "assessment")
    parser.add_argument("--assessment-pin", type=Path, default=ROOT / "assessment-version.json")
    args = parser.parse_args(argv)
    try:
        allocation_bytes, index_bytes = args.allocation.read_bytes(), args.index.read_bytes()
        allocation = parse_json(allocation_bytes)
        index = parse_json(index_bytes)
        contract = load_contract(args.assessor, args.assessment_pin)
        tables = aggregate(allocation, index, args.index.resolve().parent, contract)
        write_tables(tables, args.output)
        from comparison_figures import render
        render(tables, contract.items, args.output)
        provenance = {"schema_version": 1, "allocation_sha256": sha256(allocation_bytes),
                      "index_sha256": sha256(index_bytes),
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
