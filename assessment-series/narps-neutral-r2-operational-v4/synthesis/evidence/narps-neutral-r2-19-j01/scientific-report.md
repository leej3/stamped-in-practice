# Independent assessment — NARPS potential gain and vmPFC

**STAMPED item results:** MUST: 4 met / 4 partial / 9 unmet / 0 not-checked / 0 not-applicable (17 total). SHOULD: 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable (9 total). MAY: 4 met / 1 partial / 0 unmet / 0 not-checked / 0 not-applicable (5 total). Partial does not satisfy a MUST. No overall score is assigned.

Evidence citations identify canonical original capture SHA-256 `55039e27138c4d8ef8a473d7df48357003536c639d50b13ecab2264b1ad404e7`; abbreviated paths below mean `content/workspace/<path>` in that capture. Assessor records and the worker-stop receipt are named separately. The operational copy was the inspection target; operational observations are labeled and are not treated as worker artifacts.

## Scientific assessment

**Scientific adequacy: qualified.** The delivered group analysis supports its reported lack of whole-brain-corrected vmPFC evidence, but the conclusion remains conditional on the zero-as-coverage mask and sign-symmetry assumptions; the report should make the former explicit as a limitation.

**Reported hypothesis outcome:** “the available participant maps do not support a positive vmPFC gain effect under whole-brain family-wise error (FWE) correction.” This is a failure to find corrected positive evidence, not a claim that the neural response is exactly zero.

The report's conclusion is supported by a clear group analysis of the 54 intended participants. The code checks the map count against cohort IDs, checks image shape and affine alignment, and applies an equal-weight one-sample t statistic with 10,000 participant sign flips and a maximum-positive-t correction over its common brain mask (`scripts/group_analysis.py#L32-L76`). It defines vmPFC in MNI coordinates before examining the result and retains whole-brain correction for the hypothesis (`scripts/group_analysis.py#L78-L94`; `report.md#L23`). The reported vmPFC mean is −0.0036, its 95% interval is [−0.0227, 0.0156], and zero vmPFC voxels pass the directional whole-brain FWE threshold; 24 corrected voxels occur posteriorly outside vmPFC (`results/group_results.json`; `report.md#L5-L7`). The report correctly describes a lack of support rather than proof of no effect, and limits interpretation to the normalized gain-modulator coefficient rather than BOLD change per dollar (`report.md#L29-L35`; `input/upstream-methods.md#L3-L15`).

One assumption affects coverage: the code derives the intersection mask from `finite` and nonzero effect estimates (`scripts/group_analysis.py#L45-L52`), relying on the documented zero-fill outside each participant brain mask (`scripts/group_analysis.py#L47-L49`). No separate participant masks are supplied. Inspection of the captured maps found 198,029 voxels in the all-participant intersection versus 251,063 in the union; 54 of 4,200 voxels in the rectangular vmPFC coordinate region were excluded from the common mask. This is a defensible way to avoid treating uncovered voxels as zero if zeros exclusively mark outside-mask locations, but exact zero estimates inside coverage would also be excluded. The report should name this assumption and show coverage explicitly. That limitation, plus the sign-flip test's stated symmetry/exchangeability assumption, warrants “qualified,” not “not supported.” The 95% interval and corrected result remain meaningful conditional on those assumptions.

The report says a robust-z screen found no participant beyond 3.5 (`report.md#L25`), while the analysis script writes QC summaries without implementing that statistic (`scripts/group_analysis.py#L108-L118`). I independently recomputed robust z from the shipped participant whole-brain and vmPFC means; neither exceeded 3.5. The result is reproducible from the table, but the analysis code should implement or more clearly label the screen as a separate check. The figures show the mean map, vmPFC threshold result, participant-level ROI values, and posterior whole-brain corrected finding; their captions match the numerical summary (`figures/group_effect_and_fwe.png`, `figures/vmPFC_participant_effects.png`, `figures/whole_brain_fwe.png`).

### Replay measurement

One replay was declared in [replay-plan.md](replay-plan.md) and run by the frozen helper in a separate copy of the complete capture. The exact documented second command was `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python scripts/group_analysis.py`; its captured maps were used without scientific-input retrieval, repair or environment installation. The 7,200-second limit and 5 GB compatibility parameter were retained. The run returned 0 in 22.7 seconds. Nine selected outputs were byte-identical. The helper recorded a `partial` replay because `results/voxel_results.csv.gz` had different compressed bytes. I compared the decompressed 198,029-row table: its columns and all numeric values were identical (maximum absolute difference 0); the TSV, JSON, NIfTI and PNG outputs were byte-identical. The compressed-byte difference is a serialization difference, not a scientific numerical disagreement. The replay used the README's shared host environment, so it does not establish clean-environment portability or a worker-run test. See [replay.json](replay.json), [replay stdout](replay-work/replay.stdout), [replay stderr](replay-work/replay.stderr), and [numeric replay comparison](numeric-replay-comparison.stdout.txt).

## What to improve first

1. Commit the report, scripts, figures and results, or retain a complete versioned snapshot. This captures the actual worker result state and closes must/004 and should/001.
2. Replace the host-local interpreter dependency with a versioned environment specification and document how to install it. This supports dependency completeness, portability and sharing (must/003, /009–/017; should/005–/008).
3. Supply explicit participant coverage masks or document and validate the zero-fill convention; report common and union coverage. This makes the voxel family and ROI coverage auditable.
4. Record a run manifest linking the captured code, input hashes, exact environment and outputs; make the robust-z QC calculation executable. This links results to actions and improves QC traceability (must/006).

## What is already useful

- The input map identities are recorded with per-image checksums, and large source maps are represented by Git-annex pointers (`input/sources.json`; `input/data/sub-001_hypo1_cope.nii.gz`).
- The README gives a concise sequence from exact-map retrieval to group analysis and inventories key outputs (`README.md#L5-L26`).
- The scientific report distinguishes participant effect estimates from t/z statistics, uses whole-brain FWE correction, reports uncertainty, and states upstream limits (`report.md#L23-L35`).

## STAMPED checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/README.md` | The complete analysis workspace, inputs, scripts, results and figures sit under one root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | The 54 participant maps and metadata are included under the common root; exact upstream URLs and hashes are recorded. |
| must/003 | S.1 | unmet | probe:env-spec-tracked | `content/workspace/README.md` | Python packages are named, but no delivered environment installs or links those dependencies. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `content/workspace/.git/index`, `content/workspace/README.md` | The worker’s code, report, figures and results were untracked at stop; Git does not version the complete research state. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `content/workspace/input/sources.json` | The 54 large source maps have Git-annex pointer entries; checksums tie the captured work copies to those inputs. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+probe:run-env-linked+judgement | `content/workspace/scripts/group_analysis.py`, `content/workspace/results/group_results.json` | The delivered results have no run record linking the analysis action and its exact environment. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `content/workspace/README.md` | Usage is documented, but installing or obtaining the named environment is not reproducible from the delivery. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/README.md`, `content/workspace/scripts/group_analysis.py` | The README names the group-analysis entrypoint and its generated products. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `content/workspace/scripts/group_analysis.py`, `content/workspace/README.md` | Project-relative file paths are used in code, but the README command hardcodes a host-specific Python path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `content/workspace/README.md` | No environment specification declares the required packages; the README relies on preinstalled software. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `content/workspace/README.md` | Python and a named shared-environment path are stated; OS and other host assumptions are not. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `content/workspace/README.md` | The README lists Python packages but omits a portable system-requirements or install specification. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `content/workspace/README.md` | No environment specification is delivered alongside code and data. |
| must/014 | P.3 | unmet | judgement | `content/workspace/README.md` | No dependency-update process or tracked environment specification is present. |
| must/015 | D.1 | unmet | probe:env-spec-tracked | `content/workspace/README.md` | The object contains no pinned package lock or environment image identity. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/.git/config`, `content/workspace/input/sources.json` | No worker-published route exposes the complete code, results, report and environment. |
| must/017 | D.1 | unmet | judgement | `content/workspace/README.md` | The README points to a host-local environment path; it gives no route to obtain an environment specification. |
| should/001 | T.2 | partial | judgement | `content/workspace/.git/index`, `content/workspace/scripts/group_analysis.py` | Git tracks supplied input metadata and annex pointers, but the worker’s code, report and outputs were untracked at stop. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `content/workspace/README.md` | No recurring test record is present; a CI filename scan cannot establish whether manual checks recur. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/README.md` | Inputs, scripts, work maps, results and figures have separate directories, but no independent environment module exists. |
| should/004 | E.1 | not-checked | judgement | `content/workspace/README.md#L7-L14`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-19-j01/attempt-01/judgment/replay.json` | The one replay succeeded on the documented shared host environment; no fresh container, VM or cloud environment was tested. |
| should/005 | E.1 | unmet | judgement | `content/workspace/README.md` | The workflow runs in a pre-existing shared environment and does not create a disposable environment. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `content/workspace/README.md` | No exact environment specification exists to reconstitute or test. |
| should/007 | D.2 | unmet | judgement | `content/workspace/README.md` | No environment image, binaries or package artifacts are archived in the research object. |
| should/008 | D.2 | unmet | judgement | `content/workspace/README.md` | No dependency-update process or tracked environment specification is present; duplicate of must/014. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: the delivered source maps are public; no restricted data or software component is identified. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-19-j01/attempt-01/judgment/access-check-retry.stdout.txt` | The independently maintained NeuroVault map source is explicitly identified by per-image URLs and hashes; all 54 URLs responded to HEAD from this host. |
| may/002 | M.2 | met | judgement | `content/workspace/README.md` | README documents the input, code, work, result and figure roles and their use. |
| may/003 | M.2 | partial | judgement | `content/workspace/README.md` | Directories separate roles, but no independent module boundaries or dependency contracts are supplied. |
| may/004 | M.2 | met | judgement | `content/workspace/README.md` | README composes exact-map retrieval followed by group analysis with two explicit commands. |
| may/005 | M.2 | met | judgement | `content/workspace/README.md` | README lists main files and explains their purpose and expected output. |

### Flagged items

- **must/002** — the probe checked submodules, while this object includes its input maps and identifies them through captured per-file URLs and hashes.
- **must/006** — the tracked-path probe missed untracked generated results; the complete delivery contains outputs but no run record connecting them to an environment.
- **must/007, must/008** — the probe examined tracked files only; the complete stopped delivery includes a README and executable script. Usage is documented, environment setup is not.
- **must/009** — the probe missed the untracked README's absolute host interpreter path; code-internal paths are relative to the script.
- **must/011, must/012** — these required reading the documented route; the probe's command scan cannot establish system-requirement completeness.
- **must/014 and should/008** — the checklist repeats the same environment-update question; the same unmet state is recorded on both.
- **may/001** — the submodule probe did not test the independently identified NeuroVault input route; 54 URL checks support the equivalent link evidence.

### Not checked

- **should/002:** regular manual or scheduled testing cannot be established from a single stopped workspace; a dated recurring run record would settle it.
- **should/004:** the only replay used the documented shared environment on this host; a run in a clean container, VM or cloud instance would settle fresh-environment execution.

### Goals, kind and scope

**Assumption (not confirmed with a human):** the goal is to assess a script-first study analysis and its supplied scientific report for the NARPS gain-effect question; the object kind is **study**. This emphasis treats the complete analysis workspace, fixed participant maps, outputs and report as one study product.

The canonical capture is complete and has no manifest-listed omissions. Its original HEAD is `c341bb810566ffec5a12747e921f38c28c618b4a`, which the stop receipt identifies as the seed commit; it contains supplied study inputs, while the worker's report, scripts, results and figures were untracked at stop. The worker exited with return code 0 at 2026-10-16 15:36:18 UTC. The worker-stop receipt is `worker-end-state.json` (SHA-256 `702e95337005119a068608337e95aa5c83d508c61529ce53f55579fcd038e008`). Coordinator retention and delivery are not counted as worker versioning or publication. No Git remote or complete-object retrieval route was declared. The input-only NeuroVault route was reachable for all 54 images from this assessment host; that says nothing about access to the worker's complete report, code, outputs or environment. Details are in [access-record.json](access-record.json).

Captured `.codex` material and Git metadata reveal Codex assistance; this exposure is recorded, not used as grading evidence. Inspection and Git commands were run only against the operational copy. The Git configuration contains an external absolute hooks path; it was inspected as captured text, not followed. Replay used the helper's hooks-path overlay. The initial access-route query also included a metadata row without a URL; that assessor-side query error is retained, then corrected for the 54 image URLs. The first response-set helper driver had a tuple-format error and is retained with its failed logs; a corrected driver set all answers through the frozen response action. A process listing also briefly surfaced an unrelated assessment command fragment; no other worker output or judgment was opened or used. These assessor errors and exposure did not change the target or grading evidence.

The canonical and initial operational manifests had the same SHA-256. A final full workspace inventory comparison found no missing, extra or mismatched target paths except a changed regular file at `content/workspace/.git/annex/keysdb/db`, classified as permitted operational metadata; this does not establish logical database equivalence. No other target path changed. The frozen helper created the replay from the canonical complete capture. No treatment assignment is inferred or reported.

### Checklist URL and provenance

[Open the completed checklist](2026-10-16-url.txt). The full machine-readable answers are in [response.json](response.json); frozen probe output is in [probes.json](probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.2.0, checklist 0.3.1, on the complete canonical capture `55039e27138c4d8ef8a473d7df48357003536c639d50b13ecab2264b1ad404e7`, original HEAD `c341bb810566ffec5a12747e921f38c28c618b4a`, 2026-10-16, Codex operational assessment / model not reported by runtime. Frozen assessor commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`; frozen environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`. Probe output: `probes.json`.
