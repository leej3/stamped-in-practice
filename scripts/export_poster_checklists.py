#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Expose retained primary checklists without new assessment or changed answers."""
from __future__ import annotations

import argparse
from collections import Counter
import contextlib
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import subprocess
import tarfile
import tempfile
import types

from summarize_poster_outcomes import LABELS

ROOT = Path(__file__).resolve().parents[1]
REPORTING = Path("experiments/retained-round-reporting")
EXPORT = Path("experiments/narps-poster/checklists")
ENCODER_COMMIT = "9852d8360f9519d21d11099b45f5deb8ba80cb28"
ENCODER_FILES = (
    "skills/stamped-conventions/scripts/encode_response.py",
    "skills/stamped-conventions/checklist/lock.json",
    "skills/stamped-conventions/checklist/stamped-checklist-0.3.1.json",
    "skills/stamped-conventions/references/response-schema.json",
)
REPOSITORY = "https://github.com/leej3/stamped-in-practice"
BRANCH = "codex/stamped-poster-analysis"
STATUSES = {"met", "partial", "unmet", "not-checked", "not-applicable"}
MAX_APP_URL_BYTES = 8000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def entry(path, relative):
    data = path.read_bytes()
    return {"path": relative.as_posix(), "sha256": sha(data), "bytes": len(data)}


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(data)
        temporary = Path(stream.name)
    temporary.replace(path)


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def readme(rows):
    lines = ["# Filled primary STAMPED checklists", "",
             "All 72 assigned research runs are retained below; 68 have valid primary checklist scores.",
             "The responses are copied unchanged from the original retained assessments; this export performs no regrading.", "",
             "**Evaluated items met** is `met / (met + partial + unmet)`, the per-run fraction used in the progression plot.",
             "**All items met** is `met / 31`, the checklist app's denominator; the app rounds its percentage to a whole number.",
             "Not-checked and not-applicable items therefore change the denominator between the two displays.", "",
             "The filled app maps met to Yes, partial/unmet to No, and not-checked/not-applicable to blank.",
             "It omits evidence, source and assessor metadata, truncates reasons to 250 characters, and shows reasons only for No.",
             "One filled-form URL would exceed the site's request limit: its undisplayed reasons on Yes/blank answers are omitted to keep the URL below 8,000 bytes.",
             "All answer states and visible No reasons remain intact; the omitted reasons remain unchanged in the raw JSON.",
             "Use each raw JSON link for the complete authoritative response and distinct verdicts.",
             "Unavailable primary scores remain unlinked dashes; their excluded raw records are retained for inspection.",
             "The poster's pooled checklist table averages the all-item percentages equally across valid runs in each condition.",
             "Its progression plot retains evaluated-item percentages, a separate measure.", "",
             "[Machine-readable index and definitions](index.json) · [Source and output hashes](manifest.json)", "",
             "Recreate with `pixi run poster-checklists` after retrieving the three retained-round input archives and initializing the frozen `assessment` submodule.",
             "The exporter verifies the archives, selected response hashes, primary admission and original per-run scores before generating links with the pinned encoder.", ""]
    for condition, label in LABELS.items():
        valid = [r for r in rows if r["condition"] == condition and r["checklist_valid"]]
        mean = statistics.mean(row["app_all_items_met_percent"] for row in valid)
        lines.extend([f"## {label}", "", f"Pooled all-item mean: {mean:.1f}% from {len(valid)} valid primary responses.", "",
                      "| Round | Run | All items met (app) | Evaluated items met (plot) | Full response |",
                      "| --- | --- | ---: | ---: | --- |"])
        for row in (r for r in rows if r["condition"] == condition):
            if row["checklist_valid"]:
                evaluated = f'{row["met_count"]}/{row["evaluated_count"]} ({row["evaluated_met_percent"]:.1f}%)'
                app_rounded = math.floor(row["app_all_items_met_percent"] + .5)
                all_items = f'{row["met_count"]}/{row["all_item_count"]} ([{app_rounded}%][{row["run_id"]}])'
            else:
                evaluated = all_items = "—"
            raw = f'[JSON](responses/{row["run_id"]}.json)'
            lines.append(f'| {row["round"]} | {row["run_id"]} | {all_items} | {evaluated} | {raw} |')
        lines.append("")
    lines.extend(["## Unavailable primary scores", ""])
    for row in rows:
        if not row["checklist_valid"]:
            lines.append(f'- `{row["run_id"]}`: {"; ".join(row["exclusion_reasons"])}.')
    lines.append("")
    lines.extend(f'[{row["run_id"]}]: {row["app_url"]}' for row in rows if row["app_url"])
    return "\n".join(lines) + "\n"


def load_encoder(assessor):
    """Use the exact frozen projection code; do not run an assessment."""
    files = []
    for name in ENCODER_FILES:
        recorded = subprocess.check_output(
            ["git", "-C", str(assessor), "show", f"{ENCODER_COMMIT}:{name}"]
        )
        local = (assessor / name).read_bytes()
        if recorded != local:
            raise ValueError(f"Frozen encoder input differs: {name}")
        files.append({"path": name, "sha256": sha(local), "bytes": len(local)})
    path = assessor / ENCODER_FILES[0]
    module = types.ModuleType("frozen_checklist_encoder")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module, {
        "repository": "https://github.com/con/skills", "commit": ENCODER_COMMIT,
        "files": files, "operation": "encode canonical answers for display; no assessment",
    }


def app_link(response, encoder, checklist):
    """Fit the site's request limit without changing any visible answer."""
    with contextlib.redirect_stderr(io.StringIO()):
        url = encoder.encode(response, checklist)
    omit_undisplayed = len(url.encode()) > MAX_APP_URL_BYTES
    if omit_undisplayed:
        projection = copy.deepcopy(response)
        for answer in projection["responses"].values():
            if answer["status"] not in {"partial", "unmet"}:
                answer["reason"] = ""
        with contextlib.redirect_stderr(io.StringIO()):
            url = encoder.encode(projection, checklist)
    if len(url.encode()) > MAX_APP_URL_BYTES:
        raise ValueError("Filled-form URL exceeds the checked app transport limit")
    return url, {"undisplayed_reasons_omitted": omit_undisplayed,
                 "maximum_url_bytes": MAX_APP_URL_BYTES, "url_bytes": len(url.encode()),
                 "reason_character_limit": encoder.REASON_MAX}


def export(reporting, assessor, output):
    encoder, encoder_identity = load_encoder(assessor)
    checklist = encoder.Checklist()
    outcomes_path = reporting / "pooled/run-outcomes.json"
    outcomes = json.loads(outcomes_path.read_text())
    if len(outcomes) != 72 or len({row["run_id"] for row in outcomes}) != 72:
        raise ValueError("Expected all 72 distinct retained research runs")
    sources = [entry(outcomes_path, REPORTING / "pooled/run-outcomes.json")]
    rows, response_copies = [], {}
    for number in (1, 2, 3):
        folder = reporting / f"round-{number:02d}"
        relative = REPORTING / folder.name
        identity_path = folder / "input.json"
        identity = json.loads(identity_path.read_text())
        archive_path = folder / "input.tar.gz"
        archive = entry(archive_path, relative / "input.tar.gz")
        if archive["sha256"] != identity["archive"]["sha256"] or archive["bytes"] != identity["archive"]["bytes"]:
            raise ValueError(f"Archive identity mismatch for round {number}")
        judgment_path = folder / "analysis/judgments.jsonl"
        judgments = [json.loads(line) for line in judgment_path.read_text().splitlines() if line.strip()]
        primaries = [row for row in judgments if row["round"] == number and row["role"] == "primary"]
        if len(primaries) != 24 or len({row["judgment_id"] for row in primaries}) != 24:
            raise ValueError("Expected 24 unique primary judgments per retained round")
        by_id = {row["judgment_id"]: row for row in primaries}
        issues_path = folder / "analysis/issues.tsv"
        issues = list(csv.DictReader(io.StringIO(issues_path.read_text()), delimiter="\t"))
        sources.extend((entry(identity_path, relative / "input.json"), archive,
                        entry(judgment_path, relative / "analysis/judgments.jsonl"),
                        entry(issues_path, relative / "analysis/issues.tsv")))
        assigned = [row for row in outcomes if row["round"] == number]
        if Counter(row["condition"] for row in assigned) != Counter({condition: 6 for condition in LABELS}):
            raise ValueError("Each round must retain six assigned runs per condition")
        with tarfile.open(archive_path) as archive_file:
            for run in sorted(assigned, key=lambda row: row["run_id"]):
                judgment = by_id[run["judgment_id"]]
                if judgment["run_id"] != run["run_id"] or judgment["condition"] != run["condition"]:
                    raise ValueError("Run and primary judgment identity differ")
                valid = judgment["inclusion_status"] == "eligible" and judgment["response_status"] == "valid"
                if valid != run["checklist_valid"] or judgment["inclusion_status"] != run["admission"]:
                    raise ValueError("Run and primary judgment admission differ")
                response_ref = judgment["response"]
                member = archive_file.getmember(response_ref["path"])
                if not member.isfile():
                    raise ValueError("Canonical response must be a regular archived file")
                raw = archive_file.extractfile(member).read()
                if sha(raw) != response_ref["sha256"]:
                    raise ValueError("Canonical response hash differs from admitted judgment")
                response = json.loads(raw)
                counts = Counter(answer["status"] for answer in response["responses"].values())
                if set(counts) - STATUSES:
                    raise ValueError("Unknown retained checklist status")
                all_items = len(response["responses"])
                evaluated = sum(counts[status] for status in ("met", "partial", "unmet"))
                app_url = app_projection = evaluated_percent = app_percent = None
                if valid:
                    if set(response["responses"]) != set(checklist.by_id) or response["checklist_version"] != checklist.version:
                        raise ValueError("Admitted response differs from the pinned 31-item checklist")
                    if (dict(counts) != run["checklist_status_counts"] or evaluated != run["checklist_evaluated_items"]
                            or not evaluated or counts["met"] / evaluated != run["checklist_met_fraction"]):
                        raise ValueError("Authoritative response does not reproduce the reported score")
                    if response["object"]["capture"]["sha256"] != run["delivery_capture_sha256"]:
                        raise ValueError("Response is not bound to the scored original delivery")
                    app_url, app_projection = app_link(response, encoder, checklist)
                    evaluated_percent = 100 * counts["met"] / evaluated
                    app_percent = 100 * counts["met"] / all_items
                exported = EXPORT / "responses" / f'{run["run_id"]}.json'
                response_copies[exported.name] = raw
                rows.append({
                    "run_id": run["run_id"], "round": number, "condition": run["condition"],
                    "label": LABELS[run["condition"]], "judgment_id": run["judgment_id"],
                    "admission": judgment["inclusion_status"], "response_status": judgment["response_status"],
                    "checklist_valid": valid,
                    "exclusion_reasons": [issue["message"] for issue in issues
                                          if issue["run_id"] == run["run_id"] and issue["role"] == "primary"],
                    "met_count": counts["met"], "evaluated_count": evaluated, "all_item_count": all_items,
                    "status_counts": dict(counts), "evaluated_met_percent": evaluated_percent,
                    "app_all_items_met_percent": app_percent, "app_url": app_url,
                    "app_projection": app_projection,
                    "app_url_sha256": sha(app_url.encode()) if app_url else None,
                    "raw_response_path": exported.as_posix(),
                    "raw_response_url": f"https://raw.githubusercontent.com/leej3/stamped-in-practice/{BRANCH}/{exported.as_posix()}",
                    "response_sha256": sha(raw), "response_bytes": len(raw),
                    "source": {"archive": archive, "member_path": member.name,
                               "response_sha256": response_ref["sha256"],
                               "original_delivery_capture_sha256": run["delivery_capture_sha256"]},
                })
    if sum(row["checklist_valid"] for row in rows) != 68:
        raise ValueError("Expected exactly 68 admitted checklist responses and four unavailable scores")
    definitions = {
        "evaluated_met_percent": "100 * met / (met + partial + unmet), exactly the per-run fraction used in the progression plot.",
        "app_all_items_met_percent": "100 * met / all 31 checklist items; the checklist app rounds this to a whole percentage.",
        "app_all_items_mean_met_percent": "Equal-run mean of the unrounded all-item percentages among admitted primary responses in a condition; this is separate from the plot's evaluated-item mean.",
        "unavailable": "Invalid or unadmitted primary responses have null scores and app links. Their unchanged raw responses and counts are retained for inspection, never included in means.",
        "app_projection": "The frozen encoder maps met to yes, partial/unmet to no, and not-checked/not-applicable to blank. The web form omits evidence, source and assessor metadata; it truncates reasons to 250 characters and shows reasons only for no. The raw JSON is the authoritative complete response.",
        "app_transport": "URLs must fit within 8,000 bytes. Only when necessary, undisplayed reasons for yes/blank answers are omitted before invoking the frozen encoder; every answer state and visible no reason is preserved. Per-run app_projection records this display-only loss. Exact original reasons remain in the raw response JSON.",
        "source": "Every response is copied byte-for-byte from the member selected by its retained primary judgment, after archive and response hash verification. App URLs are generated from these canonical responses, not reused from potentially stale retained URL files. No responses are regraded or repaired.",
    }
    conditions = []
    for condition, label in LABELS.items():
        valid = [row for row in rows if row["condition"] == condition and row["checklist_valid"]]
        anchor = label.lower().replace(" ", "-")
        conditions.append({"condition": condition, "label": label, "checklist_n": len(valid),
                           "app_all_items_mean_met_percent": statistics.mean(row["app_all_items_met_percent"] for row in valid),
                           "checklist_list_url": f"{REPOSITORY}/tree/{BRANCH}/{EXPORT.as_posix()}#{anchor}"})
    index = {"schema_version": 1, "repository": REPOSITORY, "branch": BRANCH,
             "scope": "All 72 assigned runs; 68 valid primary checklist scores. Display export only.",
             "definitions": definitions, "encoder": encoder_identity,
             "sources": sources, "conditions": conditions, "runs": rows}
    for name, raw in response_copies.items():
        atomic_write(output / "responses" / name, raw)
    atomic_write(output / "index.json", json_bytes(index))
    atomic_write(output / "README.md", readme(rows).encode())
    manifest = {"schema_version": 1, "command": "pixi run poster-checklists",
                "scope": index["scope"], "encoder": encoder_identity, "sources": sources,
                "generator": entry(Path(__file__), Path("scripts/export_poster_checklists.py")),
                "label_source": entry(ROOT / "scripts/summarize_poster_outcomes.py", Path("scripts/summarize_poster_outcomes.py")),
                "outputs": [entry(output / "index.json", EXPORT / "index.json"),
                            entry(output / "README.md", EXPORT / "README.md")] + [
                    entry(output / "responses" / name, EXPORT / "responses" / name)
                    for name in sorted(response_copies)]}
    atomic_write(output / "manifest.json", json_bytes(manifest))
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reporting", type=Path, default=ROOT / REPORTING)
    parser.add_argument("--assessor", type=Path, default=ROOT / "assessment")
    parser.add_argument("--output", type=Path, default=ROOT / EXPORT)
    args = parser.parse_args()
    result = export(args.reporting.resolve(), args.assessor.resolve(), args.output.resolve())
    print(f'Exported {len(result["runs"])} original responses and 68 canonical filled-checklist links.')


if __name__ == "__main__":
    main()
