"""Verify additive historical command excerpts without rerunning the study."""
from pathlib import Path
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent
REVIEW = OUT.parent
BASE = REVIEW.parent
RETAINED = BASE / "alignment-session-retention-01"
raw_path = RETAINED / "raw-session.jsonl"
excerpt_path = RETAINED / "two-environment-command-excerpts.json"
expected_hash = "a939dd11cb30a029a8ceb6f99ccff1c4a36aa966d8aed113f96814db4e38b3fa"
raw_bytes = raw_path.read_bytes()
raw_lines = raw_bytes.splitlines()
excerpt = json.loads(excerpt_path.read_text())
raw_hash = hashlib.sha256(raw_bytes).hexdigest()
result = {
    "raw_sha256": raw_hash,
    "raw_matches_expected_hash": raw_hash == expected_hash,
    "excerpt_sha256": hashlib.sha256(excerpt_path.read_bytes()).hexdigest(),
    "excerpt_names_correct_raw_hash": excerpt["raw_sha256"] == raw_hash,
    "raw_line_count": len(raw_lines),
    "session_id": json.loads(raw_lines[0])["payload"]["id"],
    "line_bindings": [],
}
records = {}
for item in excerpt["records"]:
    line = item["line"]
    source = json.loads(raw_lines[line - 1])
    payload = source["payload"]
    result["line_bindings"].append({
        "line": line, "kind": "request", "timestamp_matches": source["timestamp"] == item["timestamp"],
        "call_id_matches": payload["call_id"] == item["call_id"],
        "input_matches_exactly": payload["input"] == item["input"],
        "line_sha256": hashlib.sha256(raw_lines[line - 1]).hexdigest(),
    })
    records[line] = payload
    for response in item["responses"]:
        response_line = response["line"]
        original = json.loads(raw_lines[response_line - 1])
        original_payload = original["payload"]
        blocks = [block["text"] for block in original_payload["output"] if block["type"] == "input_text"]
        result["line_bindings"].append({
            "line": response_line, "kind": "response",
            "timestamp_matches": original["timestamp"] == response["timestamp"],
            "call_id_matches_request": original_payload["call_id"] == item["call_id"],
            "text_blocks_match_exactly": blocks == response["text_blocks"],
            "omitted_nontext_block_types": [block["type"] for block in original_payload["output"] if block["type"] != "input_text"],
            "line_sha256": hashlib.sha256(raw_lines[response_line - 1]).hexdigest(),
        })
        records[response_line] = original_payload

def output_objects(line):
    values = []
    for block in records[line]["output"]:
        if block["type"] == "input_text":
            try:
                values.append(json.loads(block["text"]))
            except json.JSONDecodeError:
                pass
    return values

command_text = json.loads(re.search(r'cmd:("(?:[^"\\]|\\.)*")', records[95]["input"]).group(1))
commands = command_text.splitlines()
result["historical_shell_commands"] = commands
result["explicit_fresh_venv_command"] = commands[1]
result["explicit_supplied_environment_command"] = commands[2]
result["commands_name_distinct_environment_routes"] = (
    commands[1] == "../evidence/verification-venv/bin/python code/reproduce.py --output runs/verification-20261016"
    and commands[2] == "pixi run --manifest-path /Users/johnlee/code/CON/stamped-in-practice/pixi.toml --locked python code/reproduce.py --output runs/supplied-environment-20261016"
)
result["shell_session_initial"] = output_objects(98)[-1]
result["fresh_venv_completion"] = output_objects(105)[0]
result["supplied_environment_completion"] = output_objects(116)[-1]
result["polls_bind_same_session"] = (
    result["shell_session_initial"]["session_id"] == 83657
    and "session_id:83657" in records[102]["input"]
    and "session_id:83657" in records[112]["input"]
    and result["fresh_venv_completion"]["session_id"] == 83657
)
result["both_outputs_report_verification_exit_zero"] = (
    "Verification exit 0; receipt:" in result["fresh_venv_completion"]["output"]
    and "Verification exit 0; receipt:" in result["supplied_environment_completion"]["output"]
    and result["supplied_environment_completion"]["exit_code"] == 0
)
historical_receipt, _ = json.JSONDecoder().raw_decode(output_objects(105)[1]["output"])
project = BASE / "alignment-trial-01/project"
fresh_receipt_path = project / "runs/verification-20261016/run.json"
supplied_receipt_path = project / "runs/supplied-environment-20261016/run.json"
result["fresh_receipt_printed_in_session_matches_retained_receipt"] = historical_receipt == json.loads(fresh_receipt_path.read_text())
result["retained_receipt_hashes"] = {str(p.relative_to(BASE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [fresh_receipt_path, supplied_receipt_path]}
result["completion_paths_match_retained_receipts"] = (
    str(fresh_receipt_path) in result["fresh_venv_completion"]["output"]
    and str(supplied_receipt_path) in result["supplied_environment_completion"]["output"]
)
old_manifest = json.loads((REVIEW / "review-manifest.json").read_text())
result["original_review_file_mismatches"] = [name for name, expected in old_manifest.items() if hashlib.sha256((REVIEW / name).read_bytes()).hexdigest() != expected]
result["original_review_manifest_sha256"] = hashlib.sha256((REVIEW / "review-manifest.json").read_bytes()).hexdigest()
result["raw_after_review_sha256"] = hashlib.sha256(raw_path.read_bytes()).hexdigest()
result["review_action"] = "Read source records and retained receipts; no scientific rerun, project edit, raw-session edit, or original-review edit."
(OUT / "checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
