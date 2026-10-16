"""Check interval interpretation, source agreement and deterministic rendering."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import render_poster_progression as render

DATA = ROOT / "experiments/retained-round-reporting/pooled"
FIGURES = ROOT / "experiments/narps-poster/figures"


def inputs():
    return (json.loads((DATA / "poster-outcomes.json").read_text()),
            json.loads((DATA / "run-outcomes.json").read_text()))


@pytest.mark.parametrize("k,n,expected", [
    (0, 6, (0, 39.033429)),
    (6, 6, (60.966571, 100)),
    (3, 6, (18.761631, 81.238369)),
    (2, 5, (11.762077, 76.927572)),
])
def test_wilson_reference_intervals(k, n, expected):
    assert render.wilson_percent(k, n) == pytest.approx(expected, abs=1e-6)


def test_retained_source_counts_and_missingness():
    summary, runs = inputs()
    points = render.points_from_summary(summary)
    dots = render.attach_run_statistics(points, runs)
    assert len(points) == 12 and len(dots) == 68
    assert sum(p["scientific_n"] for p in points) == 70
    missing = {r["run_id"] for r in runs} - {r["run_id"] for r in dots}
    assert missing == {"narps-neutral-r1-16", "narps-neutral-r1-23", "narps-neutral-r2-05", "narps-neutral-r3-20"}
    for p in points:
        assert p["scientific_interval_lower_percent"] <= p["scientific_supported_percent"] <= p["scientific_interval_upper_percent"]
        assert p["checklist_sd_upper_percent"] - p["checklist_sd_lower_percent"] == pytest.approx(2 * p["checklist_sd_met_percent"])


def test_mean_and_sd_weight_runs_equally():
    summary, runs = inputs()
    selected = [r for r in runs if r["round"] == 1 and r["condition"] == "baseline"]
    for i, row in enumerate(selected):
        if i < 3:
            met, evaluated = ((1, 10), (4, 20), (9, 30))[i]
            row.update(checklist_valid=True, checklist_met_fraction=met / evaluated,
                       checklist_evaluated_items=evaluated,
                       checklist_status_counts={"met": met, "unmet": evaluated - met, "not-checked": 31 - evaluated})
        else:
            row.update(checklist_valid=False, checklist_met_fraction=None)
    target = next(p for p in summary["round_conditions"] if p["round"] == 1 and p["condition"] == "baseline")
    target.update(checklist_n=3, checklist_unavailable=3, checklist_mean_met_percent=20., checklist_sd_met_percent=10.)
    points = render.points_from_summary(summary)
    render.attach_run_statistics(points, runs)
    p = next(p for p in points if p["round"] == 1 and p["condition"] == "baseline")
    assert p["checklist_sd_lower_percent"] == pytest.approx(10)
    assert p["checklist_sd_upper_percent"] == pytest.approx(30)


def test_conflicting_run_identity_or_summary_is_rejected():
    summary, runs = inputs()
    duplicate = copy.deepcopy(runs)
    duplicate[1]["run_id"] = duplicate[0]["run_id"]
    with pytest.raises(ValueError, match="distinct"):
        render.attach_run_statistics(render.points_from_summary(summary), duplicate)
    summary["round_conditions"][0]["checklist_mean_met_percent"] += 1
    with pytest.raises(ValueError, match="mean or sample SD"):
        render.attach_run_statistics(render.points_from_summary(summary), runs)


def test_progression_replay_and_input_bindings(tmp_path):
    subprocess.run([sys.executable, str(ROOT / "scripts/render_poster_progression.py"), "--output", str(tmp_path)], check=True)
    for name in ("round-progression.svg", "round-progression.png", "round-progression-manifest.json"):
        assert (tmp_path / name).read_bytes() == (FIGURES / name).read_bytes()
    manifest = json.loads((tmp_path / "round-progression-manifest.json").read_text())
    for key in ("input", "run_input"):
        source = manifest[key]
        assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
    assert b'<text' in (tmp_path / "round-progression.svg").read_bytes()
