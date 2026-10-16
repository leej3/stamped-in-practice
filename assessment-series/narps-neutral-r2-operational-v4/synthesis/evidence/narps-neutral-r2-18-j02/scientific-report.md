# Independent assessment

Capture: `8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb`; original captured HEAD: `bfe069501c140673f38778116f34bc8a5c36366f`.

## STAMPED verdicts

MUST: 5 met / 2 partial / 10 unmet / 0 not-checked (17 items).
SHOULD: 0 met / 1 partial / 5 unmet / 2 not-checked / 1 not-applicable (9 items).
MAY: 2 met / 2 partial / 1 unmet / 0 not-checked / 0 not-applicable (5 items).

### What to fix first

1. Add and track a complete environment declaration and lockfile, including the scientific packages and host assumptions. Link the result run to that environment and document how recipients obtain it (must/003, /006, /010–/017; should/006–/008).
2. Commit the analysis code, report, notebook and results before handoff so the delivered version identifies the actual scientific work (must/004; should/001).
3. Add discoverable setup instructions and a repeatable clean-environment workflow, with recurring execution records (must/007; should/002, /004, /005).

### What the delivery does well

- Large inputs are annexed, and `sources.json` records the independently maintained NeuroVault collection boundary and per-map retrieval links. The analysis checks the 54 source-map checksums, participant uniqueness, image shape/affine and finite analysis values (`content/workspace/code/analyze.py`, SHA-256 `6c853f514b8fff58123d317c95da4249248601e6c61082987f2750dade1212ff`; `content/workspace/input/sources.json`, `919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`).
- Code, inputs and results occupy separate directories; the script uses workspace-relative paths and the report points to the code, notebook, provenance and outputs (`content/workspace/report.md`, SHA-256 `e1545efc76abf52ce79d0b979b9cc87db697efe6afda651426b827677d4832b7`).
- One documented replay of the full capture recreated the 11 selected outputs byte-for-byte in 22.2 seconds. See `replay-plan.md` and `replay-record.json`; shipped outputs were not counted as replay evidence.

### Per-item table


The table below was rendered from the validated response JSON. Its `capture://` evidence URIs include the canonical capture digest and capture-relative path.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/.git/HEAD` | All delivered workspace components sit under the common workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/code/analyze.py`, `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/input/sources.json` | All 54 maps and metadata are included under input/ and code resolves them with workspace-relative paths. |
| must/003 | S.1 | unmet | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/code/analyze.py`, `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md` | No worker-supplied environment specification includes the external Python packages. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/code/analyze.py`, `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-18-j02/attempt-01/worker-end-state.json` | At worker stop, report, code, notebook, and results were untracked; only supplied inputs were committed. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-18-j02/attempt-01/judgment/2026-10-16-probes.json` | Large participant maps are stored through Git annex in the captured repository. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/results/run.log`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-18-j02/attempt-01/judgment/2026-10-16-probes.json` | A run record exists, but it does not link the results or actions to an exact environment. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md` | report.md provides usage as an equivalent document, but not installation or environment acquisition instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md`, `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/code/analyze.py` | The report gives a clear starting command for code/analyze.py and also identifies the notebook. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/code/analyze.py` | The analysis script constructs inputs and outputs from its own root using relative paths. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/code/analyze.py` | Scientific dependencies are not declared in a delivered environment specification. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md` | The run documents BLAS/OpenMP thread variables, but omits host OS and system-library assumptions. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md`, `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/code/analyze.py` | No clear system-requirements or dependency list is supplied in the report or an environment specification. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/.git/HEAD` | No environment specification is included in version control or the captured workspace. |
| must/014 | P.3 | unmet | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md` | No environment update or regeneration process is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/results/run.log`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-18-j02/attempt-01/judgment/2026-10-16-probes.json` | No frozen package manifest, container digest, or equivalent exact environment record is supplied. |
| must/016 | D.1 | unmet | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md` | No worker-supplied environment artifact is shared for recipients to use. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md` | The report names an interpreter for use but does not explain how a recipient obtains the environment. |
| should/001 | T.2 | unmet | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/code/analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-18-j02/attempt-01/worker-end-state.json` | Git tracks supplied inputs, but not the worker-created code, report, notebook, or results at stop. |
| should/002 | A.2 | not-checked | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/results/run.log` | One stored run is present, but the complete delivery does not establish whether the workflow was tested repeatedly elsewhere; recurring run records would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/code/analyze.py`, `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/results/results.json` | Inputs, code, and results are separated into directories, but there is no environment module. |
| should/004 | E.1 | not-checked | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/results/run.log` | No captured record establishes a clean-container or clean-VM execution; a run-environment record would settle it. |
| should/005 | E.1 | unmet | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md` | The delivered workflow is a direct script invocation and contains no disposable-environment launcher. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r2-operational-v4/judgments/narps-neutral-r2-18-j02/attempt-01/judgment/2026-10-16-probes.json` | No environment specification exists to be regularly reconstituted and tested. |
| should/007 | D.2 | unmet | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/.git/HEAD` | No environment artifact is archived in the workspace. |
| should/008 | D.2 | unmet | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md` | No process for updating and tracking environment specifications is declared. |
| should/009 | M.4 | not-applicable | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/input/sources.json` | N/A: all declared data and software routes are public; there is no restricted component to isolate. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/input/sources.json` | The independent NeuroVault dataset has a clear input boundary and per-map retrieval links in sources.json. |
| may/002 | M.2 | partial | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md` | The report lists the input, code, notebook, and result artifacts, but does not explain how modules relate or can be recombined. |
| may/003 | M.2 | partial | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/code/analyze.py` | Directory boundaries exist, but the workflow is a single script with no documented independent module update contract. |
| may/004 | M.2 | unmet | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md` | No composition mechanism such as submodules or orchestration is provided. |
| may/005 | M.2 | met | judgement | `capture://8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb/content/workspace/report.md` | The report gives a reproducibility index linking the report, code, notebook, data provenance, and results. |

### Flagged items

- **must/002, may/001 — mapping-questioned.** The subdatasets probe checks Git submodules, while the frozen rule also accepts included or directly linked data. Inspection found the 54 local annexed maps, their explicit source links, and the input boundary, so both items are met.
- **must/006 — probe-overridden.** The derived-records probe looked only at tracked paths and marked the item not-applicable. The complete stop contains an untracked `results/run.log`, but it does not identify an environment, so must/006 is unmet.
- **must/007 — mapping-questioned.** The entry-point probe only recognized a README or Makefile. `report.md` is an equivalent instruction document and gives usage, but not installation or environment acquisition, so the item remains unmet.
- **must/008 — probe-overridden.** The probe missed the untracked script and report. The report identifies `code/analyze.py` and gives the starting command, so the item is met.
- **must/009 — probe-overridden.** The path probe scanned tracked text and missed the untracked analysis script. Direct inspection confirms its input and output paths are workspace-relative, so the item is met.
- **must/011, must/012 — probe-overridden.** The platform probe only scans command patterns. The report documents BLAS/OpenMP variables but no host OS/system-library assumptions or dependency list; the resulting partial/unmet verdicts come from reading the route and code.
- **must/015 — probe-overridden.** The run-environment probe had no named environment to check for a pin. The complete delivery contains no frozen package manifest or equivalent, so exact-environment capture is unmet.
- **should/003 — probe-overridden.** The module probe saw tracked paths only. In the full delivery, inputs, untracked code and results have separate directories, but no environment module exists; attainment is partial.
- **should/006 — probe-overridden.** The CI probe left this not-checked because no recognized CI file exists. The complete delivery contains no environment specification to reconstitute and test, so this item is unmet.

### Not checked

- **should/002:** one stored run is present, but repeated testing beyond the captured run cannot be established. Recurring run records or a maintained test workflow would settle this.
- **should/004:** no worker-stop record identifies a clean container, batch job, VM or cloud execution. A worker-generated environment/run record would settle this.

### Goals and kind

The goal is the supplied study task: evaluate the positive gain-modulator effect in vmPFC in the 54-person equal-indifference cohort at the group-analysis stage, with whole-brain correction and uncertainty/limitations. The object is a computational study containing source inputs, group-analysis code, results and a report. No human guidance was attached.

Checklist link: [`2026-10-16-url.txt`](2026-10-16-url.txt). Full answers: [`2026-10-16-response.json`](2026-10-16-response.json). Probe output: [`2026-10-16-probes.json`](2026-10-16-probes.json).

## Scientific assessment

Scientific adequacy: supported. The analysis supports its limited conclusion that this group-level test found no whole-brain-corrected positive vmPFC gain effect. It uses one-sided participant-level sign flips and a max-T family-wise correction over the common-coverage mask; its vmPFC sphere summary is descriptive, independently localized, and accompanied by a participant-level interval. It checks hashes, participant count, image grids and finite values, retains all 54 maps, and explains why cope values are not currency-unit effects. The 9,999-permutation sign-flip test assumes symmetric participant-level errors under the null; a strict nonzero intersection mask is conservative and may exclude true exact-zero voxels; participant variance maps are unavailable, so inference is unweighted and conditional on fixed upstream models. The report distinguishes corrected posterior effects from the target vmPFC claim. Visual inspection of `content/workspace/results/figures/positive_fwe.png` (SHA-256 `b604080b21bb4fa0548a6d4567db52e3c78b8bf23fd99231a549a6cba420ed79`) shows the corrected posterior locus away from the target; `content/workspace/results/figures/vmpfc_effects.png` (`e0ad2280d80c46ea755d98201d4119ccd37126c0accce6e6c5b99b86c10bfb59`) shows participant values on both sides of zero, consistent with the interval.

Reported hypothesis outcome: “we find no corrected support for a positive vmPFC gain effect.” This is absence of corrected support, not evidence that the true effect is exactly zero.

Scientific evidence: `content/workspace/report.md` (SHA-256 `e1545efc76abf52ce79d0b979b9cc87db697efe6afda651426b827677d4832b7`), `content/workspace/results/results.json` (`45d5e17c1132085564b583c2bb10fd61be0f41134f3aedc4258c5e3be110c54f`), `content/workspace/code/analyze.py` (`6c853f514b8fff58123d317c95da4249248601e6c61082987f2750dade1212ff`), and fixed upstream methods `content/workspace/input/upstream-methods.md` (`508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`). Each path is relative to canonical capture SHA-256 `8fbefacc47b197b025120e613c35fa886fe8a1e6e7cc236ed643ac74ad845dbb`.

A lack of corrected vmPFC support means this analysis did not detect the predicted positive response at its stated whole-brain FWE criterion. It does not show that the effect is exactly zero, and it is conditional on the supplied gain-modulator estimates and upstream choices. The unweighted group test cannot use participant variance maps because none were supplied. The worker reports a vmPFC mean of −0.014 cope units (95% participant-level t interval −0.044 to 0.015), no sphere voxel passing the whole-brain correction, and 24 corrected positive voxels outside vmPFC; the result is not a gain-versus-loss comparison.

## Worker stop state, access and integrity

The stop receipt records a complete capture, clean worker exit, no omissions or capture errors, original HEAD `bfe069501c140673f38778116f34bc8a5c36366f`, and all 54 supplied maps. At stop, input material was committed and large maps were annexed, but `code/`, `report.md`, `results/`, and `.codex/` were untracked. Those worker-created artifacts therefore receive no version-control credit. The receipt is coordinator-supplied evidence at `worker-end-state.json`, SHA-256 `d99f296419a1ebc7f2467baf3d086d16ab0bce2f376fbee8179aae4feec1eded`. Coordinator preservation and this assessment's replay copy do not alter the worker attribution.

No environment specification or lockfile is included in the worker stop state. The recorded run output is not linked to an exact package environment. The report names an absolute interpreter path in the coordinator's common environment; it enabled the replay but is not a worker-shared environment artifact.

The intended recipient is a researcher using the worker-declared route in `content/workspace/input/sources.json` (SHA-256 `919be9b4278c31f7e39ae3d02fcf159eb4ae222a2fb96c90df7c3a92e5fb19cd`): the public NeuroVault collection/API and map URLs, plus pinned raw GitHub cohort/methods URLs. Read-only HTTP header checks returned 200 for the collection, API (`limit=1`), one map (`sub-001`) and the pinned cohort table. The pinned methods URL returned 200; the other 53 map URLs were not individually tested, nor was availability from the worker host at stop. These source routes cover input artifacts, not the report, code or results; no worker-declared route for the complete package was identified. Coordinator delivery is not worker publication evidence. See `access-record.json`.

The initial operational and canonical manifests have the same SHA-256 as the canonical capture identity above. Inspection comparison found no target-integrity mismatch outside the separately classified regular-file changes to `.git/annex/keysdb/db`, `db-shm` and `db-wal`; `inspection-integrity.json` records their sizes and hashes. These assessment-associated annex metadata changes are not worker evidence and do not establish logical database equivalence. No other target bytes, links, index, refs, objects or configuration differed from the initial operational manifest.

The capture contains `.entire/logs/entire.log` and `.entire/metadata/...` session-artifact paths. They may expose AI assistance; their contents were not used as grading evidence.

## Assessment provenance

The frozen runtime check passed. I used assessor version 1 (`source_commit` `9852d8360f9519d21d11099b45f5deb8ba80cb28`; environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`) from `assessment-version.json`, its supplied runner/interpreter, the frozen probes, one captured-delivery replay and the scientific record validator. This report makes no overall-score claim.
