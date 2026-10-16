# Independent assessment: NARPS potential gains and brain activity

## Checklist verdicts

MUST: 5 met / 6 unmet / 6 partial / 0 not-checked (17 items). SHOULD: 0 met / 4 unmet / 2 partial / 2 not-checked / 1 not-applicable (9 items). MAY: 2 met / 0 unmet / 1 partial / 0 not-checked / 2 not-applicable (5 items). Partial MUST items do not satisfy the MUST requirement. No overall score is assigned.

## Scientific assessment

**Scientific adequacy: supported. Reported hypothesis outcome: no support for a positive vmPFC response under whole-brain FWE correction.** This is a supported absence of corrected evidence, not evidence that the effect is exactly zero.

The analysis uses the 54 equal-indifference participants as independent observations and their supplied gain-effect COPE maps as group-level data. The result summary reports no exclusions, 186,192 voxels in the final mask, and 9,999 whole-participant sign flips with the maximum positive t statistic controlling whole-brain familywise error at .05. It identifies vmPFC in advance with an explicit midline MNI box, and uses the whole-brain result for the hypothesis decision. The descriptive vmPFC mean is −0.0026 COPE units (95% t interval −0.0219 to 0.0167); no vmPFC voxel survives correction (the in-box peak has max-T FWE p=.7742). These results support the stated conclusion that the supplied analysis does not establish a positive vmPFC effect.

The same whole-brain test finds 24 corrected positive voxels in three descriptive clusters, with its maximum at MNI (−26, −102, −3.6), well posterior to the stated vmPFC region. The report does not misattribute that finding to vmPFC. Its independent SciPy spot checks, per-map QC table and two figures make the inferential and descriptive claims inspectable. Key evidence: `scientific-report.md`, `research-protocol.md`, `analysis/analyze.py`, `results/primary_v2_template_mask/summary.json`, `results/primary_v2_template_mask/input_qc.csv`, `results/primary_v2_template_mask/whole_brain_fwe_voxels.csv`, and `figures/primary_v2_template_mask/`.

The conclusion is conditional on the fixed AO86 first-level maps and their gain/loss modeling. The upstream gain modulator was centered and variance-normalized, so COPE units are not change per currency unit. The one-sample model treats participant effects as group observations and assumes exchangeability/symmetry for sign flips; participant variance maps are unavailable. Requiring nonzero support in all participants avoids treating background zeros as observations but excludes 5.2% of the template brain mask. The vmPFC interval crosses zero, so a small positive or negative effect remains compatible with the data. This is not an equivalence test or a claim of no neural response. The coordinator-supplied study guidance also notes that whole-brain-corrected inference is required by the original analysis instructions; the delivery follows that requirement.

## Replay and delivery integrity

The delivery manifest matched the complete workspace exactly: 1,140 paths checked, with no missing, extra or hash-mismatched paths (`manifest-verification.json`). Assessment used the unchanged stopped workspace, including untracked deliverables and annexed data; no source bytes were repaired.

Replay was **not checked**. The declared single attempt used the README command, the supplied Python 3.13.16 environment and the 11 explicitly listed generated outputs, with a 7,200-second timeout, 5 GB retrieval limit, and the frozen helper’s 1e-6 relative tolerance for numeric CSV cells. NIfTI, PNG and JSON outputs would have been compared by exact SHA-256. The helper raised `ValueError: Materialization requires a new destination` before copying or invoking the target because the attempt workdir had been pre-created to preserve logs. This is an assessor-side setup error; no target behavior or replay output was observed. The failed command and stderr are retained in `replay-attempt-01/`, and no retry was made.

## Worker-stop attribution and access

The worker stop receipt reports a complete capture with no capture errors or omissions and associates it with commit `d857ab1302d13cb660a7a044af07141f44bfa9ba`. At that stop, Git tracked the input maps with git-annex, but the analysis code, report, protocol, figures and results were untracked; the probe's worker-stop status corroborates this. This makes tracking partial for the scientific delivery even though coordinator capture preserves it. Later coordinator preservation does not earn worker credit. Package versions and command are recorded in the summary, but the only documented interpreter is an absolute path outside the object, and no environment manifest/lockfile is included. No worker-declared route for retrieving the complete study object or environment was found.

The intended recipient is a researcher using the routes in `input/sources.json` and `README.md`. From the assessment host, representative public HTTP HEAD checks for a NeuroVault map, pinned GitHub metadata and methods, and both TemplateFlow files returned 200. These checks establish current endpoint reachability from this host only, not full-byte retrieval, another-host access, worker publication, or object-wide artifact coverage. The full code/report/results/environment do not have a declared worker retrieval route, and the captured Git configuration has no remote. See `access-record.json` and its per-command stdout/stderr.

## Highest-priority changes

1. Add and track a complete, pinned environment specification and instructions for recreating it. This is needed to reconstruct the scientific computation and closes MUST 003, 006, 010, 013, 015–017 and SHOULD 006–008.
2. Track the analysis, protocol, report, figures and derived outputs at worker stop, retaining annex for large maps. Otherwise the Git revision does not identify the delivered scientific result. This closes MUST 004 and improves SHOULD 001.
3. Replace the absolute interpreter path with a portable documented launcher, and state host requirements and installation steps. This makes the entrypoint actionable to another researcher and closes MUST 007, 009, 011 and 017.
4. Publish an authorized retrieval route for the complete study object and declare reuse terms. Current public routes cover inputs/templates only. This addresses MUST 016 and the extra license finding.
5. Add a recurring check in a clean, disposable environment once the environment is declared. The present delivery documents rerunning but does not establish regular or isolated reconstitution; this addresses SHOULD 002, 004 and 005.

## What is already done well

- The analysis joins exactly 54 participant IDs to one map each, checks hashes and geometry, reports exclusions and support, and preserves per-map QC (`analysis/analyze.py`; `results/primary_v2_template_mask/input_qc.csv`).
- The group test follows the requested whole-brain positive FWE standard, and the vmPFC definition is explicit and not selected from the observed peak (`research-protocol.md`; `results/primary_v2_template_mask/summary.json`).
- The report carefully explains COPE scaling, upstream limitations and why a nonsignificant vmPFC result does not establish no effect (`scientific-report.md`; `input/upstream-methods.md`).

## Per-item record

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `judge-target.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/manifest-verification.json` | All captured workspace content is under the workspace root; manifest verification found no extra or missing paths. |
| must/002 | S.1 | met | judgement | `README.md`, `analysis/analyze.py` | All 54 maps and metadata are included within the root and reachable by the analysis; templates are local files. |
| must/003 | S.1 | unmet | probe:env-spec-tracked | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | The code depends on Python packages, but the delivered object has no environment file or linked software module. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/worker-end-state.json` | Git versions only part of the delivery: analysis, report, protocol, figures and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `.git/annex`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | Git-annex stores the 54 binary participant maps; the probe found no large binary blobs in Git. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+judgement | `results/primary_v2_template_mask/summary.json`, `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | The result summary records the command, script and input hashes, and package versions, but no exact environment specification links the run to a reconstructable environment. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | README gives a usage command, but installation and acquisition instructions for its absolute-path environment are missing. |
| must/008 | A.1 | met | probe:entry-point+judgement | `README.md`, `analysis/analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | The README points to the analysis script as the starting point and documents its command. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `analysis/analyze.py`, `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | Analysis paths are root-relative, but the documented interpreter command hard-codes an absolute host path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | No dependency or environment specification is delivered; package names in prose rely on an external preinstalled environment. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | The required host-specific interpreter location is stated, but OS and other host requirements are not specified. |
| must/012 | P.2 | met | probe:platform-assumptions+judgement | `README.md`, `input/upstream-methods.md` | README identifies Python 3.13.16 and the required scientific Python packages; data and template files are shipped. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/manifest-verification.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | No environment file is present in the complete stopped delivery, so no specification is tracked alongside the code. |
| must/014 | P.3 | unmet | judgement | `README.md`, `research-protocol.md` | No command or process for updating and tracking environment specifications is documented. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/primary_v2_template_mask/summary.json`, `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | Package versions are recorded in the result summary, but no exact environment specification is included for reconstruction. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/manifest-verification.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/worker-end-state.json` | The study object contains no environment specification to share; coordinator-provided runtime access does not establish worker publication. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `README.md` | README gives an invocation and package names but does not tell a researcher how to obtain the exact environment. |
| should/001 | T.2 | partial | probe:tree-clean+judgement | `.git/annex`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | Git-annex tracks input maps, while the analysis, report and derived outputs are untracked at worker stop. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | No CI configuration or recurring manual test record was found; the retained evidence is insufficient to establish whether testing occurs regularly. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | Inputs, code, templates, results and figures have distinct directories, but there is no separate environment module. |
| should/004 | E.1 | not-checked | judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/replay-record.json` | No delivered record establishes a worker run in a fresh container, batch job or clean virtual machine. |
| should/005 | E.1 | unmet | judgement | `README.md`, `analysis/analyze.py` | The documented run uses a pre-existing interpreter; no disposable environment is created per execution. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | No exact environment specification exists to reconstitute or test. |
| should/007 | D.2 | unmet | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/manifest-verification.json`, `README.md` | No environment specification or archived runtime artifact is included in the research object. |
| should/008 | D.2 | unmet | judgement | `README.md` | No process for updating and tracking an environment specification is documented. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/access-record.json` | N/A: the delivered inputs and declared data/template routes are public; no restricted data or software is identified. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j01/attempt-01/judgment/probes.json` | N/A: no independently maintained project component is linked as a module; data and template dependencies are included in the root. |
| may/002 | M.2 | met | judgement | `README.md`, `research-protocol.md` | README explains how input, analysis, external templates, results and figures relate. |
| may/003 | M.2 | partial | judgement | `README.md`, `research-protocol.md` | Directories separate inputs, code, external templates and outputs, but no interfaces or independent update rules are defined. |
| may/004 | M.2 | not-applicable | judgement | `README.md` | N/A: there are no independently maintained modules that need a composition mechanism. |
| may/005 | M.2 | met | judgement | `README.md`, `research-protocol.md` | README and protocol give a usable map of the object and explain the output folders. |


## Flagged findings

- `must/006`, `must/007`, `must/008`, `must/009`, and `should/003`: the automated probes primarily inspected tracked Git paths and missed meaningful untracked scientific artifacts in the complete stop-state delivery. The human verdicts use those artifacts and the worker-stop receipt; probe limitations are retained in `2026-10-16-probes.json`.
- `should/008`: duplicates the environment-update question in `must/014`; the same unmet process is recorded by design.

## Not checked

- `should/002`: a CI configuration was not recognized, and the delivery has no recurring manual test record; that does not rule out all testing outside the retained object. Recurring run records would settle it.
- `should/004`: the delivery does not establish whether a worker fresh-environment run occurred. The assessor replay never reached target execution; a worker run record or clean-environment CI record would settle it.
- Scientific replay: unavailable because of the retained assessor setup error described above. This is separate from scientific adequacy.

## Goals, kind and assumptions

**Assumption, not confirmed with a human:** the goal is to answer the supplied NARPS Hypothesis 1 question using the fixed 54 participant maps; the primary object kind is a study, whose product is a scientific inference and its supporting artifacts. This follows the user-provided brief and `README.md`.

## Checklist, provenance and records

Checklist version 0.3.1 (stamped-checklist-schema v0.3.1, commit `af259bad237fa57b856417db8dba45a1b283a527`). Assessment workflow `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, Codex / gpt-6.1-sol, 2026-10-16. Object commit: `d857ab1302d13cb660a7a044af07141f44bfa9ba`; complete delivery manifest SHA-256 `a870dc3c816f624dcd1ecd9e513fe56b76cf182e109a2f95963749235a4df8d7`, captured 2026-10-16T06:48:11.174906Z. The delivery is a study; this is not an attribution to any treatment or assignment. No treatment assignment was inferred. No assistance exposure was apparent in the scientific and protocol artifacts used for grading.

- [Checklist app URL](2026-10-16-url.txt)
- [Machine-readable response](2026-10-16-response.json)
- [Probe results](2026-10-16-probes.json)
- [Access record](access-record.json)
- [Replay record](replay-record.json)
- [Manifest verification](manifest-verification.json)
