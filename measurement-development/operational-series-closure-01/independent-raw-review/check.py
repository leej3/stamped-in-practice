"""Check reported categories and duplicate differences against raw judge output.

This is a transcription check, not a regrade or a replacement acceptance gate.
The frozen extractor's checklist admission decisions remain authoritative.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("snapshot", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.snapshot.resolve()
identities = {}

def read(path):
    data = path.read_bytes()
    identities[str(path)] = hashlib.sha256(data).hexdigest()
    return data

def document(path):
    return json.loads(read(path))

def rows(name):
    return [json.loads(line) for line in read(root / "analysis" / name).splitlines() if line]

judgments = [r for r in rows("judgments.jsonl") if r["round"] == 1]
pairs = [r for r in rows("pairs.jsonl") if r["round"] == 1]
read(root / "index.json")
read(root / "source-manifest.json")
assert {r["procedure_sha256"] for r in judgments} == {
    "6f25ebbec5310442e8fd3fd20bd20682ecb5653b350362119af3e825a2668084"}
assert len(judgments) == 32
assert len({r["judgment_id"] for r in judgments}) == 32
assert Counter(r["role"] for r in judgments) == {"primary": 24, "duplicate": 8}
primary_counts = Counter(r["condition"] for r in judgments if r["role"] == "primary")
assert len(primary_counts) == 4 and set(primary_counts.values()) == {6}
raw = {}
science_by_group = defaultdict(Counter)
checklist_by_group = defaultdict(Counter)
for row in judgments:
    assert row["inclusion_status"] == "eligible", row["judgment_id"]
    folder = root / "evidence" / "judgments" / row["judgment_id"]
    response_path = folder / "response.json"
    response = document(response_path)
    assert identities[str(response_path)] == row["response"]["sha256"]
    science = document(folder / "scientific-judgment.json")
    assert science["delivery_capture_sha256"] == row["delivery_capture"]["sha256"]
    assert science["scientific_adequacy"] == row["adequacy"]
    assert row["extraction_status"] == "explicit"
    report = read(folder / "scientific-report.md")
    assert hashlib.sha256(report).hexdigest() == science["report"]["sha256"]
    evidence = science["adequacy_evidence"]
    lines = report.decode().splitlines()
    selected = "\n".join(lines[evidence["start_line"] - 1:evidence["end_line"]])
    assert evidence["quote"] in selected
    raw[row["judgment_id"]] = (response, science)
    if row["role"] == "primary":
        science_by_group[row["condition"]][science["scientific_adequacy"]] += 1
        checklist_by_group[row["condition"]][row["response_status"]] += 1

assert len(pairs) == 8 and len({p["run_id"] for p in pairs}) == 8
pair_results = []
expected_items = {}
for pair in pairs:
    first, first_science = raw[pair["primary_id"]]
    second, second_science = raw[pair["duplicate_id"]]
    assert pair["item_pair_complete"] and pair["adequacy_pair_complete"]
    first_items, second_items = first["responses"], second["responses"]
    assert set(first_items) == set(second_items)
    assert len(first_items) == pair["comparable_item_count"] == 31
    changed = [key for key in sorted(first_items)
               if first_items[key]["status"] != second_items[key]["status"]]
    assert len(changed) == pair["item_disagreements"]
    for key in first_items:
        expected_items[(pair["run_id"], key)] = (
            first_items[key]["status"], second_items[key]["status"], key in changed)
    first_category = first_science["scientific_adequacy"]
    second_category = second_science["scientific_adequacy"]
    assert first_category == pair["primary_adequacy"]
    assert second_category == pair["duplicate_adequacy"]
    assert (first_category != second_category) == pair["adequacy_disagreement"]
    pair_results.append({"run_id": pair["run_id"], "condition": pair["condition"],
                         "compared_items": len(first_items), "changed_items": changed,
                         "primary_science": first_category, "duplicate_science": second_category})

observed_items = {}
for item in rows("disagreement.jsonl"):
    if item["run_id"] in {p["run_id"] for p in pairs}:
        key = (item["run_id"], item["item_id"])
        assert key not in observed_items
        observed_items[key] = (item["primary_status"], item["duplicate_status"], item["exact_disagreement"])
assert observed_items == expected_items

for path, digest in identities.items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
result = {
    "schema_version": 1,
    "scope": "Read-only raw-output transcription check; no regrading, repairs, replacement, or imputation.",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "snapshot": str(root),
    "judgments_checked": len(judgments),
    "primary_scientific_categories": science_by_group,
    "primary_checklist_admission": checklist_by_group,
    "pairs": pair_results,
    "item_comparisons": sum(p["compared_items"] for p in pair_results),
    "item_disagreements": sum(len(p["changed_items"]) for p in pair_results),
    "science_category_disagreements": sum(p["primary_science"] != p["duplicate_science"] for p in pair_results),
    "source_files_unchanged": True,
    "source_sha256": identities,
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "status": "passed",
}
with args.output.open("x") as stream:
    json.dump(result, stream, indent=2)
    stream.write("\n")
print(json.dumps({k: v for k, v in result.items() if k not in {"source_sha256", "pairs"}}))
