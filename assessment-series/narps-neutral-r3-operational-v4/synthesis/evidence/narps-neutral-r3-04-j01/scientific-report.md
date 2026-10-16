# Independent assessment — NARPS potential-gain group analysis

## Verdicts

MUST: 4 met / 1 partial / 11 unmet / 1 not-checked. SHOULD: 0 met / 1 partial / 5 unmet / 2 not-checked / 1 not-applicable. MAY: 1 met / 1 partial / 0 unmet / 0 not-checked / 3 not-applicable. No overall score is assigned.

**Scientific adequacy: supported.** The group model and whole-brain maximum-t FWE test support the report’s non-detection conclusion, with the nonzero-support mask and atlas approximation kept as limits.

**Reported hypothesis outcome:** “The supplied maps do not support a greater vmPFC response with increasing potential gain in the NARPS equal-indifference group.”

The checklist verdicts assess research-object practice at the worker’s recorded stop. Scientific adequacy assesses the inference from the complete stopped delivery. The canonical original capture SHA-256 is `b3e9de83b279dd3fc84a0d3bc3747073a0ee1ff9354c715c951024158bf504ba`; citations such as `content/workspace/report.md` are paths relative to that capture’s root. The captured Git HEAD is `c5e927c2c46296ba59886bffc66dc165f9cf2c78`.

## What to improve first

1. Commit the report, analysis script, generated figures, tables, and maps at worker stop → the captured Git history currently contains only seed state → closes must/004 and should/001.
2. Add a tracked environment manifest or lockfile and connect it to a run record → package versions in prose do not identify an installable environment → closes must/003, must/006, must/010, must/013, must/015–017, should/006–008.
3. Add a README or Makefile with setup and run steps, including system and atlas requirements → the report supplies a command but depends on a host-specific interpreter → closes must/007, must/011–012, must/017.
4. Publish an authorized retrieval route covering the complete workspace and its map content → no worker route is recorded, so a researcher cannot retrieve the delivery from worker-declared access → closes must/016.
5. Add an explicit spatial-coverage check or sensitivity analysis for zeros in participant cope maps → the shared nonzero support is used as a coverage proxy without supplied participant coverage masks → strengthens the scientific interpretation.

## What is already strong

- The report describes the one-sample group model, one-sided whole-brain maximum-t permutation correction, 10,000 permutations, independent atlas ROI, effect-estimate scaling, lack of variance maps, uncertainty, exclusions, and the interpretation of a null result (`content/workspace/report.md`; `content/workspace/scripts/group_analysis.py`). The original NARPS instructions require a binary hypothesis decision based on whole-brain-corrected analysis and request group maps ([NARPS analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).
- The complete delivery includes 54 supplied gain-effect maps and cohort metadata. The script checks IDs, source checksums, image grid, and finite values; the summary records no exclusions (`content/workspace/input/sources.json`, `content/workspace/input/participants.tsv`, `content/workspace/results/summary.json`).
- The worker’s report, script, figures, and outputs are present in the complete stop capture, and a fresh replay recreated the eight selected outputs byte-for-byte. This replay is evidence about scientific reproducibility on this host, not worker versioning or publication practice.

## Scientific assessment

**Category: supported.** The scientific conclusion is supportable as a statement that this analysis did not detect the predicted positive vmPFC response at whole-brain FWE α=.05. It is not support for an exactly zero effect. The report gives an atlas ROI participant-mean estimate of −0.0108 with a 95% CI [−0.0304, 0.0089], and a best-voxel vmPFC FWE p=.777; the interval still permits a small positive mean (`content/workspace/results/summary.json`, `content/workspace/results/participant_qc_and_roi.csv`).

The analysis uses the complete equal-indifference cohort of 54 independent participant maps, with checksums and geometry checks and no data-driven exclusions. A one-sample intercept model of cope estimates is a defensible group model given the supplied maps and absent participant variance maps. The one-sided maximum-t sign-flip test controls whole-brain family-wise error across the reported search mask. It found 23 corrected voxels, but its strongest positive result is in occipital pole rather than vmPFC; the report does not present that secondary finding as support for the hypothesis (`content/workspace/results/summary.json`, `content/workspace/figures/group_fwe_maxT.png`).

The vmPFC localization is operationalized by independently selected Harvard-Oxford Frontal Medial, Subcallosal, and Paracingulate labels, intersected with the group mask. That is a defensible but broad anatomical approximation, not a uniquely established vmPFC boundary. The script uses the intersection of nonzero voxels across all maps as its coverage indicator and intersects it with a resampled brain mask. Since no participant coverage maps are supplied, the shared-support choice is understandable; however, exact zeros could also be valid in-mask estimates, and the analysis does not demonstrate that they exclusively indicate missing coverage. This bounds spatial interpretation. Other stated limits are material: the effect estimates come from a mean-centered, variance-normalized upstream gain modulator, not a per-currency response; gain and loss were modeled separately upstream; and first-level uncertainty cannot be propagated without variance maps (`content/workspace/input/upstream-methods.md`, `content/workspace/report.md`, `content/workspace/scripts/group_analysis.py`).

The reported positive hypothesis outcome is therefore not supported by the corrected vmPFC evidence, while the broader claim of no effect would be too strong. The CI and explicit lack-of-equivalence caveat make that distinction clear. Figures show the corrected map, ROI location, and participant-level ROI estimates; code and summary values make the principal decisions inspectable.

### Hypothesis outcome excerpt

The supplied maps do not support a greater vmPFC response with increasing potential gain in the NARPS equal-indifference group.

## Replay and measurement availability

The worker-documented entrypoint was run once by the frozen helper from a fresh writable copy of the canonical complete delivery. The exact command was:

```text
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python scripts/group_analysis.py
```

Before replay, the eight selected generated outputs were declared in `replay-record.json`; only those files were removed from the replay copy. Inputs, participant metadata, code, and all other delivery content were protected. The documented interpreter existed on the assessment host. No environment repair or adapter prefetch occurred. The entrypoint’s own atlas-cache/network behavior is not separately byte-metered by this adapter, so this does not establish independent-host availability.

The attempt returned 0 in 601.98 seconds. All eight selected outputs were SHA-256 identical to the shipped files: the participant QC/ROI CSV, three group NIfTI maps, summary JSON, and three figures. No tolerance fallback or scientific numerical difference required interpretation. The helper’s 7,200-second limit and 5 GB prefetch compatibility parameter were not reached; the captured-delivery adapter performed no prefetch. Full replay record, stdout/stderr, and generated workspace are retained under `replay-helper.json` and `replay-work/`.

Assessment measurement remains separate from item attainment: the complete delivery allowed scientific review and replay; must/005 remains not-checked for worker attribution because annex storage of the large maps is already present in supplied seed inputs. The probe’s annex observation is retained in `probes.json` but is not treated as evidence of a worker-created practice.

## Worker stop state, integrity, and access

The stop receipt reports a complete capture, worker return code 0, normal exit, no omissions or errors, and stopped HEAD `c5e927c2c46296ba59886bffc66dc165f9cf2c78`. The receipt’s seed identity gives the same commit as `seed_commit`; its 54 map entries were supplied as annex links. This is coordinator-supplied input state. The report, code, results, and figures were untracked at stop, so their presence in the complete capture supports scientific assessment but does not count as tracked worker output. Later preservation, coordinator uploads, annex operations, and assessor replay receive no worker-practice credit.

The operational copy matched its initial manifest for all 1,106 workspace entries except regular files under `.git/annex/keysdb`: `db` changed from SHA-256 `f6f8fd7af99434db59fadc6da021051789c6aaa271ebf878c54dafc6c9fde5ca` to `233c0be3e02857e0fbf47b00b8a94de3e9126529bee41b2491286aef7372be80`; new `db-shm` and `db-wal` files appeared. No other path or byte mismatch was found. These are inspection-induced operational metadata only; no logical database equivalence is claimed (`integrity-record.json`). The captured annex links point within the retained `.git/annex/objects`; the manifest declares no external Git dependencies, and no external `.git` pointer was followed.

The intended recipient is a researcher using the worker-declared authorized route. No route was found: captured `.git/config` has no remote, `git remote -v` returned none, and the report contains no delivery URL. Required coverage would be the entire stopped workspace, including all maps, metadata, code, results, and figures; no worker route was available to test on any host. Coordinator delivery to the assessor is not evidence of worker access. See `access-record.json`.

The stopped workspace has no license declaration. The probe marks `license-declared` unmet; input provenance cites sources but does not state reuse terms. The worker report names software versions but contains no tracked environment specification. The captured Git config also has a host-specific hooks path; replay disables original hooks only in its fresh copy, leaving captured configuration unchanged.

## Checklist and item table

The response follows checklist 0.3.1. The complete response is `response.json`; unedited probe output is `probes.json`; the checklist-app URL is in [`checklist-url.txt`](checklist-url.txt). The response was validated by the frozen external runner.

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `content/workspace` | The assessed workspace is nested under one captured workspace root. |
| must/002 | S.1 | met | judgement | `content/workspace/input/participants.tsv`, `content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | The supplied maps and metadata are included and resolve within the workspace. |
| must/003 | S.1 | unmet | judgement | `content/workspace/report.md` | The report names external Python packages, but the worker delivery has no environment specification or linked software module. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `content/workspace/report.md`, `content/workspace/scripts/group_analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-04-j01/attempt-01/worker-end-state.json` | At worker stop, the scientific report, code, figures, and results were untracked and absent from the captured HEAD. |
| must/005 | T.1,T.3,T.5 | not-checked | probe:large-in-annex+judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-04-j01/attempt-01/worker-end-state.json` | The probe sees annexed large maps, but the stop receipt identifies them as supplied seed inputs; no worker handling of large generated data is established. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `content/workspace/results/summary.json`, `content/workspace/report.md` | Results exist, but no run record links them to an exact environment specification. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `content/workspace/report.md` | The worker report gives a command, but no README or Makefile provides installation and usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `content/workspace/report.md`, `content/workspace/scripts/group_analysis.py` | The report documents the analysis script as the reproduction starting point. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `content/workspace/scripts/group_analysis.py` | The analysis script resolves project inputs and outputs relative to its own workspace root. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace`, `content/workspace/report.md` | No environment specification declares the packages needed by the analysis. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `content/workspace/report.md` | Host assumptions and external atlas access/cache requirements are not fully documented. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `content/workspace/report.md` | The report lists package versions, but does not provide a complete system requirements and installation list. |
| must/013 | P.3 | unmet | probe:env-spec-tracked+judgement | `content/workspace` | No environment specification is included in the worker's versioned project state. |
| must/014 | P.3 | unmet | judgement | `content/workspace` | No process for updating environment specifications is documented. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `content/workspace/report.md` | The exact environment used for the reported results is not captured. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `content/workspace/.git/config`, `content/workspace/report.md` | No worker-published environment specification or authorized route is present. |
| must/017 | D.1 | unmet | judgement | `content/workspace/report.md` | The report gives a run command but not instructions for obtaining and using an environment specification. |
| should/001 | T.2 | unmet | judgement | `content/workspace/scripts/group_analysis.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-04-j01/attempt-01/worker-end-state.json` | The worker's analysis code and outputs are outside the captured Git history; only coordinator-seeded inputs are tracked. |
| should/002 | A.2 | not-checked | probe:ci-present+judgement | `content/workspace` | The stopped delivery does not establish whether the workflow is tested regularly. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `content/workspace/input`, `content/workspace/scripts/group_analysis.py`, `content/workspace/results/summary.json` | Inputs, code, and derived results occupy separate directories, but no environment module is supplied. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/assessment-series/narps-neutral-r3-operational-v4/judgments/narps-neutral-r3-04-j01/attempt-01/worker-end-state.json` | No worker-stop evidence establishes testing in a fresh container, batch job, clean VM, or cloud instance; the later same-host assessment replay is not worker practice. |
| should/005 | E.1 | unmet | judgement | `content/workspace/report.md` | No workflow or documentation shows that runs use disposable environments. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `content/workspace` | No exact environment specification is available to reconstitute and test. |
| should/007 | D.2 | unmet | judgement | `content/workspace` | No worker-captured environment artifact is archived with the project. |
| should/008 | D.2 | unmet | judgement | `content/workspace` | No environment specification update process is documented. |
| should/009 | M.4 | not-applicable | judgement | `content/workspace/input/sources.json` | No restricted data or software is identified in the stopped project. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | `content/workspace/input/data/sub-001_hypo1_cope.nii.gz` | No independent external project module or subdataset is declared; the maps are included within the workspace. |
| may/002 | M.2 | partial | judgement | `content/workspace/report.md` | The report lists the input, code, result, and figure paths, but does not explain modular relationships or recombination. |
| may/003 | M.2 | not-applicable | judgement | `content/workspace` | The stopped project has no separately maintained components with independently updateable module boundaries. |
| may/004 | M.2 | not-applicable | judgement | `content/workspace` | There are no separately maintained modules to compose. |
| may/005 | M.2 | met | judgement | `content/workspace/report.md` | The report names the script, results, figures, and their roles. |

## Flags and not-checked items

- **must/005 — `probe-overridden`:** the annex probe describes the supplied map storage, while the stop receipt attributes those links to seed inputs; worker annex handling is not established.
- **must/006 — `mapping-questioned`, `probe-overridden`:** the probe missed untracked scientific outputs and called the item not-applicable; complete-stop evidence shows generated results but no exact environment-linked run record.
- **must/008 — `probe-overridden`:** the entrypoint probe missed untracked files and the report-based reproduction command; the item is met because the report names and invokes the main analysis script.
- **must/014 and should/008 — `upstream-duplicate`:** both ask about the environment-specification update process; the same absent process is reported for both.

Not-checked: **must/005** needs evidence that a worker-created large binary output was managed at stop; **should/002** needs repeated testing history; **should/004** needs worker-attributed testing in a fresh environment. Coordinator replay does not settle the latter. The status distinctions are in the table and `response.json`.

## Project goal, kind, and provenance

The goal, from the retained task, is group-level inference on whether potential gain predicts a positive vmPFC fMRI response in the equal-indifference NARPS group. This is a study/research analysis object. Scientific conclusions are conditional on the supplied AO86 participant maps and fixed upstream model.

Assessor: `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), assessment date 2026-10-16. Object commit: `c5e927c2c46296ba59886bffc66dc165f9cf2c78`; canonical capture manifest SHA-256: `b3e9de83b279dd3fc84a0d3bc3747073a0ee1ff9354c715c951024158bf504ba`. Probe output: `probes.json`. Frozen assessor/runtime check passed. The checklist URL and response are linked above.

## Assistance exposure

The captured workspace includes `.codex/` and `.entire/` tooling/session material, which indicates coding-assistant activity. This exposure is recorded only and was not used as grading evidence.

The supplied `judge-target.json` matches the manifest’s canonical capture SHA-256 and commit, and its `reference_limits` list is empty. No original external target was followed.
