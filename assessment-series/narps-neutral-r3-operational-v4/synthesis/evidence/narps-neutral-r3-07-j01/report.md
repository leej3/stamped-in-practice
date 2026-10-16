# Independent assessment

## Identity and scope

Canonical capture SHA-256: `d7cf1ebc3853ab588abbe2eaf32f8391b1e0e96fa80aa4c92128bdb71cd7c495`. Original captured HEAD: `d0ad0ea69075111a6de1229d1b5eeb1aa710d550`. The canonical and operational manifests identify the same complete capture; `judge-target.json` reports no reference limits. Inspection and Git commands ran only against the operational copy. Citations below use the canonical capture digest and capture-relative workspace paths.

The worker stop receipt (`worker-end-state.json`, SHA-256 `b4558a1936a2f8300c50a230965c46df953cdd3417d2b02a1b9bb5077e5e63b5`) identifies a complete, cleanly exited worker state at that HEAD. It lists 54 supplied cope maps and metadata as input identities. The report, analysis script, and result directory are present in the complete delivery but untracked at stop (`git status`: `?? analysis/`, `?? report.md`, `?? results/`, `?? skills/`). Thus they are assessable worker deliverables, but the captured commit does not version them. No coordinator preservation action is credited as worker practice. The delivered annex content and stop receipt support assessment of the files; they do not prove that the worker published an accessible research object.

The delivery contains `.codex` and `.entire` assistant-session material. I note this exposure only; those contents and identifiers were not used as grading evidence, and no treatment assignment is inferred or reported.

## Scientific judgment

**Scientific adequacy: supported.** The analysis is a defensible group-stage test of the stated positive vmPFC prediction, including a defensible absence of positive support. It analyzes the 54 independent participant-level cope maps with one-sided one-sample *t* statistics and participant sign flips, controls whole-brain family-wise error with a maximum-*t* distribution, checks image dimensions, affine and finite data, verifies input checksums, and builds a common-support mask so every tested voxel has all 54 observations. Its coordinate-defined vmPFC ROI is stated in MNI space, is not selected from observed peaks, and is honestly described as an approximation. The ROI participant mean is used for uncertainty rather than treating correlated ROI voxels as independent.

The reported vmPFC estimate is −0.0042 cope (95% *t* interval −0.0217 to 0.0133; one-sided uncorrected *p* = .685); no vmPFC voxel survives whole-brain FWE correction. A separate whole-brain corrected peak at [−26, −102, −3.6] is outside vmPFC and is not taken as support for the hypothesis. The report appropriately says this is lack of support, not proof of a zero effect. It notes the interval, the lack of participant variance maps, equal-weight group inference and its symmetry assumption, common-mask coverage loss, upstream gain-modulator scaling, and the fixed upstream model. These limits qualify interpretation but do not invalidate the specific group inference.

The conclusion is conditional on AO86 participant models and the supplied maps. The rectangular vmPFC approximation is not a definitive anatomical parcellation; the report makes that limitation visible. A no-support result here does not establish equivalence, exclude a small effect, or decide effects under another upstream model. It does mean that these supplied data and this analysis do not provide whole-brain-corrected support for a positive vmPFC effect.

**Reported hypothesis outcome (verbatim):** “The supplied maps do not support a greater vmPFC response with increasing potential gain in the equal-indifference group.” This is the worker report's conclusion, retained separately from the adequacy label.

Scientific evidence: `report.md` lines 5–31; `analysis/run_analysis.py` lines 45–130 and 163–196; `input/upstream-methods.md` lines 3–17; `results/summary.json` lines 1–73; `results/map_qc.tsv` and `results/vmPFC_participant_estimates.tsv`; figures `results/figures/whole_brain_fwe_vmPFC.png` and `results/figures/vmPFC_participant_estimates.png` (all paths relative to the capture digest above).

## STAMPED item judgments

MUST: 5 met / 1 partial / 11 unmet / 0 not-checked (17 items). SHOULD: 0 met / 2 partial / 3 unmet / 3 not-checked / 1 not-applicable (9 items). MAY: 0 met / 2 partial / 0 unmet / 1 not-checked / 2 not-applicable (5 items). No overall score is calculated.

### What to fix first

1. Commit the analysis script, report, figures, and results as part of the worker stop state. This would make the research work itself trackable (must/004; should/001).
2. Supply and track a pinned environment specification and link it to the run/results. This would support installation, provenance, reconstitution, and dependency sharing (must/006, 010, 013, 015–017; should/006–008).
3. Replace the host-specific interpreter command with a portable documented setup, including complete system requirements and how to obtain required template assets (must/007, 011, 012).
4. Declare an authorized retrieval route covering the full object, including all maps, outputs, code, report, and environment artifacts (must/016–017).
5. Record repeatable clean-environment workflow checks and their results (should/002, 004–006).

### What the project already does well

- The 54 map inputs are annex-managed and accompanied by source metadata and checksums (`input/sources.json`; frozen `large-in-annex` probe).
- The analysis checks map geometry, finite values, cohort membership, and checksums, then uses a common observed-support mask (`analysis/run_analysis.py#L45-L72`; `results/map_qc.tsv`).
- The report separates the vmPFC hypothesis from a corrected posterior focus and explains uncertainty and upstream limits (`report.md#L17-L31`).

### Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/.git/HEAD` | All delivered files and directories inspected are nested under the workspace common root. |
| must/002 | S.1 | met | judgement | `content/workspace/analysis/run_analysis.py#L21-L24`, `content/workspace/input/sources.json` | Code addresses the maps and metadata through paths beneath its workspace root; annex-backed inputs resolve inside the captured root. |
| must/003 | S.1 | unmet | judgement | `probe:env-spec-tracked` | No external-software environment or linked software submodule is supplied; package names in the report are not environment artifacts. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `probe:tree-clean`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-07-j01/attempt-01/worker-end-state.json` | Git tracks supplied inputs and metadata, but the worker analysis code, report and results were untracked at stop, leaving substantive work outside version control. |
| must/005 | T.1,T.3,T.5 | met | judgement | `probe:large-in-annex`, `content/workspace/input/sources.json` | Git-annex carries 54 participant maps and annex object content is present in the captured delivery. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `probe:run-env-linked`, `content/workspace/report.md#L33-L42` | The report names package versions but no exact environment specification is linked to these results. |
| must/007 | A.1 | unmet | judgement | `probe:entry-point`, `content/workspace/report.md#L33-L42` | No README or Makefile supplies installation and usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/report.md#L33-L40`, `content/workspace/analysis/run_analysis.py` | The report identifies analysis/run_analysis.py and supplies a run command, giving a clear starting script; the external runtime prerequisite remains unresolved. |
| must/009 | P.1 | met | judgement | `content/workspace/analysis/run_analysis.py#L21-L24` | The script derives input and output locations from its own file and uses project-relative paths. |
| must/010 | P.1 | unmet | judgement | `probe:env-spec-tracked` | There is no supplied environment specification containing the software dependencies. |
| must/011 | P.1 | unmet | judgement | `content/workspace/report.md#L35`, `probe:platform-assumptions` | Host/runtime assumptions are incomplete; the run command embeds an external absolute interpreter and does not specify a complete supported host setup. |
| must/012 | P.2 | unmet | judgement | `probe:env-spec-tracked`, `content/workspace/report.md#L42` | No README or environment specification gives a complete list of system requirements and installable dependencies. |
| must/013 | P.3 | unmet | judgement | `probe:env-spec-tracked` | No environment specification is present alongside the versioned files. |
| must/014 | P.3 | unmet | judgement | `content/workspace` | No process for updating and tracking environment specifications is supplied. |
| must/015 | D.1 | unmet | judgement | `probe:run-env-linked` | No frozen dependency manifest, container digest or equivalent exact environment artifact is supplied. |
| must/016 | D.1 | unmet | judgement | `probe:env-spec-tracked`, `content/workspace/.git/config` | No worker-shared environment artifact or authorized access route is identified. |
| must/017 | D.1 | unmet | judgement | `content/workspace/report.md#L33-L42` | No instructions explain how to obtain and use an environment specification. |
| should/001 | T.2 | partial | judgement | `probe:tree-clean`, `probe:large-in-annex` | Git and annex cover supplied inputs, but untracked code/report/results are not captured by worker version control. |
| should/002 | A.2 | not-checked | judgement | `probe:ci-present` | The delivery does not establish regular repeated testing; absence of a recognized CI file does not settle equivalent records. |
| should/003 | M.1 | partial | judgement | `content/workspace/analysis/run_analysis.py`, `content/workspace/results` | Input, analysis and results directories are separated, but there is no environment module and the report remains at the root. |
| should/004 | E.1 | not-checked | judgement | `probe:ci-present` | No fresh-container, batch-job, clean-VM or cloud workflow record was identified. |
| should/005 | E.1 | not-checked | judgement | `content/workspace` | The delivery does not document disposable environments for executions. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `probe:env-spec-tracked` | No exact environment specification exists to be regularly reconstituted and tested. |
| should/007 | D.2 | unmet | judgement | `content/workspace` | No environment artifact is archived in the delivery. |
| should/008 | D.2 | unmet | judgement | `content/workspace` | No tracked environment update process is supplied. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/study-task.md#L9-L16` | No restricted dataset or software module is identified in the supplied project materials. |
| may/001 | M.2 | not-applicable | judgement | `content/workspace/input/sources.json` | No independently maintained dataset/software component is declared as a submodule; inputs are already included under the root. |
| may/002 | M.2 | partial | judgement | `content/workspace/report.md#L33-L40` | The report links input, code and results artifacts, but does not document a general modular architecture. |
| may/003 | M.2 | not-checked | judgement | `content/workspace/analysis/run_analysis.py` | The delivery does not establish whether modules can be independently updated without breaking the workflow. |
| may/004 | M.2 | not-applicable | judgement | `content/workspace` | No independent modules are declared that require composition. |
| may/005 | M.2 | partial | judgement | `content/workspace/report.md#L33-L40` | The report links the principal script and outputs, but no general navigation guide is supplied. |

### Flagged items

- `must/004` (`probe-overridden`): tree-clean found untracked deliverables; the item is partial because Git does track supplied input and metadata while omitting worker analysis/report/results.
- `must/006` (`probe-overridden`): run-env-linked had no run record to inspect; the report and absence of an environment specification establish that exact environment provenance is unmet.
- `must/008` (`probe-overridden`): entry-point missed the untracked script; `report.md` explicitly documents `analysis/run_analysis.py` and a command.
- `should/006` (`probe-overridden`): the CI probe did not find regular workflow tests, and no exact environment specification exists to reconstitute and test.

### Not checked

- `should/002`: a dated repeated-testing record or CI/workflow evidence would settle whether instructions are tested regularly.
- `should/004`: a record of execution in a fresh container, batch job, clean VM, or cloud instance would settle this.
- `should/005`: a documented execution process showing disposable environments would settle this.
- `may/003`: documentation or workflow evidence showing independently updateable module boundaries would settle this.

### Goals and kind

Kind: study. The goal is the group-stage test of a positive potential-gain effect in vmPFC for the equal-indifference cohort, from the supplied `input/study-task.md` and coordinator scientific guidance. The assessment covers the complete stopped delivery and worker-stop practices; no prior judgment or other worker output was consulted.

## Reproduction and access

**Replay: not checked.** The report's declared command is `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/run_analysis.py`, from the project root. The interpreter/environment is outside the captured delivery and no lockfile or other worker-supplied environment declaration is present. The script also calls Nilearn's MNI template loader, but no template asset is declared in the delivery. Reconstructing or relying on these external resources would exceed the permitted replay scope. Therefore no replay copy was executed and existing outputs are treated only as shipped worker outputs, not replay evidence. The explicitly identifiable generated-output selection is recorded in `replay-record.json`; no inputs or code were selected for removal.

**Access route:** intended recipient is a researcher using the worker-declared authorized route. No worker retrieval route is declared: the operational Git checkout has no remote configured, and no publication/access instructions appear in the report. The source URLs in `input/sources.json` identify upstream inputs, not a retrieval route for this complete research object. Required coverage would include the report, analysis code, results/figures, environment specification and all 54 maps plus metadata. Tested host scope is the supplied operational checkout and its local annex content only; coordinator delivery to the assessor does not establish worker access. Anonymous access was not required. See `access-record.json`.

## Measurement and integrity

The frozen assessor check passed and the 13-probe output is retained. Automated checks are measurements, not substitutes for the above reading: in particular, the entry-point probe missed the script and run command in the untracked complete delivery, and the CI/platform probes remain not-checked where equivalence requires inspection. No target mismatch was observed during inspection. A corrected, read-only workspace comparison against the operational manifest found 1,115 of 1,115 entries matching in content, mode and link target. The only delta was `.git/annex/keysdb/db`, recorded separately as operational metadata; this is not worker evidence and does not establish logical database equivalence. An initial supplemental verifier had path-prefix and symlink-field bugs and was corrected; its false discrepancy output is retained in `operational-audit-attempt-history.txt`. The frozen runner had no malfunction; the first response validation exposed missing assessor dependency metadata, then the response was restamped.

## Checklist and provenance

[Open the filled checklist](checklist-url.txt) · [Response JSON](response.json) · [Frozen probes](probes.json) · [Scientific judgment record](scientific-judgment.json) · [Replay record](replay-record.json) · [Access record](access-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the original captured HEAD `d0ad0ea69075111a6de1229d1b5eeb1aa710d550`, 2026-10-16, Codex independent assessment/GPT-6. Canonical capture manifest: `d7cf1ebc3853ab588abbe2eaf32f8391b1e0e96fa80aa4c92128bdb71cd7c495`. Probe output: `probes.json`.
