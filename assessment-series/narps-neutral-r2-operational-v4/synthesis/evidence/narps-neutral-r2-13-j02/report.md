# Independent assessment — NARPS potential gain / vmPFC

## Verdicts

**MUST:** 4 met / 2 partial / 11 unmet / 0 not-checked. **SHOULD:** 0 met / 2 partial / 5 unmet / 1 not-checked / 1 not-applicable. **MAY:** 2 met / 2 partial / 0 unmet / 0 not-checked / 1 not-applicable. These are item attainments and measurement availability, not an overall score. Partial does not satisfy a MUST.

## What to address first

1. Track the worker's analysis, report, figures, and generated maps/results in version control, then publish an identified snapshot with a route researchers can use. These files were untracked at stop and no worker remote is configured; this closes the main gaps in must/004–005 and must/016.
2. Supply an installable, pinned environment and explain how to obtain it. The report lists package names but not versions or installation steps; this affects must/003, 007, 010–017 and replayability.
3. Record each run with its code/input/environment identity and outputs. Existing summaries describe settings but do not connect results to an execution record; this addresses must/006 and should/006.
4. Add repeatable testing evidence for the documented command, including a fresh-environment run when the environment is defined; this addresses should/002 and should/004.

## What is already strong

- The scientific report states the inferential scope and limits clearly, and distinguishes a lack of corrected vmPFC support from evidence that the effect is exactly zero (`content/workspace/REPORT.md`; capture SHA-256 `85aa5d916991b5b56e67d4c065b7c2fa4c18790910f761b154be501bf51fe77`).
- The delivered group code checks participant IDs, all 54 input checksums, finite values, image dimensions and affine, then uses whole-map sign flips with a one-sided whole-mask maximum statistic (`content/workspace/analyze.py`; same capture SHA-256).
- The complete captured root contains the input metadata and annex payloads, analysis script, report, figures, and result files. The report points to these files (`content/workspace/input/`, `analyze.py`, `REPORT.md`, `figures/`, `results/`; same capture SHA-256).

## Scientific judgment

**Scientific adequacy: supported.** The reported conclusion is: “The supplied data do **not support a positive vmPFC gain effect** at the required whole-brain corrected level.” (`content/workspace/REPORT.md`, capture SHA-256 `85aa5d916991b5b56e67d4c065b7c2fa4c18790910f761b154be501bf51fe77`). The outcome is supported by the stated confirmatory analysis: 54 participants, no exclusions, checks for ID/checksum/geometry/finite values, an intersection brain/common-coverage mask, and 10,000 participant-level sign flips with a one-sided whole-brain maximum-statistic correction. The report says the 23 surviving voxels were occipital, while its broad atlas-based vmPFC summary was near zero (mean 0.0019; 95% CI −0.0200 to 0.0238; descriptive *p*=.86) (`content/workspace/results/summary.json`, `corrected_clusters.csv`, `vmPFC_roi_summary.json`; same capture SHA-256).

This is a defensible absence-of-support conclusion, not a claim that the effect is exactly zero. The confidence interval includes small effects of either sign. The sign-flip procedure depends on symmetric, zero-centered participant errors and independent participants; the analysis makes that assumption explicit. Participant variance maps are absent, so the group inference reflects variation among participant effect estimates and cannot fully propagate first-level uncertainty. The gain coefficient is for the upstream standardized modulator, not response per unit of currency. Upstream preprocessing/modeling remains fixed and cannot be rechecked from these inputs. The atlas-defined ROI is transparent but not a unique vmPFC boundary. These limits qualify scope without overturning the reported conclusion.

**Hypothesis conclusion (verbatim):** The supplied data do **not support a positive vmPFC gain effect** at the required whole-brain corrected level.

## Delivery boundary and attribution

The canonical capture identity is SHA-256 `85aa5d916991b5b56e67d4c065b7c2fa4c18790910f761b154be501bf51fe77`; canonical capture-relative paths below use the `content/workspace/` prefix. Its captured HEAD is `bfe069501c140673f38778116f34bc8a5c36366f`. The canonical and operational manifests both identify a complete capture with no omissions or retained Git dependencies. The operational copy began with the same manifest identity.

I inspected the operational copy only. My final comparison found 1,096 expected and 1,096 current entries under the workspace root. The only difference was a regular-file change to `.git/annex/keysdb/db`, an allowed operational-metadata path. This inspection-induced database change is not worker evidence, and I make no claim of logical database equivalence. No other file, link, mode, or path changed. The integrity audit is retained as `capture-integrity.json`.

The stop receipt records a normally exited worker process and the complete stop capture (`worker-end-state.json`, SHA-256 `a5b81c7f265e90323f156ce5d1f98b3ac849e44f4b268959765f47ba0572eeb1`). The original Git HEAD contains the supplied scientific-input baseline. At stop, `REPORT.md`, `analyze.py`, `figures/`, and `results/` were untracked; the probe recorded these paths in `2026-10-16-probes.json`. The 54 annex-backed input maps were present in the supplied baseline. Their presence demonstrates that this delivery contains the data, but does not establish that the worker tracked them. Coordinator commits, retained annex storage, and delivery to this assessor receive no worker publication or versioning credit.

The captured `.entire/` ignored session metadata indicates assistant-tooling exposure. I did not use its contents as evidence for scientific quality or checklist attainment. No treatment assignment was inferred or used.

## Retrieval and replay

**Intended recipient:** a researcher seeking the complete study. **Worker-declared route:** none found; the captured Git configuration has no remote. `input/sources.json` identifies upstream input sources, but those URLs do not retrieve this report, code, figures, results, or environment. I tested only the local operational copy; no publication route could be tested. Coordinator delivery is not evidence of worker access. Details are in `access-record.json`.

**Replay: not checked; no replay attempt was made.** The documented command is `python analyze.py`, and the output selection is listed in `2026-10-16-replay-record.json`. The worker named package dependencies but supplied no installable specification or versions. The script also fetches atlas/template resources that are not captured. Reconstructing those prerequisites would require an unverified environment or uncaptured retrieval, so I did not make a replay copy or modify/remove any outputs. This is a scoped unavailable measurement, not a scientific failure. No assessor malfunction occurred.

## STAMPED item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | The complete captured workspace and its annex payloads are nested beneath one root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `content/workspace/analyze.py` | All 54 maps and metadata are included in the root; code resolves them with relative paths. |
| must/003 | S.1 | unmet | judgement | `content/workspace/analyze.py` | The analysis imports external Python packages, but no environment specification or linked software module is delivered. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `content/workspace/REPORT.md` | The worker's report, code, figures and results remained untracked at stop; the input commit does not track the worker analysis. |
| must/005 | T.1,T.3,T.5 | unmet | probe:large-in-annex+judgement | `content/workspace/results/mean_effect.nii.gz` | Annex tracks coordinator-supplied maps, but worker-generated NIfTI results are untracked and not in annex. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `content/workspace/results/summary.json` | Shipped summaries describe analysis settings but no run record links the generated results to an exact environment. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `content/workspace/REPORT.md` | REPORT.md gives the run command and package names, but omits installation steps and a reproducible environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/analyze.py` | The report names python analyze.py and analyze.py is a clear group-analysis starting point. |
| must/009 | P.1 | met | probe:no-abs-paths | `content/workspace/analyze.py` | The analysis script uses paths relative to its own location; the probe found no host-specific absolute paths in tracked text. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `content/workspace/REPORT.md` | No dependency specification declares or installs the imported packages; a prose list does not make the environment reconstructable. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `content/workspace/analyze.py` | The documented route leaves required host conditions unstated, including Python setup and atlas/template retrieval or cache availability. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `content/workspace/REPORT.md` | REPORT.md lists Python packages but gives no versions, install route, or system requirements. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `content/workspace/REPORT.md` | The captured root contains no version-controlled environment specification. |
| must/014 | P.3 | unmet | probe:env-spec-tracked | `content/workspace/REPORT.md` | No dependency-update process or tracked environment changes are present because no environment specification is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked | `content/workspace/REPORT.md` | No frozen environment specification is included to support exact reconstruction. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/.git/config` | No worker-declared route publishes the study outputs or an environment; Git has no remote configured. |
| must/017 | D.1 | unmet | judgement | `content/workspace/REPORT.md` | The report says to use a prepared environment but does not explain how to obtain or install it. |
| should/001 | T.2 | partial | judgement | `content/workspace/analyze.py` | The root Git repository and annex contain supplied inputs, but the worker's analysis code and results are untracked. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `content/workspace/.git` | No recurring CI or equivalent schedule/manual test record appears in the complete stop capture. |
| should/003 | M.1 | partial | probe:modules-separated | `content/workspace/input` | The input directory is separate, but code, results and environment are not defined as distinct modules. |
| should/004 | E.1 | not-checked | judgement | `content/workspace/REPORT.md` | The captured workspace has no fresh-environment run record; establishing whether a prior fresh run occurred needs worker execution evidence. |
| should/005 | E.1 | unmet | judgement | `content/workspace/REPORT.md` | The documented command runs in an existing Python environment and does not create a disposable environment per execution. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `content/workspace/results/summary.json` | No environment specification or reconstitution tests are recorded. |
| should/007 | D.2 | unmet | judgement | `content/workspace` | No environment image, package archive, or executable artifact is archived with the study. |
| should/008 | D.2 | unmet | judgement | `content/workspace/REPORT.md` | No process for updating environment specifications is documented or tracked; this duplicates must/014 by checklist design. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: the delivered dataset and software are public; no restricted component is present. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json` | N/A: there are no independently maintained project modules; inputs are bundled in the single research object. |
| may/002 | M.2 | partial | judgement | `content/workspace/REPORT.md` | Report and directory layout identify inputs, analysis code and outputs, but do not define a fuller module relationship or recombination contract. |
| may/003 | M.2 | partial | judgement | `content/workspace` | Input, code and result directories are visibly separated, but they remain coupled within one tree and outputs are not independently versioned. |
| may/004 | M.2 | met | judgement | `content/workspace/analyze.py` | The documented python analyze.py entrypoint composes the captured input directory, analysis code and output directories. |
| may/005 | M.2 | met | judgement | `content/workspace/REPORT.md` | REPORT.md lists the main code, input-methods file, results and figures, giving readers a navigation guide. |

## Flagged items

- `must/002` (`probe-overridden`): the probe saw no subdataset; the scientific inputs are included under the root through relative annex links.
- `must/005` (`probe-overridden`): annex correctly describes the supplied maps, but misses the worker's untracked binary results.
- `must/006` (`probe-overridden`): the probe found no recognizable run record; inspection of the complete output set confirms no environment-linked provenance record.
- `must/007` (`probe-overridden`): filename heuristic missed the report's run instruction; installation remains undocumented, so the item is partial.
- `must/008` (`probe-overridden`): the documented `python analyze.py` entrypoint is clear despite the probe's README/Makefile heuristic.
- `must/011` and `must/012` (`probe-overridden`): the command scan cannot judge network/cache and environment requirements or the prose dependency list; the report documents only package names.
- `should/002` (`probe-overridden`): no CI was found, and the full capture also contains no equivalent recurring test record.
- `should/006` (`probe-overridden`): no exact environment or reconstitution test is recorded.
- `may/001` (`probe-overridden`): no independently maintained project module exists; source URLs describe provenance, not project components.
- `must/014` and `should/008` (`upstream-duplicate`): the pinned checklist asks the same environment-update question twice.

## Not checked

- `should/004`: no stop-state evidence establishes whether the worker previously tested in a fresh environment. A worker run record or a valid fresh replay would settle it.
- Replay: prerequisites described above could not be reconstructed from supplied instructions without adding dependencies or retrieving uncaptured atlas/template resources.
- Worker publication: no worker-declared route was present, so independent retrieval of the whole study could not be tested.

## Goals, kind, and scope

The documented goal is group-level testing of the positive potential-gain effect in vmPFC for the equal-indifference group using the 54 supplied participant effect maps, with whole-brain correction (`content/workspace/input/study-task.md` and `upstream-methods.md`; capture SHA-256 above). I assume the primary kind is **study** because the product is an answer to a scientific question. No human guidance was attached to confirm this assumption. Emphasis is therefore on complete inputs, traceable results, and actionable reproduction.

The frozen probes were run against the operational copy; the individual readings above include the full stopped workspace, including untracked and ignored files. Per-item evidence appears in the response JSON and cites the canonical capture digest and capture-relative path. Probe coverage is limited to the properties and formats named in `2026-10-16-probes.json`.

## Checklist, record, and provenance

[Open the filled STAMPED checklist](2026-10-16-url.txt). The per-item record is [2026-10-16-response.json](2026-10-16-response.json); probes are [2026-10-16-probes.json](2026-10-16-probes.json). The separate scientific record is `scientific-judgment.json`.

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on canonical capture SHA-256 `85aa5d916991b5b56e67d4c065b7c2fa4c18790910f761b154be501bf51fe77`, original HEAD `bfe069501c140673f38778116f34bc8a5c36366f`, 2026-10-16, Codex/GPT-6. Frozen runner preflight succeeded; probe output: `2026-10-16-probes.json`.
