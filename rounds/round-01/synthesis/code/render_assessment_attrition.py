"""Render assigned assessment availability, separately from scientific grades."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


CONDITIONS = ("baseline", "discover-general", "discover-science", "stamped-explicit")
LABELS = ("Baseline", "General discovery", "Science discovery", "Explicit STAMPED")
STATUSES = ("usable", "metadata-unavailable", "other-unavailable")
COLORS = ("#286D80", "#B65430", "#656B73")
METADATA = {"content/workspace/.git/annex/keysdb/" + name
            for name in ("db", "db-shm", "db-wal")}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(record, delta=None):
    if record["response_status"] == "valid":
        return "usable"
    if record["response_status"] == "pending":
        raise ValueError("The assigned round is not complete")
    if (record.get("provenance_error") !=
            "Malformed provenance: target_unchanged: True was expected" or delta is None):
        return "other-unavailable"
    paths = {row["path"] for kind in ("added", "missing", "modified")
             for row in delta[kind]}
    if (paths and paths <= METADATA and
            delta["baseline_manifest_bytes_identical_to_original_worker_capture_manifest"] and
            delta["baseline_manifest_sha256"] == record["delivery_capture"]["sha256"]):
        return "metadata-unavailable"
    return "other-unavailable"


def counts(rows):
    if len(rows) != 32 or len({r["judgment_id"] for r in rows}) != 32:
        raise ValueError("Expected all 32 distinct assigned judgments")
    expected = Counter({(c, "primary"): 6 for c in CONDITIONS})
    expected.update({(c, "duplicate"): 2 for c in CONDITIONS})
    if Counter((r["condition"], r["role"]) for r in rows) != expected:
        raise ValueError("Assigned condition and role denominators differ")
    if any(r["availability"] not in STATUSES for r in rows):
        raise ValueError("Unknown assessment availability")
    return {c: Counter(r["availability"] for r in rows if r["condition"] == c)
            for c in CONDITIONS}


def render(rows, output):
    groups = counts(rows)
    total = Counter(r["availability"] for r in rows)
    fig, (left, right) = plt.subplots(1, 2, figsize=(9.6, 5.0),
                                     gridspec_kw={"width_ratios": [1, 3]})
    bottom = 0
    for status, color in zip(STATUSES, COLORS):
        value = total[status]
        left.bar(0, value, bottom=bottom, color=color, width=.62)
        if value:
            left.text(0, bottom + value / 2, str(value), ha="center", va="center",
                      color="white", weight="bold", fontsize=13)
        bottom += value
    left.set(ylim=(0, 32), yticks=range(0, 33, 8), xticks=[0], xticklabels=["All 32"],
             ylabel="Assigned judgments", title="Overall")
    ticks = []
    for y, (condition, label) in enumerate(zip(CONDITIONS, LABELS)):
        start = 0
        for status, color in zip(STATUSES, COLORS):
            value = groups[condition][status]
            right.barh(y, value, left=start, color=color, height=.55)
            if value:
                right.text(start + value / 2, y, str(value), ha="center", va="center",
                           color="white", weight="bold", fontsize=11)
            start += value
        valid = Counter(r["role"] for r in rows if r["condition"] == condition
                        and r["availability"] == "usable")
        ticks.append(f"{label}\nUsable: primary {valid['primary']}/6 · duplicate {valid['duplicate']}/2")
    right.set(yticks=range(4), yticklabels=ticks, xlim=(0, 8), xticks=range(0, 9, 2),
              xlabel="Assigned judgments per assistance condition", title="Availability by condition")
    right.invert_yaxis()
    for ax in (left, right):
        ax.spines[["top", "right"]].set_visible(False)
    names = ("Usable under frozen gate", "Unavailable: target metadata changed",
             "Unavailable: other cause")
    handles = [Patch(color=color, label=name) for status, color, name in
               zip(STATUSES, COLORS, names) if total[status]]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .08),
               ncol=1 if total["other-unavailable"] else 2, frameon=False, fontsize=9)
    fig.suptitle("Assessment availability is a measurement outcome", fontsize=15, x=.5)
    fig.text(.5, .025, "Metadata-related exclusions are not worker scientific failures. "
             "Original reports and the frozen admission rule remain unchanged.",
             ha="center", fontsize=9)
    fig.subplots_adjust(left=.08, right=.98, top=.83, bottom=.24, wspace=1.15)
    for suffix in ("png", "svg", "pdf"):
        fig.savefig(output / ("assessment-attrition." + suffix), dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--run-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = [json.loads(line) for line in (args.analysis / "judgments.jsonl").read_text().splitlines()]
    records = [r for r in records if r["round"] == 1]
    args.output.mkdir(parents=True, exist_ok=False)
    rows = []
    for record in records:
        identifier = record["judgment_id"]
        evidence = []
        delta = None
        root = args.run_evidence / record["run_id"] / "judgments" / identifier
        delta_path = root / "retention/target-as-found-01/manifest-to-as-found-delta.json"
        if record["response_status"] != "valid" and delta_path.is_file():
            verification = delta_path.parent / "verification.json"
            proof = json.loads(verification.read_bytes())
            if not (proof["preservation_verified"] and proof["source_before_copy_after_final_equal"]
                    and proof["original_worker_capture_manifest_unchanged"]
                    and proof["judge_result_unchanged"]):
                raise ValueError("Unverified target delta")
            delta = json.loads(delta_path.read_bytes())
            for source in (delta_path, verification):
                dest = args.output / "evidence" / identifier / source.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
                evidence.append({"path": str(dest.relative_to(args.output)), "sha256": sha(dest)})
        rows.append({"judgment_id": identifier, "condition": record["condition"],
                     "role": record["role"], "availability": classify(record, delta),
                     "evidence": evidence})
    counts(rows)
    data = {"scope": "All 32 assigned round-one judgments; original admission unchanged.",
            "judgments_source_sha256": sha(args.analysis / "judgments.jsonl"), "rows": rows}
    (args.output / "assessment-attrition.json").write_text(json.dumps(data, indent=2) + "\n")
    render(rows, args.output)


if __name__ == "__main__":
    main()
