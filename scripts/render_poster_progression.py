#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Plot existing round summaries without new judgments or scientific computation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from summarize_poster_outcomes import LABELS

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "experiments/retained-round-reporting/pooled/poster-outcomes.json"
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
            "checklist_mean_met_percent": checklist, "checklist_n": checklist_n,
            "checklist_unavailable": row["checklist_unavailable"],
            "checklist_evaluated_items_min": row["checklist_evaluated_items_min"],
            "checklist_evaluated_items_max": row["checklist_evaluated_items_max"],
            "checklist_status_counts": row["checklist_status_counts"],
        })
    return points


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
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    source, output = args.inputs.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    summary = json.loads(source.read_text())
    points = points_from_summary(summary)
    plt.rcParams.update({
        "font.family": ["Arial", "DejaVu Sans", "sans-serif"], "font.size": 24,
        "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
        "xtick.color": INK, "ytick.color": INK,
        "svg.fonttype": "none", "svg.hashsalt": "stamped-round-progression",
    })
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.5))
    fig.subplots_adjust(left=.075, right=.985, bottom=.16, top=.64, wspace=.32)
    # Small, fixed horizontal offsets keep coincident observations visible.
    offsets = dict(zip(LABELS, (-.06, -.02, .02, .06)))
    metrics = ("scientific_supported_percent", "checklist_mean_met_percent")
    titles = ("Analyses supported (%)", "Mean items met (%)")
    handles = []
    for condition, (color, marker, linestyle) in STYLES.items():
        group = sorted((p for p in points if p["condition"] == condition), key=lambda p: p["round"])
        x = [p["round"] + offsets[condition] for p in group]
        for ax, metric in zip(axes, metrics):
            y = [p[metric] if p[metric] is not None else float("nan") for p in group]
            ax.plot(x, y, color=color, marker=marker, linestyle=linestyle,
                    linewidth=3, markersize=11, markeredgecolor="white", markeredgewidth=1.2)
        handles.append(Line2D([], [], color=color, marker=marker, linestyle=linestyle,
                              linewidth=3, markersize=11, label=LABELS[condition]))
    for ax, title in zip(axes, titles):
        ax.set_title(title, fontsize=26, weight="bold", pad=18)
        ax.set_xlim(.8, 3.2)
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
        "research_and_assessment_revisions": summary["revisions"],
        "retained_source_hashes": summary["sources"],
        "definitions": {key: summary["definitions"][key] for key in ("science", "checklist", "pooling")},
        "points": points,
        "display": {"size_inches": [14, 6.5], "minimum_font_pt": 24,
                    "minimum_display_width_css_px_for_24pt": 1344,
                    "condition_x_offsets_for_visibility": offsets,
                    "lines": "Connect separate round summaries; they are not longitudinal trajectories of individual workers.",
                    "missing_values": "Unavailable means are omitted, never plotted as zero."},
        "caption": "Six assigned workers per condition per round; primary judgments only. Science is supported/assessed, not hypothesis direction. Checklist is the equal-run mean of met/(met+partial+unmet); not-checked and not-applicable items are excluded. Science n=5 for round 2 research discovery and round 3 STAMPED, otherwise 6. Checklist n=4 for round 1 baseline, n=5 for those same two groups, otherwise 6. Descriptive differences do not establish a causal skill effect.",
        "script_sha256": digest(Path(__file__)),
        "label_source_sha256": digest(ROOT / "scripts/summarize_poster_outcomes.py"),
        "software": {"matplotlib": matplotlib.__version__},
        "figure_sha256": {ext: digest(output / f"round-progression.{ext}") for ext in ("svg", "png")},
    }
    atomic_text(output / "round-progression-manifest.json", json.dumps(manifest, indent=2) + "\n")
    print("Rendered 12 retained round/condition summaries; all denominators preserved.")


if __name__ == "__main__":
    main()
