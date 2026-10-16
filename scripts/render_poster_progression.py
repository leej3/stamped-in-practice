#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Plot existing round summaries without new judgments or scientific computation."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import scipy
from scipy.stats import binomtest

from summarize_poster_outcomes import LABELS

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "experiments/retained-round-reporting/pooled/poster-outcomes.json"
RUNS = ROOT / "experiments/retained-round-reporting/pooled/run-outcomes.json"
OUT = ROOT / "experiments/narps-poster/figures"
INK = "#193c4d"
STYLES = {
    "baseline": ("#386f9f", "o", "-"),
    "discover-general": ("#b56a28", "s", "--"),
    "discover-science": ("#80629e", "^", "-."),
    "stamped-explicit": ("#286857", "D", ":"),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_text(path, text):
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        stream.write(text)
        temporary = Path(stream.name)
    temporary.replace(path)


def points_from_summary(summary):
    """Validate the existing denominators; never replace missing values with zero."""
    if summary["retained_rounds"] != [1, 2, 3]:
        raise ValueError("Expected the three retained rounds")
    rows = summary["round_conditions"]
    expected = {(r, c) for r in (1, 2, 3) for c in LABELS}
    if len(rows) != 12 or {(r["round"], r["condition"]) for r in rows} != expected:
        raise ValueError("Expected one row per round and assistance condition")
    points = []
    for row in rows:
        assigned = row["assigned_runs"]
        science_n = row["scientific_n"]
        checklist_n = row["checklist_n"]
        supported = row["science"]["supported"]
        checklist = row["checklist_mean_met_percent"]
        if assigned != 6 or not 0 <= supported <= science_n <= assigned:
            raise ValueError("Invalid scientific denominator")
        if sum(row["science"].values()) != science_n:
            raise ValueError("Scientific category counts disagree with available n")
        if science_n + row["scientific_unavailable"] != assigned:
            raise ValueError("Scientific missingness does not preserve assigned n")
        if not 0 <= checklist_n <= assigned or checklist_n + row["checklist_unavailable"] != assigned:
            raise ValueError("Checklist missingness does not preserve assigned n")
        if (checklist_n == 0) != (checklist is None) or (checklist is not None and not 0 <= checklist <= 100):
            raise ValueError("Invalid checklist mean or missingness")
        points.append({
            "round": row["round"], "condition": row["condition"],
            "label": LABELS[row["condition"]], "assigned_runs": assigned,
            "scientific_supported": supported, "scientific_n": science_n,
            "scientific_unavailable": row["scientific_unavailable"],
            "scientific_supported_percent": 100 * supported / science_n if science_n else None,
            "scientific_category_counts": row["science"],
            "checklist_mean_met_percent": checklist, "checklist_n": checklist_n,
            "checklist_sd_met_percent": row["checklist_sd_met_percent"],
            "checklist_unavailable": row["checklist_unavailable"],
            "checklist_evaluated_items_min": row["checklist_evaluated_items_min"],
            "checklist_evaluated_items_max": row["checklist_evaluated_items_max"],
            "checklist_status_counts": row["checklist_status_counts"],
        })
    return points


def wilson_percent(supported, assessed):
    if not assessed:
        return None, None
    interval = binomtest(supported, assessed).proportion_ci(confidence_level=.95, method="wilson")
    return 100 * interval.low, 100 * interval.high


def attach_run_statistics(points, runs):
    """Cross-check original per-run values before plotting spread and intervals."""
    if len(runs) != 72 or len({row["run_id"] for row in runs}) != 72:
        raise ValueError("Expected all 72 distinct retained research runs")
    run_points = []
    for point in points:
        group = sorted((row for row in runs if row["round"] == point["round"]
                        and row["condition"] == point["condition"]), key=lambda row: row["run_id"])
        if len(group) != point["assigned_runs"]:
            raise ValueError("Run membership differs from the round summary")
        science = Counter(row["science"] for row in group if row["science"] is not None)
        if science != Counter(point["scientific_category_counts"]):
            raise ValueError("Scientific outcomes differ between run and summary inputs")
        values, valid_rows = [], []
        for run in group:
            fraction = run["checklist_met_fraction"]
            if not run["checklist_valid"]:
                if fraction is not None:
                    raise ValueError("Unavailable checklist cannot supply a score")
                continue
            counts = run["checklist_status_counts"]
            denominator = sum(counts.get(status, 0) for status in ("met", "partial", "unmet"))
            if (not denominator or denominator != run["checklist_evaluated_items"]
                    or fraction != counts.get("met", 0) / denominator):
                raise ValueError("Per-run checklist score differs from its recorded counts")
            values.append(100 * fraction)
            valid_rows.append(run)
        if len(values) != point["checklist_n"]:
            raise ValueError("Checklist availability differs between run and summary inputs")
        mean = statistics.mean(values) if values else None
        sd = statistics.stdev(values) if len(values) > 1 else None
        for value, key in ((mean, "checklist_mean_met_percent"), (sd, "checklist_sd_met_percent")):
            saved = point[key]
            if (value is None) != (saved is None) or (value is not None and not math.isclose(value, saved, abs_tol=1e-12)):
                raise ValueError("Checklist mean or sample SD differs from the retained summary")
        point["scientific_interval_lower_percent"], point["scientific_interval_upper_percent"] = wilson_percent(
            point["scientific_supported"], point["scientific_n"])
        point["checklist_sd_lower_percent"] = mean - sd if sd is not None else None
        point["checklist_sd_upper_percent"] = mean + sd if sd is not None else None
        for index, run in enumerate(valid_rows):
            # Fixed order and spread: no random jitter or data-dependent optimization.
            offset = .09 * (index / (len(valid_rows) - 1) - .5) if len(valid_rows) > 1 else 0
            run_points.append({"run_id": run["run_id"], "judgment_id": run["judgment_id"],
                               "round": run["round"], "condition": run["condition"],
                               "checklist_met_percent": 100 * run["checklist_met_fraction"],
                               "met_count": run["checklist_status_counts"].get("met", 0),
                               "evaluated_count": run["checklist_evaluated_items"],
                               "within_condition_x_offset": offset})
    return run_points


def save(fig, output):
    for extension in ("svg", "png"):
        with tempfile.NamedTemporaryFile(dir=output, suffix=f".{extension}", delete=False) as stream:
            temporary = Path(stream.name)
        try:
            fig.savefig(temporary, format=extension, dpi=160, facecolor="white",
                        metadata={"Date": None} if extension == "svg" else {})
            if extension == "svg":
                temporary.write_text("\n".join(line.rstrip() for line in temporary.read_text().splitlines()) + "\n")
            temporary.replace(output / f"round-progression.{extension}")
        finally:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=INPUT)
    parser.add_argument("--runs", type=Path, default=RUNS)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    source, output = args.inputs.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    summary = json.loads(source.read_text())
    points = points_from_summary(summary)
    run_source = args.runs.resolve()
    run_points = attach_run_statistics(points, json.loads(run_source.read_text()))
    plt.rcParams.update({
        "font.family": ["Arial", "DejaVu Sans", "sans-serif"], "font.size": 24,
        "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
        "xtick.color": INK, "ytick.color": INK,
        "svg.fonttype": "none", "svg.hashsalt": "stamped-round-progression",
    })
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.5))
    fig.subplots_adjust(left=.075, right=.985, bottom=.16, top=.64, wspace=.32)
    # Small, fixed horizontal offsets keep coincident observations visible.
    offsets = dict(zip(LABELS, (-.21, -.07, .07, .21)))
    metrics = ("scientific_supported_percent", "checklist_mean_met_percent")
    titles = ("Analyses supported (%)", "Evaluated items met (%)")
    handles = []
    for condition, (color, marker, linestyle) in STYLES.items():
        group = sorted((p for p in points if p["condition"] == condition), key=lambda p: p["round"])
        x = [p["round"] + offsets[condition] for p in group]
        for ax, metric in zip(axes, metrics):
            y = [p[metric] if p[metric] is not None else float("nan") for p in group]
            ax.plot(x, y, color=color, marker=marker, linestyle=linestyle,
                    linewidth=2, markersize=9, markeredgecolor="white", markeredgewidth=1.2, zorder=4)
            lower_key, upper_key = (("scientific_interval_lower_percent", "scientific_interval_upper_percent")
                                    if ax is axes[0] else ("checklist_sd_lower_percent", "checklist_sd_upper_percent"))
            selected = [p for p in group if p[lower_key] is not None]
            ax.errorbar([p["round"] + offsets[condition] for p in selected], [p[metric] for p in selected],
                        yerr=[[max(0, p[metric] - p[lower_key]) for p in selected],
                              [max(0, p[upper_key] - p[metric]) for p in selected]],
                        fmt="none", ecolor=color, elinewidth=1.8, capsize=4, capthick=1.8, zorder=2)
        individual = [p for p in run_points if p["condition"] == condition]
        axes[1].scatter([p["round"] + offsets[condition] + p["within_condition_x_offset"] for p in individual],
                        [p["checklist_met_percent"] for p in individual], color=color, marker=marker,
                        s=32, alpha=.8, edgecolors="white", linewidths=.4, zorder=3)
        handles.append(Line2D([], [], color=color, marker=marker, linestyle=linestyle,
                              linewidth=3, markersize=11, label=LABELS[condition]))
    for ax, title in zip(axes, titles):
        ax.set_title(title, fontsize=26, weight="bold", pad=18)
        ax.set_xlim(.65, 3.35)
        ax.set_ylim(-4, 105)
        ax.set_xticks([1, 2, 3])
        ax.set_yticks([0, 50, 100])
        ax.set_xlabel("Round", labelpad=8)
        ax.grid(axis="y", color="#d4dedb", linewidth=1)
        ax.set_axisbelow(True)
        ax.tick_params(length=0, pad=9)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color("#a5b7b1")
    # Sample SD is a spread measure, not a bounded confidence interval.
    lower = [p["checklist_sd_lower_percent"] for p in points if p["checklist_sd_lower_percent"] is not None]
    upper = [p["checklist_sd_upper_percent"] for p in points if p["checklist_sd_upper_percent"] is not None]
    if lower and upper:
        axes[1].set_ylim(min(-4, min(lower) - 4), max(105, max(upper) + 4))
    # Legend is read row-wise in the same order as the poster's outcome table.
    fig.legend(handles=[handles[i] for i in (0, 2, 1, 3)], ncol=2, frameon=False,
               loc="upper center", bbox_to_anchor=(.5, 1.01), fontsize=24,
               columnspacing=1.8, handlelength=2, labelspacing=.55)
    save(fig, output)
    plt.close(fig)
    manifest = {
        "schema_version": 1,
        "scope": "Descriptive progression of retained primary summaries; no new analysis, judgment or causal inference.",
        "input": {"path": "experiments/retained-round-reporting/pooled/poster-outcomes.json",
                  "sha256": digest(source), "bytes": source.stat().st_size},
        "run_input": {"path": "experiments/retained-round-reporting/pooled/run-outcomes.json",
                      "sha256": digest(run_source), "bytes": run_source.stat().st_size},
        "research_and_assessment_revisions": summary["revisions"],
        "retained_source_hashes": summary["sources"],
        "definitions": {key: summary["definitions"][key] for key in ("science", "checklist", "pooling")},
        "points": points,
        "checklist_run_points": run_points,
        "statistical_methods": {
            "science": "95% Wilson score intervals via scipy.stats.binomtest(k, n).proportion_ci(confidence_level=0.95, method='wilson'), with k supported and n assessed primary judgments. These intervals are conditional on the binomial model of independent runs with a common success probability within each condition/round.",
            "checklist": "Small points are the 68 available original primary run percentages. Large markers are equal-run means; bars show plus/minus one sample SD (ddof=1), describing observed worker-score variation, not a confidence interval or standard error.",
            "limits": "Bars do not account for judge disagreement, missing or excluded assessments, shared-host or model dependence, or other design uncertainties. Round-to-round differences do not establish a causal skill effect.",
        },
        "display": {"size_inches": [14, 6.5], "minimum_font_pt": 24,
                    "minimum_display_width_css_px_for_24pt": 1344,
                    "condition_x_offsets_for_visibility": offsets,
                    "lines": "Connect separate round summaries; they are not longitudinal trajectories of individual workers.",
                    "missing_values": "Unavailable means are omitted, never plotted as zero."},
        "caption": "Six assigned workers per condition per round; primary judgments only. Science: supported/assessed with 95% Wilson intervals. Checklist: individual evaluated-item fractions, equal-run mean and plus/minus sample SD. Science n=5 for round 2 research discovery and round 3 STAMPED, otherwise 6; checklist n=4 for round 1 baseline, n=5 for those same two groups, otherwise 6. Bars omit judge, missingness and shared-host uncertainty; differences do not establish a causal skill effect.",
        "script_sha256": digest(Path(__file__)),
        "label_source_sha256": digest(ROOT / "scripts/summarize_poster_outcomes.py"),
        "software": {"matplotlib": matplotlib.__version__, "scipy": scipy.__version__},
        "figure_sha256": {ext: digest(output / f"round-progression.{ext}") for ext in ("svg", "png")},
    }
    atomic_text(output / "round-progression-manifest.json", json.dumps(manifest, indent=2) + "\n")
    print("Rendered 12 retained round/condition summaries; all denominators preserved.")


if __name__ == "__main__":
    main()
