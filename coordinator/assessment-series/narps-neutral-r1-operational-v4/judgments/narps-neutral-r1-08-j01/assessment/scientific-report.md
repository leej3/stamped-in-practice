# Independent assessment: NARPS equal-indifference gain effect

Assessment date: 2026-10-16. Object kind: **study**. Assumption: its goal is the documented group-level test of a positive gain effect in vmPFC using the supplied participant maps; no human correction to that goal or kind was available.

## STAMPED verdicts

MUST: 4 met / 0 partial / 13 unmet / 0 not-checked (17 total). SHOULD: 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable (9 total). MAY: 0 met / 1 partial / 3 unmet / 0 not-checked / 1 not-applicable (5 total). These are per-item results, not an overall score.

### What to improve first

- Add a locked environment declaration and a short installation/usage route, including how the MNI brain mask is obtained. This makes the supplied workflow runnable and its outputs attributable to an exact environment (must/003, 006, 007, 010–017; should/005–008).
- Track the analysis script, report, figures and results in a worker commit. At stop, these were untracked, so Git history did not preserve the worker's actual analysis or outputs (must/004; should/001).
- Document an authorized route for a researcher to retrieve the scientific artifacts, with coverage for code, data, results and figures (must/016; access record).

### What is already strong

- The complete delivery includes the 54 supplied participant maps and their cohort metadata, so the scientific result can be reviewed against its stated inputs. Their annex state was supplied and earns no worker data-versioning credit (input/data/sub-001_hypo1_cope.nii.gz; input/participants.tsv; worker stop receipt).
- The analysis uses relative paths, makes participant-level group inference, documents its mask/coverage rule and applies one-sided whole-brain max-T FWE correction (analysis.py; REPORT.md).
- The report interprets the gain coefficients as normalized-modulator effects rather than currency-unit slopes and limits its conclusion to evidence for this group and model (input/upstream-methods.md; REPORT.md).

## Scientific assessment

**Scientific adequacy: supported.** The reported inference that this analysis does not support a positive gain response in vmPFC is supported by the supplied participant-level estimates and the documented whole-brain corrected analysis. This judgment evaluates the reported conclusion, not whether the true effect is exactly zero.

**Hypothesis conclusion:** No whole-brain-corrected evidence supports a positive gain response in the vmPFC proxy; the analysis instead finds a corrected posterior effect.

The worker reports 54 participants, no exclusions, common grid 97 × 115 × 81 at 2 × 2 × 2.4 mm, and 190,657 voxels after resampling a standard MNI152 brain mask and retaining voxels nonzero in at least 95% of maps. The input cohort table and supplied maps correspond to the task. The one-sample equal-participant test uses 10,000 participant-level sign flips and max-T across the analysis mask for positive whole-brain FWE inference (analysis.py; REPORT.md; results/summary.json). The reported maximum is t(53)=6.62 at [−26, −102, −3.6], FWE p=.00090, with 23 corrected voxels; this is posterior and does not answer the vmPFC question.

The vmPFC proxy is a 12-mm sphere at MNI [0, 40, −12], intersected with the tested mask. Its mean is −0.0057 (95% t interval [−0.0323, 0.0210]); the positive one-sample test is t(53)=−0.43, p=.664, and no proxy voxel survives whole-brain correction (maximum proxy t=2.12, FWE p=1.00). This is a defensible operational anatomical definition, although the boundary of vmPFC is not unique. The result is not evidence of an exact null: the interval permits modest effects in either direction.

The maps are participant contrast estimates, not standardized statistics. The supplied upstream method mean-centers and variance-normalizes the gain modulator, so the coefficient is not an effect per unit of money; separate gain and loss models and response-time event durations condition its interpretation. No participant variance maps were supplied, so equal-weight group inference is reasonable and precision-weighted inference is unavailable. The sign-flip test assumes exchangeable, approximately symmetric participant effects; the worker discloses this assumption.

One limitation is that the script treats zero-valued map voxels as missing when constructing coverage, then includes zero values at retained voxels with up to 5% missing coverage. Whole-brain nonzero coverage is high (97.4–99.8%), but the report does not separately quantify missingness within the vmPFC proxy. This could attenuate local estimates modestly; the available evidence does not indicate a material error that overturns the carefully bounded conclusion. The capture has pre-existing outputs but no safe replay was performed, so this assessment does not claim independent computational reproduction.

## Worker stop state, access and capture integrity

The worker-stop receipt identifies a complete capture at 2026-10-16 06:30:33 UTC with HEAD `eece8595d255a766517e32ff10b2e6574d3c4e6a`. At that stop state, `REPORT.md`, `analysis.py`, `figures/` and `results/` were untracked; the Git commit therefore does not contain the delivered analysis. The participant data links were already present in the supplied Git-annex state. Later coordinator preservation of the complete delivery is not worker publication, tracking or environment provenance. No remote is configured for the captured Git repository, and no worker-declared authorized route for the scientific outputs was found. The source URLs identify upstream inputs, not access to this analysis. See access-record.json.

The captured `.codex/hooks.json` and `.entire/settings.local.json` identify Codex hooks and Entire session-checkpoint configuration. This records an assistance-related exposure only; session contents and identifiers were not used as grading evidence, and no treatment assignment is inferred. No other worker's material or prior judgment was inspected. During runner syntax discovery, a coordinator procedure file was inadvertently displayed and contained allocation metadata. This assessor-process exposure was not used to select, analyze or characterize target evidence; no assignment information is stated here.

Assessment-runner probes and Git inspection changed only `.git/annex/keysdb/db` among the separately classified metadata files. No other workspace byte, link target, index, ref, object or configuration mismatch was detected against the operational manifest. This database change is inspection-induced metadata, not worker evidence; logical database equivalence is not claimed. The launcher independently verifies canonical identity before and after assessment. Assessment command records and separate stdout/stderr are in assessment-commands.json and the named log files.

## Replay record

Replay is **not checked**. The documented command is `python analysis.py`, but the worker supplied no dependency lock or environment manifest, and the script calls Nilearn's template-mask loader without documenting whether its asset is already cached or must be retrieved. Installing or retrieving missing prerequisites would exceed this assessment's allowed reconstruction. The explicit candidate outputs and comparison plan are recorded in replay-record.json; the planned numeric comparison uses rtol 1e-6 and atol 1e-7 to accommodate float32 output near zero, with geometry checked exactly. No attempt, command, output deletion or execution occurred.

## Individual checklist answers

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `REPORT.md` | The delivered study, inputs, code and results share one workspace root. |
| must/002 | S.1 | met | judgement | `input/data/sub-001_hypo1_cope.nii.gz` | All participant maps resolve through annex symlinks inside the captured root. |
| must/003 | S.1 | unmet | judgement | `analysis.py` | Python packages and the MNI mask source are assumed rather than declared in a supplied environment. |
| must/004 | T.1,T.3,T.5 | unmet | judgement | `REPORT.md` | Git exists, but the worker’s code, report and generated results were untracked at stop. |
| must/005 | T.1,T.3,T.5 | unmet | probe:large-in-annex+judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-08-j01/attempt-01/worker-end-state.json` | The annex-managed input maps were supplied; the worker’s own analysis and results were not tracked. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `results/summary.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-08-j01/attempt-01/worker-end-state.json` | No run record links the generated results to an exact software environment. |
| must/007 | A.1 | unmet | judgement | `REPORT.md` | The report gives a command but no installation steps or usable environment instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-08-j01/attempt-01/worker-end-state.json` | The complete delivery names analysis.py as the group workflow starting point. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-08-j01/attempt-01/worker-end-state.json` | The delivered workflow derives its root from its location and uses relative paths. |
| must/010 | P.1 | unmet | judgement | `analysis.py` | No dependency declaration is delivered for imported packages or template-mask retrieval. |
| must/011 | P.1 | unmet | judgement | `REPORT.md` | The documented route assumes an unspecified supplied Python environment and host setup. |
| must/012 | P.2 | unmet | judgement | `REPORT.md` | No installation or system-dependency list is provided. |
| must/013 | P.3 | unmet | judgement | `probes.json` | No environment specification is present alongside the workflow. |
| must/014 | P.3 | unmet | judgement | `REPORT.md` | No environment-update process is declared. |
| must/015 | D.1 | unmet | judgement | `results/summary.json` | There is no frozen manifest or container identity for the environment that produced results. |
| must/016 | D.1 | unmet | judgement | `REPORT.md` | No retrievable environment specification is included or linked. |
| must/017 | D.1 | unmet | judgement | `REPORT.md` | Readers are not told how to obtain or construct the assumed Python environment. |
| should/001 | T.2 | partial | judgement | `REPORT.md` | Supplied inputs are versioned, but the worker’s code and result components remain untracked. |
| should/002 | A.2 | not-checked | judgement | `probes.json` | No repeat-run or regular workflow-testing record is supplied; a testing record would settle this. |
| should/003 | M.1 | partial | judgement | `input/participants.tsv` | Inputs, results and figures are separated, but code and environment are not distinct modules. |
| should/004 | E.1 | not-checked | judgement | `REPORT.md` | The stopped state has outputs but no evidence of a clean container or host test; such a run record would settle this. |
| should/005 | E.1 | unmet | judgement | `analysis.py` | The workflow does not create or describe a disposable execution environment. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `probes.json`, `REPORT.md` | No supplied environment specification exists to reconstitute and test. |
| should/007 | D.2 | unmet | judgement | `REPORT.md` | No environment image, package archive or executable environment is included. |
| should/008 | D.2 | unmet | judgement | `REPORT.md` | No process for regenerating and tracking environment specifications is declared. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: No restricted data or software component is identified in this public-data study. |
| may/001 | M.2 | not-applicable | judgement | `input/sources.json` | N/A: No independently maintained project component is present; data and packages are dependencies. |
| may/002 | M.2 | unmet | judgement | `REPORT.md` | The folders are separated, but the report does not describe component relationships or recombination. |
| may/003 | M.2 | partial | judgement | `input/participants.tsv` | Data and output folders offer some separation, but independent update boundaries are not described. |
| may/004 | M.2 | unmet | judgement | `REPORT.md` | No module composition or orchestration mechanism is documented. |
| may/005 | M.2 | unmet | judgement | `REPORT.md` | No navigation or modular-structure guide is supplied. |

## Flagged items

- must/014 and should/008 carry `upstream-duplicate`: the checklist repeats the same environment-update question.
- must/005, must/006 and must/008 override probes that saw only tracked paths; should/006 is an evidence-based override of the probe’s not-checked state: the complete worker-stop delivery contains supplied annex data and untracked analysis artifacts. The annex state was coordinator-supplied, while analysis.py and its products exist but are not tracked. Probe output and reasons are retained in probes.json and response.json.

## Not checked

- should/002: no repeated workflow-test record was supplied; a recurring test record would settle it.
- should/004: the stopped outputs do not establish a fresh container/VM test; a completed clean-host execution record would settle it.
- Replay: a worker-supplied environment declaration and documented mask-asset prerequisite are needed for a safe attempt.
- Access: a worker-declared authorized publication route and a remote-host retrieval test covering the listed artifacts would settle accessibility.

## Checklist link and provenance

[Open the completed checklist](checklist-url.txt). Machine-readable answers and evidence are in [response.json](response.json); scientific judgment is separately recorded in [scientific-judgment.json](scientific-judgment.json).

Evidence key: all paths naming original artifacts above are capture-relative and identify bytes in canonical delivery SHA-256 `2afd81ca5fdfaa03e85f2d3e65b04aac9f4b3d90eb39f95c2497266e4cf3cdc7`. Key file hashes: `REPORT.md` a621fde6376b7af8f5b3a120d631fb1bf16585dc1fce16ef3029d12901a0d769; `analysis.py` e06520fcf4667336e63c864ad33f286e50ccea6b08409081532ab9daf3d905c3; `results/summary.json` 302e27d4392831093cbee1baadb0c8969f61f22a6b8b7432b3945b7c3e785c7c; `input/upstream-methods.md` 508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b; `input/participants.tsv` faca815bcb042144bdb8dcff915f45de0d27650f60416ed76a5a72557341abbf. Worker stop receipt SHA-256: 77c8a710004eeb6bc42610e3a53bb6905ac963c8746604860256cf30491dde98.

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on capture `2afd81ca5fdfaa03e85f2d3e65b04aac9f4b3d90eb39f95c2497266e4cf3cdc7`, original commit `eece8595d255a766517e32ff10b2e6574d3c4e6a`, 2026-10-16, OpenAI Codex API / GPT-6 family (exact served model unavailable). Probe output: probes.json.
