# Independent assessment

**Assessment date:** 2026-10-16 (UTC)  
**Assumption — kind and goal:** This is a study whose product is a group-level answer to the supplied NARPS Hypothesis 1 task; the task and the worker report define that goal. No human confirmation was attached.  
**Scope:** Complete worker-stopped workspace as captured, including untracked and ignored material. Canonical original capture SHA-256: `8d0fdaeeda6a0b9c877ea7fd74222e16e75697ca45da5b39bfacb8c8a312eabf`; captured HEAD: `78d5939f13b4caeecb07a75518298c6c9c44cfd1`. Every `content/workspace/...` citation below names a path relative to that canonical capture. The worker-end-state receipt SHA-256 is `a0bbbe31a545341523d8c75c7cd6f5662f49ea6290ad460788b68f6826ce044e`.

## Verdicts

MUST: 2 met / 3 partial / 12 unmet / 0 not-checked (17 total). SHOULD: 0 met / 1 partial / 5 unmet / 2 not-checked / 1 not-applicable (9 total). MAY: 3 met / 2 partial / 0 unmet / 0 not-checked (5 total). Partial does not satisfy a MUST. Not-checked is reported separately; there is no overall score.

## What to fix first

1. Add a pinned dependency/environment specification and capture or explicitly pin the Nilearn MNI mask/template assets; this makes the complete computation self-contained and portable (must/001–003, must/010–017, should/006–008, may/001).
2. Put the worker analysis, report, generated maps, tables and figures under the worker's version-control history, with a run record naming code, input and environment identities; this preserves the actual scientific result and its provenance (must/004–006).
3. Add complete setup and execution instructions, including how a researcher obtains the environment; the present report gives the command but assumes an unspecified prepared environment (must/007, must/012, must/017).

## What the study does well

- The report and script address all 54 equal-indifference participants, check map identity, geometry and finite values, and explain why participant variance maps are unavailable [capture `8d0fdaeeda6a0b9c877ea7fd74222e16e75697ca45da5b39bfacb8c8a312eabf`: `content/workspace/report.md#L9-L13`; `content/workspace/analyze.py#L25-L62`].
- The primary group inference uses one-sided whole-mask max-*t* permutation FWE correction; the report distinguishes corrected whole-brain inference from the descriptive coordinate vmPFC summary [capture `8d0fdaeeda6a0b9c877ea7fd74222e16e75697ca45da5b39bfacb8c8a312eabf`: `content/workspace/analyze.py#L65-L76`; `content/workspace/report.md#L17-L19`].
- The scientific report describes coefficient scaling, upstream-model limits, uncertainty, the approximate vmPFC locator and the meaning of a non-significant result [capture `8d0fdaeeda6a0b9c877ea7fd74222e16e75697ca45da5b39bfacb8c8a312eabf`: `content/workspace/report.md#L29-L33`].

## Scientific assessment

**Scientific adequacy: supported.** The conclusion of no convincing whole-brain-corrected vmPFC support is adequately supported by the supplied group maps and reported analysis. It is a defensible absence-of-positive-finding conclusion, not proof of a zero effect.

In the 54-person equal-indifference group, the supplied gain-effect estimates do **not** support a positive vmPFC response to increasing potential gain at the whole-brain family-wise error (FWE) corrected level.

The report identifies 54 participant effect maps, checks matching grids and finite values, and excludes none. It tests the positive mean effect with 5,000 one-sided permutation max-*t* draws over a 192,339-voxel brain/support mask. The `tested_vars=np.ones(...)` one-sample setup matches Nilearn’s documented one-sample `permuted_ols` example ([Nilearn 0.10.3 example](https://nilearn.github.io/0.10.3/auto_examples/07_advanced/plot_localizer_mass_univariate_methods.html)). The three reported corrected clusters contain 23 voxels in posterior occipital locations; no corrected positive voxel is in the vmPFC search zone. The exploratory regional mean is 0.00012 (95% *t* interval −0.0152 to 0.0154), with a nominal one-sided *p* of .494. These results support saying the task did not establish a positive vmPFC response; they do not establish equivalence or rule out a smaller or heterogeneous effect. See the report, `results/analysis_summary.json`, `results/fwe_clusters.csv`, `results/vmPFC_search_zone.json`, the participant QC table and supplied effect maps [capture `8d0fdaeeda6a0b9c877ea7fd74222e16e75697ca45da5b39bfacb8c8a312eabf`: `content/workspace/report.md#L9-L19`; `content/workspace/results/analysis_summary.json`; `content/workspace/results/fwe_clusters.csv`; `content/workspace/results/vmPFC_search_zone.json`; `content/workspace/results/participant_qc_summary.csv`; `content/workspace/input/data/`].

The maps are participant contrast estimates, not test statistics or currency-unit slopes. Upstream gain modulation was centered and variance-normalized, and gain and loss were modeled separately. The group model weights participants equally because individual variance maps were not supplied. The sign-permutation inference relies on exchangeability under sign changes. The anatomical mask is an MNI152 mask resampled to the MNI152NLin2009cAsym map grid; the vmPFC box is a broad coordinate locator rather than a cytoarchitectonic ROI. These choices are disclosed and do not invalidate the reported conclusion, but they bound precision and anatomical specificity [capture `8d0fdaeeda6a0b9c877ea7fd74222e16e75697ca45da5b39bfacb8c8a312eabf`: `content/workspace/upstream-methods.md`; `content/workspace/analyze.py#L52-L62`; `content/workspace/report.md#L29-L33`].

**Reported hypothesis outcome (kept separate from adequacy):** no support for a positive vmPFC response at whole-brain FWE-corrected level. The exact reported conclusion is quoted above; the outcome is not inferred from the adequacy label.

## Worker state, capture and attribution

The canonical and operational manifests identify the same 1,165-entry complete capture, no omissions, and HEAD `78d5939f13b4caeecb07a75518298c6c9c44cfd1`. The stop receipt records that this HEAD equals the seed commit and lists the input maps, metadata and study task as supplied files. The worker-created `analyze.py`, `report.md`, figures and results are untracked at stop; `.codex/` and `.entire/` are ignored. Therefore the existing seed Git history and annex storage of the supplied maps are not credited as worker version-control actions. The untracked scientific work remains part of the assessed delivery [canonical capture: `content/workspace/analyze.py`, `content/workspace/report.md`, `content/workspace/results/`, `content/workspace/figures/`; worker-end-state receipt above].

The input map links are relative and resolve to annex objects retained inside the capture. The analysis also calls Nilearn loaders for standard MNI mask and anatomical template datasets that are not in the captured workspace. The captured `.git/config` contains an absolute `core.hooksPath` outside the capture; that path was not followed. The replay helper would disable hooks only in a separate replay copy.

The frozen runner/runtime pin and later coordinator preservation are assessment infrastructure, not worker environment or publication evidence. The worker-stop inventory exposes assistance-related identifiers: `.codex/hooks.json`, a `.codex/skills/pdf/` tree and `.entire/` session metadata. I record that exposure only; I did not inspect those session contents or use assistance details as grading evidence.

The canonical and operational starting manifests were byte-identical, complete, and omission-free. A post-inspection comparison found changes only to regular files `.git/annex/keysdb/db`, `db-shm` and `db-wal`, classified as operational metadata. Every other captured path, content hash, symlink and mode matched. This does not establish logical database equivalence; the changed database files are inspection side effects, not worker evidence. See [`integrity-check.json`](integrity-check.json).

## Access and replay

No worker-declared publication route for the complete study, code, results or environment was found; `.git/config` has no remote. The worker's `input/sources.json` does declare public NeuroVault and pinned raw GitHub routes for source inputs. Header-only checks returned HTTP 200 for the NeuroVault collection, one map, and the pinned cohort TSV. This verifies only those hosts and endpoints, not all maps, software dependencies, environment access or access from other networks. Coordinator delivery of the complete object is not evidence of worker publication. The full recipient/coverage record is [`access.json`](access.json).

Replay is **not checked**. The documented command is `python analyze.py`, and generated outputs were identifiable, but the worker supplied no dependency declaration beyond “prepared environment.” The script also loads external MNI resources absent from the capture; allowing that retrieval would violate the captured-input replay scope. No replay process was started, no outputs were removed, and no replay stdout/stderr exists. The planned outputs, prerequisites and comparison limitations are retained in [`fresh-rerun.json`](fresh-rerun.json). A pinned environment and captured or explicitly authorized MNI assets would settle replay availability.

## Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `content/workspace/analyze.py#L57-L59`, `content/workspace/analyze.py#L201-L206` | Participant maps are captured, but the code fetches standard brain-mask and anatomical-template datasets outside the project root. |
| must/002 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `content/workspace/analyze.py#L57-L59` | Captured participant maps resolve internally; the MNI mask and display template are fetched through Nilearn outside the root. |
| must/003 | S.1 | unmet | judgement | `content/workspace/analyze.py#L7-L14` | The code imports scientific packages, but no delivered environment or linked software module supplies them. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `git status --short --ignored`, `worker-end-state.json` | The captured HEAD equals the seed commit; worker analysis code, report, figures and results remain untracked. |
| must/005 | T.1,T.3,T.5 | unmet | probe:large-in-annex+judgement | `worker-end-state.json`, `content/workspace/results` | Annex-backed maps were coordinator-supplied inputs; worker-generated binary maps remain untracked and no annex action is attributable to the worker. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `content/workspace/report.md#L35-L37`, `content/workspace/results/analysis_summary.json` | Shipped results have no execution record linking the analysis action to an exact environment. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `content/workspace/report.md#L35-L37`, `content/workspace/analyze.py` | report.md documents usage, but installation and environment setup instructions are absent. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/report.md#L35-L37`, `content/workspace/analyze.py` | The report names python analyze.py and the script is included. |
| must/009 | P.1 | met | probe:no-abs-paths | `content/workspace/analyze.py#L16-L19` | Analysis code uses paths relative to its own directory. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/analyze.py#L7-L14` | No environment declaration covers the scientific Python imports or plotting dependencies. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `content/workspace/report.md#L35-L37`, `content/workspace/.git/config` | The host Python and package environment are not documented; captured Git config also contains an absolute hooks path. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `content/workspace/analyze.py#L7-L14`, `content/workspace/report.md#L35-L37` | No README or environment specification lists system requirements and dependencies. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `git ls-files` | No environment specification is included in version control or the stopped workspace. |
| must/014 | P.3 | unmet | judgement | `content/workspace/analyze.py`, `git log -1` | No dependency update procedure or tracked environment specification is present. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `content/workspace/report.md#L35-L37`, `content/workspace/analyze.py#L7-L14` | No frozen environment specification identifies the packages used for these results. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/.git/config`, `content/workspace/input/sources.json` | No worker-declared route publishes an environment specification for researcher retrieval. |
| must/017 | D.1 | unmet | judgement | `content/workspace/report.md#L35-L37` | Instructions do not explain how to obtain or use an environment; the setup is called “prepared” only. |
| should/001 | T.2 | unmet | judgement | `git status --short --ignored`, `worker-end-state.json` | Worker-created code, documentation and results are untracked; Git/annex state belongs to the supplied seed inputs. |
| should/002 | A.2 | not-checked | probe:ci-present | `git ls-files` | No repeat-testing evidence is supplied; a future scheduled or repeated run record would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/input`, `content/workspace/results`, `content/workspace/analyze.py` | Inputs, code, results and figures have separate paths, but environment is not a module. |
| should/004 | E.1 | not-checked | judgement | `content/workspace/report.md#L35-L37` | No safe fresh replay was possible because no package environment was supplied; a pinned environment and rerun would settle it. |
| should/005 | E.1 | unmet | judgement | `content/workspace/analyze.py#L1-L25` | python analyze.py uses the caller’s active environment and does not create a disposable one. |
| should/006 | D.2 | unmet | judgement | `content/workspace/analyze.py#L7-L14`, `content/workspace/report.md#L35-L37` | No exact environment specification or reconstitution test is supplied. |
| should/007 | D.2 | unmet | judgement | `content/workspace/analyze.py` | No environment image, binary environment artifact or package cache is archived in the workspace. |
| should/008 | D.2 | unmet | judgement | `content/workspace/analyze.py#L7-L14` | No dependency update process is documented or tracked. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: captured data are publicly retrievable and no restricted software or data component is identified. |
| may/001 | M.2 | partial | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json`, `content/workspace/analyze.py#L57-L59` | The participant maps are captured and their source is identified, but Nilearn template datasets are implicit external inputs. |
| may/002 | M.2 | met | judgement | `content/workspace/report.md#L7-L13`, `content/workspace/report.md#L35-L37` | The report and directory structure explain inputs, analysis, results and figures. |
| may/003 | M.2 | partial | judgement | `content/workspace/analyze.py#L30-L47`, `content/workspace/input/sources.json` | The input boundary is checksum- and grid-checked, but changes require coordinated manifest updates. |
| may/004 | M.2 | met | judgement | `content/workspace/analyze.py#L25-L29`, `content/workspace/analyze.py#L200-L218` | analyze.py composes the captured inputs into result maps, tables and figures. |
| may/005 | M.2 | met | judgement | `content/workspace/report.md#L35-L37` | The report names the input, result and figure locations and the script to run. |


## Flagged items

- **must/001, must/002:** direct reading overrides the self-containment probe gap because the script fetches MNI template assets beyond the captured maps.
- **must/004, must/005:** probes saw Git/annex, but the stop receipt shows they are seed/coordinator state; worker deliverables are untracked.
- **must/006:** the probe did not recognize a completed record; direct inspection confirms there is no run/environment provenance record.
- **must/007, must/008:** the entry-point probe did not recognize `report.md` plus `analyze.py`; direct reading finds a documented command (usage only, so must/007 is partial).
- **must/011, must/012, must/015:** command scans cannot settle host/environment requirements; direct reading finds an unspecified Python environment and external template loads.
- **may/001:** the identified input dataset is retrievable, but MNI template datasets are implicit external dependencies.
- **should/008:** repeats must/014 verbatim in the pinned checklist; the same unmet environment-update process applies.

## Not checked

- **should/002:** no repeated or scheduled instruction-testing record was supplied; an equivalent test log would settle it.
- **should/004:** no safe fresh-container/VM replay could be established from worker-supplied environment and input declarations; a pinned environment with the template inputs and a fresh rerun would settle it.

## Goals, kind and checklist

The declared goal is to assess the positive parametric gain effect in vmPFC for the NARPS equal-indifference group using the 54 supplied participant maps, with whole-brain correction. I treat this as a **study** because the product is the scientific answer and its supporting code/results. This kind is an explicit assumption from `input/study-task.md` and `report.md`, not a user-confirmed classification.

The checklist link is [`checklist-url.txt`](checklist-url.txt); the machine-readable per-item answers are [`response.json`](response.json), and the frozen probe output is [`probes.json`](probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the original complete capture, SHA-256 `8d0fdaeeda6a0b9c877ea7fd74222e16e75697ca45da5b39bfacb8c8a312eabf`, at Git HEAD `78d5939f13b4caeecb07a75518298c6c9c44cfd1`, 2026-10-16, OpenAI Codex API / GPT-6. The frozen external assessment runtime was checked at the supplied version. Probe output: `probes.json`.
