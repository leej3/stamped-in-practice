# Independent assessment: NARPS gain effect and vmPFC

## STAMPED verdict line

MUST: 5 met / 1 partial / 11 unmet / 0 not-checked / 0 not-applicable (17 items). SHOULD: 1 met / 2 partial / 5 unmet / 0 not-checked / 1 not-applicable (9 items). MAY: 1 met / 0 partial / 3 unmet / 0 not-checked / 1 not-applicable (5 items). These are item verdicts, not an overall score.

## Scientific assessment

**Scientific adequacy: qualified.** The reported result is **no positive whole-brain-corrected vmPFC support**. The analysis provides a defensible absence of evidence for a positive vmPFC response under its stated group model and correction, while not establishing equivalence to zero or absence of gain coding.

The worker included all 54 equal-indifference participants, checked map finiteness and matching geometry, and reported no exclusions. They used an equal-weight one-sample *t* analysis (df=53) and one-sided participant sign flips with max-*t* family-wise correction over a 90% nonzero-coverage mask. This addresses the required whole-brain correction. The 24 corrected voxels form small posterior clusters, away from the independently specified 10-mm sphere centered at MNI [0, 44, -10]. In that descriptive sphere, the mean estimate is -0.013 map units (95% participant-level *t* interval [-0.044, 0.018]). The effect maps are correctly treated as cope-like estimates, not *t/z* statistics or currency-unit slopes.

The interpretation is appropriately qualified by the absent participant variance maps, sign-exchangeability assumption, finite permutation sample, data-derived coverage mask, and operational sphere definition. No material inference error was identified. The analysis does not show that effects are zero; the interval includes positive and negative values. The fixed upstream model and its separate gain/loss regressors constrain what these maps measure.

Evidence: [report.md](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j02/content/workspace/report.md), [group analysis code](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j02/content/workspace/code/group_analysis.py), [summary.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j02/content/workspace/results/summary.json), [participant QC and ROI table](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j02/content/workspace/results/participant_qc_and_roi.tsv), [FWE clusters](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j02/content/workspace/results/fwe_clusters.tsv), and [permutation maxima](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j02/content/workspace/results/permutation_max_t.tsv).

## Delivery and attribution

The complete captured delivery validated against the delivery manifest and worker stop receipt: capture status complete, no recorded omissions/errors, commit `2906eaca49c5a00d3df4b0c2dcd59eba9c8a3fb8`. The inspected workspace manifest has no reference limits. A first manual verification attempt was malformed and reported false mismatches because it constructed paths incorrectly and expected a nonexistent symlink field; this was an assessor-side verifier error, not a delivery mismatch. The frozen `delivery_snapshot.validate_capture` check then confirmed the capture and stop-receipt identity.

At worker stop, the five substantive output groups (`code/`, `figures/`, `report.md`, `results/`, and `.codex/`) were untracked. The worker did use Git and Git-annex, but the scientific report, code and results were not committed, so they do not earn version-tracking credit. The full capture preserves them as assessment evidence. No worker publication route or remote is recorded; coordinator preservation and delivery to this assessor do not establish worker publication or access. The captured repository config has no `remote.origin.url`.

The report lists Python and package versions, but no dependency declaration, lockfile, install instructions, or environment identity is supplied. The retained worker session history records one failed and six successful analysis-script executions using a coordinator-supplied shared interpreter. That establishes repeated worker execution but not a portable exact environment identity: the command points to a host-specific interpreter path, and no manifest hash is linked to the outputs. The environment was supplied as a common resource, not captured or published by the worker. The worker did not provide an authorized retrieval route for the analysis deliverables or environment. Input source links identify the original published maps and metadata, not a retrieval route for this analysis object.

The intended recipient for access assessment is a researcher using a worker-declared authorized route. No such route was found in the report, sources, stop receipt or captured Git config. The required scope would include the report, script, figures, results, participant metadata/methods and all 54 maps. Only the local coordinator-provided captured copy was tested; independent-host access was not established. Anonymous access was neither required nor tested. See [access record](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j02/attempt-01/judgment/access.json).

The workspace contains `.codex/` skill material and `.entire/` session-history material, which disclose AI/tooling assistance. This exposure was not used as grading evidence. No treatment assignment was inferred or reported.

## Replay

**Not checked; zero attempts.** The report identifies `code/group_analysis.py` and gives software versions, but supplies no installation instructions or portable environment declaration. The exact invocation appears in the retained session history, not the report. The script also calls Nilearn's MNI template loader without documenting whether the template is cached or retrieved. Under the supplied rules, constructing an environment or assuming these packages are available would exceed scope. No outputs were removed and no source files were changed.

The candidate invocation and the exact generated outputs identifiable from the script/report are recorded in [replay.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j02/attempt-01/judgment/replay.json). The frozen helper was not invoked because its prerequisites could not be established. Scientific replay therefore remains unavailable; this does not invalidate the inspected scientific report or outputs.

## What to improve first

1. Add a versioned, installable environment specification and document setup, host/network requirements, and how to use it. This addresses must/003, must/007, must/010–017 and supports a bounded replay.
2. Commit the analysis script, report, figures and results at worker stop; keep large maps in Annex. This closes must/004 and makes the complete scientific delivery visible in version history.
3. Add a documented run command and a compact execution record tying outputs to code and the exact environment. This addresses must/006 and must/008 and makes scientific provenance inspectable.
4. Record repeated workflow/environment checks and, if practical, run them in an isolated fresh environment. This addresses should/002, should/004 and should/006.

## What is already strong

- The scientific report distinguishes whole-brain corrected inference from a descriptive vmPFC ROI and avoids claiming equivalence from a nonsignificant ROI result.
- The full analysis artifacts include participant QC, coverage mask, effect and inference maps, permutation maxima, cluster summaries and figures.
- The supplied 54 large participant maps are represented by internal Git-annex links with captured payloads; inputs, code, results and figures are visibly separated in the workspace.

## Per-item STAMPED verdicts

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `judge-target.json`, `input/data/` | All delivered inputs, code, report, figures, and results are nested under the workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz`, `probes.json` | All 54 map links resolve to retained Annex objects inside the common root; no external data route is needed. |
| must/003 | S.1 | unmet | probe:env-spec-tracked+judgement | `report.md`, `probes.json` | The report names packages and versions, but no environment spec includes the external software dependencies. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `probes.json`, `worker-end-state.json` | Git was used, but report, code, figures, and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probes.json`, `input/data/` | The 54 large participant maps use Git-annex links and retained payloads. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+probe:run-env-linked+judgement | `.entire/metadata/01a143a3-31fb-7263-b4ca-bcf92756e9df/full.jsonl`, `report.md` | Session history records successful runs in the shared supplied Python environment, but no portable environment identity or manifest digest links results to an exact specification. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `report.md`, `probes.json` | The report links artifacts but gives no installation and usage instructions or executable setup route. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `code/group_analysis.py`, `probes.json` | The report identifies code/group_analysis.py as the analysis script, a clear starting point in this small study. |
| must/009 | P.1 | met | probe:no-abs-paths | `code/group_analysis.py`, `probes.json` | The analysis script derives paths from its own location and uses relative project paths. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `report.md`, `probes.json` | Required scientific packages are listed in prose but absent from any dependency/environment specification. |
| must/011 | P.1 | unmet | judgement | `code/group_analysis.py`, `report.md` | The documented route leaves host assumptions unstated, including the Nilearn template availability/network prerequisite. |
| must/012 | P.2 | unmet | judgement | `report.md`, `probes.json` | There is no README or environment specification with setup requirements; the report’s package list is not an installable requirements route. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probes.json`, `worker-end-state.json` | No environment specification is included in the worker’s version-controlled state. |
| must/014 | P.3 | unmet | judgement | `report.md`, `probes.json` | No dependency-update/regeneration process is declared, and no such updates are tracked. |
| must/015 | D.1 | unmet | probe:run-env-linked | `report.md`, `probes.json` | No frozen environment artifact or specification lets another researcher reconstruct the reported runtime. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `.git/config`, `access.json`, `probes.json` | The worker supplied no accessible environment specification or declared authorized route for obtaining one. |
| must/017 | D.1 | unmet | judgement | `report.md`, `access.json` | No documentation explains how to obtain and use an environment specification. |
| should/001 | T.2 | met | judgement | `probes.json`, `.git/config` | Git and Git-annex are used for code/history and large participant-map content. |
| should/002 | A.2 | partial | probe:ci-present+judgement | `.entire/metadata/01a143a3-31fb-7263-b4ca-bcf92756e9df/full.jsonl` | Repeated manual runs are recorded during one work session, but no ongoing or recurring test record shows the workflow is checked regularly. |
| should/003 | M.1 | partial | probe:modules-separated | `probes.json`, `report.md` | Inputs, code, results, and figures have separate directories, but the layout is not fully separated: no environment module, and the report sits at root. |
| should/004 | E.1 | unmet | judgement | `.entire/metadata/01a143a3-31fb-7263-b4ca-bcf92756e9df/full.jsonl`, `replay.json` | Recorded runs use the existing shared coordinator environment; no fresh container, clean VM, or isolated-environment test is recorded. |
| should/005 | E.1 | unmet | judgement | `code/group_analysis.py`, `report.md` | The delivered workflow has no mechanism that creates a disposable environment for each run. |
| should/006 | D.2 | unmet | probe:ci-present+probe:run-env-linked | `report.md`, `probes.json` | There is no exact environment specification to reconstitute and test. |
| should/007 | D.2 | unmet | judgement | `probes.json`, `report.md` | No environment artifacts (container, lockfile, or archived environment) are included. |
| should/008 | D.2 | unmet | judgement | `report.md`, `probes.json` | No environment update process is declared or tracked; same finding as must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: no restricted data or software is identified in this study delivery. |
| may/001 | M.2 | not-applicable | judgement | `probes.json`, `input/sources.json` | N/A: there are no independently maintained project subcomponents; ordinary runtime packages and input datasets are assessed elsewhere. |
| may/002 | M.2 | unmet | judgement | `report.md` | The directory layout is apparent, but documentation does not explain module relationships or recombination. |
| may/003 | M.2 | unmet | judgement | `code/group_analysis.py`, `report.md` | No independently updateable module boundaries or dependency contracts are documented. |
| may/004 | M.2 | unmet | judgement | `code/group_analysis.py`, `probes.json` | No composition mechanism is documented; the project is one direct script with no module orchestration. |
| may/005 | M.2 | met | judgement | `report.md` | The report links the script, data methods, summary, QC, maps, permutation table, clusters, and figures. |

## Flagged probe disagreements

- **must/002:** the subdataset probe did not check Annex-backed dataset links because it found no submodules. The complete capture shows 54 relative links to in-root Annex payloads, so the item is met; the probe's submodule test does not answer dataset reachability.
- **must/003:** the tracked-file probe reports no environment specification, while the untracked report does list package versions. That list does not include an installable declaration, so the unmet verdict stands.
- **must/006:** the probe missed untracked products and session history. The retained history records repeated runs in the supplied shared environment; partial credit reflects this linkage, while the absence of a portable manifest identity prevents a met verdict.
- **must/007–008:** the probe only recognized tracked paths. The complete report links the single analysis script, supporting must/008; it gives no installation or usage instructions, leaving must/007 unmet.
- **must/009:** the path probe scanned tracked text only; direct inspection of the untracked script confirms project-relative paths.

## Not checked and limitations

- **should/002:** repeated manual runs are recorded in one work session, but no ongoing or recurring test practice is evidenced. A recurring CI, scheduled, or documented regular manual check would settle it.
- **Access:** no worker-declared retrieval route to test. A route and independent-host check covering all required artifacts would settle accessibility.
- The assessor replay was not necessary to complete the scientific assessment. Assessor malfunction was limited to the initial manual manifest verifier attempt; the frozen capture validator subsequently succeeded. No target behavior was inferred from that malfunction.

## Kind, links, and assessor stamp

Object kind: **study** (a group-level scientific question answered with supplied data and computation). See [response JSON](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j02/attempt-01/judgment/2026-10-16-response.json), [frozen probe output](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j02/attempt-01/judgment/probes.json), [checklist link](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j02/attempt-01/judgment/2026-10-16-url.txt), [scientific assessment JSON](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j02/attempt-01/judgment/scientific-assessment.json), and [replay record](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j02/attempt-01/judgment/replay.json).

Produced by `assess-alignment-with-stamped-principles` 0.2.0 with `stamped-conventions` 0.2.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the captured study at commit `2906eaca49c5a00d3df4b0c2dcd59eba9c8a3fb8`, 2026-10-16, OpenAI Codex API / GPT-6. Probe output: `probes.json`. The response carries the validated delivery-manifest URI and hash. Worker-session run history is cited in must/006 and should/002/004; its coordinator-supplied common environment is not credited as worker environment capture or publication. The [worker stop receipt](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j02/attempt-01/worker-end-state.json) records the worker HEAD and complete capture; the [delivery manifest](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j02/manifest.json) retains the captured path inventory and hashes.
