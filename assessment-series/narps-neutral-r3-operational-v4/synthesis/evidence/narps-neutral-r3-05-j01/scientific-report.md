# Independent assessment: NARPS Hypothesis 1

**Object:** study producing a group-level result from fixed NARPS participant gain-effect maps. This is a stated assumption from the supplied task and delivered report; no human confirmation was attached.

**Capture identity:** canonical original capture SHA-256 `d75485e99456b2c86422f940111694530e096867cdbd581892caa49710571fe6`; original captured HEAD `129f3ae3717999e72ef6fbb9e9335f6d69c27470`. Unless stated otherwise, citations below use paths relative to this canonical manifest, prefixed by `content/workspace/`. The manifest records each entry's SHA-256. The stop receipt is external to the capture and has SHA-256 `6607b72de68db4a4fc094f391d9ee034470db18711dc0a38a88f1a79dda5afd8`.

## Verdicts

**MUST:** 5 met / 1 partial / 11 unmet / 0 not-checked / 0 not-applicable (17 total). **SHOULD:** 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable (9 total). **MAY:** 3 met / 1 partial / 1 unmet / 0 not-checked / 0 not-applicable (5 total). No overall score is assigned.

## Scientific judgment

**Scientific adequacy: supported.** This category means the evidence supports the report's stated conclusion that the supplied analysis does not establish a greater vmPFC response; it does not prove a zero effect. The report's verbatim hypothesis outcome is: “In the 54-person NARPS equal-indifference group, the supplied gain-effect estimates do not support a greater vmPFC response as potential gain increases.”

The report analyzes all 54 independent participant cope maps with an equal-weight one-sample group model and a prespecified positive direction (`content/workspace/analyze.py`, SHA-256 `8fad1299cb8d55abaae89e756bfa5966946c21f5c94747cee147f989e6b4214d`). It reports matching map geometry and checks, an intersection-of-support mask of 198,029 voxels, and a one-sided sign-flip permutation maximum-*t* whole-brain FWE procedure (4,999 permutations; seed 20261016). The shipped summary reports 24 significant voxels, all in three posterior cerebellar clusters, with no significant voxel in the descriptively defined 12-mm vmPFC sphere. The ROI mean cope is −0.0068 with 95% *t* interval [−0.0325, 0.0189] (`content/workspace/results/summary.json`, SHA-256 `5937161957ed293563879f0bb112411fb9477bf4316f5d67d89efa083129ce79`; `content/workspace/results/fwe_significant_clusters.csv`, SHA-256 `a12af4454885bd353f57241d2827b9ca64c7633cda11f0b28369bfb9fbf29a9e). The positive whole-brain findings are correctly not treated as vmPFC evidence.

The approach is defensible for these fixed inputs: the maps are participant effect estimates, not *t* or *z* maps; runs are already combined; and the gain regressor was normalized upstream, so the analysis appropriately avoids interpreting the coefficient as BOLD change per currency unit (`content/workspace/input/upstream-methods.md`, SHA-256 `508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`). The report discloses equal weighting without participant variance maps, sign-exchangeability, common-support coverage, the approximate anatomical sphere, and the fact that non-significance is not equivalence.

One numerical wording error does not change the inference: the report calls *p* = .001 the minimum attainable Monte Carlo *p* with 4,999 permutations. Under its plus-one formula, the minimum possible value is .0002; .001 is the observed value here. The claimed result remains significant and the vmPFC conclusion is unaffected. Replay was not checked because no worker-supplied dependency specification exists; scientific review therefore relies on the unchanged delivered code and outputs, not a new run. Hypothesis outcome and adequacy category are recorded separately in `scientific-judgment.json`.

## What to fix first

1. Track the report, analysis script and all generated results together in the worker's version-control state. The captured worker stop has these as untracked, so the repository revision does not identify the scientific result (`must/004`, `must/005`, `should/001`).
2. Supply a complete, pinned environment declaration and document how to install it. The script imports six third-party packages, while the report points to an environment that is not in the task or delivery (`must/003`, `must/010`–`must/017`, `should/006`–`should/008`).
3. Record the actual analysis command, code revision, environment identity, inputs and output paths in a run record. Shipped outputs have no worker run record linking them to code and environment (`must/006`).
4. Provide a worker-controlled retrieval route for the complete object, including code, data, results and environment. The stop state has no Git remote or annex publication route (`must/016`).
5. Correct the report's minimum Monte Carlo *p* wording while retaining the valid observed *p* = .001 result.

## What is already done well

- The output is a complete scientific response with code, a concise report, tabular summaries, maps and figures, although these worker-created files were not committed (`content/workspace/REPORT.md`, SHA-256 `4c1e1c7c2ab3104141a719915e66c4f8378efec96d33cd895fe1919d7636d162`; `content/workspace/results/figure1_group_maps.png`, SHA-256 `ac38d13997bc537f5e11fa585685446631060e1d3194ea3a3c0645d8162bb94b`; `content/workspace/results/figure2_vmPFC_roi.png`, SHA-256 `830ca552492b341911b2e8a03a84f9805a7523a56fdb6357015f402e377c5f51`).
- The analysis checks participant identity, finite values, shape, affine and input hashes; it excludes nobody and states its coverage mask and inference assumptions (`content/workspace/analyze.py`; `content/workspace/results/participant_qc.csv`, SHA-256 `4038b5359fb20ac4d53a16264b3a54734f4b2e253b3eacdb941f78b81f5a4c36`).
- Inputs are present as relative links into an in-root annex store and have source/checksum metadata (`content/workspace/input/data`; `content/workspace/input/sources.json`, SHA-256 `919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`).

## Delivery boundary, attribution and scope

The complete target contained the Git repository and annex data, 54 input maps, metadata and source manifests, plus untracked `REPORT.md`, `analyze.py`, and `results/` including ignored/session material. The worker-stop receipt reports a complete capture with no omissions or errors. The recorded worker HEAD is `129f3ae...`; its commit title is “supply materialized scientific inputs.” At stop, Git status showed `?? REPORT.md`, `?? analyze.py`, and `?? results/`. Thus Git history covers supplied inputs, not the worker's complete analysis result. The 54 annex pointers are present, but the worker-created binary result maps and figures are outside annex/version control; supplied annex state is not credited as a worker annex-conversion action.

The launcher-provided operational copy matched the canonical initial manifest before inspection. The first post-probe comparison found `.git/annex/keysdb/db` changed. After later read-only Git inspection, the final comparison found that file changed plus two added regular sidecars, `.git/annex/keysdb/db-shm` and `db-wal`; all three fall under the explicit operational-metadata exception, and every other captured entry matched. The sidecars appeared during inspection and are not worker evidence. This does not establish logical annex-database equivalence. The original manifest has `reference_limits: []`; I did not follow absolute hook paths or external pointers. The captured `.git/config` names an external hooks path, which was not accessed; no external `.git` pointer was used.

The capture also contains the model identifier `gpt-6-lunaCodex` and the captured HEAD has a Codex co-author trailer. This is recorded as assistance exposure only and was not used to judge scientific adequacy or checklist attainment. No treatment assignment was inferred or reported.

The worker-declared full-object route is absent. The Git config contains no remote, and the stop state documents no annex publication. `input/sources.json` lists public source URLs for input data, but those do not cover the worker's script, report, derived outputs or execution environment. Intended recipient: a researcher using the worker's authorized route. Required full coverage: code/report, all 54 maps and metadata, results/figures, and an environment specification. No complete route was available to test; coordinator delivery to the assessor is not evidence of worker accessibility. See `access-record.json`.

The documented scientific entrypoint is `python analyze.py`; the output list and comparison rule were recorded before deciding on replay. Since no required dependency declaration or reconstructible worker environment is present, no replay was attempted. It would have required an assessor-selected or newly inferred environment. See `2026-10-16-replay-plan.md` and `formal-replay-attempt.json`.

## STAMPED item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/input/data` | All scientific inputs, code and outputs are inside one root; the data links resolve within its annex store. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `content/workspace/input/data`, `content/workspace/input/sources.json` | The 54 maps are present through relative annex links inside the object boundary. |
| must/003 | S.1 | unmet | judgement | `content/workspace/analyze.py#L5-L11` | The analysis imports external Python packages, but no environment declaration or linked software module is supplied. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `content/workspace/REPORT.md`, `content/workspace/analyze.py`, `content/workspace/results` | The worker’s report, analysis script and generated results were untracked at stop. |
| must/005 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:large-in-annex+judgement | `content/workspace/input/data`, `content/workspace/results` | Supplied input maps use annex pointers, but the worker’s generated NIfTI maps and figures remain untracked. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `content/workspace/results/summary.json`, `content/workspace/analyze.py` | Shipped results have no worker run record linking the generating action, code and environment. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `content/workspace/REPORT.md#L23-L25` | REPORT.md gives a run command but no usable installation instructions; its claimed prepared environment is absent from the task and delivery. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/REPORT.md#L23-L25`, `content/workspace/analyze.py#L1-L15` | The untracked analyze.py is a clear start point, and REPORT.md instructs readers to run it. |
| must/009 | P.1 | met | probe:no-abs-paths | `content/workspace/analyze.py#L13-L15` | The script resolves inputs and outputs relative to its own directory. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/analyze.py#L5-L11` | Required Python packages are imported but no environment or dependency declaration lists them. |
| must/011 | P.1 | met | probe:platform-assumptions+judgement | `content/workspace/analyze.py` | The documented route and script state no platform-specific host assumptions beyond a Python package environment. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `content/workspace/analyze.py#L5-L11` | The route’s Python and package requirements are not listed in a README or environment specification. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `content/workspace` | No environment specification is tracked with the code and data. |
| must/014 | P.3 | unmet | judgement | `content/workspace` | No dependency specification or update process is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `content/workspace` | No pinned environment artifact identifies the exact software versions used for the results. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `content/workspace/.git/config`, `content/workspace` | No environment specification is supplied or published for a researcher to retrieve. |
| must/017 | D.1 | unmet | judgement | `content/workspace/REPORT.md#L25`, `content/workspace/input/study-task.md` | The report points to an environment supposedly documented in the task, but the task does not provide it or instructions for obtaining it. |
| should/001 | T.2 | partial | judgement | `content/workspace/.git/HEAD`, `content/workspace/REPORT.md`, `content/workspace/analyze.py`, `content/workspace/results` | Git and annex represent supplied inputs, but worker-authored code, report and results are outside version control. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `content/workspace` | One shipped result set does not establish regular testing; repeated run or CI records would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/input`, `content/workspace/analyze.py`, `content/workspace/results` | Inputs and generated results have separate directories and the script is distinct, but there is no environment module. |
| should/004 | E.1 | not-checked | judgement | `content/workspace` | No fresh isolated run was available; a successful run in a fresh environment with supplied dependencies would settle this. |
| should/005 | E.1 | unmet | judgement | `content/workspace/REPORT.md#L25`, `content/workspace/analyze.py#L1-L15` | The documented entrypoint runs directly in the caller’s Python environment and creates no disposable environment. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `content/workspace` | There is no environment specification or record of repeated environment reconstruction. |
| should/007 | D.2 | unmet | judgement | `content/workspace` | No environment image, binary bundle or other environment artifact is archived in the object. |
| should/008 | D.2 | unmet | judgement | `content/workspace` | No dependency update process or tracked update instance is present; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: no restricted data or software component is identified in the supplied object. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json` | Independent participant-map and cohort sources are identified by dataset boundaries, retrieval URLs and byte checksums. |
| may/002 | M.2 | unmet | judgement | `content/workspace/REPORT.md` | Directories separate inputs and outputs, but documentation does not explain a modular structure or recombination. |
| may/003 | M.2 | partial | judgement | `content/workspace/analyze.py#L13-L15` | Relative input and output paths give some separation, but no interface or contract defines independently updateable modules. |
| may/004 | M.2 | met | judgement | `content/workspace/analyze.py#L13-L15` | The standalone script composes the input files into the documented result set. |
| may/005 | M.2 | met | judgement | `content/workspace/REPORT.md#L23-L25` | The report points readers to the analysis, inputs, methods, provenance and figures. |

## Flagged items

- `must/002` (`probe-overridden`): the probe left it unchecked because it recognizes submodules/subdatasets; the delivered participant maps instead resolve via relative links to annex data within the common root.
- `must/005` (`probe-overridden`): the probe saw annex pointers but did not attribute supplied annex state or distinguish it from untracked worker result maps and figures.
- `must/007` (`probe-overridden`): the probe's README/Makefile filename heuristic missed `REPORT.md`, which offers partial run instructions; it still lacks a usable install route.
- `must/008` (`probe-overridden`): the probe scans tracked paths and missed the untracked but delivered `analyze.py`, which the report names as its entrypoint.
- `must/011`, `must/012` (`probe-overridden`): the command scan did not settle host documentation or dependency completeness; the script imports packages, but no OS-specific host setup is required.
- `should/003` (`mapping-questioned`): the probe treats only recognized directory patterns as separate modules; the delivery has distinct `input/`, root `analyze.py`, and `results/` areas, with no environment module.
- `must/014`, `should/008` (`upstream-duplicate`): both checklist items ask the same environment-update question; both repeat the answer by design.
- `may/001` (`probe-overridden`, `mapping-questioned`): the probe only checked for subdatasets; `sources.json` identifies independent upstream map/cohort datasets with direct retrieval URLs and checksums.

## Extra finding

No license file or reuse terms are present in the complete capture; the automated license probe reports this outside the 31-item checklist (`content/workspace/input/sources.json`; full captured file inventory in the canonical manifest).

## Not checked

- `should/002`: the supplied output set shows one analysis result, not regular workflow testing. Repeated dated test/CI records would settle it.
- `should/004`: no fresh isolated execution record exists. A successful run in a clean container, batch job or machine would settle it.
- Replay: not checked because the worker supplied no dependency specification. A worker-declared installable environment plus a safe generated-output selector would enable the one permitted replay.
- Access: no worker-declared full-object route was available to test. A researcher-accessible, authorized route covering the required artifact set would settle it.

## Goals and kind

The documented goal is to assess whether increasing potential monetary gain predicts a greater group-level fMRI effect in vmPFC for the NARPS equal-indifference group, using fixed participant effects, then deliver a concise report, figures, code and results. I assess this as a **study**, with emphasis on traceable analysis results, complete inputs, and a reproducible group workflow. The kind is an assumption because no human guidance was attached.

## Checklist link and record

[Open the filled STAMPED checklist](2026-10-16-url.txt). The canonical per-item record is [2026-10-16-response.json](2026-10-16-response.json), with scripted outputs in [2026-10-16-probes.json](2026-10-16-probes.json). The report, response and checklist link are assessment artifacts outside the target.

Produced with `assess-alignment-with-stamped-principles` 0.1.0 and `stamped-conventions` 0.1.0; checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad`); on canonical capture SHA-256 `d75485e99456b2c86422f940111694530e096867cdbd581892caa49710571fe6`, inspected through the operational copy, original HEAD `129f3ae3717999e72ef6fbb9e9335f6d69c27470`, 2026-10-16, OpenAI Codex / GPT-6. Probe output: `2026-10-16-probes.json`.
