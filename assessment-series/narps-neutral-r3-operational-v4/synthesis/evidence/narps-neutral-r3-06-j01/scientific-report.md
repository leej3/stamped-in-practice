# Independent assessment — NARPS equal-indifference gain effect

**MUST: 6 met / 3 partial / 8 unmet / 0 not-checked. SHOULD: 0 met / 2 partial / 3 unmet / 3 not-checked / 1 not-applicable. MAY: 1 met / 2 partial / 1 unmet / 0 not-checked / 1 not-applicable.** These are item verdicts, not an overall score.

## What to fix first

1. Add a pinned, complete environment specification and install instructions, including the atlas data prerequisite → the documented analysis currently depends on an unrecorded prepared environment and runtime atlas fetch → closes must/003, 010, 012, 013, 015–017 and should/006–008.
2. Track the report, analysis script, retrieved map copies and generated results in the repository or a documented versioned data mechanism → the worker-stop Git state contains only `input/` in HEAD while the scientific deliverables are untracked → closes must/004 and improves should/001.
3. Add a provenance record tying the exact command, software environment, input identities and generated result hashes together → the result JSON records statistical settings but not the runtime or a run record → closes must/006.
4. Add a workflow validation record for a clean environment and a regular test path → no testing history or equivalent run record is supplied → closes should/002, 004–006.
5. State reuse terms for the code and derived artifacts → no license declaration is present → extra item `license-declared`.

## What the project does well

- The report correctly distinguishes participant cope estimates from z/t maps and currency-scaled slopes, and explains the fixed upstream model and missing participant variance maps. The analysis uses all 54 matching participants and states no exclusions. [capture `d9a460b5bc349513f883c33039f469882bc878d31c0e09eee434a9cfc4ac5eda`, `content/workspace/REPORT.md`; `content/workspace/input/upstream-methods.md`]
- The group test is a one-sided studentized one-sample max-T sign-flip procedure over a declared whole-brain mask, with plus-one corrected p-values and an explicit symmetry assumption. The vmPFC atlas definition is independent of the observed map and is descriptive; the report does not substitute ROI-only inference for whole-brain correction. [capture `d9a460b5bc349513f883c33039f469882bc878d31c0e09eee434a9cfc4ac5eda`, `content/workspace/REPORT.md`; `content/workspace/analysis/run_group_analysis.py`]
- The complete stop delivery includes code, outputs and all 54 retrieved maps. The two figures and result table make the negative vmPFC estimate and the corrected whole-brain result inspectable. [capture `d9a460b5bc349513f883c33039f469882bc878d31c0e09eee434a9cfc4ac5eda`, `content/workspace/results/analysis_results.json`; `content/workspace/results/group_maps.png`; `content/workspace/results/vmPFC_subject_effects.png`]

## Scientific assessment

**Scientific adequacy: qualified.** The reported absence of corrected positive vmPFC support is scientifically defensible given the stated whole-brain max-T procedure and the supplied artifacts. The analysis is appropriately conditional on the fixed AO86 gain maps and explicitly limits interpretation of the upstream gain coefficient. Confidence is qualified because I could not independently replay the computation: the worker supplied only a prose package list, the frozen interpreter lacks NiBabel and Nilearn, and the documented script fetches a Harvard–Oxford atlas without a captured atlas prerequisite or pinned environment. No result mismatch was demonstrated; numerical claims therefore remain worker-reported rather than replay-confirmed.

**Reported hypothesis outcome:** no whole-brain-corrected support for a greater vmPFC response as potential gain increases.

Verbatim conclusion from the worker report: In the NARPS equal-indifference group, the supplied participant maps do **not** support a greater vmPFC response with increasing potential gain under a whole-brain corrected test. The report gives a vmPFC mean participant estimate of −0.017 cope (95% interval −0.038 to 0.004), one-sided ROI p=.949, and no vmPFC voxel surviving whole-brain FWE correction. It separately reports 24 corrected voxels at a posterior peak outside vmPFC, appropriately treated as secondary. The reported result means insufficient evidence for the predicted positive group effect under these data and this fixed upstream model; it does not establish a zero effect.

The method is defensible: participant maps are treated as independent observations; the code checks the cohort IDs, checksums, dimensions/affines and finite values; the coverage/atlas mask is stated; equal weights are reasonable without participant variance maps; and max-T controls positive whole-brain inference under the sign-flip symmetry assumption. The main scientific limitations are the untestable symmetry/model assumptions, mask dependence, absent participant variance maps and fixed upstream modeling choices. Figures show unthresholded vmPFC slices and individual ROI estimates, though the overlays lack an anatomical underlay. The output ROI is explicitly descriptive, avoiding circular ROI-only support claims.

### Replay measurement

Status: **not checked; no replay command was launched.** The documented command is `python analysis/run_group_analysis.py`; the report names NumPy, SciPy, pandas, Matplotlib, NiBabel and Nilearn, `NILEARN_DATA`, and a default of 10,000 permutations, but gives no environment spec or versions. The available frozen interpreter lacks NiBabel/Nilearn, and the script calls Nilearn atlas fetchers. Installing an unconstrained environment or supplying the missing atlas would add prerequisites. Had replay been feasible, the selected outputs would have been the nine explicitly listed in [replay record](replay/replay-record.json), comparing numeric maps and tabular estimates at the helper's rtol 1e-6 while separating stochastic, formatting, timestamp and prose differences. No scientific-input retrieval or output deletion occurred.

### Access and worker-stop attribution

The intended recipient is a researcher using the worker-declared input retrieval route. `input/sources.json` names NeuroVault for the collection and 54 maps, plus commit-pinned raw GitHub sources for cohort/methods. HTTP HEAD checks from this assessment host returned 200 for the collection, API, both pinned source URLs and all 54 map URLs. This tests only host/path reachability at the check time, not authenticated access, data integrity or durable access. The captured Git config has no remote; no worker publication/access route for the report, script and generated results was found. Coordinator delivery is not worker publication. Details: [access record](access/access-record.json).

Worker-stop evidence is the supplied receipt. At stop, the scientific report, script, map copies and results were untracked; the captured HEAD tracked only `input/`. I therefore do not credit that HEAD for versioning the scientific analysis. Later coordinator preservation is not worker practice. Captured Git commit metadata exposed an AI co-author attribution; I record that exposure here and did not use it as grading evidence. During initial metadata inspection, an out-of-scope coordinator procedure file was inadvertently displayed; it was excluded from all judgments, and no treatment assignment was inferred or reported.

The operational copy was inspected directly; the frozen launcher verified it against the canonical capture before and after assessment. Canonical original capture SHA-256: `d9a460b5bc349513f883c33039f469882bc878d31c0e09eee434a9cfc4ac5eda`. Original captured HEAD: `e09e9887ff701ffa1b550ad83676aed6d27f5ff1`. No evidence mismatch was reported. References to target artifacts below are capture-relative and refer to the canonical original, not inspection-induced metadata.

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `REPORT.md` | The delivered files are nested under one workspace root. |
| must/002 | S.1 | met | judgement | `input/sources.json` | The complete map set, cohort metadata and methods reference are within the root and connected through the manifest/code. |
| must/003 | S.1 | unmet | judgement | `REPORT.md` | Runtime software is referred to in prose but is not declared in a delivered environment or linked software module. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `REPORT.md` | Git is present, but the report, analysis code, retrieved maps and results were uncommitted at worker stop. |
| must/005 | T.1,T.3,T.5 | met | judgement | `input/sources.json` | The 54 large participant maps are tracked as git-annex content. |
| must/006 | T.1,T.3,T.5 | unmet | judgement | `results/analysis_results.json` | The result record names analysis parameters but does not link the produced outputs and actions to an exact runtime environment. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `REPORT.md` | The report gives usage instructions but does not explain how to install the prepared environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `REPORT.md` | The report identifies analysis/run_group_analysis.py as the runnable starting point. |
| must/009 | P.1 | met | judgement | `analysis/run_group_analysis.py` | The analysis script resolves inputs and outputs relative to its own workspace. |
| must/010 | P.1 | unmet | judgement | `REPORT.md` | The dependency names are not included in a machine-readable environment specification. |
| must/011 | P.1 | met | probe:platform-assumptions+judgement | `REPORT.md` | Documented runtime assumptions are the named Python packages and workspace-local NILEARN_DATA; no additional host-specific assumption appears in the route. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `REPORT.md` | The report names Python dependencies and NILEARN_DATA but gives no install steps or system requirements. |
| must/013 | P.3 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json` | No environment specification is tracked alongside the code. |
| must/014 | P.3 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json` | No process for regenerating and tracking environment specifications is declared. |
| must/015 | D.1 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json` | No pinned environment artifact is supplied for exact reconstitution. |
| must/016 | D.1 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json` | There is no environment specification available for others to access. |
| must/017 | D.1 | unmet | judgement | `REPORT.md` | The report does not explain how to obtain or install the prepared environment. |
| should/001 | T.2 | partial | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json` | Git and annex cover inputs, while uncommitted code and results are outside tracked version history. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json` | No recognized CI or repeated-test record was found; the captured delivery does not establish whether equivalent tests ran regularly. |
| should/003 | M.1 | partial | judgement | `REPORT.md` | Inputs, analysis code and outputs occupy separate directories, but no environment module exists. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json` | No evidence establishes whether the workflow was tested in a fresh container, VM, batch job or cloud instance. |
| should/005 | E.1 | not-checked | judgement | `REPORT.md` | No supplied record establishes whether executions use disposable environments. |
| should/006 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json` | No exact environment specification exists to test for reconstitution. |
| should/007 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json` | No environment artifact is archived in the research object. |
| should/008 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json` | No environment update process is declared. |
| should/009 | M.4 | not-applicable | judgement | — | N/A: no restricted data or software component is identified in this public-input analysis delivery. |
| may/001 | M.2 | not-applicable | judgement | — | N/A: no independently maintained project components are identified; runtime packages are not project modules. |
| may/002 | M.2 | partial | judgement | `REPORT.md` | The report explains the fixed input, group analysis and results roles, but not an environment module or composition map. |
| may/003 | M.2 | partial | judgement | `analysis/run_group_analysis.py` | Input, analysis and results directories are separable, but reproducible independent updates are limited by the absent environment specification. |
| may/004 | M.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-06-j01/attempt-01/judgment/probes/probes.json` | The object has no mechanism for composing independent modules. |
| may/005 | M.2 | met | judgement | `REPORT.md` | The report and sources manifest help readers navigate the input, analysis and result artifacts. |

## Flagged items

- **must/007 and must/008:** the entry-point probe recognizes neither a qualifying README/Makefile nor a start point. The report supplies equivalent usage documentation and names the script, but omits installation steps; must/007 is partial and must/008 is met.
- **must/011:** the platform probe leaves this open; the report documents the Python packages and `NILEARN_DATA`, and no further host-specific assumption is apparent, so it is met on inspection.

## Not checked

- **should/002:** the probe finds no CI; the full stop delivery provides no evidence settling whether equivalent repeated workflow testing occurred. A testing history would settle it.
- **should/004:** no evidence shows a fresh-container, batch, VM or cloud run; a retained test/run record would settle it.
- **should/005:** no record describes disposable execution environments; environment/run configuration would settle it.
- **Scientific replay:** the required runtime/atlas prerequisites were not supplied, as detailed above.

## Goals and kind

The documented goal is group-level inference for the NARPS equal-indifference potential-gain effect, conditional on supplied AO86 participant maps. This is a computational study. The assessment emphasizes traceability, actionability and portability of the analysis and input-to-result path.

## Checklist link and provenance

Checklist: [open the filled checklist](2026-10-16-url.txt). Machine-readable answers: [response.json](response.json). Probe output: [probes/probes.json](probes/probes.json).

Assessment used frozen runtime version 1 and the pinned checklist 0.3.1. Response object identity is canonical capture SHA-256 `d9a460b5bc349513f883c33039f469882bc878d31c0e09eee434a9cfc4ac5eda`, original commit `e09e9887ff701ffa1b550ad83676aed6d27f5ff1`, capture time `2026-10-16T16:44:55.960666+00:00`; assessor: Codex / GPT-6, 2026-10-16.
