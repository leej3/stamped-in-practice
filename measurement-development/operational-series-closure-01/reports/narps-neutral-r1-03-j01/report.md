# Independent assessment

**Object:** study workspace at worker stop, 2026-10-16. **Canonical capture SHA-256:** `b321a85c15f4ada27df7bfdb1a8ac1083c4cf328f8db985598daefa0c322444f`. **Captured HEAD:** `d857ab1302d13cb660a7a044af07141f44bfa9ba`. **Capture status:** complete, no manifest errors or omissions. The worker stop receipt is retained at `worker-end-state.json` (SHA-256 `2d6b098f70edec77b7994f1bc00a9ec902dc6a1c324607c6b5c0572584e1cb68`). All original-object citations below use this canonical capture digest and a capture-relative path. Workspace-relative paths in citations and the item table resolve under `content/workspace/` in the capture; for example, `analysis/report.md` denotes `content/workspace/analysis/report.md`.

## Scientific judgment

Scientific adequacy: supported.

The reported outcome is that the supplied inputs do not provide corrected support for a positive vmPFC gain effect. The worker states: “In the 54-person NARPS equal-indifference group, these gain-effect estimates did **not support a positive vmPFC response to increasing potential gain**.” [capture `b321a85c15f4ada27df7bfdb1a8ac1083c4cf328f8db985598daefa0c322444f`: `analysis/report.md`, lines 7–11]

This is a defensible absence-of-positive-finding conclusion, not a claim that the true effect is exactly zero. The script analyzes all 54 equal-indifference participant maps as independent observations, validates geometry and finite values, and uses a common-support mask so out-of-coverage zeros are not treated as measurements. It tests a positive one-sample group effect and controls whole-brain familywise error with Bonferroni adjustment over 198,029 voxels. The report transparently operationalizes vmPFC as a 12-mm MNI sphere centered at (0, 40, −10), then requires corrected whole-brain support in that location. No sphere voxel survived correction; its mean was −0.0055 cope units, with a 95% interval spanning −0.0309 to 0.0199. Eleven corrected positive voxels were posterior to the target region. These numerical results and choices are documented in [capture `b321a85c15f4ada27df7bfdb1a8ac1083c4cf328f8db985598daefa0c322444f`: `analysis/report.md` and `results/summary.json`].

The supplied estimates are unthresholded participant cope values, not test statistics or change per currency unit. The report accounts for upstream gain-modulator normalization, fixed participant-level modeling and the absence of variance maps. Equal-weight one-sample inference is defensible for these fixed inputs; its limits (first-level precision, model assumptions and sample-level inference) are stated. A non-significant local result does not establish a zero effect. No atlas, mask or particular software is necessary for the accepted conclusion.

The documented script and generated summary, QC table, maps and figures were replayed once from a fresh copy of the canonical complete delivery. The frozen helper reports byte-identical reproduction of all seven selected artifacts, with no retrieval, repair or timeout. The replay validates these artifacts on the available host environment; it is not worker execution evidence. See `replay-plan.json`, `replay-record.json`, and `replay-work/replay.stdout` / `replay-work/replay.stderr`.

## Delivery boundary, attribution and integrity

The operational copy began byte-identical to the canonical manifest. Final comparison found no change to worker evidence outside the specifically permitted annex database metadata: `.git/annex/keysdb/db` changed, and regular files `.git/annex/keysdb/db-shm` and `db-wal` appeared during inspection. These are operational metadata under the supplied rule; no logical database equivalence is claimed. No other missing, altered or extra target paths were found. Annex data links retained their original relative targets. The frozen replay helper independently revalidated the canonical manifest before and after replay.

At worker stop, Git HEAD was the recorded `d857ab1302d13cb660a7a044af07141f44bfa9ba`. The 54 input pointers were tracked through git-annex, while `.codex/`, `analysis/`, and `results/` (including the analysis, report and scientific outputs) were untracked. No Git remote was configured. The report names an absolute local prepared-environment interpreter and package versions, but the delivery contains no environment lock/specification or worker-declared publication route. The recipient is a researcher using a declared authorized route; no such route to the report, code, results or environment was established or tested. The source links in `input/sources.json` cover upstream input provenance, not access to the worker's analysis package. Anonymous access was not required. Coordinator preservation/delivery to this assessor and the successful evaluator-host replay do not establish worker sharing.

The capture contains Codex configuration/skills and `.entire` session metadata indicating AI-assisted work and skill installation. That exposure is disclosed and was not used as STAMPED attainment evidence or scientific grading evidence. During assessment, I also opened the coordinator procedure file by mistake while locating helper requirements; it contained cross-run assignment metadata. No assignment was inferred or used, and that file is excluded from all grading. No treatment assignment is reported.

## STAMPED item attainment

The supplied frozen probes were run on the operational copy. Their machine-readable output is `probes.json`; a probe result was retained only where it answered the actual item. In particular, the entry-point probe recognizes README/Makefile patterns, so I also assessed the report's equivalent instructions directly. `response.json` contains all 31 pinned item verdicts and citations. The frozen checklist validator and URL encoder were used after review. There is no overall score.

- MUST: 5 met, 5 partial, 7 unmet, 0 not-checked.
- SHOULD: 0 met, 2 partial, 4 unmet, 2 not-checked, 1 not-applicable.
- MAY: 4 met, 0 partial, 0 unmet, 0 not-checked, 1 not-applicable.

Key gaps are the absent delivered environment specification and worker sharing route; scientific code, report and results were not tracked at worker stop. The analysis itself is clearly described and scientifically defensible, and the full capture retains the data and generated artifacts.

### Checklist URL and records

- Checklist URL: see [`checklist-url.txt`](checklist-url.txt).
- Canonical response: [`response.json`](response.json).
- Item table: [`response-table.md`](response-table.md).
- Access record: [`access-record.json`](access-record.json).
- Replay plan and result: [`replay-plan.json`](replay-plan.json), [`replay-record.json`](replay-record.json).
- Scientific record: [`scientific-judgment.json`](scientific-judgment.json).

## Provenance

Produced with the frozen STAMPED assessor identified in `assessment-version.json`, checklist 0.3.1, against the complete stop-state capture above. Probe output: `probes.json`. Assessment and generated records are outside the assessed object.

## Per-item table

For each capture-relative citation in the table, the canonical original capture SHA-256 is `b321a85c15f4ada27df7bfdb1a8ac1083c4cf328f8db985598daefa0c322444f`; the response JSON records that digest and evidence path for each source artifact.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `analysis/report.md` | The complete object is contained under the captured workspace root. |
| must/002 | S.1 | met | judgement | `analysis/group_analysis.py`, `input/upstream-methods.md` | The analysis resolves all cohort data and fixed inputs through paths under the workspace. |
| must/003 | S.1 | unmet | judgement | `analysis/report.md` | No delivered environment declaration installs or links the external software dependencies. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `analysis/group_analysis.py`, `analysis/report.md`, `results/summary.json`, `commands/operational-status.stdout.txt` | Git tracks supplied inputs, but the worker analysis, report and results were untracked at stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data/sub-001_hypo1_cope.nii.gz`, `probes.json` | All 54 large participant maps are managed through git-annex in the captured workspace. |
| must/006 | T.1,T.3,T.5 | unmet | judgement | `analysis/report.md`, `results/summary.json` | The stop-state delivery has no provenance record binding generated results to an exact environment specification. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `analysis/report.md`, `probes.json` | The report provides a usage command but does not explain how to obtain/install its external prepared environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analysis/report.md`, `analysis/group_analysis.py` | The report identifies a clear runnable analysis script and command. |
| must/009 | P.1 | met | probe:no-abs-paths | `analysis/group_analysis.py` | The analysis script resolves its inputs and outputs relative to its own location. |
| must/010 | P.1 | unmet | judgement | `analysis/group_analysis.py`, `analysis/report.md` | The complete delivery has no environment specification covering all required software. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `analysis/report.md` | The report exposes a host-specific absolute interpreter path but does not document a portable host/platform requirement set. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `analysis/report.md` | The report lists Python package versions, but does not provide a complete installable dependency and system-requirements list. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `analysis/report.md`, `probes.json` | No environment specification is present in the version-controlled worker state. |
| must/014 | P.3 | unmet | probe:env-spec-tracked | `analysis/report.md`, `probes.json` | No process for updating environment specifications is declared or tracked. |
| must/015 | D.1 | unmet | judgement | `analysis/report.md`, `results/summary.json` | Package names and versions do not identify the exact environment used to make these results. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `analysis/report.md`, `commands/operational-status.stdout.txt` | No worker-published or otherwise declared route provides an environment specification to the intended researcher. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `analysis/report.md`, `probes.json` | The report explains how to invoke the analysis but not how a researcher obtains its named environment. |
| should/001 | T.2 | partial | judgement | `analysis/group_analysis.py`, `results/summary.json`, `commands/operational-status.stdout.txt` | Git is used for supplied data, while the new code, report and results were outside version control at worker stop. |
| should/002 | A.2 | not-checked | probe:ci-present | `probes.json` | No recognized CI configuration was found; an equivalent worker-run testing schedule could not be established from admissible evidence. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `analysis/report.md`, `probes.json` | Inputs, analysis code and derived results have separate directories; environment definitions are not a delivered module. |
| should/004 | E.1 | not-checked | judgement | `probes.json` | The worker delivery does not establish whether the pipeline was tested in a fresh container, batch job, VM or cloud instance. |
| should/005 | E.1 | unmet | judgement | `analysis/report.md`, `analysis/group_analysis.py` | The documented workflow invokes Python directly and does not create a disposable environment for each run. |
| should/006 | D.2 | unmet | probe:ci-present | `analysis/report.md` | No exact environment specification exists to be regularly tested for reconstitution. |
| should/007 | D.2 | unmet | probe:env-spec-tracked | `probes.json`, `analysis/report.md` | No environment artifacts are archived in the worker delivery. |
| should/008 | D.2 | unmet | probe:env-spec-tracked | `analysis/report.md` | No dependency-update process is declared or tracked. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: no restricted data or software component is identified in the delivered object. |
| may/001 | M.2 | not-applicable | judgement | `input/sources.json` | N/A: no independently maintained external project module is part of this object; ordinary packages and annexed files are not such modules. |
| may/002 | M.2 | met | judgement | `analysis/report.md` | The report explains how the fixed input module, group-analysis script and results relate. |
| may/003 | M.2 | met | judgement | `analysis/group_analysis.py`, `analysis/report.md` | The input, analysis and results directories give separable boundaries for data, code and derived outputs. |
| may/004 | M.2 | met | judgement | `analysis/report.md` | A single documented script composes the supplied inputs into the reported group outputs. |
| may/005 | M.2 | met | judgement | `analysis/report.md` | The report provides links and paths that let a reader navigate inputs, analysis and results. |

### Flagged probe judgments

`must/007` and `must/008` override the entry-point probe's filename-only reading: the report is an equivalent user instruction and identifies the script, although environment acquisition is incomplete. `must/011` overrides the platform probe after direct review: the report names a host-specific absolute interpreter but does not document broader host assumptions. `should/003` uses the probe's finding of a separate input directory and the report/code evidence for separate analysis and results; environment definitions remain absent.

### Not checked

- `should/002`: no recognized CI file was found; whether a manual/scheduled testing process exists could not be established from admissible evidence. A worker-maintained test record or recurrent job history would settle it.
- `should/004`: no admissible evidence establishes a fresh container, batch, VM or cloud test. A worker-run record tied to such an environment would settle it.
