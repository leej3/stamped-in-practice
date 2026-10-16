# Independent assessment: NARPS potential gains and vmPFC

## Verdict

MUST: **5 met / 3 partial / 9 unmet / 0 not-checked** (17 total). SHOULD: **0 met / 3 partial / 4 unmet / 1 not-checked / 1 not-applicable** (9 total). MAY: **1 met / 2 partial / 0 unmet / 0 not-checked / 2 not-applicable** (5 total). Partial does not satisfy a MUST. No overall score is assigned.

## What to fix first

1. Add a portable, exact environment specification and instructions to create it; the current route depends on a common host interpreter and leaves future readers without a reproducible setup (must/003, 006, 010–017; should/005–008).
2. Track the analysis, report, and derived results at the worker stop so Git captures the delivered scientific work and links it to its inputs (must/004; should/001).
3. Publish a worker-controlled retrieval route that covers code, report, results, inputs, and the environment; current source URLs cover upstream inputs only (must/016).
4. Add installation instructions and document host requirements, while keeping the useful run command (must/007, 011, 012, 017).

## What the project already does well

- The complete workspace keeps all 54 input maps inside the root via relative git-annex links and retains their payloads; the frozen probe found 54 pointers (canonical content/workspace/input/data/sub-001_hypo1_cope.nii.gz; capture SHA-256 658531a315fac6eb936c0366c378bf110333f70d6bf0a10dd9dea9f30a58547d).
- The report documents effect-map interpretation, sample selection, spatial and support checks, a positive-direction whole-brain max-t correction, and uncertainty (canonical content/workspace/report.md, lines 19–31; file SHA-256 d5b4358cff78c4b84bfde8788fa3d21281064d46dd9b21372a2d9853417ab295).
- The analysis is a single identified script with input and result paths rooted at __file__, and the 11 selected result artifacts reproduced byte-for-byte in the one allowed fresh-copy replay (canonical content/workspace/analysis.py, SHA-256 eafd08b16a91aa973d2c952f2e4b86739fae814d4374d2fad64af167434851d8; replay record at replay.json).

## Scientific assessment

Scientific adequacy is **supported**. The report's conclusion is appropriately bounded to the supplied participant-level cope maps and the fixed upstream model. Its one-sided one-sample sign-flip max-t test controls familywise error over the 90%-support whole-brain mask; it also checks the all-participant intersection, uses the vmPFC box only for localization, and explains the standardized gain modulator and absent participant variance maps. The methods and caveats support the reported absence of whole-brain-corrected positive vmPFC evidence (canonical content/workspace/analysis.py, SHA-256 eafd08b16a91aa973d2c952f2e4b86739fae814d4374d2fad64af167434851d8; content/workspace/results/summary.json, SHA-256 2a688886cf26a86397175b17663647cb2c26c77ad43e5ce779fbb0bc6c190f8e; content/workspace/results/group_p_fwe.nii.gz, SHA-256 f7c4e55c60d25683db8f2190438e005ad5dadb82473038cf3292a1e938d36461).

The reported hypothesis outcome is: "The supplied gain-effect estimates did **not** support a positive vmPFC response to increasing potential gain." The minimum vmPFC voxelwise whole-brain FWE p was .162; the descriptive regional mean was 0.0003 cope units (95% t interval -0.0140 to 0.0145). The analysis found 159 corrected positive voxels posteriorly, outside the vmPFC region; it does not assign them a mechanistic interpretation. This is a defensible absence of positive findings, not evidence that the effect is exactly zero. The broad coordinate box, unweighted group model, sign-symmetry assumption, map-coverage rule, limited sensitivity at n=54, and fixed upstream modeling bound the conclusion. The supplied maps are not currency-unit BOLD effects.

The reproduction attempt used exactly the documented command /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analysis.py in one fresh writable copy of the complete canonical delivery. Before replay, the selected generated outputs were declared as results/summary.json, five NIfTI maps (group_mean_effect, group_t, group_p_fwe, group_p_uncorrected, group_mask_90pct), vmPFC_subject_estimates.tsv, peak.tsv, and three figures (mean_effect_slices, vmPFC_subject_effects, positive_fwe_result). No inputs, metadata, or source files were selected for removal. The adapter used its rtol=1e-6 table comparison rule; all 11 selected artifacts were byte-identical, so no numerical or presentation differences needed interpretation. The attempt used the frozen 7,200-second timeout and 5 GB helper compatibility bound; the adapter performed no prefetch. Execution took 19.6 seconds, returned 0, and the adapter performed no input retrieval. The environment was the prepared common interpreter already supplied to the worker, on the same host; this replay confirms repeatability in that scope, not cross-host environment reconstruction or worker-time provenance.

## Delivery boundary and attribution

The canonical original capture is 658531a315fac6eb936c0366c378bf110333f70d6bf0a10dd9dea9f30a58547d (manifest SHA-256), captured complete at 2026-10-16T16:41:43.644419+00:00; the original captured HEAD is 0acda2e09b35799b07d22052122402c9e54c8965. The worker-stop receipt records 54 map inputs and source metadata. The retained worker prompt at content/workspace/.entire/metadata/01a14592-ddab-7af0-8ef9-ce8eb94cfd88/prompt.txt (file SHA-256 28c57a4ec173893af7ccffbf17c99d867fd1dfecfc32f5e1ab034c3f970ef7bc) identifies the prepared common interpreter as a supplied resource. The recorded stop workspace also contains untracked analysis.py, report.md, and results/; those outputs are not represented by the HEAD commit. Coordinator preservation and assessment-time replay are not worker version-control, publication, or environment-capture credit.

The complete Git refs also contain an Entire side-branch commit (0ac0e2c455f772b92c2926d8011c1e48383a501b) whose tree includes analysis.py, report.md, and results/. The captured Entire log identifies this as an automatic session checkpoint, and the associated hooks/settings are listed as supplied at worker start. I therefore record the commit as coordinator-provided preservation, not worker-managed versioning; the worker-stop HEAD and working tree still do not track the scientific deliverables.

The assessed workspace had no declared Git remote. input/sources.json points to upstream input sources; header checks from this assessor host returned HTTP 200 for the NeuroVault collection, one of 54 map URLs, the pinned participant table, and the pinned methods spreadsheet. That route covers upstream data and provenance sources, not the worker's code, report, generated outputs, or environment. Complete-object access for a researcher is therefore not established. The access record states the intended recipient, route coverage, and tested host scope.

The captured .git/config also contains a host-specific core.hooksPath. I read the captured setting but did not resolve or invoke that external path; the frozen replay disabled hooks in its separate copy.

The operational workspace matched its initial manifest in every path and byte outside one separately classified regular-file change: .git/annex/keysdb/db changed from SHA-256 f6f8fd7af99434db59fadc6da021051789c6aaa271ebf878c54dafc6c9fde5ca to 233c0be3e02857e0fbf47b00b8a94de3e9126529bee41b2491286aef7372be80. This is inspection-induced operational metadata, not worker evidence. Logical database equivalence was not established. The initial assessor-side integrity check had a root-path normalization error; it and its output are retained, and the corrected check reports no missing, extra, or changed paths outside the allowed metadata file (integrity record at operational-integrity.json).

Exposure note: retained .entire session metadata identifies assistant/Codex use. This exposure is recorded but was not used as grading evidence; no treatment assignment was read or inferred.

## Flagged items

- must/007: the probe only recognized README/Makefile patterns, while the untracked report provides a use command but no installation instructions; therefore partial.
- must/008: the probe searched tracked paths and missed the untracked analysis script and documented entrypoint; therefore met.
- must/004: the tree-clean probe only evaluated the checked-out HEAD. A complete-ref review found the scientific files in a supplied Entire checkpoint, which is preserved as attribution evidence and does not change the worker-practice verdict.
- must/014 and should/008: these checklist items duplicate the same environment-update question; their answers intentionally repeat.

Extra finding outside the pinned checklist: no license statement appears in the complete delivery (license-declared probe; source inventory at content/workspace/input/sources.json). This is not included in the checklist denominators.

## Not checked

- should/002: no CI or repeated-testing record was found. The single assessor replay cannot establish regular testing; a worker-maintained repeated-run record would settle it.

## Goals and kind

Assumption (not confirmed with human guidance): this is a study whose product is a group-level scientific conclusion about potential-gain effects in the vmPFC, plus the code and results that support it. This follows the supplied task and report.md; the emphasis is on complete inputs, traceable analysis, usable execution instructions, and access to the delivered result.

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/input/sources.json`, `content/workspace/results/summary.json` | The complete project workspace, including annex payloads and stopped outputs, sits under one captured root. |
| must/002 | S.1 | met | judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `content/workspace/analysis.py` | All 54 map links resolve within the workspace to retained .git/annex/objects payloads; metadata and code use the in-root input/ tree. |
| must/003 | S.1 | unmet | judgement | `content/workspace/analysis.py`, `content/workspace/report.md` | The code imports external Python packages, but the project contains no environment specification or linked software module. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `content/workspace/.git/HEAD`, `content/workspace/.git/refs/heads/entire/0acda2e-e3b0c4`, `content/workspace/.entire/logs/entire.log` | Original HEAD leaves the scientific work untracked; a supplied Entire capture hook created a side-branch commit before stop, so that coordinator checkpoint is not worker-managed Git practice. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/2026-10-16-probes.json` | All 54 large map payloads are carried by git-annex; the worker-stop receipt records their keys, sizes, and content checksums. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `content/workspace/report.md`, `content/workspace/results/summary.json` | The report names package versions and the seed, but no run record links the shipped outputs to an exact environment specification. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `content/workspace/report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/2026-10-16-probes.json` | report.md gives a run command but no installation instructions; the equivalent documentation covers use only. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/report.md`, `content/workspace/analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/2026-10-16-probes.json` | The report identifies analysis.py as the reproducible starting script and gives its command. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `content/workspace/analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/2026-10-16-probes.json` | analysis.py derives the workspace from __file__ and uses root-relative input and output paths. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/analysis.py`, `content/workspace/report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/2026-10-16-probes.json` | No environment specification includes the imports on the documented route; package versions appear only as prose. |
| must/011 | P.1 | unmet | judgement | `content/workspace/report.md`, `content/workspace/analysis.py` | The documented route depends on an absolute common-environment path outside the project and does not specify the host OS or system requirements. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `content/workspace/report.md` | The report lists Python package versions, but omits system requirements and instructions for obtaining or creating the environment. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `content/workspace/.git/HEAD`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/2026-10-16-probes.json` | No environment specification is included in the worker-stop Git tree. |
| must/014 | P.3 | unmet | judgement | `content/workspace/report.md`, `content/workspace/.git/HEAD` | No environment specification or dependency-update command is present in the complete delivery or its worker-stop history. |
| must/015 | D.1 | unmet | probe:env-spec-tracked | `content/workspace/report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/2026-10-16-probes.json` | No frozen package manifest or environment image is included to reproduce the listed package versions. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/.git/config`, `content/workspace/input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/access-record.json` | No worker-declared route publishes the project or its environment; the listed public URLs retrieve inputs only. |
| must/017 | D.1 | unmet | judgement | `content/workspace/report.md` | The report gives a host-specific interpreter path but no instructions to obtain or use a project-contained environment specification. |
| should/001 | T.2 | partial | judgement | `content/workspace/.git/HEAD`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/2026-10-16-probes.json` | Git and git-annex version the supplied inputs, but the worker-stop analysis, report and derived outputs are untracked. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/2026-10-16-probes.json` | No CI or repeated-testing record is present; one assessor replay cannot establish regular worker testing. A maintained repeated-run record would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/input/study-task.md`, `content/workspace/analysis.py`, `content/workspace/results/summary.json` | Inputs and results have separate directories and code is a separate script, but the environment is absent and the separation is not versioned. |
| should/004 | E.1 | partial | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/replay.json` | The assessor replay ran in a fresh delivery copy on the same host with a reused prepared environment, not a fresh container or clean VM. |
| should/005 | E.1 | unmet | judgement | `content/workspace/report.md`, `content/workspace/analysis.py` | The documented workflow invokes a shared prepared interpreter and creates no disposable environment per run. |
| should/006 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-21-j01/attempt-01/judgment/2026-10-16-probes.json` | No environment lock or capture exists to reconstitute and test against the reported results. |
| should/007 | D.2 | unmet | judgement | `content/workspace/report.md`, `content/workspace/analysis.py` | The project archives no environment specification, image or executable; the prepared interpreter remains outside the delivered boundary. |
| should/008 | D.2 | unmet | judgement | `content/workspace/report.md` | No dependency-update process is documented or tracked; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | — | N/A: the complete source inventory identifies no access-restricted data or software module. |
| may/001 | M.2 | not-applicable | judgement | — | N/A: the study contains no independently maintained project modules; runtime packages are dependencies, not project components. |
| may/002 | M.2 | partial | judgement | `content/workspace/report.md` | The report explains input and result roles, but does not document modular boundaries or how components can be recombined. |
| may/003 | M.2 | partial | judgement | `content/workspace/analysis.py` | Input, analysis and output paths are distinct, but their boundaries are not defined for independent updates. |
| may/004 | M.2 | not-applicable | judgement | `content/workspace/analysis.py` | N/A: there are no independently maintained project modules to compose; the analysis is a single script. |
| may/005 | M.2 | met | judgement | `content/workspace/report.md` | The report explains the analysis route and points readers to inputs, code and results. |

## Checklist URL and provenance stamp

Checklist URL: [2026-10-16-url.txt](2026-10-16-url.txt). Machine-readable answers: [2026-10-16-response.json](2026-10-16-response.json). Probes: [2026-10-16-probes.json](2026-10-16-probes.json). Replay record: [replay.json](replay.json).

Produced by assess-alignment-with-stamped-principles 0.1.0 with stamped-conventions 0.1.0, checklist 0.3.1 (stamped-checklist-schema@v0.3.1, af259ba), on canonical capture SHA-256 658531a315fac6eb936c0366c378bf110333f70d6bf0a10dd9dea9f30a58547d, original commit 0acda2e09b35799b07d22052122402c9e54c8965, 2026-10-16, Codex API / GPT-6 (variant and runtime version not exposed). Probe output: 2026-10-16-probes.json.

Scientific adequacy record: [scientific-judgment.json](scientific-judgment.json).
