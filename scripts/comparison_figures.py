"""Static descriptive figures from normalized coordinator tables."""
from collections import defaultdict
import statistics

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


def legend(axis, labels, colors, columns=3):
    axis.legend(handles=[Patch(facecolor=color, edgecolor="#cccccc", label=label)
                         for label, color in zip(labels, colors)],
                loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=columns,
                frameon=False, fontsize=9)


def categorical(axis, values, colors):
    return axis.imshow(np.asarray(values), aspect="auto",
        cmap=ListedColormap(colors), norm=BoundaryNorm(np.arange(len(colors) + 1) - .5, len(colors)),
        interpolation="nearest")


def render(tables, items, output):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    runs = tables["runs"]
    primary = {j["run_id"]: j for j in tables["judgments"] if j["role"] == "primary"}
    answers = {(i["run_id"], i["item_id"]): i["status"] for i in tables["items"] if i["role"] == "primary"}
    valid = sum(j["response_status"] == "valid" for j in primary.values())
    groups = list(dict.fromkeys((r["round"], r["condition"]) for r in runs))
    groups.sort(key=lambda g: (g[0], list(dict.fromkeys(r["condition"] for r in runs)).index(g[1])))
    abbreviations = {"baseline": "B", "discover-general": "DG",
                     "discover-science": "DS", "stamped-explicit": "SE"}
    run_labels = [r["run_id"] + " (" + abbreviations.get(r["condition"], r["condition"]) + ")" for r in runs]
    group_labels = [f"R{round_id} · {condition}" for round_id, condition in groups]

    def sci(judgment):
        return judgment["adequacy"] or judgment["extraction_status"]

    fig, axes = plt.subplots(2, 1, figsize=(16, 8), gridspec_kw={"height_ratios": [1, 3]})
    categorical(axes[0], [[SCI_LABELS.index(sci(primary[r["run_id"]])) for r in runs]], SCI_COLORS)
    axes[0].set_xticks(range(len(runs)), run_labels, rotation=90, fontsize=7)
    axes[0].set_yticks([])
    axes[0].set_title(f"Scientific adequacy · one tile per assigned worker (n={len(runs)})\n"
                     "B baseline · DG general discovery · DS science discovery · SE explicit STAMPED", loc="left")
    left = np.zeros(len(groups))
    for status, color in zip(SCI_LABELS, SCI_COLORS):
        counts = [sum(sci(primary[r["run_id"]]) == status for r in runs
                      if (r["round"], r["condition"]) == group) for group in groups]
        axes[1].barh(range(len(groups)), counts, left=left, color=color, edgecolor="white")
        for y, (count, offset) in enumerate(zip(counts, left)):
            if count:
                axes[1].text(offset + count / 2, y, str(count), ha="center", va="center", fontsize=9)
        left += counts
    axes[1].set_yticks(range(len(groups)), [f"{label} (n={int(n)})" for label, n in zip(group_labels, left)])
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Assigned workers; categories describe support for the reported conclusion")
    legend(axes[1], SCI_LABELS, SCI_COLORS, 4)
    fig.tight_layout(h_pad=3)
    save(fig, output, "scientific-adequacy")

    labels = (*STATUSES, "assessment missing/invalid")
    matrix = [[STATUSES.index(answers[r["run_id"], i["id"]]) if (r["run_id"], i["id"]) in answers
               else len(STATUSES) for r in runs] for i in items]
    fig, ax = plt.subplots(figsize=(16, 11))
    categorical(ax, matrix, STATUS_COLORS)
    ax.set_xticks(range(len(runs)), run_labels, rotation=90, fontsize=8)
    ax.set_yticks(range(len(items)), [i["id"].split(":")[-1] + " · " + "/".join(i["dimension"]) for i in items])
    ax.set_title(f"Checklist items · primary judgments · {valid}/{len(runs)} valid assessments\n"
                 "Registered launch order · B baseline · DG general · DS science · SE explicit", loc="left", pad=15)
    legend(ax, labels, STATUS_COLORS)
    fig.tight_layout()
    save(fig, output, "item-statuses")

    fig, ax = plt.subplots(figsize=(13, 12))
    left = np.zeros(len(items))
    for index, (label, color) in enumerate(zip(labels, STATUS_COLORS)):
        counts = [sum(value == index for value in row) for row in matrix]
        ax.barh(range(len(items)), counts, left=left, color=color, edgecolor="white", height=.8)
        left += counts
    ax.set_yticks(range(len(items)), [i["id"].split(":")[-1] for i in items])
    ax.invert_yaxis()
    ax.set_xlabel(f"Assigned workers per item (n={len(runs)}); missing assessments are not item verdicts")
    ax.set_title("Recurring item outcomes · partial and unmet remain separate\n"
                 f"{valid}/{len(runs)} valid primary judgments; no combined certification score", loc="left")
    legend(ax, labels, STATUS_COLORS)
    fig.tight_layout()
    save(fig, output, "recurring-outcomes")

    by_scope = defaultdict(list)
    for row in tables["effort"]:
        by_scope[row["stage"], row["actor"], row["scope"]].append(row)
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
        ax.set_title(" · ".join(scope) + f"\n{len(rows)} verified measurements; durations are not summed", loc="left", fontsize=10)
    fig.tight_layout()
    save(fig, output, "effort")

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    paired = sum(p["item_pair_complete"] for p in tables["pairs"])
    scientific = sum(p["adequacy_pair_complete"] for p in tables["pairs"])
    item_matrix = np.zeros((len(STATUSES), len(STATUSES)), dtype=int)
    scientific_matrix = np.zeros((len(ADEQUACY), len(ADEQUACY)), dtype=int)
    for row in tables["disagreement"]:
        item_matrix[STATUSES.index(row["primary_status"]), STATUSES.index(row["duplicate_status"])] += 1
    for pair in tables["pairs"]:
        if pair["adequacy_pair_complete"]:
            scientific_matrix[ADEQUACY.index(pair["primary_adequacy"]), ADEQUACY.index(pair["duplicate_adequacy"])] += 1
    for ax, matrix, categories, title in (
        (axes[0], item_matrix, STATUSES, f"Checklist: {paired}/{len(tables['pairs'])} complete object pairs"),
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
        ax.set_title(title + "\nMissing pairs excluded and reported above", fontsize=10)
    fig.suptitle("Independent-judge disagreement · counts, not additional workers\n"
                 f"{len(tables['disagreement'])} item comparisons nested within {paired} objects", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, .88))
    save(fig, output, "duplicate-disagreement")
