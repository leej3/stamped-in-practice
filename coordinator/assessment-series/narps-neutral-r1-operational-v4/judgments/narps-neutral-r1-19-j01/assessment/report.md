# Independent assessment — NARPS equal-indifference gain maps

## Verdict line

MUST: 3 met / 1 partial / 13 unmet / 0 not-checked (17 items; partial does not satisfy a MUST). SHOULD: 0 met / 2 partial / 5 unmet / 1 not-checked / 1 not-applicable (9 items). MAY: 1 met / 0 partial / 2 unmet / 0 not-checked / 2 not-applicable (5 items). No overall score is assigned.

## What to fix first

1. Add a pinned environment specification and setup instructions, replace the host-specific interpreter path, and document the required host assumptions. This would let another researcher reproduce the analysis outside the worker machine (must/003, must/007, must/009–017; should/006–007).
2. Track the analysis, report, environment, and scientific outputs at worker stop, with a run record linking inputs, code, outputs, and environment. This would preserve the complete scientific state rather than relying on a supplied-input commit and an untracked working tree (must/004–006; should/001).
3. State the supported retrieval route and coverage for the report, code, results, atlas files, and environment, in addition to the input-source routes. This would make the complete study retrievable to its intended research recipient (must/016–017).
4. Add an automated or recurring validation path for the documented analysis and its environment. This would make instruction drift and environment failures discoverable (should/002, should/004–006).
5. Describe the input, code, result, and environment boundaries and their relationships so components can be updated or recombined independently (should/003; may/002–003).

## What the project already does well

- The script validates all 54 source checksums, requires unique participants in the equal-indifference cohort, checks map geometry and finite values, and excludes nobody by default (`analyze.py`; canonical capture SHA-256 `3d05d8750a1d869cef98d6b221d945d97e8297b0c81f3f4ebc4ed10643e04ec1`, capture-relative `content/workspace/analyze.py`).
- The primary test is a positive one-sample group test with participant-level sign flips and whole-brain max-T FWER correction. The vmPFC proxy is anatomically defined independently of the observed effects, and its ROI summary is clearly labelled secondary (`analyze.py`, `report.md`; same capture and paths `content/workspace/analyze.py`, `content/workspace/report.md`).
- The report presents participant variation, uncertainty, corrected whole-brain findings, model-unit interpretation, upstream-model limits, and a cautious explanation of a null vmPFC result (`report.md`; same capture, `content/workspace/report.md`).

## Scientific assessment

**Scientific adequacy: qualified.** The analysis is a defensible group-stage test conditional on the supplied AO86 participant COPEs. It includes the complete 54-person equal-indifference group, checks checksum and geometry consistency, uses an independent participant-level one-sample test, and controls positive whole-brain voxelwise FWER with a max-T sign-flip distribution. The Harvard–Oxford Frontal Medial plus Subcallosal proxy is defined independently of observed effects, and the report does not treat an uncorrected ROI statistic as the hypothesis decision. The selected result summary, participant QC table, and cluster table were reproduced byte-for-byte in the one frozen captured-delivery replay (`fresh-rerun.json`; replay stdout/stderr are retained under `replay/work/`).

The conclusion remains qualified by the sign-flip test's symmetry/exchangeability assumption, equal weighting because participant variance maps were not supplied, the use of nonzero values as a coverage proxy, and the practical atlas/brain-mask resampling from MNI152 to MNI152NLin2009cAsym. The supplied COPE scale is based on a normalized gain modulator, so it is not a BOLD change per currency unit. Potential gains spanned twice the potential-loss range, so these results cannot be read as a gain-versus-loss sensitivity comparison. The separate gain/loss models and fixed upstream model also limit interpretation. These are disclosed and do not invalidate the stated conditional group inference. The captured replay used the exact interpreter path documented by the worker, which happened to exist on this assessment host; the worker did not include a dependency declaration, so replay success does not establish environment portability.

### Reported hypothesis outcome (kept separate from adequacy)

> The supplied data do **not support a positive gain effect in vmPFC** under the prespecified whole-brain family-wise error (FWE) criterion.

In the supplied summary, the vmPFC proxy mean is 0.0027 model units (95% t interval −0.0217 to 0.0270), the ROI sign-flip p-value is 0.403, and no whole-brain FWER-significant voxels overlap the proxy. There are 23 positive whole-brain FWER voxels in three small posterior occipital clusters. Lack of vmPFC support means this analysis did not detect a sufficiently consistent positive effect at the stated threshold; it is not evidence that the true effect is exactly zero (`results/results.json`, `results/fwer_positive_clusters.tsv`, `report.md`; canonical capture and paths `content/workspace/results/results.json`, `content/workspace/results/fwer_positive_clusters.tsv`, `content/workspace/report.md`).

The absence of whole-brain-corrected vmPFC support is reported separately from adequacy: a defensible absence of positive findings is a valid reported conclusion. It does not confirm the positive hypothesis. The report's scientific conclusion is conditional on fixed inputs and does not audit the unsupplied upstream time-series analysis.

## Capture, attribution, and integrity

Canonical original capture identity: SHA-256 `3d05d8750a1d869cef98d6b221d945d97e8297b0c81f3f4ebc4ed10643e04ec1`; captured at `2026-10-16T07:23:20.394907+00:00`; original captured HEAD `675620fed8a134102b1b07226fe39d67630ee6f7`. The canonical and operational manifests have identical bytes and digest, with no declared omissions or capture errors. `judge-target.json` lists no reference limits. The final target integrity check found no missing/extra paths and no non-metadata changes. One regular file, `.git/annex/keysdb/db`, changed during inspection and is classified as operational metadata; logical database equivalence is not established, and this inspection-induced change is not worker evidence (`operational-integrity.json`).

The stop receipt records the same original HEAD and a complete capture (worker-end-state.json SHA-256 `b1af21635199a76129667fb740712c8840b192c2d2f25e921b15e21df55e8614`). At stop, `analyze.py`, `report.md`, `references/`, `results/`, and `.task-skills/` were untracked. The captured HEAD commit message describes supplying materialized scientific inputs; it is not treated as worker authorship or credit for the untracked analysis. Worker versioning, publication, environment capture, and sharing are judged from that stop state. No worker publication record for the report, code, generated products, atlas cache, or environment was found. The coordinator's later preservation and this assessment's replay do not establish worker practice.

Exposure note: captured `.git/COMMIT_EDITMSG` contains a Codex Desktop / GPT-6 co-author identifier. This is recorded as possible assistance exposure only and was not used as grading evidence. No treatment assignment is inferred or reported.

## Replay and access

Before replay, the selected generated outputs were declared as `results/results.json`, `results/participant_qc.tsv`, and `results/fwer_positive_clusters.tsv`. The helper copied the complete canonical stopped delivery, removed only those three generated outputs in the replay copy, and ran the exact documented command:

```text
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analyze.py
```

The command returned 0 in 9.6 seconds. All three selected files were byte-identical. The comparison was exact for the JSON result summary and the frozen helper's numeric table comparison at relative tolerance 1e-6 for TSVs; no timestamps or prose were treated as scientific quantities. Full NIfTI maps and figures were not selected and are not claimed as replay evidence. Replay used only captured scientific inputs; the adapter performed no input prefetch. The interpreter itself was available outside the object and is not declared or captured by the worker.

The worker-declared source routes in `input/sources.json` cover the 54 NeuroVault maps plus pinned cohort metadata and methods references. HTTP HEAD returned 200 for one representative NeuroVault map URL and both pinned raw GitHub source URLs; the other 53 map URLs were not individually tested. These routes do not cover the worker's analysis code, report, derived outputs, atlas cache, or environment. The full delivery of files to the assessor is not evidence that the worker made those artifacts retrievable. The intended recipient, route coverage, and tested host scope are recorded in [`access-record.json`](access-record.json).

## STAMPED item responses

The assessment treats the object as a **study**: the product is a group-level answer to the supplied scientific question, with code and results. That kind follows from `input/study-task.md` and `report.md`. Per-item citations below refer to the canonical capture SHA-256 above and capture-relative paths; the response JSON carries the full evidence descriptions and file digests.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/participants.tsv`, `input/data/sub-001_hypo1_cope.nii.gz` | All delivered workspace material is under one root; map links resolve within its captured annex store. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz`, `analyze.py` | All 54 maps and metadata are supplied under input/; relative links and the retained annex objects stay inside the root. |
| must/003 | S.1 | unmet | judgement | `analyze.py`, `report.md` | Python/Nilearn and scientific dependencies are imported by the delivered script but no environment declaration includes them. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `analyze.py`, `report.md`, `results/results.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/probes.json` | At worker stop, the analysis, report, atlas cache and results were untracked; the only captured HEAD contains supplied inputs. |
| must/005 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:large-in-annex+probe:tree-clean+judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `results/group_mean_cope.nii.gz`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-19-j01/attempt-01/worker-end-state.json` | The supplied input maps use annex pointers, but worker-produced NIfTI derivatives are untracked and not in version control. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `results/run.log`, `report.md` | The shipped run.log is only the result JSON; neither it nor the report links the execution to an exact environment specification. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `report.md`, `analyze.py` | report.md gives a run command, but the delivered route has no installation instructions or dependency setup a researcher can follow. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `analyze.py` | The report names analyze.py and gives its invocation as the reproduction starting point. |
| must/009 | P.1 | unmet | probe:no-abs-paths+judgement | `report.md`, `.git/config` | The documented run command hardcodes a host-specific absolute Python path; captured Git config also names an external hooks path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `analyze.py`, `report.md` | There is no delivered environment specification for the imported Python libraries or system requirements. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `report.md`, `.git/config` | The run depends on a host-specific absolute interpreter path and Git hooks path, neither documented as a host assumption. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `report.md`, `analyze.py` | No README or environment file lists Python/package versions, system requirements or setup dependencies. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `analyze.py`, `input/participants.tsv`, `report.md` | No environment specification is present alongside the worker code and data. |
| must/014 | P.3 | unmet | probe:env-spec-tracked+judgement | `report.md`, `analyze.py` | No environment specification or dependency-update process is declared or tracked. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `report.md`, `analyze.py` | No pinned manifest or image identity lets another researcher recreate the worker environment. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `report.md`, `analyze.py` | No environment artifacts or frozen dependency specification are shared in the delivery. |
| must/017 | D.1 | unmet | judgement | `report.md` | The report tells readers to use a machine-specific interpreter but does not explain how to obtain or recreate it. |
| should/001 | T.2 | partial | probe:tree-clean+judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `analyze.py`, `results/results.json` | Git contains the supplied input pointers, while all worker-produced code, documentation and results are untracked. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `analyze.py`, `results/run.log`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/probes.json` | The complete delivery contains one result record and no test suite, CI setup or recurring workflow check. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/participants.tsv`, `analyze.py`, `results/results.json`, `report.md` | Inputs and results have separate directories, but code sits at root and no environment module exists. |
| should/004 | E.1 | not-checked | judgement | `report.md`, `results/run.log` | Worker records do not establish a fresh-container, batch, clean-VM or cloud test; the assessment replay is not worker practice. |
| should/005 | E.1 | unmet | judgement | `report.md`, `analyze.py` | The documented command invokes a fixed host interpreter directly and does not create a disposable environment per run. |
| should/006 | D.2 | unmet | probe:ci-present+probe:env-spec-tracked+judgement | `report.md`, `analyze.py` | No exact environment specification exists to reconstitute or test regularly. |
| should/007 | D.2 | unmet | judgement | `report.md`, `analyze.py` | No environment image, executable bundle or archived package environment is included. |
| should/008 | D.2 | unmet | probe:env-spec-tracked+judgement | `report.md`, `analyze.py` | No dependency-update process is documented or tracked; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json`, `references/nilearn/README.md` | N/A: no restricted data or software component is identified; the input sources and included atlas are public. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `input/sources.json`, `analyze.py` | N/A: no independently maintained project components are included as external modules; source datasets are copied into input/. |
| may/002 | M.2 | unmet | judgement | `report.md` | The report lists artifacts but does not explain component relationships or how modules can be recombined. |
| may/003 | M.2 | unmet | judgement | `report.md`, `analyze.py` | No module boundaries or independent update contracts are documented. |
| may/004 | M.2 | not-applicable | judgement | `report.md`, `analyze.py` | N/A: the delivery has no independently composed modules requiring a module-composition mechanism. |
| may/005 | M.2 | met | judgement | `report.md` | report.md links the entrypoint, result summary, QC table, clusters and figures for navigation. |

## Flagged items

- **must/002:** the probe treated absence of submodules as uncertainty; the complete delivery shows all 54 source maps are supplied as relative in-root annex links.
- **must/005:** the probe saw supplied annex pointers; the complete worker stop also contains untracked worker-produced binary maps, so the result is partial.
- **must/006:** the probe recognized no run record; the captured `run.log` is only the output JSON and does not link an environment, so manual inspection establishes unmet.
- **must/007:** the probe checked for README/Makefile naming; `report.md` and `analyze.py` are an equivalent usage route, but installation/setup instructions remain absent.
- **must/008:** the probe missed the untracked script; the documented invocation establishes a clear starting point.
- **must/009, must/011, must/012:** the probe scanned tracked text only; the untracked report and captured Git configuration contain host-specific paths and leave host/dependency requirements undocumented.
- **must/015:** manual inspection of the complete delivery establishes that no environment pin exists.
- **should/002:** no recognized CI setup alone is inconclusive, but the complete delivery has no recurring test record or test suite.
- **may/001:** the probe could not classify external inputs; there are no independently maintained project modules, so this item is not applicable.
- **must/014 and should/008:** these checklist statements are duplicates; the same unmet answer is intentionally repeated.

## Not checked

- **should/004:** worker-stop records do not establish testing in a fresh container, batch job, clean VM, or cloud instance. A worker run record or documented infrastructure record would settle this. The successful assessor replay is not worker-practice credit.

## Checklist link and provenance

Checklist-app URL: [`2026-10-16-url.txt`](2026-10-16-url.txt). Machine-readable item answers: [`response.json`](response.json). Scripted probe results: [`probes.json`](probes.json). The frozen checklist pin check passed for checklist 0.3.1 (31 items).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259bad`), on captured HEAD `675620fed8a134102b1b07226fe39d67630ee6f7`, 2026-10-16, Codex/GPT-6 with the frozen external assessment runtime. Probe output: `probes.json`; replay record: `fresh-rerun.json`.
