"""Bounded routing/identity checks; no process launch or scientific execution."""
from pathlib import Path
import hashlib
import json
import shutil
import tempfile
import pytest

import dispatch_series as dispatch

ROOT = Path(__file__).resolve().parent
STATE = ROOT.parent
CHECKOUT = Path("/Users/johnlee/code/CON/stamped-in-practice")


def test_all_32_slots_remain_ordered_with_separate_paths():
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in ROOT.glob("original-*.json")}
    rows = []
    for batch in range(1, 12):
        record, state, selected = dispatch.prepare(ROOT / "series-draft-02.json", batch,
            CHECKOUT, STATE, describe=True)
        assert len(selected) <= 3
        rows.extend(selected)
    assert len(rows) == 32
    assert [r["slot"]["dispatch_order"] for r in rows] == list(range(1, 33))
    assert len({r["output"] for r in rows}) == 32
    for row in rows:
        assert Path(row["output"]).is_relative_to(STATE / "assessment-series" / record["series_id"])
        assert not Path(row["output"]).exists()
        argv = row["argv"]
        assert argv[argv.index("--role") + 1] == "judge"
        assert argv[argv.index("--branch") + 1] != "codex/" + row["slot"]["judgment"]
        assert "FINAL_REVIEWED_SEAL_REQUIRED" in argv
    assert before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in ROOT.glob("original-*.json")}


def test_draft_cannot_dispatch_or_create_output():
    with tempfile.TemporaryDirectory() as tmp:
        state = Path(tmp)
        with pytest.raises(AssertionError, match="Draft series"):
            dispatch.prepare(ROOT / "series-draft-02.json", 1, CHECKOUT, state, describe=False)
        assert list(state.iterdir()) == []


@pytest.mark.parametrize("field", ["order", "slot", "role", "capture", "stop"])
def test_changed_identity_is_rejected_before_dispatch(field):
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp)
        for filename in ["original-allocation.json", "original-procedure.json",
                         "retained-objects.json", "original-object-sources.json", "series-draft-02.json"]:
            shutil.copy2(ROOT / filename, copy / filename)
        record = json.loads((copy / "series-draft-02.json").read_bytes())
        if field in ("order", "slot", "role"):
            slot = record["judgment_dispatch_order"][0]
            if field == "order": slot["dispatch_order"] = 32
            if field == "slot": slot["judgment"] += "-replacement"
            if field == "role": slot["role"] = "duplicate"
            (copy / "series-draft-02.json").write_text(json.dumps(record))
        else:
            objects = json.loads((copy / "retained-objects.json").read_bytes())
            key = "delivery_capture_sha256" if field == "capture" else "worker_end_state_sha256"
            objects[0][key] = "0" * 64
            (copy / "retained-objects.json").write_text(json.dumps(objects))
        with pytest.raises(AssertionError):
            dispatch.prepare(copy / "series-draft-02.json", 1, CHECKOUT, STATE, describe=True)


@pytest.mark.parametrize("batch", [0, 12])
def test_outside_allocation_is_rejected(batch):
    with pytest.raises(AssertionError):
        dispatch.prepare(ROOT / "series-draft-02.json", batch, CHECKOUT, STATE, describe=True)
