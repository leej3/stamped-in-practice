# Independent assessment — NARPS equal-indifference gain effect

## Verdict

MUST: 4 met / 4 partial / 9 unmet / 0 not-checked (17 items; partial does not satisfy a MUST).

SHOULD: 1 met / 2 partial / 4 unmet / 1 not-checked / 1 not-applicable (9 items).

MAY: 2 met / 2 partial / 0 unmet / 0 not-checked / 1 not-applicable (5 items).

## Scientific assessment

**Scientific adequacy: supported, with stated limits.** The worker tested the intended 54 equal-indifference participants using their participant-level gain-effect maps, verified exact participant IDs against metadata, checked geometry and finite values, and excluded no participant. Voxelwise one-sample positive t statistics were tested using 9,999 participant-level sign flips and a whole-brain maximum-t correction. The descriptive vmPFC box was not used to constrain or select the whole-brain inference.

**Reported hypothesis outcome: not supported at the whole-brain-corrected criterion.** No voxel in the coordinate-defined vmPFC box survived whole-brain correction. Its descriptive mean was −0.00347 (95% CI −0.02293 to 0.01599 upstream units). The analysis found 24 corrected positive voxels in three posterior islands; the strongest was at MNI (−26, −102, −3.6) mm, outside vmPFC. The broad interval and absence of corrected vmPFC voxels do not establish a zero effect or rule out smaller effects or another defensible anatomical boundary.

The protocol correctly states that these are participant contrast coefficients for a mean-centered, variance-normalized gain regressor, not currency-unit slopes or standardized statistics. The group analysis is unweighted because participant variance maps were not supplied; sign-flip inference assumes symmetry under the null. The supplied upstream methods describe separate gain and loss models. These qualifications bound the conclusion but do not undermine the reported absence of whole-brain-corrected vmPFC evidence. See [the scientific report](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-05-j02/content/workspace/REPORT.md), [protocol](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-05-j02/content/workspace/protocol.md), [group analysis](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-05-j02/content/workspace/scripts/group_analysis.py), [summary](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-05-j02/content/workspace/results/summary.json), [cluster table](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-05-j02/content/workspace/results/fwe_clusters.csv), and [figure](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-r1-05-j02/content/workspace/figures/group_results.png).

## Replay and measurement availability

The stopped delivery matched its complete capture manifest and worker-stop receipt: capture status complete, with no manifest errors or omissions. The frozen runner's pinned version check passed before probes or replay. One replay used a fresh copy of the complete delivery and the documented command `bash run_analysis.sh`, with the script's supplied Python interpreter. The 7,200-second and 5 GB limits were not reached; the command exited 0 in 21.1 seconds.

The summary, NIfTI maps, tables, PNG, retrieval manifest, and run logs reproduced byte-for-byte. The SVG differed only in its embedded generation timestamp and generated internal SVG IDs/references; the PNG and numeric artifacts were identical. The frozen helper therefore records **partial** bytewise replay, while the scientifically relevant generated quantities reproduced exactly. Replay records, outputs, command and child stdout/stderr are retained in [the replay directory](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/replay/). The worker's retained first failed run records a postprocessing indexing error; its corrected full run is what the supplied outputs and successful replay cover. This is target history, not an assessor malfunction.

## Access and attribution

The intended recipient is a researcher using the worker-declared authorized route. The route in `input/sources.json` covers 54 map files (96,387,264 bytes total); metadata and methods files are local. A HEAD and 1 KB range request to one NeuroVault map URL succeeded (200 and 206 respectively). All 54 map URLs use `neurovault.org`; all 54 retrieved payloads are represented in the worker's checksum manifest, but only one remote URL was contacted for this access check. No worker-declared publication route for the analysis outputs or environment was found. Coordinator delivery of this object is not evidence that the worker had published those outputs. See [access record](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/access-record.json).

At worker stop (2026-10-16 07:14:46 UTC), the receipt records exit code 0 and commit `afb62884c70115b6e46a92ddcd1d17bbf4f33544`. Git/git-annex tracked the starter materials and 54 map pointers, but `REPORT.md`, `protocol.md`, `scripts/`, `results/`, `figures/`, `run_analysis.sh`, and retrieved `data/` were untracked. This materially limits version-control completeness and reproducibility of the exact delivered state. Coordinator capture, retention and assessment artifacts receive no worker-practice credit. No retained links outside the allowed reference boundary were followed. See the [worker-stop receipt](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/worker-end-state.json) and [manifest verification](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/manifest-verification.json).

## What to address first

- Track the report, scripts, outputs, figures, and downloaded data in the worker's version-control state so the record identifies the complete delivered analysis (must/004).
- Supply and track a pinned environment specification, document its installation and host requirements, and link the recorded run to it (must/003, 006, 010–017).
- Replace the hard-coded host Python default with a documented relative or portable environment invocation (must/009).
- Keep the successful corrected workflow run and its QC/results provenance; add recurring workflow checks if regular testing is intended (should/002, 006).

## What the project does well

- The protocol states a transparent participant-level estimand, explicit common-support mask, directional test, whole-brain maximum-t correction, and permutation assumptions ([protocol](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-05-j02/content/workspace/protocol.md)).
- The worker retained input identities and checksums, per-participant QC, independent numerical checks, corrected maps, clusters, and an informative figure ([summary](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-05-j02/content/workspace/results/summary.json), [QC table](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-05-j02/content/workspace/results/participant_qc.csv)).

## Item table

Canonical [response JSON](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/2026-10-16-response.json); unedited [probe record](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/2026-10-16-probes.json).

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | probe:judgement | `protocol.md`, `input/` | All delivered files and directories are rooted in the workspace. |
| must/002 | S.1 | met | probe:judgement | `input/sources.json`, `input/data/`, `results/retrieval-manifest.txt` | The analysis inputs resolve within the delivery through local files and annex content. |
| must/003 | S.1 | unmet | probe:judgement | `run_analysis.sh`, `scripts/group_analysis.py` | The workflow relies on externally installed Python packages; no delivered environment or software module supplies them. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/worker-end-state.json` | Git tracks part of the project, but the report, scripts, results, figures and retrieved data remained untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data/`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/manifest-verification.json` | git-annex stores the 54 large map payloads behind tracked pointers. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `results/summary.json`, `run_analysis.sh`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json` | Run records list package versions but do not include or identify an exact environment specification. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `REPORT.md`, `run_analysis.sh`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json` | REPORT.md explains usage and names the command, but provides no install instructions for the external common Python environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `REPORT.md`, `run_analysis.sh`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/replay/replay.json` | The documented reproduction starting point is bash run_analysis.sh. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `run_analysis.sh`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json` | The run script defaults PYTHON to a host-specific absolute path, although callers can override it. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `run_analysis.sh`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json` | No tracked environment specification declares the Python dependencies. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `REPORT.md`, `results/summary.json` | The report names the provided common environment and summary records the observed platform, but the required host assumptions are not specified sufficiently to reconstruct it. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `REPORT.md`, `run_analysis.sh` | No clear installable system and dependency requirements list is supplied. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/worker-end-state.json` | No environment specification is present in the worker delivery. |
| must/014 | P.3 | unmet | probe:env-spec-tracked | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/worker-end-state.json` | No dependency-update process is declared or tracked. |
| must/015 | D.1 | unmet | probe:env-spec-tracked | `results/summary.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json` | Package versions are recorded, but no frozen manifest or container digest identifies the exact runtime. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json` | There is no environment specification to share. |
| must/017 | D.1 | unmet | probe:judgement | `REPORT.md`, `run_analysis.sh` | The report refers to a pre-provided common environment without instructions to obtain or reconstruct its specification. |
| should/001 | T.2 | partial | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json`, `input/data/` | Git/git-annex covers tracked inputs, but untracked scripts, outputs, and retrieved data were outside version control at worker stop. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `results/attempts/README.md`, `results/run.stdout` | The stopped delivery documents a failed attempt and a corrected rerun, but not a recurring test schedule or repeated independent workflow checks. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/`, `scripts/`, `results/`, `figures/` | Inputs, scripts, and outputs occupy separate directories; environment definitions are absent. |
| should/004 | E.1 | unmet | probe:judgement | `run_analysis.sh`, `results/summary.json` | Worker records show execution in a shared preconfigured environment, not a clean container, VM, batch job, or cloud instance. |
| should/005 | E.1 | unmet | probe:judgement | `run_analysis.sh` | The workflow does not create a disposable environment for each run. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json`, `results/summary.json` | There is no exact environment specification or record of regular reconstitution tests. |
| should/007 | D.2 | unmet | probe:judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json` | No environment artifact is archived in the delivered object. |
| should/008 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/probes.json` | No dependency-update process or tracked updates are present. |
| should/009 | M.4 | not-applicable | probe:judgement | `input/sources.json` | N/A: delivered inputs and software are public; there is no restricted component to isolate. |
| may/001 | M.2 | not-applicable | probe:judgement | `input/sources.json`, `input/data/` | N/A: the project contains no independently maintained external project module; input maps are locally included through git-annex. |
| may/002 | M.2 | partial | probe:judgement | `REPORT.md`, `protocol.md` | The report and protocol identify inputs, scripts, results, and figures, but do not fully explain modular relations. |
| may/003 | M.2 | partial | probe:judgement | `protocol.md`, `run_analysis.sh` | Directories give some separation, but environment boundaries and independently updateable module interfaces are not defined. |
| may/004 | M.2 | met | probe:judgement | `run_analysis.sh` | run_analysis.sh composes retrieval and group analysis as the workflow entrypoint. |
| may/005 | M.2 | met | probe:judgement | `REPORT.md` | REPORT.md links the report, protocol, code, data manifest, outputs, and figures for navigation. |
## Flagged items

- **must/004:** tree-clean found untracked scientific deliverables; the partial verdict reflects Git use for starter/input materials alongside untracked final analysis.
- **must/006 and should/006:** the run summary records package versions, but no exact environment specification links the results to a reconstructable runtime.
- **must/007 and must/008:** the probe's filename heuristic missed `REPORT.md` and `run_analysis.sh`; the documented entrypoint exists, but installation instructions for its external environment are incomplete.
- **must/009:** the probe scanned tracked text and missed the untracked run script's absolute Python path.
- **must/011 and must/012:** text scanning could not assess the declared common environment; reading shows incomplete host and dependency requirements.
- **should/002:** no CI configuration was found; the assessment leaves regular testing not-checked because the probe does not settle manual or scheduled recurring checks. The delivery records one failed attempt and one corrected full run.
- **should/003:** the full delivery separates inputs, scripts and derived outputs; the probe inventory was limited to tracked paths and missed the latter directories.
- **should/008:** repeats the dependency-update requirement in must/014, flagged as an upstream duplicate.

## Not checked and not applicable

- **should/002 (not-checked):** recurring manual or scheduled testing records would settle whether the workflow is tested regularly.
- **should/009 (not-applicable):** there is no restricted data or software component.
- **may/001 (not-applicable):** the object contains no independently maintained external project module; the participant maps are included through git-annex.

## Goals and kind

The stated goal is group-stage inference for the positive gain effect in vmPFC in the 54-person equal-indifference NARPS group, with concise reporting and reproducible code/results. That goal appears in the supplied `input/study-task.md` and the worker's `protocol.md`/`REPORT.md`. This is a **study** object; the assessment emphasizes scientific inference, fixed-input integrity, tracked code/results, portable execution, and result-to-environment provenance.

## Checklist and stamp

Checklist URL: [open the 0.3.1 checklist response](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-05/judgments/narps-neutral-r1-05-j02/attempt-01/judgment/2026-10-16-url.txt).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the worker-stopped delivery at commit `afb62884c70115b6e46a92ddcd1d17bbf4f33544`, captured 2026-10-16, Codex/GPT-6. Delivery capture SHA-256: `62fae7a1b4cf57bb811b88cb718ed01596b5d9b784e996e678b4851cadefbd0d`. Probe output: `2026-10-16-probes.json`.
