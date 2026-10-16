# Independent assessment

**STAMPED verdicts:** MUST: 6 met / 3 partial / 8 unmet / 0 not-checked (17 total); SHOULD: 0 met / 2 partial / 5 unmet / 2 not-checked (9 total); MAY: 1 met / 1 partial / 2 unmet / 1 not-applicable (5 total). Partial does not satisfy a MUST. No overall score is assigned.

## What to fix first

- Add and track a complete environment specification (including pandas, nibabel, Nilearn and exact versions) with a regeneration command; this supports execution provenance, portability and distribution (must/003, 006, 010, 012–017; should/006–008).
- Track the report, analysis code, figures and results at the worker stop, not only the supplied input material; this makes the delivered workspace versioned (must/004).
- Add installation and exact run instructions, then test that route in a fresh environment; the current replay attempt could not start without nibabel (must/007; should/002, 004–006).
- Declare an authorized recipient route that covers the complete delivery, including annex content and the environment artifact; access to the coordinator's assessment copy does not establish worker sharing (must/016; access record).

## What the project does well

The scientific report uses all 54 supplied equal-indifference participants, checks checksums and geometry, explains that the images are participant cope estimates rather than standardized statistics or per-currency effects, and distinguishes a lack of corrected evidence from equivalence to zero. It uses one-sided max-T sign-flip correction across the common whole-brain mask and identifies the operational vmPFC coordinate region separately (captured `report/report.md`, `input/upstream-methods.md`, `code/group_analysis.py`). The script, tables, maps and figures are separated into discoverable directories and the report links them.

## Scientific assessment

**Scientific adequacy: supported.** The reported conclusion is a defensible absence of positive corrected evidence in vmPFC, not a claim that the effect is exactly zero. The report gives 54 participants, 198,029 common-mask voxels, 5,000 sign flips, a directional full-mask max-T correction, and no vmPFC voxels surviving correction (minimum positive corrected p=.776). Its descriptive vmPFC mean is −0.00055 cope units with a 95% t interval spanning zero. It appropriately interprets the three significant small clusters as posterior and outside the vmPFC bounds. The analysis treats participants as independent and states the sign-symmetry assumption. Because participant variance maps are not supplied, the unweighted group model cannot propagate first-level precision; this is a limitation, not a material inference error for the qualified group-stage conclusion. The common mask treats zero values as outside coverage, an explicit but consequential assumption; the report does not establish that every zero is missing rather than a genuine estimate. This and the operational coordinate bounds qualify the inference but do not make the absence claim unsupported. The shipped figures and numerical results are inspection evidence only; replay failed before recomputation.

The **reported hypothesis outcome**, retained separately from adequacy, is: “In the 54-person NARPS equal-indifference group, the supplied gain-effect maps do **not** provide whole-brain-corrected support for an increasing gain-related response in vmPFC.” This is the report’s verbatim outcome statement; it does not establish equivalence to zero or rule out smaller effects. Scientific evidence is from `report/report.md` lines 5–7, 19–27, 33–35; `results/analysis_summary.json`; and `code/group_analysis.py`.

## Worker stop state, access and replay

The canonical original capture is SHA-256 `62c8b372c45e5f68e3c1dcde3ec4f36603924a7aa80cec4a1085c0c719c141b4`; all target paths cited here are relative to that captured workspace. Its manifest and the operational manifest retain the same digest. The captured HEAD is `d4d11a9c1bd38a9c96b5a4cf0c5403c455f1f96c`. At worker stop, Git status showed `code/`, `figures/`, `report/` and `results/` untracked; the worker commit contains the supplied task/input material. The worker-stop receipt (SHA-256 `307ddc9a2f0722b26ba7cb360ce4d97c1d051d858e6f82b8c16524788ef6656c`) lists no omissions and has no declared-artifacts field. The scientific materials themselves are assessed as part of the complete stopped workspace, but they do not earn versioning credit. No publication route or Git remote was declared. The workspace contains `.codex/` and `.entire/` assistance-related artifacts; this exposure is noted but was not used as grading evidence. Coordinator preservation and delivery are not worker access evidence.

The declared access-route check found no route for a researcher to retrieve the complete project. Required coverage would include the full workspace and annex data, instructions, code, outputs and a usable environment specification; the last is absent. No remote host or authorized route could be tested. See [access record](access-record.json).

One replay was declared before execution: `python code/group_analysis.py`, with exactly 14 generated result and figure paths selected and inputs protected. The frozen helper copied the canonical complete delivery and removed only those selected outputs in the replay copy. It failed immediately with `ModuleNotFoundError: No module named 'nibabel'`; no dependency was installed and no retry was made. The helper would compare numerical tables with relative tolerance but byte-compare other output types, so its comparison cannot distinguish scientific NIfTI changes from header changes or figure rendering changes. No outputs were generated and no comparison was made. This is an unavailable replay measurement caused by the supplied runnable environment, not evidence that the scientific analysis failed. Existing shipped results were not treated as replay evidence. The runner itself completed the copy and recorded the failed attempt in [replay record](2026-10-16-fresh-rerun.json), with stdout/stderr under `replay/work/`.

Inspection integrity comparison found no non-metadata additions, removals or modifications relative to the operational manifest. Git inspection changed/created only regular files at `.git/annex/keysdb/db`, `db-shm` and `db-wal`; these are inspection-induced operational metadata and not worker evidence. Logical database equivalence was not established. No external Git pointer or hook path was followed. `judge-target.json` listed no reference limits.

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/study-task.md`, `code/group_analysis.py`, `report/report.md` | All supplied materials reside under the workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `code/group_analysis.py`, `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz` | All 54 maps and metadata are inside input/ and the script reaches them through relative workspace paths. |
| must/003 | S.1 | unmet | judgement | `probe:env-spec-tracked`, `code/group_analysis.py` | No supplied environment specification includes or links the external software dependencies. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `probe:tree-clean`, `.git/index` | At worker stop, report, code, figures and results were untracked, so Git did not track the complete workspace. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex`, `input/sources.json` | git-annex stores the 54 supplied participant maps. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+judgement | `results/analysis_summary.json`, `code/group_analysis.py` | Results record most package versions and analysis settings, but not a complete environment or fully linked execution record. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report/report.md`, `code/group_analysis.py` | Report identifies the script and outputs, but supplies no installation instructions or explicit run command. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report/report.md`, `code/group_analysis.py` | The report names the complete group-analysis script and the notebook as starting points. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths`, `code/group_analysis.py` | Analysis code resolves inputs and outputs relative to its own workspace root. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked`, `code/group_analysis.py` | Required Python packages are not supplied in an environment specification. |
| must/011 | P.1 | met | judgement | `report/report.md`, `code/group_analysis.py` | No OS, hardware or external service assumptions are stated or required by the group script; Python/package assumptions are described separately. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `report/report.md`, `results/analysis_summary.json` | Report and run summary list most software versions, but omit pandas and give no complete installation requirements. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked`, `integrity-check` | No environment specification is present in the stopped workspace. |
| must/014 | P.3 | unmet | judgement | `integrity-check` | No process for regenerating and tracking environment specifications is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked | `results/analysis_summary.json` | No pinned environment artifact is supplied for exact reconstruction. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `access-record.json` | No environment specification is available to share through a recipient route. |
| must/017 | D.1 | unmet | judgement | `report/report.md` | The report lists software versions but gives no instructions for obtaining or using an environment specification. |
| should/001 | T.2 | partial | judgement | `probe:tree-clean`, `probe:large-in-annex` | Git and git-annex are configured for inputs, but code, report, figures and results were untracked at worker stop. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `probe:ci-present`, `results/analysis_summary.json` | Only one analysis result set is present; no repeated workflow test or CI record is supplied. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `report/report.md`, `code/group_analysis.py` | Inputs, code, results, figures and report occupy distinct directories; environment definitions are absent. |
| should/004 | E.1 | not-checked | judgement | `worker-end-state.json` | Worker-stop evidence does not establish whether the pipeline was tested in a fresh container or host. |
| should/005 | E.1 | unmet | judgement | `integrity-check`, `code/group_analysis.py` | No workflow mechanism for disposable execution environments is supplied. |
| should/006 | D.2 | unmet | probe:ci-present+probe:env-spec-tracked+judgement | `probe:ci-present`, `probe:env-spec-tracked` | No environment specification or reconstitution test is supplied. |
| should/007 | D.2 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked` | No environment artifact is archived in the project. |
| should/008 | D.2 | unmet | judgement | `integrity-check` | No process for updating environment definitions is declared. |
| should/009 | M.4 | not-checked | judgement | `input/sources.json` | The supplied record does not establish whether any data or software component is access-restricted. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | — | N/A: no independently maintained project subcomponents are declared; scientific inputs are supplied within the object. |
| may/002 | M.2 | partial | judgement | `report/report.md` | The report maps files and directories, but does not document module relationships or recombination. |
| may/003 | M.2 | unmet | judgement | `code/group_analysis.py` | No independently updateable module boundaries or interfaces are defined. |
| may/004 | M.2 | unmet | judgement | `integrity-check` | No module composition mechanism such as linked components or orchestration is supplied. |
| may/005 | M.2 | met | judgement | `report/report.md` | The report provides links to the entrypoint, input methods, result tables/maps and figures. |

## Flagged items

- **must/002, must/006, must/007, must/008, must/012, should/002, should/003 and may/001 — `probe-overridden`:** the probes were limited to tracked paths or recognized records; inspection of the full stopped workspace supplied the missing evidence. For should/003, the status remains partial, but the full workspace shows separate code/results/report directories while the probe only saw tracked inputs.
- **should/008 — `upstream-duplicate`:** this repeats must/014 word for word; both are unmet because no environment-update process is declared.
- **must/007 and must/008:** the entry-point probe missed the untracked script and report; the complete delivery does document the analysis starting point, but lacks install/run instructions.
- **must/006:** the derived-record probe did not inventory the untracked shipped outputs; direct review found partial software-version provenance, not a complete environment record.



## Probe disagreements and not-checked items

The scripted entry-point probe and tree-clean probe inspect tracked Git content; the complete stopped delivery also contains untracked report/code/results. Direct inspection therefore overrode the entry-point probe for must/007–008 and the module probe for should/003. The derived-record probe returned not-applicable for must/006 because it saw no tracked generated output; the complete delivery includes generated result artifacts, so this item is partial. The platform-assumptions probe was not conclusive for must/012; direct review found version lists that omit pandas. These overrides and their reasons are recorded in the response JSON.

- **should/004 not-checked:** the captured worker stop does not establish whether an earlier run was tested in a fresh container, batch job or clean host; a worker-side test record would settle it.
- **should/009 not-checked:** the delivery does not establish whether any component is access-restricted; a worker declaration of restriction status would settle it.
- **may/001 not-applicable:** no independently maintained subcomponent is declared; the supplied scientific inputs are included as project data.

## Goal, kind and checklist link

**Assumption (not confirmed):** this is a study object for group analysis of the NARPS equal-indifference potential-gain effect in vmPFC, as stated in `input/study-task.md`; no human guidance is attached to confirm the goal or kind. The pinned checklist URL is available in [2026-10-16-url.txt](2026-10-16-url.txt); the complete item answers and evidence are in [2026-10-16-response.json](2026-10-16-response.json). Scientific adequacy and the verbatim reported hypothesis outcome are also recorded in [scientific-judgment.json](scientific-judgment.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the complete captured study workspace at commit `d4d11a9c1bd38a9c96b5a4cf0c5403c455f1f96c`, 2026-10-16, Codex/GPT-6. Probe output: [2026-10-16-probes.json](2026-10-16-probes.json).
