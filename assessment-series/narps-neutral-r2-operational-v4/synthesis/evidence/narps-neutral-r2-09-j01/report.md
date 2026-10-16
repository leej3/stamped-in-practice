# Independent assessment — NARPS equal-indifference gain analysis

**Verdicts:** MUST: 5 met / 3 partial / 9 unmet / 0 not-checked (17). SHOULD: 1 met / 2 partial / 5 unmet / 0 not-checked / 1 not-applicable (9). MAY: 3 met / 1 partial / 0 unmet / 0 not-checked / 1 not-applicable (5).

## What to fix first

1. Track the analysis script, report and generated results in the worker's Git state; this makes the scientific delivery addressable and reviewable (must/004).
2. Include a pinned dependency specification, connect it to each result-producing run, and document how a researcher obtains it; this closes the main reproduction gap (must/003, 006, 010, 012–017; should/006–008).
3. Replace the host-specific interpreter path with an obtainable route and state the supported host requirements (must/007, 011, 012, 017).
4. Declare and test an authorized researcher route covering all annex payloads, code, reports and outputs (must/016).

## What is already good

- The worker delivered all 54 fixed participant maps through Git-annex and kept integrity checks and cohort metadata alongside them (`input/sources.json`, `input/participants.tsv`).
- The protocol makes the estimand, coverage mask, whole-brain correction, anatomical proxy, uncertainty and upstream limitations inspectable (`analysis/protocol.md`).
- The attempt history records a corrected permutation-statistic scaling bug, and the worker's same-environment replay and independent SciPy spot check are recorded (`results/attempts/attempt_history.md`, `results/replay_validation.txt`).

Assessment date: 2026-10-16. **Assumption (not confirmed):** this is a study-stage group-analysis project. Its goal is to assess the positive gain effect in vmPFC for the NARPS equal-indifference group and leave an inspectable report, code and results. No human guidance was attached.

## Identity and scope

Canonical capture SHA-256: `427104fd0fe3dc76fa4cb6bc017f1e7bfe618cc1709cd37c9a1ce9c875b0c7cf`. Canonical original captured HEAD: `a724b670072a95a253e752be8336783858df768a`. The delivery manifest reports a complete capture with no omissions or capture errors. I inspected the operational copy and cite original evidence as `capture#content/workspace/<path>`; the launcher validates the canonical capture before and after. The probe draft and this report are assessment products, not worker artifacts.

Scope included the complete stopped workspace, worker-stop receipt, frozen probe set, one documented replay on a separate complete copy, and a check for a worker-declared access route. No scientific target file was intentionally changed. A read-only post-inspection comparison found `.git/annex/keysdb/db` changed and regular-file `db-shm` and `db-wal` present; these are the only changes and are permitted operational metadata. They are inspection-induced, not worker evidence. No logical database equivalence is claimed. The first ad hoc comparison misclassified annex symlink hashes; its false-positive record is retained as `operational-integrity.json`, and the corrected comparison is `operational-integrity-final.json`. The captured tree contains ignored `.codex/` and `.entire/` session/tooling material; this indicates recorded assistant/session tooling, but I did not use its contents or identifiers as grading evidence. The only external paths I followed were frozen assessor/runtime inputs. Original external skill symlinks and external Git hook pointers are retained by reference only, per `judge-target.json` limits. The worker-stop receipt identifies a stopped process but does not itself record an authorized retrieval route.

## Scientific assessment

**Scientific adequacy: supported.** The whole-brain one-sided max-T sign-flip test is an appropriate group-stage test of mean positive participant gain-effect estimates, applies correction over the full common fitted support, and uses participants rather than voxels as independent units. Image checks, all-54 retention, coverage accounting, an independently defined vmPFC proxy, uncertainty, and a restrained interpretation make the reported lack of corrected vmPFC support defensible. The ROI estimate is near zero with a wide interval, and no corrected voxels overlap the stated proxy; this supports “not established,” not a claim of a true zero effect. The report's own outcome is: “This group analysis found no support for a positive vmPFC effect.”

The maps are first-level gain-modulator estimates, not currency-unit BOLD changes; the upstream gain regressor was normalized, separate gain/loss models were used, and participant variance maps are unavailable. The nominal gain range is twice the loss range; this test does not estimate a gain-versus-loss sensitivity contrast. Sign-flip inference assumes independent participants and approximately symmetric null errors. The common-support mask excludes voxels lacking nonzero fitted support in any participant; this is transparent and avoids treating outside-coverage zeros as observations, though exact zeros are assumed to mark outside support. The 24 corrected positives are posterior occipital and near the support edge, not evidence for the vmPFC hypothesis. The Harvard–Oxford Frontal Medial plus Subcallosal proxy is a reasonable explicit boundary choice, not a unique vmPFC definition. The display template is standard MNI152 while maps are MNI152NLin2009cAsym; this could affect visual alignment, not the reported voxelwise calculation. The conclusion is conditional on the supplied AO86 maps and fixed upstream model. The original NARPS instructions call for whole-brain-corrected hypothesis decisions and group maps ([instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

**Scientific adequacy evidence:** Supported: the reported lack of corrected vmPFC support follows from whole-brain-corrected inference and a concordant descriptive ROI estimate, while the report does not claim that the true effect is zero.

**Reported hypothesis outcome (verbatim from the delivered report):** This group analysis found no support for a positive vmPFC effect.

## Inspection, replay and access

The analysis protocol and code are present as uncommitted files at worker stop. The code validates each supplied map checksum, matching dimensions/affines and finite values; it intersects fitted support; computes a one-sample t field; uses 9,999 seeded participant sign flips and a one-sided maximum-t familywise correction; and summarizes a separate atlas proxy. The shipped summary reports 54 participants, no exclusions, 198,029 common-support voxels, 24 corrected positives, zero corrected vmPFC voxels, and a vmPFC mean of 0.0027 with 95% t interval [−0.0217, 0.0270] (`analysis/run_group.py`, `analysis/protocol.md`, `results/summary.json`, `report.md`).

One fresh-copy replay was run with the exact README entrypoint and the documented common interpreter. It used the frozen runner's copy of the canonical complete delivery; only the 12 named generated summary/map/table outputs in `replay-plan.json` were removed in that copy. The entrypoint exited 0 in 29.2 seconds; all 12 selected outputs were byte-identical to the shipped outputs. Exact-byte agreement is stricter than the planned numeric tolerance, so no tolerance fallback was needed; logs, figures and prose were excluded. This establishes same-host repeatability for those selected outputs, not independent environment reconstruction or cross-host portability. The helper performed no prefetch; the code's Nilearn atlas/template functions may access their reference data, and helper-managed byte limits do not meter such entrypoint downloads. No time-series scans were retrieved. Full command, stdout/stderr, runner record and retained replay copy are in this assessment directory.

**Access:** intended recipient is a researcher using a worker-declared authorized route. No worker route is declared in the README or stop receipt, and no worker publication/access endpoint was available to test. Required coverage would include this workspace, all 54 annex payloads, code, outputs and any runtime/reference data needed by the entrypoint. The local operational copy was readable on this host, but it is coordinator delivery to the assessor and does not establish worker-side access. Tested worker-route host scope: none.

## Worker-stop attribution and boundary

At stop, `HEAD` was `a724b670072a95a253e752be8336783858df768a`; `README.md`, `analysis/`, `figures/`, `report.md`, and `results/` were untracked, while `.codex/` and `.entire/` were ignored. Thus the delivered analysis itself was not versioned at worker stop. The 54 maps and cohort metadata under `input/` and the common interpreter are supplied resources; the untracked report, analysis code, figures and results are worker-stop deliverables. The maps were Git-annex links to payloads within the workspace's annex store. Results include a run-attempt history and same-environment replay-validation note, but no exact archived environment specification or run-to-environment pin. The README points to an absolute common-interpreter path and gives a launch command, but does not explain how a researcher obtains or recreates that environment. No worker publication route is recorded. These statements concern the captured worker-stop state; later coordinator commits, annex handling, uploads and retention are preservation only and are not credited as worker practice. The stop receipt (`worker-end-state.json`, SHA-256 `a9631f7d2444a4a5398d2f95105b851d14464b4522080cd2349ffdc40ab614f5`) reports no capture omissions/errors but only process stop metadata, so other worker action attribution is limited.

## STAMPED checklist

Each citation below uses the canonical capture SHA-256 above and a capture-relative path. Verdicts assess worker-stop practices; replay evidence is not attributed to the worker.

| Item | Verdict | Evidence and reason |
|---|---|---|
| must/001 | met | `README.md`, `input/`, `analysis/`, `results/`: all delivered project files are nested under the workspace root. |
| must/002 | met | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz`, `.git/annex/objects/`: the inputs and annex payloads resolve within the captured workspace. |
| must/003 | unmet | `README.md`, `results/summary.json`: the executable common environment is external; no environment package specification or in-boundary software module is supplied. |
| must/004 | partial | `README.md`, `analysis/run_group.py`, `report.md`, `results/`: Git exists, but all analysis, report and result paths were untracked at stop. |
| must/005 | met | `input/data/`, `.git/annex/objects/`: the 54 large participant maps use Git-annex links and captured payloads. |
| must/006 | unmet | `results/summary.json`, `results/attempts/`: version strings and run logs exist, but no exact environment spec is linked to the result-generating run. |
| must/007 | partial | `README.md`: it documents a run command and usage, but not how to install or obtain its absolute-path interpreter. |
| must/008 | met | `README.md`, `analysis/run_group.py`: the README names the executable group-analysis entrypoint and command. |
| must/009 | met | `analysis/run_group.py`: code derives input/output paths from the script root; no system-specific data path is hardcoded in the script. |
| must/010 | unmet | `README.md`, `results/summary.json`: package versions are recorded, but there is no environment specification declaring all dependencies. |
| must/011 | unmet | `README.md`, `results/summary.json`: a host path/platform is observable, but OS and host assumptions are not documented as requirements. |
| must/012 | unmet | `README.md`: no clear system-requirement and dependency list or installable environment spec is provided. |
| must/013 | unmet | workspace root, `README.md`: no environment specification is present in the captured project tree. |
| must/014 | unmet | workspace root, `results/attempts/attempt_history.md`: there is no environment spec or tracked process for updating one. |
| must/015 | unmet | workspace root, `README.md`: no frozen environment specification enables another user to reconstruct the run environment. |
| must/016 | unmet | `README.md`, workspace root: no worker-published environment or authorized retrieval route is documented. |
| must/017 | partial | `README.md`: a command points to a supplied interpreter, but users are not told how to obtain or reconstruct its environment. |
| should/001 | met | `.git/`, `input/data/`: Git tracks small files and Git-annex manages large files within one repository boundary. |
| should/002 | partial | `results/attempts/attempt_history.md`, `results/replay_validation.txt`: multiple attempts and a same-environment replay are recorded, but no regular automated test schedule is shown. |
| should/003 | partial | `input/`, `analysis/`, `results/`, `figures/`: inputs, code and derived files have directory separation, but no separate environment module exists. |
| should/009 | not-applicable | `input/upstream-methods.md`, `input/sources.json`: no restricted data/software is identified in this public-data analysis. |
| should/004 | unmet | `results/replay_validation.txt`, `README.md`: the worker's replay uses the same interpreter; no worker fresh-container/VM/batch test is recorded. |
| should/005 | unmet | `README.md`: execution reuses an externally supplied fixed interpreter; it does not create a disposable environment. |
| should/006 | unmet | workspace root, `results/summary.json`: package versions are recorded, but there is no exact environment specification to reconstitute and test. |
| should/007 | unmet | workspace root, `README.md`: no environment artifact or archived environment specification is included. |
| should/008 | unmet | workspace root, `results/attempts/attempt_history.md`: no environment-update process or tracked specification exists; duplicate of must/014. |
| may/001 | not-applicable | `input/`, workspace root: no independently maintained submodule/component is used; the fixed maps are included through annex. |
| may/002 | met | `README.md`: it explains the relationship among fixed inputs, protocol, analysis code, results and figures. |
| may/003 | partial | `analysis/run_group.py`, `input/`, `results/`: directory roles are clear, but code and derived modules are not independently versioned or released. |
| may/004 | met | `README.md`, `analysis/run_group.py`: the documented entrypoint composes the input directory and produces the result/figure directories. |
| may/005 | met | `README.md`: users are directed to the report, methods, protocol, script, results and figures. |

**Extra probe finding (not a checklist item):** no license/reuse declaration was present in the complete captured workspace; reuse terms are unstated.

## Flagged items

- **must/006:** the derived-file probe only saw committed paths and missed the untracked outputs; direct review found logs and package versions, but no exact environment link.
- **must/007 and must/008:** the entry-point probe missed the untracked README and script; the complete capture documents and supplies a clear script entrypoint, so its unmet results were overridden.
- **must/009:** the path probe scanned tracked text only; direct review of the untracked script confirms root-relative data/output paths, so the verdict is met but the probe route is incomplete.
- **should/002 and should/006:** the CI probe did not cover equivalent repeated-test or environment-reconstitution evidence; direct review found several attempts but no regular test schedule or exact environment spec.
- **should/003:** the module probe saw only tracked roots and missed the untracked analysis/results/figures directories; partial status reflects those directories, with no separate environment module.
- **must/014 and should/008:** the checklist repeats the same environment-update question; both answers repeat the same unmet finding by design.

## Not checked

None. The worker retrieval route is not checked as an item verdict because no route was declared; its availability limitation is recorded in the access section.

## Goals and kind

The supplied task defines the goal as group-stage inference for a positive potential-gain effect in vmPFC for the NARPS equal-indifference group. I assume the object kind is **study**, not confirmed by a human; it answers that question from fixed participant maps and compute. The emphasis therefore covers scientific inputs, provenance and portability as well as the analysis result.

## Checklist URL and provenance stamp

[Open the completed STAMPED checklist](checklist-url.txt). The full per-item record is [response.json](response.json), with probe output in [probes.json](probes.json) and the replay receipt in [replay-record.json](replay-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1, on canonical capture `427104fd0fe3dc76fa4cb6bc017f1e7bfe618cc1709cd37c9a1ce9c875b0c7cf` (original HEAD `a724b670072a95a253e752be8336783858df768a`), 2026-10-16, Codex native session / gpt-6-luna; frozen assessment runner SHA-256 `7d16037883b5ec059caa5cb4828f64ca926a3ddb37fd086267caf69c3cb01913`. Probe output: `probes.json`.

No overall score is assigned.
