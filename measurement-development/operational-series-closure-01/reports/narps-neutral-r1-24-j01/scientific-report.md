# Independent assessment: NARPS potential gain and vmPFC

Assessment date: 2026-10-16. Assessed the complete captured workspace as a **study**: a group-level scientific answer with code, inputs, results, and report. The declared goal is to assess a positive parametric gain effect in vmPFC in the equal-indifference cohort using 54 supplied participant maps and whole-brain corrected inference. This goal and kind are taken from the task brief and worker README; no human guidance was attached for confirmation.

Canonical capture SHA-256: `76ac670f9e4cce6766e693dd8c5530c28998efb09d91bbeb09fbb3ef8198c311`. Original captured HEAD: `675620fed8a134102b1b07226fe39d67630ee6f7`. The stop receipt names the same capture digest and HEAD. The operational copy began byte-identical to the canonical capture. The assigned `judge-target.json` records only the captured external skill-directory links as references not to follow; retained input symlinks point within the workspace to annex objects. I did not follow external Git pointers or use any external `.git` hook path.

## Scientific judgment

Scientific adequacy category: supported.

Hypothesis conclusion: The supplied maps do **not support a positive vmPFC gain effect** in the NARPS equal-indifference group.

The report’s conclusion that the supplied estimates do not support a positive vmPFC gain effect is supported by a defensible group analysis. The protocol defines the target as a participant-level mean cope conditional on the supplied AO86 models, uses all 54 participants without outcome-based exclusions, limits the mask to common nonzero coverage, and tests positive effects using participant sign flips and a whole-brain maximum-*t* correction. The result reports no vmPFC voxel surviving whole-brain FWE (minimum ROI FWE *p*=0.780; zero significant ROI voxels), while the broader 90%-coverage sensitivity gives the same decision. The vmPFC ROI is independently defined from Harvard–Oxford parcels; the report acknowledges the atlas-space mismatch and broad orbital parcel.

The interpretation is appropriately bounded: the maps are normalized-modulator cope estimates, not currency-unit slopes; participant variance maps are absent; sign-flip inference assumes independent, sign-symmetric errors; and failure to reject is not evidence of equivalence or a true zero. The corrected whole-brain clusters are posterior and do not support the vmPFC hypothesis. Evidence: canonical capture `content/workspace/analysis/protocol.md`, `content/workspace/analysis/run_analysis.py`, `content/workspace/results/summary.json`, `content/workspace/results/sensitivity_90pct/summary.json`, `content/workspace/input/upstream-methods.md`, and `content/workspace/report/report.md`.

This outcome statement is retained separately from the adequacy category.

## Evidence boundary and worker stop state

The canonical manifest is complete, reports no capture errors or omissions, and identifies 1,226 entries. The worker stop receipt is complete and has no omissions. The operational starting manifest matches the canonical digest. The final inspection delta records a change only to `.git/annex/keysdb/db`; temporary `db-shm` and `db-wal` files also appeared during inspection and were absent at the final comparison. These are the separately classified operational metadata paths. No other path changed. This classification does not establish logical database equivalence. Probes and direct inspection observed the operational copy; those observations are not worker actions. At the worker stop, the scientific deliverables (`README.md`, `analysis/`, `figures/`, `report/`, `results/`) were untracked. The captured Git HEAD tracks the supplied cohort metadata and 54 input symlinks; it does not track the worker’s code, report, figures, or derived results. Accordingly, coordinator-seeded Git/annex inputs do not establish worker tracking of the scientific work. Probe output from the operational copy confirms those untracked paths (`tree-clean`) and that its HEAD has 54 annex pointers (`large-in-annex`); the latter is not credited as worker handling of generated outputs.

The capture identity and input map checksums are reported in `input/sources.json` and the analysis summaries. I did not read other workers’ artifacts or infer any assignment. 

## STAMPED findings

The full per-item checklist table, probe disagreements, item evidence, and encoded checklist link are in the response and URL files linked below. Key findings:

- The worker supplied an actionable analysis script and a report with an analysis protocol, 54-participant QC, exclusions table, machine-readable results, and figures. These were not committed at stop.
- The documented entrypoint is `analysis/run_analysis.py`, but the README instructs the reader to use a host-specific absolute Python path under a common-environment directory outside the delivery. The required environment specification, environment acquisition route, and exact result-to-environment provenance link are absent from the captured workspace.
- The participant maps are included through relative links to workspace-local annex objects. The worker-declared NeuroVault collection/API route was reachable from this assessment host: HEAD checks returned HTTP 200 for the collection, metadata API, and all 54 map URLs. This demonstrates access to the input data route only, not publication of code, results, figures, report, or environment. No credentials were supplied for this host check; anonymous access is not a requirement when a researcher has an authorized route.
- The generated binary NIfTI maps and compressed voxel table are in the worker’s untracked `results/` directory and are not handled by the captured annex pointers. No worker publication route for the complete study is declared.

## Replay and access measurements

No scientific replay was attempted. The first auxiliary all-files URL check stopped with a selector error because a non-map manifest entry had no `url`; no request was sent by that failed attempt. A corrected check selected the 54 `data/` map entries and all returned HTTP 200. The failed command output is retained in `commands/neurovault-head-all.stderr.txt`. The primary documented command is the absolute-path Python command in `content/workspace/README.md`; the README also documents a 90%-coverage sensitivity invocation. Its required atlas is fetched by the script with `nilearn.datasets.fetch_atlas_harvard_oxford(...)`; the recorded atlas lives in a host cache and is absent from the captured delivery. The frozen adapter performs no scientific-input retrieval, and no delivered atlas file or dependency declaration makes this prerequisite available. Running it would require supplying an unrecorded input. The candidate generated outputs and replay comparison rule are retained in `replay-record.json`; no output was removed and the inspection copy was not replayed.

The access record is `access-record.json`. Intended recipient: a researcher following the worker-declared authorized route. Tested host scope: this assessment host with network access on 2026-10-16, using metadata and HTTP HEAD requests only; no map payloads were downloaded. Required project coverage is the inputs, code, environment specification, report, results, and figures. Only the 54 input map URLs and collection metadata were reachable; the complete project has no worker-declared publication route.

## Scope limitations and integrity

The assessment is conditional on AO86’s supplied participant models and cannot revisit preprocessing or first-level estimates. The capture provides no participant variance maps. The runner could not establish a safe captured-delivery replay because the atlas prerequisite is not included. The current `judge-target.json` reference limits were consulted before any consideration of retained links; only internal relative input links were inspected. The canonical original identity and original HEAD are used in the response object, not any coordinator preservation commit.

## Stamp

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on capture `76ac670f9e4cce6766e693dd8c5530c28998efb09d91bbeb09fbb3ef8198c311`, original HEAD `675620fed8a134102b1b07226fe39d67630ee6f7`, 2026-10-16. Runtime: frozen assessment runner in `$STAMPED_ASSESSMENT_RUNNER`; assessor model identity was not supplied in the runtime metadata. Probe output: `probes.json`. See `response.json`, `scientific-judgment.json`, `replay-record.json`, and `access-record.json`.


## Checklist verdicts

MUST: 4 met / 2 partial / 11 unmet / 0 not-checked. SHOULD: 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable. MAY: 2 met / 1 partial / 1 unmet / 0 not-checked / 1 not-applicable. No overall score is assigned.

### What to improve first

1. Put the analysis code, report, figures, and derived outputs under worker version control; these are the scientific product and were untracked at stop (must/004, should/001).
2. Deliver a reproducible environment specification and link the run record to it; the absolute-path prepared environment is not available as a portable dependency (must/003, 006, 010, 013, 015–017; should/006–008).
3. Declare a complete publication/retrieval route for code, results, figures, report, and environment, not only source maps (must/016).
4. Add clear host requirements and installation instructions (must/007, 011, 012).

### What is already strong

- The scientific protocol defines the estimand, whole-brain max-*t* sign-flip test, coverage handling, and independent vmPFC annotation before inference (`content/workspace/analysis/protocol.md`).
- The analysis includes detailed participant checks, all 54 maps, no outcome-driven exclusions, a coverage sensitivity analysis, and SciPy cross-checks (`content/workspace/results/summary.json`, `content/workspace/results/sensitivity_90pct/summary.json`).
- The README provides a clear script entrypoint and navigates the results and methods (`content/workspace/README.md`).

### Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/README.md` | The complete delivered project files share the workspace root. |
| must/002 | S.1 | met | judgement | `content/workspace/input/sources.json` | The cohort and maps are present under the root; map links resolve to workspace-local annex objects. |
| must/003 | S.1 | unmet | judgement | `content/workspace/analysis/run_analysis.py` | The workflow imports external Python packages but the delivery contains no installable environment specification. |
| must/004 | T.1,T.3,T.5 | unmet | judgement | `content/workspace/README.md` | At worker stop, the analysis, report, figures, and generated results were untracked by Git. |
| must/005 | T.1,T.3,T.5 | unmet | probe:large-in-annex+judgement | `content/workspace/results/group_mean_cope.nii.gz`, `probes.json` | Coordinator-seeded annex pointers cover supplied inputs; worker-generated binary results remained untracked and outside annex. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `content/workspace/results/summary.json`, `probes.json` | Result summaries record package versions and platform, but no exact environment specification is linked to these runs. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `content/workspace/README.md`, `probes.json` | README gives usage instructions, but no environment installation or acquisition instructions are available within the delivery. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/README.md`, `probes.json` | The README identifies analysis/run_analysis.py as the primary starting point and gives its command. |
| must/009 | P.1 | met | judgement | `content/workspace/analysis/run_analysis.py` | The analysis script builds input and output paths relative to its own project root. |
| must/010 | P.1 | unmet | judgement | `content/workspace/README.md` | Package versions are listed in prose, but no delivered environment specification installs or resolves the dependencies. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `content/workspace/README.md` | The documented route assumes a host-specific absolute Python path and external prepared environment without portable host requirements. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `content/workspace/README.md` | README lists Python and package versions, but does not give system requirements or an obtainable environment. |
| must/013 | P.3 | unmet | judgement | `content/workspace/README.md` | No environment specification is included in the worker's captured project files or Git state. |
| must/014 | P.3 | unmet | judgement | `content/workspace/README.md` | No environment specification or dependency-update procedure is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `content/workspace/results/summary.json` | No frozen environment specification is included for exact reconstruction. |
| must/016 | D.1 | unmet | judgement | `content/workspace/README.md` | The worker declares no route for recipients to obtain the environment specification or complete study. |
| must/017 | D.1 | unmet | judgement | `content/workspace/README.md` | README says to use a pre-existing absolute-path environment but does not explain how recipients obtain it. |
| should/001 | T.2 | partial | judgement | `content/workspace/README.md` | Git/annex covers supplied input links, while worker code, prose, figures, and derived results were untracked. |
| should/002 | A.2 | not-checked | judgement | `content/workspace/README.md` | No cadence or repeated-testing record is established; worker execution history or a regular test schedule would settle this. |
| should/003 | M.1 | partial | judgement | `content/workspace/README.md` | Inputs, analysis, results, figures, and report have separate directories; no environment module is delivered. |
| should/004 | E.1 | not-checked | judgement | `content/workspace/results/summary.json` | No fresh replay was safe because the required atlas is absent from the captured delivery; a replay with that supplied prerequisite would settle this. |
| should/005 | E.1 | unmet | judgement | `content/workspace/README.md` | The documented route invokes one pre-existing environment and has no disposable-environment mechanism. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `content/workspace/README.md` | No exact environment specification exists in the delivery to reconstitute and test. |
| should/007 | D.2 | unmet | judgement | `content/workspace/README.md` | No environment artifact is archived in the workspace. |
| should/008 | D.2 | unmet | judgement | `content/workspace/README.md` | No environment update process is declared or tracked; this duplicate item repeats must/014. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: the captured study contains no restricted data or software component. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json`, `probes.json` | N/A: no independently maintained project modules are declared; the data are included in the workspace and packages are runtime dependencies. |
| may/002 | M.2 | met | judgement | `content/workspace/README.md` | README explains the inputs, analysis, results, figures, and report locations and links the analysis protocol. |
| may/003 | M.2 | partial | judgement | `content/workspace/analysis/run_analysis.py` | Input and output directories are separable, but code writes to fixed root-relative paths and there is no independent environment module. |
| may/004 | M.2 | unmet | judgement | `content/workspace/analysis/README.md` | The project uses a single analysis script and provides no module composition mechanism. |
| may/005 | M.2 | met | judgement | `content/workspace/README.md` | README links the input methods, analysis protocol, result summaries, and scientific report. |

### Flagged items

- **must/005:** `large-in-annex` counted coordinator-seeded input pointers, not worker-generated outputs.
- **must/006, must/015:** `run-env-linked` found no linked environment record; the result summaries record versions but no exact environment identity.
- **must/007, must/008:** `entry-point` scanned tracked files and missed the worker’s untracked README and analysis script; manual reading found usage but no install route.
- **must/011, must/012:** `platform-assumptions` only scanned for known platform-specific commands; the documented absolute environment path and missing host setup requirements required a reading.
- **should/006:** `ci-present` could not test reconstitution without a delivered exact environment specification.
- **must/014, should/008:** these duplicate the same environment-update question in the pinned checklist; both repeat the same unmet finding by design.
- **may/001:** `subdatasets-resolvable` left the item open because it found no submodules; the complete workspace has no independently maintained project modules, so this is not-applicable.

### Not checked

- **should/002:** regular test cadence cannot be established from the captured workspace; a worker execution or scheduled test record would settle it.
- **should/004:** no replay was attempted because the required atlas is absent and the frozen adapter does not retrieve scientific inputs; a replay with the captured atlas prerequisite would settle it.

### Goals and kind

Assumption from the task brief and README: this is a **study** answering the specified NARPS group-analysis question. The complete workspace is the relevant boundary. The scientific interpretation is supported, while worker tracking and distribution practices are not established by coordinator preservation.

Checklist URL: [open the checklist](2026-10-16-checklist-url.txt). Machine record: [response.json](response.json). Scientific category and excerpt record: [scientific-judgment.json](scientific-judgment.json).
