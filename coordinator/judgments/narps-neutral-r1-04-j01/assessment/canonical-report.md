# Independent assessment — 2026-10-16

## Verdicts

**MUST:** 5 met / 3 partial / 9 unmet / 0 not-checked (17 total). **SHOULD:** 0 met / 2 partial / 6 unmet / 0 not-checked / 1 not-applicable (9 total). **MAY:** 1 met / 2 partial / 0 unmet / 0 not-checked / 2 not-applicable (5 total). No overall score is assigned.

## Scientific assessment

**Scientific adequacy: qualified.** The analysis provides a defensible whole-brain-corrected test of the supplied participant gain-effect coefficients and appropriately separates the vmPFC hypothesis from the posterior visual-cortex finding. The qualification is about missing-coverage handling: `analysis.py` defines support from finite, nonzero voxels, retains voxels with support from at least 90% of participants, then uses every participant value at those voxels. Any zero representing absent spatial coverage is therefore included as a measured zero; no explicit participant coverage masks are supplied to distinguish an actual zero coefficient from outside-analysis support. At most five of 54 maps can lack support at a retained voxel. This may pull a group estimate toward zero, and the supplied evidence cannot establish whether it does so in the vmPFC or elsewhere. The report discloses the 90% rule but describes it as accommodating variation rather than explaining this zero-as-observation assumption. This warrants qualification, not rejection of the analysis.

**Reported hypothesis outcome:** no positive vmPFC effect is supported by this analysis under the required whole-brain-corrected inference. The anatomical ROI mean is −0.0041 (95% t interval −0.0250 to 0.0169; descriptive one-sided uncorrected p=.651), and no voxel in the AAL3v2 vmPFC approximation is in the positive max-T FWE significant mask. The whole-brain maximum is in posterior occipital cortex (t=6.62, pFWE=.00060); it does not support the vmPFC claim. This is lack of corrected evidence at the analysis's precision, not evidence that the true effect is exactly zero.

The scientific report and code correctly state that the supplied maps are unstandardized participant-level coefficients from a fixed first-level model, with a mean-centered and variance-normalized gain regressor, and thus are not response changes per currency unit. The 54 participants are treated as independent; none are excluded; the maps are checksum-checked and share geometry; the sign-flip max-T procedure is seeded and corrects over the 210,968-voxel coverage search mask. The sign-symmetry assumption, absence of participant variance maps, and broad anatomical approximation are disclosed. The ROI is used for interpretation rather than to restrict or replace whole-brain correction. Evidence: `REPORT.md`, `analysis.py`, `input/upstream-methods.md`, `results/group_results.json`, `results/participant_map_qc.tsv`, and the preserved replay record.

## Delivery boundary and attribution

The original stopped delivery is the complete captured workspace, not just its Git commit. The manifest contains 1,246 entries, has no omissions or capture errors, and matches all delivered regular-file hashes and preserved link targets. The 54 relative map links resolve to annex objects within the workspace. The corrected verification found no delivery mismatch. The first manual manifest check used the wrong base path and generated false missing-file/link findings; this assessor error and its correction are preserved in `manifest-verification-initial-error.json` and `2026-10-16-delivery-verification.json`.

The worker-stop receipt records exit code 0 at 2026-10-16 07:40:27 UTC. The captured Git HEAD history contains only the initial coordinator input-materialization commit. At worker stop, `analysis.py`, `REPORT.md`, `results/`, and `output/` were untracked; the probe also found `.cache/` and `.codex/` untracked. The scientific artifacts are assessed as delivered, but coordinator preservation does not count as worker tracking or publication. The captured `.git/config` records an absolute external `hooksPath`; that target was not followed. No external Git dependencies are recorded in the manifest.

The documented entrypoint was replayed once in a fresh writable copy of the complete capture with the supplied interpreter, without code or environment repair. The exact command, 13 explicit generated output paths, 1e-6 tolerance, 7,200-second limit, 5 GB retrieval cap, output hashes, comparison and exit status are in [the replay record](2026-10-16-fresh-rerun.json); stdout and stderr are retained under `replay/`. The run completed in 23.4 seconds and all 13 outputs matched byte-for-byte. This verifies the documented computation on this host and supplied runtime; it does not establish worker environment capture or portability.

## Retrieval route

The intended recipient is a researcher using the worker-declared route. `input/sources.json` declares public NeuroVault routes for all 54 maps and public GitHub raw routes for the cohort table and methods source. All 57 URLs returned HTTP 200 to HEAD requests on this host, from `neurovault.org` and `raw.githubusercontent.com`; no authentication was required for this tested route. The route covers inputs and provenance sources only. It does not cover `analysis.py`, the report, results, figures, or an environment specification, and no worker-declared route for the complete study object was found. The coordinator's delivery to the assessor is not evidence of worker publication or sharing. Details and per-URL results are in [the access record](2026-10-16-access-record.json).

## What to address first

1. Add a versioned environment specification and document its reconstruction, required host assumptions, and dependency-update process. This closes the largest reproduction gap across MUST 003, 006, 010–017 and SHOULD 006–008.
2. Track the analysis, report, results and figures in the worker's versioned state. At stop, Git contained only the supplied-input commit (MUST 004; SHOULD 001).
3. Clarify coverage handling by supplying explicit participant masks or documenting why zero-valued voxels are observed estimates, then make the group calculation handle absent support explicitly. This tightens the scientific inference.
4. Publish or declare a durable retrieval route for the complete code, report, results and environment, not only the input maps (D.1 items).

## What is already strong

- The study question, fixed upstream model, estimand and limits of the supplied coefficient maps are explained (`REPORT.md`, `input/upstream-methods.md`).
- Input identity checks, geometry checks, per-map QC, coverage mask, seeded max-T null distribution, FWE outputs and readable figures are delivered (`analysis.py`, `results/`, `output/figures/`).
- The documentation provides an executable entry command, and the single bounded replay reproduced all explicitly selected outputs exactly.

## Per-item STAMPED checklist

The table below is generated from the pinned checklist response; `partial` does not satisfy a MUST.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `REPORT.md`, `analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-04-j01/manifest.json` | Workspace files, cached atlas and annex-backed maps resolve within the single workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `.git/annex` | The 54 maps resolve through relative links to annex objects inside the root; source URLs also identify upstream bytes. |
| must/003 | S.1 | unmet | judgement | `analysis.py` | Python libraries are used, but no environment specification or linked software module declares them. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `.git/logs/HEAD`, `2026-10-16-probes.json` | Git tracks the supplied inputs, but the analysis, report, results and figures were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex+judgement | `.git/config`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-04-j01/manifest.json` | All 54 large maps are annex-backed; captured relative symlinks and annex objects preserve their bytes. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `results/group_results.json`, `REPORT.md` | Results record selected package versions and settings, but no exact environment specification links the worker run to an environment. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `REPORT.md#Reproducibility` | REPORT.md gives a usage command, but there are no installation instructions or declared environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `REPORT.md#Reproducibility`, `analysis.py` | The report identifies analysis.py as the starting point and gives its executable command. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analysis.py`, `REPORT.md#Reproducibility` | analysis.py derives its root from __file__ and uses workspace-relative paths for inputs and outputs. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `analysis.py`, `2026-10-16-probes.json` | No environment specification declares the script dependencies. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `REPORT.md#Reproducibility` | The absolute interpreter and thread variables are explicit, but platform and system-library assumptions are not documented. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `REPORT.md#Reproducibility`, `analysis.py` | No complete system requirements or dependency list accompanies the launch command. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `2026-10-16-probes.json` | No environment specification is present in version control. |
| must/014 | P.3 | unmet | judgement | `REPORT.md` | No environment update process is declared; the corresponding duplicate SHOULD item is also unmet. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/group_results.json` | No frozen environment manifest or container digest is provided for exact reconstruction. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `input/sources.json` | There is no environment specification to share; the public input links do not include one. |
| must/017 | D.1 | unmet | judgement | `REPORT.md#Reproducibility` | The report gives a launch command but no instructions for obtaining or reconstructing an environment specification. |
| should/001 | T.2 | partial | judgement | `.git/logs/HEAD`, `2026-10-16-probes.json` | Git and annex cover supplied code/data components, but worker-produced code and outputs were untracked and no environment component was versioned. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `2026-10-16-probes.json`, `REPORT.md` | The delivery contains no worker-run repeated testing or regular workflow checks. |
| should/003 | M.1 | partial | probe:modules-separated | `input/, results/, analysis.py` | Inputs and results have separate directories, but code, environment and independent modules are not separated. |
| should/004 | E.1 | unmet | judgement | `REPORT.md` | No worker evidence shows testing in a fresh container, batch job, clean VM or cloud instance. |
| should/005 | E.1 | unmet | judgement | `REPORT.md#Reproducibility` | The workflow invokes a shared interpreter directly and does not create a disposable environment per run. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `results/group_results.json`, `REPORT.md` | No exact environment specification or worker record of regular environment reconstruction tests is present. |
| should/007 | D.2 | unmet | judgement | `2026-10-16-probes.json` | No environment artifacts, such as an archived container or package environment, are included. |
| should/008 | D.2 | unmet | judgement | `REPORT.md` | Same environment-update process as MUST 014: none is declared or tracked. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: all supplied data and software inputs are public; there is no restricted component to isolate. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `input/sources.json` | N/A: no independently maintained project modules; inputs are included through annex links and package dependencies are not project modules. |
| may/002 | M.2 | partial | judgement | `REPORT.md`, `results/README.md` | REPORT.md and results/README.md explain the data and result files, but do not define independent module boundaries. |
| may/003 | M.2 | partial | judgement | `analysis.py`, `REPORT.md` | The script and input/output folders have an implicit interface, but boundaries and independent update guarantees are not specified. |
| may/004 | M.2 | not-applicable | judgement | `input/sources.json` | N/A: the object has no independently versioned modules that need to be composed. |
| may/005 | M.2 | met | judgement | `REPORT.md`, `results/README.md` | The report and results README guide readers through the workflow and generated artifacts. |

## Extra finding outside the pinned checklist

The licence scan found no licence or reuse declaration for the worker-produced code, report or results. Input source terms were not assessed. This is reported separately because licence is outside the 31 checklist items; see the `license-declared` extra item in the response and probe record.

## Flagged items

- **must/002:** The probe looked for subdatasets and could not answer external-input reachability; direct inspection found the relative annex links and source checksums.
- **must/004:** The tree-clean probe correctly found untracked files, but Git was in use; partial captures incomplete worker tracking more accurately.
- **must/005:** The probe's verdict is supported by annex evidence, but its `.datalad/config` citation does not exist here; annex is enabled in captured `.git/config` and the manifest preserves the content.
- **must/006:** The run-record probe returned not-checked; direct inspection shows selected versions in results but no exact environment identity, so unmet is supported.
- **must/007:** Filename heuristics missed `REPORT.md`'s usage command; it supports partial because installation/environment setup is absent.
- **must/008:** The probe missed the untracked `analysis.py` entrypoint; direct inspection confirms a clear start point.
- **must/009:** The tracked-path scan missed untracked files, but inspection confirms the script itself uses workspace-relative paths; the absolute path occurs in the launch command.
- **must/011, must/012:** The platform scan found no recognized command but cannot assess the explicitly named shared interpreter and omitted system/dependency requirements; direct reading supports partial/unmet.
- **should/008:** This repeats must/014 verbatim by checklist design; the same unmet environment-update process is reported.
- **may/001:** The subdataset probe could not resolve modules; direct inspection found no independently maintained project modules, making this item not-applicable.

## Not checked

No STAMPED checklist item remains not-checked. Scientific adequacy is qualified by the unverified meaning of zero values outside participant map support. The external hook target in `.git/config` was not followed, and no external Git dependency was declared.

## Goals and kind

The goal is to assess whether potential monetary gain produces a greater gain-related fMRI response in vmPFC in the NARPS equal-indifference group, conditional on the supplied fixed participant models. The goal comes from the retained coordinator brief and `input/study-task.md`; the report supplies the methods and product context. No human confirmation was attached. **Kind assumption:** this is a scientific study whose product is an answer with code, data inputs, results and figures.

## Checklist, response and provenance

[Open the completed checklist](2026-10-16-url.txt); the canonical per-item record is [2026-10-16-response.json](2026-10-16-response.json). Probe results are in [2026-10-16-probes.json](2026-10-16-probes.json). The response validated against checklist 0.3.1 using the frozen external assessor: source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`, runtime commit `3552d5003a2485b6405805236d5c54e7ed42f097`. The Codex deployment identifier was not exposed beyond GPT-6. The assessed object is worker-stop commit `2906eaca49c5a00d3df4b0c2dcd59eba9c8a3fb8`, captured at 2026-10-16T07:40:27.939926Z with manifest SHA-256 `be9dfce22879dc38b64f8b9cc6bda8a262258c88cb8bf5a7e14d691d479f9b07`.
