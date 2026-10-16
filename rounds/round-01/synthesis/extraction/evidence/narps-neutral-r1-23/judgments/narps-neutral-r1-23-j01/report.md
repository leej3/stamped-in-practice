# Independent assessment — 2026-10-16

## STAMPED verdict

**MUST:** 6/17 met, 0 partial, 11 unmet, 0 not-checked. **SHOULD:** 1/9 met, 1 partial, 6 unmet, 0 not-checked, 1 not-applicable. **MAY:** 3/5 met, 2 partial, 0 unmet, 0 not-checked, 0 not-applicable. Not-applicable items are reported separately; no overall score is assigned.

## What to fix first

- Add a pinned environment specification, dependency list and setup instructions. The current report names a supplied Python environment, and the script imports scientific packages and fetches nilearn resources; this closes must/003, must/006, must/010–015 and must/017.
- Publish a worker-authorized route that includes the complete study, inputs and environment. The delivery has no project remote or retrieval instructions; this closes must/016 and supports must/001–003.
- Make the final scientific state a clear commit on the checked-out project branch and identify that revision in the report. A local Entire checkpoint preserves the work, while the worker's checked-out base branch still reports the science directories as untracked; this improves must/004 and T.2 traceability.
- Add a clean-environment reconstitution check and a documented dependency-update process. The worker transcript records one development session and no fresh-environment test; this closes should/002, should/004–008 and the duplicate must/014.

## What is already good

- The complete delivery carries all 54 gain maps and participant metadata, with internal relative Git-annex links and source checksums in `input/sources.json`.
- The group analysis uses participants as independent units, checks image geometry and finite values, restricts inference to shared brain support, and applies one-sided whole-brain max-T correction.
- The report gives a cautious null interpretation, makes its vmPFC convention explicit, discusses the absence of participant variance maps, and includes useful QC tables, numeric results and figures.

## Per-item assessment

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `report.md`, `input/data/sub-001_hypo1_cope.nii.gz` | Study files and all 54 relative map links sit under the workspace root; annex payloads are internal. |
| must/002 | S.1 | met | judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `input/participants.tsv` | All 54 input maps and metadata are reachable within the common root; no external input is needed. |
| must/003 | S.1 | unmet | judgement | `analysis/group_analysis.py`, `report.md` | The analysis imports external Python packages and nilearn resources, but the delivery has no environment specification. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean+judgement | `git:5dfd349391c3887ce53b7c442529ae51455ef232`, `.entire/logs/entire.log` | Git contains the worker-created Entire checkpoint with code, report and results; the checked-out base branch remained dirty. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `git ls-tree -r -l HEAD`, `input/data/sub-001_hypo1_cope.nii.gz` | Git-annex stores the 54 participant maps; their payloads are included in the captured delivery. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `git:5dfd349391c3887ce53b7c442529ae51455ef232`, `report.md` | Worker run records show success, but identify only an external shared Python path, not an exact pinned environment specification. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `report.md`, `analysis/group_analysis.py` | report.md gives a run command, but no instructions explain how to obtain or install the required Python environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `analysis/group_analysis.py` | The report documents analysis/group_analysis.py as the executable starting point and names its outputs. |
| must/009 | P.1 | met | probe:no-abs-paths | `analysis/group_analysis.py`, `probe:no-abs-paths` | The analysis uses paths relative to its own workspace; probe found no host-specific absolute paths in tracked text. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analysis/group_analysis.py`, `report.md` | No dependency declaration covers imported packages or the atlas/template resources fetched by nilearn. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `report.md`, `analysis/group_analysis.py` | The documented route omits system and service assumptions, including the Python environment and nilearn atlas/template availability. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `report.md`, `analysis/group_analysis.py` | No system requirements or dependency list is documented; the report only names a supplied Python environment. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-23-j01/manifest.json` | No environment file or package specification is tracked in the delivered workspace. |
| must/014 | P.3 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-23-j01/manifest.json` | No environment specification or runnable update process is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `git:5dfd349391c3887ce53b7c442529ae51455ef232`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-23-j01/manifest.json` | The worker recorded an executable path but no pinned package manifest, lockfile, or container identity. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `report.md`, `.git/config`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-23/judgments/narps-neutral-r1-23-j01/attempt-01/judgment/2026-10-16-access-record.json` | No worker-declared authorized route publishes the study object or its environment; the checkout has no remote. |
| must/017 | D.1 | unmet | judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-23-j01/manifest.json` | No instructions explain how to obtain or use an environment specification; none is included. |
| should/001 | T.2 | met | judgement | `git:5dfd349391c3887ce53b7c442529ae51455ef232`, `input/data/sub-001_hypo1_cope.nii.gz` | Git and git-annex are used in the same repository for code, text and large input maps. |
| should/002 | A.2 | unmet | judgement | `git:5dfd349391c3887ce53b7c442529ae51455ef232` | The worker log shows one development session with retries, not a recurring workflow test or scheduled check. |
| should/003 | M.1 | partial | probe:modules-separated | `input`, `analysis`, `results`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-23-j01/manifest.json` | Input data, analysis, results and figures have separate directories; no separate environment module is supplied. |
| should/004 | E.1 | unmet | judgement | `git:5dfd349391c3887ce53b7c442529ae51455ef232` | The successful worker runs used a shared pre-existing Python environment; no fresh container or clean environment test is recorded. |
| should/005 | E.1 | unmet | judgement | `analysis/group_analysis.py`, `git:5dfd349391c3887ce53b7c442529ae51455ef232` | The workflow runs directly in a shared Python environment and does not create a disposable environment. |
| should/006 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-23-j01/manifest.json`, `git:5dfd349391c3887ce53b7c442529ae51455ef232` | No exact environment specification is included or regularly tested for reconstruction. |
| should/007 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-23-j01/manifest.json` | No environment image, binaries, or package artifacts are archived in the study object. |
| should/008 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-23-j01/manifest.json` | No dependency-update process exists because no environment specification is supplied. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: supplied public research derivatives and software are not identified as restricted. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-23/judgments/narps-neutral-r1-23-j01/attempt-01/judgment/command-logs/source-route-head.stdout` | NeuroVault is identified as the independent input source; input/ has a clear boundary and its cited map URL returned HTTP 200. |
| may/002 | M.2 | partial | judgement | `report.md` | Directories separate inputs, code and outputs, but documentation does not explain modular boundaries or recombination. |
| may/003 | M.2 | partial | judgement | `analysis/group_analysis.py`, `report.md` | The code reads inputs and writes outputs through stable directories, but no independent update contract is documented. |
| may/004 | M.2 | met | judgement | `analysis/group_analysis.py` | The analysis script composes the supplied maps and metadata into result tables, maps and figures. |
| may/005 | M.2 | met | judgement | `report.md` | report.md gives a runnable entrypoint and points readers to the numerical summary and QC table. |

## Flagged items

- **must/004** (`mapping-questioned`, `probe-overridden`): `tree-clean` measured an unmodified checkout; the item asks whether version control is used. The worker's local Entire checkpoint commit records code, report, figures and results, while the checked-out branch remains dirty.
- **must/006** (`probe-overridden`): `derived-have-records` missed untracked outputs. The worker transcript does record successful runs, but not an exact environment specification or lock identity.
- **must/007** (`mapping-questioned`): the entry-point probe required README/Makefile names; `report.md` is an equivalent document, but omits environment installation instructions, so the unmet verdict remains.
- **must/008** (`probe-overridden`): the analysis script and documented command are a clear start point, contrary to the probe result.
- **must/011, must/012** (`probe-overridden`): the platform probe found no known platform-specific command, but did not answer whether the documented route states host, package and external-resource requirements. The report and code leave these unspecified.
- **must/014, should/008** (`upstream-duplicate`): the pinned checklist repeats the same environment-update question.
- **may/001** (`probe-overridden`): the probe missed direct upstream dataset links. `input/sources.json` identifies the NeuroVault collection and map URLs; one representative map URL returned HTTP 200.

The extra license probe is recorded separately from the checklist: the study does not state reuse terms.

## Scientific assessment

**Adequacy: supported. Reported hypothesis outcome: not supported under the required whole-brain-corrected inference.** These labels address separate questions: the reported conclusion is that the supplied maps do not provide corrected evidence for a positive vmPFC effect, not that the true effect is exactly zero.

The delivered analysis includes all 54 equal-indifference participants, validates matching image shapes/affines and finite values, intersects shared nonzero support with a resampled MNI152 brain mask (186,400 voxels), and tests a positive one-sample group effect with 10,000 participant-level sign flips and whole-brain maximum-t FWE control. The vmPFC definition is an independently chosen Harvard-Oxford Frontal Medial Cortex subset (y ≥ 0, z ≤ 0), used for anatomical interpretation rather than ROI-only inference. The reported vmPFC mean is −0.00914 (95% t interval −0.03989 to 0.02162), with no vmPFC voxel surviving whole-brain correction. Twenty-three corrected voxels occur in three small occipital-pole clusters; they do not support the vmPFC hypothesis.

The interpretation is appropriately limited to these participant COPE maps and their fixed upstream model. Those estimates are not slopes per currency unit; gains and losses were modeled separately, and gains spanned twice the loss range. No participant variance maps are supplied, so participants receive equal weight and group variance combines participant differences with first-level estimation error. Sign-flip inference assumes symmetric participant errors under the null, and 10,000 permutations limit p-value resolution. The report states these limits and explains what a non-significant vmPFC result does not establish.

The worker's Entire session checkpoint records an early failed run, subsequent code changes, and successful final runs whose printed summary matches the shipped outputs. The initial failure is preserved in the worker transcript; it is not the final delivered analysis. This is worker execution evidence, not an independent replay. The captured Entire telemetry identifies Codex/model assistance. This exposure is recorded as context only; assistant narrative and model identity did not affect scientific or STAMPED verdicts. Machine records of the worker checkpoint and command executions were used only as execution/versioning evidence.

## Delivery boundary and manifest

The worker stop receipt records return code 0, a complete capture and no declared omissions. The delivery manifest SHA-256 is `9370db020f9b437ca3a96b2e171d89d3d52cc94554a3d62d23da0b0ca71fcb59`; `judge-target.json` has no reference limits. All 1,152 manifest entries were checked, including the captured external support files. No paths were missing. The checkout also records a `core.hooksPath` outside the captured root; I did not follow or execute those original hooks, and they were not needed for the scientific analysis. One mismatch and two extra sidecars are assessor-induced: after reading the workspace, I ran Git status/log/config before manifest verification; that inspection changed `.git/annex/keysdb/db` and created `db-shm`/`db-wal`. The database was 53,248 bytes, but its SHA-256 differed from the recorded value. I did not restore or otherwise repair the source. The other listed workspace files, symlink targets and external support files matched. This limits confidence in the captured annex database/VCS internals; scientific results, inputs and their relative links were not altered by this inspection.

At worker stop, the checked-out branch was at `afb62884c70115b6e46a92ddcd1d17bbf4f33544`; `analysis/`, `figures/`, `report.md` and `results/` appeared untracked there. The worker's Entire session log records a local checkpoint commit `5dfd349391c3887ce53b7c442529ae51455ef232` just before stop, containing the final scientific materials and session transcript. This worker-created local checkpoint earns tracking credit, but is not a published access route. Coordinator delivery/preservation is not credited as worker sharing.

## Access

The intended recipient is a researcher using the worker's declared authorized route; anonymous access is not required. No route for the complete project is declared in the report or Git configuration, and no project remote is configured. The upstream map route in `input/sources.json` was checked: one NeuroVault map URL returned HTTP 200 with a 1,794,522-byte Content-Length. The tested host scope is `neurovault.org` for that representative map only. The required complete artifact set is code, all participant maps and metadata, results/figures, and the environment; the data route does not publish this complete study object. See [the access record](2026-10-16-access-record.json).

## Not checked and measurement availability

No replay attempt was made. The documented command is `python analysis/group_analysis.py`, but the only environment description is “supplied Python environment”; there is no worker-supplied package lock or environment recipe, and the script fetches atlas/template data through nilearn. Reconstructing that environment would require adding a declaration or substituting an assessor environment, both outside scope. The [replay record](2026-10-16-replay-record.json) lists the explicit generated outputs and comparison rule that would apply if the prerequisite were available. Replay availability is **not checked**, not a scientific failure. Testing a retrieval route for the complete study is also not possible because the worker declared none; the upstream input URL check does not settle project access. No checklist item was left not-checked: concrete presence/absence evidence or an argued not-applicable status was available for each. Scientific adequacy and the reported conclusion were assessable from the final code, outputs and worker execution record. Item attainment is reported only in the table above.

## Assumptions, kind and scope

**Assumption (not confirmed by a separate human reply):** this is a **study** whose product is a group-level answer to NARPS Hypothesis 1, based on fixed participant maps. The goal comes from the retained scientific task and `report.md`. All seven STAMPED principles were considered, with emphasis on result provenance, complete scientific inputs, reproducible execution and retrieval. No treatment assignment was inferred or reported.

No treatment assignment was inferred or reported. Target contents were treated as evidence rather than instructions. The checklist assesses the captured worker stop state, not later coordinator preservation.

## Checklist URL and provenance

[Open the completed checklist](2026-10-16-url.txt). The machine-readable answers are in [2026-10-16-response.json](2026-10-16-response.json); the scientific assessment is in [2026-10-16-science.json](2026-10-16-science.json). Probe output: [2026-10-16-probes.json](2026-10-16-probes.json). The complete command ledger and retained command outputs are in [assessment-command-log.md](assessment-command-log.md) and `command-logs/`.

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259bad`), on the original complete delivery at Git commit `afb62884c70115b6e46a92ddcd1d17bbf4f33544`, 2026-10-16, Codex API/frozen assessment runner; model identity was not exposed by the harness. Runner pins and capture identity are recorded in `2026-10-16-response.json`.
