# Independent assessment — NARPS potential gains

Assessment date: 2026-10-16 UTC. Canonical capture SHA-256: `d75485e99456b2c86422f940111694530e096867cdbd581892caa49710571fe6`; captured HEAD: `129f3ae3717999e72ef6fbb9e9335f6d69c27470`. The complete operational copy matched its initial manifest except the explicitly permitted annex keys database files; see [integrity-check.json](integrity-check.json). All project evidence paths below are relative to that canonical capture and should be read at this identity.

Scientific adequacy: supported.

Reported hypothesis outcome: The 54 supplied maps do not support a greater vmPFC response as potential gain increases.

## Scientific assessment

The conclusion is adequately supported by the delivered group analysis. `analyze.py` tests the 54 supplied participant cope maps in the positive direction with a one-sample statistic and a one-sided sign-flip maximum-*t* permutation correction over the full common-support mask. The report and `results/summary.json` give the mask definition (intersection of all participants' nonzero support), 198,029 tested voxels, 4,999 permutations, seed, and familywise α=.05 threshold. It reports 24 corrected voxels in three small posterior cerebellar clusters, with no corrected voxel in its approximate vmPFC summary sphere. `results/group_summary.csv` and `results/fwe_significant_clusters.csv` provide the reported quantities; `results/figure1_group_maps.png` and `results/figure2_vmPFC_roi.png` make the spatial result and participant spread inspectable. Evidence: canonical capture `d75485e99456b2c86422f940111694530e096867cdbd581892caa49710571fe6`, paths `REPORT.md`, `analyze.py`, `results/summary.json`, `results/group_summary.csv`, `results/fwe_significant_clusters.csv`, and `results/figure1_group_maps.png` / `results/figure2_vmPFC_roi.png`.

The vmPFC sphere is centered at MNI (0, 42, −8), has a 12-mm radius and 750 tested voxels. Its participant-average cope is −0.0068 (between-participant SD 0.094; 95% *t* interval −0.0325 to 0.0189); none of its voxels passed whole-brain correction. The report correctly treats this as a descriptive anatomical summary, not a second significance test. It also distinguishes the gain-modulator cope from a per-currency BOLD slope and says that failure to detect a corrected vmPFC effect does not establish a zero effect or equivalence. The original analysis instructions' whole-brain-correction requirement is met.

The conclusion remains conditional on the fixed AO86 participant model. The report recognizes that participant variance maps are absent, so participants receive equal weight; sign-flip inference assumes exchangeability of signs under the null; and correction covers common supplied map support only. `input/upstream-methods.md` explains that gain was mean-centered and variance-normalized before convolution, runs were combined within participants, and gain and loss were modeled separately. `results/participant_qc.csv` and `input/sources.json` support the stated all-54 inclusion, map identity and checks. These are appropriate limits, not material inference errors.

Replay independently recreated four selected scientific CSV outputs from a fresh writable copy of the complete capture. All four were byte-identical after the documented script reran. This supports computational repeatability for those tables; it does not validate the scientific assumptions or establish equality of the unselected NIfTI maps, figures, JSON or prose. The replay record and preserved logs are [2026-10-16-fresh-rerun.json](2026-10-16-fresh-rerun.json), [logs/replay.stdout](logs/replay.stdout), [logs/replay.stderr](logs/replay.stderr), and [replay-copy/replay.stdout](replay-copy/replay.stdout). The exact command, supplied interpreter/package prerequisites, output selection and comparison rule were declared in [replay-declaration.md](replay-declaration.md) before the attempt.

## STAMPED verdicts

MUST: 5 met / 2 partial / 10 unmet / 0 not-checked / 0 not-applicable (17 total). SHOULD: 1 met / 1 partial / 6 unmet / 0 not-checked / 1 not-applicable (9 total). MAY: 2 met / 3 partial / 0 unmet / 0 not-checked / 0 not-applicable (5 total). A partial MUST does not satisfy that item; no overall score is calculated.

**Measurement availability:** all 31 checklist items received a verdict. The replay measured four selected CSV outputs only; other generated artifact types were not compared. The authorized project retrieval route could not be tested because none was declared; one upstream map URL was host-checked by HEAD (HTTP 200), covering that map only.

### What to fix first

1. Add a portable dependency specification and short setup/run instructions → lets another researcher recreate the analysis without the worker's host environment → must/003, must/007, must/010–017, should/006–008.
2. Track the analysis code, report and derived results in a worker revision → makes the stopped scientific state recoverable from version control → must/004.
3. Publish a worker-authorized route to the complete study and its required inputs/environment → enables a recipient to retrieve the same artifact set → must/016; current input-source links cover source maps only.
4. Keep the report's strong spatial, uncertainty and upstream-model explanations alongside the tracked result files → preserves the scientific interpretation with the reproducible artifacts → must/006, must/017.

### What the project already does well

- It includes 54 checksum-identified participant maps as annex content and keeps map provenance, cohort metadata and fixed upstream methods under `input/` (capture paths `input/sources.json`, `input/participants.tsv`, `input/upstream-methods.md`, and `.git/annex/objects/`).
- The code and report state the one-sided whole-brain max-*t* method, common-support mask, anatomical ROI definition, limitations and a restrained interpretation (capture paths `analyze.py`, `REPORT.md`, and `results/`).
- In the one permitted separate-copy replay, all four explicitly selected numeric CSV outputs matched byte for byte after the run (record `2026-10-16-fresh-rerun.json`; this is assessor replay evidence, not worker-practice credit).

### Per-item checklist

The table is generated from the validated response record. Each listed path refers to the canonical capture SHA-256 stated above.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `analyze.py` | One captured workspace contains the full project tree; participant links stay inside its annex. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz` | All 54 maps and metadata are within the common root and reached through relative annex links. |
| must/003 | S.1 | unmet | judgement | `analyze.py`, `REPORT.md` | NumPy, SciPy, pandas, Matplotlib, NiBabel and Nilearn are imported but not specified or vendored within the project. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `.git/HEAD`, `REPORT.md`, `analyze.py`, `results/summary.json` | Git tracks supplied inputs, but the worker-stop code, report and results are untracked. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `.git/annex/objects/`, `input/data/sub-001_hypo1_cope.nii.gz` | Git-annex stores all 54 participant maps; annex payloads are present in the captured workspace. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `.entire/metadata/01a1459a-f79b-79b2-b5a2-6a25ac605e8a/full.jsonl`, `.entire/metadata/01a1459a-f79b-79b2-b5a2-6a25ac605e8a/prompt.txt`, `results/summary.json` | The session transcript records the command and package versions, but no exact environment spec is linked to shipped outputs. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `REPORT.md`, `analyze.py` | REPORT.md gives a run command, but no obtainable environment or installation instructions accompany it. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analyze.py`, `REPORT.md` | analyze.py is a clear start point and writes the reported result files. |
| must/009 | P.1 | met | probe:no-abs-paths | `analyze.py` | The analysis uses paths relative to its own root; no hardcoded host path appears in the script. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analyze.py`, `REPORT.md` | The entrypoint imports scientific packages without a delivered dependency declaration; it relies on a prepared host environment. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `.entire/metadata/01a1459a-f79b-79b2-b5a2-6a25ac605e8a/prompt.txt`, `REPORT.md` | The stated interpreter is a host-specific absolute path, with no project documentation of host assumptions. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `REPORT.md`, `analyze.py` | No project README or environment spec lists Python and package/system requirements for a researcher. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `analyze.py`, `REPORT.md` | No environment specification is versioned alongside the code and inputs. |
| must/014 | P.3 | unmet | judgement | `analyze.py`, `.git/logs/HEAD` | No dependency update/regeneration process is declared or tracked. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `REPORT.md`, `analyze.py` | No frozen environment file, image digest or equivalent project pin is supplied. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `.git/config`, `REPORT.md` | No worker-declared route publishes an environment spec or complete study; the repository has no remote. |
| must/017 | D.1 | unmet | judgement | `REPORT.md`, `analyze.py` | The report names a script but not how to obtain or reconstruct its required environment. |
| should/001 | T.2 | met | judgement | `.git/HEAD`, `input/data/sub-001_hypo1_cope.nii.gz` | The single project uses Git for text and git-annex for participant-map payloads. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `.entire/metadata/01a1459a-f79b-79b2-b5a2-6a25ac605e8a/full.jsonl`, `.git/` | The stop record shows analysis runs but no recurring workflow test or CI configuration. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/`, `results/`, `analyze.py` | Inputs and results have directories, but code is at root and no environment module exists. |
| should/004 | E.1 | unmet | judgement | `.entire/metadata/01a1459a-f79b-79b2-b5a2-6a25ac605e8a/prompt.txt`, `analyze.py` | Worker evidence shows execution in the supplied shared environment, not a fresh container, VM or batch job. |
| should/005 | E.1 | unmet | judgement | `analyze.py`, `REPORT.md` | The script does not create a disposable environment; it uses the session’s pre-existing interpreter. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `REPORT.md`, `.git/` | No exact environment specification exists to reconstitute and test regularly. |
| should/007 | D.2 | unmet | judgement | `.git/`, `analyze.py` | No environment image, executable bundle or lock snapshot is archived with the study. |
| should/008 | D.2 | unmet | judgement | `analyze.py` | No dependency update process exists to follow; this repeats must/014 by checklist design. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json`, `analyze.py` | N/A: the delivered inputs and declared scientific packages have no restricted access terms or software. |
| may/001 | M.2 | met | judgement | `input/sources.json`, `input/data/` | The upstream map dataset is identified by NeuroVault collection/API links and exact map URLs, with its copied boundary under input/data/. |
| may/002 | M.2 | partial | judgement | `REPORT.md`, `analyze.py` | REPORT.md links code, inputs and results, but does not document their component boundaries or recombination. |
| may/003 | M.2 | partial | judgement | `analyze.py`, `input/` | Input and result directories are separable, but code assumes their fixed layout and no environment boundary exists. |
| may/004 | M.2 | met | judgement | `analyze.py` | analyze.py composes the input maps and metadata into group results through a single reproducible entrypoint. |
| may/005 | M.2 | partial | judgement | `REPORT.md`, `input/upstream-methods.md` | Report and directory names help navigation, but no guide explains the full module layout or environment. |

### Additional probe finding

The full captured project inventory contains no reuse license declaration; the probe records this as an extra finding (`license-declared`, outside the 31 checklist items). This limits downstream reuse terms. Probe evidence is retained in [2026-10-16-probes.json](2026-10-16-probes.json).

### Flagged items

- **must/004** — the probe measured tree cleanliness; the item asks whether Git covers code, text, documentation and configuration. The full stop state shows Git was used, but the report, code and results were untracked, so partial is the better fit.
- **must/006** — the run-environment probe did not recognize the ignored `.entire` session record. That record shows commands and output, but does not identify an exact environment specification linked to the shipped results.
- **must/007–008** — the tracked-path entrypoint probe missed the untracked `analyze.py` and `REPORT.md`; the complete workspace supplies a script and a limited run instruction. The script exists, while environment installation instructions remain incomplete.
- **must/014** and **should/008** — duplicated checklist question; the same absent dependency-update process is reported in both by design.

### Not checked

No checklist item remains not-checked. Project retrieval was not tested because the worker state declares no complete-project route; the upstream map URLs in `input/sources.json` identify source data and do not publish the study outputs or environment. See [access.json](access.json) for recipient, route, artifact coverage and host scope.

### Goals, kind and scope

**Assumption, not confirmed with a human:** this is a study whose product is a group-level answer to the supplied NARPS question, supported by participant maps, code, results and a report. The stated task is in `input/study-task.md` and the fixed input methods are in `input/upstream-methods.md`. This kind emphasizes complete inputs, provenance, portability and interpretable results.

The worker stop receipt identifies the captured HEAD and complete workspace. At that stop, Git contained the supplied-input commit, while `REPORT.md`, `analyze.py` and `results/` were untracked. I did not credit later coordinator preservation, branch references, delivery or this assessment's replay as worker versioning/publication/environment practice. The captured session transcript records AI-assisted work; I noted this exposure but did not use assistant claims as grading evidence. Scientific conclusions were assessed from the delivered report, code, input metadata and generated artifacts.

The worker did not configure a Git remote or state a complete-study retrieval route. The authorized recipient is a researcher following the worker-declared route; no such route was available to test. Upstream map links are recorded in the supplied input metadata; one representative NeuroVault URL returned HTTP 200 to a HEAD request from this assessment host, covering one map only. This is not a worker-declared route or evidence that the complete study was shared. The exact command and response are retained in `logs/input-route-check-command.txt`, `logs/input-route-check.stdout` and `logs/input-route-check.stderr`. Captured `.git/config` points `core.hooksPath` to an external absolute path; I inspected the captured setting but did not follow that target. The replay helper disabled hooks only in its new copy.

The operational tree matched the initial operational manifest, whose SHA-256 equals the canonical manifest, except regular files `.git/annex/keysdb/db`, `db-shm`, and `db-wal`, which changed during inspection and are recorded as operational metadata. This comparison does not establish logical database equivalence. No other target changes were detected. The runner's separate replay used the canonical complete delivery; no input retrieval or repair occurred. The frozen-runner check passed; no assessor malfunction was observed.

Probe output: [2026-10-16-probes.json](2026-10-16-probes.json). Full per-item evidence and capture identity: [2026-10-16-response.json](2026-10-16-response.json). Replay plan and preserved command output: [replay-declaration.md](replay-declaration.md) and [logs/](logs/). Checklist app: [2026-10-16-url.txt](2026-10-16-url.txt).

Produced with `assess-alignment-with-stamped-principles` 0.1.0 and the pinned external assessment runner/runtime (`source_commit` 9852d8360f9519d21d11099b45f5deb8ba80cb28; environment commit 3552d5003a2485b6405805236d5c54e7ed42f097), checklist 0.3.1, on canonical capture `d75485e99456b2c86422f940111694530e096867cdbd581892caa49710571fe6` at original captured HEAD `129f3ae3717999e72ef6fbb9e9335f6d69c27470`. The runtime did not expose the exact model identifier. Probe output: `2026-10-16-probes.json`.
