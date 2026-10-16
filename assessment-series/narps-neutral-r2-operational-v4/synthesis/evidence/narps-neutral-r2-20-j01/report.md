# Independent assessment — NARPS potential gains and brain activity

**Checklist verdicts:** MUST: 5 met / 3 partial / 9 unmet / 0 not-checked (17 total). SHOULD: 0 met / 2 partial / 3 unmet / 3 not-checked / 1 not-applicable (9 total). MAY: 2 met / 3 partial / 0 unmet / 0 not-checked / 0 not-applicable (5 total). No aggregate score is assigned.

**Capture identity:** canonical SHA-256 `d6429e3233789df0d5b036bc1a2563dab06eb47a8dcf71ac0ee90c4d592a0de5`; original captured HEAD `ee2121676b82900d355458da4ad9a13014094fc4`; captured 2026-10-16T15:43:02.444997+00:00. Unless stated otherwise, `path` citations below mean the capture-relative path under this SHA-256 identity. The delivery manifest and worker stop receipt record a complete capture with no omissions. The complete stopped workspace includes three untracked-at-HEAD scientific deliverables: `analyze.py`, `report.md`, and `results/`; the HEAD alone is not the delivery.

## What to fix first

1. **Include a pinned environment and dependency list, with the source and versions of atlas/template data** → a researcher cannot know how to provision the software and external image resources required by the documented command → closes must/003, must/010, must/012–017 and supports provenance under must/006.
2. **Track the analysis, report, and results in version control and publish the complete object at an authorized researcher route** → the captured HEAD omits the study’s central artifacts and no worker publication route is declared → closes must/004, should/001 and must/016.
3. **Add install and usage instructions plus a supported environment setup path** → the current command depends on a host-specific shared interpreter path → closes must/007, must/011, must/017.
4. **Record each analysis run with the code state, complete environment identity, input identities, command, and output identities** → current summary metadata does not identify the exact runtime that produced the reported results → closes must/006 and improves should/006.

## What the project already does well

- It captures all 54 participant maps as annex content reached by relative links inside the workspace, and the fresh-copy replay successfully read those inputs (`input/data/`, `input/sources.json`; replay details in `replay-record.json`).
- The analysis is a clear group-level entrypoint and the report explains effect scaling, the selected coverage rule, whole-brain correction, uncertainty, limitations, and a cautious interpretation (`analyze.py`, `report.md`).
- Inputs, results, QC tables, participant-level ROI estimates, and figures are included in the complete stopped workspace, even though the scientific deliverables were not committed at worker stop (`input/`, `results/`, `probes.json`).

## Scientific assessment

**Scientific adequacy: supported.** The delivered analysis supports its appropriately limited conclusion that these data do not show a positive vmPFC gain effect under the required whole-brain correction. It uses the 54 independent participant effect maps, a common coverage mask, positive one-sided whole-brain max-T sign-flip inference, an explicit vmPFC anatomical proxy, an uncertainty interval, and transparent limits of the fixed upstream model. The result does not establish an exactly zero effect.

**Reported hypothesis outcome:** “In the 54-person equal-indifference group, the whole-brain analysis did not support a positive gain effect in vmPFC.” This is an outcome about evidence under the chosen analysis, not proof of absence of any effect (`report.md`).

Whole-brain-corrected decisions are explicitly required by the retained `input/study-task.md` and the [original NARPS analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf). The analysis matches all 54 map IDs to cohort metadata, verifies input checksums, checks finite data and common geometry, and excludes no participants. Its common-mask analysis tests 198,029 voxels, 78.9% of the union coverage; it states this restriction and reports the ROI has 1,422 in-mask voxels. The ROI mean is 0.0027 (SD 0.0891; 95% t interval −0.0217 to 0.0270; t(53)=0.22; unadjusted one-sided p=.414). No ROI voxel survives whole-brain FWE correction. The whole-brain maximum is an occipital-pole result (24 voxels; peak t(53)=6.62; FWE p=.0006), while the strongest vmPFC-proxy voxel has FWE p=.780. These findings support the report’s lack-of-support conclusion rather than a localized positive vmPFC claim (`results/input_qc.csv`, `results/summary.json`, `results/vmPFC_subject_effects.csv`, `results/fwe_p_map.nii.gz`, figures in `results/figures/`).

The one-sample group model treats participants equally because participant variance maps are not supplied. The sign-flip test assumes independent participants and a symmetric null for participant effects; the report states this. The gain coefficient is not a per-dollar response: the upstream regressor was centered and variance-normalized. Separate gain and loss models, response-time duration, and other fixed upstream choices constrain interpretation. The ROI interval is not an equivalence test, and the non-significant result does not rule out smaller effects. The broad Harvard–Oxford frontal-medial/subcallosal proxy is identified as an operational vmPFC definition rather than a unique boundary. No material inferential error was found that would undermine this cautious conclusion (`input/upstream-methods.md`, `report.md`, `analyze.py`).

## Per-item checklist
| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `analyze.py` | Core inputs, analysis, report, and results sit under one workspace root; map links resolve through captured annex objects inside that root. |
| must/002 | S.1 | met | judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `input/sources.json`, `replay-record.json` | All 54 maps are internally reachable through relative annex links, and the documented replay read them from the complete captured copy. |
| must/003 | S.1 | unmet | judgement | `analyze.py`, `report.md` | The required Python/scientific software is not included in an environment or linked software module. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `probes.json`, `analyze.py` | Git tracks the supplied inputs and config, but the analysis script, report, and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data/sub-001_hypo1_cope.nii.gz`, `probes.json` | Git-annex stores all 54 participant maps, with the relative map links and payloads retained in the capture. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `results/summary.json`, `analyze.py`, `report.md` | The delivered results have no run record linking their generation to an exact environment; summary software versions are incomplete. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report.md`, `probes.json` | report.md gives a usage command, but no installation instructions or obtainable environment specification. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `analyze.py` | The report identifies analyze.py as the starting point and supplies the command that runs it. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analyze.py`, `probes.json` | analyze.py builds input and output paths relative to its own directory; the report absolute interpreter path is a separate host assumption. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analyze.py`, `report.md`, `probes.json` | No dependency specification covers the script imports or the atlas/template data requested through Nilearn. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `report.md`, `analyze.py`, `.git/config` | The report names an external interpreter and thread variables, but omits a complete account of the host and runtime assumptions. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `report.md`, `analyze.py` | No usable system requirements or complete dependency list tells a researcher what to install or provide. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probes.json`, `report.md` | No environment specification is present in the captured workspace or versioned alongside the analysis. |
| must/014 | P.3 | unmet | judgement | `analyze.py`, `probes.json` | No environment specification or dependency-update process is declared or tracked. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `report.md`, `probes.json` | The delivery contains no pinned environment manifest or archived environment from which to reconstruct the run. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `.git/config`, `report.md`, `access-route.json` | No worker-published route provides the environment or the complete research object to a researcher. |
| must/017 | D.1 | unmet | judgement | `report.md`, `analyze.py` | The report gives a run command but does not explain how to obtain or install the referenced environment. |
| should/001 | T.2 | partial | judgement | `probes.json`, `probes.json` | Git and annex form one data/code repository, but the main analysis, report, and results were untracked at worker stop. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `probes.json`, `worker-end-state.json` | No recognized CI is present; worker run history was not established. A worker test log or repeated CI record would settle this. |
| should/003 | M.1 | partial | probe:modules-separated | `input/participants.tsv`, `analyze.py`, `results/summary.json` | Inputs and results are separate directories, but analysis code is at the root and no environment module exists. |
| should/004 | E.1 | not-checked | judgement | `replay-record.json`, `report.md` | The assessor replay used a fresh copy but the documented shared host environment, not a fresh container, VM, or cloud instance; worker evidence is absent. |
| should/005 | E.1 | unmet | judgement | `report.md` | The documented command reuses a shared interpreter environment; it does not create a disposable environment for each run. |
| should/006 | D.2 | not-checked | probe:run-env-linked+judgement | `probes.json`, `report.md` | No environment spec or worker reconstitution history exists to assess regular clean reconstruction; a pinned spec and repeat logs would settle it. |
| should/007 | D.2 | unmet | judgement | `probes.json`, `report.md` | No environment image, lockfile, or executable environment artifact is archived in the workspace. |
| should/008 | D.2 | unmet | judgement | `analyze.py`, `probes.json` | No environment specification or dependency-update process is declared or tracked. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: captured sources identify public NeuroVault maps and public metadata; no access-restricted data or software component is identified. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz` | The independent AO86 input dataset is identified by source and boundary, with its files included under input/data via annex. |
| may/002 | M.2 | partial | judgement | `report.md`, `input/` | The report explains inputs, analysis, and results, but does not document a modular design or how components can be recombined. |
| may/003 | M.2 | partial | judgement | `input/participants.tsv`, `results/summary.json`, `analyze.py` | Input files and results are separable, but code and environment boundaries are not independently maintained. |
| may/004 | M.2 | partial | judgement | `analyze.py`, `report.md` | analyze.py composes captured inputs into results, but no separate module composition or orchestration mechanism is documented. |
| may/005 | M.2 | met | judgement | `report.md`, `input/sources.json` | The report names the input metadata, script, key results, and figures, giving readers a usable map of the workspace. |

## Probe disagreements and flags

- **must/004:** `tree-clean` called the item unmet because analysis/report/results were untracked; the judgment records partial because Git does track captured input/configuration text, but not the core scientific outputs.
- **must/006:** `derived-have-records` returned not-applicable after scanning tracked paths; the full captured delivery has generated result files, but no exact run-to-environment record. The item is unmet.
- **must/007–008:** the entry-point probe did not recognize the untracked report and script. The report supplies usage but no installation route (partial must/007); it does name an executable starting point (met must/008).
- **must/009:** the path probe scanned tracked text only, while `analyze.py` was untracked. Direct inspection shows script input/output paths are relative to `__file__`; the probe's tracked-text scan is incomplete for that question. The absolute interpreter path is assessed under portability assumptions (must/011).

The response flags these disagreements as `probe-overridden` or `mapping-questioned`. The duplicate environment-update question in must/014 and should/008 carries `upstream-duplicate` on both items.

## Not checked

- **should/002:** no recognized CI or repeated worker testing history was available. A worker-side test log or repeated CI record would settle it.
- **should/004:** the replay made a fresh copy but reused the documented host environment on the same host; there is no worker record of a fresh container, VM, batch job, or cloud run.
- **should/006:** there is no environment pin or worker reconstitution history to assess regular rebuilding. A pinned environment and repeated reconstruction records would settle it.

## Assumptions, access, and capture integrity

**Goals and kind (assumption; no human guidance was attached):** based on `input/study-task.md` and `report.md`, this is a **study** whose product is a group-level answer about the positive potential-gain effect in vmPFC for the equal-indifference cohort. This kind emphasizes complete reachable inputs and traceable results/actions/environments.

**Recipient and route:** the intended recipient is a researcher following a worker-declared authorized route; anonymous access is not required. No worker project remote or publication URL is present in captured `.git/config` or `report.md`. HEAD requests to the declared source URLs returned HTTP 200 for one representative NeuroVault map and the pinned cohort and methods files on `raw.githubusercontent.com`. Those routes cover source inputs and upstream methods, not `analyze.py`, `report.md`, generated results, the environment, or the complete project. Coordinator delivery to this assessment is not evidence that the worker made the project accessible. See `access-route.json` for tested host scope and limitations.

**Worker stop versus later assessment:** the worker stop receipt (SHA-256 `bc3d543e0348529a943cb14d05761a53ae13b673ff90773f97b814f242bfc4b6`) records a successful worker exit, the same captured HEAD, and no omissions; it does not identify a worker-published project route or exact analysis environment. It also labels the initial external skills directory as coordinator-supplied guidance, not a worker discovery or output. Git history/status and supplied annex state are judged at that stop. The coordinator-retained capture/operational copy establishes preservation for this assessment, not worker publication. The captured environment is not self-contained; the report points to a shared absolute interpreter outside the root. No coordinator upload or later preservation action is credited to the worker.

**Integrity observation:** the operational copy matched the canonical manifest across all 1,099 workspace entries at inspection, with no missing, extra, or mismatched files, links, modes, or content except the explicitly classified operational metadata file `.git/annex/keysdb/db`. That regular file changed during inspection; this is assessor-induced metadata, not worker evidence, and no logical database equivalence is claimed. No conclusion relies on that database state: map availability is supported by the captured relative links and annex object bytes and by replay from the canonical complete delivery. No scientific file or other target content changed. See `capture-integrity-final.json`. Captured `.codex/` and `.entire/` identifiers indicate assistance tooling/session logging exposure; their contents were not used as grading evidence. Captured `.git/config` has an external `core.hooksPath`; it was not followed or invoked. The replay helper overlaid `/dev/null` for hooks in its separate copy and left captured config unchanged. `judge-target.json` has no reference limits; no external Git pointer was used.

## Replay record

Before the attempt, `replay-plan.md` declared the exact command, prerequisites, all 12 generated outputs, protected inputs, and comparison rule. The frozen helper made a fresh writable copy of the canonical complete delivery and removed only those selected generated outputs. One replay completed in 14.1 seconds with return code 0; every selected file was byte-identical. This supports computational repeatability of the selected outputs on this host with the documented shared interpreter and existing atlas/template cache. It does not supply a worker environment capture or establish cross-host reproducibility. The adapter initiated no scientific-input prefetch; the documented script itself calls Nilearn for atlas/template data. Replay evidence is separate from the scientific judgment and from the worker-stop provenance. Full result and command output: `replay-record.json`, `replay.stdout.txt`, `replay.stderr.txt`, and `replay-workdir/`.

## Extra finding

The `license-declared` probe found no license file or dataset License field; reuse terms are unstated. This is reported outside the 31-item checklist (`response.json`).

## Checklist URL and assessment stamp

Checklist-app URL: [2026-10-16-url.txt](2026-10-16-url.txt). Machine-readable verdicts and evidence: [response.json](response.json). Probes: [probes.json](probes.json). Replay: [replay-record.json](replay-record.json). Scientific judgment: [scientific-judgment.json](scientific-judgment.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259bad`), on canonical capture `d6429e3233789df0d5b036bc1a2563dab06eb47a8dcf71ac0ee90c4d592a0de5` at original commit `ee2121676b82900d355458da4ad9a13014094fc4`, 2026-10-16, Codex API / GPT-6 (exact runtime build unavailable). Frozen assessor source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`; environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`. Probe output: `probes.json`.
