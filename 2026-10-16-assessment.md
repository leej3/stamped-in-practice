# Assessment: NARPS potential-gain group analysis

Assessed committed state: `40164f018638f6fc744881a91a70d3257b77985f` (verified against the requested revision). Scope: source inspection, remote retrieval checks, and one authorized fresh-clone replay attempt. The source checkout was not changed. The worker-stop receipt matches the assessed `HEAD` and records an empty index/worktree.

## STAMPED verdicts

**MUST: 17 met / 0 partial / 0 unmet / 0 not-checked. SHOULD: 3 met / 4 partial / 1 unmet / 1 not-checked. MAY: 5 met / 0 partial / 0 unmet / 0 not-checked.** There is no overall score.

## What to improve first

1. Add a recurring clean-clone check that installs the locked environment and validates the replay → the object has successful replay records, but no ongoing check keeps instructions and the environment current → `should/002`, `should/006`.
2. Run the documented workflow in a clean VM, container, batch job or cloud instance, and make per-run isolation explicit → current successful replays use fresh Pixi clones on the same host, while the normal task reuses its project environment → `should/004`, `should/005`.
3. State the reuse/access terms for the NARPS maps and software, and archive feasible environment artifacts → terms are not declared and the package binaries remain external → `should/007`, `should/009`, extra finding `license-declared`.

## What the object does well

- The code checks the 54-person cohort against map identities and SHA256 manifests, verifies matching image geometry, and reports its finite/nonzero support rule. The protocol discloses that 53,034 partial-support voxels are excluded because no participant brain masks are supplied. See [analysis/PROTOCOL.md](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/targets/judgment-01/analysis/PROTOCOL.md) and [analysis/group_analysis.py](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/targets/judgment-01/analysis/group_analysis.py).
- The analysis specifies one-sided sign-flip max-t whole-brain FWE, an independent anatomical vmPFC ROI, uncertainty summaries, and limits on the effect estimates. Result, maps, tables, figures and an independent numerical audit are retained under [results/group-analysis/](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/targets/judgment-01/results/group-analysis).
- Code and results link to a specific code revision, lock hash and recorded run. A direct retrieval clone fetched the exact task commit, the lock snapshot and all annex objects; all 71 objects passed annex integrity checks. Evidence: [access record](2026-10-16-access-evidence.json) and [retrieval log](attempts/2026-10-16/retrieval-check.stdout).

## Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `README.md` | All study files are under the repository root; data and atlas payloads are annexed there. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `.gitmodules`, `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/2026-10-16-access-evidence.json` | The module URL resolves and the documented annex route retrieves all required maps, atlas and result payloads. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `.gitmodules` | Analysis libraries and execution tools are in Pixi; shared skills are a resolvable submodule. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/worker-end-state.json`, `git:HEAD` | At worker stop, the receipt records this commit and a clean index/worktree; Git tracks code and metadata. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `.gitattributes`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/attempts/2026-10-16/retrieval-check.stdout` | Git-annex tracks large maps and NIfTI results; the published clone retrieved all 71 annex objects. |
| must/006 | T.1,T.3,T.5 | met | probe:derived-have-records+judgement | `results/group-analysis/provenance.json`, `logs/final-common_2026.10.15T23.33.03-647_info.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/2026-10-16-access-evidence.json` | Provenance links the result to its code commit, exact lock SHA, command and duct run records; the probe missed it. |
| must/007 | A.1 | met | probe:entry-point+judgement | `README.md`, `pixi.toml` | README documents installation, retrieval and the group-analysis command. |
| must/008 | A.1 | met | probe:entry-point+judgement | `README.md`, `analysis/group_analysis.py` | The README names a runnable Pixi task backed by analysis/group_analysis.py. |
| must/009 | P.1 | met | probe:no-abs-paths | `analysis/group_analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/2026-10-16-probes.json` | Execution uses repository-relative paths; the recorded /tmp path is a portable historical replay location. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `pixi.toml`, `analysis/group_analysis.py` | Imports and invoked tools are declared in Pixi, including scientific libraries, Git-annex and duct. |
| must/011 | P.1 | met | judgement | `README.md`, `pixi.toml` | README specifies macOS 14 Apple Silicon or Linux x86-64, Pixi, Git-annex and network; it disclaims mounts, GPU and license service. |
| must/012 | P.2 | met | judgement | `README.md` | README lists Pixi, Git with git-annex, network access and supported platforms. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/attempts/2026-10-16/access-verification.stdout` | pixi.toml is tracked beside code and data; the exact lock is on the linked environment branch. |
| must/014 | P.3 | met | judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/attempts/2026-10-16/access-verification.stdout` | README gives the lock and environment-branch update procedure; a retrievable snapshot branch carries the exact lock. |
| must/015 | D.1 | met | judgement | `results/group-analysis/provenance.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/2026-10-16-access-evidence.json` | The lock snapshot branch contains the exact pixi.lock whose SHA256 is recorded with results. |
| must/016 | D.1 | met | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/2026-10-16-access-evidence.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/attempts/2026-10-16/retrieval-check.stdout` | An authorized researcher route retrieved the exact task commit, lock and all annex payloads with verified content. |
| must/017 | D.1 | met | judgement | `README.md` | README tells users to check out the environment snapshot, retrieve annex content and run pixi install --locked. |
| should/001 | T.2 | met | judgement | `.gitattributes`, `git:HEAD` | Git versions code and text; Git-annex integrates binary inputs and outputs with the same repository. |
| should/002 | A.2 | partial | probe:ci-present+judgement | `logs/attempts.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/2026-10-16-probes.json` | Several fresh-clone replays are recorded, but there is no ongoing CI or schedule to test the workflow regularly. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `analysis`, `results`, `pixi.toml` | Inputs, analysis code, results and environment definitions occupy distinct paths. |
| should/004 | E.1 | partial | judgement | `logs/attempts.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/2026-10-16-fresh-rerun.json` | Recorded replays use fresh Pixi clones on the same host; no container, batch job, clean VM or cloud run is evidenced. |
| should/005 | E.1 | unmet | judgement | `README.md`, `pixi.toml` | The documented task reuses a project-local Pixi environment; it does not create a disposable environment for each run. |
| should/006 | D.2 | partial | probe:ci-present+judgement | `logs/attempts.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/2026-10-16-probes.json` | Several fresh-clone locked replays are recorded, but there is no ongoing CI or periodic environment check. |
| should/007 | D.2 | partial | judgement | `README.md`, `pixi.toml` | The lock is archived on the environment branch, while package binaries remain resolved from conda-forge and PyPI. |
| should/008 | D.2 | met | judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/judgment-01/judgment/2026-10-16-access-evidence.json` | The documented environment update process has a tracked snapshot instance; this duplicates must/014 by checklist design. |
| should/009 | M.4 | not-checked | judgement | `input/sources.json` | No restriction or reuse terms are stated, so the status of any restricted component cannot be established. |
| may/001 | M.2 | met | probe:subdatasets-resolvable | `.gitmodules` | Shared skills are linked at a resolvable Git submodule URL. |
| may/002 | M.2 | met | judgement | `README.md` | README explains how input, analysis, outputs and environment fit together. |
| may/003 | M.2 | met | judgement | `analysis/PROTOCOL.md`, `README.md` | Inputs, analysis and environment are separately maintained; manifests and the snapshot branch define stable interfaces. |
| may/004 | M.2 | met | judgement | `README.md`, `pixi.toml` | Pixi tasks compose the declared environment, annex retrieval and group-analysis script. |
| may/005 | M.2 | met | judgement | `README.md`, `analysis/PROTOCOL.md`, `results/README.md` | README, protocol and results inventory guide users through inputs, methods, results and replay. |

## Flagged items

- `must/002`: the probe measured whether the skills submodule URL resolves; the item asks whether required datasets are reachable within the project boundary. The independent annex retrieval is the direct evidence (`mapping-questioned`).
- `must/006`: the probe reported no run record; I overrode it because `results/group-analysis/provenance.json` links the result to the code commit, exact lock hash, command and duct record (`probe-overridden`).
- `must/016`: the probe could not verify remote content; the published GitHub task branch, lock snapshot and annex payloads were independently retrieved and checked (`probe-overridden`).
- `should/002` and `should/006`: the CI probe measures CI configuration, while the items ask whether the workflow/environment is tested regularly. Recorded clean-clone replays support `partial`, but not ongoing testing (`mapping-questioned`, `probe-overridden`).
- `should/008`: duplicates `must/014` by checklist design (`upstream-duplicate`).

## Not checked

- `should/009`: the object does not state whether any inputs or software are restricted or provide reuse terms. A rights/access statement for each component would settle this. Current technical retrieval succeeded through the documented researcher route.

The separate probe extra `license-declared` is unmet: the tracked tree has no license file or reuse declaration. This is not a checklist item in pin 0.3.1.

## Goals and kind

**Assumption, not human-confirmed:** this is a **study** whose product is a group-level answer about a positive gain effect in vmPFC for the specified equal-indifference cohort. The scientific brief and README define that goal. As a study, the assessment emphasizes input linkage, provenance for derived results, re-executable group methods, portability and retrievability.

## Blinding limitation

Participant and source metadata can expose group membership. I did not infer or report any treatment assignment, and this information was not used as grading evidence.

## Scientific assessment (separate from STAMPED)

**Scientific adequacy: supported.** The reported conclusion is appropriately limited to “no whole-brain-corrected vmPFC evidence was found”; it does not claim the response is zero. This decision rule is consistent with the [original NARPS analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf), which call for whole-brain-corrected hypothesis decisions.

**Supported findings:** The one-sided one-sample group test used 9,999 participant sign flips and max-t correction across 198,029 common-support voxels. The atlas-defined 797-voxel vmPFC ROI was not used to restrict the corrected search. No voxel in that ROI survived whole-brain FWE correction: its peak was t(53)=4.19, max-t adjusted p=.782. The descriptive ROI mean was 0.012 cope units (95% t interval −0.008 to 0.033; one-sided unadjusted p=.115). There were 24 corrected positive voxels elsewhere; the maximum was in posterior cerebellum (t=6.62, FWE p=.0007). These results support the stated lack of vmPFC-specific corrected support, not a null-effect claim. The independent audit in [audit.json](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/targets/judgment-01/results/group-analysis/audit.json) matched the ROI mean, corrected peak, and voxel count. See [REPORT.md](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/targets/judgment-01/REPORT.md) and [results/group-analysis/summary.json](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/targets/judgment-01/results/group-analysis/summary.json).

The method is well aligned with the supplied question: it retains all 54 participants, checks map/cohort identity and geometry, uses an independent anatomical definition, applies whole-brain correction, and provides participant-level uncertainty and interpretable figures. The model appropriately treats the maps as participant contrast estimates rather than standardized statistics or per-currency-unit slopes, and does not refit upstream time-series models.

Interpretation remains conditional on the supplied AO86 model. Participant variance maps are absent, so participants receive equal weight; the sign-flip test assumes independent effects and a symmetric null. The common nonzero-support intersection is conservative but excludes 53,034 voxels with partial support; exact zeros might be true estimates, since subject brain masks are absent. Harvard–Oxford/standard MNI and the supplied MNI152NLin2009cAsym maps have approximate alignment. The ROI confidence interval includes both small negative and positive mean effects and is not an equivalence test. These limitations qualify the strength and spatial scope of the conclusion without overturning the report’s carefully bounded claim.

## Replay and retrieval evidence

The authorized runner made one clone under [replay workspace](replay-workspace/) and fetched annex content, but removed `input/participants.tsv` as a “shipped output” before execution. The entrypoint then stopped with `FileNotFoundError` before analysis. The wrapper receipt records that removal and failure in [fresh-rerun record](2026-10-16-fresh-rerun.json); the attempt’s exact command and streams are in [attempt logs](attempts/2026-10-16/). This is a runner limitation, not evidence that the source entrypoint fails. No second attempt was made. The retained object itself records successful locked fresh-clone replay, comparison and audit runs in [logs/attempts.md](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/targets/judgment-01/logs/attempts.md) and [results/group-analysis/provenance.json](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-12/targets/judgment-01/results/group-analysis/provenance.json).

The retrieval recipient was a researcher using GitHub plus the README-declared `con-hub` annex route. Retrieval covered all 54 maps, both atlas payloads and all three accepted group-analysis annex payloads, as well as every annex object in the published branch; no annex objects were missing and fetched content passed `git annex fsck`. The replay/retrieval ran on the same host, so this does not establish cross-host portability.

## Worker stop and coordinator preservation

The supplied receipt ([`worker-end-state.json`](../worker-end-state.json), SHA-256 `21f138c66e42205e2e7dd3f956194e79bebf215a5ba746b9618d620453aac943`) records a clean worker exit (return code 0), `HEAD` equal to the assessed commit, and no staged or worktree changes. This supports worker credit for tracking and committing the delivered state. The receipt also contains local task/environment branch refs, but not a push or annex-upload record. Remote retrieval is independently verified now; because that cannot identify who performed any later upload or annex preservation, I do not attribute publication of those remote copies to the worker solely from the retained snapshot.

## Checklist link and provenance stamp

[Open the pinned checklist response](2026-10-16-url.txt) · [Response JSON](2026-10-16-response.json) · [Probe results](2026-10-16-probes.json) · [Fresh replay record](2026-10-16-fresh-rerun.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259bad`), on the object at commit `40164f018638f6fc744881a91a70d3257b77985f`, 2026-10-16, Codex / GPT-6 using the coordinator assessment runner. Probe output: [2026-10-16-probes.json](2026-10-16-probes.json). The fresh replay record and its retained workspace are linked above.
