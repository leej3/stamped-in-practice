# Independent assessment: NARPS potential gains and brain activity

**Capture:** `73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b`; original captured HEAD `ad3956ae64dcbdd1eec6af4ed21e0b168e478106`. The canonical delivery and operational manifest identities match, and the launcher uses exact before/after verification. `judge-target.json` has no reference-limit exceptions. Evidence citations below use the canonical capture digest and capture-relative paths (`content/workspace/...`). The complete stop receipt reports no omissions or capture errors. Its worker state and original commit are distinguished from later coordinator retention.

**Assumption (no human guidance attached):** The goal is to assess a study answering the supplied NARPS group-analysis question, with a scientific report and reproducible analysis as products. The object kind is **study**. The report and code are present, but these scientific artifacts were untracked in the captured worker stop state; the recorded HEAD only contains the supplied/materialized input baseline.

## Verdicts

**MUST:** 5 met / 4 partial / 8 unmet / 0 not-checked. **SHOULD:** 1 met / 1 partial / 5 unmet / 1 not-checked / 1 not-applicable. **MAY:** 4 met / 1 partial.

## What to address first

1. Add a pinned, installable environment declaration and setup instructions; this enables dependency completeness, portable execution and reconstruction (must/003, must/010–017; should/006–008).
2. Record the analysis code, report, notebook and outputs in version control at the worker stop; this makes the scientific delivery identifiable as a revision (must/004).
3. Publish the complete analysis artifact set through an authorized, durable route, with the report, code, figures, results and inputs covered (must/016).
4. Link execution records to code, input checksums and the exact environment, then test that environment on a fresh host (must/006; should/002, should/004, should/006).

## What is done well

- The delivery includes all 54 participant maps under one root, with annex payloads and per-map retrieval URLs/checksums in `input/sources.json` (capture SHA above; `content/workspace/input/data/`, `content/workspace/input/sources.json`).
- The code checks cohort identity, map count, grid, affine and finite values, and writes a seed, input checksums, summary tables, corrected maps and four figures (`content/workspace/scripts/group_analysis.py`, `content/workspace/results/summary.json`, `content/workspace/figures/`).
- The report uses whole-brain one-sided max-T familywise correction and clearly limits the vmPFC coordinate box to descriptive localization, while discussing normalized regressors, missing participant variance maps and the sign-flip assumption (`content/workspace/report.md`).

## Scientific assessment

**Scientific adequacy: supported.** The reported conclusion is: “No whole-brain-corrected evidence supports a positive gain effect in vmPFC in the NARPS equal-indifference group.” The analysis tests 54 independent participant effects with a positive one-sample statistic and a sign-flip maximum-t correction across 210,968 voxels. It reports 24 corrected voxels in three posterior clusters, and none in its explicit broad vmPFC locator; the locator mean is −0.003 (95% t interval −0.021 to 0.016), with its most positive voxel at max-statistic FWE p=.938 (`content/workspace/results/summary.json`, `content/workspace/results/fwe_clusters.csv`, `content/workspace/report.md`). This supports the bounded absence-of-evidence conclusion, not a claim that the true vmPFC response is zero.

The analysis is scientifically defensible for the supplied fixed inputs: it checks image geometry and data quality, keeps all 54 intended participants, and corrects the directional whole-brain search. The nonzero-in-at-least-90%-of-maps coverage mask is an explicit but data-dependent coverage choice; inference is conditional on that tested mask. Sign-flip validity assumes symmetric participant effects under the null, and absent first-level variance maps prevent precision weighting. The upstream gain coefficient reflects a normalized regressor conditional on AO86's fixed model, not BOLD change per currency unit. The broad MNI coordinate box is a transparent anatomical approximation rather than an independently defined anatomical mask. The report acknowledges these constraints and does not overstate the null result.

The separately reported hypothesis outcome is **no whole-brain-corrected support for a positive vmPFC gain effect**. It is not inferred from the adequacy category.

## Replay and access

Replay was **not checked**. The notebook's documented route runs `scripts/group_analysis.py`, and the script's ten generated artifacts are explicitly listed in `replay-record.json`. However, the worker supplied package versions only in prose and no environment declaration or install instructions; I did not substitute the assessor environment. No replay attempt was made. The record declares inputs/source protected, output selection, and the intended numeric comparison rule.

The intended recipient is a researcher using the worker-declared route. `report.md` and `input/sources.json` point to NeuroVault collection 4932 and the 54 map URLs. The assessment host received HTTP/2 200 from the collection endpoint; this tests only that host/endpoint, not all map payloads or access terms. The worker declared no route for the report, script, notebook, figures or results. Coordinator delivery is not worker publication evidence. Details and captured command output are in `access-record.json` and `access-route.*`.

## Capture integrity and attribution

The frozen probes ran against the operational copy and wrote only assessment-side `probes.json` and `response.json`; they are assessor measurements, not worker evidence. The NeuroVault request output is also preserved in the assessment directory. No additional target changes were observed in Git status; final exact integrity is left to the launcher verification. The permitted annex keys database files are excluded from worker attribution if inspection touched them; logical database equivalence is not claimed.

The stop receipt identifies the worker stop at the original HEAD and reports a complete capture with no omissions. Git status shows `report.md`, `scripts/`, `notebooks/`, `results/`, `figures/` and `.codex/` as untracked at that state. The input maps are annex-backed. Later coordinator preservation does not earn worker tracking, publication or reproducibility credit. The capture contains `.codex` and `.entire` material that may expose assistance context; it was not used to grade scientific or STAMPED attainment, and no treatment assignment was inferred or reported.

## Per-item judgments

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/input/sources.json` | The full study, inputs, code, and outputs share the captured workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/input/sources.json` | All 54 input pointers resolve to annex objects inside this captured root. |
| must/003 | S.1 | unmet | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/scripts/group_analysis.py`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/report.md` | No delivered environment includes or links the required scientific packages. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/scripts/group_analysis.py`, `probes.json` | Git is used, but the scientific code, report, notebook, figures and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | Git-annex stores all 54 participant maps as large binary inputs. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/results/summary.json`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/report.md` | The result summary records inputs and seed, but no exact environment or run record links actions to it. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/report.md`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/notebooks/narps_gain_group_analysis.ipynb` | Report and notebook explain the analysis route, but give no dependency installation instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/notebooks/narps_gain_group_analysis.ipynb` | The notebook identifies and runs the authoritative group-analysis script. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/scripts/group_analysis.py` | The analysis script resolves inputs and outputs relative to its own workspace root. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/scripts/group_analysis.py`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/report.md` | Required Python packages have no dependency declaration or reproducible installer. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/report.md` | Python package versions are noted, but OS, Python provisioning, native libraries and other host assumptions are unspecified. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/report.md` | The report lists Python packages, but omits system requirements and installation steps. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace` | No environment specification appears in the complete delivered workspace. |
| must/014 | P.3 | unmet | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace` | No dependency update or lock regeneration process is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/results/summary.json` | No pinned environment manifest identifies the environment used for these results. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/report.md`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace` | No worker route publishes the analysis, and no environment specification is shared. |
| must/017 | D.1 | unmet | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/report.md` | No instructions explain obtaining or using an environment specification. |
| should/001 | T.2 | met | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/.git/config`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | The workspace uses Git for text and git-annex for binary content within one repository. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `probes.json`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/results/summary.json` | The complete stop state has no repeated test record or recurring workflow; shipped outputs evidence one analysis run. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/input`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/scripts/group_analysis.py`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/results` | Inputs, scripts, results and figures are separated by directories; no environment module is supplied. |
| should/004 | E.1 | not-checked | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/report.md` | No safe fresh replay: the worker supplied no environment specification; a replay needs one. |
| should/005 | E.1 | unmet | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/scripts/group_analysis.py` | The documented script runs inside the caller environment and creates no disposable environment. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace` | No exact environment is specified or regularly tested for reconstitution. |
| should/007 | D.2 | unmet | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace` | No environment artifact, container image or executable bundle is archived with the study. |
| should/008 | D.2 | unmet | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace` | No dependency update or lock regeneration process is declared. |
| should/009 | M.4 | not-applicable | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/input/sources.json` | N/A: no restricted data or software is identified; the cited input collection is public. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/input/sources.json` | The independently maintained AO86 maps are identified by collection and per-image retrieval URLs. |
| may/002 | M.2 | met | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/report.md`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/notebooks/narps_gain_group_analysis.ipynb` | The report and notebook describe how inputs, group script and generated outputs relate. |
| may/003 | M.2 | partial | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/scripts/group_analysis.py`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace` | Input, code and result directories are distinct, but the workflow depends on unversioned environment state. |
| may/004 | M.2 | met | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/notebooks/narps_gain_group_analysis.ipynb`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/scripts/group_analysis.py` | The notebook runs the group script, which reads input/ and composes results/ and figures/. |
| may/005 | M.2 | met | judgement | `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/report.md`, `capture:73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b#content/workspace/notebooks/narps_gain_group_analysis.ipynb` | The report links the script and result artifacts, and the notebook presents the workflow. |

## Flagged items

- **must/002, may/001:** `subdatasets-resolvable` did not recognize the internal annex pointers and explicit upstream map URLs; the complete source listing establishes both input reachability and the independently maintained source collection.
- **must/004:** `tree-clean` treated any uncommitted analysis content as the whole versioning answer; the stop inventory shows Git use, but the scientific deliverables were untracked, so `partial` is retained.
- **must/006, must/015, should/006:** the environment-link and CI probes could not find a pinned execution environment; the complete delivery confirms the environment is absent, so these are `unmet`.
- **must/007, must/008:** `entry-point` missed the report/notebook route. The notebook runs the analysis script, but setup instructions remain incomplete.
- **must/011, must/012:** `platform-assumptions` scans commands only; the report lists packages but leaves system and install requirements undocumented.
- **should/002:** `ci-present` found no recognized CI; complete delivered evidence also has no recurring test record, so the finding is `unmet`.
- **must/014 and should/008:** These checklist items duplicate the same question and therefore share the same answer (`upstream-duplicate`).

## Not checked

- **should/004:** No fresh replay was attempted because no worker-supplied environment specification or installation route makes environment reconstruction possible. A supplied, pinned dependency declaration and fresh-host replay would settle it. See [replay record](replay-record.json).

## Goals and kind

The supplied task asks for a group-level answer using the 54 fixed AO86 gain-effect maps, with whole-brain correction, interpretable vmPFC localization, code, outputs, figures and limitations. I assume this documented goal because no human guidance was attached. The primary kind is a **study**, so this review emphasizes complete inputs and the link from code/actions/environment to results.

## Additional finding outside the checklist

The captured tree has no reuse/license statement for worker-produced code and results (`extra_items` in `response.json`; the `license-declared` probe). No license terms are inferred from public availability of the input collection.

## Checklist and provenance

Checklist link: [open this response in the STAMPED checklist app](2026-10-16-url.txt). The complete machine-readable judgments and evidence are in [response.json](response.json); scripted probe output is [probes.json](probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the original capture `73fc9ea62e9106b5f3562d14654e02b51bde570d8c60ba8727e0a67c3f1f689b`, original HEAD `ad3956ae64dcbdd1eec6af4ed21e0b168e478106`, 2026-10-16, Codex API / gpt-6.1-sol. The frozen runner check used source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28` and environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`. Probe output: `probes.json`.
