# Independent assessment — NARPS equal-indifference gain effect

Assessment date: 2026-10-16. Original complete delivery capture SHA-256: `62fae7a1b4cf57bb811b88cb718ed01596b5d9b784e996e678b4851cadefbd0d`; captured HEAD: `afb62884c70115b6e46a92ddcd1d17bbf4f33544`. Unless identified as an external receipt or assessor output, every `content/workspace/...` path below is relative to this canonical capture digest.

**Scientific adequacy: qualified — the reported negative support finding is credible for the supplied maps and declared common-support analysis, but depends on zero-as-no-coverage masking, sign-flip symmetry, and a coordinate-box approximation of vmPFC.**

**Hypothesis outcome (verbatim):** “The supplied maps do not support a positive vmPFC gain effect in the NARPS equal-indifference group.”

## Scientific assessment

The analysis addresses the supplied group-stage question. It identifies exactly 54 equal-indifference participants, checks IDs against metadata, checks image shape and affine, excludes nobody, and analyzes each participant as the sampling unit. Maps are unthresholded participant contrast estimates from the fixed upstream gain model, not t/z statistics or dollar slopes (`content/workspace/input/upstream-methods.md`, `content/workspace/input/participants.tsv`, `content/workspace/scripts/group_analysis.py`, `content/workspace/results/summary.json`).

The task requires whole-brain-corrected hypothesis decisions, consistent with the [original NARPS analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf). The one-sample positive-mean test uses 9,999 participant-level sign flips and a whole-brain maximum-t correction over 198,029 common-support voxels. It reports 24 FWE-significant positive voxels in small posterior clusters, with peak MNI coordinate (−26, −102, −3.6), and none inside its declared vmPFC display box. The vmPFC box mean is −0.0035 (95% CI −0.0229 to 0.0160). The code cross-checks voxelwise t values against SciPy and compares a sign-flip calculation against an independent implementation (`content/workspace/scripts/group_analysis.py`, `content/workspace/results/summary.json`, `content/workspace/results/fwe_clusters.csv`, `content/workspace/figures/group_results.svg`).

I rate adequacy **qualified**. The result supports the bounded statement that this analysis did not find a positive whole-brain-corrected effect in the declared vmPFC box; it does not establish zero or absence. The unweighted group model cannot propagate missing participant-level variance maps. Permutation inference assumes symmetry under the null. The analysis defines image support as nonzero in every map without a separately supplied mask to verify that zero always means uncovered, and defines vmPFC using an explicit coordinate box rather than a validated anatomical ROI. These assumptions are disclosed, and the box is not used to constrain the whole-brain correction. The report also correctly explains that the upstream gain coefficient is not a per-currency-unit sensitivity and that the twice-wide gain range does not rescale it (`content/workspace/REPORT.md`, `content/workspace/protocol.md`, `content/workspace/input/upstream-methods.md`).

The protocol records a change from Bonferroni to max-t sign-flip FWE as the primary analysis before accepting the final run, retaining Bonferroni as a reference. Both are whole-brain corrections; the change is disclosed, though it leaves some analytic flexibility. The first failed execution is retained, and its recorded correction was a postprocessing indexing error; the final script reran the analysis without changing participants, mask, or statistical method (`content/workspace/protocol.md`, `content/workspace/results/attempts/README.md`, `content/workspace/results/attempts/first-run.stderr`).

## STAMPED verdicts

- MUST: **3 met / 7 partial / 7 unmet / 0 not-checked** (17 items).
- SHOULD: **0 met / 2 partial / 6 unmet / 0 not-checked / 1 not-applicable** (9 items).
- MAY: **3 met / 1 partial / 0 unmet / 0 not-checked / 1 not-applicable** (5 items).

No overall score is assigned.

## What to fix first

1. Add a portable, pinned environment declaration and install instructions; replace the external absolute interpreter default. This would address the largest reproduction gap across must/003, 006, 007, 009–017 and should/005–007.
2. Track the worker-created report, scripts, results and retrieved map copies at the worker stop, or record them in a versioned delivery mechanism. This would make must/004–005 and should/001 reflect the complete work.
3. Publish a stable authorized route for the complete study package, including code, report, results and environment. NeuroVault currently covers only source maps; this would address must/016.
4. Add a recurring check and a fresh-environment run using the pinned environment. This would address should/002, 004 and 006.
5. Document and track how environment specifications are updated; this duplicated checklist item applies to must/014 and should/008.

## What is already strong

- The report distinguishes the hypothesis outcome from evidence of absence, states the interval, describes uncertainty, and interprets the supplied gain estimates at their actual scale (`content/workspace/REPORT.md`, `content/workspace/input/upstream-methods.md`).
- The group script checks all 54 IDs, common geometry and finite values; it applies whole-brain max-t FWE and records independent numerical checks (`content/workspace/scripts/group_analysis.py`, `content/workspace/results/summary.json`).
- The failed first attempt and corrected script are retained. The two delivered map copies were byte-identical for all 54 participants; the source route test and map-copy comparison are recorded in this assessment directory (`content/workspace/results/attempts/README.md`, `content/workspace/input/sources.json`, `map-copy-check.txt`, `access-route-head.txt`).

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace/REPORT.md`, `content/workspace/input/sources.json` | The complete study workspace is rooted at one directory. |
| must/002 | S.1 | met | judgement | `content/workspace/input/sources.json`, `content/workspace/input/participants.tsv` | All required maps and metadata are present inside the workspace. |
| must/003 | S.1 | unmet | judgement | `content/workspace/scripts/group_analysis.py`, `content/workspace/run_analysis.sh` | The Python dependencies and execution environment are not specified within the project. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `content/workspace/.git/index`, `content/workspace/REPORT.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-05-j01/attempt-01/worker-end-state.json` | Git exists, but the worker report, code, results and downloaded map copies were untracked at stop. |
| must/005 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:large-in-annex+judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `content/workspace/data/sub-001_hypo1_cope.nii.gz`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-05-j01/attempt-01/worker-end-state.json` | Annex holds supplied maps, but worker-created map copies and derived images are untracked. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `content/workspace/results/summary.json`, `content/workspace/results/code-input-sha256.txt`, `content/workspace/results/run.stdout` | Results record versions and input/code hashes, but no exact installable environment specification. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `content/workspace/REPORT.md`, `content/workspace/run_analysis.sh` | REPORT.md gives a run command, but installation instructions and a reproducible environment are missing. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/REPORT.md`, `content/workspace/run_analysis.sh` | REPORT.md names a clear entrypoint that runs retrieval and group analysis. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `content/workspace/run_analysis.sh` | The default interpreter is an absolute host path, although PYTHON can override it. |
| must/010 | P.1 | unmet | judgement | `content/workspace/scripts/group_analysis.py`, `content/workspace/run_analysis.sh` | Required Python packages are imported but no dependency declaration is delivered. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `content/workspace/run_analysis.sh`, `content/workspace/results/summary.json` | The run records the actual OS and architecture, but omits required host assumptions and setup details. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `content/workspace/REPORT.md`, `content/workspace/scripts/group_analysis.py` | No system requirements or dependency list is provided for a reader. |
| must/013 | P.3 | unmet | judgement | `content/workspace/.git/index`, `content/workspace/run_analysis.sh` | No environment specification is included in the worker version-controlled state. |
| must/014 | P.3 | unmet | judgement | `content/workspace/protocol.md` | No dependency update or lock regeneration process is documented. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `content/workspace/results/summary.json` | The run records Python and direct package versions, but not an exact reconstructible environment. |
| must/016 | D.1 | unmet | judgement | `content/workspace/.git/config`, `content/workspace/input/sources.json` | No environment specification exists to share, and no worker route exposes the complete study. |
| must/017 | D.1 | unmet | judgement | `content/workspace/REPORT.md`, `content/workspace/run_analysis.sh` | Readers are not told how to obtain and install the environment used by the entrypoint. |
| should/001 | T.2 | partial | judgement | `content/workspace/.git/index`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r1-operational-v4/judgments/narps-neutral-r1-05-j01/attempt-01/worker-end-state.json` | One Git repository covers the workspace, but worker analysis components were not tracked at stop. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `content/workspace/results/run.stdout`, `content/workspace/results/attempts/README.md` | Two local attempts are recorded; no recurring test mechanism appears. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/REPORT.md`, `content/workspace/input/sources.json`, `content/workspace/scripts/group_analysis.py` | Inputs, code and results are separated, but there is no environment module. |
| should/004 | E.1 | unmet | judgement | `content/workspace/results/summary.json`, `content/workspace/run_analysis.sh` | The worker log records a same-host run, not a fresh container, VM, batch job or cloud instance. |
| should/005 | E.1 | unmet | judgement | `content/workspace/run_analysis.sh` | The entrypoint reuses a persistent interpreter path and does not create a disposable environment. |
| should/006 | D.2 | unmet | judgement | `content/workspace/results/summary.json`, `content/workspace/run_analysis.sh` | There is no pinned environment specification or recurring reconstitution test. |
| should/007 | D.2 | unmet | judgement | `content/workspace/run_analysis.sh` | The environment binaries and package artifacts are not archived in the workspace. |
| should/008 | D.2 | unmet | judgement | `content/workspace/protocol.md` | No environment update process is documented or tracked; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | N/A: supplied inputs and required software are public; no restricted component exists. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `content/workspace/input/sources.json`, `content/workspace/.git/config` | N/A: no independently maintained project component is linked; the supplied maps are included. |
| may/002 | M.2 | met | judgement | `content/workspace/REPORT.md`, `content/workspace/protocol.md` | REPORT.md and protocol.md explain the input, analysis and results components. |
| may/003 | M.2 | partial | judgement | `content/workspace/scripts/group_analysis.py`, `content/workspace/results/summary.json`, `content/workspace/protocol.md` | Inputs, scripts and results can be updated separately, though interfaces and environment are not pinned. |
| may/004 | M.2 | met | judgement | `content/workspace/run_analysis.sh` | run_analysis.sh composes the retrieval and group-analysis scripts in order. |
| may/005 | M.2 | met | judgement | `content/workspace/REPORT.md` | REPORT.md provides artifact links and a starting point for navigating the study. |

## Flagged items

- **must/004, must/005:** the probes credited Git and annex state found in the supplied capture, but worker-generated code, report, results and retrieved map copies remained untracked at stop; coordinator-supplied annex pointers do not establish worker practice.
- **must/006, must/015:** probes could not recognize a run-to-environment link; inspection found platform and package-version metadata, but no exact installable specification.
- **must/007, must/008:** the filename probe missed the untracked `REPORT.md` and `run_analysis.sh`; the documented command establishes a usable starting point, while setup instructions remain incomplete.
- **must/009:** the text probe scanned tracked files only; the untracked runner sets an absolute default interpreter path, with `PYTHON` as an override.
- **must/011, must/012:** command scanning could not decide host requirements; the documented route assumes an external path but gives no reader-facing system requirements.
- **should/002:** absence of recognized CI was not treated as absence of all execution; the two retained local attempts do not establish recurring testing.
- **should/003:** the path probe missed the separate `scripts/` and `results/` components; the remaining gap is the lack of an environment component.
- **must/014, should/008:** the pinned checklist repeats the environment-update question; both answers repeat by design.
- **may/001:** the probe could not decide applicability; maps are supplied inside the root and there is no independently maintained project component linked as a module.

## Extra findings outside the checklist

The full operational workspace search found no LICENSE/COPYING/REUSE declaration and no `dataset_description.json` (`license-inventory.txt`, `dataset-description-inventory.txt`); this is an extra reuse-terms gap, not a checklist item. The scripted `clone-weight` result only describes Git text blobs, and `inputs-untouched` was not applicable because no linked modules exist; neither changes checklist verdicts. These observations are bounded to the complete captured workspace and its unchanged non-metadata bytes.

## Not checked

No checklist item was left not-checked. **Replay was not checked:** the documented command is `bash run_analysis.sh`, but its default interpreter is an absolute path outside the captured project and no environment specification or declared install procedure is included. I did not substitute the assessor environment or repair the delivery. The exact selected outputs and comparison rule are recorded in `2026-10-16-replay-record.json`; no replay command ran and no output was removed. Command and validation receipts are indexed in `commands/assessment-command-log.md`.

## Delivery boundary, attribution and access

The canonical and operational manifests each identify 1,283 entries with no omissions; the stop receipt records a complete capture and the worker exited successfully at the stated HEAD. The assessment inspected the operational copy and used the canonical manifest digest for citations. The preserved Git commit contains supplied input material; the worker-stop inventory and operational Git status show that the analysis report, code, results and `data/` copies were untracked. The source maps in `input/data/` are annex-backed supplied inputs; the worker’s `data/` copies match them byte for byte. The stop receipt identifies the initial catalog under `content/external/0000` as coordinator-supplied guidance and later installed skill links as worker discoveries; those external links were not followed. Coordinator capture and annex preservation are not credited as worker actions (`worker-end-state.json`, SHA-256 `2cbea3294b9b3c2e5985990c6c541f58aef039df1fd9e507cb685af2f2ccadb1`; canonical manifest SHA-256 above).

**Access assessment:** the intended recipient is a researcher following the worker-declared authorized route. `input/sources.json` and `scripts/retrieve_maps.py` declare NeuroVault source-map URLs. A HEAD request for one map returned HTTP 200 and the expected byte length from this assessment host; that checks only the NeuroVault host and one source file, not all artifacts or another host. The source route covers participant maps, not the worker’s report, code, results, or environment. No worker-declared route for retrieving the complete study was found in the captured Git configuration or report. Coordinator delivery to this assessor is not evidence of worker publication. Full details are in `access-record.json`.

**Assistance exposure:** captured HEAD commit metadata (`afb62884c70115b6e46a92ddcd1d17bbf4f33544`; `content/workspace/.git/COMMIT_EDITMSG`) contains a Codex co-author attribution. This is recorded as exposure only and was not used as grading evidence. Retained external absolute links are preserved as captured; I did not follow them or run Git through an external pointer. The local Git configuration names an external hooks path, which was not followed. The operational manifest comparison (`operational-integrity-check.stdout`) found no scientific-file, code, configuration, index, ref, object, mode or link mismatch. It found only a changed regular `.git/annex/keysdb/db` (captured SHA-256 `f6f8fd7af99434db59fadc6da021051789c6aaa271ebf878c54dafc6c9fde5ca`; operational SHA-256 `233c0be3e02857e0fbf47b00b8a94de3e9126529bee41b2491286aef7372be80`) and new regular `db-shm`/`db-wal` files, classified as operational metadata under the supplied rule. These inspection-induced changes are not worker evidence; this check does not establish logical database equivalence. Annex database conclusions are therefore limited to captured pointers and file bytes, not logical database state.

**Goals and kind (assumption; not confirmed):** based on `REPORT.md`, `protocol.md` and the task brief, this is a **study** whose goal is group-stage inference on the supplied NARPS participant gain-effect maps and a concise report with reproducible code and results. No human guidance was attached, so this interpretation is labelled as an assumption.

Checklist link: [open the completed 0.3.1 checklist](2026-10-16-url.txt). Machine-readable answers: [response JSON](2026-10-16-response.json); unedited probe output: [probes JSON](2026-10-16-probes.json).

## Provenance stamp

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259bad`), on the complete original delivery at captured HEAD `afb62884c70115b6e46a92ddcd1d17bbf4f33544`, 2026-10-16, OpenAI Codex / GPT-6 (exact build unavailable in session metadata). Frozen runner check passed: assessor source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`, lock SHA-256 `f8fff1394fbeaa2ab1c4993fceb0dd6463fe0c08c81fcda397f3e752a72c4249`. Probe output: `2026-10-16-probes.json`. Canonical capture manifest: `62fae7a1b4cf57bb811b88cb718ed01596b5d9b784e996e678b4851cadefbd0d`.
