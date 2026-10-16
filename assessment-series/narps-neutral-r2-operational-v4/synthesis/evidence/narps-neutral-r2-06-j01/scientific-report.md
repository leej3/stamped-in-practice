# Independent assessment of the NARPS gain-effect delivery

**STAMPED assessment date:** 2026-10-16  
**Project kind:** study  
**Canonical capture:** SHA-256 `200c46ed7c6fb6320bec58e218778c6d7e426d286019e27eca034e3bb18915be`  
**Captured HEAD:** `78d5939f13b4caeecb07a75518298c6c9c44cfd1`  
**Worker stop:** capture complete, exit 0, no capture errors or omissions; stop receipt SHA-256 `7ec0450bec9378ccc7495a25262a42e1bf9c7e6cad6f775eef1d2ea6bf2cbd34`.

The capture-relative paths below are relative to the complete original capture. Unless labeled an operational observation, each citation identifies evidence in the canonical capture above. Worker artifacts were assessed at the recorded stop state, including uncommitted, untracked and ignored files. The original captured HEAD is only one part of that state.

## Scientific assessment

Scientific adequacy: supported. The reported lack of positive vmPFC evidence is consistent with the participant-level analysis, its stated uncertainty, and the required whole-brain correction; it does not establish a zero effect.

Worker's reported hypothesis conclusion: The supplied gain-effect maps do **not** support a positive vmPFC response to increasing potential gain. (Verbatim from capture path `content/workspace/report/report.md`.)

The report uses all 54 equal-indifference participants, models each independent participant map with a one-sample group t test, and tests a positive alternative over the shared nonzero support with Bonferroni family-wise correction. The protocol specifies an operational vmPFC box and describes it as anatomical rather than data-derived; the capture does not independently establish when that choice was first made. The ROI estimate is negative, its 95% interval crosses zero, and its descriptive p value is not substituted for whole-brain inference. No voxel in the ROI survived correction. The 11 corrected positive voxels are reported outside vmPFC. This supports a conclusion of no detected positive vmPFC effect under the declared analysis, not a claim of biological absence. (Capture paths: `content/workspace/protocol.md`, `content/workspace/report/report.md`, `content/workspace/results/run_metadata.json`, `content/workspace/results/vmPFC_roi_summary.csv`, `content/workspace/results/wholebrain_summary.csv`, `content/workspace/results/wholebrain_significant_voxels.csv`.)

The supplied methods say these are participant contrast parameter estimates from a gain regressor that was mean-centered and variance-normalized upstream, not change per currency unit or standardized statistics. Separate gain and loss models and the absence of participant variance maps limit the estimand and precision model. The report states these limits and does not turn nonsignificance into equivalence. The maps' common MNI geometry, participant matching, coverage intersection, finite-value checks, checksums and no-exclusion decision are documented. The code implements those checks and the declared group model. Figures distinguish descriptive means, corrected whole-brain results and participant ROI variability. (Capture paths: `content/workspace/input/upstream-methods.md`, `content/workspace/protocol.md`, `content/workspace/code/analyze.py`, `content/workspace/report/validation.md`, `content/workspace/results/participant_qc.csv`, `content/workspace/figures/group_mean_slices.png`, `content/workspace/figures/wholebrain_fwe_positive.png`, `content/workspace/figures/vmPFC_roi_distribution.png`.)

I found no material inference error in the reported conclusion. Adequacy applies to group inference conditional on the supplied fixed upstream maps; it does not independently validate the upstream first-level model or establish effects per currency unit. Existing outputs are delivery evidence, not replay evidence.

## Measurement availability and replay

The supplied stop receipt reports a complete capture with no errors or omissions. The canonical and operational initial manifest digests both equal `200c46ed7c6fb6320bec58e218778c6d7e426d286019e27eca034e3bb18915be`; they identify the same initial bytes. A post-inspection inventory matched all workspace entries except regular files `.git/annex/keysdb/db`, `db-shm` and `db-wal`, which are separately classified operational metadata. Their byte changes do not establish logical database equivalence and are not worker evidence. The successful comparison is retained in `integrity/operational-integrity.json`. Two earlier comparison-script versions had manifest-normalization errors; they are retained as assessor-tooling errors and were superseded by the normalized comparison, not interpreted as capture mismatches.

Replay is **not checked**. Before the attempt, I recorded the documented command, prerequisites, explicit generated scientific output selection and comparison rule in `replay/declaration.json`. The single frozen helper invocation failed before making the fresh copy: I had pre-created its required new destination, producing `ValueError: Materialization requires a new destination`. The analysis command did not run, so there is no scientific replay result or output comparison. This assessor setup error is retained in `replay/command.stderr` and `replay/replay-record.json`; I made no second attempt. It does not count against the target or alter the scientific adequacy judgment.

A later response-edit invocation also failed once because the runner detected a locally changed frozen `pixi.toml`; the required frozen `check` then passed and subsequent response stamping and validation succeeded. This assessor-runtime error did not affect the target. Its stderr is retained at `response-edits/30.stderr`.

Automated probes are in `probes/probes.json`. They ran against the operational copy and are observations, not worker actions. The first probe invocation used a mistaken `--path` option and failed before probing; its output is preserved separately. The valid probe ran after the required frozen check. Manual judgments below include complete untracked and ignored workspace contents where relevant and override probe heuristics when they only scanned the active Git tree.

## Worker practices, attribution and access

The stop receipt records HEAD `78d5939f13b4caeecb07a75518298c6c9c44cfd1`. In the operational copy, the analysis code, reports, figures and results are outside that commit on the active branch. The captured `.entire` log records an automated local shadow checkpoint of 21 new files. Since those files were not on the stop HEAD and the checkpoint is not a worker-declared publication route, I count Git use as partial and do not count the checkpoint as publication. The captured `.git/config` contains no remote. The complete stop workspace still contains the untracked analysis artifacts and they were assessed normally. The stop receipt identifies 58 seeded input paths and 61 supplied files, including the participant maps and metadata; those coordinator-supplied assets are not credited as worker-created versioning or annex practice. No subsequent coordinator preservation commit or publication is counted. (Capture paths: `content/workspace/.git/HEAD`, `content/workspace/.entire/logs/entire.log`, `content/workspace/code/analyze.py`, `content/workspace/report/report.md`, `content/workspace/results/run_metadata.json`.)

The analysis script uses workspace-relative paths and the inputs are available through relative links into the captured annex store. I did not follow the original absolute/external references listed in `judge-target.json` reference limits; this leaves their separate skill contents outside scope. The captured `.git` is a directory, not an external Git pointer, and all Git commands were run against the operational copy only. The large maps and annex setup are supplied coordinator inputs, so the probe's `large-in-annex` observation earns no worker-practice credit; no worker-produced binary over 10 MiB was identified. The worker documented actual package versions, Python, macOS and architecture, and result metadata includes inputs plus code/protocol hashes. However, the required common Pixi environment and its manifest are outside this object; no local installable specification, lockfile or environment archive is present. Result provenance is therefore partial, while environment portability, distribution and obtaining instructions are unmet or incomplete as itemized below. (Capture paths: `content/workspace/environment.md`, `content/workspace/results/run_metadata.json`, `content/workspace/code/analyze.py`, `content/workspace/input/sources.json`.)

For access, the intended recipient is a researcher using the authorized route the worker declared. No worker-declared route for the complete project was found. The source inventory's NeuroVault URLs are coordinator-supplied input provenance, not evidence that the worker published the analysis package. A no-body HEAD request to one map at `neurovault.org` returned HTTP 200; this tests one input artifact on that host only. It does not cover code, metadata, environment, outputs, report or instructions. The full access record is `access/access-record.json`.

The captured `.entire` session metadata/logs reveal assistant use. I record this exposure without using it as scientific grading evidence. No treatment assignment is inferred or reported.

## STAMPED item attainment

Counts by requirement level are reported separately; there is no overall score. `N/A` means the item does not apply to worker-produced practice in this delivery, not that the coordinator-supplied input is absent. Evidence paths in the table use the canonical capture SHA-256 in the report header; probe paths are explicitly operational observations.

### MUST (17 items)

| Item | Status | Evidence and reason |
|---|---|---|
| must/001 | met | `content/workspace/protocol.md`, `content/workspace/code/analyze.py`: one workspace root; code derives paths from its own location. |
| must/002 | met | `content/workspace/input/sources.json`, `content/workspace/input/data/`: all 54 map links and metadata are inside the workspace and the script reads them. |
| must/003 | unmet | `content/workspace/environment.md`, `content/workspace/code/analyze.py`: analysis software is named but the shared environment is outside the object. |
| must/004 | partial | `content/workspace/.git/HEAD`, `content/workspace/.entire/logs/entire.log`: Git and an automated local checkpoint exist, but analysis artifacts were not on the worker stop HEAD. |
| must/005 | not-applicable | `content/workspace/input/sources.json`: annexed maps are supplied coordinator inputs; no worker-produced large binary was identified. |
| must/006 | partial | `content/workspace/results/run_metadata.json`, `content/workspace/environment.md`: versions, platform and code/input hashes are recorded, but no frozen environment specification is linked to results. |
| must/007 | unmet | `content/workspace/environment.md`: it gives a run command, but there is no README or Makefile with install and usage instructions. |
| must/008 | met | `content/workspace/code/analyze.py`, `content/workspace/environment.md`: clear documented analysis entrypoint. |
| must/009 | met | `content/workspace/code/analyze.py`: code uses paths relative to the script-derived workspace root. |
| must/010 | unmet | `content/workspace/environment.md`, `content/workspace/code/analyze.py`: no installable workspace environment specification covers dependencies. |
| must/011 | partial | `content/workspace/environment.md`: records Python, macOS and architecture, but not a self-contained host setup. |
| must/012 | partial | `content/workspace/environment.md`: lists packages/platform but leaves setup requirements in an external shared environment. |
| must/013 | unmet | `content/workspace/environment.md`: points outside the object; no tracked environment specification is present. |
| must/014 | unmet | `content/workspace/environment.md`: no specification update process is documented. |
| must/015 | unmet | `content/workspace/results/run_metadata.json`: package versions are recorded but no frozen environment artifact or immutable identifier is supplied. |
| must/016 | unmet | `content/workspace/environment.md`: the environment path is external and no worker-declared sharing route is supplied. |
| must/017 | unmet | `content/workspace/environment.md`: an invocation is given for an already-existing shared environment, not a route or instructions to obtain it. |

**MUST counts:** 4 met / 4 partial / 8 unmet / 0 not-checked / 1 not-applicable.

### SHOULD (9 items)

| Item | Status | Evidence and reason |
|---|---|---|
| should/001 | partial | `content/workspace/.git/HEAD`, `content/workspace/.entire/logs/entire.log`: one Git repository and local checkpoint, but not a complete active worker branch or publication route. |
| should/002 | not-checked | `content/workspace/report/validation.md`: a final validation is described, but regular testing cadence cannot be established. |
| should/003 | partial | `content/workspace/code/analyze.py`, `content/workspace/environment.md`: input, code, results and figures are separated; environment is external and module boundaries are incomplete. |
| should/004 | unmet | `content/workspace/environment.md`, `content/workspace/report/validation.md`: final run is in the shared host environment; no clean container, batch, VM or cloud test is recorded. |
| should/005 | unmet | `content/workspace/environment.md`: workflow uses the common environment and does not create a disposable environment per run. |
| should/006 | not-checked | `content/workspace/report/validation.md`: a final rerun is described, but recurring clean environment reconstruction is not established. |
| should/007 | unmet | `content/workspace/environment.md`: environment artifacts are external; no lockfile or image is archived in the object. |
| should/008 | unmet | `content/workspace/environment.md`: no dependency-update process; same requirement as must/014. |
| should/009 | not-checked | `content/workspace/input/sources.json`: origins are listed, but reuse restrictions are not; applicability cannot be grounded without rights metadata. |

**SHOULD counts:** 0 met / 2 partial / 4 unmet / 3 not-checked / 0 not-applicable.

### MAY (5 items)

| Item | Status | Evidence and reason |
|---|---|---|
| may/001 | not-applicable | `content/workspace/input/data/`: annex links are in-root inputs, not independently composed Git submodules or subdatasets. |
| may/002 | partial | `content/workspace/protocol.md`, `content/workspace/environment.md`: major parts and outputs are described, but no complete architecture/composition map is provided. |
| may/003 | not-checked | `content/workspace/protocol.md`: distinct directories exist, but independently updateable boundaries and compatibility contracts are not documented. |
| may/004 | not-applicable | `content/workspace/protocol.md`: this is one analysis workflow without separately maintained components to compose. |
| may/005 | partial | `content/workspace/environment.md`, `content/workspace/protocol.md`: command and layout are documented, but there is no complete module navigation guide. |

**MAY counts:** 0 met / 2 partial / 0 unmet / 1 not-checked / 2 not-applicable.

### Probe overrides and duplicated item

- **must/004:** probe marked the active tree unclean. The full capture also includes a local automated Entire checkpoint, so Git use is partial; active-branch tracking remains incomplete.
- **must/005:** probe saw annex storage. That is coordinator-supplied data plumbing, not attributable worker practice; the worker-produced-large-file item is not applicable.
- **must/006:** probe did not recognize the run metadata. Manual reading finds partial provenance (exact package versions and hashes, no frozen environment specification).
- **must/008:** probe scanned tracked paths and missed the complete untracked `code/analyze.py` entrypoint and usage notes.
- **must/011:** probe only scanned commands; manual reading finds some host assumptions documented but the setup remains incomplete.
- **should/003:** probe saw only input separation; full workspace also separates code, figures and results, while environment remains external.
- **may/001:** probe did not identify modules; manual reading finds no independently composed Git submodule or subdataset.
- **should/008** repeats must/014 by checklist design.

## Extra finding

The automated license probe found no license file or dataset license field in tracked paths. The source inventory identifies origins but not reuse terms; this is a separate undeclared-license finding and also limits the applicability judgment for should/009. See `probes/probes.json` and `content/workspace/input/sources.json`.

## Record links and assessor stamp

- [Response JSON](response.json)
- [Probe results](probes/probes.json)
- [Checklist app URL](checklist-url.txt)
- [Scientific judgment record](scientific-judgment.json)
- [Access record](access/access-record.json)
- [Replay declaration and record](replay/declaration.json), [replay status](replay/replay-record.json)
- [Operational integrity record](integrity/operational-integrity.json)

Produced with the frozen external assessment runner pinned at source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28` and environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`; checklist 0.3.1. Object: study, original HEAD `78d5939f13b4caeecb07a75518298c6c9c44cfd1`, captured 2026-10-16T15:36:32.611449+00:00, canonical capture manifest `200c46ed7c6fb6320bec58e218778c6d7e426d286019e27eca034e3bb18915be`. Probe output: `probes/probes.json`.
