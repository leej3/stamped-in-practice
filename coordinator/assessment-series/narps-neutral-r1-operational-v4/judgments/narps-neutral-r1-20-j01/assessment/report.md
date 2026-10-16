# Independent STAMPED and scientific assessment

Date: 2026-10-16 (UTC)

## Scientific judgment

Scientific adequacy: qualified.

The group inference is coherent and the conclusion is appropriately limited: the complete 54-person cohort is analyzed with positive one-sample t statistics and participant-wise sign-flip maximum-t correction over the common nonzero support. The report correctly treats the supplied images as participant COPEs from a normalized gain modulator, not as currency-unit slopes, and describes the absent participant variance maps, upstream model limits, sign-flip assumptions, and uncertainty. The vmPFC summary is labeled descriptive and does not replace whole-brain correction. Qualification is warranted because this is conditional on the supplied upstream estimates and chosen all-participant common-support mask, and the anatomical sphere is an operational coordinate definition rather than a validated individual anatomical segmentation. The limitations do not overturn the stated absence of corrected vmPFC evidence.

Reported hypothesis outcome (verbatim from the worker report):

> In the 54-person NARPS equal-indifference group, we found no support for a greater vmPFC response as potential gain increased under whole-brain family-wise error (FWE) correction.

This adequacy judgment is distinct from the reported hypothesis outcome, STAMPED item attainment, and replay measurement availability. No overall score is assigned.

## Scope, capture, and attribution

The assessed object is the complete captured workspace, including uncommitted and ignored material. Canonical original capture SHA-256: `8c58f2ad4f7217840ed53d63437da4101513952d049c15d85357a0391846b75b`. All paths to workspace artifacts in this report are relative to the captured workspace root (`content/workspace/` in the manifest). The original captured HEAD is `eece8595d255a766517e32ff10b2e6574d3c4e6a`; capture time is 2026-10-16T06:30:44.860153+00:00. The canonical manifest is retained at [manifest.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/targets/narps-neutral-r1-20-j01/canonical/manifest.json).

The stop receipt [worker-end-state.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-20-j01/attempt-01/worker-end-state.json) (SHA-256 `2a4e6c7fb90f34d785dac103f30c16eca11ac566bf6405e80b910d11e6f5a100`) records a normal worker exit and the stop-state capture. At stop, the Git tree tracked the supplied inputs; `analysis/`, `figures/`, `results/`, `report.md`, and `.codex/` were untracked (with `.codex/` and `.entire/` ignored). Thus the scientific products are present in the delivery but were not versioned in the worker's Git tree. Coordinator preservation, packaging, or later access does not earn worker-practice credit.

The inspection used the operational copy. Initial bytes were declared equal to the canonical capture. Its final integrity check found no missing paths, unexpected paths, or changed files outside `.git/annex/keysdb/db`, `db-shm`, and `db-wal`. Those three regular-file database differences are recorded separately in [operational-integrity.json](operational-integrity.json); their logical equivalence is not established. The runner's failed replay did not materialize a separate copy or execute target code. One earlier Git inventory command used invalid shell assignment syntax and did not run; the corrected command and both outputs are retained under `logs/`.

The delivered scientific files are present in the canonical manifest: `report.md` (SHA-256 `d22704a597befd2afcf3dc207053c0ca4a54a05a1a73be20beb00dfbcd0c9c25`), `analysis/analyze.py` (`97d510aca5d4821a8a880085af0c41494bfe11f13059836d18326292448af25c`), `results/summary.json` (`ca2d7767a96bb659a93df6011197fe98f5c7d1b906d0eb8ba49768502effac79`), and `results/participant_qc.csv` (`cb8176844646dddd1eb52a78adab61b3dc7fe5421ee45112923d6c9a65f4504e`). The 54 map references and their payloads are represented in the captured workspace's annex structure; `input/sources.json` records original image checksums and cohort provenance.

## Scientific evidence and limits

The report states that all 54 equal-indifference participants were included, with matching 97 × 115 × 81 geometry and affine transforms, finite nonempty maps, and no effect-based exclusions (`report.md` lines 9–15, 31–35; `analysis/analyze.py` lines 27–55). The script constructs common nonzero support so that zeros outside individual map support are not treated as measured zero effects. It reports 198,029 tested voxels, 5,000 sign flips, a fixed seed, and positive max-T whole-mask correction (`analysis/analyze.py` lines 58–85 and 208–227; `results/summary.json`).

The worker reports no corrected vmPFC overlap, a descriptive ROI mean of -0.0061 COPE units and 95% t interval [-0.0342, 0.0221], with 25/54 positive participant ROI means. The positive whole-brain corrected findings are posterior to the hypothesized region (`report.md` lines 17–25; `results/summary.json`). The figure shows the mean map, corrected positive map, and participant ROI values (`figures/group_gain_vmPFC.png`, SHA-256 `5ec9684e227a6b35e09571c5572ac4b82fd2684dd8c737b12a6dd2c40bd221a9`). These values are shipped results, not replay evidence.

The model is a defensible unweighted one-sample analysis of independent participants given the absence of participant variance maps. Sign flipping relies on independence and a sufficiently symmetric null, as disclosed. The common-support intersection avoids missing-as-zero bias but limits inference to shared coverage. The ROI is independent of the observed results, but its 10 mm MNI152 sphere is only one operational definition and may not match tissue boundaries exactly in the supplied MNI152NLin2009cAsym images. The result is therefore evidence of no corrected support under this model and mask, not evidence that the true effect is exactly zero, nor a causal effect of money or an effect per currency unit.

## Replay and measurement availability

The declared command was `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis/analyze.py`, from the workspace root. The report names that interpreter path, but no environment specification is delivered; the external path was not inspected or reconstructed. The intended explicit outputs were `results/participant_qc.csv`, `results/summary.json`, the four generated group NIfTI maps, and the two figures. Only those eight outputs would have been removed from the separate replay copy. Comparison was to use frozen `rtol=1e-6`, timeout 7,200 seconds, and `max_get_gb=5` (the captured-delivery helper performs no prefetch or input retrieval).

One helper attempt failed before copy or scientific execution because the requested work directory already existed: `ValueError: Materialization requires a new destination`. This was an assessment setup error, not target behavior. The failed command and stdout/stderr are retained in `logs/fresh-rerun.*`; [fresh-rerun.json](fresh-rerun.json) records the attempt. No successful replay measurement is available, and no second attempt was made. This failure does not invalidate the shipped scientific results or substitute for them.

## Access and sharing

The intended recipient is a researcher using the worker-declared authorized route. No complete-object retrieval route is declared in the worker stop state; the report's interpreter path is not a sharing route, and the upstream image URLs in `input/sources.json` do not provide access to this complete analysis workspace. Required coverage would include code/report, all 54 maps and metadata, generated results/figures, and a usable environment specification. No worker route was available to test on any host; local coordinator delivery is not proof of worker publication. The retained [access record](access-record.json) gives this scope. The captured `.git/config` contains an absolute hooks path; no external target was followed. `judge-target.json` lists no additional reference limits.

The captured `.entire/` session material and `.codex/` configuration indicate agent/tooling artifacts in the workspace. This exposure is recorded as context only and was not used as grading evidence; no treatment assignment was inferred.

## STAMPED verdicts

MUST: 5 met / 1 partial / 11 unmet / 0 not-checked of 17. SHOULD: 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable of 9. MAY: 0 met / 3 partial / 1 unmet / 0 not-checked / 1 not-applicable of 5.

### What to address first

1. Include a pinned environment specification and link it from the documented command → readers need the declared Python packages and host assumptions to reproduce this group analysis (must/003, 006, 010–017; should/005–008).
2. Track the analysis script, report, and generated products at the worker stop → these are the core scientific deliverables and currently sit outside the captured Git history (must/004; should/001).
3. Replace the machine-specific interpreter path with an obtainable environment and setup instructions → the current command is not portable for a new researcher (must/007, 011, 012, 017).
4. Publish an authorized route covering the complete workspace and environment → an upstream input source is not access to the complete study (must/016).

### What is already strong

- The analysis uses the supplied full cohort, checks geometry and values, preserves all participants, and reports quality checks and uncertainty (`analysis/analyze.py`; `results/participant_qc.csv`).
- Whole-brain positive max-T FWE inference is implemented, with a separate anatomically defined descriptive vmPFC summary (`analysis/analyze.py` lines 67–104; `report.md` lines 13–25).
- Large participant maps are stored through annex pointers with local captured payloads; the complete input mapping is documented in `input/sources.json`.

### Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/study-task.md#L9-L15`, `report.md#L37-L45` | The captured workspace, inputs, code, outputs, and Git metadata share one root. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `analysis/analyze.py#L20-L31` | All 54 maps and metadata are present under input/ and consumed with workspace-relative paths. |
| must/003 | S.1 | unmet | judgement | `analysis/analyze.py#L11-L18`, `report.md#L39-L45` | The analysis imports external Python packages, but no delivered environment specification includes them. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `analysis/analyze.py`, `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-20-j01/attempt-01/judgment/logs/git-status.stdout.txt` | Git tracks supplied inputs, but worker code, report, figures, and results were untracked at stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data/sub-001_hypo1_cope.nii.gz`, `input/sources.json` | Git-annex pointers and their payloads carry the 54 large participant maps. |
| must/006 | T.1,T.3,T.5 | unmet | judgement | `results/run-log.json`, `report.md#L37-L45` | The run record repeats summary results but does not identify an exact environment for the executed action. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report.md#L39-L45`, `analysis/analyze.py` | The report gives a usage command, but installation and environment acquisition instructions are absent. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md#L39-L45`, `analysis/analyze.py#L1-L6` | The report names analysis/analyze.py as the starting point and states its generated products. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analysis/analyze.py#L20-L23`, `analysis/analyze.py#L27-L30` | The analysis script resolves inputs and outputs relative to its own workspace root. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `analysis/analyze.py#L11-L18`, `report.md#L39-L45` | No dependency specification is delivered for Python, NumPy, pandas, SciPy, nibabel, or Matplotlib. |
| must/011 | P.1 | unmet | judgement | `report.md#L39-L43`, `analysis/analyze.py#L11-L18` | The required external interpreter location is host-specific, and OS or host prerequisites are not documented. |
| must/012 | P.2 | unmet | judgement | `report.md#L37-L45`, `analysis/analyze.py#L11-L18` | No system requirements or dependency list accompanies the documented execution route. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `input/sources.json`, `analysis/analyze.py#L11-L18` | No environment specification is present in the delivered tracked files. |
| must/014 | P.3 | unmet | judgement | `report.md#L37-L45`, `analysis/analyze.py#L11-L18` | No dependency-update process or tracked environment updates are present. |
| must/015 | D.1 | unmet | probe:env-spec-tracked | `analysis/analyze.py#L11-L18`, `report.md#L39-L45` | No frozen package manifest or other exact environment specification is included. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `report.md#L37-L45`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-20-j01/attempt-01/worker-end-state.json` | The worker stop state contains no published or archived environment specification or retrieval route. |
| must/017 | D.1 | unmet | judgement | `report.md#L39-L45` | The report names an interpreter path but gives no instructions to obtain the environment specification. |
| should/001 | T.2 | partial | probe:tree-clean+judgement | `input/participants.tsv`, `analysis/analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-20-j01/attempt-01/judgment/logs/git-status.stdout.txt` | Git tracks the supplied inputs, while analysis code, report, outputs, and ignored session material were outside version control. |
| should/002 | A.2 | not-checked | probe:ci-present | `report.md#L37-L45`, `results/run-log.json` | No repeated-test record is identified; CI absence alone cannot settle regular workflow testing. Test history would settle this. |
| should/003 | M.1 | partial | probe:modules-separated | `input/`, `analysis/analyze.py` | Inputs are separated under input/, but code, outputs, and environment are not organized as distinct modules. |
| should/004 | E.1 | not-checked | judgement | `fresh-rerun.json` | The one replay attempt failed in the assessment helper before execution; a successful fresh-machine test would settle this. |
| should/005 | E.1 | unmet | judgement | `report.md#L39-L43` | The documented route invokes a shared external interpreter and does not create a disposable environment. |
| should/006 | D.2 | unmet | probe:env-spec-tracked | `analysis/analyze.py#L11-L18`, `report.md#L39-L45` | No exact environment specification exists to reconstitute or test. |
| should/007 | D.2 | unmet | judgement | `input/`, `analysis/analyze.py` | No environment artifacts are archived with the study. |
| should/008 | D.2 | unmet | judgement | `report.md#L37-L45` | No environment-update process is declared; this repeats must/014 by checklist design. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: no restricted data or software is identified in the complete captured workspace. |
| may/001 | M.2 | not-applicable | judgement | `input/sources.json`, `analysis/analyze.py` | N/A: no independently maintained project components are declared; inputs and analysis are delivered within this workspace. |
| may/002 | M.2 | partial | judgement | `report.md#L37-L45`, `input/study-task.md#L9-L15` | The report describes the input and result locations but does not explain the broader component relationships. |
| may/003 | M.2 | partial | judgement | `input/`, `analysis/analyze.py#L20-L23` | Input, code, results, and figures have separate directories, but no contracts define independent updates. |
| may/004 | M.2 | unmet | judgement | `analysis/analyze.py#L20-L23`, `report.md#L39-L45` | No explicit module-composition mechanism is documented; the single script uses fixed workspace paths. |
| may/005 | M.2 | partial | judgement | `report.md#L23-L29`, `report.md#L37-L45` | The report points readers to input, analysis, results, and figures but offers no fuller navigation guide. |

### Extra probe finding (outside the checklist)

The license probe found no study-level reuse terms. The complete capture does contain an Apache License file at `.codex/skills/pdf/LICENSE.txt` (capture SHA-256 `4dd13869245e356246a5b770723247bbb80a8f07a181d1d3d873a1734297cdb9`), scoped by its path to the vendored PDF skill; it does not declare terms for the NARPS maps, analysis, report, or results. This is an extra finding, not a checklist item.

### Flagged items

- **must/007 — probe-overridden:** the probe looked for README/Makefile, while the complete untracked `report.md` supplies a usage command but not installation/environment-acquisition instructions; partial is retained.
- **must/008 — probe-overridden:** the probe only found tracked entrypoints; direct inspection of the complete delivery found the documented `analysis/analyze.py` route, so this item is met.
- **must/009 — mapping-questioned:** the probe scanned tracked text, while the item asks about script paths; direct inspection shows workspace-relative data and output paths in the analysis script.
- **should/001 — probe-overridden:** the tree-clean probe measures uncommitted paths; direct inspection shows Git covers supplied inputs but not the untracked code, report, and results, so this is partial across components.
- **should/008 — upstream-duplicate:** this repeats must/014 by checklist design.

### Not checked

- **should/002:** one result record and no recognized CI do not settle whether the workflow is tested regularly. A test history or repeated run record would settle it.
- **should/004 / fresh replay:** the helper never reached a fresh environment or target execution because of the assessment workdir setup error. A successful isolated run would settle this measurement.

### Goals, kind, and assumptions

The documented goal is group-level inference for a positive gain effect in vmPFC from the supplied 54 participant COPE maps, with whole-brain correction, quality checks, uncertainty, and an inspectable report (`input/study-task.md`). This is a **study**: the product is a scientific answer supported by supplied data, code, results, and figures. The goal and kind are assumptions from the supplied brief and delivery documentation; no human confirmation was attached. The study emphasis is on tracked inputs/code, result provenance, portability, and recipient access.

### Checklist link and provenance

Checklist URL: [2026-10-16-url.txt](2026-10-16-url.txt). Machine-readable item responses: [response.json](response.json). Probe receipt: [probes.json](probes.json). Replay attempt: [fresh-rerun.json](fresh-rerun.json). Access: [access-record.json](access-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the original capture `8c58f2ad4f7217840ed53d63437da4101513952d049c15d85357a0391846b75b` at captured HEAD `eece8595d255a766517e32ff10b2e6574d3c4e6a`, 2026-10-16, Codex/GPT-6. Frozen probe output: `probes.json`.
