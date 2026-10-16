# Independent assessment — NARPS equal-indifference study

**STAMPED verdicts:** MUST: 5 met / 1 partial / 11 unmet / 0 not-checked (17 total). SHOULD: 1 met / 1 partial / 4 unmet / 2 not-checked / 1 not-applicable (9 total). MAY: 4 met / 1 partial / 0 unmet / 0 not-checked / 0 not-applicable (5 total). These are item attainments, not a score.

**Scientific adequacy: supported.** The reported lack of whole-brain-corrected vmPFC support follows a suitable one-sample group analysis of all 54 maps and a positive, whole-brain max-T permutation test. The report states what the COPEs measure, gives uncertainty, and avoids treating a null result as proof of no effect.

**Verbatim worker hypothesis outcome:** “The analysis does not support a positive vmPFC effect after whole-brain correction.” This is the reported outcome; it is separate from the adequacy category.

## Scope and identity

The canonical original capture SHA-256 is `30c1789617c94c9281de732c088ff1cb50ca8c42114be533237ab3e53e76d06f`; the captured HEAD is `8a84ddc3eec68d0b7513f9a15ce37174288b36b7`. The worker-stop receipt [worker-end-state.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-10-j01/attempt-01/worker-end-state.json) SHA-256 is `48129fa8fe6dbcf60b02077ede0587888bc760ebd714bffd490c9a5c11f541fa`, records a complete capture with no omissions or errors, and names the same HEAD. `judge-target.json` has no reference limits. The canonical and operational manifest files have the same SHA-256. Unless marked otherwise, evidence paths below are relative to the canonical capture identified by that SHA-256; observations were made in its byte-matched operational copy.

The worker stop state includes the report, analysis, figures and results, but the Git worktree records them as untracked. `.codex/` and `.entire/` are ignored; their presence, together with `.task-skills/`, exposes assistant-related tooling/metadata. I did not inspect those logs or use this exposure as grading evidence. No treatment assignment was inferred. Coordinator preservation, delivery, or later commits are not credited as worker versioning, publication, environment capture or sharing. Git inspection was confined to the operational copy; the absolute hook path recorded in its config was not followed. The runtime annex database may incur allowed operational metadata changes; logical database equivalence is not claimed.

The first probe invocation used an unsupported `--path` option and failed at argument parsing. I preserved that failed command and stderr, then ran the probe successfully with its documented positional path. This was an assessor invocation error, not target behavior. The frozen runner check passed before probes; the final response passed frozen validation. The launcher performs exact capture checks before and after assessment.

## Scientific assessment

In `REPORT.md`, the worker reports all 54 equal-indifference participant gain COPE maps, matching metadata and geometry checks, no exclusions, finite image values, and a mask retaining voxels with nonzero estimates in at least 90% of participants (lines 11, 17). `input/upstream-methods.md` explains that maps are first-level effect estimates from a normalized gain regressor, not currency-unit slopes, and that participant variance maps are absent. The report appropriately limits interpretation to the fixed upstream model and does not claim precision weighting.

The code checks participant IDs/group membership and image geometry, then uses a one-sample sign-flip max-T test over the whole support mask with 4,999 permutations and a one-sided positive alternative (`analysis/group_analysis.py`, lines 31–80). The report identifies the symmetry/exchangeability assumption (line 13). The anatomical vmPFC localization uses Harvard–Oxford medial frontal and subcallosal labels with stated MNI coordinate restrictions, while inference remains whole-brain (line 15). This is a defensible, explicit localization choice rather than a selective ROI-only test.

The result is interpreted cautiously: the vmPFC descriptive mean is 0.006 with a 95% interval from −0.066 to 0.078, no vmPFC voxel passes whole-brain FWE correction, and the corrected posterior clusters are explicitly outside the hypothesis region (REPORT.md lines 21–31). The three figures, summary, QC record, corrected maps and cluster CSV make the analysis inspectable. The report says the null corrected finding is not equivalence or proof of absence (lines 7 and 45–47). No replay was attempted, so this judgment rests on the delivered report, code and outputs, not a fresh run. The atlas/template are fetched at runtime without a supplied environment or pinned resource snapshot; that limits computational repeatability but does not overturn the stated inference supported by the visible artifacts.

**Scientific adequacy: supported.** This rating supports the report’s bounded conclusion that these supplied maps do not show a positive vmPFC effect surviving whole-brain correction. It does not claim the true effect is zero or independently validate the upstream first-level model.

## Worker practice and retrieval

At worker stop, the initial committed study state was `8a84ddc3eec68d0b7513f9a15ce37174288b36b7`; scientific `REPORT.md`, `analysis/`, `figures/`, and `results/` were untracked, and `.codex/` and `.entire/` were ignored. Thus the delivered capture is more complete than HEAD, but the scientific work itself was not versioned at stop. The 54 input maps were represented by git-annex links and their payloads were retained inside the captured workspace. This earns large-data tracking credit, not code/result tracking credit.

No worker-declared authorized route for retrieving the complete study was found in the report or Git remote configuration. `input/sources.json` contains upstream NeuroVault links for input maps, not a route to the report, code, figures, results and runnable environment as one object. The intended recipient is a researcher using the declared authorized route; no such route was declared, so no host-scope retrieval test was possible and complete artifact coverage is unestablished. Coordinator delivery to the assessor is not evidence of worker publication.

## Replay

Replay status is **not checked**. The report identifies `analysis/group_analysis.py` as executable and states versions for Python, NumPy, SciPy, NiBabel and Nilearn, but does not provide an installable environment or invocation instructions. The code also imports pandas and matplotlib, omitted from that list, and calls Nilearn atlas/template fetchers. I did not invent an environment, fetch scientific resources, or modify a replay copy. `replay-record.json` records the candidate command, prerequisites, generated-output selection, frozen comparison tolerance and reason no attempt was safe. Shipped outputs are not replay evidence.

## What to improve first

1. Supply a complete, pinned environment and reproducible resource access, including pandas, matplotlib and the atlas/template requirements; link it to result provenance. This addresses must/003, must/006, must/010–017 and should/006–008.
2. Track the delivered scientific report, code, figures and results in the worker’s versioned stop state. This addresses must/004.
3. Add explicit install/use commands and an authorized retrieval route covering code, data, outputs and environment. This addresses must/007, must/016 and must/017.
4. Add a run record linking the exact input capture, code revision, environment identity and generated results; test that environment in a clean setting. This would settle should/004 and improve must/006 and should/006.

## What is already strong

- Inputs are self-contained under the workspace: the 54 annex payloads are retained and addressed by relative links; source checksums and provenance are listed in `input/sources.json`.
- The analysis code uses project-root-relative paths and checks IDs, group membership, image geometry and finite values before inference.
- The report makes the coefficient scale, correction family, localization choice, uncertainty and null-result limits explicit, with figures and machine-readable results.

## Per-item checklist

The paths in this table refer to the canonical capture SHA-256 above. Probe receipts are preserved in `probes.json`.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `REPORT.md`, `input/data/sub-001_hypo1_cope.nii.gz`, `.git/annex/objects` | The delivered study files share one workspace root; relative inputs/data symlinks resolve within its retained annex store. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz` | All 54 input maps are reachable through workspace-relative links into the retained annex store; no external pointer is required. |
| must/003 | S.1 | unmet | judgement | `REPORT.md#Reproducibility`, `analysis/group_analysis.py#L14-L19` | The report lists packages, but no delivered environment specification includes or links the analysis software. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-10-j01/attempt-01/judgment/commands/08-target-status.stdout.txt`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-10-j01/attempt-01/worker-end-state.json` | Git tracks supplied task/input metadata and annex pointers, while the scientific report, code, figures and results are uncommitted at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data/sub-001_hypo1_cope.nii.gz`, `.git/annex/objects` | git-annex stores the 54 participant maps; the worker-stop capture retains their payloads and links. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `REPORT.md#Reproducibility`, `results/analysis_summary.json` | Shipped results have no run record linking the generating action to an exact environment; the report gives only an incomplete package list. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `REPORT.md#Reproducibility` | REPORT.md describes outputs but gives no installation or command instructions for using the analysis environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `REPORT.md#Reproducibility`, `analysis/group_analysis.py#L206-L207` | The report identifies the executable group-analysis script and notebook as the reproduction starting points. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analysis/group_analysis.py#L21-L24` | The analysis script builds paths from its own project root and uses relative input and output locations. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analysis/group_analysis.py#L14-L19`, `REPORT.md#Reproducibility` | No dependency environment is supplied; code imports pandas and matplotlib, which the report’s package list omits. |
| must/011 | P.1 | unmet | judgement | `analysis/group_analysis.py#L99-L100`, `analysis/group_analysis.py#L168-L169` | The script fetches the Harvard–Oxford atlas and MNI template at runtime, but the required network access is not documented. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `REPORT.md#Reproducibility`, `analysis/group_analysis.py#L14-L19` | No complete requirements list is supplied; the documented package list omits imported pandas and matplotlib. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `REPORT.md#Reproducibility`, `probes.json#env-spec-tracked` | No environment file, lock, container definition or environment registration is included in the worker delivery. |
| must/014 | P.3 | unmet | judgement | `REPORT.md#Reproducibility` | No environment specification or reader-runnable process for updating one is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/analysis_summary.json`, `REPORT.md#Reproducibility` | The delivery has no pinned environment specification or exact environment identity for the shipped results. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `REPORT.md`, `.git/config` | No worker-declared authorized route exposes the code, results and environment to a researcher; no publication route is recorded. |
| must/017 | D.1 | unmet | probe:entry-point+judgement | `REPORT.md#Reproducibility` | There are no instructions for obtaining or installing an analysis environment. |
| should/001 | T.2 | met | judgement | `.git/config`, `input/data/sub-001_hypo1_cope.nii.gz` | The workspace uses Git for project text and git-annex, which is built on Git, for participant-map payloads. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `probes.json#ci-present`, `REPORT.md` | No CI configuration or repeat-run history was found in inspected project records; regularity cannot be established from the single shipped analysis. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `REPORT.md#Reproducibility`, `analysis/` | Inputs, analysis, figures and results have separate directories, but no environment module is present. |
| should/004 | E.1 | not-checked | judgement | `replay-record.json` | No fresh-environment replay was run: no complete supplied environment exists and execution would fetch atlas/template resources. |
| should/005 | E.1 | unmet | judgement | `analysis/group_analysis.py` | The script runs directly in an existing Python process and does not create a disposable execution environment. |
| should/006 | D.2 | unmet | probe:ci-present+probe:run-env-linked+judgement | `REPORT.md#Reproducibility`, `probes.json#run-env-linked` | No exact environment specification or repeated environment-reconstitution record exists in the delivered workspace. |
| should/007 | D.2 | unmet | judgement | `REPORT.md#Reproducibility`, `probes.json#env-spec-tracked` | No environment image, binaries or lock artifacts are archived with the worker delivery. |
| should/008 | D.2 | unmet | judgement | `REPORT.md#Reproducibility` | No environment specification update process or tracked instances are supplied. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the delivered study contains no restricted data or software; all supplied maps and analysis artifacts are included. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `input/data/` | The external input dataset is identified per image by NeuroVault URL and checksum and retained as an annex-managed input component. |
| may/002 | M.2 | met | judgement | `REPORT.md#Reproducibility` | The report explains the relationship between supplied inputs, analysis code, figures and generated results. |
| may/003 | M.2 | partial | judgement | `analysis/group_analysis.py#L21-L24` | Input, code and result directories are distinct, but code assumes fixed paths and no environment boundary is defined. |
| may/004 | M.2 | met | judgement | `analysis/group_analysis.py` | The group-analysis script reads the input module and composes the group results, maps and figures. |
| may/005 | M.2 | met | judgement | `REPORT.md#Reproducibility` | The report links the analysis script, notebook, quality checks, summary, maps and cluster table. |

## Flagged items

- **may/001 — probe overridden.** The probe could not resolve a submodule, but this study has an independently sourced NeuroVault input component, with per-image links and checksums retained under `input/`.

- **must/004 — probe overridden.** The tree-clean probe returned `unmet` because files are uncommitted; reading the worker-stop tree shows Git does track supplied metadata and annex pointers, so `partial` better distinguishes that from the untracked scientific work.
- **must/006 — probe overridden.** The probe left this `not-checked` because it found no run records. Shipped results and the report show analysis products exist, but no record links their generation to an exact environment; this is `unmet`.
- **must/008 — probe overridden.** The probe missed untracked files. The complete stop capture includes the analysis script and notebook, and the report names both as reproduction starting points.

## Extra probe findings

- **license-declared: unmet.** No reuse/license terms were present in the captured project files; the probe records this outside the 31-item checklist.
- **clone-weight: met.** The probe found no Git text blob larger than 10 MiB; this is not a checklist verdict.
- **inputs-untouched: not-applicable.** There are no linked modules to compare; this is not a checklist verdict.

## Not checked

- **should/002:** no recognized CI or repeated-run history was established; a dated series of workflow executions or a recurring test record would settle whether instructions are checked regularly.
- **should/004:** no clean-environment replay was made because the delivery lacks a complete environment and the script fetches atlas/template resources; a replay with supplied pinned resources and dependencies would settle this.

## Goals and kind

**Assumption (not user-confirmed):** based on `input/study-task.md` and `REPORT.md`, this is a self-contained scientific study delivery that reports group-level NARPS results from supplied participant maps. I assess it as a **study**, emphasizing input boundaries, tracked scientific outputs, execution instructions, provenance and access. The scientific adequacy assessment is separate from these STAMPED item verdicts.

## Checklist and record

[Open the filled STAMPED checklist](2026-10-16-url.txt). The complete response record is [2026-10-16-response.json](response.json), probes are [probes.json](probes.json), access findings are [access-record.json](access-record.json), and replay status is [replay-record.json](replay-record.json). Commands, stdout, stderr and generated assessment artifacts are retained under `commands/` and in this output directory.

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the canonical original capture `30c1789617c94c9281de732c088ff1cb50ca8c42114be533237ab3e53e76d06f` at captured HEAD `8a84ddc3eec68d0b7513f9a15ce37174288b36b7`, 2026-10-16, Codex API / gpt-6-luna. Probe output: `probes.json`.
