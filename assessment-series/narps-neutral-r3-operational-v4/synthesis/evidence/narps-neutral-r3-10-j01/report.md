# Independent assessment: NARPS potential gains and vmPFC response

## STAMPED verdicts

MUST: 5 met / 1 partial / 11 unmet / 0 not-checked (17 total).  
SHOULD: 0 met / 1 partial / 4 unmet / 3 not-checked / 1 not-applicable (9 total).  
MAY: 1 met / 1 partial / 0 unmet / 1 not-checked / 2 not-applicable (5 total).

### What to address first

- Track the report, analysis code, notebook and generated results in Git at the worker stop; this would make the scientific delivery versioned as one state (must/004, should/001).
- Include a complete pinned environment and dependency declaration with the code, and link result generation to it; this addresses portability and provenance (must/003, must/006, must/010–015, should/006–008).
- Add portable installation and use instructions, including how a recipient obtains the environment (must/007, must/011–012, must/017).
- Publish a worker-controlled retrieval route covering the report, code, maps, metadata, outputs and environment (must/016).

### What is already strong

- The analysis applies whole-brain corrected inference and does not treat significant posterior results as vmPFC confirmation; the report also explains uncertainty and limits (canonical capture 19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md).
- All 54 supplied maps are retained through annex links and identified in the source manifest (canonical capture 19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/input/sources.json).
- The complete stop-state delivery includes code, report, notebook, quality tables, result maps and figures, not only the captured Git commit (canonical capture 19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/scripts/analyze.py and content/workspace/results/summary.json).

### Per-item checklist

The response records evidence for each verdict. File citations point into the complete canonical capture, including untracked worker files.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/input/study-task.md`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | The complete delivery has one common workspace root containing inputs, code, report and generated results. |
| must/002 | S.1 | met | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/input/sources.json` | All 54 map links resolve to annex objects retained beneath the same workspace root; metadata and source checksums identify the inputs. |
| must/003 | S.1 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/scripts/analyze.py` | The delivered script depends on externally installed Python packages and an absolute host interpreter; no environment package specification or linked software module is included. |
| must/004 | T.1,T.3,T.5 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/.git/index`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/scripts/analyze.py` | At worker stop the report, code, notebook and results were outside the Git index and untracked; the captured commit does not version the complete work. |
| must/005 | T.1,T.3,T.5 | met | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/.git/annex/objects` | The supplied large participant maps are represented by 54 git-annex links with retained annex content. This is inherited input organization, not a newly established worker action. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/results/summary.json`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | The complete delivery has outputs and a software-version summary, but no exact environment specification linked to the run that produced those outputs. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | report.md gives a run command but no installation instructions; the probe missed this equivalent documentation because it was not tracked. |
| must/008 | A.1 | met | probe:entry-point+judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/scripts/analyze.py` | The report names scripts/analyze.py as the analysis entrypoint and gives a runnable command; the script implements the group workflow. |
| must/009 | P.1 | met | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/scripts/analyze.py` | The analysis script constructs input and output paths relative to its own location rather than embedding data paths. |
| must/010 | P.1 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/scripts/analyze.py`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | No environment specification declares all Python dependencies; imports rely on a preinstalled external environment. |
| must/011 | P.1 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | Host assumptions are not documented as a supported system specification; an absolute interpreter path is the only host-specific instruction. |
| must/012 | P.2 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | No README or environment file lists system requirements and complete software dependencies. |
| must/013 | P.3 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/scripts/analyze.py`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | No environment file is present in the workspace or version-controlled alongside the code. |
| must/014 | P.3 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | No environment specification or tracked dependency-update process is documented. |
| must/015 | D.1 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/results/summary.json` | No complete frozen package manifest, container digest or equivalent environment pin is supplied. |
| must/016 | D.1 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | There is no worker-declared shareable environment specification. |
| must/017 | D.1 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | The report provides a host-specific interpreter path but does not explain how a recipient can obtain or recreate the environment. |
| should/001 | T.2 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/.git/index`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/scripts/analyze.py` | Git/annex covers supplied inputs, but the worker’s code, report, notebook and generated results were untracked at stop. |
| should/002 | A.2 | not-checked | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | No worker-stop test schedule or repeated-run record was found. The complete delivery and lack of recognized CI are evidence of measurement limits, not proof that the workflow was never tested regularly. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/input/participants.tsv`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/scripts/analyze.py`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/results/summary.json`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | Inputs, code, analysis notebook and results occupy separate directories, but the environment is not specified and the module boundaries are not fully documented. |
| should/004 | E.1 | not-checked | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | No worker evidence establishes testing in a fresh container, batch job, clean VM or cloud instance; the assessor replay is not worker practice evidence. |
| should/005 | E.1 | not-checked | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | No worker documentation establishes disposable isolated environments for execution. |
| should/006 | D.2 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/results/summary.json`, `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | No exact environment specification exists to reconstitute or regularly test. |
| should/007 | D.2 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | No environment artifact is archived in the delivery. |
| should/008 | D.2 | unmet | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | No dependency specification or tracked update process exists. |
| should/009 | M.4 | not-applicable | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/input/sources.json` | No restricted data or software is identified in this research object; cohort maps and source references are supplied as the analysis inputs. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/input/sources.json` | There are no independently maintained project components to include as submodules; the input dataset itself is included via annex links. |
| may/002 | M.2 | partial | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | The report identifies input, analysis, script and result artifacts, but does not document a composable module architecture. |
| may/003 | M.2 | not-checked | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | The directory layout suggests separable inputs/code/results, but no documented independent-update contract supports a stronger judgment. |
| may/004 | M.2 | not-applicable | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | The object is a single group-analysis workflow with bundled inputs rather than multiple components requiring composition. |
| may/005 | M.2 | met | judgement | `capture:19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a:content/workspace/report.md` | The report includes a reproducibility-file list and identifies the principal script, notebook, inputs and outputs, which helps a reader navigate the object. |

### Flagged items

- must/006: The probe left provenance unchecked because it recognized no run record; inspection of the complete delivery found only partial software versions and no exact environment link, so the item is unmet.
- must/007: The filename probe missed report.md because it was untracked. The report does give a run command, but no installation route; the item is partial.
- must/008: The entrypoint probe only considered tracked files. The complete delivery has a runnable script named in the report, so the item is met.
- should/003: The probe described only tracked input paths. The complete delivery also separates code and results, but lacks an environment module; partial remains appropriate.
- may/001: The probe could not determine component boundaries from submodules. Inspection found no independently maintained project components; not-applicable.
- must/014 and should/008: The pinned checklist repeats the environment-update-process question; the same unmet finding applies to both.

### Not checked

- should/002: No worker-stop record establishes regular workflow testing. A test schedule or repeated run records would settle it.
- should/004: No worker evidence establishes a fresh-container or clean-host run. A worker-produced run record from such an environment would settle it.
- should/005: No worker record shows disposable environments per run. Execution configuration/history would settle it.
- may/003: No component update contract establishes independent module boundaries. A documented interface and independent update procedure would settle it.

### Goals and kind

Assumption, not human-confirmed: the goal is the coordinator-supplied scientific task of testing whether gain effects in the 54-person equal-indifference group support a positive vmPFC response using group analysis. The primary kind is a study: the product is a scientific answer with its code, inputs and results. Emphasis therefore falls on traceable results, portable execution and complete inputs.

### Checklist URL and stamp

[Open the completed checklist](2026-10-16-url.txt). Machine-readable responses: [2026-10-16-response.json](2026-10-16-response.json). Probe results: [probes.json](probes.json). The checklist URL was generated by the frozen runner.

Produced by assess-alignment-with-stamped-principles 0.1.0 with stamped-conventions 0.1.0, checklist 0.3.1 (stamped-checklist-schema@v0.3.1, af259ba), on the original delivery at commit a5761281bfdd9868cd88cb0720d8d06b9e2f7fb8, 2026-10-16, Codex/GPT-6. Canonical capture manifest: 19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a. Probe output: 2026-10-16-probes.json.

## Scientific adequacy

Scientific adequacy: supported.

Hypothesis conclusion: In the 54-person equal-indifference group, the supplied gain-effect maps do **not** support a positive vmPFC response to increasing potential gain.

The analysis uses the 54 supplied participant cope maps as independent observations, checks exact participant matching, finite values, common shape and affine, and uses the intersection of nonzero map support so uncovered zero-filled voxels are not mistaken for measured nulls. It reports a one-sided participant-level group test and applies sampled sign-flip max-*t* correction across 198,029 voxels. The confirmatory report is appropriately based on whole-brain corrected results, as required by the task. The original NARPS instructions also base the binary hypothesis decision on whole-brain-corrected analysis and request whole-brain statistical maps ([NARPS analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)). The vmPFC sphere is defined independently at MNI [0, 40, -8] with 10 mm radius and identified as an operational ROI rather than a unique anatomical boundary.

The report finds a vmPFC sphere mean cope of −0.0057 (SD 0.0983; 95% *t* interval −0.0326 to 0.0211), with 25/54 positive participant means, and no vmPFC voxel passing whole-brain FWE correction (largest sphere *t* = 1.70, corrected *p* = 1.00). It finds 24 corrected positive voxels in three posterior clusters, which it correctly does not treat as evidence for the vmPFC hypothesis. The ROI’s nominal one-sided *p* is clearly labelled unadjusted/descriptive; it does not replace the corrected whole-brain criterion.

The inference is scientifically defensible for the supplied effects: the directional test, coverage handling, independent ROI definition, correction, uncertainty display and interpretation align with the question. The reported outcome is absence of corrected support, not proof of a zero effect. The interval includes effects in either direction. Sign-flip inference assumes symmetric participant-level errors; the supplied maps are effect estimates rather than standardized statistics, and the absent participant variance maps prevent weighting or propagation of first-level uncertainty. The upstream gain regressor was mean-centered and variance-normalized, so the estimates are not effects per currency unit; the result is conditional on AO86’s fixed first-level model. These limits are stated and do not overturn the appropriately qualified group conclusion.

Primary scientific evidence: canonical capture 19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a at content/workspace/report.md, content/workspace/scripts/analyze.py, content/workspace/results/summary.json, content/workspace/results/participant_qc.tsv, content/workspace/results/vmPFC_participant_values.tsv, content/workspace/input/upstream-methods.md, and content/workspace/input/participants.tsv.

## Replay

One frozen-helper replay ran from a fresh copy of the canonical complete delivery using the exact documented entrypoint:

    /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python scripts/analyze.py

The documented interpreter was available; no dependency installation, input retrieval, source edit or repair was needed. Eleven generated outputs were selected from the script’s explicit writes. Ten were byte-identical to the shipped outputs. The compressed voxelwise_results.tsv.gz differed as a byte stream, so the helper recorded the attempt as partial. Decompression showed identical 20,368,521-byte table content (198,029 rows; 10 columns), and parsed numeric values and all table values were exactly equal (maximum numeric difference 0). Thus the observed discrepancy is gzip/container serialization, not a changed scientific quantity. Full helper record and stdout/stderr are retained in 2026-10-16-fresh-rerun.json, replay-copy/replay.stdout, and replay-copy/replay.stderr; comparison detail is in replay-comparison.json. This independent replay supports reproducibility but is not worker-stop evidence of testing practice.

## Access route

Intended recipient: another researcher. Worker-declared route for retrieving the analysis package: none found in the complete stopped delivery. The report’s NeuroVault/OpenNeuro references identify upstream input sources, not a route to the worker’s report, code, environment or generated outputs. Required coverage for a useful reproduction would include the report, group-analysis script, notebook or other entrypoint, participant maps and metadata, and generated tables/maps/figures; the full delivery contains these locally. No worker publication route was available to test, so tested host scope is none. Coordinator access to the assessment capture is not evidence that the worker had published or shared the package. Details are in access-record.json.

## Capture integrity and attribution

The canonical and initial operational manifest identities both have SHA-256 19e3221a4666a17010e4fdeff780c4bd908b6a62f4552006bbcc9f514e65501a; both manifests report 1,204 entries, complete status, and no capture errors or omissions. judge-target.json records no reference limits. The launcher verifies the operational copy before and after assessment. The final inspection comparison found only allowed regular-file metadata differences under .git/annex/keysdb/: db changed from the initial hash, and db-shm/db-wal appeared. These are inspection-period operational metadata, not worker evidence; no claim of logical database equivalence is made. No target repair or replay in the inspection copy was performed. The runner’s replay copy is separate. Inspection observations describe the operational copy; replay observations describe the fresh copy; only original capture-relative paths are used above for scientific evidence.

Possible assistance exposure: capture paths include .codex configuration and .entire activity/session metadata (content/workspace/.codex/hooks.json and content/workspace/.entire/logs/entire.log). These identifiers suggest agent/tool artifacts; their contents were not used as grading evidence, and no treatment assignment is inferred or reported. No other worker’s output or prior judgment was consulted.
