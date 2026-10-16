# Independent assessment: NARPS Hypothesis 1

**MUST:** 5 met / 2 partial / 9 unmet / 1 not-checked (17 total). **SHOULD:** 0 met / 1 partial / 3 unmet / 4 not-checked / 1 not-applicable (9 total). **MAY:** 0 met / 0 partial / 4 unmet / 0 not-checked / 1 not-applicable (5 total). These are item counts, not an overall score.

**Assumption, not confirmed with a human:** the documented goal is a study answering the supplied NARPS Hypothesis 1 group-analysis question. The primary product is the scientific conclusion and its code/results; the object kind is **study**. The task brief and report support this reading.

**What to improve first:**

1. Track the worker-authored report, analysis code, figures, results and any copied large maps at stop; the captured commit contains only supplied input material (must/004–005, should/001).
2. Supply a complete, pinned environment and link each result run to that environment; this would make the numerical analysis reconstructable (must/003, must/006, must/010, must/013, must/015–017).
3. Put installation and usage instructions at a discoverable entry point and document host requirements (must/007, must/011–012).

**What is already done well:** the analysis verifies the 54 input map checksums; the report describes the conditional meaning and limits of the supplied copes; the group inference and atlas proxy are explicit and whole-brain corrected.

## Identity and scope

This assessment concerns the canonical complete delivery with SHA-256 `fb77bbc21fa696b959436d9f9f8bc0f3f8488816b8dc572c7d02fe80b47e414d` and captured HEAD `447429ce6b992313fd5ad4fc326519db7a4f839a`. The canonical capture is the source of evidence cited below; paths are relative to its capture root. I inspected the operational copy, whose initial manifest matches the canonical capture. No target mismatch was found. The captured Git links for the participant maps resolve into the workspace's own `.git/annex/objects`; no external Git pointer or absolute target was followed. `judge-target.json` lists no reference limits.

The worker stop receipt (`worker-end-state.json`, SHA-256 `798f1f6b11d8ac4d3adcce781cb9f0c69ee4fd0372167d5b2d66fafe6fead758`) records a complete, successful stop and the captured HEAD above. It identifies the submitted scientific files as part of the complete stopped workspace. The captured HEAD is the input-supply commit (`chore(study): supply materialized scientific inputs`); it contains no worker-authored analysis. The worker report, script, figures, result maps and copied `data/` maps are untracked at stop. The stop receipt identifies the `input/data/` annex pointers as supplied seed inputs; who authored the input-supply commit cannot be established from its metadata, so I do not credit that inherited annex representation as worker practice. All conclusions below concern the complete captured files and stop-state practices. Later coordinator preservation and this assessment's observations do not count as worker actions.

## Scientific assessment

**Scientific adequacy: supported.** The report's conclusion of no whole-brain-corrected positive vmPFC evidence is supported by a defensible analysis of the supplied participant-level gain effect estimates. The code verifies the 54 input map checksums, dimensions, affine agreement and finite values; retains all participants; reports the common nonzero-support mask and its coverage limitation; and uses a one-sided, studentized sign-flip permutation max-*T* test over the full tested mask. The vmPFC proxy is defined from Harvard–Oxford medial frontal, subcallosal and orbital labels before examining results, and is not used as a reduced search volume. The report states that no proxy voxel passed whole-brain FWE correction, while the proxy mean is −0.0048 cope (95% *t* interval −0.0243 to 0.0147). This appropriately supports an absence of corrected evidence, not proof of a zero effect.

The global positive peak is posterior to the target region (MNI −26, −102, −3.6; max-*T* FWE *p* = .0006), and the report correctly does not treat it as support for vmPFC. The figures show the anatomical proxy and participant-level dispersion. The analysis is conditional on the fixed upstream gain model: the supplied maps are mean-centered/variance-normalized gain-modulator copes, not standardized statistics or currency-unit BOLD slopes; participant variance maps and the executable upstream model are absent. Equal group weighting, the assumed sign-flip symmetry, the broad atlas proxy and the nonzero-support intersection are material qualifications. The script acknowledges that exact zero estimates inside an input map's field may be dropped. These limits reduce scope but do not undermine the reported group-stage inference.

**Verbatim worker hypothesis conclusion:** “This analysis does not support that prediction: no positive voxel in the operational vmPFC region survived whole-brain family-wise error (FWE) correction.” This is the reported outcome, distinct from the adequacy label.

Key scientific evidence (canonical capture SHA-256 as above):

- `content/workspace/report/hypothesis1-report.md` (SHA-256 `61828e1cd0eb8d3231c0a0b3a777f999821908c7b3e07c866d73f11b5707d5ca`) lines 5–7 report the vmPFC and posterior outcomes; lines 19–29 explain participant coverage, max-*T* correction, anatomical proxy, effect-estimate meaning, uncertainty and limits.
- `content/workspace/scripts/analyze.py` (SHA-256 `f6a20a0ee606f2067511f52353cf1859985f4a243f8289455f24e075608aaea9`) lines 37–78 check input identities, geometry, finite values and complete-case coverage; lines 81–98 implement the one-sided permutation max-*T* inference; lines 114–135 define the proxy and descriptive ROI summary.
- `content/workspace/results/summary.json` (SHA-256 `ae6a7896376ccd4b36e39b12708608ba1e8337f6405f53a88066f60cc22e1495`) records 54 retained participants, 198,029 common-support voxels, 9,999 permutations, 24 corrected positive voxels outside the vmPFC proxy, zero corrected positive proxy voxels, and the ROI estimate/interval.
- `content/workspace/input/upstream-methods.md` (SHA-256 `508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`) describes the fixed participant model and unavailable variance maps. `content/workspace/figures/group_maps.png` (SHA-256 `6035ca3e75d12c4afca60c03229344a0835c193a274094797a8c183f7f703687`) and `content/workspace/figures/vmPFC_participant_means.png` (SHA-256 `e78135d2691ec1be2fcd6aa5c33f57b09bca8bbb7b0798b7988bb0e6ed97d65d`) make the group map and participant spread inspectable.

## STAMPED item attainment

Statuses below assess the worker's recorded stop state. “Not checked” means evidence was insufficient; it is not a negative finding. No overall score is assigned.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/input/study-task.md`, `content/workspace/scripts/analyze.py` | All delivered material is contained under the common content/workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `content/workspace/input/participants.tsv`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `content/workspace/.git/annex/objects/fW/JZ/MD5E-s1794522--2a6f64556ba73c42049c33979409bb66.nii.gz/MD5E-s1794522--2a6f64556ba73c42049c33979409bb66.nii.gz` | Complete-delivery review found the supplied maps and metadata under the root, with local annex links; the probe did not inspect this representation. |
| must/003 | S.1 | unmet | judgement | `content/workspace/scripts/analyze.py`, `content/workspace/report/hypothesis1-report.md` | The script depends on external Python packages, but no environment specification or linked software module is supplied. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `content/workspace/.git/HEAD`, `content/workspace/.git/index`, `content/workspace/scripts/analyze.py` | The captured commit supplies inputs only; worker-authored code, report and outputs are untracked. |
| must/005 | T.1,T.3,T.5 | not-checked | probe:large-in-annex+judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `content/workspace/.git/annex/objects/fW/JZ/MD5E-s1794522--2a6f64556ba73c42049c33979409bb66.nii.gz/MD5E-s1794522--2a6f64556ba73c42049c33979409bb66.nii.gz`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-03-j01/attempt-01/worker-end-state.json` | Annex pointers are identified as supplied inputs; worker-attributed annex use cannot be established. Worker copies/results are untracked. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `content/workspace/results/summary.json`, `content/workspace/report/hypothesis1-report.md` | The shipped summary gives only selected package versions; no exact run-linked environment specification is present. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `content/workspace/report/hypothesis1-report.md` | The report contains usage and package instructions, but no README.md or Makefile provides them. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/report/hypothesis1-report.md`, `content/workspace/scripts/analyze.py` | The complete delivery contains the report-linked analysis script and a runnable command, although both are untracked. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `content/workspace/scripts/analyze.py` | The script derives paths from its own location and uses relative project paths. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/report/hypothesis1-report.md`, `content/workspace/scripts/analyze.py` | Required scientific Python packages are named but not supplied in an environment specification. |
| must/011 | P.1 | met | probe:platform-assumptions+judgement | `content/workspace/report/hypothesis1-report.md` | The documented Python route and script require no additional OS, hardware, mount, scheduler or host configuration. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `content/workspace/report/hypothesis1-report.md` | Python packages are listed in the report, but there is no complete installable system-requirements specification. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `content/workspace/.git/index` | No environment specification is included in the captured repository. |
| must/014 | P.3 | unmet | judgement | `content/workspace/.git/index` | No environment update process or tracked environment specification is present. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `content/workspace/results/summary.json` | No frozen environment specification exists for exact reconstruction. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/input/sources.json` | No environment specification or sharing route is supplied for others to use. |
| must/017 | D.1 | unmet | judgement | `content/workspace/report/hypothesis1-report.md` | The report assumes a prepared interpreter but does not document how to obtain a frozen environment specification. |
| should/001 | T.2 | unmet | judgement | `content/workspace/.git/HEAD`, `content/workspace/.git/index`, `content/workspace/report/hypothesis1-report.md` | Only supplied input material is tracked; worker code, report and results are untracked. |
| should/002 | A.2 | not-checked | probe:ci-present | `content/workspace/scripts/analyze.py` | No recurring test or CI evidence establishes that the workflow is tested regularly. |
| should/003 | M.1 | partial | probe:modules-separated | `content/workspace/input/participants.tsv`, `content/workspace/scripts/analyze.py`, `content/workspace/results/summary.json` | Inputs, analysis code and derived outputs have separate directories; no environment module is provided. |
| should/004 | E.1 | not-checked | judgement | `content/workspace/report/hypothesis1-report.md` | No worker record establishes a clean container, batch job or VM run; the assessment replay did not execute. |
| should/005 | E.1 | not-checked | judgement | `content/workspace/report/hypothesis1-report.md` | No worker evidence describes disposable isolated environments per run. |
| should/006 | D.2 | not-checked | judgement | `content/workspace/results/summary.json` | No exact environment specification exists to assess for regular reconstruction. |
| should/007 | D.2 | unmet | judgement | `content/workspace/.git/index` | No environment artifact is archived in the workspace. |
| should/008 | D.2 | unmet | judgement | `content/workspace/report/hypothesis1-report.md` | No environment update process is documented; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: The delivery declares no restricted data or software requiring a separate module. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json` | N/A: There are no separate independently maintained project components linked as submodules; source data are included under the project root. |
| may/002 | M.2 | unmet | judgement | `content/workspace/input/`, `content/workspace/scripts/analyze.py` | No document explains how the input, code and result parts relate or can be recombined. |
| may/003 | M.2 | unmet | judgement | `content/workspace/input/`, `content/workspace/scripts/analyze.py` | No independently updateable module boundaries or interfaces are described. |
| may/004 | M.2 | unmet | judgement | `content/workspace/report/hypothesis1-report.md` | No mechanism composes the input, code and result parts. |
| may/005 | M.2 | unmet | judgement | `content/workspace/input/`, `content/workspace/scripts/analyze.py`, `content/workspace/results/summary.json` | No guide explains how to navigate the input/code/result layout. |

The automated probe results are retained in `probes.json`. **Flagged probe disagreements:** must/002 overrides probe not-checked because the complete delivery contains the inputs and its annex links stay inside the root; must/004 remains unmet; must/005 overrides the annex probe to not-checked because the stop receipt identifies tracked pointers as supplied inputs and worker-attributed annex use cannot be established; must/007 and must/008 account for equivalent report/script evidence; must/006 and must/015 use the incomplete shipped version record to settle missing run/environment linkage; must/011 and must/012 use direct route review to assess host assumptions and requirements. must/014 and should/008 carry `upstream-duplicate` because the checklist repeats the same update-process item. Probe observations are not scientific evidence.

**Not checked:** must/005 (worker-attributed annex use; settle with provenance for the annex setup), should/002 (regular testing; settle with recurring run/CI evidence), should/004 (fresh-host test; settle with a completed clean-environment run), should/005 (per-run disposable environment; settle with a worker run record or environment procedure), and should/006 (regular environment reconstruction; settle with a frozen environment plus repeated reconstruction records). Replay availability is separately not checked for the helper/setup reason below.

## Replay and measurement availability

The declared plan is in `replay-plan.md`. It selected the worker-documented `python scripts/analyze.py` command, retained all supplied data/code/metadata/atlas files, and listed only the script's explicit generated outputs. The intended comparison used a relative tolerance of `1e-6` for numeric CSVs and exact bytes for deterministic NIfTI, JSON and PNG outputs.

Replay status is **not checked**. The first frozen-helper invocation failed before materialization because the requested work directory already existed; its complete command and traceback are retained in `replay-command.stdout.txt` and `replay-command.stderr.txt`. The helper then rejected a second invocation because the formal one-attempt allowance had been consumed; that command/output is retained in `replay-command-02.stdout.txt` and `replay-command-02.stderr.txt`. No script process ran, no replay copy/output was produced, and no shipped output is claimed as replay evidence. This is an assessment setup/allowance failure, not evidence of target execution failure. Replay-dependent measures remain unavailable.

## Access and worker-stop attribution

The intended recipient is a researcher using an authorized route. No worker-declared route for the complete code/report/results/environment object was found: the captured Git repository has no remote, and the report does not name a publication/archive for the complete analysis. Thus the required artifact coverage (inputs, code, report, results/figures and a reconstructable environment) is not established as accessible from the worker stop state. Coordinator delivery of this assessment copy is not access evidence.

The worker's `input/sources.json` does declare NeuroVault collection/API URLs for the 54 upstream input maps. Both endpoints returned HTTP 200 when checked from this assessment host; the exact requests and response headers are retained as `neurovault-*-test.*` and `neurovault-*.headers.txt`. These source routes cover the participant maps only, not the worker's complete analysis object or environment. Tested host scope is this assessment host's unauthenticated HTTP access to the collection page and metadata API; individual map downloads and access from a recipient's host were not tested. This does not establish the worker had published the analysis artifacts.

The complete stopped workspace contains `.entire/` interaction-history artifacts and `.codex/` configuration/skill files, which expose assistance-related material. This exposure is recorded without using that content or identifiers as grading evidence. No treatment assignment was inferred or reported.

## Operational integrity

Canonical and operational manifests both contain 1,357 entries with identical paths and entry metadata at the start of inspection. The final byte-level check found three allowlisted operational metadata changes: `.git/annex/keysdb/db` changed from captured SHA-256 `f6f8fd7af99434db59fadc6da021051789c6aaa271ebf878c54dafc6c9fde5ca` to observed SHA-256 `233c0be3e02857e0fbf47b00b8a94de3e9126529bee41b2491286aef7372be80`; new regular sidecars `.git/annex/keysdb/db-shm` (32,768 bytes; SHA-256 `fd4c9fda9cd3f9ae7c962b0ddf37232294d55580e1aa165aa06129b8549389eb`) and `.git/annex/keysdb/db-wal` (empty; SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`) appeared. These inspection-induced metadata files are not worker evidence, and logical database equivalence was not established. Every other workspace path, content hash, link target and mode matched the canonical capture; there were no other changes to bound. The canonical manifest itself has SHA-256 `fb77bbc21fa696b959436d9f9f8bc0f3f8488816b8dc572c7d02fe80b47e414d`; detailed comparisons are in `operational-integrity.json`.


## Assumption, checklist link and assessor provenance

The project goal and kind above are an unconfirmed assessment assumption because no human guidance was attached. The pinned checklist is 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`). The app link is in [2026-10-16-url.txt](2026-10-16-url.txt); the full item record is [response.json](response.json), and the raw probe record is [probes.json](probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0 on the original delivery captured 2026-10-16, Git commit `447429ce6b992313fd5ad4fc326519db7a4f839a`, checklist 0.3.1, Codex/GPT-6. Frozen assessor check: `runner-check.stdout.txt`. Probe output: `probes.json`.
