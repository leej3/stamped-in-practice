# Independent assessment — NARPS gain effect in vmPFC

## Scope and identity

This assessment concerns the complete stopped workspace captured at SHA-256 `4cb6043b8fa2409c631a8c49a0b0b5ea0feec21e0162f4e924f9c08d1be8939f` (canonical manifest `manifest.json`). Original captured HEAD is **null**. The current operational checkout reports commit `8a84ddc3eec68d0b7513f9a15ce37174288b36b7`, but the worker-stop receipt records no commit; that checkout commit is coordinator state and receives no worker versioning credit. The scientific report, code, figures, and results were present as untracked files in the operational tree. Canonical evidence below is cited by capture-relative path and per-file SHA-256; the operational copy was used for inspection.

The worker-stop receipt records a normal exit (return code 0, not timed out). The supplied inputs include the cohort table, source manifest, upstream methods, and 54 participant maps. The capture is complete. The checkout contains symlinks for the map files into its internal `.git/annex/objects`; the canonical capture retained the link bytes and annex dependencies. No Git command was run through an external `.git` pointer. The inspected local Git config contains an absolute hooks path outside the captured tree, and `judge-target.json` identifies external skill-directory references that were not followed. This bounds conclusions about those external resources and their state, not the captured scientific files.

The frozen runner check succeeded. Its automated probes are retained in `probes.json`; they were treated as leads, not conclusions, because they inspect the coordinator-created commit and do not represent the worker-stop state or all untracked files. The `tree-clean` and tracked-file probes therefore do not substitute for stop-state review.

## Scientific judgment

**Scientific adequacy: supported.** The report's conclusion is supported by a defensible group-stage analysis. It tests the supplied gain-effect estimates for all 54 equal-indifference participants using a positive one-sample model and whole-brain maximum-t sign-flip family-wise correction, and localizes vmPFC descriptively without restricting the correction family. The report distinguishes the positive corrected posterior clusters from vmPFC and states that no vmPFC voxel survived correction. It also avoids interpreting a null corrected result as evidence of zero effect.

The protocol specifies participant-level sampling, input identity and geometry checks, a common nonzero coverage mask, 10,000 sign flips, plus-one correction, seed, and an anatomical coordinate locator. The code implements these decisions and directly checks a voxelwise statistic against SciPy. The recorded summary reports 54 included participants, 198,029 common-coverage voxels, 24 corrected voxels in three clusters outside vmPFC, and zero corrected voxels in the vmPFC locator. The vmPFC regional mean interval spans zero and the uncorrected vmPFC peak has whole-brain FWE p=0.932. These artifacts support the report's absence-of-support conclusion.

Important limits are appropriately stated: supplied maps are normalized-regressor participant cope estimates rather than slopes per currency unit; gain and loss were fit separately; participant variance maps and the executable first-level pipeline are absent; and inference is conditional on those upstream inputs and the equal-weight group model. The sign-flip test assumes participant independence and sign-symmetric errors, which the report names. The protocol describes inspection of a pilot and mask, although the retained material does not include a separate pilot record or a rendered mask-inspection artifact; this limits auditability of that check but does not undermine the documented whole-brain inference. No numerical replay was attempted (see replay record).

**Reported hypothesis outcome:** “The supplied group maps do not support a greater gain-related fMRI response in vmPFC after whole-brain correction.” This is the worker's conclusion, retained separately from the adequacy category.

Key scientific artifacts (capture SHA-256 follows each path):

- `content/workspace/report/report.md` — `3cda75c9387c17a0e27888364f21a476def491e0bcde778a2e8c85b8e602f6d2`
- `content/workspace/analysis/protocol.md` — `a9ec3085aee04ae796fc176816826c77b56d4da37a446d4ad6eb1dd81e27f404`
- `content/workspace/analysis/group_analysis.py` — `b3f9b7763a927fd0447e3ec1ca6fb11da455041dfe5226386b9fc6a1cde30fa2`
- `content/workspace/results/summary.json` — `2da6c571d6a96bbc326c70c75e140f6194c32e73bc81a6910a084e7feccaa73b`
- `content/workspace/results/participant_qc.tsv` — `e5ae3e0e6fa88d29675713b8d9a35b89fc6bae8db2b3ab2bf7690667474806e5`
- `content/workspace/input/upstream-methods.md` — `508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`

## STAMPED checklist findings

These are item attainments, not a combined score. Unless otherwise stated, a path is relative to the captured workspace under the canonical capture above. The response JSON carries an evidence citation for every verdict. Items about versioning, publication, environment capture, and sharing reflect the worker stop state; coordinator-created commits, annex conversion/retention, and delivery routes are not treated as worker actions.

| Item | Status | Finding |
|---|---|---|
| must/001 | met | The complete object is organized under one workspace root. |
| must/002 | met | Code uses relative input paths; all 54 input map links resolve within the captured workspace's annex store. |
| must/003 | unmet | No environment specification includes the external software dependencies. |
| must/004 | unmet | At worker stop there was no captured HEAD and the scientific additions were uncommitted/untracked; the current coordinator commit does not count. |
| must/005 | unmet | Large map content is annex-backed in the delivered copy, but annex conversion/retention is coordinator-supplied and does not establish worker use of version control for large files. Scientific outputs are ordinary files. |
| must/006 | unmet | Results record software versions and a seed, but no exact environment specification is linked to the run. |
| must/007 | unmet | `analysis/README.md` explains the analysis, but does not provide installation and system dependency instructions; no root README or Makefile supplies them. |
| must/008 | met | `report/report.md` and `analysis/README.md` name `analysis/group_analysis.py` as the reproduction entrypoint. |
| must/009 | unmet | The reproduction command embeds a host-specific absolute Python path in `report/report.md`; internal analysis paths are relative. |
| must/010 | unmet | No dependency declaration or lockfile is present in the stopped workspace. |
| must/011 | unmet | Host requirements and system configuration are not documented; the report's local absolute interpreter path is not a portable host specification. |
| must/012 | unmet | No clear dependency/system-requirement list is provided. |
| must/013 | unmet | Environment files are absent from the worker's captured workspace. |
| must/014 | unmet | There is no tracked environment specification or documented update process. |
| must/015 | unmet | Software versions are listed, but there is no frozen manifest from which the environment can be reconstructed. |
| must/016 | unmet | No worker-published environment specification or archive is recorded. |
| must/017 | unmet | Environment acquisition/use instructions are absent; the report points to a machine-local path. |
| should/001 | unmet | The worker-stop record does not show a worker commit tracking code, text, and configuration. |
| should/002 | not-checked | No evidence establishes regular workflow testing over time. |
| should/003 | met | Inputs, analysis code, results, figures, and report occupy distinct directories. |
| should/009 | not-applicable | No restricted data or software is identified in the captured task package. |
| should/004 | not-checked | No worker evidence establishes execution in a fresh container, VM, batch job, or cloud instance. |
| should/005 | not-checked | No disposable-environment workflow is documented. |
| should/006 | not-checked | No exact environment specification exists to test for reconstruction. |
| should/007 | unmet | No environment artifact is archived in the worker's stop state. |
| should/008 | unmet | No process for tracking environment updates is documented. |
| may/001 | not-applicable | No independently maintained software component is identified for submodule composition. |
| may/002 | partial | Directory boundaries are apparent, but no guide explains how the modules relate. |
| may/003 | not-checked | Independent updating/recomposition of the directories is not demonstrated. |
| may/004 | not-applicable | No separately versioned modules require a composition mechanism. |
| may/005 | partial | The report points to the code and results, but no project-level navigation guide covers the full workspace. |

Worker-stop attribution is supported by the supplied receipt (`worker-end-state.json`, SHA-256 `b989c63ef99528772a7594ef4adba6eb1e961ef6c9c087485740c28468bb9d06`) and the canonical capture. Probe output `probes.json` reports several apparent failures and passes against the later coordinator commit; where that state differs, the table applies the recorded worker stop and complete workspace instead. In particular, the presence of annex pointers in a coordinator-provisioned input package is not evidence that the worker performed annex conversion.

## Access and retrieval

**Intended recipient:** a researcher using the public source URLs recorded in `input/sources.json`. **Route:** NeuroVault collection 4932 for the participant maps, plus pinned `raw.githubusercontent.com` URLs for the cohort table and upstream-methods workbook. The route record is part of the supplied input manifest, so worker authorship of that route is not established. **Required artifact coverage:** the route covers source maps and referenced metadata; it does not cover the worker's group-analysis code, protocol, generated maps, figure, or report as one retrievable project. No worker publication or repository route for the complete delivery was recorded.

I made HTTP HEAD requests from this assessment host to the collection page, one representative map (`sub-001`), and both pinned metadata URLs. Each returned HTTP 200. The tested host scope was `neurovault.org` and `raw.githubusercontent.com`, for those four URLs only. Request headers, stdout, stderr, and exit status are retained under `route-check/`. This confirms current access to those requested source resources; it does not show that the worker had published the complete object or that all 54 map URLs were individually tested.

## Replay and measurement availability

**Replay status: not checked.** The documented invocation is `.../bin/python analysis/group_analysis.py` from the workspace root; the report gives the absolute interpreter path `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python`. That runtime is outside the captured workspace, and the reference-limit rule prohibits following external absolute targets. The stopped workspace contains no dependency specification from which to reconstruct it. Using the assessor interpreter as a substitute would not follow the worker's supplied environment instructions, so no replay attempt or output deletion was made.

Had the documented runtime been available within the permitted scope, the explicit generated-output selection would have been `results/mean_cope.nii.gz`, `results/tstat.nii.gz`, `results/p_uncorrected.nii.gz`, `results/p_fwe_maxT.nii.gz`, `results/common_coverage_mask.nii.gz`, `results/participant_qc.tsv`, `results/summary.json`, and `figures/group_gain_effect.png`. Those are identifiable outputs named by the code; source maps, participant metadata, code, protocol, and report would remain protected. The documented analysis uses a fixed seed; a replay comparison would compare numeric map voxels, QC rows, and quantitative summary values at relative tolerance 1e-6, while treating image encoding/formatting as non-scientific and not treating logs, timestamps, or prose as scientific quantities. No helper attempt was made because the necessary runtime could not be established safely. This is a scoped unavailable measurement, not a scientific failure.

## Integrity and limitations

Inspection was performed on the operational copy. The captured original remains identified by canonical manifest SHA-256 above. No repair, source modification, or replay was made. Some early reconnaissance stdout was displayed in the assessment session rather than separately retained; subsequent probe output, route requests, and generated assessment artifacts are retained outside the target. No evidence of treatment assignment was sought or used. The target's assistance-related `.entire` logs were not opened, so no conclusion about their contents is made.

Operational-copy integrity check found no missing or extra paths and no scientific-content, link, index, ref, object, or configuration differences. One regular-file difference was observed at `.git/annex/keysdb/db`; it is within the specifically permitted operational metadata set. This may have been updated by read-only Git/annex inspection or the frozen probe. The database's logical equivalence is not established, and this metadata difference is not worker evidence. See `integrity.json`.

Scientific adequacy category: supported.

Visual review of `figures/group_gain_effect.png` (capture SHA-256 `590e972b902641d386728e7d65f27a8443722215c2249214436abc908b6a4aaf`) found the unthresholded maps and corrected contour consistent with the text: the only outlined focus is posterior/inferior, and the participant plot shows the vmPFC locator mean centered near zero with a broader selected-peak distribution. The figure is legible and labeled with MNI coordinates and normalized-regressor units.
