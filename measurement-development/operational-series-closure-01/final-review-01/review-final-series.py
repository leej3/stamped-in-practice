"""Summarize retained gates and replay evidence without grading or executing research."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("snapshot", type=Path)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--allow-interim", action="store_true")
args = parser.parse_args()
root = args.snapshot.resolve()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def ref(path):
    return {"path": str(path), "sha256": sha(path.read_bytes())}


def read(name):
    return json.loads((root / name).read_bytes())


def table(name):
    return [json.loads(line) for line in (root / "analysis" / (name + ".jsonl")).read_text().splitlines()]


meta = read("snapshot.json")
availability = read("round-01-availability.json")
rows = availability["rows"]
runs = [row for row in table("runs") if row["round"] == 1]
run_ids = {row["run_id"] for row in runs}
judgments = [row for row in table("judgments") if row["run_id"] in run_ids]
assert len(rows) == len(judgments) == 32 and len(runs) == 24
assert {row["judgment_id"] for row in rows} == {row["judgment_id"] for row in judgments}
assert Counter(row["role"] for row in rows) == {"primary": 24, "duplicate": 8}
if not args.allow_interim:
    assert meta["closed_current_series_launchers"] == 32 and meta["pending_current_series_slots"] == 0
    assert all(row["launcher_native_state"] != "pending" for row in rows)
replay = read("replay-native-observations.json")
replay_by_slot = {}
for record in replay["rows"]:
    replay_by_slot.setdefault(record["judgment_id"], []).append(record)


def summarize(selected):
    ids = {row["judgment_id"] for row in selected}
    native = [record for identity in ids for record in replay_by_slot.get(identity, [])]
    return {
        "assigned_slots": len(selected),
        "launcher_closed": sum(row["launcher_native_state"] != "pending" for row in selected),
        "native_states": dict(Counter(row["launcher_native_state"] for row in selected)),
        "admission": dict(Counter(row["admission"] for row in selected)),
        "checklist": dict(Counter(row["checklist"] for row in selected)),
        "scientific_availability": dict(Counter(row["scientific_availability"] for row in selected)),
        "replay_record_availability": dict(Counter(row["replay_record_availability"] for row in selected)),
        "native_helper_completion_slots": sum(any(r["native_helper_completion_observed"] for r in replay_by_slot.get(identity, [])) for identity in ids),
        "native_entrypoint_execution_slots": sum(any(r["entrypoint_execution_observed"] for r in replay_by_slot.get(identity, [])) for identity in ids),
        "replay_native_evidence_states_by_record": dict(Counter(r["status"] for r in native)),
        "declared_replay_statuses_by_record": dict(Counter(r["supporting_record"].get("literal_replay_fields", {}).get("status", "absent") for r in native)),
        "direct_capture_bound_replay_records": sum(r["supporting_record"].get("capture_matches_original") is True for r in native),
    }


groups = [{"group": "All current slots", "condition": None, "role": None, **summarize(rows)}]
for role in ("primary", "duplicate"):
    groups.append({"group": role, "condition": None, "role": role,
                   **summarize([row for row in rows if row["role"] == role])})
for condition in ("baseline", "discover-general", "discover-science", "stamped-explicit"):
    for role in (None, "primary", "duplicate"):
        selected = [row for row in rows if row["condition"] == condition and (role is None or row["role"] == role)]
        assert len(selected) == (8 if role is None else 6 if role == "primary" else 2)
        groups.append({"group": condition + (" / " + role if role else ""), "condition": condition,
                       "role": role, **summarize(selected)})

pairs = [row for row in table("pairs") if row["run_id"] in run_ids]
assert len(pairs) == 8 and len({row["run_id"] for row in pairs}) == 8
disagreements = [row for row in table("disagreement") if row["run_id"] in run_ids]
for pair in pairs:
    records = [row for row in disagreements if row["run_id"] == pair["run_id"]]
    assert len(records) == pair["comparable_item_count"]
    if pair["item_disagreements"] is not None:
        assert sum(row["exact_disagreement"] for row in records) == pair["item_disagreements"]
pair_summary = {"assigned_object_pairs": len(pairs),
                "checklist_complete_pairs": sum(row["item_pair_complete"] for row in pairs),
                "scientific_complete_pairs": sum(row["adequacy_pair_complete"] for row in pairs),
                "scientific_disagreeing_pairs": sum(row["adequacy_disagreement"] is True for row in pairs),
                "comparable_item_records": len(disagreements),
                "disagreeing_item_records": sum(row["exact_disagreement"] for row in disagreements),
                "scope": "Frozen pair table values; item observations are nested within eight objects, not independent workers.",
                "rows": pairs}

# Retain every closed command mentioning replay for final human provenance review.
# Mentions alone are never counted as attempts or successful execution.
hashes = {row["copy"]["path"]: row["sha256"] for row in read("source-manifest.json")}
candidates = []
for row in rows:
    if row["launcher_native_state"] == "pending":
        continue
    path = root / "evidence/judgments" / row["judgment_id"] / "native-events.jsonl"
    if not path.is_file():
        continue
    assert sha(path.read_bytes()) == hashes[str(path.relative_to(root))]
    for line_number, raw in enumerate(path.read_bytes().splitlines(), 1):
        event = json.loads(raw)
        item = event.get("item", {})
        command = item.get("command", "")
        if (event.get("type") == "item.completed" and item.get("type") == "command_execution"
                and item.get("status") == "completed" and isinstance(command, str)
                and "fresh-rerun" in command):
            candidates.append({"judgment_id": row["judgment_id"], "events": ref(path), "line": line_number,
                               "raw_event_sha256": sha(raw), "event": event,
                               "scope": "Candidate mention only; do not infer invocation, attempt, completion or entrypoint execution."})

issues = table("issues")
sources = [ref(root / name) for name in ("index.json", "snapshot.json", "round-01-availability.json",
    "replay-native-observations.json", "source-manifest.json", "analysis/aggregation.json",
    "analysis/judgments.jsonl", "analysis/pairs.jsonl", "analysis/disagreement.jsonl", "analysis/issues.jsonl")]
result = {"kind": "current-series-evidence-review", "interim": bool(meta["pending_current_series_slots"]),
          "scope": "Only round1:24 workers/32 judgments; primary24/duplicate8. Full original allocation72/96 retained; future48/64 outside current-series missingness.",
          "snapshot": str(root), "reviewer_script": ref(Path(__file__)), "sources": sources,
          "groups": groups, "pairs": pair_summary, "retained_aggregation_issues": issues,
          "replay": {"same_event_binding_only": True,
                     "native_helper_completions": replay["native_helper_completions"],
                     "observed_entrypoint_executions": replay["observed_entrypoint_executions"],
                     "bound_records": [r for r in replay["rows"] if r["native_helper_completion_observed"]],
                     "unmatched_helper_shaped_records": [r for r in replay["rows"] if r["status"] == "helper-shaped-record-native-binding-unavailable"],
                     "scope": "Exact native output binding is separate from literal judge-authored replay JSON. Optional replay unavailability is not scientific failure. Candidate mentions are not automatically counted."}}
(out / "review.json").write_text(json.dumps(result, indent=2) + "\n")
(out / "replay-command-candidates.json").write_text(json.dumps(candidates, indent=2) + "\n")
lines = ["# Current-series evidence availability", "", result["scope"], "",
         "Counts describe retained evidence and frozen validation gates. They are not new grades. Native completion, admission, checklist validity, scientific extraction and replay are separate; duplicate observations never replace primaries.", "",
         "| Group | Assigned | Closed | Admitted | Checklist valid | Checklist invalid | Science available | Replay record | Same-event replay entrypoint |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
for group in groups:
    values = [group["group"], group["assigned_slots"], group["launcher_closed"], group["admission"].get("eligible", 0),
              group["checklist"].get("valid", 0), group["checklist"].get("invalid", 0),
              group["scientific_availability"].get("available", 0), group["replay_record_availability"].get("retained", 0),
              group["native_entrypoint_execution_slots"]]
    lines.append("| " + " | ".join(map(str, values)) + " |")
lines += ["", "Replay records can declare non-attempt or unavailable states. The automated replay column requires exact same-event helper output binding and an explicit entrypoint return code; outer shell exit is insufficient. A separately reviewed redirection chain is reported additively in the final evidence brief and does not change this automated count. The command-candidate inventory includes mentions and is not an attempt count.", "",
          "## Preselected duplicate pairs", "", "| Object | Condition | Checklist comparable items | Checklist disagreements | Primary science category | Duplicate science category | Science pair available | Science disagreement |", "|---|---|---:|---:|---|---|---|---|"]
for pair in pairs:
    lines.append("| " + " | ".join(map(str, (pair["run_id"], pair["condition"], pair["comparable_item_count"], pair["item_disagreements"], pair["primary_adequacy"], pair["duplicate_adequacy"], pair["adequacy_pair_complete"], pair["adequacy_disagreement"]))) + " |")
lines += ["", "These are repeated measurements of eight existing objects. Item comparisons are nested within objects and do not increase worker sample size. Schema and integrity success do not establish grading reliability; these disagreements are retained without adjudication or claims of reduced variance.", "", "## Retained checker issues", ""]
for issue in issues:
    lines.append("- " + issue.get("run_id", "comparison") + " / " + issue["area"] + ": " + issue["message"])
lines += ["", "Raw records and frozen acceptance criteria are unchanged. Independent science remains governed by its separate structured-record and report/capture bindings.", "", "## Source identities", ""]
for source in sources:
    lines.append("- `" + source["path"] + "`: `" + source["sha256"] + "`")
(out / "README.md").write_text("\n".join(lines) + "\n")
print(json.dumps({"output": str(out), "review": ref(out / "review.json"), "groups": groups[:3], "pair_counts": {key: value for key, value in pair_summary.items() if key != "rows"}, "replay_command_candidates": len(candidates)}))
