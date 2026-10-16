# Independent assessment

**MUST:** 5 met / 5 partial / 7 unmet / 0 not checked. **SHOULD:** 0 met / 2 partial / 2 unmet / 4 not checked / 1 not applicable. **MAY:** 1 met / 3 partial / 0 unmet / 0 not checked / 1 not applicable. These are item counts, not an overall score.

Every original-evidence citation below refers to canonical capture SHA-256 `ed7946e85562771975e45223c4cde2c262250659088e6419b82c54c440564212`; paths are capture-relative under `content/workspace/`. Original file hashes are recorded in `response.json` and the canonical manifest. The captured HEAD was `e09e9887ff701ffa1b550ad83676aed6d27f5ff1`.

## Scientific assessment

**Scientific adequacy: supported.** The analysis supports its reported conclusion that this group analysis does not support a positive gain effect in vmPFC. This label assesses support for the worker's conclusion, including a defensible absence of corrected positive findings; it does not imply that the hypothesis itself was supported.

Hypothesis outcome (verbatim): This group analysis does not support a positive gain effect in vmPFC at whole-brain family-wise error rate (FWER) .05.

The delivered code and results address the supplied group question rather than repeating fixed preprocessing or participant modeling. The report describes all 54 equal-indifference maps, no exclusions, matching grids/affines, a strict common finite/nonzero mask, and per-participant QC. The source metadata and participant table are present alongside the maps (`content/workspace/input/sources.json`, `input/participants.tsv`, `results/participant_qc.tsv`). The analysis code implements checksum and cohort assertions, grid checks, and an intercept-only unweighted one-sample group model (`content/workspace/code/analyze.py`). The mask's nonzero rule can exclude true zero estimates; the report explicitly calls this an operational coverage proxy. This is a reasonable conservative response to zero-coded out-of-coverage voxels, with that limitation visible.

Whole-brain inference uses a positive one-sided sign-flip permutation test with voxelwise maximum-*t* correction over the coverage mask, 5,000 permutations, and a fixed seed. The report states the sign-symmetry assumption. The Harvard–Oxford medial frontal/subcallosal proxy is described with coordinate clipping and is used for localization rather than restricting the corrected search. These choices are defensible and satisfy the whole-brain correction requirement. The proxy is approximate, but the result does not rest on an uncorrected ROI test.

The saved summary reports 24 voxels at whole-brain FWER *p* < .05, zero significant voxels in the vmPFC proxy, and a strongest posterior focus at MNI [−26, −102, −3.6] mm (*t* = 6.62, *p*FWER = .0010). The saved component and peak tables locate the corrected foci in posterior cerebellar areas (`content/workspace/results/summary.json`, `significant_components.tsv`, `significant_peak_voxels.tsv`). The descriptive vmPFC mean is 0.0027 cope units with a 95% *t* interval [−0.0217, 0.0270]; the report correctly says this is not a separate confirmatory ROI test (`content/workspace/results/summary.json`, `content/workspace/figures/vmPFC_subject_effects.png`). The whole-brain figure also shows the corrected posterior foci outside the proxy (`content/workspace/figures/whole_brain_fwe_maxT.png`), though its title is crowded. These are worker-shipped results, not replay evidence.

The report properly interprets the supplied maps as participant cope estimates, not *t*/*z* values or BOLD change per dollar, and notes the normalized gain modulator, fixed upstream model, absent participant variance maps, equal participant weighting, and limits of a nonsignificant corrected result (`content/workspace/input/upstream-methods.md`, `content/workspace/report.md`). I found no material inference error. The conclusion is conditional on the supplied maps and upstream model and does not establish a zero vmPFC effect or rule out a smaller effect. I did not independently recompute the group model; replay was not checked because the worker did not supply a complete executable environment and atlas prerequisite.

## Worker stop state, attribution and integrity

The worker stop receipt (SHA-256 `e788e32f27b98796ea63de7a5b7ba34cb25438a00e6c4ff45186830edc284b58`) records a normal exit at `2026-10-16T16:55:54.768446+00:00`, return code 0, with HEAD `e09e9887ff701ffa1b550ad83676aed6d27f5ff1`. At that stop, Git showed `analysis.ipynb`, `code/`, `figures/`, `report.md` and `results/` as untracked. These files remain valid scientific delivery evidence, but they were not tracked in the worker's Git state. The annex-held input maps were present in the delivered workspace. Later coordinator retention, any preservation commit, and delivery to this assessor receive no worker-practice credit.

The worker report names Python 3.13.16, NumPy 2.5.4, NiBabel 5.4.2 and Nilearn 0.14.1, but the analysis also imports pandas, SciPy and Matplotlib without declaring their versions or an installable environment. It calls Nilearn's Harvard–Oxford atlas fetcher at run time. The complete stopped workspace has no environment lockfile, package declaration, container definition, README or Makefile. The worker report does give a script sequence and partial package versions. A shell runtime inspection found Python 3.9.18 and older NumPy/NiBabel/Nilearn versions; that is the assessor host, not evidence of the worker's run environment. The response records partial attainment where some run/version details exist and unmet attainment where a required declaration or installation route is absent.

No worker-declared publication or retrieval route covers the complete report, code, results and environment. The recorded Git remote list is empty. The URLs in `content/workspace/input/sources.json` identify upstream inputs and methods, not a route for a researcher to retrieve this worker's complete analysis. Intended recipient: a researcher following an authorized worker-declared route. Required coverage would include the inputs, instructions, code, report, figures, results/QC and executable environment. Tested host scope was limited to the local operational copy and route metadata; there was no worker route to test over a network. Coordinator delivery is not evidence of worker accessibility.

The canonical and operational initial manifests have the same digest. After inspection, the operational tree still has the same entry count and no content, link, mode, index, ref or object mismatch. The only observed change is a regular-file hash change to `.git/annex/keysdb/db`, classified as permitted operational metadata; logical database equivalence is not established. This inspection-induced change is not worker evidence. `judge-target.json` lists no reference limits. No target content was repaired. The workspace inventory includes `.entire/logs` and session metadata paths; I did not inspect their contents, and did not use assistant-session details as grading evidence.

## Replay and access records

Replay status is **not checked**, not a scientific failure. The report supplies the sequence `python code/analyze.py && python code/make_figures.py && python code/summarize_components.py` and identifies 12 generated result/figure artifacts in `replay.json`. However, the full imported runtime is not specified, the available shell Python does not match the report's runtime, and the atlas payload/retrieval prerequisite is not captured or documented. Installing guessed dependencies or treating the mismatched host as the worker environment would exceed scope. No fresh copy was executed, no shipped outputs were removed, and no output is claimed as a replay result. The time limit was 7,200 seconds; the 5 GB parameter is recorded for compatibility, with no helper prefetch or adapter input retrieval.

The intended recipient, route findings, required coverage and tested host scope are recorded in `access.json`. Because no complete worker-declared route was found, no route retrieval test was possible.

## STAMPED checklist

The full item table is generated from the frozen response. Its probe outputs are retained unedited in [`probes.json`](probes.json); overrides and incomplete probe coverage are discussed in the flagged-items section below.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/input/sources.json` | All workspace content and annex objects are beneath the common workspace root. |
| must/002 | S.1 | met | judgement | `content/workspace/input/sources.json`, `content/workspace/input/participants.tsv` | All 54 participant maps and metadata are delivered with the analysis inputs. |
| must/003 | S.1 | unmet | judgement | `content/workspace/code/analyze.py`, `content/workspace/report.md` | No installable environment specification includes the external software dependencies. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `probe:tree-clean`, `content/workspace/report.md` | The report, analysis code and results were untracked at worker stop, so Git did not track the delivered analysis. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex`, `content/workspace/input/sources.json` | Git-annex carries the 54 large participant maps in the delivered workspace. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+probe:run-env-linked+judgement | `content/workspace/results/summary.json`, `content/workspace/code/analyze.py`, `probe:run-env-linked` | The summary records four software versions and run parameters, but not the complete environment used. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `content/workspace/report.md`, `probe:entry-point` | The report gives run commands but omits installation and environment setup instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/report.md`, `content/workspace/code/analyze.py` | The report names a clear starting sequence and the delivered scripts implement it. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `content/workspace/code/analyze.py`, `probe:no-abs-paths` | Analysis scripts resolve paths relative to their own workspace. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/code/analyze.py`, `probe:env-spec-tracked` | The runtime dependencies are not all declared; several imported packages rely on the host environment. |
| must/011 | P.1 | unmet | judgement | `content/workspace/code/analyze.py`, `content/workspace/report.md` | The analysis calls a Nilearn atlas fetcher without documenting the required network/cache assumption. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `content/workspace/report.md`, `content/workspace/code/analyze.py` | The report names Python and four package versions, but omits a complete system and dependency list. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+probe:tree-clean | `probe:env-spec-tracked`, `probe:tree-clean` | No environment specification is included in the version-controlled project. |
| must/014 | P.3 | unmet | judgement | `content/workspace/report.md` | No environment specification or reproducible update command is supplied. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:env-spec-tracked+judgement | `content/workspace/results/summary.json`, `probe:env-spec-tracked` | Some versions are recorded, but no frozen manifest identifies the complete replicating environment. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `probe:env-spec-tracked`, `content/workspace/.git/config`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-16-j01/attempt-01/judgment/commands/08-access-and-report-lines.log` | There is no worker-declared route publishing an environment specification. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `content/workspace/report.md`, `content/workspace/code/analyze.py` | The report states partial version information and run commands, but not how to obtain or install a complete environment. |
| should/001 | T.2 | partial | probe:tree-clean+probe:large-in-annex+judgement | `probe:tree-clean`, `probe:large-in-annex` | Git and annex are present, but the principal scientific artifacts were untracked at worker stop. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `probe:ci-present` | No record establishes regular workflow testing; a single delivered run does not settle frequency. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/report.md`, `probe:modules-separated` | Inputs, code, results and figures have separate directories, but there is no environment module. |
| should/004 | E.1 | not-checked | probe:ci-present+judgement | `probe:ci-present` | The stopped delivery contains no record showing execution in a fresh container, batch job or clean VM. |
| should/005 | E.1 | not-checked | judgement | `content/workspace/report.md` | No disposable execution environment or per-run isolation record is captured. |
| should/006 | D.2 | not-checked | probe:run-env-linked | `probe:run-env-linked` | There is no record of repeated environment reconstruction and verification. |
| should/007 | D.2 | unmet | probe:env-spec-tracked+judgement | `probe:env-spec-tracked`, `content/workspace/report.md` | No environment artifact is archived in the stopped workspace. |
| should/008 | D.2 | unmet | judgement | `content/workspace/report.md` | No environment update process is declared; this repeats must/014. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: the cited source maps and cohort table are public resources; no restricted component is identified. |
| may/001 | M.2 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: the workspace contains one analysis project and its supplied dataset, with no independently maintained project components. |
| may/002 | M.2 | partial | judgement | `content/workspace/report.md`, `content/workspace/code/analyze.py` | The report explains the input-to-code-to-results sequence, but does not define reusable module boundaries. |
| may/003 | M.2 | partial | judgement | `content/workspace/code/analyze.py` | Separate folders support basic organization, but code and outputs are not independently updateable components. |
| may/004 | M.2 | partial | judgement | `content/workspace/report.md`, `content/workspace/code/summarize_components.py` | The report composes three scripts manually; no automated component or environment orchestration is supplied. |
| may/005 | M.2 | met | judgement | `content/workspace/report.md`, `content/workspace/analysis.ipynb` | The report, notebook and descriptive filenames let a reader navigate the main analysis artifacts. |

## Flagged items

- **must/004 — mapping questioned.** `tree-clean` measured whether the repository was clean; must/004 asks whether Git tracked the analysis code, text and documentation. The worker-stop status shows those analysis artifacts were untracked, so the unmet verdict stands on the actual VCS coverage.
- **must/006 — probe overridden.** The tracked-path probes found no run record, but the untracked `results/summary.json` records four versions, run parameters and a seed. That is partial environment provenance, not a complete exact environment.
- **must/007 — probe overridden.** The probe required a README or Makefile. The report gives the script sequence, but it omits installation/setup, so this is partial.
- **must/008 — probe overridden.** The probe missed the worker's untracked report and scripts; together they provide a clear entrypoint.
- **should/003 — probe overridden.** The probe saw tracked paths only. The complete stopped workspace separates inputs, code, results and figures, but has no environment module, so attainment remains partial.
- **should/008 — upstream duplicate.** This repeats must/014's environment update-process question; the same unmet evidence applies.

## Not checked

- **should/002:** no repeated workflow-testing record was established. A worker run history or recurring test record would settle frequency.
- **should/004:** no clean-container/VM/batch execution evidence was established. A worker run record identifying that host would settle this.
- **should/005:** no disposable-environment mechanism was established. A delivered workflow or run record showing isolation would settle this.
- **should/006:** no repeated environment-reconstitution record was established. A reconstitution/test log tied to the recorded environment would settle this.
- **Scientific replay:** no complete worker-supplied runtime and atlas prerequisite is available. A complete dependency declaration plus the needed atlas asset or its documented retrieval route would allow the one permitted replay.

## Goals and project kind

The stated goal is a group-stage analysis of whether potential gain increases the fMRI response in vmPFC for the equal-indifference group, using 54 supplied participant gain-effect maps. The task explicitly fixes upstream modeling and requires whole-brain-corrected inference. This is a computational **study** with linked large inputs and derived group analyses; the emphasis is on tracking, environment capture and distributable analysis artifacts.

## Checklist, record and provenance

The [checklist-app URL](checklist-url.txt) was encoded from the validated response. The complete per-item evidence is in [`response.json`](response.json); the unedited probe output is [`probes.json`](probes.json). The capture and stop-state checks are in [`integrity.json`](integrity.json); replay and access records are [`replay.json`](replay.json) and [`access.json`](access.json). Command records are under [`commands/`](commands/).

Assessment runner: frozen `assessment.py` version 1, source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`; checklist 0.3.1; Codex / GPT-6; 2026-10-16. Target: canonical capture SHA-256 `ed7946e85562771975e45223c4cde2c262250659088e6419b82c54c440564212`, captured HEAD `e09e9887ff701ffa1b550ad83676aed6d27f5ff1`. Probe output: [`probes.json`](probes.json).
