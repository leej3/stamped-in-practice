# Independent assessment — NARPS potential gain and vmPFC

**STAMPED MUST:** 5 met / 1 partial / 11 unmet / 0 not-checked (17). **SHOULD:** 0 met / 1 partial / 5 unmet / 2 not-checked / 1 not-applicable (9). **MAY:** 3 met / 0 partial / 2 unmet / 0 not-checked / 0 not-applicable (5). No overall score is assigned.

## Scientific assessment

**Scientific adequacy: qualified.** The delivered analysis supports its cautious, narrow statement that it did not find a positive whole-brain-corrected vmPFC result. It does not establish a zero effect. However, the whole-brain group test treats some uncovered map locations as observed zeros, which limits confidence in the global corrected search and needs to be resolved before treating the full-brain inference as definitive.

**Reported hypothesis outcome:** no support for a positive vmPFC effect under the reported whole-brain-corrected test. The worker reports 24 corrected voxels in small posterior clusters (peak *t*(53)=6.62, max-T adjusted *p*=.0010), outside the vmPFC sphere. The sphere’s mean estimate is −0.013 map units, with a participant-level 95% *t* interval [−0.044, 0.018]. This is not an equivalence test and does not establish absence of gain-related activity.

The group method is otherwise well aligned with the supplied task: it selects all 54 equal-indifference participants, treats each run-combined participant map as an effect estimate rather than a *t/z* map, checks common shape and affine, checks finiteness, and uses an equal-weight one-sample random-effects *t* statistic. Given no participant variance maps, equal participant weights are defensible. The one-sided participant sign-flip maximum-*t* procedure controls whole-mask family-wise error without cluster assumptions and states its sign-exchangeability assumption and finite permutation resolution. The 10-mm sphere at [0,44,−10] is declared an operational, descriptive vmPFC definition independent of results; it is not used as an uncorrected primary test. The interpretation also correctly says these normalized gain-modulator coefficients are not per-currency-unit effects and bounds conclusions by the upstream participant model. Evidence: [report.md](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j01/content/workspace/report.md), [group_analysis.py](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j01/content/workspace/code/group_analysis.py), [summary.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j01/content/workspace/results/summary.json), and [upstream-methods.md](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j01/content/workspace/input/upstream-methods.md).

The material qualification is coverage handling. The script counts nonzero voxels per map, forms a mask at 90% coverage, and then stacks all 54 maps and runs the test on every masked voxel. It does not convert each participant’s uncovered zeros to missing values or use a complete-coverage mask. The reported mask has 210,968 voxels, while only 198,029 are covered in all 54 maps; its minimum coverage is 49/54. Thus, at least 12,939 included locations treat one to five uncovered values as observations. This can attenuate estimates and changes the sampling structure at mask edges. The worker acknowledges edge sensitivity, but the calculation does not remove the missing observations. I could not verify whether the operational vmPFC sphere itself is fully covered by every participant. This issue qualifies the whole-brain corrected result; it does not justify claiming a positive vmPFC finding or declaring the hypothesis true. A follow-up using an explicit participant-level missing-data policy and rerunning max-*t* inference would settle its impact.

Other limits are stated appropriately: the ROI interval is wide and crosses zero; variance weighting cannot be done without participant variance maps; the sign-flip test depends on participant-level exchangeability; and the operational sphere is not a uniquely authoritative anatomical boundary. The figures, participant QC table, coverage mask, effect maps, thresholded map, permutation distribution and cluster table make most choices inspectable. The numerical details above are from the shipped outputs; no replay was performed and no pre-existing output is presented as replay evidence.

## Delivery boundary, worker stop and access

The delivery manifest SHA-256 is `44b45c2d1e80cd01a5c6725623e8bffd63b3732ef2c1f010cdceea08c89f6878`; frozen `validate_capture` matched it to the stop receipt. It records 1,150 entries, no capture errors or omissions, 54 internal annex-backed input pointers, and no external Git dependencies. The scientific artifacts were assessed from that complete captured workspace. No source bytes were repaired. See [capture verification](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j01/attempt-01/judgment/commands/capture-verify.stdout), [probes](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j01/attempt-01/judgment/probes.json), and the [worker stop receipt](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j01/attempt-01/worker-end-state.json).

At worker stop (2026-10-16 07:41:21 UTC), the receipt records exit code 0 and commit `2906eaca49c5a00d3df4b0c2dcd59eba9c8a3fb8`. The tracked commit is not the complete delivered state: the frozen probe found `.codex/`, `code/`, `figures/`, `report.md`, and `results/` untracked. Those worker artifacts were inspected scientifically but do not earn version-control credit. The later retained capture and coordinator assessment delivery establish preservation for this review only; they do not establish worker publication or sharing. Exposure note: the captured `.codex/skills/pdf/` directory identifies use or availability of a PDF-specific assistant skill; this identifier was not used as evidence for scientific grading.

The intended recipient is a researcher following the worker’s authorized route. No worker-declared retrieval route for the finished report, code and results was present, so no remote delivery host could be tested. `input/sources.json` lists public upstream routes for the source maps and cohort/method references; those cover inputs, not this analysis product. The complete local target supplied by the coordinator was inspected but is not evidence of worker access. Details are in [access-record.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j01/attempt-01/judgment/access-record.json).

A scientific replay was **not checked**. The report points to `code/group_analysis.py` but gives no invocation command; the package versions in prose are not an installable or pinned environment declaration. There is therefore no safe documented entrypoint and no worker-supplied environment to reconstruct. The frozen comparison helper also cannot compare the primary NIfTI outputs scientifically using its table tolerance. Nothing was deleted or executed in a replay copy. The candidate command, potential generated table outputs and precise limitation are recorded in [replay-record.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j01/attempt-01/judgment/replay-record.json). A separate assessor-side attempt to inspect coverage with NiBabel failed because NiBabel is absent in the assessor interpreter; that failure is recorded and is not attributed to the worker.

## What to address first

1. Add a pinned, installable environment declaration and clear host requirements, with an acquisition and setup command. This enables safe reproduction and closes the largest portability gap (must/003, 010–017; should/006–008).
2. Track the report, analysis code, figures and results at worker stop, and retain a run record linking inputs, command and exact environment to generated results. The current Git commit alone omits the central scientific delivery (must/004, 006; should/001).
3. Represent uncovered voxels as missing observations or define a justified common coverage mask before voxelwise group and max-*t* inference. This resolves the scientific qualification.
4. Add a documented command and a clean-environment execution record. This will let a recipient reproduce the shipped result and verify the documented route (must/007–008; should/002, 004–005).

## What is already strong

- `input/sources.json` records source URLs, IDs, transformations, and retrieved-byte hashes; all 54 supplied maps are retained through annex content under the workspace.
- The scientific report separates the corrected whole-brain result from the descriptive ROI estimate, states assumptions and uncertainty, and explains what a null result does and does not mean.
- The analysis provides readable code, participant-level QC, coverage and result maps, figures, permutation values and a compact machine-readable summary.

## Per-item STAMPED checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/study-task.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j01/manifest.json` | All delivered files are beneath the workspace root; the capture inventories the complete tree. |
| must/002 | S.1 | met | probe:large-in-annex | `input/data/sub-001_hypo1_cope.nii.gz` | The 54 maps and cohort table are within the root; map payloads resolve through retained annex content. |
| must/003 | S.1 | unmet | judgement | `report.md` | No delivered environment specification includes the imported Python packages. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `probes.json` | At worker stop, code, report, figures and results were uncommitted; the commit is not the complete research state. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probes.json` | The 54 large participant maps use git-annex pointers with retained payloads. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `report.md` | Shipped outputs have no run record linking the execution to an exact environment specification. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `report.md` | The report names files but gives no installation and usage instructions or environment setup. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md` | The report identifies code/group_analysis.py as the analysis starting point and the script derives paths from its root. |
| must/009 | P.1 | met | probe:no-abs-paths | `code/group_analysis.py` | The analysis builds paths relative to the script root and uses no host-specific absolute paths. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `code/group_analysis.py` | The script imports six external distributions but no environment specification declares or resolves them. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `code/group_analysis.py` | Host assumptions are not documented; the figure path also calls a template loader that may need a cache or network. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `report.md` | The report names Python and package versions, but gives no system requirements or installable dependency list. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probes.json` | No environment specification is captured alongside the code and data. |
| must/014 | P.3 | unmet | judgement | `Full capture has no environment manifest or update instructions.` | No environment update or regeneration process is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `report.md` | No frozen environment specification identifies the execution environment. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `worker-end-state.json` | No worker-published environment specification or retrieval route is recorded. |
| must/017 | D.1 | unmet | judgement | `report.md` | The report does not explain how to obtain or install the environment. |
| should/001 | T.2 | unmet | probe:tree-clean+judgement | `probes.json` | The inputs are annex-tracked, but the analysis code and results were untracked at worker stop. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `probes.json` | No repeat-testing records or test workflow appear in the complete stopped delivery. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/, code/, results/ and figures/ are separate in the complete workspace; no environment specification.` | Inputs, code and results occupy separate directories, but no environment module exists. |
| should/004 | E.1 | not-checked | judgement | `report.md` | No fresh-environment test record exists; a documented environment and completed clean replay would settle this. |
| should/005 | E.1 | not-checked | judgement | `report.md` | The delivery does not say whether each run used a disposable or persistent environment; execution records would settle this. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `probes.json` | No exact environment specification or reconstitution test is present. |
| should/007 | D.2 | unmet | judgement | `Full capture inventory contains no environment image or package artifact.` | No environment image, binary archive or other environment artifact is retained. |
| should/008 | D.2 | unmet | judgement | `Full capture has no environment manifest or update instructions.` | No environment specification or update process exists; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the delivery contains public study inputs and no restricted data or software component. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `input/sources.json` | The external input collection is bounded and individually linked to source URLs and byte hashes. |
| may/002 | M.2 | unmet | judgement | `report.md` | The report describes the analysis but not how workspace components relate or can be recombined. |
| may/003 | M.2 | unmet | judgement | `code/group_analysis.py` | The script expects the fixed input/data layout and does not define independently updateable module boundaries. |
| may/004 | M.2 | met | judgement | `code/group_analysis.py` | The analysis script composes input maps, metadata and generated outputs through root-relative paths. |
| may/005 | M.2 | met | judgement | `report.md` | The report links the script, summary/QC, whole-brain maps, permutation table and figures. |

## Flagged items

- **must/006, must/011, should/002, should/006, may/001:** probe statuses were revised after direct inspection of the complete delivery; see the per-item evidence and reasons. For may/001, `input/sources.json` supplies retrievable source links and boundaries for the external input collection.
- **must/008:** the entry-point probe only searched recognized README/Makefile/workflow forms. The report’s script link and its root-relative self-contained script provide a starting point, so the probe verdict was overridden.
- **should/008:** duplicates must/014 in the pinned checklist; it repeats the same finding by design.

## Not checked

- **should/004:** no fresh-container, batch, clean-VM or cloud execution record; a fresh-environment run with the declared setup would settle it.
- **should/005:** the worker did not document whether runs use disposable environments; an execution/environment lifecycle declaration would settle it.
- **Replay:** no safe documented command or worker-supplied environment specification; see replay record. The assessor-side NiBabel diagnostic failed independently because the package was unavailable.
- **Access:** no worker-declared delivery route for the finished product; a researcher-accessible authorized route with report, code, inputs and outputs would settle it.

## Goals and kind

The goal is group-stage assessment of whether potential monetary gain produces a positive gain-modulator response in vmPFC for the equal-indifference cohort, using the fixed 54 participant maps and whole-brain-corrected inference. This comes from the supplied task and the worker’s report. The object is treated as a **study**: an analysis workflow with scientific outputs and supporting data. No human clarification was attached; this assumption was not confirmed.

Checklist URL: [2026-10-16-url.txt](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j01/attempt-01/judgment/2026-10-16-url.txt). Canonical answers: [2026-10-16-response.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j01/attempt-01/judgment/2026-10-16-response.json). The unlicensed reuse terms are recorded as an extra finding (not a checklist item) in the response JSON. Probe record: [probes.json](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-06/judgments/narps-neutral-r1-06-j01/attempt-01/judgment/probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the captured workspace at commit `2906eaca49c5a00d3df4b0c2dcd59eba9c8a3fb8`, 2026-10-16, Codex API / GPT-6 (exact deployment label unavailable). Capture manifest: `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-06-j01/manifest.json`, SHA-256 `44b45c2d1e80cd01a5c6725623e8bffd63b3732ef2c1f010cdceea08c89f6878`. Probe output: `probes.json`.
