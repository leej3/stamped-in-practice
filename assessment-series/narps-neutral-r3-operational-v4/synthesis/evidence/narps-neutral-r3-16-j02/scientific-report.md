# Independent assessment — 2026-10-16

## Verdict

MUST: 5 met / 4 partial / 8 unmet / 0 not-checked (17 items). SHOULD: 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable (9 items). MAY: 1 met / 2 partial / 1 unmet / 0 not-checked / 1 not-applicable (5 items). These are item counts, not an overall score.

## What to address first

1. Track the report, notebook, analysis code, figures and results in Git so a revision records the complete scientific state (must/004, should/001).
2. Add a complete, pinned environment file and a documented install/update procedure; include all direct imports (must/003, 006, 010, 012–017; should/006–008).
3. Pin or include the Harvard–Oxford atlas input and document any network requirement, so reproduction does not silently fetch a scientific input (must/002, 011).
4. State reuse terms for the data and code; the declared source route does not state a project license (extra item `license-declared`).

## What is already done well

- All 54 participant maps are represented by Git-annex pointers, with payloads retained inside the capture; the probe found 54 pointers. `input/sources.json` (SHA-256 `919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`).
- The scientific report describes a one-sided whole-brain maximum-t permutation test, checks 54 map identities and common geometry, and distinguishes nonsignificance from a zero effect. `report.md` (SHA-256 `eea99feb32e8f3a5230633f0a9d9adf93b8cf5159e3e69e2af477a45e63f18f5`) `code/analyze.py` (SHA-256 `cf52b4935ca58834a33805e571f0b16f2c06a19092d138e0ea29e80a12e0dc86`).
- The report provides machine-readable summaries, participant QC, a corrected map and two figures, including a clearly labeled descriptive vmPFC interval. `results/summary.json` (SHA-256 `a443515509b9da0f05210d41645d38e320b65260ea9332ac886a4fe7c96453ac`) `results/participant_qc.tsv` (SHA-256 `7f33796d2c073e3744ba0bccaa1a10a58d0e815c5d29716078e712b97183dd15`) `figures/whole_brain_fwe_maxT.png` (SHA-256 `92e2525a0922ba6cb03aff843b72f28258ab2b7ab179eed7dcd7eeae669b6f74`).

## Scientific assessment

**Scientific adequacy: supported.** The reported conclusion is adequately supported for this supplied group-analysis task. The report uses all 54 equal-indifference participants, verifies input checksums and shared grid/affine, defines a common coverage proxy, and applies a directional one-sample max-*t* permutation correction across the whole covered search space. Its vmPFC proxy is explicit and kept out of the inferential mask; the reported corrected foci are posterior and outside that proxy. The report appropriately treats the atlas boundary as approximate and the vmPFC interval as descriptive, and does not turn failure to reject into proof of no effect. Evidence: `report.md` (SHA-256 `eea99feb32e8f3a5230633f0a9d9adf93b8cf5159e3e69e2af477a45e63f18f5`), `code/analyze.py` (SHA-256 `cf52b4935ca58834a33805e571f0b16f2c06a19092d138e0ea29e80a12e0dc86`), `results/summary.json` (SHA-256 `a443515509b9da0f05210d41645d38e320b65260ea9332ac886a4fe7c96453ac`), `results/significant_components.tsv` (SHA-256 `a128ec18501e49d75a531f89a7d6789e572d36be2731aa1f6468c6ee46f91198`).

Limits: inference relies on participant-level sign symmetry and equal weighting because first-level variance maps are absent. The finite/nonzero intersection is a conservative coverage proxy that can omit a genuine exact zero. The coefficient is an upstream gain-modulator cope, not BOLD per unit currency. The anatomical label is a defensible approximation, not a unique vmPFC definition. These limits qualify the scope but do not materially undermine the reported absence of corrected vmPFC support. The first figure's title is clipped/overlaps at the top, a presentation defect that does not alter the numerical result. The shipped values are reviewed as worker artifacts; no replay was run.

**Hypothesis conclusion:** “This group analysis does not support a positive gain effect in vmPFC at whole-brain family-wise error rate (FWER) .05.” This is the worker's reported outcome, separate from the adequacy category. `report.md` (SHA-256 `eea99feb32e8f3a5230633f0a9d9adf93b8cf5159e3e69e2af477a45e63f18f5`)

## Capture, attribution and scope

Canonical original capture: SHA-256 `ed7946e85562771975e45223c4cde2c262250659088e6419b82c54c440564212`; original captured HEAD `e09e9887ff701ffa1b550ad83676aed6d27f5ff1`. The capture has 1183 entries, no omissions and no capture errors. The canonical and operational manifest hashes match. The supplied worker-stop receipt (`worker-end-state.json`, SHA-256 `e788e32f27b98796ea63de7a5b7ba34cb25438a00e6c4ff45186830edc284b58`) records a successful worker exit and corresponds to the complete stopped workspace, including untracked scientific files. `git status --porcelain` in the operational copy showed `analysis.ipynb`, `code/`, `figures/`, `report.md` and `results/` untracked. Coordinator preservation after stop earns no worker versioning or publication credit.

Inspection changed one regular file, `.git/annex/keysdb/db`, from the initial hash in the operational manifest to a new hash; this is within the separately classified annex operational metadata. Logical database equivalence is not inferred. No other difference was found across the 1,091 operational-workspace manifest entries. The allowed annex DB change is inspection-induced metadata, not worker evidence. The assessment did not repair the target.

`judge-target.json` has no reference limits. The captured `.git/config` contains an absolute external `core.hooksPath`; the hooks were not followed or executed. Git status/revision probes were read-only. No Git pointer or external `.git` file was present. `.entire` trace/session material exists in the delivery; it was not opened or used as grading evidence, so no assistance attribution is made.

## Access and replay

The declared route in `input/sources.json` points researchers to NeuroVault collection 4932 and individual map URLs; its OpenNeuro cohort URL is pinned to a source commit. Header-only checks from this assessment host returned HTTP 200 for the collection and one map, with the map's advertised length matching its recorded bytes. This tests route reachability only; it does not independently retrieve/checksum all 54 files or prove that the worker published the code, report and derived outputs. Recipient: a researcher using those declared public routes. Coverage: inputs/cohort metadata only; complete worker analysis artifacts are not established as retrievable by that route. Host scope: this assessment host's network at assessment time. No license terms are stated. See `access-record.json`, `retrieval.stdout`, `retrieval.stderr` and `retrieval.exit`.

Replay status: **not checked**. The documented command sequence is `python code/analyze.py && python code/make_figures.py && python code/summarize_components.py`, with the stated Python/package versions. `analyze.py` calls Nilearn's Harvard–Oxford atlas fetch routine, but the atlas file is absent from the complete capture; allowing the run to proceed could retrieve an undeclared scientific input. Therefore no replay copy was changed and no scientific command was launched. The output selection and prospective numeric comparison rule are recorded in `replay-record.json`; shipped outputs remain worker evidence only, not replay evidence.

## STAMPED items

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/sources.json` | All scientific inputs, scripts, report, results and figures are within the workspace root; annex payloads remain inside .git/annex. |
| must/002 | S.1 | met | judgement | `input/sources.json` | The 54 maps and cohort table are included; sources.json records the NeuroVault collection and per-map retrieval URLs. |
| must/003 | S.1 | unmet | judgement | `report.md`, `code/analyze.py` | No delivered environment specification includes the external Python and atlas software dependencies. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `probes.json` | At worker stop, analysis code, report, notebook and derived outputs were untracked in Git. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probes.json` | Git-annex tracks all 54 large participant maps; probe verified 54 pointers and no large Git blobs. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+judgement | `report.md`, `results/summary.json` | The report identifies analysis commands and package versions, but no exact environment specification links these results to a reproducible environment. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report.md` | report.md documents execution commands and versions, but gives no environment installation procedure. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `code/analyze.py` | The report identifies code/analyze.py as the first command in the reproduction sequence. |
| must/009 | P.1 | met | probe:no-abs-paths | `probes.json` | The delivered scripts resolve paths from their own workspace root; no absolute host paths occur in the route. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `code/analyze.py`, `code/make_figures.py` | The delivered route imports scientific packages but has no environment specification to install them reproducibly. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `code/analyze.py`, `report.md` | The documented route omits host/network requirements; analysis calls Nilearn to fetch an external atlas. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `report.md`, `code/analyze.py` | Python and several package versions are listed, but the dependency list omits direct imports such as pandas, SciPy and Matplotlib. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probes.json` | No tracked environment specification accompanies the delivered code and results. |
| must/014 | P.3 | unmet | judgement | `report.md` | No command or process for updating an environment specification is declared. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `report.md`, `capture inventory` | The report records several tool versions, but no complete pinned environment or lock snapshot is supplied. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `capture inventory` | No environment specification is included or shared for another researcher to retrieve. |
| must/017 | D.1 | unmet | judgement | `report.md` | The report names versions but gives no instructions for obtaining and installing the environment. |
| should/001 | T.2 | partial | judgement | `probes.json`, `probes.json` | Git and git-annex share one repository, but delivered code, report, notebook, figures and results were untracked at worker stop. |
| should/002 | A.2 | not-checked | probe:ci-present | `probes.json` | No CI was found; whether equivalent manual or scheduled repeat testing occurred cannot be established from checked records. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/, code/, results/ and figures/ are distinct in the complete delivery` | Inputs, code and derived outputs occupy separate directories, but no environment module exists. |
| should/004 | E.1 | not-checked | judgement | `replay-record.json` | The shipped run is documented, but no fresh isolated execution was completed in this assessment. |
| should/005 | E.1 | unmet | judgement | `report.md` | The documented commands run inside an existing Python environment and create no disposable environment. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `probes.json`, `report.md` | No exact environment specification or environment-reconstitution testing record is included. |
| should/007 | D.2 | unmet | judgement | `capture inventory` | No environment image, package lock or other environment artifact is archived with the delivery. |
| should/008 | D.2 | unmet | judgement | `report.md` | No environment-update process is declared or recorded. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the declared map sources and software dependencies are public; no restricted component is present. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `operational manifest` | N/A: there are no independently maintained project components; annex data are within this repository. |
| may/002 | M.2 | partial | judgement | `report.md` | The report identifies the code, input and result commands, but does not describe module boundaries or recombination. |
| may/003 | M.2 | unmet | judgement | `report.md` | Directories are separated, but no stable interfaces or independent update boundaries are described. |
| may/004 | M.2 | met | judgement | `report.md` | report.md gives an ordered three-command sequence composing analysis, figures and component summaries. |
| may/005 | M.2 | partial | judgement | `report.md` | The report links figures and gives command paths, but there is no README or module navigation guide. |

### Flagged items

- `must/006`: the probe considered tracked results only; this complete delivery contains untracked results and report. Their recorded versions are incomplete, so the verdict is partial.
- `must/007` and `must/008`: filename probes missed the untracked report and scripts; the documented route is partly usable but lacks environment installation steps.
- `must/011` and `must/012`: command scans cannot assess the external atlas fetch or dependency completeness; full code/report reading found an undocumented network need and an incomplete dependency list.
- `must/015`: the probe only looked for recognized environment records; the report has a partial version list but no complete pin.
- `should/003`: the probe considered tracked paths only; complete delivery separates `input`, `code`, `results` and `figures`, but has no environment module.
- `should/006`: the CI probe alone did not settle equivalent environment testing; the full delivery contains no exact environment specification or reconstitution record.
- `may/001`: the probe could not determine module applicability; the captured Git dependency list is empty and map payloads are internal annex content.

### Not checked

- `should/002`: whether manual/scheduled repeated tests occurred; worker test records would settle it.
- `should/004`: whether the pipeline succeeds in a fresh isolated environment; a safe rerun with the atlas supplied or cached by worker documentation would settle it.

### Goals and kind

Assumption (not confirmed by a human): this is a **study** research object whose goal is to deliver a group fMRI analysis of the NARPS equal-indifference gain-effect maps, with code and results. This follows the supplied `input/study-task.md` and the delivered report. Emphasis is on traceability of analysis, input provenance and reproducible execution.

## Checklist and provenance

Checklist URL: [open the STAMPED checklist](2026-10-16-url.txt). Full response: [response.json](response.json). Probe record: [probes.json](probes.json). Replay record: [replay-record.json](replay-record.json). Access record: [access-record.json](access-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on captured original delivery at HEAD `e09e9887ff701ffa1b550ad83676aed6d27f5ff1`, capture SHA-256 `ed7946e85562771975e45223c4cde2c262250659088e6419b82c54c440564212`, 2026-10-16, Codex/GPT-6. Probe output: `probes.json`.
