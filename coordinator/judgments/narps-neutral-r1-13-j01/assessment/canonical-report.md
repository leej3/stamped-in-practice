# Independent assessment — NARPS Hypothesis 1

## Scientific assessment

**Scientific adequacy: qualified. Reported hypothesis outcome: not supported.** The analysis is a defensible group-stage test of the positive gain-effect hypothesis, conditional on the supplied AO86 estimates. The reported conclusion is appropriately narrow: this analysis did not find whole-brain-corrected evidence of a positive vmPFC effect; it does not show that the true effect is zero.

The protocol and implementation use the full 54-person equal-indifference cohort, match map identities to metadata and checksums, check dimensions/affines/voxel sizes and finite values, and use a common nonzero coverage mask. The one-sample equal-weight model is appropriate for participant-level estimates when variance maps are absent. A positive max-T sign-flip test across 198,029 covered voxels, with 10,000 assignments and plus-one correction, satisfies the task's whole-brain correction requirement under participant independence and sign-symmetric null errors. The independently computed t statistic at the strongest voxel is also cross-checked in the code. See [protocol](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-13-j01/content/workspace/analysis/protocol.md), [analysis code](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-13-j01/content/workspace/analysis/group_analysis.py), [summary](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-13-j01/content/workspace/results/summary.json), and [QC table](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-13-j01/content/workspace/results/participant_qc.tsv).

There were no exclusions. The summary reports 24 whole-brain max-T FWE-significant voxels in three clusters, with its strongest voxel at MNI (−26, −102, −3.6) mm (t=6.62, pFWE=0.00060), anatomically remote from vmPFC. The predeclared broad MNI coordinate locator is transparent and limited to localization, rather than being treated as a separate corrected ROI test. Within it, no voxel survived whole-brain correction; the largest uncorrected t was 3.92 at (−2, 26, −18) mm with pFWE=0.932. Its descriptive mean was −0.0075 normalized-regressor units (95% t interval −0.031 to 0.016). The figure presents unthresholded t maps, corrected contours, and participant estimates; the localization rule is coarse and not an atlas-based anatomical boundary. See [report](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-13-j01/content/workspace/report/report.md) and [figure](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-13-j01/content/workspace/figures/group_gain_effect.png).

The report correctly says these are contrast parameter estimates from a mean-centered, variance-normalized gain regressor, not a per-dollar slope or a gain-versus-loss comparison. Its uncertainty discussion covers the missing participant variance maps, equal weighting, assumptions of the permutation test, and limits of the fixed upstream model. Those caveats qualify the population interpretation; no material error in the group inference was identified. The absence of corrected vmPFC evidence is not an equivalence test and does not rule out smaller effects.

The task asks for the hypothesis outcome separately from adequacy: **the positive vmPFC hypothesis is not supported by the reported analysis**. This is a conclusion about evidence in the supplied maps and model, not proof of no biological response. A replay did not run; that does not change this assessment of the shipped analysis and outputs.

## Replay and capture integrity

Replay was declared before execution in [replay plan](replay-plan.md), with the exact documented command, prerequisites, eight generated outputs, comparison rules, and frozen limits. One frozen-helper attempt was made. It stopped before creating a replay copy or starting the scientific command because exact capture validation found an unexpected file list. After the initial complete-capture validation, Git inspection of the retained workspace was followed by two unexpected SQLite sidecars under `.git/annex/keysdb/` (`db-shm` and `db-wal`). I did not remove or otherwise repair them and did not retry. This is an assessor-caused state change, not worker behavior or target-pipeline behavior. The exact adapter invocation is retained in [replay-command.txt](replay-command.txt); its failure is retained in [stdout](replay-runner.stdout) and [stderr](replay-runner.stderr). The [replay record](replay-record.json) and [capture mismatch observation](capture-mismatch-observation.txt) mark replay not checked and document the exact list difference. The failure occurred before the helper created its formal attempt marker.

At first validation, the delivery manifest hash matched the worker-stop receipt, and the complete capture reported zero omissions/errors. The later mismatch limits claims about the target's current byte-for-byte integrity. Scientific evidence above was inspected before the sidecars appeared; the two unexpected paths are annex metadata, not scientific outputs. Validation stopped at the file-list mismatch and did not re-hash every retained payload, so full post-inspection integrity remains unavailable. The stop receipt records worker exit code 0 at 2026-10-16 06:53:47 UTC. Its declared inputs and captured state are distinct from later coordinator preservation. No external `.git` pointer or original absolute target was followed. The external skill links listed in `judge-target.json` `reference_limits` were not followed.

**Exposure note:** The captured commit metadata and session logs identify Codex assistance. I record that exposure but do not use it as grading evidence or infer any treatment assignment.

## STAMPED assessment

**Assumed goal and kind (not confirmed):** the delivered object is a study whose product is a scientific answer with code, fixed inputs, derived results, figures, and report. This follows the supplied task and the worker's report. The study kind emphasizes complete inputs and traceable results.

**MUST:** 7 met / 3 partial / 7 unmet / 0 not-checked (17 total). **SHOULD:** 0 met / 2 partial / 6 unmet / 0 not-checked / 1 not-applicable (9 total). **MAY:** 4 met / 1 partial / 0 unmet / 0 not-checked / 0 not-applicable (5 total). `Partial` does not satisfy a MUST. No overall score is assigned. The per-item table below is generated from the validated [response JSON](2026-10-16-response.json); automated results are retained in [probes](2026-10-16-probes.json).

### What to address first

1. Add and track an environment specification with a usable install/reproduction route, then test that route. This is the main barrier to another researcher recreating the exact group result and environment (must/003, 006, 010, 012–017; should/006–008).
2. Track the analysis code, protocol, report, figures, and results at the worker stop. Those are the scientific product, while the stop-state Git status showed them all untracked (must/004; should/001).
3. Publish an authorized retrieval route that covers the full object and environment. No worker-declared route was available to test, and the coordinator's delivery to the assessor is not evidence of worker publication (must/016). See [access record](access-record.json).

### What is already in good shape

- The 54 source maps are present as git-annex content, with source IDs and checksums recorded in `input/sources.json` (must/005).
- The analysis has a documented start point and ROOT-relative paths; the report explains the estimand, whole-brain correction, localization and limits (must/008–009; [README](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-13-j01/content/workspace/analysis/README.md)).
- Data checks, participant-level QC, protocol, summary, statistical maps and an informative figure make the scientific choices inspectable ([protocol](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-13-j01/content/workspace/analysis/protocol.md), [QC](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-13-j01/content/workspace/results/participant_qc.tsv), [figure](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-13-j01/content/workspace/figures/group_gain_effect.png)).

### Per-item response

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `judge-target.json` | The complete object is rooted in one workspace containing input, analysis, results, figures, and report. |
| must/002 | S.1 | met | judgement | `analysis/group_analysis.py`, `input/sources.json` | All 54 maps and metadata are inside the workspace; code resolves inputs relative to its root and annex links stay inside the captured repository. |
| must/003 | S.1 | unmet | judgement | `analysis/group_analysis.py`, `probe:env-spec-tracked` | The script imports NumPy, pandas, nibabel, SciPy, and Matplotlib, but the delivery has no environment declaration or linked software modules. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-13/judgments/narps-neutral-r1-13-j01/attempt-01/worker-end-state.json`, `stop-state-observation.txt` | Git contains the supplied inputs, but the worker analysis, report, figures, and results were untracked at stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data/sub-001_hypo1_cope.nii.gz`, `2026-10-16-probes.json` | The 54 input maps are git-annex payloads referenced by tracked links; map bytes are retained in the captured annex store. |
| must/006 | T.1,T.3,T.5 | unmet | judgement | `results/summary.json`, `analysis/README.md` | The summary records package versions and platform, but no exact environment specification is linked to the generated results. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `analysis/README.md`, `report/report.md#Reproduction` | The untracked analysis README and report explain usage, but they do not explain how a recipient installs or obtains the prepared environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analysis/group_analysis.py`, `analysis/README.md` | analysis/group_analysis.py is the runnable starting point documented in the analysis README, protocol, and report. |
| must/009 | P.1 | met | judgement | `analysis/group_analysis.py` | The analysis script derives all data and output paths from its own location; no host-specific paths are embedded in code. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analysis/group_analysis.py`, `2026-10-16-probes.json` | No delivered environment specification declares the imported Python dependencies or their versions. |
| must/011 | P.1 | met | judgement | `results/summary.json`, `report/report.md#Reproduction` | The result summary records Python, package versions, and macOS arm64 platform; the report identifies the prepared Python runtime. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/summary.json`, `analysis/README.md` | The summary lists Python and imported package versions, but there is no reader-facing system requirements or installation specification. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `2026-10-16-probes.json` | No environment specification is present in the worker delivery or its Git-tracked files. |
| must/014 | P.3 | unmet | judgement | `analysis/README.md, analysis/protocol.md` | No dependency-update or environment-regeneration process is documented or tracked. |
| must/015 | D.1 | unmet | judgement | `results/summary.json`, `judge-target.json` | The delivery records versions but does not include frozen package resolution or an environment artifact to reproduce that runtime. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `access-record.json` | No worker-published route or environment specification is available; local Git has no remote and checkpoint pushing is disabled. |
| must/017 | D.1 | unmet | judgement | `report/report.md#Reproduction`, `analysis/protocol.md#Reproducibility` | The report names a prepared absolute interpreter path, but gives no way for a recipient to obtain the environment specification or recreate it. |
| should/001 | T.2 | partial | judgement | `stop-state-observation.txt` | Git-annex stores input payloads, while all worker-produced code, results, figures, and report were untracked at stop. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `2026-10-16-probes.json`, `analysis/README.md` | No CI, recurring test record, or documented repeated check of the execution instructions is included. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `2026-10-16-probes.json`, `analysis/README.md` | Input data and analysis/results are in separate directories, but code, generated products, and environment are not independent modules. |
| should/004 | E.1 | unmet | judgement | `judge-target.json` | No fresh container, batch job, clean VM, or cloud execution record is included. |
| should/005 | E.1 | unmet | judgement | `analysis/group_analysis.py` | The script writes to fixed results/ and figures/ directories and does not create a disposable environment per run. |
| should/006 | D.2 | unmet | judgement | `judge-target.json`, `2026-10-16-probes.json` | No exact environment specification or reconstitution test is present in the delivery. |
| should/007 | D.2 | unmet | judgement | `judge-target.json` | No environment files, packages, binaries, or container artifacts are archived with the project. |
| should/008 | D.2 | unmet | judgement | `analysis/README.md, analysis/protocol.md` | No process for updating dependencies or tracking corresponding environment changes is documented. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the supplied public participant maps and software are not access-restricted components. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `input/data` | Input maps are a separately bounded external dataset: sources.json records per-map NeuroVault URLs, IDs, and checksums, with payloads retained in git-annex. |
| may/002 | M.2 | met | judgement | `analysis/README.md` | The analysis README describes input, analysis, results, and figure relationships. |
| may/003 | M.2 | partial | judgement | `analysis/README.md` | Inputs and analysis have distinct directories, but outputs share the workspace and no independent environment boundary exists. |
| may/004 | M.2 | met | judgement | `analysis/group_analysis.py`, `report/report.md#Reproduction` | The documented Python entrypoint reads the supplied input module and creates the listed results and figure. |
| may/005 | M.2 | met | judgement | `analysis/README.md`, `analysis/protocol.md` | The analysis README and protocol explain the directories, entrypoint, and main outputs. |


### Flagged items

- **must/004:** the tree-clean probe treats untracked files as unmet; the checklist asks whether version control is used for project text/code. Inputs are versioned but the worker's scientific deliverables are not, so partial is more accurate.
- **must/007:** the filename-oriented entry-point probe did not recognize `analysis/README.md`; manual review finds usage instructions, but no way to install or obtain the prepared environment, so the item is partial.
- **must/008:** the filename-oriented entry-point probe did not recognize the documented `analysis/group_analysis.py`, which is a clear runnable start point.
- **must/016:** the environment-spec probe cannot establish publication. The local Git remote list was empty and the only captured checkpoint setting has `push_sessions=false`; no authorized worker route was demonstrated.
- **should/003:** the module probe recognized input separation only. Manual review also considered analysis and outputs; no independent environment module exists, so partial remains.
- **should/008:** repeats the environment-update question in must/014; answer intentionally duplicates it.
- **may/001:** the subdataset probe found no Git submodules, but the input dataset is independently identified and retrievable through per-map NeuroVault URLs in `input/sources.json`, with content retained in git-annex.

The extra `license-declared` probe also found no reuse license in the delivered tree; this finding has no checklist item.

### Not checked

- **Replay of scientific outputs:** the single attempt was blocked before execution by the assessment-caused capture-list mismatch. A clean, unchanged delivery copy would settle it; no repaired or second attempt was made.
- **Worker publication/access:** no worker-declared retrieval endpoint was available to test. A declared authorized route plus recipient-side retrieval of all required artifacts would settle it. Anonymous access was not required or tested.
- **Current full-capture integrity after inspection:** two unmanifested annex SQLite sidecars prevent a fresh exact-tree validation. The original source was not repaired.

### Recipient and access scope

The intended recipient is a researcher using a worker-declared authorized route. No such route was available. The captured Git configuration had no remote; `.entire/settings.local.json` names a GitHub checkpoint repository but disables session pushing. Required coverage is analysis/protocol, all 54 maps and metadata, an environment specification/runtime, generated results/figures, and report. No endpoint or recipient account was tested; scope is the local captured workspace. Anonymous access was not tested. See [access record](access-record.json).

### Checklist, response, and provenance

Checklist link: [open the completed STAMPED checklist](2026-10-16-url.txt).

Response: [2026-10-16-response.json](2026-10-16-response.json). Probes: [2026-10-16-probes.json](2026-10-16-probes.json). Replay: [replay-record.json](replay-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the retained NARPS study at commit `8a84ddc3eec68d0b7513f9a15ce37174288b36b7`, 2026-10-16, con-duct run 0.23.0 / gpt-6-luna. The manifest SHA-256 is `4cb6043b8fa2409c631a8c49a0b0b5ea0feec21e0162f4e924f9c08d1be8939f`; its complete original file list matched the worker-stop receipt before the assessor-caused sidecars. Probe output: `2026-10-16-probes.json`.

