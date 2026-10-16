# Independent assessment

Capture identity: canonical original manifest SHA-256 `0353862d1b7ed1c084dd47c8198aafe204a3c51fe110182be971d309a595b6f0`; captured HEAD `c341bb810566ffec5a12747e921f38c28c618b4a`; captured 2026-10-16T15:30:25.102818+00:00. All cited project paths below are relative to the captured workspace and refer to those original bytes. The operational copy initially matched the canonical capture. No substantive integrity mismatch was observed during inspection; inspection-induced annex database metadata is excluded from worker evidence.

## Scientific assessment

Scientific adequacy: **supported**. The report supports its narrow conclusion that this analysis found no corrected positive vmPFC evidence, while explicitly avoiding a claim that the true effect is zero. It uses all 54 equal-indifference participant maps and reports quality checks, a positive one-sample group model, one-sided whole-brain max-t sign-flip inference, and an a priori MNI vmPFC search box. The report states no positive FWE-significant vmPFC voxels; the supplied summary records 0/2,400 ROI voxels and a descriptive ROI mean of −0.0027 (95% interval −0.0226 to 0.0171). The 24 corrected voxels are posterior and outside the vmPFC region. This is a defensible absence-of-corrected-support conclusion, not evidence of a null effect. The worker report discusses equal weighting without participant variance maps, sign-flip exchangeability/symmetry, mask dependence, upstream modeling limits, and small posterior clusters. [Capture `0353862d1b7ed1c084dd47c8198aafe204a3c51fe110182be971d309a595b6f0`: `report.md`, `results/summary.json`, `analyze.py`, `input/upstream-methods.md`].

One numerical description is inaccurate: `report.md` says the smallest attainable Monte Carlo p-value is 1/1001 although `analyze.py` uses 5,000 draws and the plus-one denominator is 5,001. The reported observed minimum p≈0.001 is compatible with its observed exceedance count, so this precision sentence does not change the vmPFC conclusion. Scientific interpretation remains conditional on fixed upstream maps and an equally weighted group model; the supplied maps are normalized contrast estimates, not effects per currency unit. The anatomy box is a reasonable, transparent operational vmPFC definition, though broad and not an atlas-derived boundary.

Hypothesis outcome (verbatim from worker report): “the supplied gain-effect estimates do not support a positive vmPFC response under whole-brain family-wise error (FWE) control.” This is the reported outcome; it is recorded separately from the adequacy category.

## STAMPED assessment

- MUST: 3 met / 13 unmet / 1 not-checked / 0 not-applicable.
- SHOULD: 0 met / 6 unmet / 2 partial / 0 not-checked / 1 not-applicable.
- MAY: 0 met / 0 unmet / 2 partial / 0 not-checked / 3 not-applicable.

The frozen probes are retained in [probes/probes.json](probes/probes.json). The full item response and evidence are in [response.json](response.json), and the checklist app link is in [checklist-url.txt](checklist-url.txt). Probe output was treated as a draft: items 008 and 009 were judged from the complete delivery rather than the tracked-path heuristic; the report offers a documented script and the complete stop includes untracked worker outputs. The absolute interpreter path in that same report makes must/009 unmet. Probe disagreements are described in the response record.

### Key findings

- The report, analysis, figures and result maps are present in the complete stopped workspace, but worker deliverables were untracked at stop. The operational Git observation showed `?? analyze.py`, `?? figures/`, `?? report.md`, and `?? results/`; worker stop receipt establishes the captured stop. Coordinator-supplied committed inputs do not earn worker version-control credit. [Capture `0353862d1b7ed1c084dd47c8198aafe204a3c51fe110182be971d309a595b6f0`: `analyze.py`, `report.md`, `results/summary.json`; operational observation: `git status --short`].
- The report provides a starting script and generated-output description, but only via a host-specific absolute interpreter path. No dependency manifest, install instructions, environment identity, update process, or worker publication route is included. [Capture `0353862d1b7ed1c084dd47c8198aafe204a3c51fe110182be971d309a595b6f0`: `report.md`, `analyze.py`, `input/sources.json`].
- The worker stop receipt at `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-17-j01/attempt-01/worker-end-state.json` (SHA-256 `567c1c01a325936390749bda85756984267896531ff91367f282c91d38e32ebb`) records an exited process with return code 0. The scientific report/results are worker artifacts in the captured stop; the earlier Git commit covers coordinator-supplied material. Captured commit metadata includes a Codex Desktop co-author identifier; this exposure is recorded but was not used as grading evidence.

### Access and replay

No worker-declared retrieval or publication route was found. The intended recipient is a researcher using an authorized route; none was declared, so no host scope or artifact coverage could be tested. The coordinator’s preservation copy is not worker access evidence. See [access-record.json](access-record.json).

Replay was not checked. The report's command is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analyze.py`; that interpreter is outside the delivery, and no environment declaration is supplied. The constraint against following external paths or supplying an inferred replacement environment therefore prevents a safe replay. The documented outputs and comparison rule are retained in [replay/replay-record.json](replay/replay-record.json). No replay was attempted and no shipped output is counted as replay evidence.

### Integrity and scope

Canonical and operational manifest digests were both `0353862d1b7ed1c084dd47c8198aafe204a3c51fe110182be971d309a595b6f0`; `judge-target.json` has no reference limits. Git/probe inspection was directed only to the operational copy, with `GIT_OPTIONAL_LOCKS=0`, `annex.merge-annex-branches=false`, and `annex.alwayscommit=false` inherited. Annex pointer files were treated as captured bytes; no original absolute/external pointer was followed and no Git hook at the configured external hooks path was run. Any operational `keysdb/db`, `db-shm`, or `db-wal` change is operational metadata only and does not establish logical DB equivalence. The launcher’s post-assessment integrity verification remains authoritative.
### What to fix first

1. Commit the analysis, report, figures and results at the worker stop; this makes the delivered scientific state trackable (must/004, should/001).
2. Add a portable, pinned dependency specification and a process for updating and testing it; this lets another researcher reconstruct the analysis environment (must/003, must/006, must/010, must/013–016; should/006–008).
3. Replace the host-specific interpreter path with portable installation and usage instructions, and state system requirements (must/007, must/009, must/011–012, must/017).
4. Publish a worker-declared authorized retrieval route covering all source maps, metadata, code, results, figures and the environment (must/016–017; access record).

### Flagged items

- must/008: the probe only recognized README/Makefile and tracked entrypoints; the complete report names `analyze.py` and its outputs, so the full-delivery reading is met.
- must/009: the probe scanned tracked text only; the untracked `report.md` in the complete stop contains a host-specific absolute interpreter path, so the item is unmet.
- must/011: the command scan did not find platform syntax, but the documented route assumes an interpreter at an external host path without setup instructions.
- should/002: no recognized CI was found; full-delivery inspection found no repeat-testing record either, so the item is unmet.
- should/008 repeats must/014 by design.

### Not checked and scope

Must/005 remains not-checked for worker attribution: annex content is present for coordinator-supplied maps, but stop evidence does not establish worker use of annex for large data. A worker-authored annex action would settle attribution. Replay is not checked because the external interpreter and undeclared dependencies cannot be reconstructed within scope. Access was not tested because there is no worker-declared route; a declared authorized route and its covered artifacts/hosts would settle it.

The documented goal is the group-level NARPS Hypothesis 1 test on the equal-indifference cohort; this object is a study analysis. Evidence is conditional on the supplied AO86 participant effect maps and fixed upstream model. No overall score is assigned.

Checklist 0.3.1 URL: [open the checklist](checklist-url.txt). Full record: [response.json](response.json). Assessment uses the frozen external assessor version in `assessment-version.json`; runner check output is retained under `commands/`. The inspected commit is `c341bb810566ffec5a12747e921f38c28c618b4a`, while the canonical capture is separately identified by SHA-256 above.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/participants.tsv`, `analyze.py` | Inputs, code, report, results and figures are nested under the workspace root. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `input/participants.tsv` | The supplied maps and metadata resolve within the captured workspace through the annex content store. |
| must/003 | S.1 | unmet | judgement | `analyze.py`, `report.md` | The Python scientific dependencies are external and no delivered environment declaration includes them. |
| must/004 | T.1,T.3,T.5 | unmet | judgement | `operational observation: git status --short`, `analyze.py`, `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-17-j01/attempt-01/worker-end-state.json` | The worker analysis, report, figures and results were untracked at stop; only supplied inputs were committed. |
| must/005 | T.1,T.3,T.5 | not-checked | judgement | `input/sources.json`, `worker stop receipt` | Annex stores the coordinator-supplied participant maps; worker use of annex for large data is not attributable from stop evidence. |
| must/006 | T.1,T.3,T.5 | unmet | judgement | `results/summary.json`, `results/run.log` | The run log and summary record parameters and package versions but do not link results to an exact captured environment. |
| must/007 | A.1 | unmet | judgement | `report.md`, `analyze.py` | The report gives a run command but no installation steps or dependency setup a recipient can follow. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `analyze.py` | The report names analyze.py as the reproduction entrypoint and lists generated outputs. |
| must/009 | P.1 | unmet | probe:no-abs-paths+judgement | `report.md` | The documented command hardcodes a host-specific absolute interpreter path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `analyze.py` | Required Python packages are not declared in a delivered environment specification. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `report.md` | The report assumes an external interpreter at a host-specific path without documenting host setup. |
| must/012 | P.2 | unmet | judgement | `report.md`, `analyze.py` | No list of system requirements or software dependencies accompanies the usage instructions. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked` | No environment specification is included in version control or the delivery. |
| must/014 | P.3 | unmet | probe:env-spec-tracked | `analyze.py`, `report.md` | No environment specification or update process is declared. |
| must/015 | D.1 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked` | No pinned environment specification is supplied for exact reconstitution. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked` | No environment artifact or specification is shared from the worker stop state. |
| must/017 | D.1 | unmet | judgement | `report.md` | A reader is not told how to obtain or install the external environment used by the command. |
| should/001 | T.2 | partial | judgement | `operational observation: git status --short`, `input/participants.tsv` | Git tracks supplied inputs, while worker code, report, figures and results were untracked. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `probe:ci-present`, `results/run.log` | No CI or repeated-testing record is present in the complete delivery. |
| should/003 | M.1 | partial | probe:modules-separated | `input/participants.tsv`, `analyze.py` | Inputs, results and figures have directories, but code and environment are not separated as maintained modules. |
| should/004 | E.1 | unmet | judgement | `results/run.log`, `probe:ci-present` | No record shows the workflow tested in a fresh container, job or clean environment. |
| should/005 | E.1 | unmet | judgement | `analyze.py` | The workflow does not create a disposable environment for each execution. |
| should/006 | D.2 | unmet | judgement | `probe:env-spec-tracked`, `probe:ci-present` | No environment specification or reconstitution test record exists. |
| should/007 | D.2 | unmet | judgement | `probe:env-spec-tracked` | No environment artifacts are archived in the delivered object. |
| should/008 | D.2 | unmet | probe:env-spec-tracked+judgement | `report.md`, `analyze.py` | No environment update process is declared. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: no restricted data or software component is identified; supplied sources are public research inputs. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable | `probe:subdatasets-resolvable` | N/A: there are no independently maintained project components; runtime packages are not project modules. |
| may/002 | M.2 | partial | judgement | `report.md`, `analyze.py` | The report and directories distinguish inputs and outputs, but do not document their module relationships. |
| may/003 | M.2 | not-applicable | judgement | `probe:modules-separated` | N/A: no separately maintained modules exist to update independently. |
| may/004 | M.2 | not-applicable | judgement | `probe:subdatasets-resolvable` | N/A: there are no distinct components to compose. |
| may/005 | M.2 | partial | judgement | `report.md`, `input/study-task.md` | The report provides a starting point and explains outputs, but offers little navigation guidance for the project layout. |
