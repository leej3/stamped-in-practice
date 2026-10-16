# Independent assessment — NARPS potential gain and vmPFC

## Scientific assessment

**Scientific adequacy: qualified. Scientific conclusion: supported within the stated scope. Reported hypothesis outcome: no positive vmPFC effect established after whole-brain correction.** This is a defensible absence-of-support conclusion, not evidence that the true response is exactly zero.

The analysis uses the 54 equal-indifference participants, checks exact participant-ID agreement, source hashes, finite values, and shared image shape/affine, and excludes no participants. Its group statistic is a one-sided one-sample t on participant contrast estimates. Since participant variance maps are absent, the unweighted model is reasonable and the report does not present the maps as t/z scores. A 5,000-draw sign-flip maximum-T test controls voxelwise whole-brain FWE at 0.05; its key assumption, symmetry of participant effects under the null, is stated. The analysis mask combines a standard brain mask with at least 90% nonzero map coverage.

The bilateral AAL3v2 `Frontal_Med_Orb` parcel is a defensible, explicitly labeled vmPFC proxy, though it is not a unique functional definition and the atlas and input MNI spaces differ slightly. In that proxy, the mean is −0.00795 supplied units (descriptive 95% t interval −0.0345 to 0.0186), with **zero** whole-brain-FWE-significant voxels and minimum adjusted p=1.0. The 23 corrected positive voxels are in small posterior-inferior foci, not the proxy; the report appropriately avoids interpreting them as vmPFC evidence. The plots make the participant spread, proxy boundary and corrected map inspectable.

The scientific conclusion is qualified by the absent participant variances, the sign-flip symmetry assumption, anatomical-proxy and template alignment choices, and the upstream model. Gain coefficients came from a mean-centered, variance-normalized regressor in a separate gain model; they are not effects per currency unit and do not establish a causal gain response. The ROI interval is descriptive, not an equivalence test. Thus the result does not establish the predicted positive vmPFC association at the stated corrected error rate, while modest, spatially heterogeneous or differently modeled effects remain possible.

Evidence: [scientific report](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/REPORT.md>), [analysis script](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/analyze.py>), [summary](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/results/summary.json>), [cluster table](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/results/fwe_clusters.tsv>), [participant QC](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/results/participant_qc.tsv>), [vmPFC figure](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/results/vmPFC_proxy_effects.png>), [whole-brain figure](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/results/wholebrain_fwe_map.png>), and [upstream methods](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/input/upstream-methods.md>).

## Delivery boundary and attribution

The supplied [worker-stop receipt](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-22/judgments/narps-neutral-r1-22-j01/attempt-01/worker-end-state.json>) records exit code 0 at 2026-10-16 06:59:04 UTC. Its seed commit is the assessed commit `8a84ddc3eec68d0b7513f9a15ce37174288b36b7`; this is the supplied starting state, not worker-authored analysis history. At stop, `REPORT.md`, `analyze.py`, `atlas_cache/` and `results/` were untracked, while `.codex/` and `.entire/` were ignored. The captured complete workspace preserves those bytes; the 54 input maps are annex-backed. Coordinator-supplied inputs and later preservation are not credited as worker actions. `.entire` activity logs were not used as scientific or grading evidence.

The manifest SHA-256 matches the stop receipt, and its capture status is complete with no declared omissions. Exact tree verification now finds one difference at `content/workspace/.git/annex/keysdb/db`; all other 1,208 declared entries match individually. A preliminary Git status/probe inspection exposed transient annex SQLite sidecars. The mismatching database mtime is 08:17:45 UTC, after the 06:59:04 UTC worker stop; my earlier Git status/probe interaction likely rewrote this annex database. I cannot attribute the exact write to one command, and I did not restore it. No evidence was repaired or restored. This assessor-side mismatch bounds version-control metadata inspection and prevents a faithful replay copy; it is not counted as a worker defect. The worker's stop inventory still establishes the untracked code/results state.

The target's `judge-target.json` lists no reference limits. No retained external pointer was followed, and the scientific inputs and outputs were read from the captured workspace. The original complete delivery was assessed beyond Git `HEAD`.

## STAMPED assessment

**MUST:** 4 met / 2 partial / 11 unmet / 0 not-checked (17). **SHOULD:** 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable (9). **MAY:** 3 met / 2 partial / 0 unmet / 0 not-checked / 0 not-applicable (5). Partial does not satisfy a MUST. No overall score is assigned.

### What to improve first

1. Track the analysis script, report and result artifacts at worker stop; this makes the actual delivered study state reviewable as a versioned object (**must/004**, **should/001**).
2. Add a portable, pinned dependency specification and a documented way to recreate it; the current report points to an external absolute interpreter (**must/003**, **must/010–017**, **should/006–008**).
3. Record the exact environment used for each result set and a repeatable validation route (**must/006**, **should/002**, **should/004**).
4. Replace the absolute interpreter path with a root-relative documented invocation and state host requirements (**must/007**, **must/009**, **must/011–012**, **must/017**).

### What is already working

- All supplied maps are annex-backed and source metadata identifies the cohort, provenance URLs and checksums ([probe result](2026-10-16-probes.json), [source manifest](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/input/sources.json>)).
- The group script separates inputs from generated results, saves numeric maps/tables and exposes QC and exclusion decisions ([analysis script](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/analyze.py>), [QC table](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/results/participant_qc.tsv>)).
- The scientific report states the corrected inference, uncertainty and upstream coefficient limits; it supplies interpretable figures ([report](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-22-j01/content/workspace/REPORT.md>)).

### Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `REPORT.md`, `analyze.py`, `input/participants.tsv` | The study files, inputs, cache, code and results sit beneath one workspace root. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `probe:large-in-annex`, `input/upstream-methods.md` | All 54 maps and metadata are included under input; their annex links resolve within the captured root. |
| must/003 | S.1 | unmet | judgement | `analyze.py`, `probe:env-spec-tracked`, `REPORT.md` | Python packages and atlas software are not declared in a delivered environment or linked software module. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `probe:tree-clean`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-22/judgments/narps-neutral-r1-22-j01/attempt-01/worker-end-state.json`, `input/sources.json` | Git-annex tracks supplied maps, but the analysis code, report, cache and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex`, `input/sources.json` | Git-annex holds the 54 large map payloads; the probe found 54 tracked pointers. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+probe:run-env-linked+judgement | `REPORT.md`, `probe:derived-have-records`, `probe:run-env-linked`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-22/judgments/narps-neutral-r1-22-j01/attempt-01/worker-end-state.json` | No exact environment is linked to the generated results; the report names only an external interpreter path. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `probe:entry-point`, `REPORT.md` | REPORT.md gives usage but no installation route; it relies on an external absolute interpreter. |
| must/008 | A.1 | met | probe:entry-point+judgement | `REPORT.md`, `analyze.py` | REPORT.md names analyze.py as the reproduction entrypoint, and that script is included. |
| must/009 | P.1 | unmet | probe:no-abs-paths+judgement | `REPORT.md`, `probe:no-abs-paths` | REPORT.md embeds an absolute host path to the Python interpreter. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analyze.py`, `probe:env-spec-tracked` | The imports used by analyze.py have no delivered dependency specification. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `REPORT.md`, `probe:platform-assumptions` | The documented command assumes an external host path; OS and other host requirements are not documented. |
| must/012 | P.2 | unmet | judgement | `REPORT.md`, `probe:env-spec-tracked` | No system-requirements or dependency list explains how to obtain the external interpreter and packages. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-22/judgments/narps-neutral-r1-22-j01/attempt-01/worker-end-state.json` | No environment specification is present in the worker delivery or Git-tracked project. |
| must/014 | P.3 | unmet | judgement | `probe:env-spec-tracked`, `REPORT.md` | No environment specification or dependency-update process is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `probe:run-env-linked`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-22/judgments/narps-neutral-r1-22-j01/attempt-01/worker-end-state.json` | The delivery contains no pinned environment specification for exact reconstruction. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `probe:env-spec-tracked`, `.git/config` | No environment specification or project publication route is recorded; the Git config has no remote. |
| must/017 | D.1 | unmet | judgement | `REPORT.md`, `probe:entry-point` | The report gives an external interpreter path but does not explain how to obtain or install that environment. |
| should/001 | T.2 | partial | judgement | `probe:large-in-annex`, `probe:tree-clean` | Git-annex versions inputs, while the study code and results are outside the worker-stop commit. |
| should/002 | A.2 | not-checked | judgement | `probe:ci-present`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-22/judgments/narps-neutral-r1-22-j01/attempt-01/worker-end-state.json` | No recurring test record is evident; the capture cannot establish whether external or manual repeat checks occurred. |
| should/003 | M.1 | partial | probe:modules-separated | `probe:modules-separated`, `REPORT.md` | Inputs and results have separate directories, but code is at root and no environment module exists. |
| should/004 | E.1 | not-checked | judgement | `REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-22/judgments/narps-neutral-r1-22-j01/attempt-01/judgment/delivery-verification.json` | Fresh-environment replay was not checked because the exact capture inventory failed verification and no worker environment is supplied. |
| should/005 | E.1 | unmet | judgement | `analyze.py`, `REPORT.md` | analyze.py runs in the named external interpreter and does not create a disposable environment. |
| should/006 | D.2 | unmet | judgement | `probe:env-spec-tracked`, `probe:run-env-linked` | There is no pinned environment specification or recurring reconstitution check. |
| should/007 | D.2 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-22/judgments/narps-neutral-r1-22-j01/attempt-01/worker-end-state.json` | No environment artifact or dependency lock is archived in the delivery. |
| should/008 | D.2 | unmet | judgement | `probe:env-spec-tracked`, `REPORT.md` | No environment update process is declared or tracked. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: delivered source data and software are public; there is no restricted component to isolate. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `probe:large-in-annex` | External source maps are independently identified in input/sources.json; all payloads are included and annex-backed under input/. |
| may/002 | M.2 | partial | judgement | `REPORT.md`, `probe:modules-separated` | REPORT.md explains file roles, but gives no complete modular map or environment boundary. |
| may/003 | M.2 | partial | judgement | `analyze.py`, `atlas_cache/README.md` | Input and result paths are distinct, but code and atlas cache are not defined as independently updateable components. |
| may/004 | M.2 | met | judgement | `analyze.py` | The included analyze.py composes the input and atlas cache into results through workspace-relative paths. |
| may/005 | M.2 | met | judgement | `REPORT.md` | REPORT.md explains the report figures, code, summaries, maps and QC files. |
### Flagged items

- **must/006:** the probe treated the study as having no derived files because it scans tracked paths; the complete worker-stop delivery includes untracked results, but no exact environment is recorded for them.
- **must/007, must/008:** the filename probe did not recognize the alternate `REPORT.md` instructions and `analyze.py`; the report documents usage but omits environment installation, while the script is a clear starting point.
- **must/009:** the probe scanned tracked text only; the untracked report includes an absolute interpreter path.
- **may/001:** the submodule probe does not capture the independently identified, public input-data route through `input/sources.json` and the annex-backed payloads.

### Not checked

- **should/002:** no recurring test record is in the assessed delivery; a worker-authored schedule or history of repeated instruction checks would settle it.
- **should/004:** no fresh-environment test was established. A valid complete copy and the actual worker environment or complete dependency declaration would allow one safe attempt.
- **Replay:** not checked. See [replay record](2026-10-16-replay-record.json). The helper was not run: exact capture materialization is unavailable after the annex database mismatch, and the named runtime/cache requirements are not in the worker stop inventory. The documented candidate command, prospective generated-output selection and comparison rule are retained there. No target command, rerun or repair occurred.

### Goals and kind

The goal is a group-stage NARPS Hypothesis 1 analysis from supplied gain-effect maps, with whole-brain-corrected inference and a concise report, figures, code and results. This comes from the retained scientific task and `REPORT.md`. The object is a **study**: its product is a scientific conclusion and supporting analysis. This assessment applies the study emphasis to inputs, result provenance, execution and retrieval. The scope and kind follow the supplied task; no separate user correction was available.

### Access and record

The intended recipient is a researcher using the worker-declared authorized route. No full-delivery route or Git remote is declared, so access to the complete worker object was not independently testable; the coordinator's local transfer does not earn worker credit. `input/sources.json` records public input URLs, but those URLs were inspected and not fetched. The [access record](2026-10-16-access-record.json) states required artifact coverage and the single-host test scope.

Checklist link: [open the 0.3.1 checklist](2026-10-16-url.txt). Machine-readable answers: [response JSON](2026-10-16-response.json). Probe receipt: [frozen probes](2026-10-16-probes.json). Delivery comparison: [verification record](delivery-verification.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1, on the captured study at commit `8a84ddc3eec68d0b7513f9a15ce37174288b36b7`, 2026-10-16, OpenAI Codex API / gpt-6-luna. Worker stop: 2026-10-16T06:59:04Z. Coordinator capture manifest SHA-256: `62844be8e123ee4970d90409a641082a3126743ee3b90d914b2b5ef26a50aaf1`. Frozen runner check passed; response validation passed (31 answers). Probe output: `2026-10-16-probes.json`.
