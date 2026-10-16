# Independent assessment — NARPS Hypothesis 1

## Verdict

**STAMPED checklist:** MUST: 5 met / 1 partial / 11 unmet / 0 not-checked (17); SHOULD: 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable (9); MAY: 1 met / 1 partial / 3 unmet / 0 not-checked / 0 not-applicable (5). There is no overall score.

**Scientific adequacy: qualified.** The group inference is well matched to the supplied participant COPE maps and the whole-brain correction requirement. Its interpretation remains conditional on the fixed upstream estimates, missing participant variance maps, a broad vmPFC proxy, and sign-flip symmetry/exchangeability assumptions.

**Reported hypothesis outcome:** not supported by this analysis. The worker reports no positive vmPFC result under whole-brain FWE control. This is evidence of no detected effect at this sample and method, not evidence that the true effect is exactly zero.

## Scientific assessment

The task asks whether gain-related response increases in vmPFC for the 54-person equal-indifference group. The worker used all 54 participants, checked IDs, source checksums, image geometry, and finite values, and formed a common support mask intersected with a resampled MNI152 brain mask (186,400 voxels). The maps are participant COPEs, not standardized statistics; the report correctly avoids interpreting them as BOLD change per dollar and notes that gain was modeled separately from loss and alongside choice.

The primary test is a positive one-sample group *t* field with 5,000 participant-level sign flips and a whole-brain max-*t* FWE correction. This is a defensible way to control voxelwise family-wise error while retaining the spatial dependence in the maps. The 25% Harvard–Oxford Frontal Medial plus Subcallosal proxy was defined independently of the observed effects and resampled to the map grid. Its boundary is approximate, as the report acknowledges. There were 23 corrected positive voxels in three small occipital clusters, none overlapping the proxy; the largest had 16 voxels (peak *t*=6.62 at MNI (−26, −102, −3.6), max-*t* corrected *p*=.001). The proxy mean was 0.0027 model units (95% *t* interval −0.0217 to 0.0270; one-sided ROI summary *p*≈.40). The participant plot shows a wide distribution around zero with the group interval crossing zero, and the corrected-result figure localizes the positive clusters posteriorly. The result does not support a positive vmPFC effect under the required whole-brain criterion.

The report appropriately limits generalization: runs were already combined; first-level variance maps and the executable upstream pipeline were not supplied; the group test is unweighted; and the COPE scale follows AO86’s mean-centered, variance-normalized gain modulator. The absent variance maps preclude precision-weighted group modeling, but do not prevent a defensible participant-level group test. The inference assumes participant effects are independent and sign-flippable under the null. It is qualified rather than unqualified because these are material limits on what a null finding means, and the atlas-to-map resampling gives an approximate anatomical locator.

**Evidence:** [worker report](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-19-j01/content/workspace/report.md>), [analysis script](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-19-j01/content/workspace/analyze.py>), [machine-readable results](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-19-j01/content/workspace/results/results.json>), [upstream methods](</Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-19-j01/content/workspace/input/upstream-methods.md>).

## Replay and measurement

One replay attempt used the exact command documented in `report.md`:

```sh
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python analyze.py
```

The frozen helper copied the complete stopped workspace, retained its inputs/cache bytes, and removed only the three selected generated files in that copy: `results/results.json`, `results/participant_qc.tsv`, and `results/fwer_positive_clusters.tsv`. It then recreated all three byte-for-byte. The comparison therefore covers the machine-readable result and participant/cluster tables; it does not claim the pre-existing figures or NIfTI maps were replayed. The analysis script itself checks all 54 input hashes and matching geometry during this replay. The attempt took 9.46 seconds, exited 0, and stayed within the fixed 7,200-second and 5 GB bounds. See [replay record](2026-10-16-fresh-rerun.json), [declaration](replay/declaration.md), and retained stdout/stderr under `replay/work/`.

No assessor malfunction occurred during probe or replay. A direct fetch of the linked original instructions PDF timed out; the supplied frozen task and scientific guidance state the applicable whole-brain correction rule, so the assessment continued on that basis (see `source-lookup.json`). Two response-format command errors occurred during assessment finalization (a non-checklist `qualified` status was rejected for an extra item; the URL encoder was first called with an unsupported `-o`). Both failures and outputs are retained in `commands/`; the invalid extra item was removed, the checklist response validated, and no target file was changed.

## Delivery boundary, access, and attribution

The stop receipt says the worker exited normally at 2026-10-16 07:23:20 UTC with HEAD `675620fed8a134102b1b07226fe39d67630ee6f7`. The complete delivery manifest verified against the receipt hash: capture complete, zero errors, zero omissions. This assessment uses the entire capture, including untracked material. The worker’s code, report, cached atlas references, and results were untracked at stop; the `tree-clean` probe records these paths. The commit alone therefore does not contain the scientific delivery. No coordinator preservation action or this assessment’s replay receives worker-practice credit.

The input map links resolve within the delivery to retained Git-annex payloads; source URLs, IDs, and hashes are in `input/sources.json`. No original external Git pointer was followed. The frozen replay helper’s `judge-target.json` records an empty `reference_limits` list. Workspace `.codex`, `.entire`, and task-skill material reveal agent/tooling assistance; this exposure is recorded but not used as grading evidence. No treatment assignment was inferred or used.

**Access:** intended recipient is a researcher using the worker-declared authorized route. No worker-declared retrieval/publication route for this scientific delivery was found, and the local Git config has no remote. The upstream input URLs are not an access route for the worker’s report, code, results, and environment. No route host could be tested; the coordinator’s access to the captured object is not evidence of worker sharing. See [access record](access-record.json).

## What to fix first

1. Track the analysis, report, references, and generated results in the worker’s version control state → the committed snapshot omits the scientific delivery (MUST/004; SHOULD/001).
2. Add a portable, pinned environment declaration, installation instructions, and an environment-linked run record → the current command assumes a host-specific interpreter and cannot reconstruct the analysis environment (MUST/003, 006, 007, 010–017; SHOULD/006–008).
3. Publish an authorized route that contains the report, code, results, inputs or their retrieval instructions, and environment artifacts → a recipient cannot retrieve the complete research object from a worker-declared location.
4. Record regular workflow checks and clean-environment execution, and make any per-run environment disposable → repeatability evidence is absent (SHOULD/002, 004, 005).
5. Document the input/code/results/environment boundaries and how components compose → the current structure is usable but not modularly described (SHOULD/003; MAY/002–005).

## What is already done well

- The report explains the whole-brain max-*t* decision, the independent vmPFC locator, the COPE scale, and limits on a null result.
- The script validates participant identities, all input checksums, image geometry, and finite values before group inference; no participants were excluded.
- Large maps are annex-backed and source provenance is detailed, while the worker’s complete stopped workspace preserves the otherwise uncommitted report, code, and results for this assessment.

## Per-item checklist

The 31 checklist items (checklist 0.3.1; `partial` does not satisfy a MUST):

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/participants.tsv`, `analyze.py` | All delivered files, inputs, code, and results sit under one workspace root. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz` | Participant maps resolve through relative in-root annex links; sources.json records origin, IDs, and checksums. |
| must/003 | S.1 | unmet | judgement | `report.md`, `analyze.py` | No delivered environment specification or linked external software module declares the runtime dependencies. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/worker-end-state.json` | Git is present, but the analysis script, report, references, and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex+judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json` | All 54 large map payloads use relative Git-annex links with retained payloads inside .git/annex. |
| must/006 | T.1,T.3,T.5 | unmet | judgement | `results/results.json`, `results/run.log`, `report.md` | Results list package versions, but no exact environment specification is linked to the worker run. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json` | report.md gives a usable invocation, but no installation steps or portable environment setup. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-fresh-rerun.json` | The report identifies analyze.py as the entrypoint and the documented command completed in the replay copy. |
| must/009 | P.1 | met | judgement | `analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json` | analyze.py uses paths relative to its own directory; it contains no host-specific input or output path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json` | No environment file declares all required Python packages. |
| must/011 | P.1 | unmet | judgement | `report.md` | The documentation assumes an already installed interpreter at a machine-specific path and does not state host requirements. |
| must/012 | P.2 | unmet | judgement | `report.md`, `results/results.json` | No portable list of system requirements and installable dependencies is provided. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json`, `analyze.py` | No environment specification is tracked with the analysis. |
| must/014 | P.3 | unmet | judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json` | There is no declared environment update or lockfile regeneration process. |
| must/015 | D.1 | unmet | judgement | `report.md`, `results/results.json` | No frozen manifest or container digest permits exact environment reconstruction. |
| must/016 | D.1 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/worker-end-state.json` | No environment artifact is published or archived with the worker delivery. |
| must/017 | D.1 | unmet | judgement | `report.md` | The report does not explain how to obtain or recreate its external Python environment. |
| should/001 | T.2 | partial | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json`, `input/sources.json` | Git-annex tracks the large inputs, while the analysis, report, and generated results remain untracked. |
| should/002 | A.2 | not-checked | judgement | `results/run.log`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/worker-end-state.json` | The captured workspace has one run log; whether the worker regularly tested the workflow needs the worker’s broader run history. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/participants.tsv`, `results/results.json`, `analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json` | Inputs and outputs have directories, but code is at the root and no environment module is defined. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-fresh-rerun.json`, `results/run.log` | Worker-side fresh-container or clean-machine testing is not evidenced; the coordinator replay is not worker practice. |
| should/005 | E.1 | unmet | judgement | `analyze.py`, `report.md` | The workflow runs in the supplied pre-existing environment and does not create a disposable environment. |
| should/006 | D.2 | unmet | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json`, `results/results.json` | No exact environment specification exists to reconstitute and test. |
| should/007 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/worker-end-state.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json` | No environment binaries, image, or frozen package artifacts are archived with the delivery. |
| should/008 | D.2 | unmet | judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json` | No environment update process is declared or tracked. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the delivery contains no restricted data or software; the supplied public cohort/maps are handled as inputs. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json` | External scientific inputs are independently identified and retrievable by source URL, with stable IDs and checksums; payloads are annex-backed in-root. |
| may/002 | M.2 | unmet | judgement | `report.md` | No document describes module relationships or recombination. |
| may/003 | M.2 | unmet | judgement | `analyze.py`, `report.md` | No modular interfaces or independent update boundaries are defined. |
| may/004 | M.2 | unmet | judgement | `report.md`, `analyze.py` | No mechanism composes separately maintained modules. |
| may/005 | M.2 | partial | probe:modules-separated+judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-19/judgments/narps-neutral-r1-19-j01/attempt-01/judgment/2026-10-16-probes.json` | The report names key files, but does not document the directory/module structure or how components relate. |

Canonical [response JSON](2026-10-16-response.json).

### Flagged items

- **MUST/005:** the probe recognized annex use; direct inspection confirmed the 54 relative links and payloads retained under the complete capture.
- **MUST/007 and MUST/008:** the entry-point probe scanned tracked paths and missed the untracked `report.md` and `analyze.py`; full-delivery inspection found the documented command and the replay confirmed it runs.
- **MAY/001:** the subdataset probe found no Git submodules. The dataset is instead present as annex-backed in-root inputs with independently identified source URLs and checksums.

### Not checked

- **SHOULD/002:** one run log is present, but the captured stop state does not settle whether the worker tested the workflow regularly. A retained history of repeated worker runs would settle this.
- **SHOULD/004:** worker-side execution in a fresh container, batch job, clean VM, or cloud instance is not established. The coordinator’s replay is excluded; a worker run record or CI configuration would settle it.

## Goals and kind

The goal is the supplied NARPS Hypothesis 1 group-analysis task, as stated in `input/study-task.md`. This is a computational study. The assessment emphasizes traceable inputs, versioned code and results, an executable entrypoint, environment reconstruction, and accessible delivery.

**Checklist URL:** [open the completed checklist](2026-10-16-url.txt). **Response:** [2026-10-16-response.json](2026-10-16-response.json). **Probe output:** [2026-10-16-probes.json](2026-10-16-probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.2.0 with `stamped-conventions` 0.2.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the captured study workspace at commit `675620fed8a134102b1b07226fe39d67630ee6f7`, 2026-10-16, Codex API/GPT-6. Probe output: `2026-10-16-probes.json`. Delivery capture SHA-256: `3d05d8750a1d869cef98d6b221d945d97e8297b0c81f3f4ebc4ed10643e04ec1`.
