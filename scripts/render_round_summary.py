"""Render a round from validated tables without reclassifying any observation."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from aggregate_comparison import load_contract
from comparison_figures import render, save


CONDITIONS = ("baseline", "discover-general", "discover-science", "stamped-explicit")
LABELS = ("Baseline", "General discovery", "Science discovery", "Explicit STAMPED")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_round(tables, number):
    selected = {row["run_id"] for row in tables["runs"] if row["round"] == number}
    if not selected:
        raise ValueError("Requested round has no assigned workers")
    result = {}
    for name, rows in tables.items():
        result[name] = []
        for row in rows:
            if "run_id" in row:
                keep = row["run_id"] in selected
            elif "round" in row:
                keep = row["round"] == number
            else:
                raise ValueError("Cannot scope nonempty table to a round: " + name)
            if keep:
                result[name].append(row)
    return result


def token_rows(tables):
    rows, seen = [], set()
    for operation in tables["operations"]:
        if operation["stage"] != "worker" or operation["evidence_status"] != "valid":
            continue
        metrics = [m for m in operation.get("metrics", []) if m["unit"] == "tokens"]
        values = {m["name"]: m["value"] for m in metrics}
        if len(values) != len(metrics):
            raise ValueError("Duplicate token metric")
        required = {"input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"}
        if not required <= values.keys():
            continue
        if operation["run_id"] in seen:
            raise ValueError("Multiple worker token operations need explicit interpretation")
        seen.add(operation["run_id"])
        if not (0 <= values["cached_input_tokens"] <= values["input_tokens"] and
                0 <= values["reasoning_output_tokens"] <= values["output_tokens"]):
            raise ValueError("Invalid subset token counts")
        rows.append({"run_id": operation["run_id"], "condition": operation["condition"],
                     "operation_id": operation["operation_id"], "metrics": metrics,
                     "values": values, "evidence": operation["evidence"]})
    return rows


def render_tokens(tables, output):
    rows = token_rows(tables)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), sharey=True)
    panels = [("input_tokens", 1e6, "Reported input tokens (millions)"),
              ("output_tokens", 1e3, "Reported output tokens (thousands)"),
              ("cached_share", 1, "Cached input / input (%)")]
    labels = []
    for condition, label in zip(CONDITIONS, LABELS):
        n = sum(row["condition"] == condition for row in rows)
        assigned = sum(row["condition"] == condition for row in tables["runs"])
        labels.append(f"{label} ({n}/{assigned})")
    for axis, (metric, scale, label) in zip(axes, panels):
        for y, condition in enumerate(CONDITIONS):
            group = [row for row in rows if row["condition"] == condition]
            values = [(100 * row["values"]["cached_input_tokens"] / row["values"]["input_tokens"]
                       if row["values"]["input_tokens"] else None)
                      if metric == "cached_share" else row["values"][metric] / scale for row in group]
            values = [value for value in values if value is not None]
            if values:
                axis.scatter(values, y + np.linspace(-.14, .14, len(values)), s=32,
                             color="#315c8c", alpha=.8)
                axis.plot([statistics.median(values)] * 2, [y - .23, y + .23],
                          color="#172f49", linewidth=2)
        axis.set_xlabel(label)
        axis.set_xlim(left=0)
        if metric == "cached_share":
            axis.set_xlim(0, 105)
        axis.grid(axis="x", alpha=.2)
    axes[0].set_yticks(range(len(CONDITIONS)), labels)
    axes[0].invert_yaxis()
    fig.suptitle("Research session usage · individual workers and medians", x=.01, ha="left")
    fig.text(.01, .01, "Parent native sessions only; no billing inference. Cached input is a subset of input; "
             "reasoning output is a subset of output.\nNeither subset is added again. Labels show observed / assigned workers; "
             "missing metrics are omitted, not zero.", fontsize=9)
    fig.tight_layout(rect=(0, .12, 1, .94))
    save(fig, output, "research-token-usage")
    return rows


def read_skill_observations(root, tables):
    selected = {row["run_id"]: row["condition"] for row in tables["runs"]}
    rows, seen = [], set()
    for path in sorted(root.glob("*.json")):
        value = json.loads(path.read_bytes())
        if value.get("kind") != "coordinator-skill-use-observations":
            continue
        run = value["run_id"]
        if run not in selected:
            continue
        if run in seen or value["assigned_condition"] != selected[run]:
            raise ValueError("Duplicate or mismatched skill observation: " + run)
        seen.add(run)
        observations = value["observations"]
        for key in ("discovery", "installation", "loaded"):
            if type(observations[key]) is not bool:
                raise ValueError("Skill counts require explicit observed-action booleans")
        rows.append({"run_id": run, "condition": selected[run], "observations": observations,
                     "source": str(path), "sha256": digest(path)})
    return rows


def render_skill_observations(rows, tables, output):
    fig, axis = plt.subplots(figsize=(10.5, 5))
    features = [("discovery", "Discovery observed"), ("installation", "Worker installation observed"),
                ("loaded", "Any skill instructions read")]
    colors = ("#376b85", "#78a6a1", "#d8aa56")
    for i, ((key, label), color) in enumerate(zip(features, colors)):
        counts = [sum(row["observations"][key] for row in rows if row["condition"] == condition)
                  for condition in CONDITIONS]
        positions = np.arange(len(CONDITIONS)) + (i - 1) * .23
        axis.barh(positions, counts, height=.21, label=label, color=color)
        for y, count in zip(positions, counts):
            axis.text(count + .06, y, str(count), va="center", fontsize=9)
    labels = [f"{label} ({sum(r['condition'] == c for r in rows)}/"
              f"{sum(r['condition'] == c for r in tables['runs'])} observed)"
              for c, label in zip(CONDITIONS, LABELS)]
    axis.set_yticks(range(len(CONDITIONS)), labels)
    axis.invert_yaxis()
    axis.set_xlim(0, max(1, max(sum(r["condition"] == c for r in tables["runs"])
                              for c in CONDITIONS)) + .7)
    axis.set_xlabel("Workers with the recorded action; counts are not additive")
    axis.set_title("Observed discovery, installation and instruction reading", loc="left")
    axis.legend(loc="upper center", bbox_to_anchor=(.5, -.18), ncol=3, frameon=False, fontsize=9)
    fig.text(.01, .01, "Supplied STAMPED guidance requires no worker installation. Instruction reads include the installer.\n"
             "Availability, reading, application and scientific benefit are distinct; this panel does not establish benefit.",
             fontsize=9)
    fig.tight_layout(rect=(0, .14, 1, 1))
    save(fig, output, "observed-skill-actions")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--round", type=int, required=True)
    parser.add_argument("--assessor", type=Path, required=True)
    parser.add_argument("--assessment-pin", type=Path, required=True)
    parser.add_argument("--skill-observations", type=Path,
                        help="Directory of retained coordinator observation JSON records")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads((args.analysis / "aggregation.json").read_bytes())
    contract = load_contract(args.assessor, args.assessment_pin)
    if source["assessment_pin"] != contract.assessment_pin:
        raise ValueError("Figure contract differs from the validated aggregation")
    paths = sorted(args.analysis.glob("*.jsonl"))
    tables = {path.stem: [json.loads(line) for line in path.read_text().splitlines()] for path in paths}
    selected = select_round(tables, args.round)
    args.output.mkdir(parents=True, exist_ok=False)
    render(selected, contract.items, args.output)
    tokens = render_tokens(selected, args.output)
    observations = read_skill_observations(args.skill_observations, selected) if args.skill_observations else []
    if args.skill_observations:
        render_skill_observations(observations, selected, args.output)
    receipt = {"scope": "Round-filtered presentation of validated tables; no regrading, imputation or changed admission.",
               "round": args.round, "assigned_workers": len(selected["runs"]),
               "assigned_judgments": len(selected["judgments"]),
               "source_aggregation": {"path": str(args.analysis / "aggregation.json"),
                                      "sha256": digest(args.analysis / "aggregation.json")},
               "source_tables": [{"path": str(path), "sha256": digest(path)} for path in paths],
               "renderer_sha256": digest(Path(__file__)), "token_rows": tokens,
               "skill_observations": observations}
    (args.output / "presentation.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
