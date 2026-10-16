#!/usr/bin/env python3
"""Pool validated primary judgments, keeping per-round and per-run denominators."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import statistics
import tempfile

LABELS = {
    "baseline": "No supplied research skills",
    "discover-general": "Find useful skills",
    "discover-science": "Find research skills",
    "stamped-explicit": "Use STAMPED skills",
}
SCIENCE = ("supported", "qualified", "not supported", "unable to assess")
CHECKED = {"met", "partial", "unmet"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def atomic_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        stream.write(value)
        temporary = Path(stream.name)
    temporary.replace(path)


def output_json(path, value):
    atomic_write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def matched(comparison):
    return bool(comparison.get("identical") or comparison.get("within_tolerance")) and not (
        comparison.get("differing") or comparison.get("missing_after_rerun")
    )


def retained_reference(value):
    return isinstance(value, dict) and isinstance(value.get("path"), str) and bool(value["path"]) and bool(re.fullmatch(r"[0-9a-f]{64}", str(value.get("sha256", ""))))


def replay_row(row, capture, comparison):
    if not re.fullmatch(r"[0-9a-f]{64}", str(capture)) or type(row.get("entrypoint_returncode")) is not int:
        raise ValueError("Native replay needs an exact capture identity and recorded exit status")
    if comparison is None:
        comparison = {}
    if not isinstance(comparison, dict):
        raise ValueError("Native replay comparison must be an object or null")
    some_match = bool(comparison.get("identical") or comparison.get("within_tolerance"))
    complete = row["entrypoint_returncode"] == 0 and matched(comparison)
    return {"judgment_id": row["judgment_id"], "capture": capture, "executed": True,
            "matched": complete, "partial_selected_output_match": some_match and not complete}


def replay_records(audit):
    """Return only native-bound executions; never promote a judge's prose claim."""
    if audit.get("kind") == "final-native-replay-evidence-audit":
        if audit.get("interim") is not False:
            raise ValueError("Native replay audit must be final")
        for row in audit["helper_completions"]:
            if row.get("native_binding") not in {"same-event", "separately-validated-redirected-output-chain"} or not all(retained_reference(row.get(key)) for key in ("helper_record", "binding_receipt")):
                raise ValueError("Final replay completion lacks its retained native binding")
            yield replay_row(row, row["capture_sha256"], row.get("reported_comparison", {}))
    elif audit.get("kind") == "native-replay-evidence-extraction":
        for row in audit["rows"]:
            if not (row.get("native_helper_completion_observed") and row.get("entrypoint_execution_observed")):
                continue
            support = row.get("supporting_record", {})
            if not support.get("capture_matches_original"):
                continue
            events = row.get("matched_native_events", [])
            if row.get("status") != "native-helper-output-bound" or support.get("judgment_id") != row["judgment_id"] or not events or row.get("evidence") not in events or not all(retained_reference(event) for event in events):
                raise ValueError("Replay extraction lacks its exact native event binding")
            yield replay_row(row, support.get("reported_capture_sha256"), row.get("literal_comparison", {}))
    else:
        raise ValueError("Unknown native replay audit format")


def summarize_round(round_number, runs, judgments, items, audits):
    selected = [row for row in runs if row["round"] == round_number]
    if len({row["run_id"] for row in selected}) != len(selected):
        raise ValueError("Duplicate research run in normalized input")
    primaries = {}
    for row in judgments:
        if row["round"] == round_number and row["role"] == "primary":
            if row["run_id"] in primaries:
                raise ValueError("Multiple primary judgments for one run")
            primaries[row["run_id"]] = row
    by_judgment = defaultdict(list)
    for row in items:
        by_judgment[row["judgment_id"]].append(row)
    replay = {}
    for audit in audits:
        for row in replay_records(audit):
            key = row["judgment_id"]
            if key in replay and replay[key] != row:
                raise ValueError("Conflicting native replay records: " + key)
            replay[key] = row
    result = []
    for run in sorted(selected, key=lambda row: row["run_id"]):
        condition = run["condition"]
        if condition not in LABELS:
            raise ValueError("Unknown condition: " + condition)
        judgment = primaries.get(run["run_id"], {})
        eligible = judgment.get("inclusion_status") == "eligible"
        adequacy = judgment.get("adequacy") if eligible else None
        if adequacy is not None and adequacy not in SCIENCE:
            raise ValueError("Unknown scientific category: " + str(adequacy))
        checklist_valid = eligible and judgment.get("response_status") == "valid"
        answers = by_judgment[judgment.get("judgment_id")]
        counts = Counter()
        if checklist_valid:
            if len(answers) != 31 or len({row["item_id"] for row in answers}) != 31:
                raise ValueError("Valid checklist must contain all 31 distinct items")
            if any(row["role"] != "primary" or row["run_id"] != run["run_id"] for row in answers):
                raise ValueError("Checklist does not belong to its primary run")
            counts.update(row["status"] for row in answers)
            if set(counts) - CHECKED - {"not-checked", "not-applicable"}:
                raise ValueError("Unknown checklist status")
        evaluated = sum(counts[key] for key in CHECKED)
        fraction = counts["met"] / evaluated if checklist_valid and evaluated else None
        native = replay.get(judgment.get("judgment_id"))
        if native and native["capture"] != run.get("delivery_capture", {}).get("sha256"):
            raise ValueError("Replay is bound to a different original capture")
        result.append({
            "run_id": run["run_id"], "round": round_number, "condition": condition,
            "completed": run.get("worker_completion") == "completed",
            "judgment_id": judgment.get("judgment_id"),
            "admission": judgment.get("inclusion_status", "pending"),
            "science": adequacy, "checklist_valid": checklist_valid,
            "checklist_status_counts": dict(counts), "checklist_evaluated_items": evaluated,
            "checklist_met_fraction": fraction,
            "native_replay_executed": bool(eligible and native),
            "native_replay_matched": bool(eligible and native and native["matched"]),
            "native_replay_partial_selected_output_match": bool(eligible and native and native["partial_selected_output_match"]),
            "raw_native_replay_executed": bool(native),
            "raw_native_replay_matched": bool(native and native["matched"]),
            "raw_native_replay_partial_selected_output_match": bool(native and native["partial_selected_output_match"]),
            "delivery_capture_sha256": run.get("delivery_capture", {}).get("sha256"),
            "procedure_sha256": judgment.get("procedure_sha256"),
        })
    return result


def summarize(rows):
    result = []
    for condition, label in LABELS.items():
        group = [row for row in rows if row["condition"] == condition]
        science = Counter(row["science"] for row in group if row["science"] is not None)
        fractions = [row["checklist_met_fraction"] for row in group if row["checklist_met_fraction"] is not None]
        evaluated = [row["checklist_evaluated_items"] for row in group if row["checklist_met_fraction"] is not None]
        statuses = Counter()
        for row in group:
            statuses.update(row["checklist_status_counts"])
        result.append({
            "condition": condition, "label": label, "assigned_runs": len(group),
            "completed_runs": sum(row["completed"] for row in group),
            "scientific_n": sum(science.values()), "science": {key: science[key] for key in SCIENCE},
            "scientific_unavailable": len(group) - sum(science.values()),
            "checklist_n": len(fractions), "checklist_unavailable": len(group) - len(fractions),
            "checklist_mean_met_percent": 100 * statistics.mean(fractions) if fractions else None,
            "checklist_sd_met_percent": 100 * statistics.stdev(fractions) if len(fractions) > 1 else None,
            "checklist_evaluated_items_mean": statistics.mean(evaluated) if evaluated else None,
            "checklist_evaluated_items_min": min(evaluated) if evaluated else None,
            "checklist_evaluated_items_max": max(evaluated) if evaluated else None,
            "checklist_status_counts": dict(statuses),
            "replay_executed_n": sum(row["native_replay_executed"] for row in group),
            "replay_matched_n": sum(row["native_replay_matched"] for row in group),
            "replay_partial_selected_output_match_n": sum(row["native_replay_partial_selected_output_match"] for row in group),
            "replay_execution_unobserved_or_unavailable": sum(not row["native_replay_executed"] for row in group),
        })
    return result


def tsv(rows):
    stream = io.StringIO()
    columns = list(dict.fromkeys(key for row in rows for key in row))
    writer = csv.DictWriter(stream, fieldnames=columns, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value for key, value in row.items()})
    return stream.getvalue()


def markdown(summary):
    lines = ["# Pooled condition outcomes", "",
             "Retained rounds: " + ", ".join(map(str, summary["retained_rounds"])) + ".", "",
             "| Instruction | Assigned runs | Science: supported / assessed | Replay: matching / executed | STAMPED mean met % (n) |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for row in summary["conditions"]:
        science = f'{row["science"]["supported"]}/{row["scientific_n"]}'
        replay = f'{row["replay_matched_n"]}/{row["replay_executed_n"]}' if row["replay_executed_n"] else "None observed"
        score = f'{row["checklist_mean_met_percent"]:.1f} ({row["checklist_n"]})' if row["checklist_n"] else "Unavailable"
        lines.append(f'| {row["label"]} | {row["assigned_runs"]} | {science} | {replay} | {score} |')
    lines.extend(["", *[value + "\n" for value in summary["definitions"].values()],
                  "[All counts and input hashes](poster-outcomes.json) · [Round-specific summaries](round-outcomes.tsv) · [Every research run](run-outcomes.json).", "",
                  "Checklist summaries also retain evaluated-item coverage, partial/unmet answers and unavailable responses. Replay counts retain partial selected-output matches separately; differences in a selected figure or execution record do not by themselves establish a failed scientific reproduction.", "",
                  "The [reporting record](../README.md) links the original inputs, original rejection reports, additive corrections and preserved validation failures.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    base = args.config.resolve().parent
    all_rows, sources, per_round, revisions = [], [], [], []
    seen_rounds = set()
    for spec in config["rounds"]:
        number = spec["round"]
        if number in seen_rounds:
            raise ValueError("More than one assessment series selected for the same round")
        seen_rounds.add(number)
        folder = base / spec["analysis"]
        inputs = {}
        for name in ("runs", "judgments", "items"):
            path = folder / (name + ".jsonl")
            inputs[name] = read_rows(path)
            sources.append({"round": number, "path": str(path.relative_to(base)), "sha256": sha(path)})
        audits = []
        for relative in spec.get("replay_audits", []):
            path = base / relative
            audits.append(json.loads(path.read_text()))
            sources.append({"round": number, "path": relative, "sha256": sha(path)})
        rows = summarize_round(number, inputs["runs"], inputs["judgments"], inputs["items"], audits)
        if len(rows) != 24 or any(sum(row["condition"] == condition for row in rows) != 6 for condition in LABELS):
            raise ValueError("Each retained round must preserve all 24 assigned research runs")
        revision = {key: spec[key] for key in ("assessment_series", "research_guidance_commit") if key in spec}
        revisions.append({"round": number, **revision})
        for row in rows:
            row.update(revision)
        all_rows.extend(rows)
        per_round.extend({"round": number, **row} for row in summarize(rows))
    summary = {
        "schema_version": 1,
        "scope": "One selected operational assessment series per round; original primaries only, every assigned run retained.",
        "retained_rounds": sorted(seen_rounds),
        "revisions": revisions,
        "definitions": {
            "science": "Recorded adequacy of the analysis supporting its conclusion, not direction of the neuroscience hypothesis.",
            "checklist": "For each valid primary response: met/(met+partial+unmet). Average these run fractions equally. Not-checked and not-applicable items do not enter the evaluated-item denominator; their counts remain in the run table.",
            "replay": "Native-bound entrypoint execution and explicit selected-output matches on the assessment host, restricted to admitted primary judgments. No execution claim from prose or launcher exit alone. Unobserved or unavailable replay is not failure.",
            "pooling": "Each research run has equal weight; duplicate judges do not replace primaries or increase sample size. Round-specific tables retain revision history.",
        },
        "conditions": summarize(all_rows), "round_conditions": per_round,
        "sources": sources, "generator_sha256": sha(Path(__file__)),
        "config_sha256": sha(args.config),
    }
    output_json(args.output / "poster-outcomes.json", summary)
    output_json(args.output / "run-outcomes.json", all_rows)
    atomic_write(args.output / "poster-outcomes.tsv", tsv(summary["conditions"]))
    atomic_write(args.output / "round-outcomes.tsv", tsv(per_round))
    atomic_write(args.output / "run-outcomes.tsv", tsv(all_rows))
    atomic_write(args.output / "README.md", markdown(summary))
    print(json.dumps({"runs": len(all_rows), "rounds": sorted(seen_rounds), "output": str(args.output)}))


if __name__ == "__main__":
    main()
