# Independent assessment

**Scope and identity.** The assessment used the complete stopped delivery, identified by canonical capture SHA-256 68b83ae17508a0293ee1ae60d80ce07321a3d0598bc484b990ca852b64f07441, captured HEAD e929d623d8de313d2ecdd97911ea8487077af580, and stop time 2026-10-16 06:36:45 UTC. The evidence paths below are relative to that captured root. The operational copy initially matched the canonical capture; the launcher is responsible for its exact pre/post verification. The retained stop inventory includes uncommitted scientific files and ignored session material, so the commit alone does not define the assessed delivery. A read-only comparison of the operational copy against all 1,057 captured workspace entries found no content, mode, link, or unexpected-path mismatch. The regular file .git/annex/keysdb/db changed during inspection and is the sole permitted operational-metadata difference; logical database equivalence is not established. An initial custom checker used the wrong manifest field for symlink targets and produced false key lookup errors; its corrected comparison is retained in integrity-check.json.

## Scientific judgment

**Scientific adequacy: supported.** The worker's reported conclusion is: “The supplied group maps do not support a positive gain effect in vmPFC under whole-brain corrected inference.” The analysis supports this conclusion conditionally on the supplied participant estimates. The code tests all 54 gain COPE maps with a one-sided one-sample t statistic and 9,999 sign flips, comparing voxel statistics against each permutation's whole-analysis-mask maximum. The reported 23 family-wise-error significant positive voxels peak in posterior occipital cortex, not vmPFC. The vmPFC-core estimate is descriptive (mean 0.0018, 95% t interval −0.0153 to 0.0190; one-sided uncorrected p=.416); it is not presented as corrected regional evidence. The report correctly says this does not establish a zero effect or rule out smaller effects.

The group method is defensible for these inputs: maps are participant effect estimates rather than t/z statistics; runs are already combined; IDs match the 54-row metadata; common shape and affine are asserted; and the intersection of nonzero coverage avoids treating outside-estimation zeros as data. The reported MNI vmPFC envelope is explicit and used descriptively while confirmatory inference remains whole brain, as required. Fixed upstream mean-centered, variance-normalized gain estimates are not currency-unit response slopes, and participant variance maps are unavailable; equal weighting and the report's stated symmetric/exchangeable sign-flip assumption therefore limit interpretation. The output also does not directly compare gain and loss or establish causality. These qualifications do not overturn the reported absence of corrected vmPFC support. No replay result is used as scientific evidence.

Evidence: analysis/group_analysis.py (SHA-256 9b4df616e47890d4236a96b7cd7359ef58a91aa5f42968a17bcf9e516af1f6d2), results/summary.json (4cc200c8c6dd21e8cad9fbe9d9f8a8177487198c5666106082322ec8564b1fd0), report.md (8e70ad20b717ded5ab34a9cebf741da55fbd6d381dc3f51041376719bce82a14), input/upstream-methods.md (508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b), and input/participants.tsv (faca815bcb042144bdb8dcff915f45de0d27650f60416ed76a5a72557341abbf). Each path refers to bytes in the canonical capture named above.

The code checks map geometry and cohort membership, but the written QC does not show participant overlay or coverage visualizations; the plotted group maps help inspect the group result but do not fully substitute for per-map spatial QC. Inference is bounded to common support and the chosen anatomical envelope. The supplied upstream methods also state that no first-level variance maps or executable upstream model are available.

**Reported hypothesis outcome:** no positive vmPFC gain effect is supported under whole-brain correction. This is the worker's reported outcome, kept separate from scientific adequacy.

## Replay and measurement availability

Replay is **not checked**. Before replay, the declared command was python analysis/group_analysis.py; prerequisites were the captured inputs and the worker-described “supplied Python environment,” with no added dependency installation or repair. The selected generated outputs were the four named NIfTI maps, results/summary.json, and the three named figures. The declared comparison was numeric table comparison at rtol=1e-6; images would be byte-compared; logs, timestamps and prose were not selected as scientific outputs.

The first frozen-helper invocation failed before materialization because I had created its required-new work directory. I preserved its command, stdout, stderr and exit status under replay/. A second invocation was refused with “Formal replay allowance already consumed”; no scientific entrypoint ran. This is an assessor invocation/setup failure, not target behavior. No replacement replay was attempted. See replay/replay-record.json and the two retained command/output sets.

## STAMPED assessment

| Level | Met | Partial | Unmet | Not checked | Not applicable |
|---|---:|---:|---:|---:|---:|
| MUST | 5 | 0 | 12 | 0 | 0 |
| SHOULD | 0 | 2 | 6 | 0 | 1 |
| MAY | 0 | 2 | 0 | 0 | 3 |

The per-item verdicts and evidence citations are in [response.json](response.json); the frozen probe output is [probes.json](probes.json), and the generated per-item table is [checklist-table.md](checklist-table.md). The checklist application link is [checklist-link.txt](checklist-link.txt).

The principal gaps are environment definition and provenance, inclusion of scientific work in worker version control, and user-facing setup instructions. At worker stop, the captured Git HEAD contains the supplied inputs, while analysis/, report.md, figures/, and results/ are outside that commit. They remain assessable as part of the complete stopped workspace. The participant maps are annex-managed and retained; this earns large-file tracking credit, but coordinator preservation does not add worker publication credit.

The report documents a clear script entry point and relative project paths. The code, figures, results, and input data are separated by directories, but there is no environment module or dependency declaration. input/sources.json declares NeuroVault and pinned raw GitHub source routes. Current HEAD requests to the collection page, one map URL, the participant-table URL, and the upstream-methods URL returned HTTP 200; the tested hosts were neurovault.org and raw.githubusercontent.com. The intended recipient is a researcher using those authorized source routes. They cover the original maps, cohort metadata, and methods source, not the worker's report, analysis code, figures, or group outputs. These current host checks do not establish availability or complete-project publication at worker stop. No separate worker-declared route for the complete project or a pinned execution environment was found.

Captured Git configuration records an absolute core.hooksPath outside the project root. The replay helper would overlay hooks only in its separate copy; replay never reached that step. This host-bound configuration does not change the scientific conclusion. Inspection of the captured commit metadata also exposed a Codex Desktop co-author attribution. This is recorded as assistance exposure only and was not used as grading evidence; no treatment assignment is inferred.

## Item-level evidence and verdicts

All citations in response.json point to original capture-relative paths. File SHA-256 values there identify the cited original bytes; the canonical capture identity above identifies the complete delivery boundary. Probe-only signals were reviewed against the full stopped workspace, including untracked files. No overall score is assigned.

## Assessment provenance

Produced by the frozen assess-alignment-with-stamped-principles assessor version 0.1.0 with the supplied stamped-conventions dependency and checklist 0.3.1 on 2026-10-16. Object kind: study. Original commit: e929d623d8de313d2ecdd97911ea8487077af580; canonical delivery capture SHA-256: 68b83ae17508a0293ee1ae60d80ce07321a3d0598bc484b990ca852b64f07441. Frozen probe output: probes.json. Full response: response.json.
