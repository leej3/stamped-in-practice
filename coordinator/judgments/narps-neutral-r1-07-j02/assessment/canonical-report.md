# Independent assessment: NARPS potential gains and vmPFC

## Verdict

**MUST:** 5 met / 3 partial / 9 unmet / 0 not-checked. **SHOULD:** 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable. **MAY:** 3 met / 1 partial / 0 unmet / 0 not-checked / 1 not-applicable. These are item findings, not an overall score.

## Scientific assessment

**Scientific adequacy: supported** for the reported conclusion that the supplied data do not support a positive vmPFC gain effect at the required whole-brain corrected standard. **Reported hypothesis outcome: no support for a positive vmPFC result.** This does not establish a zero or absent vmPFC response.

The original NARPS instructions request a binary hypothesis decision based on whole-brain-corrected analysis; this analysis meets that inferential scope. [Original NARPS analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf) The analysis uses all 54 equal-indifference participants as independent units and correctly treats the supplied images as participant COPE effect estimates, not t/z maps or effects per currency unit. It checks IDs, checksums, image dimensions and affine, finite and nonzero support, and uses a matching MNI152NLin2009cAsym brain mask. A one-sample random-effects t statistic with 9,999 participant-level sign flips and max-T whole-brain FWE correction addresses the original study's correction requirement. The analysis reports an independent SciPy check and participant-level uncertainty.

In the vmPFC midline box (|x| ≤ 10, y=20–60, z=−20–20 mm), the mean is −0.0026 COPE (95% t interval −0.0219 to 0.0167; n=54), with descriptive one-sided p=.606. The most positive voxel in that box has t=4.19 and whole-brain max-T p=.7742. No vmPFC voxel survives correction. There are 24 corrected positive voxels in three small descriptive clusters; the maximum is posterior at (−26, −102, −3.6) mm, t(53)=6.62, max-T p=.0006. These posterior findings do not support the vmPFC hypothesis.

The conclusion is conditional on AO86's fixed first-level models. Mean-centered, variance-normalized gain regressors mean the COPE is not a currency-unit slope; gain effects are conditional on separate gain/loss models and do not establish an isolated causal effect of gain. The voxelwise sign-flip inference relies on exchangeability and approximate symmetry under the null. Participant variance maps are unavailable, so the unweighted one-sample t model is reasonable but cannot use first-level uncertainty. The descriptive ROI interval crosses zero and is not evidence of equivalence. The final analysis mask covers 186,192/196,466 template brain voxels (94.8%) after requiring nonzero support in every participant. The midline box is a transparent operational vmPFC definition, though not a parcel-specific anatomical delineation.

The preserved pilot uses shared map support without an anatomical brain mask. It retains the same posterior maximum and vmPFC summary, but the anatomically constrained `primary_v2_template_mask` is the appropriate primary result. It is separately named and the protocol explains the revision. The report appropriately distinguishes lack of corrected support from evidence of no response.

## Delivery and worker-stop boundary

The capture manifest was SHA-256 verified against the stop receipt: all 1,222 entries matched, with zero capture errors or omissions. The worker stop receipt records a normal exit at 2026-10-16 06:48:11 UTC and HEAD `d857ab1302d13cb660a7a044af07141f44bfa9ba`. At that stop, the analysis script, report, README, protocol, figures, outputs and template files were untracked; the seed commit and annex-backed participant inputs were committed. The scientific content was assessed from the complete unchanged captured delivery, including those untracked files. Later preservation and this assessment's files do not earn worker-practice credit.

The output includes `.codex` hook configuration and `.entire` session artifacts, indicating coding-assistant tooling exposure. Their contents were not used as evidence for scientific or STAMPED verdicts. No treatment assignment was inferred or reported.

## Replay

One replay used the full captured delivery copied to a new writable directory. Before running, the command was declared as the README's exact prepared interpreter followed by `analysis/analyze.py`; prerequisites were the documented Python 3.13.16 environment and named packages, with no installation or repair. The 11 selected generated outputs were the four primary NIfTI maps, four CSV tables, summary JSON and two primary figures. Tables were eligible for numeric comparison at rtol 1e−6; other outputs were compared byte-for-byte. All 11 were byte-identical; the command exited 0 in 17.8 seconds. This supports repeatability on the same host and existing documented environment; it does not verify clean environment reconstruction or another host. Replay stdout/stderr and the frozen helper record are retained in `replay-copy/` and `2026-10-16-fresh-rerun.json`. The captured `.git/config` names a host-local hooks path; that external path was not followed, and the replay helper disabled hooks only in the replay process environment as recorded.

## Access check

The intended recipient is a researcher using the worker-declared route. The worker supplied no full-object publication or authorized retrieval route in the README, repository config or stop receipt. The complete coordinator-captured object available to this assessor is not proof of worker sharing. The input source manifest declares per-file NeuroVault URLs and TemplateFlow template URLs. HTTP HEAD returned 200 for one map on `neurovault.org` and the analysis mask on `templateflow.s3.amazonaws.com` (0 bytes retrieved); the remaining per-file URLs and access by other recipients were not tested. Those routes cover selected input resources only, not code, report, results, figures or the environment required to rerun. See `access-record.json` and retained headers.

## What to address first

- Track the delivered analysis, protocol, report, figures and results in the worker's version-control state → makes the submitted scientific state traceable → must/004, should/001.
- Supply a complete, pinned environment specification and link the result record to it → lets a researcher reconstruct the software that generated the maps → must/003, must/006, must/010, must/013, must/015, must/017.
- Replace the host-specific interpreter path with documented environment acquisition and usage instructions → makes the run route usable beyond the worker host → must/009, must/011, must/012, must/017.
- Publish or record an authorized route to the complete project artifacts and environment → enables recipient retrieval of the actual scientific delivery → must/016.

## What is already strong

- The final group method is explicitly specified and tests positive effects with whole-brain max-T familywise correction; the code and result summary make the mask, participant unit, seed and uncertainty inspectable (`research-protocol.md`, `analysis/analyze.py`, `results/primary_v2_template_mask/summary.json`).
- The report explains the fixed upstream model and gain-scaling limits, non-significant vmPFC finding, posterior corrected result and meaning of non-rejection (`input/upstream-methods.md`, `scientific-report.md`).
- Participant inputs have source URLs, identities and checksums; all 54 large map payloads are present through annex-backed links (`input/sources.json`, `probes.json`).

## Per-item attainment

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `README.md`, `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-07-j02/manifest.json` | All supplied project files resolve within the workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `analysis/analyze.py` | All fixed maps and templates are included under the root and referenced by relative workflow paths. |
| must/003 | S.1 | unmet | judgement | `README.md`, `research-protocol.md` | The documented interpreter and packages are outside the root; no contained or linked software environment is supplied. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j02/attempt-01/judgment/probes.json`, `analysis/analyze.py` | Git tracks the seed, while the analysis, report, figures and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j02/attempt-01/judgment/probes.json` | All 54 large participant maps are tracked through git-annex, with their payloads present in the captured delivery. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `results/primary_v2_template_mask/summary.json`, `README.md` | Run summary records software versions but no exact environment specification or lock used for these results. |
| must/007 | A.1 | met | probe:entry-point+judgement | `README.md` | README gives installation context and a usage command for the analysis. |
| must/008 | A.1 | met | probe:entry-point+judgement | `README.md`, `analysis/analyze.py` | The analysis script is a clear starting point and is named by the documented command. |
| must/009 | P.1 | unmet | probe:no-abs-paths+judgement | `README.md` | README hardcodes a host-specific absolute interpreter path in the documented run command. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j02/attempt-01/judgment/probes.json` | No environment specification declares the analysis dependencies; the README only names packages in an external environment. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `README.md` | Python and package assumptions are listed, but the host environment and requirements for obtaining that interpreter are not documented. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `README.md`, `research-protocol.md` | README names Python and the main packages, but gives no complete system requirements or reproducible dependency list. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j02/attempt-01/judgment/probes.json`, `README.md` | No environment specification is present in the worker delivery or tracked commit. |
| must/014 | P.3 | unmet | judgement | `README.md`, `research-protocol.md` | No process or command for updating an environment specification is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/primary_v2_template_mask/summary.json`, `README.md` | No frozen environment specification or digest is supplied for the analysis environment. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j02/attempt-01/judgment/access-record.json` | No worker-declared route shares an environment specification for other researchers to obtain. |
| must/017 | D.1 | unmet | judgement | `README.md`, `research-protocol.md` | README shows how to invoke a pre-existing host environment but does not explain how to obtain or recreate its specification. |
| should/001 | T.2 | partial | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j02/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-07-j02/manifest.json` | Git and annex cover seed inputs, but code, documentation, figures and results were untracked at stop. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `results/attempts/20261016_plot-rerun-error.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j02/attempt-01/judgment/fresh-rerun.json` | One completed analysis and an earlier figure-generation failure are recorded; regular testing cadence cannot be established. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j02/attempt-01/judgment/probes.json` | Inputs, code, results and figures have separate directories, but no environment module is supplied. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-07/judgments/narps-neutral-r1-07-j02/attempt-01/judgment/fresh-rerun.json`, `README.md` | The replay used a fresh copy but the existing documented environment; no fresh environment reconstruction was attempted. |
| should/005 | E.1 | unmet | judgement | `README.md` | The documented command reuses a long-lived prepared interpreter; it does not create a disposable environment. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `README.md`, `results/primary_v2_template_mask/summary.json` | No exact environment specification is available to reconstitute or test regularly. |
| should/007 | D.2 | unmet | judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-07-j02/manifest.json` | The Python environment and its executable artifacts are not archived with the workspace. |
| should/008 | D.2 | unmet | judgement | `README.md`, `research-protocol.md` | No process or command for updating an environment specification is supplied; duplicate of must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json`, `README.md` | N/A: all supplied datasets and templates are public and no restricted component is identified. |
| may/001 | M.2 | not-applicable | judgement | `README.md`, `input/sources.json` | N/A: no independently maintained project component is linked as a module; datasets and templates are captured in the root. |
| may/002 | M.2 | met | judgement | `README.md` | README explains the input, analysis, results and figure relationships. |
| may/003 | M.2 | partial | judgement | `analysis/analyze.py`, `README.md` | Input/code/output boundaries are visible, but the workflow is tightly coupled to fixed paths and no environment boundary exists. |
| may/004 | M.2 | met | judgement | `analysis/analyze.py`, `README.md` | The analysis script composes the captured input and template files into results and figures. |
| may/005 | M.2 | met | judgement | `README.md` | README describes the main directories and generated artifacts for navigation. |

## Extra probe finding

No reuse license is declared for the worker workspace; the only license files in the capture belong to coordinator-supplied external skill resources, not the scientific delivery. This extra finding has no checklist item (`license-declared` in [the probe output](2026-10-16-probes.json)).

## Flagged probe disagreements

- **must/002:** the probe could not assess external inputs without submodules; the complete delivery contains the maps and mask under the root with relative workflow paths.
- **must/004 and should/001:** the probe found untracked files from Git status; the worker-stop inventory confirms that major work products were untracked, so the item is partial rather than a claim that no VCS was used.
- **must/006 and should/006:** the probe found no recognized run record; the result summary is a run record, but it reports versions rather than an exact environment specification, so attainment is unmet.
- **must/007 and must/008:** the tracked-path probe missed the untracked README and analysis script; both document a usable start point.
- **must/009:** the probe scanned tracked text only; the complete delivery's README contains an absolute host-specific interpreter path.
- **must/010, must/011, must/012 and must/016:** probe outcomes were based on tracked configuration or command scans; inspection of the full delivery shows package names and an external interpreter but no environment specification, complete host requirements or shared environment route.
- **should/008:** repeats must/014, as flagged by the pinned checklist guidance.

## Not checked

- **should/002:** one successful replay and one recorded plotting failure cannot establish regular testing; a dated cadence or repeated test history would settle this.
- **should/004:** the replay used a fresh copy but the existing host environment; a replay in a newly reconstructed environment would settle fresh-environment testing.

## Goals and kind

The stated goal is a group-stage NARPS Hypothesis 1 analysis of the positive gain effect in vmPFC for the equal-indifference group, conditional on supplied participant maps (`input/study-task.md`). The object is a **study**: it includes analysis code, scientific results, fixed input data, and interpretive reporting.

## Checklist link and assessment stamp

[Open the completed checklist](2026-10-16-url.txt). The validated item responses are in [2026-10-16-response.json](2026-10-16-response.json); the complete probe output is in [2026-10-16-probes.json](2026-10-16-probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the captured study at commit `d857ab1302d13cb660a7a044af07141f44bfa9ba`, 2026-10-16, Codex API agent / GPT-6 (exact deployment identifier unavailable). Probe output: [2026-10-16-probes.json](2026-10-16-probes.json). Capture manifest SHA-256: `a870dc3c816f624dcd1ecd9e513fe56b76cf182e109a2f95963749235a4df8d7`.
