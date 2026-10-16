# Independent assessment — 2026-10-16

## Verdicts

**MUST:** 8/17 met, 5 partial, 4 unmet, 0 not-checked. **SHOULD:** 1/9 met, 2 partial, 2 unmet, 3 not-checked, 1 not-applicable. **MAY:** 4/5 met, 0 partial, 0 unmet, 0 not-checked, 1 not-applicable. No overall score is calculated.

## What to fix first

1. Track the delivered analysis, report, environment file and results as part of the worker state; they were all untracked when work stopped. This makes the study state reviewable and versioned (must/004, must/013; should/001).
2. Replace the absolute shared-interpreter dependency with a documented, portable environment creation route and a complete lock tied into result provenance (must/006, must/011–012, must/015, must/017).
3. Publish an authorized retrieval route for the complete scientific object and its environment, and state artifact coverage (must/016).
4. Add a dependency update/regeneration process and test it in a clean environment (must/014; should/004, should/006, should/008).

## What the project already does well

- The complete delivery includes the inputs, executable group analysis, methods protocol, report, generated maps, tables, figures and attempt logs. The accepted run verifies all 54 input map checksums and independently cross-checks observed and sign-flip statistics against SciPy. Original evidence: canonical capture SHA-256 `9cfe9198ef0910fbf826de24e1df2123bccbf2cb1f955899613e9e1774b6b490`, `content/workspace/analysis/run_analysis.py` (file SHA-256 `c599f79d318aad3061edefc29ba1265096c2e20e5c1d9468d95fd139e3a21b92`), `content/workspace/results/attempts/accepted_run.log` (file SHA-256 `b408cc6bbdb70415ddde0e36cf9ec958bc172a3b1dee449f2eb3f7741de089db`).
- The protocol uses the participant as the independent unit, excludes unsupported voxels by common coverage, justifies a vmPFC proxy, and applies directional whole-brain max-T FWE correction. Original evidence: `content/workspace/protocol.md` (file SHA-256 `4b171cdf329b1a4b930da697bfed3fd18d27e2cb92a7d341c26b261c1f56c3e6`); `content/workspace/results/summary.json` (file SHA-256 `14c6d2b2bf5345576f4758037b840c24887aacf7c5548952ed467815c61af862`).
- The report separates lack of corrected support from evidence of no effect, explains the normalized upstream contrast scale, notes absent participant variance maps and bounds conclusions to the supplied group model. Original evidence: `content/workspace/report.md` (file SHA-256 `ffc6c016c1d28ebfa1e41b458d38c43a2cb3bb91337d083103ae7b271b964ce4`).

## Scientific assessment

Scientific adequacy: **supported**. The reported absence of positive whole-brain-corrected vmPFC support is supported by a suitable directional group analysis, with clear coverage, anatomical, uncertainty and upstream-model limits. The positive occipital findings are outside the predefined proxy and are not treated as support for the vmPFC hypothesis. The supplied effect estimates are normalized participant contrasts, not BOLD change per currency unit; the lack of participant variance maps prevents precision-weighted inference. No evidence supports an equivalence claim or absence of all vmPFC response.

Hypothesis conclusion (verbatim from the worker report, `content/workspace/report.md`, line 5):

The supplied gain-effect maps do **not support a positive vmPFC response** in the NARPS equal-indifference group under whole-brain family-wise error (FWE) control.

Scientific adequacy excerpt for the structured record: “Scientific adequacy: **supported**. The reported absence of positive whole-brain-corrected vmPFC support is supported by a suitable directional group analysis, with clear coverage, anatomical, uncertainty and upstream-model limits.”

## Delivery boundary and attribution

The canonical capture manifest SHA-256 is `9cfe9198ef0910fbf826de24e1df2123bccbf2cb1f955899613e9e1774b6b490`; the operational manifest has the same digest, and the captured HEAD is `767f76ed3d12c3a7ff9fb23989358c768b301bc5`. The worker stop receipt SHA-256 is `0f9c6d34a3f8c32825cb9098e0c99249636fbc87bb07ca603b42f0764394dff5`; it reports a complete capture, no omissions or errors, and a normally exited worker. The Git commit contains the supplied inputs; at stop, analysis and report artifacts were untracked and `.codex/` and `.entire/` were ignored. I attribute no later coordinator commit, upload, retention or access route to worker practice.

The operational-copy probes and Git commands were run with the supplied Git environment. The tracked-only probes missed meaningful untracked artifacts and are overridden where the complete workspace changes the item answer; the original probe JSON is retained. The external skill catalog under `content/external/0000` is excluded by `judge-target.json` reference limits and was not followed. The `.codex/hooks.json` and `.entire/` paths are present in the stop state and may expose assistance/worktree telemetry; this exposure is recorded without using it as grading evidence. No treatment assignment was inferred. The operational-copy integrity comparison found no unclassified path, content, mode or link changes; it identified only allowed regular-file changes to `.git/annex/keysdb/db`, `db-shm` and `db-wal`. These inspection-copy metadata differences are not worker evidence, and this classification does not establish logical database equivalence. The initial checker result that treated new sidecars as unlisted is retained in [integrity-check-initial.json](integrity-check-initial.json); the corrected classification is [integrity-check.json](integrity-check.json).

Worker access: no retrieval or publication route for this project was declared in the stopped workspace, and the assessed repository has no recorded Git remote. The researcher recipient, required coverage and host scope are in [access-record.json](access-record.json). Coordinator delivery to the assessor establishes only local availability.

Replay: **not checked**. Before any replay, the planned outputs were `results/summary.json`, `results/cluster_summary.tsv` and `results/roi_participant_effects.tsv`; summary JSON would be compared byte-for-byte and numeric tables at relative tolerance 1e-6. No replay was started because the only documented command points to an external absolute interpreter path outside the captured delivery, and there is no in-capture interpreter or documented environment creation command to establish that prerequisite without following the external path. The input-preserving scope, outputs, tolerances, 7,200-second limit and reason are retained in [fresh-rerun.json](fresh-rerun.json). This is a replay availability limitation, not a scientific failure.

## Per-item checklist

See the frozen-runner-rendered [per-item table](response-table.md) and [response JSON](response.json). Probe disagreements and duplicate-item flags are recorded in the response. The probe draft is [probes.json](probes.json).

### Flagged items

- must/002, must/006–008, must/010–012, must/015, should/003 and may/001 override tracked-only or unsupported probe results using complete-delivery evidence.
- must/005 keeps the probe verdict but questions its evidence route: the probe cites `.datalad/config`, while the original workspace uses `.git/config` and a map symlink into `.git/annex/objects`; these are confirmed directly in the captured bytes.
- should/008 repeats must/014 in the pinned checklist and is flagged `upstream-duplicate`.

### Not checked

- should/002: no regular testing cadence is evidenced; periodic run records or automation would settle it.
- should/004: a local accepted run exists, but no clean-container/host replay is recorded; a fresh-environment execution would settle it.
- should/006: the exact environment has not been repeatedly reconstructed and run; a clean reconstruction record would settle it.

### Goals and kind

The supplied task and README describe a group-analysis study testing whether potential gain has a positive effect in vmPFC for the NARPS equal-indifference group. I classify the object as a **study**; emphasis is on the fixed input boundary, executable group analysis, environment, result provenance, and retrieval of the complete stopped delivery. This is an explicit assessment assumption because no human guidance was attached.

## Checklist and provenance

Checklist URL: [checklist-url.txt](checklist-url.txt). Machine-readable STAMPED answers: [response.json](response.json). Scientific judgment record: [scientific-judgment.json](scientific-judgment.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 and `stamped-conventions` 0.1.0 against checklist 0.3.1, using the frozen assessment runner and Codex GPT-6 (exact serving revision unavailable), 2026-10-16. Original delivery identity: canonical manifest SHA-256 `9cfe9198ef0910fbf826de24e1df2123bccbf2cb1f955899613e9e1774b6b490`, original HEAD `767f76ed3d12c3a7ff9fb23989358c768b301bc5`. Probe output: [probes.json](probes.json).
