# Independent assessment — NARPS potential gains and brain activity

**Canonical delivery:** SHA-256 `7f2db1ff7f63c0e51f3dce32360d8f7c16a54d6339cf8bcbbadd66fa5f86d9e2`; original captured HEAD `d0ad0ea69075111a6de1229d1b5eeb1aa710d550`; captured 2026-10-16 17:01:22 UTC. Unless otherwise stated, evidence paths below are relative to the canonical capture root `content/workspace/` and refer to those original bytes. Artifact-level hashes are in the response JSON and the original delivery manifest.

The manifest reports a complete capture with no omissions or capture errors (1,158 entries). The operational manifest has the same SHA-256 as the canonical manifest. Inspection found a post-capture byte change only in `.git/annex/keysdb/db`, a regular annex metadata file; its digest changed from `f6f8fd7af99434db59fadc6da021051789c6aaa271ebf878c54dafc6c9fde5ca` to `233c0be3e02857e0fbf47b00b8a94de3e9126529bee41b2491286aef7372be80`. This is classified as operational metadata under the supplied rule; logical database equivalence is not established. No other target entry changed. Git status remained `?? REPORT.md`, `?? analyze.py`, `?? finalize_results.py`, `?? results/`; these are delivered worker-stop files, not assessor outputs.

## STAMPED verdicts

- **MUST:** 5 met / 3 partial / 9 unmet / 0 not-checked / 0 N/A (17).
- **SHOULD:** 1 met / 1 partial / 5 unmet / 1 not-checked / 1 N/A (9).
- **MAY:** 0 met / 4 partial / 0 unmet / 0 not-checked / 1 N/A (5).

No overall score is assigned.

### What to improve first

1. Add and record the exact scientific environment, dependency versions, installation steps, and template requirements. That would make the documented commands usable and link outputs to their environment (must/003, 006, 010–017; should/006–008).
2. Put the report, scripts, and generated results into the worker's versioned state before stopping. The captured HEAD omits all four delivered scientific paths (must/004).
3. Declare a researcher retrieval route and test that it provides the complete study bundle to the intended recipient. No worker route was declared or tested (must/016).
4. Add a repeatable run/test record that identifies inputs, code, environment and outputs; the current report gives commands but no environment-linked execution record (must/006; should/002, 004, 005).

### What is already strong

- All 54 participant maps, metadata and source identities are included; maps are annex-backed inside the common workspace. The script checks IDs, grids, finite values and coverage (input/sources.json; input/participants.tsv; analyze.py; results/participant_qc.tsv).
- The report applies positive one-sided voxelwise whole-brain max-T family-wise correction and clearly describes what the supplied effect estimates mean and what the null result cannot establish (REPORT.md; analyze.py; results/summary.json).
- The delivered report and two scripts provide a clear analysis starting point, even though all remain uncommitted in the captured state (REPORT.md; analyze.py; finalize_results.py).

### Per-item results

| Item | Principle | Status | Evidence | Reason |
|---|---|---|---|---|
| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/input/sources.json` | All required inputs, code and outputs are under the captured workspace root; annex links resolve within it. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | The 54 maps and cohort metadata are present under the common root, with relative annex links resolving inside the captured Git directory. |
| must/003 | S.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/REPORT.md#L29`, `content/workspace/analyze.py#L5-L15` | The report names Python packages, but no environment file installs them or links software as a project module. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `content/workspace/REPORT.md`, `content/workspace/analyze.py`, `content/workspace/results/summary.json` | The captured HEAD omits the report, analysis scripts and results; the original delivery includes these as uncommitted files. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `content/workspace/input/data`, `content/workspace/.git/annex/objects` | All 54 participant maps use git-annex pointer files with payloads retained inside the captured repository. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `content/workspace/REPORT.md#L27-L29`, `content/workspace/results/summary.json` | The report and outputs lack a run record linking the produced results to an exact environment and actions. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `content/workspace/REPORT.md#L27-L29` | REPORT.md gives usage commands but no installation or setup instructions for the named scientific environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/REPORT.md#L27-L29`, `content/workspace/analyze.py`, `content/workspace/finalize_results.py` | The report names analyze.py and finalize_results.py as the reproduction starting point, and both scripts are delivered. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `content/workspace/analyze.py#L18-L20` | The delivered analysis resolves inputs and outputs relative to its own file location, with no host-specific paths. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/analyze.py#L5-L15`, `content/workspace/REPORT.md#L29` | The documented route imports NumPy, SciPy, pandas, NiBabel, Matplotlib and Nilearn, but supplies no dependency specification. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `content/workspace/analyze.py#L138-L142`, `content/workspace/REPORT.md#L29` | The execution route leaves package installation and Nilearn template availability to host or network state without documenting those assumptions. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `content/workspace/REPORT.md#L29`, `content/workspace/analyze.py#L138-L142` | The report lists package names, but gives no versions, installation route, or requirements for the Nilearn template. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `content/workspace` | No worker-supplied environment specification is present in the captured workspace or Git history. |
| must/014 | P.3 | unmet | judgement | `content/workspace/REPORT.md#L27-L29` | No command or process for updating dependency specifications is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `content/workspace`, `content/workspace/REPORT.md#L29` | The workspace contains no exact package lock, container digest, or equivalent environment pin. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/.git/config`, `content/workspace` | No worker-declared retrieval route shares an exact environment specification or the complete study object. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `content/workspace/REPORT.md#L27-L29` | The report says how to run the scripts, but does not say how to obtain or install the unspecified environment. |
| should/001 | T.2 | met | probe:large-in-annex+judgement | `content/workspace/.git`, `content/workspace/input/data` | Code, documentation and input pointers share Git history; git-annex stores large map payloads within that repository. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `content/workspace`, `content/workspace/results/summary.json` | The complete captured workspace contains no repeated workflow test or CI record; the supplied outputs show one completed analysis state. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/input`, `content/workspace/results`, `content/workspace/analyze.py` | Inputs and results occupy separate directories, while code and environment are not separate modules. |
| should/004 | E.1 | not-checked | judgement | `content/workspace/REPORT.md#L27-L29` | No fresh-environment replay was run because the worker supplied no environment specification; a worker run record could settle prior fresh testing. |
| should/005 | E.1 | unmet | judgement | `content/workspace/REPORT.md#L27-L29`, `content/workspace` | The documented workflow runs two Python scripts directly and creates no disposable environment per execution. |
| should/006 | D.2 | unmet | probe:ci-present+probe:run-env-linked+judgement | `content/workspace` | No exact environment specification or repeated reconstitution test is supplied. |
| should/007 | D.2 | unmet | judgement | `content/workspace` | No environment image, package archive, or executable dependency artifact is included. |
| should/008 | D.2 | unmet | judgement | `content/workspace/REPORT.md#L27-L29` | No dependency-update process is declared; this duplicates must/014 by checklist design. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json`, `content/workspace/REPORT.md#L29` | N/A: the data and software identified in the delivery are public inputs and ordinary public package dependencies; no restricted component is present. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `content/workspace` | N/A: the study has no independently maintained project components; annexed data and Python packages are inputs/dependencies, not project modules. |
| may/002 | M.2 | partial | judgement | `content/workspace/REPORT.md#L27-L29`, `content/workspace/input` | The directory layout separates inputs, code files and results, but the report does not explain a modular structure or recombination. |
| may/003 | M.2 | partial | judgement | `content/workspace/analyze.py#L18-L20`, `content/workspace/input` | Inputs and results have directory boundaries, but all components share the root repository and the code assumes fixed paths and filenames. |
| may/004 | M.2 | partial | judgement | `content/workspace/REPORT.md#L27-L29` | The report composes the analysis and finalization scripts as two commands, but defines no module orchestration mechanism. |
| may/005 | M.2 | partial | judgement | `content/workspace/REPORT.md#L9-L11`, `content/workspace/REPORT.md#L15` | The report links to result figures and the QC table, but gives no overview of the directory or component boundaries. |

### Flagged items

- **must/002:** The subdataset probe only checked submodule/subdataset declarations. The maps are directly present through relative annex links and payloads under the common captured root, so the reading overrides its not-checked result.
- **must/005:** The probe's `.datalad/config` citation does not match this plain Git plus git-annex layout. The met verdict rests on the 54 pointer files and captured `.git/annex/objects` payloads.
- **must/006:** The probe found no recognized run records and left the item not-checked. The complete report and results contain no environment-linked run provenance; the final verdict is unmet.
- **must/007 and must/008:** The entry-point probe only inspected tracked files and missed the worker's untracked report and scripts. Direct inspection changes must/007 to partial (usage but no installation instructions) and must/008 to met.
- **must/011 and must/012:** The command scan did not assess the documented route's dependency and Nilearn template assumptions. Direct inspection yields unmet and partial, respectively.
- **must/015:** No environment exists in the captured delivery to pin. The probe's not-checked status is overridden by the complete inventory showing no exact environment specification.
- **should/002 and should/006:** Missing recognized CI alone would not settle these items. The complete captured delivery also lacks repeated workflow testing or environment reconstitution evidence, so both are unmet.
- **may/001:** No-submodule detection alone could not establish whether independent project modules exist. Inspection found none; this item is not-applicable.

### Not checked

- **should/004:** Fresh-environment testing could not be established. The one replay was not attempted because the worker did not supply the environment needed to reconstruct it. A worker run record naming a fresh environment would settle this.
- **Replay:** See [replay record](replay-record.json). The documented command and safe generated-output set are identified, but the required worker-supplied environment is absent. No scientific input retrieval occurred and no shipped output was treated as a replay result.

### Goals, kind and attribution

**Assumption (no human guidance was attached):** The goal is the group-analysis study in the supplied task: assess a positive parametric gain effect in vmPFC for the 54 equal-indifference participants. The primary kind is **study**, because the product is an analysis answering that question. This kind is not user-confirmed.

The worker-stop receipt records a clean worker exit (return code 0, no timeout) and the exact complete capture used here. The participant maps, cohort table, upstream methods and study task are supplied inputs. The report, analysis scripts and result files are present in the worker-stop workspace but outside the captured HEAD. The coordinator's later capture, preservation and delivery establish evidence retention only; they do not establish worker publication or access. The commit metadata identifies a Codex co-author/runtime. This assistance exposure is recorded as context and was not used as grading or scientific evidence.

**Access:** The intended recipient is a researcher using the worker's authorized route. No route was declared: the captured `.git/config` has no remote, and the report identifies no distribution route for the complete workspace. Required coverage is the maps, metadata, scripts, report, results and exact environment. No host scope could be tested. Coordinator delivery is not worker access. See [access record](access-record.json).

**Operational integrity and assessor record:** All Git/annex commands targeted the operational copy. The only detected difference from its initial manifest is the annex `keysdb/db` change described above; this does not establish logical equivalence. A redundant response-set action was rejected by the frozen helper because its local recorded runtime lock had changed. The failed invocation is retained at `response-actions/12-must-012.json`; no target bytes changed, and the completed response passed frozen validation. This assessor malfunction is separate from target behavior.

### Scientific assessment

**Scientific adequacy: supported —** the reported conclusion is appropriately limited to lack of whole-brain-corrected evidence in the operationalized vmPFC region; the analysis method and results support that statement. The report correctly avoids treating a non-significant result as proof of zero effect. Its conclusion is conditional on the supplied AO86 participant estimates and the fixed upstream model.

**Hypothesis conclusion:** the delivered analysis does not support a positive gain response in vmPFC at the required whole-brain family-wise corrected threshold.

The analysis includes all 54 supplied participant COPE maps and reports grid and finite-value checks, no exclusions, and a 90%-coverage mask. A positive one-sample t field with 9,999 participant-level sign flips and whole-mask max-T correction is a defensible voxelwise family-wise procedure for this directional question, conditional on the stated sign-exchangeability assumption. The observed corrected field contains 24 positive voxels in posterior occipital clusters and none in the declared vmPFC coordinate ROI. The broad bilateral coordinate ROI is stated in code before effect interpretation, though it is not independently preregistered and other defensible vmPFC definitions could differ. The uncorrected ROI mean and interval are appropriately presented as descriptive; they do not replace the corrected whole-brain decision.

The report also handles the supplied coefficients appropriately: they are estimates from a mean-centered, variance-normalized gain regressor and are not per-currency-unit BOLD slopes. The absence of participant variance maps prevents precision-weighted group inference. The mask treats zeros as outside-map support; the QC table reports nonzero voxel counts but cannot independently prove that every zero is missing coverage rather than a genuine estimate. These are qualifications on interpretation, not material errors in the bounded conclusion. The delivered images, summary and analysis code were inspected as original evidence; no replay was run.

### Checklist link and stamp

[Open the filled STAMPED checklist](2026-10-16-url.txt). The machine-readable answers, including item evidence and flags, are in [2026-10-16-response.json](2026-10-16-response.json). Probe output is [2026-10-16-probes.json](2026-10-16-probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on canonical capture SHA-256 `7f2db1ff7f63c0e51f3dce32360d8f7c16a54d6339cf8bcbbadd66fa5f86d9e2`, original HEAD `d0ad0ea69075111a6de1229d1b5eeb1aa710d550`, 2026-10-16. Frozen assessor source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`; harness/model deployment identifiers were not exposed. Probe output: `2026-10-16-probes.json`.
