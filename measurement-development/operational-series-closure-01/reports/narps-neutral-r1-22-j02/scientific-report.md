# Independent assessment — NARPS Hypothesis 1

Assessment date: 2026-10-16 (UTC). This report assesses the complete worker-stop capture, including uncommitted and ignored files. Citations to target artifacts below use capture-relative paths within `content/workspace`; their identity is canonical capture SHA-256 `62844be8e123ee4970d90409a641082a3126743ee3b90d914b2b5ef26a50aaf1`.

## STAMPED verdicts

MUST: 3 met / 1 partial / 13 unmet / 0 not-checked (17 total). SHOULD: 1 met / 1 partial / 4 unmet / 3 not-checked (9 total). MAY: 1 met / 1 partial / 3 unmet / 0 not-checked (5 total). No overall score is assigned.

## Scientific assessment

**Scientific adequacy: qualified.** The delivered analysis supports its reported conclusion that these supplied maps do not establish a positive vmPFC association under whole-brain FWE correction. The result is conditional on the supplied participant estimates and has important spatial and uncertainty limits described below.

Hypothesis conclusion (verbatim): In the 54-person NARPS equal-indifference group, the supplied gain-effect maps do **not** support a positive gain association in vmPFC under whole-brain family-wise error (FWE) correction.

The worker used 54 independent participant gain-effect maps and an unweighted one-sample t model, appropriate to the supplied contrast estimates and the absence of participant variance maps. `analyze.py` verifies the cohort IDs, per-image source hashes, common shape and affine; it excludes no participant. The mask requires at least 49/54 nonzero maps, finite values in every map, and overlap with a standard brain mask. The code uses 5,000 seeded sign flips and the maximum positive t over 192,339 voxels for one-sided whole-brain FWE inference. This directly addresses the required correction and does not substitute an uncorrected ROI test. The report identifies bilateral AAL3v2 `Frontal_Med_Orb` as an explicit anatomical proxy for vmPFC and keeps the ROI summary descriptive.

The delivered `results/summary.json` reports a proxy mean of −0.00795 supplied units, descriptive 95% t interval [−0.03455, 0.01864], zero proxy voxels surviving whole-brain correction, and 23 corrected voxels in three posterior-inferior foci. The report does not treat those foci as vmPFC evidence. It correctly states that these are not effects per currency unit because the upstream gain regressor was variance-normalized, that the result depends on the fixed separate gain/loss first-level model, and that absence of corrected support is not proof of zero or absence of any neural correlate.

The qualification reflects limitations that the report itself recognizes: sign flipping assumes symmetric participant effects under the null; participant variance maps are unavailable; the descriptive ROI interval is not an equivalence test; and MNI152NLin2009cAsym maps are compared with a standard mask/AAL atlas on a different template without a reported nonlinear transform. Direct nearest-neighbor resampling makes the parcel reproducible, but does not remove this anatomical localization uncertainty. The supplied output and code are internally coherent on inspection; replay was not checked because the only documented interpreter is outside the captured project, so computational reproduction was not independently measured. These limits qualify the inference without identifying a material error in the reported negative result.

Scientific evidence cited above (each path relative to the captured workspace): `REPORT.md` SHA-256 `87a86bc213b9e8157957666a1263c32249e4ff4ae5d2a677a115aaf89c743248`; `analyze.py` SHA-256 `abb28e87b1d03c0d7bcd8effac1bb9afa785fe5004a44ff7e31d017e91790dac`; `results/summary.json` SHA-256 `a49299fd75aa0baa130921e207d3e14aa5ca0dd3e7063e2d31203e45219d5e06`; `results/fwe_clusters.tsv` SHA-256 `d915de3f71444a3204c0244acc2e603a7c9afd750cf448353b521e952e341a54`; `results/participant_qc.tsv` SHA-256 `56c47f07b9c54e22be299171c7fdaf13c294ab273a31863b066f8d995853ef47`. Each is bound to canonical capture SHA-256 `62844be8e123ee4970d90409a641082a3126743ee3b90d914b2b5ef26a50aaf1`.

## What to fix first

1. Add a project-local, pinned environment and portable installation/run instructions → makes the delivered entrypoint usable and its assumptions inspectable → must/001, 003, 007, 009–017.
2. Track the worker's report, analysis script and generated results in the worker stop state, and record a run manifest linking code, inputs, outputs and exact environment → preserves the work and makes its provenance auditable → must/004, 006; should/001.
3. Document/validate spatial mapping from MNI152NLin2009cAsym into the chosen standard mask and atlas, and keep the ROI localization sensitivity visible → strengthens vmPFC localization → scientific qualification.
4. Add a documented repeated/fresh-environment check once a reproducible environment exists → determines whether the documented route works across runs → should/002, 004, 006.

## What the project already does well

- The complete stop includes all 54 supplied maps, cohort metadata, source checksums, a group-analysis script, numeric outputs and two figures; the input hashes and participant mapping are checked in code (`analyze.py`, `input/sources.json`).
- Whole-brain max-T FWE correction is implemented for the positive-direction hypothesis, with the permutation count, seed, threshold, mask rule and cluster summaries recorded (`analyze.py`, `results/summary.json`, `results/fwe_clusters.tsv`).
- The report distinguishes the supplied coefficient scale from currency units and describes uncertainty and the limits of a null finding (`input/upstream-methods.md`, `REPORT.md`).

## Per-item findings

The table below gives each pinned item, its verdict, evidence path and concise reason. Hashes for each target evidence file are in the machine-readable response JSON; all target hashes are anchored to the canonical capture SHA-256 above.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | unmet | judgement | `REPORT.md` | The delivered command depends on a user-specific interpreter outside the common root. |
| must/002 | S.1 | met | judgement | `analyze.py`, `input/sources.json` | All 54 required effect maps and cohort metadata are supplied under input and connected to the analysis. |
| must/003 | S.1 | unmet | judgement | `REPORT.md`, `analyze.py` | Python packages are named, but no environment file includes or installs them. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json`, `.git/HEAD`, `analyze.py` | Git tracks supplied inputs, but the worker analysis, report and generated results remained uncommitted at stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex+judgement | `.git/config`, `.git/annex`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json` | git-annex pointers and local annex content preserve the large participant maps. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `results/summary.json`, `REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json` | The shipped results have no run record linking their generation to a captured exact environment. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `REPORT.md` | The report gives a run command but no installation instructions or usable environment setup. |
| must/008 | A.1 | met | probe:entry-point+judgement | `REPORT.md`, `analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json` | The complete stop includes analyze.py and the report names it as the reproduction entrypoint. |
| must/009 | P.1 | unmet | probe:no-abs-paths+judgement | `REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json` | The documented reproduction command contains a host-specific absolute path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `REPORT.md`, `analyze.py` | No complete dependency specification declares package versions or the Python runtime. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json` | The external interpreter path is host-specific, while OS/runtime assumptions are undocumented. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `REPORT.md` | Package names appear in prose, but system/runtime requirements and installation dependencies are not specified. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `.git/HEAD`, `REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json` | No environment specification is tracked with the committed project state. |
| must/014 | P.3 | unmet | probe:env-spec-tracked+judgement | `REPORT.md` | No command or process for updating environment specifications is provided. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/summary.json`, `REPORT.md` | No frozen package manifest or exact environment identity accompanies the results. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json` | No environment specification is present to share; the documented interpreter is outside the captured project. |
| must/017 | D.1 | unmet | judgement | `REPORT.md` | Users are not told how to obtain or reconstruct the external environment. |
| should/001 | T.2 | partial | probe:tree-clean+judgement | `.git/config`, `analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json` | Git and git-annex cover supplied inputs, but the analysis code and results are uncommitted. |
| should/002 | A.2 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json` | The delivery has no regular-testing record; worker-authored repeated-run evidence would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `analyze.py`, `REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json` | Inputs, code and results occupy separate directories, but no environment module is provided. |
| should/004 | E.1 | not-checked | judgement | `REPORT.md`, `replay-record.json` | No fresh-environment run is recorded; replay was unsafe because its only interpreter is outside the captured delivery. |
| should/005 | E.1 | unmet | judgement | `REPORT.md` | The documented command reuses a fixed user-level Pixi environment rather than creating a disposable one. |
| should/006 | D.2 | unmet | probe:env-spec-tracked+judgement | `REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json` | There is no environment specification whose reconstitution is tested. |
| should/007 | D.2 | unmet | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/probes.json`, `REPORT.md` | No environment image, binary environment or package lock is archived with the project. |
| should/008 | D.2 | unmet | probe:env-spec-tracked+judgement | `REPORT.md` | No environment update process is stated or tracked. |
| should/009 | M.4 | not-checked | judgement | `input/sources.json` | Source URLs are public, but the delivery does not state data/software reuse restrictions; terms are needed to determine whether any component is restricted. |
| may/001 | M.2 | met | judgement | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/logs/access-neurovault.stdout.txt`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-22-j02/attempt-01/judgment/logs/access-github.stdout.txt` | The external AO86 map collection and pinned cohort table are individually identified and retrievable by source URLs. |
| may/002 | M.2 | unmet | judgement | `REPORT.md` | Directories separate data and results, but no modular relationships or recombination guidance are documented. |
| may/003 | M.2 | unmet | judgement | `analyze.py` | There are no independently updateable module boundaries or interfaces. |
| may/004 | M.2 | unmet | judgement | `analyze.py` | One script executes the analysis; no mechanism composes separate modules. |
| may/005 | M.2 | partial | judgement | `REPORT.md` | The report explains key outputs, but offers no broader module navigation guide. |


## Scientific evidence detail and scope

The task concerns the equal-indifference cohort only. Inputs report MNI152NLin2009cAsym effect estimates averaged over runs; they are not standardized test statistics. The task methods say gains spanned twice the loss range, but the gain coefficients are not currency-scaled. Accordingly, the group test is about the supplied gain coefficient conditional on the upstream model, not a per-dollar response or causal gain manipulation effect. The nonzero-coverage threshold and all-finite requirement are visible in code; the participant QC file contains 54 rows, all with finite fraction 1.0. No exclusion was made. The max-T Monte Carlo test controls voxelwise whole-brain FWE over the stated mask, subject to sign-flip symmetry and finite Monte Carlo resolution. The proxy mean interval includes zero and does not establish equivalence or rule out small positive or spatially heterogeneous effects.

## Worker stop state, attribution and integrity

The worker stop receipt `worker-end-state.json` (SHA-256 `cac1a272faf44f4e459f21af394256880b4c98e91e94a44b6939cc92cba45c83`) records a complete, successful stop at 2026-10-16T06:59:04Z, with original HEAD `8a84ddc3eec68d0b7513f9a15ce37174288b36b7`. The same HEAD is present in the operational copy. At that stop, `REPORT.md`, `analyze.py`, `atlas_cache/` and `results/` were untracked. They are valid scientific artifacts in this complete delivery but do not count as worker Git tracking. The HEAD commit tracks supplied inputs and annex pointers; it is not the whole scientific delivery.

The captured HEAD commit message (`.git/COMMIT_EDITMSG`) includes a Codex Desktop co-author attribution. This assistance exposure is recorded without using it as evidence for scientific quality or checklist attainment. Coordinator preservation and this assessment's later inspection are not worker practices.

The canonical and initial operational manifests have the same SHA-256 (`62844be8e123ee4970d90409a641082a3126743ee3b90d914b2b5ef26a50aaf1`) and matching entries. The post-inspection comparison found no integrity-invalidating target changes. It found a changed regular `.git/annex/keysdb/db` and newly present regular `.git/annex/keysdb/db-shm` and `db-wal`; these are classified as operational metadata under the supplied rule, likely from annex inspection. Logical database equivalence is not established. No links, source files, index, refs, objects or configuration were repaired or changed. `judge-target.json` declares no reference limits, so no retained links or external Git pointers were followed.

## Access record

The intended recipient is a researcher authorized to use the declared public source-data routes. The worker declared no project Git remote or complete-project publication route at stop (`.git/config` has no remote). `input/sources.json` maps the 54 maps to NeuroVault URLs and the cohort table to a pinned raw GitHub URL. HEAD checks returned HTTP 200 for one representative NeuroVault map on `neurovault.org` and for the cohort table on `raw.githubusercontent.com`; this tests those two hosts and two URLs only. It does not prove that all 54 URLs work or that the worker made the report, code, results, atlas cache or environment available. The coordinator's delivery to the assessor is not worker publication. Full details and captured command output are in `access-record.json` and `logs/access-*.stdout.txt`.

## Replay record

Replay status is **not checked**; no attempt was launched. The worker's documented command is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analyze.py`. That interpreter is outside the complete capture, and there is no supplied environment declaration from which to reconstruct it. Substituting another interpreter or adding dependencies would alter the documented workflow. The planned explicit outputs were `results/group_mask.nii.gz`, `mean_effect.nii.gz`, `t_statistic.nii.gz`, `p_fwe_maxT.nii.gz`, `vmPFC_proxy_aal3.nii.gz`, `participant_qc.tsv`, `summary.json`, `fwe_clusters.tsv`, `vmPFC_proxy_effects.png` and `wholebrain_fwe_map.png` (under `results/`). `input/**`, `analyze.py` and `atlas_cache/**` would be protected in a separate complete-delivery copy. The declared numeric comparison tolerance was relative `1e-6`; no outputs were compared. The execution limit was 7,200 seconds with no input prefetch. `replay-record.json` preserves the decision and comparison plan.

## Flagged items

- **must/004 and should/001 (`mapping-questioned`):** `tree-clean` measured uncommitted paths; the item asks whether version control covers the file types. Git tracks supplied inputs, while worker code, report and results are not committed, so the verdict is partial.
- **must/005 (`mapping-questioned`):** the probe cited `.datalad/config`, but the actual captured mechanism is Git-annex metadata/pointers.
- **must/008 (`probe-overridden`):** the entrypoint probe looked at tracked paths; the complete stop includes untracked `analyze.py` and a report command.
- **must/009 (`probe-overridden`):** the no-absolute-path probe scanned tracked text and missed untracked `REPORT.md`'s host-specific command.
- **should/008 (`upstream-duplicate`):** duplicates must/014's environment-update-process question.

## Not checked

- **should/002:** worker-authored CI or repeated workflow-validation records would establish regular testing.
- **should/004:** a safe fresh-environment replay requires a worker-supplied/reconstructible environment and the documented entrypoint's actual prerequisites.
- **should/009:** an explicit license/restriction declaration is needed to decide whether any data/software belongs in a restricted module.
- **Replay:** not checked for the external interpreter prerequisite described above; no scientific execution or output comparison occurred.

## Goals and kind

Assumption (not confirmed with a human): this object is a **study** whose product is a group-level scientific answer from supplied participant maps. The goal comes from `input/study-task.md` and `REPORT.md`. The scientific criteria come from the retained coordinator rubric; no assignment or prior-worker answer was used. As a study, the assessment emphasizes complete inputs, linkage of code/actions/results to an environment, and retrievability of the delivered work.

## Checklist and provenance

Checklist link: [open the filled STAMPED checklist](2026-10-16-url.txt). Full item responses and evidence hashes: [2026-10-16-response.json](2026-10-16-response.json). Raw probe output: [2026-10-16-probes.json](2026-10-16-probes.json). Replay decision: [replay-record.json](replay-record.json). Access check: [access-record.json](access-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on canonical capture `62844be8e123ee4970d90409a641082a3126743ee3b90d914b2b5ef26a50aaf1`, 2026-10-16, Codex / GPT-6. Probe output: `2026-10-16-probes.json`. The frozen assessment runtime was used for probe, response and validation actions.
