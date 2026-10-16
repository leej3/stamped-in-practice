"""Dispatch registered slots in a separate assessment series, in batches of three under the authorized max10 controller.

The current record is a draft. Execution requires the separately reviewed final
seal and a finalized series record; --describe never starts a process.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_new(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def prepare(record_path, batch, checkout, state, describe=False):
    base = record_path.parent
    record = read(record_path)
    allocation_path = base / "original-allocation.json"
    original_path = base / "original-procedure.json"
    objects_path = base / "retained-objects.json"
    sources_path = base / "original-object-sources.json"
    assert sha(allocation_path) == record["original_allocation_sha256"]
    assert sha(original_path) == record["research_procedure_sha256"]
    assert sha(objects_path) == record["retained_objects_sha256"]
    assert sha(sources_path) == record["original_object_sources_sha256"]
    assert record["maximum_simultaneous_native_sessions"] == 10
    allocation = read(allocation_path)
    group = next(r for r in allocation["rounds"] if r["round"] == record["round"])
    expected = sorted(group["judgment_dispatch_order"], key=lambda r: r["dispatch_order"])
    slots = record["judgment_dispatch_order"]
    assert [{k: s[k] for k in ("run", "role", "judgment", "dispatch_order")}
            for s in slots] == expected
    assert len(slots) == 32 and len({s["attempt_id"] for s in slots}) == 32
    assert {s["run"] for s in slots if s["role"] == "duplicate"} == set(group["duplicate_judgments"])
    objects = {r["run"]: r for r in read(objects_path)}
    sources = {r["run"]: r for r in read(sources_path)}
    assert set(objects) == set(sources) == {w["run"] for w in group["launch_order"]}
    assert len(objects) == 24 and record["research_restarted"] is False
    for run, source in sources.items():
        for key in ("input_boundary", "worker_stop", "delivery_capture", "native_result"):
            assert sha(Path(source[key]["path"])) == source[key]["sha256"], (run, key)
        stop = read(Path(source["worker_stop"]["path"]))
        seed = read(Path(source["input_boundary"]["path"]))
        assert seed["run"] == run and seed["seed_commit"] == objects[run]["seed_commit"]
        assert stop["head_commit"] == objects[run]["result_commit"]
        assert source["worker_stop"]["sha256"] == objects[run]["worker_end_state_sha256"]
        assert stop["capture"]["sha256"] == source["delivery_capture"]["sha256"] == objects[run]["delivery_capture_sha256"]
    sealed = record["status"] == "sealed-approved-for-separate-assessment"
    if not describe:
        assert sealed, "Draft series: no formal dispatch is authorized"
    seal_path = base / "assessment-procedure.json"
    if sealed:
        assert sha(seal_path) == record["assessment_procedure_sha256"]
        seal = read(seal_path)
        assert seal["version"] == 4 and seal["status"] == "sealed"
        amendment = seal["assessment_amendment"]
        assert amendment["research_procedure_json"].encode() == original_path.read_bytes()
        assert amendment["allocation_json"].encode() == allocation_path.read_bytes()
        assert amendment["retained_objects"] == read(objects_path)
        source_commit = seal["coordinator_commit"]
        assert source_commit == record["coordinator_source_commit"]
        assert sha(Path(record["resource_readiness"]["path"])) == record["resource_readiness"]["sha256"]
    else:
        source_commit = "FINAL_REVIEWED_SOURCE_REQUIRED"
    selected = slots[3 * (batch - 1):3 * batch]
    assert batch > 0 and selected
    series_state = state / "assessment-series" / record["series_id"]
    commands = []
    for slot in selected:
        source = sources[slot["run"]]
        output = series_state / "judgments" / slot["judgment"]
        argv = ["pixi", "run", "--locked", "launch", "--host-config",
            str(Path.home() / ".config/stamped-in-practice/launch-neutral.json"),
            "--protocol", "neutral-v1", "--role", "judge", "--repo", str(checkout),
            "--branch", "codex/" + slot["attempt_id"], "--base", source_commit,
            "--study", str(checkout / "studies/narps"),
            "--seed-receipt", source["input_boundary"]["path"],
            "--delivery-capture", source["delivery_capture"]["path"],
            "--worker-end-state", source["worker_stop"]["path"],
            "--clone-path", str(series_state / "targets" / slot["judgment"]),
            "--evidence", str(output / "attempt-01"), "--run-mode", "formal",
            "--procedure", str(seal_path), "--procedure-sha256",
            record["assessment_procedure_sha256"] or "FINAL_REVIEWED_SEAL_REQUIRED",
            "--resource-readiness", record.get("resource_readiness", {}).get("path", "FINAL_READINESS_REQUIRED"),
            "--capture-execution"]
        commands.append({"slot": slot, "output": str(output), "argv": argv})
    return record, series_state, commands


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--batch", type=int, required=True)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--describe", action="store_true")
    args = parser.parse_args()
    record, state, commands = prepare(args.record.resolve(), args.batch,
        args.checkout.resolve(), args.state.resolve(), args.describe)
    if args.describe:
        print(json.dumps({"description_only": True, "series_id": record["series_id"],
            "record_sha256": sha(args.record), "batch": args.batch, "commands": commands}, indent=2))
        return
    for previous in range(1, args.batch):
        assert (state / f"batch-{previous:02d}/plan.json").exists(), "Prior batch not dispatched"
    out = state / f"batch-{args.batch:02d}"
    out.mkdir(parents=True, exist_ok=False)
    # No output or target may reuse the old series or a previous attempt.
    for row in commands:
        output = Path(row["output"])
        assert not output.exists()
        target = state / "targets" / row["slot"]["judgment"]
        assert not target.exists()
    write_new(out / "plan.json", {"series_id": record["series_id"], "batch": args.batch,
        "record_sha256": sha(args.record), "dispatcher_sha256": sha(Path(__file__)),
        "assessment_procedure_sha256": record["assessment_procedure_sha256"], "commands": commands})
    processes = []
    results = []
    for row in commands:
        output = Path(row["output"])
        output.mkdir(parents=True)
        stdout = (output / "launcher.stdout").open("xb")
        stderr = (output / "launcher.stderr").open("xb")
        process = subprocess.Popen(row["argv"], cwd=args.checkout, stdout=stdout, stderr=stderr)
        dispatch = dict(row, series_id=record["series_id"],
            assessment_procedure_sha256=record["assessment_procedure_sha256"],
            pid=process.pid, started_at=now(), status="launcher-dispatched")
        write_new(output / "dispatch.json", dispatch)
        processes.append((process, stdout, stderr, output, dispatch))
        print(json.dumps({"slot": row["slot"]["judgment"], "pid": process.pid}), flush=True)
    while processes:
        for process, stdout, stderr, output, dispatch in list(processes):
            code = process.poll()
            if code is not None:
                stdout.close()
                stderr.close()
                result = dict(dispatch, status="launcher-finished", returncode=code, finished_at=now())
                write_new(output / "completion.json", result)
                results.append(result)
                processes.remove((process, stdout, stderr, output, dispatch))
        if processes:
            time.sleep(2)
    # Completion unlocks the next assigned batch regardless of outcome. There
    # is no replacement, outcome-dependent retry, or substitution here.
    write_new(out / "result.json", {"series_id": record["series_id"], "batch": args.batch,
        "status": "all-assigned-launchers-finished", "results": results})


if __name__ == "__main__":
    main()
