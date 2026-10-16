"""Static descriptive figures from normalized coordinator tables."""
from collections import defaultdict
import statistics
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
import numpy as np

from aggregate_comparison import ADEQUACY, STATUSES

STATUS_COLORS = ("#358061", "#e8b44c", "#bd5355", "#929aa6", "#bcabd1", "#eceff3")
SCI_COLORS = ("#358061", "#e8b44c", "#bd5355", "#929aa6", "#eceff3", "#bcabd1", "#343a46")
SCI_LABELS = (*ADEQUACY, "missing", "ambiguous", "invalid")


def save(fig, output, name):
    fig.savefig(output / (name + ".svg"), bbox_inches="tight")
    fig.savefig(output / (name + ".png"), dpi=170, bbox_inches="tight")
    plt.close(fig)


def legend(axis, labels, colors, columns=3, anchor=(0.5, -0.13)):
    axis.legend(handles=[Patch(facecolor=color, edgecolor="#cccccc", label=label)
                         for label, color in zip(labels, colors)],
                loc="upper center", bbox_to_anchor=anchor, ncol=columns,
                frameon=False, fontsize=9)


def categorical(axis, values, colors):
    return axis.imshow(np.asarray(values), aspect="auto",
        cmap=ListedColormap(colors), norm=BoundaryNorm(np.arange(len(colors) + 1) - .5, len(colors)),
        interpolation="nearest")


def _render_outcomes(tables, items, output, version=None, registered_runs=None):
    runs = tables["runs"]
    registered_runs = runs if registered_runs is None else registered_runs
    primary = {j["run_id"]: j for j in tables["judgments"] if j["role"] == "primary"}
    source = tables["comparable_items"] if version else tables["items"]
    answers = {(i["run_id"], i["judgment_id"], i["item_id"]): i["status"]
               for i in source if i["role"] == "primary"}
    validity = {(i["run_id"], i["judgment_id"], i["item_id"]): i["validity"]
                for i in tables.get("measure_validity", []) if i["role"] == "primary"}
    valid = sum(j["response_status"] == "valid" for j in primary.values())
    groups = list(dict.fromkeys((r["round"], r["condition"]) for r in registered_runs))
    groups.sort(key=lambda g: (g[0], list(dict.fromkeys(r["condition"] for r in registered_runs)).index(g[1])))
    abbreviations = {"baseline": "B", "discover-general": "DG",
                     "discover-science": "DS", "stamped-explicit": "SE"}
    run_labels = [r["run_id"] + " (" + abbreviations.get(r["condition"], r["condition"]) + ")" for r in runs]
    group_labels = [f"R{round_id} · {condition}" for round_id, condition in groups]

    def finish(fig, name):
        if version:
            fig.text(.01, .01, f"Assessment procedure: {version}\n"
                     "Condition coverage is shown within each version; empty cells are not outcomes. "
                     "No pooled cross-version comparison.", fontsize=8)
            fig.tight_layout(rect=(0, .065, 1, 1))
        save(fig, output, name + ("-" + version[:12] if version else ""))

    def sci(judgment):
        return judgment["adequacy"] or judgment["extraction_status"]

    fig, axes = plt.subplots(2, 1, figsize=(16, 8), gridspec_kw={"height_ratios": [1, 3]})
    dependencies = {r["run_id"] for r in runs
                    if (primary[r["run_id"]].get("scientific_dependency") or {}).get("status") == "uncertain"}
    if runs:
        categorical(axes[0], [[SCI_LABELS.index(sci(primary[r["run_id"]])) for r in runs]], SCI_COLORS)
    else:
        axes[0].text(.5, .5, "No primary workers assigned to this version", ha="center",
                     transform=axes[0].transAxes)
    axes[0].set_xticks(range(len(runs)), [label + (" *" if r["run_id"] in dependencies else "")
                                        for r, label in zip(runs, run_labels)], rotation=90, fontsize=7)
    axes[0].set_yticks([])
    axes[0].set_title(f"Scientific adequacy · one tile per assigned worker (n={len(runs)})\n"
                     "B baseline · DG general discovery · DS science discovery · SE explicit STAMPED"
                     + ("\n* Uncertain dependency on affected helper evidence; raw category unchanged"
                        if dependencies else ""), loc="left")
    left = np.zeros(len(groups))
    for status, color in zip(SCI_LABELS, SCI_COLORS):
        counts = [sum(sci(primary[r["run_id"]]) == status for r in runs
                      if (r["round"], r["condition"]) == group) for group in groups]
        axes[1].barh(range(len(groups)), counts, left=left, color=color, edgecolor="white")
        for y, (count, offset) in enumerate(zip(counts, left)):
            if count:
                axes[1].text(offset + count / 2, y, str(count), ha="center", va="center", fontsize=9,
                             color="white" if status == "invalid" else "black")
        left += counts
    assigned = [sum((r["round"], r["condition"]) == group for r in registered_runs) for group in groups]
    axes[1].set_yticks(range(len(groups)), [
        f"{label} ({int(n)}/{total} workers assigned to version)" if version else f"{label} (n={int(n)})"
        for label, n, total in zip(group_labels, left, assigned)])
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Assigned workers; categories describe support for the reported conclusion")
    legend(axes[1], SCI_LABELS, SCI_COLORS, 4)
    fig.tight_layout(h_pad=3)
    finish(fig, "scientific-adequacy")

    labels = (*STATUSES, "assessment missing/invalid")
    colors = STATUS_COLORS
    if version:
        labels = (*STATUSES, "assessment missing", "assessment invalid",
                  "measurement unavailable", "measurement invalid")
        colors = (*STATUS_COLORS, "#343a46", "#75b9c5", "#a563a1")

    def item_label(run, item):
        judgment = primary[run["run_id"]]
        key = (run["run_id"], judgment["judgment_id"], item["id"])
        if version and judgment["response_status"] == "valid" and validity.get(key) in ("unavailable", "invalid"):
            return "measurement " + validity[key]
        if key in answers:
            return answers[key]
        if not version:
            return "assessment missing/invalid"
        if judgment["response_status"] == "invalid":
            return "assessment invalid"
        if judgment["response_status"] == "valid":
            return "measurement unavailable"
        return "assessment missing"

    matrix = [[labels.index(item_label(r, i)) for r in runs] for i in items]
    fig, (ax, key) = plt.subplots(2, 1, figsize=(16, 11),
                                 gridspec_kw={"height_ratios": [31, 1]})
    key.axis("off")
    if runs:
        categorical(ax, matrix, colors)
    else:
        ax.text(.5, .5, "No primary workers assigned to this version", ha="center", transform=ax.transAxes)
    ax.set_xticks(range(len(runs)), run_labels, rotation=90, fontsize=8)
    ax.set_yticks(range(len(items)), [i["id"].split(":")[-1] + " · " + "/".join(i["dimension"]) for i in items])
    ax.set_title(f"Checklist items · primary judgments · {valid}/{len(runs)} valid response files\n"
                 "Registered launch order · B baseline · DG general · DS science · SE explicit", loc="left", pad=15)
    legend(key, labels, colors, anchor=(0.5, 1))
    fig.tight_layout()
    finish(fig, "item-statuses")

    fig, ax = plt.subplots(figsize=(13, 12))
    left = np.zeros(len(items))
    for index, (label, color) in enumerate(zip(labels, colors)):
        counts = [sum(value == index for value in row) for row in matrix]
        ax.barh(range(len(items)), counts, left=left, color=color, edgecolor="white", height=.8)
        left += counts
    ax.set_yticks(range(len(items)), [i["id"].split(":")[-1] for i in items])
    ax.invert_yaxis()
    ax.set_xlabel(f"Assigned workers per item (n={len(runs)}); missing assessments are not item verdicts")
    ax.set_title("Recurring item outcomes · pooled across conditions and rounds\n"
                 f"{valid}/{len(runs)} valid response files; descriptive only, not evidence of improvement",
                 loc="left")
    legend(ax, labels, colors)
    fig.tight_layout()
    finish(fig, "recurring-outcomes")

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    paired = sum(p["item_pair_complete"] for p in tables["pairs"])
    observed_pairs = len({r["run_id"] for r in tables["disagreement"]})
    scientific = sum(p["adequacy_pair_complete"] for p in tables["pairs"])
    item_matrix = np.zeros((len(STATUSES), len(STATUSES)), dtype=int)
    scientific_matrix = np.zeros((len(ADEQUACY), len(ADEQUACY)), dtype=int)
    for row in tables["disagreement"]:
        item_matrix[STATUSES.index(row["primary_status"]), STATUSES.index(row["duplicate_status"])] += 1
    for pair in tables["pairs"]:
        if pair["adequacy_pair_complete"]:
            scientific_matrix[ADEQUACY.index(pair["primary_adequacy"]), ADEQUACY.index(pair["duplicate_adequacy"])] += 1
    for ax, matrix, categories, title in (
        (axes[0], item_matrix, STATUSES,
         f"Checklist: {observed_pairs}/{len(tables['pairs'])} objects with comparable items" if version else
         f"Checklist: {paired}/{len(tables['pairs'])} complete object pairs"),
        (axes[1], scientific_matrix, ADEQUACY, f"Scientific adequacy: {scientific}/{len(tables['pairs'])} complete pairs"),
    ):
        ax.imshow(matrix, cmap="Blues", vmin=0, vmax=max(1, matrix.max()))
        for y in range(len(categories)):
            for x in range(len(categories)):
                ax.text(x, y, str(matrix[y, x]), ha="center", va="center",
                        color="white" if matrix[y, x] > max(1, matrix.max()) / 2 else "black")
        ax.set_xticks(range(len(categories)), categories, rotation=35, ha="right")
        ax.set_yticks(range(len(categories)), categories)
        ax.set_xlabel("Preselected duplicate")
        ax.set_ylabel("First assigned judgment")
        ax.set_title(title + ("\nOnly same-version, mutually valid measures compared" if version else
                             "\nMissing pairs excluded and reported above"), fontsize=10)
    unavailable = sum(bool(p.get("comparison_unavailable_reason")) for p in tables["pairs"])
    fig.suptitle("Independent-judge disagreement · counts, not additional workers\n"
                 f"{len(tables['disagreement'])} item comparisons nested within {observed_pairs} objects"
                 + (f"; {unavailable} unavailable pairs" if version else ""), fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, .88))
    finish(fig, "duplicate-disagreement")


def _render_effort(tables, output, stratified=False):
    runs = tables["runs"]
    groups = list(dict.fromkeys((r["round"], r["condition"]) for r in runs))
    conditions = list(dict.fromkeys(r["condition"] for r in runs))
    groups.sort(key=lambda g: (g[0], conditions.index(g[1])))
    group_labels = [f"R{round_id} · {condition}" for round_id, condition in groups]
    judgments = {(j["run_id"], j["role"]): j for j in tables["judgments"]}
    by_scope = defaultdict(list)
    for row in tables["effort"]:
        scope = (row["stage"], row["actor"], row["scope"], row["assessment_scope"])
        if stratified:
            version = row.get("procedure_sha256")
            if not version and row.get("judgment_role"):
                version = judgments.get((row["run_id"], row["judgment_role"]), {}).get("procedure_sha256")
            scope += ("assessment " + version[:12] if version else "assessment version unassigned",)
        by_scope[scope].append(row)
    fig, axes = plt.subplots(max(1, len(by_scope)), 1, figsize=(12, max(4, 3.8 * len(by_scope))), squeeze=False)
    if not by_scope:
        axes[0, 0].axis("off")
        axes[0, 0].text(.5, .5, f"No verified duration measurements\n{len(runs)} assigned workers; missing is not zero",
                       ha="center", va="center", transform=axes[0, 0].transAxes, fontsize=14)
    for ax, (scope, rows) in zip(axes[:, 0], by_scope.items()):
        for y, group in enumerate(groups):
            values = [r["duration_s"] / 60 for r in rows if (r["round"], r["condition"]) == group]
            if values:
                jitter = np.linspace(-.14, .14, len(values)) if len(values) > 1 else [0]
                ax.scatter(values, y + np.asarray(jitter), color="#276d99", s=25, zorder=3)
                ax.plot([min(values), max(values)], [y, y], color="#444444", linewidth=1)
                ax.plot(statistics.median(values), y, marker="|", color="black", markersize=12)
        counts = [sum((r["round"], r["condition"]) == group for r in rows) for group in groups]
        workers = [len({r["run_id"] for r in rows if (r["round"], r["condition"]) == group}) for group in groups]
        assigned = [sum((r["round"], r["condition"]) == group for r in runs) for group in groups]
        ax.set_yticks(range(len(groups)),
                     [f"{label} ({n}/{denom} workers; {count} obs.)"
                      for label, n, denom, count in zip(group_labels, workers, assigned, counts)], fontsize=8)
        ax.invert_yaxis()
        ax.set_xlim(left=0, right=max(1, max(r["duration_s"] for r in rows) / 60 * 1.1))
        ax.set_xlabel("Minutes per recorded operation · points, median and observed range")
        title = textwrap.fill(" · ".join(scope), width=95,
                              break_long_words=False, break_on_hyphens=False)
        ax.set_title(title + f"\n{len(rows)} verified measurements; durations are not summed", loc="left", fontsize=10)
    fig.tight_layout()
    save(fig, output, "effort")


def render(tables, items, output):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    strata = tables.get("version_strata")
    if not strata:
        _render_outcomes(tables, items, output)
        _render_effort(tables, output)
        return
    versions = list(dict.fromkeys(row["procedure_sha256"] for row in strata))
    if len({version[:12] for version in versions}) != len(versions):
        raise ValueError("Assessment digest prefixes collide in figure filenames")
    primary = {j["run_id"]: j for j in tables["judgments"] if j["role"] == "primary"}
    for version in versions:
        run_ids = {run_id for run_id, judgment in primary.items()
                   if judgment["procedure_sha256"] == version}
        selected = dict(tables)
        for name in ("runs", "judgments", "items", "pairs", "disagreement"):
            selected[name] = [row for row in tables[name] if row["run_id"] in run_ids]
        for name in ("comparable_items", "measure_validity"):
            selected[name] = [row for row in tables[name]
                              if row["run_id"] in run_ids and row["procedure_sha256"] == version]
        _render_outcomes(selected, items, output, version, tables["runs"])
    _render_effort(tables, output, stratified=True)
