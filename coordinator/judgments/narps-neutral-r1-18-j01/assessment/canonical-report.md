# Independent assessment — NARPS gain-effect study

**Scientific adequacy: qualified. Reported hypothesis outcome: not supported.** The analysis supports the bounded conclusion that these supplied participant gain-effect maps do not show a positive average vmPFC response under the stated group model and whole-brain correction. The result is conditional on upstream participant models and symmetric sign-flip assumptions; it is not a test of gain response per currency unit.

**STAMPED verdicts:** MUST: 4 met / 1 partial / 12 unmet / 0 not-checked (17 total). SHOULD: 1 met / 1 partial / 5 unmet / 1 not-checked / 1 not-applicable (9 total). MAY: 2 met / 3 partial (5 total). No overall score is assigned.

## Delivery and assessment boundary

The delivery manifest verified against the supplied worker stop receipt. Capture SHA-256 is `e72b24b4fadd4e55dc6cb69acb18172372637f551fa6a40c3d99eb68f6ec29da`; the receipt records worker commit `afb62884c70115b6e46a92ddcd1d17bbf4f33544`, a complete capture, and no capture errors or omissions. The captured workspace includes the untracked code, report, notebook, figures, results, and ignored coordinator files. There is no mismatch between the retained capture and stop receipt. The source object was not repaired or changed.

At worker stop, Git tracked the supplied starter and input metadata while `analysis.py`, the report, notebook, figures, and results were untracked; these later artifacts therefore do not earn worker versioning credit. `.codex/` and `.entire/` are recorded as supplied session infrastructure, not worker products. Coordinator preservation and delivery do not establish worker publication or recipient access. `judge-target.json` has no reference limits; no external `.git` pointer or original absolute link target was followed. Read-only Git probes used the captured repository directory; no hooks were run. An untracked `.skills/jupyter-notebook/` directory was present; its presence alone does not establish use and was not grading evidence.

The frozen assessor version check passed before probes or response actions. The probe sweep is retained in [`2026-10-16-probes.json`](2026-10-16-probes.json). Probe results were reviewed against the complete stopped workspace, including untracked and ignored files.

## Scientific assessment

The worker reports a one-sample group analysis of all 54 equal-indifference participants’ unthresholded cope maps, using the intersection of nonzero coverage (198,029 voxels) and a positive-direction, 5,000-draw sign-flip max-T test for whole-brain voxelwise FWER. The supplied output reports a max-T threshold of 5.397, with 24 positive voxels passing correction. The global maximum is in posterior/occipital cortex, outside the vmPFC hypothesis region. For a non-circular 12-mm sphere centered at MNI (0, 42, −10), the mean participant cope is −0.0078 (SD 0.0996; 95% t interval −0.0350 to 0.0194), t(53)=−0.58, one-sided p=.717; the minimum whole-brain-corrected p in the sphere is 1.00. The report also gives sign-flip and Wilcoxon ROI sensitivities, and leave-one-out means remain negative. These values appear consistently in `reports/report.md`, `results/summary.json`, `results/vmPFC_participant_summary.tsv`, `results/top_peaks.tsv`, and the supplied figures.

The analysis handles the supplied estimates as participant-level effect estimates, not t/z maps; uses all 54 cohort members; checks byte identities, finite values, dimensions, and affine consistency; and avoids treating noncoverage zeros as measured data through the common-coverage intersection. The vmPFC localization is specified from an external meta-analytic coordinate rather than selected from these maps. Whole-brain max-T correction addresses the task’s required familywise inference. The report appropriately limits interpretation because upstream gain scaling was normalized, participant variance maps are absent, and the sign-flip test assumes symmetric exchangeability.

Adequacy is **qualified** because spatial QC establishes common grid and affine but does not independently inspect participant-level anatomical alignment; the strict all-participant nonzero-coverage mask may omit partially covered voxels; and no first-level variance maps are available for precision weighting or full uncertainty propagation. These caveats do not create a material inference error in the reported absence of positive vmPFC support. “Not supported” means no evidence for a positive average effect at this tested scale and model; it does not establish a zero effect or rule out smaller effects. The positive corrected posterior findings do not support the vmPFC-specific hypothesis.

## Replay

Before any replay, the declared command was `python analysis.py` from the workspace root; the report says to use a “prepared Python environment,” and the notebook names a host-specific interpreter under `/Users/johnlee/.../common-environment/.pixi/envs/default/bin/python`. No environment or dependency declaration explains how to reconstruct it. Replay is **not checked**: using the coordinator’s installed environment would substitute an undeclared prerequisite, so no replay copy was created, no shipped outputs were removed, and no scientific command was run. The exact selected generated artifacts, comparison rule, limits, and reason are recorded in [`replay-record.json`](replay-record.json). Existing shipped outputs were treated as analysis evidence, not replay evidence.

## Access

The intended recipient is a researcher using the source route in `input/sources.json`. The tested host scope was `neurovault.org`: the collection URL and one participant map URL returned HTTP 200; the map response advertised 1,794,522 bytes. This checks only current source input availability, not retrieval of all 54 payloads or their checksums. No worker-declared route for the complete analysis, report, figures, result files, and environment was found. The coordinator’s delivery to this assessment is not evidence that the worker made those artifacts accessible. Details and retained command output are in [`access-record.json`](access-record.json) and `access-*.stdout` / `access-*.stderr`.

## What to fix first

1. Track the worker-created code, report, notebook, figures, and result files, and retain a run record that names the command and exact environment. This would make the delivered scientific answer auditable and close must/004 and must/006.
2. Supply a pinned environment/dependency specification, host requirements, setup instructions, and a recipient route for the complete study. This closes the main portability, actionability, and sharing gaps (must/003, must/007, must/010–017).
3. Replace the notebook’s hardcoded interpreter path with the documented relative/reconstructable route (must/009).
4. Add a recurring instruction check and a fresh-environment execution record once the environment is declared (should/002, should/004, should/006).
5. Document component boundaries and reuse terms for the complete object (should/003, may/002–005; extra finding `license-declared`).

## What is already good

- The analysis code and report make the group model, one-sided whole-brain correction, vmPFC localization, uncertainty, exclusions, and upstream limitations inspectable (`analysis.py`, `reports/report.md`).
- Input provenance identifies the source collection, cohort table, methods report, and per-map checksums; 54 large maps are retained through git-annex (`input/sources.json`, `input/data/`, probe evidence).
- The scientific report distinguishes the vmPFC hypothesis from corrected findings elsewhere and avoids claiming a per-currency effect (`results/summary.json`, `figures/whole_brain_maxT.png`).

## Per-item STAMPED findings

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `.`, `input/sources.json` | The complete delivery is nested under one workspace root. |
| must/002 | S.1 | met | judgement | `input/data/`, `input/sources.json` | All 54 maps and metadata are included through in-boundary annex links; no external pointer is needed. |
| must/003 | S.1 | unmet | judgement | `analysis.py`, `reports/report.md` | analysis.py imports external scientific packages, but the delivery has no environment specification or linked software module. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `probe:tree-clean`, `input/study-task.md` | Git tracks the supplied inputs and metadata, but worker-authored code, report, figures and results are uncommitted. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex`, `worker-end-state.json` | The 54 large maps are git-annex content, with pointer metadata and payloads retained in the complete capture. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `reports/report.md`, `analysis.py` | Shipped results lack a worker run record linking the action and exact environment; the report only gives a command and unspecified prepared environment. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `reports/report.md#Reproducibility` | The report gives a usage command but no installation or environment setup instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analysis.py`, `reports/report.md#Reproducibility` | analysis.py is a clear runnable entrypoint and writes the named results and figures. |
| must/009 | P.1 | unmet | probe:no-abs-paths+judgement | `narps_gain_analysis.ipynb` | The notebook hardcodes a host-specific absolute Python path, so the documented notebook route is not portable. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analysis.py`, `probe:env-spec-tracked` | No delivered environment specification declares the scientific Python dependencies imported by analysis.py. |
| must/011 | P.1 | unmet | judgement | `reports/report.md#Reproducibility`, `narps_gain_analysis.ipynb` | The route assumes a preconfigured Python environment, but the required host/runtime assumptions are not documented. |
| must/012 | P.2 | unmet | judgement | `analysis.py`, `reports/report.md#Reproducibility` | No system requirements or dependency list is supplied for the documented execution route. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked` | No environment specification is present in the complete stopped delivery. |
| must/014 | P.3 | unmet | judgement | `Complete delivery inventory` | No dependency update process or environment specification is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `reports/report.md#Reproducibility`, `Complete delivery inventory` | No frozen environment specification identifies the environment used for these results. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `input/sources.json`, `access-record.json` | No worker route publishes the environment; the NeuroVault links cover inputs only, not code, report and derived results. |
| must/017 | D.1 | unmet | judgement | `reports/report.md#Reproducibility` | The report names a prepared environment but does not explain how a researcher can obtain or use it. |
| should/001 | T.2 | met | judgement | `.git/config`, `probe:large-in-annex` | Git tracks text and metadata while git-annex carries the large maps within the same repository system. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `probe:ci-present`, `Complete delivery inventory` | The complete delivery has no CI or recurring workflow test that checks its instructions. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/, results/, figures/`, `analysis.py` | Inputs and outputs have separate folders, but code remains at root and no environment module is supplied. |
| should/004 | E.1 | not-checked | judgement | `replay-record.json` | No safe fresh-environment replay or worker fresh-environment run record is available; the environment is unspecified. |
| should/005 | E.1 | unmet | judgement | `narps_gain_analysis.ipynb` | The notebook invokes a fixed pre-existing host environment; no per-run disposable environment is created. |
| should/006 | D.2 | unmet | probe:env-spec-tracked+judgement | `probe:env-spec-tracked` | No exact environment specification is supplied to reconstitute or test. |
| should/007 | D.2 | unmet | judgement | `Complete delivery inventory` | No environment artifacts, such as a container or archived binaries, are included. |
| should/008 | D.2 | unmet | judgement | `Complete delivery inventory` | No environment update process or specification is supplied; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the identified input maps are publicly retrievable and no restricted data or software component is present. |
| may/001 | M.2 | met | judgement | `input/sources.json`, `input/data/` | The upstream dataset is independently identified and retrievable, and the delivered input module retains its map payloads. |
| may/002 | M.2 | partial | judgement | `reports/report.md#Reproducibility`, `input/sources.json` | The report names input, results and figure locations, but does not document how components relate or are recombined. |
| may/003 | M.2 | partial | judgement | `analysis.py`, `Complete delivery inventory` | Inputs and outputs are separated, but code and environment are not independent modules and no interface contract is documented. |
| may/004 | M.2 | met | judgement | `analysis.py` | analysis.py composes the supplied inputs, group analysis and generated outputs through explicit workspace paths. |
| may/005 | M.2 | partial | judgement | `reports/report.md#Reproducibility`, `Complete delivery inventory` | The report gives an entry command and output locations, but there is no README or component guide for navigating the workspace. |

## Flagged items

- **must/004** — the tree-clean probe measured whether the entire Git worktree was committed. Review of the full stop state shows Git was used for supplied files, but the worker’s analysis products were untracked, so the item is partial.
- **must/006** — the probe did not recognize an execution record; inspection of the full delivery confirms there is no worker record linking generated results to an exact environment.
- **must/007** — the filename probe missed `reports/report.md`; that file documents a usage command but omits installation/setup instructions, so the verdict remains unmet.
- **must/008** — the entry-point probe missed untracked `analysis.py`, which is a clear runnable starting point; the verdict is overridden to met.
- **must/009** — the tracked-text scan missed the untracked notebook’s host-specific interpreter path; the verdict is overridden to unmet.
- **must/014** and **should/008** — duplicate checklist questions; both are unmet because there is no environment update process or specification.
- **should/003** — the probe saw only the tracked input directory; full delivery inspection also found separate untracked output folders, while code/environment separation remains incomplete.

## Not checked

- **should/004:** no worker record establishes execution in a fresh environment, and replay was not safe without reconstructing an undeclared environment. A pinned environment plus a fresh isolated run record would settle it.

## Goals and kind

The goal, from the supplied task brief and `reports/report.md`, is to assess whether potential gain is positively associated with vmPFC response in the NARPS equal-indifference group from the supplied participant maps. The primary kind is a **study**: the product is a scientific answer with code, data, and results. This is an explicit assessment assumption, not separately confirmed by a human; it emphasizes the linkage between inputs, environment, action, and reported results.

## Checklist URL and provenance

Checklist answers: [`2026-10-16-url.txt`](2026-10-16-url.txt). Canonical response: [`2026-10-16-response.json`](2026-10-16-response.json). Extra finding outside the checklist: `license-declared` is unmet because no reuse terms are supplied (`input/sources.json` and complete delivery inventory).

Produced using `assess-alignment-with-stamped-principles` 0.1.0 and `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on the worker delivery at commit `afb62884c70115b6e46a92ddcd1d17bbf4f33544`, 2026-10-16, Codex / gpt-6-luna. Frozen assessment source commit: `9852d8360f9519d21d11099b45f5deb8ba80cb28`; runtime lock hash: `f8fff1394fbeaa2ab1c4993fceb0dd6463fe0c08c81fcda397f3e752a72c4249`. Probe output: [`2026-10-16-probes.json`](2026-10-16-probes.json). Retained delivery manifest SHA-256: `e72b24b4fadd4e55dc6cb69acb18172372637f551fa6a40c3d99eb68f6ec29da`.
