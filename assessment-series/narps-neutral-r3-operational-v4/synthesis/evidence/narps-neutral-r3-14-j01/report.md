# Independent assessment — NARPS potential-gain group analysis

**STAMPED verdicts:** MUST: 11 met / 3 partial / 3 unmet / 0 not-checked (17 items). SHOULD: 1 met / 2 partial / 3 unmet / 3 not-checked / 1 not-applicable (9 items). MAY: 2 met / 2 partial / 0 unmet / 0 not-checked / 1 not-applicable (5 items). No overall score is assigned.

**Scientific adequacy category: supported.** The analysis supports its reported conclusion that these supplied maps do not show a positive vmPFC gain effect surviving whole-brain family-wise error correction. This category assesses the reasoning and evidence for that conclusion; it does not mean the positive hypothesis was confirmed.

**Hypothesis conclusion:** No whole-brain-corrected support was found for a positive gain effect in vmPFC.

## What to fix first

1. Track the delivered analysis, report, figures, results and dependency file in the worker’s version-control state (must/004, must/013). The original HEAD tracks the supplied inputs, but these scientific products were untracked at worker stop.
2. Publish a researcher-accessible route covering the complete project and its environment (must/016). The captured worker Git config has no remote and README gives no package retrieval route; the coordinator’s later delivery is not worker publication.
3. Add a fully frozen dependency resolution and link the exact environment to a recorded execution (must/006, must/015). The report summary records Python and package versions, while `requirements.txt` pins direct packages only.
4. Document how dependency specifications are regenerated and track those updates (must/014, should/008).
5. Document the project-local environment creation command precisely and, if routine isolation is intended, make the workflow create a disposable environment (should/005).

## What is already strong

- The worker supplied a complete group-stage scientific package: protocol, executable analysis, report, figures, tables, maps and QC outputs. The README documents the entrypoint. These files were all present in the complete stop capture, even though most were untracked.
- The analysis uses all 54 matched participants, checks source hashes and image geometry, reports a common-coverage mask, and independently checks selected voxel statistics. The report states that participant variance maps are unavailable and does not interpret estimates as effects per currency unit.
- Whole-brain one-sided max-*t* sign-flip inference addresses the specified family-wise correction. The report distinguishes the uncorrected descriptive vmPFC summaries from the corrected hypothesis decision and does not claim equivalence from a null result.

## Scientific assessment

The protocol targets the mean participant gain-effect estimate against zero, with each participant as the unit and runs already combined upstream. `analysis/run_analysis.py` verifies one-to-one participant/map matching, exact input checksums, finite values, common shape and affine, then uses the intersection of nonzero coverage. It includes all 54 participants and reports no exclusions. These checks and the participant-wise QC table make major input and coverage decisions inspectable.

The primary test is a one-sided one-sample *t* statistic at each covered voxel. The maximum positive *t* from 9,999 participant-level sign flips controls whole-brain family-wise error at .05. This is a defensible group test conditional on the supplied first-level estimates; it assumes independent participants and sign-symmetric errors under the null. The script’s selected voxel statistics agree with independent SciPy tests. The common nonzero mask is a reasonable coverage rule, although interpreting every nonzero voxel as measured coverage remains conditional on the supplied maps’ zero-background convention.

The vmPFC coordinate box (MNI x −15..15, y 20..60, z −20..10 mm) is broad and explicitly described as a coarse anatomical approximation, not an atlas parcel. The strongest voxel in it is positive before correction (mean 0.232 map units, *t* = 4.19, uncorrected one-sided *p* = .000053) but has max-*t* FWE *p* = .780. Visual review of `figures/group_effects.png` shows the participant ROI values and t-map section with the declared coordinate box; `figures/max_t_null.png` shows the observed maximum beyond the 95th-percentile null threshold. The figures have no anatomical underlay, so they do not independently establish the vmPFC boundary. The ROI-average estimate is −0.0012 (SE .0088; 95% CI [−.0188, .0164]; one-sided *p* = .555). Twenty-four whole-brain corrected voxels occur in posterior clusters, away from vmPFC. These results support “no whole-brain-corrected support” under the stated anatomical definition. They do not establish absence or equivalence.

The report correctly limits the estimates: AO86’s gain regressor was mean-centered and variance-normalized, gain and loss were modeled separately, and participant variance maps are unavailable. Therefore the result is not an effect per currency unit, does not compare gain sensitivity with loss sensitivity, and cannot propagate first-level precision. The approximate coordinate ROI and fixed upstream models remain limitations, but they do not overturn the corrected whole-brain conclusion. Scientific adequacy is **supported** for the reported no-support conclusion.

## Worker stop state and evidence boundary

The canonical capture identity is SHA-256 `f4371d5d2658b02aba00235e0c3fd7ef9a0451f020ac7f6d0c5583446ff63ca2`; original HEAD is `a5761281bfdd9868cd88cb0720d8d06b9e2f7fb8`, captured 2026-10-16. The canonical and operational manifests report a complete capture with no declared omissions or errors. Evidence citations below refer to that canonical capture and paths relative to `content/workspace/`; file SHA-256 values identify the cited original bytes.

At worker stop, Git contained the supplied annex pointers and metadata, while README, analysis, requirements, report, figures and results were untracked. The stop receipt records the complete workspace and original HEAD. Later coordinator preservation is not counted as worker versioning, publication or accessibility. The original Git commit includes Codex co-author attribution, and the captured `.entire` files include a session record; this assistance exposure is recorded but was not used as grading evidence. No treatment assignment was inferred or reported.

Inspection and probe commands targeted only the operational copy, with the supplied Git environment settings preserved. The original `.git/config` records an absolute external `core.hooksPath`; that target was not followed. No commands were run through an external Git pointer. The captured annex links resolve inside the workspace. Probe-side Git/annex observations, including any allowed key-database metadata, are not worker actions. The canonical and operational manifest files compare byte-for-byte; the launcher’s exact before/after content verification remains the integrity authority. The replay helper failed before materializing a copy because its workdir existed already; no scientific code ran. The one-attempt limit was retained and the replay-dependent measures remain not-checked. The assessment runner/launcher is responsible for final exact-integrity verification; any allowed annex key-database metadata is not treated as worker evidence or as proof of logical equivalence.

## Access and retrieval

The intended recipient is a researcher authorized to use the analysis. No worker-declared route was found for retrieving the complete package, its generated results and its environment. The worker did declare upstream input routes in `input/sources.json`; metadata-only HTTP HEAD checks from this assessor host in New York/EWR returned 200 for the NeuroVault collection, a representative map and the pinned cohort table, and 404 for the pinned AO86 methods workbook URL. The local `input/upstream-methods.md` remains supplied. No input bytes were downloaded. This check covers upstream inputs only, not the complete project, and no other-host or independent-recipient access was tested. See `access-record.json` and `commands/access-head.stdout`.

## Replay measurement

One attempt was authorized and declared before execution in `replay-plan.md`: create a project-local Python 3.13 environment from the delivered requirements, then run the README entrypoint. Eight named generated artifacts were selected, with SHA-256 comparison for NIfTI/JSON/PNG and table comparison at relative tolerance 1e-6. The frozen runner stopped before copying or executing because `replay-work` already existed and the helper requires a new destination. This was an invocation/setup error, not target behavior or assessor malfunction; no second attempt was made. The command, stdout, stderr, exit code and explicit attempt record are retained under `commands/` and `replay-attempt.json`.

## Item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `README.md` | The complete workspace, linked inputs, code, results and documentation are within one captured root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `.git/index` | All 54 supplied maps and metadata are inside the root; relative annex links resolve within its captured .git store. |
| must/003 | S.1 | met | judgement | `requirements.txt`, `analysis/run_analysis.py` | All imported external Python packages are declared in requirements.txt; no other external software is invoked. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `.git/index`, `analysis/run_analysis.py` | Git tracks supplied inputs, but the analysis, report and generated results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `.git/index`, `input/sources.json` | Git-annex tracks the 54 supplied NIfTI maps; captured annex payloads are present under the workspace Git store. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+probe:run-env-linked+judgement | `results/summary.json`, `requirements.txt` | The shipped summary records runtime versions and results, but no exact frozen environment or complete action record is linked. |
| must/007 | A.1 | met | probe:entry-point+judgement | `README.md` | README.md provides installation instructions, the analysis command, input context and links to report and results. |
| must/008 | A.1 | met | probe:entry-point+judgement | `README.md`, `analysis/run_analysis.py` | The documented starting point is analysis/run_analysis.py, invoked from the project root. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analysis/run_analysis.py`, `README.md` | The analysis uses paths relative to its own workspace; the documented commands are portable shell/Python commands. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `requirements.txt`, `analysis/run_analysis.py` | All non-standard imports in the analysis are covered by the delivered pinned requirements.txt. |
| must/011 | P.1 | met | probe:platform-assumptions+judgement | `README.md`, `requirements.txt` | The route specifies Python 3.13.16 and needs only a project-local Python environment and standard shell; no further host service is required. |
| must/012 | P.2 | met | probe:platform-assumptions+judgement | `README.md`, `requirements.txt` | README specifies Python 3.13.16 and links the full direct dependency list in requirements.txt. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `requirements.txt`, `.git/index` | requirements.txt exists in the complete delivery but was untracked at worker stop, so the specification was not version controlled alongside code. |
| must/014 | P.3 | unmet | judgement | `README.md`, `.git/index` | No dependency-update command or process is documented, and the worker-stop history contains no tracked environment updates. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `README.md`, `requirements.txt` | Python and direct package versions are pinned, but transitive resolutions and a frozen environment lock are absent. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `.git/config`, `README.md` | No worker-declared route publishes the complete code, results and inputs; the captured Git config has no remote. |
| must/017 | D.1 | met | judgement | `README.md`, `requirements.txt` | README explains the required Python version, dependency installation and how to run the analysis. |
| should/001 | T.2 | partial | probe:tree-clean+judgement | `.git/index`, `analysis/run_analysis.py` | Git-annex versions supplied maps and metadata, while analysis, environment, report and result components were untracked. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `analysis/run_analysis.py`, `.git/index` | No regular test schedule or equivalent repeated-run record was found; a history of routine executions would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `README.md`, `analysis/protocol.md` | Inputs, analysis code and results are in separate directories; requirements and other environment details remain at the root. |
| should/004 | E.1 | not-checked | judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-14-j01/attempt-01/judgment/replay-attempt.json` | The single replay stopped before execution; no worker fresh-container, batch or clean-VM run record is available. |
| should/005 | E.1 | unmet | judgement | `README.md`, `analysis/run_analysis.py` | The instructions use a project-local environment, but the workflow does not create a disposable environment for each execution. |
| should/006 | D.2 | not-checked | probe:run-env-linked+judgement | `results/summary.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-14-j01/attempt-01/judgment/replay-attempt.json` | The stop state provides no worker record of regularly reconstituting the result environment; repeated clean reconstructions would settle this. |
| should/007 | D.2 | unmet | judgement | `requirements.txt` | The package environment is referenced by requirements.txt; package artifacts or an environment image are not archived in the workspace. |
| should/008 | D.2 | unmet | judgement | `README.md`, `.git/index` | No dependency-update process or tracked environment-specification updates are documented. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: no restricted data or software are present; all supplied scientific inputs are declared public sources. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `.git/config`, `README.md` | N/A: no independently maintained project components or external modules are part of the workspace boundary. |
| may/002 | M.2 | partial | judgement | `README.md`, `analysis/protocol.md` | README locates inputs, analysis, results, figures and report, but does not document component relationships in detail. |
| may/003 | M.2 | partial | judgement | `analysis/run_analysis.py`, `requirements.txt` | The script separates input paths and result destinations, but environment and software versions are not maintained as an independent module. |
| may/004 | M.2 | met | judgement | `analysis/run_analysis.py`, `README.md` | The Python entrypoint composes the delivered inputs, analysis and generated outputs through workspace-relative paths. |
| may/005 | M.2 | met | judgement | `README.md`, `report/report.md` | README identifies the project areas and links the analysis protocol, report, figures and result outputs. |

## Flagged items

- **must/002, must/004, must/006, must/007, must/008, must/010, must/011, must/012, must/015, should/001, may/001:** Probe scope is limited to recognized tracked representations; complete-delivery inspection changed or refined the result using untracked worker-stop artifacts.
- **must/009:** The path probe scanned tracked text only; the delivered untracked analysis script was separately read and uses workspace-relative paths.
- **must/016:** The probe measured a tracked environment specification, while this item asks whether recipients can access it. No worker package route was declared; the status is unmet on that access evidence.
- **must/014 and should/008:** These checklist items intentionally duplicate the environment-update question; both lack a documented update process.

## Extra finding

The complete worker workspace contains no license or reuse terms. This is recorded separately as `license-declared` in the response because it is not one of the pinned checklist items.

## Not checked

- **should/002:** No regular testing schedule or equivalent repeated-run record was established; repeated dated executions would settle it.
- **should/004:** The replay attempt did not start scientific execution; a successful fresh-environment run record would settle it.
- **should/006:** No worker record shows regular environment reconstitution; repeated successful reconstructions tied to the specification would settle it.
- **Replay:** Assessment setup error prevented the single allowed captured-delivery replay. No scientific reproducibility measurement is available.

## Goals, kind and assumptions

The documented goal is a group-stage NARPS Hypothesis 1 analysis from supplied AO86 gain-effect maps for the equal-indifference cohort (`README.md`, `analysis/protocol.md`, and the retained scientific task). This is assessed as a **study**. That kind is assumed from the supplied project purpose and was not separately confirmed by a human. Scientific adequacy and STAMPED practice are reported independently.

## Canonical evidence references

All references below are to capture `f4371d5d2658b02aba00235e0c3fd7ef9a0451f020ac7f6d0c5583446ff63ca2` and the stated path under `content/workspace/`.

- `README.md` — SHA-256 `e79a3ac83cab423c5f24d18bccd4afd9af72b9a2a2297a64cf38ec4ab12e6aeb`.
- `analysis/protocol.md` — SHA-256 `764f55a240cc07d3729ec9b751f7b6f071f24aaf850db761b993cad5ed34ba5f`.
- `analysis/run_analysis.py` — SHA-256 `05f15427d972f5929843618c4649e610614f7435dc9845c72ce1b67eae24e767`.
- `report/report.md` — SHA-256 `bb6ae04ccdbbb97af8df8b67f033895b8cb0f8b1dbaa7b702a53a842e0db0e65`.
- `results/summary.json` — SHA-256 `ef1d4ec704744089b75eb70d046e91ebb6e37f543a31f87a6085faa267317c92`.
- `results/participant_qc.tsv` — SHA-256 `d4780574296c74cebabadacf46620966440b16cd395d44e3f99dce850f9b5f45`.
- `figures/group_effects.png` — SHA-256 `a49a7212174c44c98c3650f14e12ee41ea57cab6c102881b5e0cd9a9418c07cd`.
- `figures/max_t_null.png` — SHA-256 `dda1647c347e85a6ee53cdb8363d82930ce6a4f98e6515a40b115753e0979dc3`.
- `requirements.txt` — SHA-256 `043bb387bd177e474bff6b22d67c06118f59c0203ab5a6694bea444c8898fcf1`.
- `input/sources.json` — SHA-256 `919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`.
- `.git/config` — SHA-256 `68e66d94455efcb364d2e8bacbe82ca42815b0ac7c039400cf7d2524cfeb4e48`.
- `.entire/metadata/01a145a1-b850-7220-b042-906390493866/full.jsonl` — SHA-256 `74156a260d715bbb2ba752a5db1991441d4a80a1e1d675ff11644a4a509fc32b` (assistance exposure; not used as grading evidence).

## Checklist and provenance

[Open the filled checklist](2026-10-16-url.txt). The complete item responses and evidence are in [2026-10-16-response.json](2026-10-16-response.json); the unedited scripted probe output is [2026-10-16-probes.json](2026-10-16-probes.json). The replay setup record is [replay-attempt.json](replay-attempt.json), with its predeclared plan in [replay-plan.md](replay-plan.md). The capture manifest and worker stop receipt are retained as [canonical-manifest.json](canonical-manifest.json) and [worker-stop-receipt.json](worker-stop-receipt.json). The separate scientific record is [scientific-judgment.json](scientific-judgment.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on canonical capture `f4371d5d2658b02aba00235e0c3fd7ef9a0451f020ac7f6d0c5583446ff63ca2`, original HEAD `a5761281bfdd9868cd88cb0720d8d06b9e2f7fb8`, 2026-10-16, Codex CLI (native; con-duct 0.23.0) / gpt-6-luna. Probe output: `2026-10-16-probes.json`.
