## Closure update

The fixed32-attempt queue and extraction watcher04 have completed, each exit0.
No formal assessment session remains active.
Exact queue/batch/watcher receipts are retained in [closure evidence](../../measurement-development/operational-series-closure-01/README.md).
Do not restart this queue or replace any attempt.
The earlier process snapshots below are historical.

All further formal launches are held for the supplied-procedure allocation exposure described in the [viability record](synthesis/viability.md).
Local full-support packaging may continue, but it does not launch agents or claim pending Hub payloads are retrievable.

# Active-series handoff

Monitor the existing queue.
Do not rerun the initial controller or start another assessment series to continue this one.
Its scripts refuse existing directories, but that guard is not a substitute for reconciling the native sessions.

The state root on the original host is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1` (`B` below).
The active series is `B/assessment-series/narps-neutral-r1-operational-v4` (`S`).
The [control snapshot](handoff-evidence-01/controller-state.json) records observed process identity, slot receipts and exact hashes; it is not a live status service.

| Component | Location or identity |
| --- | --- |
| Queue controller | `B/repaired-series-registration-01/run_series.py`; original PID 22595, tool session 64056 |
| Per-batch dispatcher | `B/repaired-series-registration-01/dispatch_series.py` |
| Approved source checkout | `/Users/johnlee/.local/share/wt-utils/worktrees/73e0/stamped-in-practice` at `4f72ef49fdbcd50c55df6e31867579a2e7e870ad` |
| Fixed series and seal | [series.json](series.json), [assessment-procedure.json](assessment-procedure.json); hashes in the snapshot |
| Queue controls | `S/queue-01/batch-NN-command.json`, `completed-batches.json`, per-batch stdout/stderr, final `result.json` |
| Batch state | `S/batch-NN/{plan,result}.json`; the plan preserves exact assigned order and argv |
| Slot state | `S/judgments/SLOT/{dispatch,completion}.json`; native receipts/logs in `attempt-01/native/` |
| Native identity | `attempt-01/native/launch.json`, `events.jsonl`, `result.json` and the referenced native/Entire session metadata; compare session IDs, not a reused PID alone |
| Targets | `S/targets/SLOT/{canonical,operational}`; leave active targets untouched |
| Extraction | `B/round-01-operational-extraction-01`; [watcher handoff](handoff-evidence-01/extraction-handoff.json) |
| Native retention/publication | `B/operational-native-publication-01/{local-capture-index,git-publication-index}.json`; closed per-slot inventories under `git-closures/` |

Before any continuation, compare the exact controller, dispatcher, series and seal hashes with the snapshot and published records.
Inspect the controller's current process argv and parent chain, batch controls, every started slot's completion/native receipts and session identity.
A missing completion file does not authorize launching that slot again.
If any corresponding native session is still running, monitor it; do not run a competing controller.
Preserve ambiguous or interrupted state and reconcile it before continuing.
Never delete or replace existing slot, batch, target or queue directories to make dispatch succeed.

The initial [controller copy](dispatch-evidence/initial-launch-01/run_series.py) starts at batch one and is historical launch evidence, not a resume command.
If the controller has ended unexpectedly, retain its stdout/stderr and establish which assigned slots actually started and stopped.
The dispatcher can advance to an entirely unstarted next batch only after prior batch results exist; a partial batch requires explicit reconciliation rather than a blind rerun.
Record any continuation command and reasoning outside the original receipts.
Keep the same 32 assignments, order, source, seal and maximum of three native sessions; no replacement or outcome-dependent retry is authorized.

Published [progress](progress.json) and [dispatch snapshots](dispatch-evidence/) are durable observations.
[Complete support receipts](publication/batch-01/README.md) identify independently retrieved payloads.
Git/Entire publication and hosted visibility are separate from full Hub retrieval; current Hub failures leave some payloads pending.
Local capture remains authoritative pending publication, with raw native and processed Entire representations retained separately.

Finish the 32 assigned attempts, preserve and publish available evidence, and extract into this series' separate output.
Report science, checklist and replay availability independently, retain every failed or invalid artifact, and compare all eight preselected duplicate pairs.
Record measurement viability before any round-two research launch.
The [round-two preparation](../../rounds/round-02/preparation-01/README.md) is explicitly unlaunched and does not remove that hold.
