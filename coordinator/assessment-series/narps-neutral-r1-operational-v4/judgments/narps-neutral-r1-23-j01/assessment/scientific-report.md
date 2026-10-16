# Independent assessment

## Identity and scope

Assessed the unchanged operational copy against canonical capture SHA-256 `9370db020f9b437ca3a96b2e171d89d3d52cc94554a3d62d23da0b0ca71fcb59`; captured HEAD is `afb62884c70115b6e46a92ddcd1d17bbf4f33544`. The worker-stop receipt records a completed, non-timeout exit. Canonical and operational manifests are identical. A read-only inventory/hash comparison found no non-database differences from the operational manifest; regular-file changes to the allowed annex keys database files were excluded from that comparison. No mismatch was found, and no target repairs were made.

Citations below use the canonical capture SHA-256 above and paths relative to the captured workspace root. The scientific delivery consists of untracked `analysis/`, `results/`, `figures/` and `report.md` at worker stop; `.codex/` and `.entire/` are ignored. Thus the committed HEAD is not the complete scientific delivery. The original Git metadata is a workspace-resident `.git` directory rather than an external pointer. No separate `judge-target.json` was present beside the supplied canonical or operational manifests, so I could not consult separate `reference_limits`; I used the retained manifest mapping and did not follow any original absolute or external target. The captured annex links resolve within the captured `.git/annex/objects` layout. The captured `.git/config` records an external hooks path, which was not followed or invoked. I did not use coordinator preservation as worker evidence.

## Scientific judgment

**Scientific adequacy: supported.** The report's conclusion is directly supported for the stated group-stage question: it includes all 54 independent participant COPEs, applies a positive one-sample test and whole-brain max-T sign-flip correction, and finds no corrected vmPFC voxel. The reported vmPFC estimate is negative and its descriptive interval includes zero. This supports absence of corrected positive evidence under this model; it does not establish a true zero effect. The script checks participant identity, finite values, shared shape and affine, and common spatial support; it documents no exclusions, a fixed random seed, permutation count, and ROI definition. The atlas-based vmPFC label is an explicit localization aid, and the report appropriately limits claims given absent participant variance maps and the upstream gain scaling. The sign-flip result depends on symmetric participant-level errors under the null; the group result is conditional on the supplied first-level estimates. No independent replay was available to confirm the shipped result.

The worker report's verbatim hypothesis outcome is: “Among the 54 participants in NARPS's equal-indifference group, the supplied gain-effect maps do **not** provide whole-brain family-wise corrected evidence for a gain-related increase in vmPFC.”

Scientific evidence: `analysis/group_analysis.py` (SHA-256 `d0dea707c7b71da7308673193a6840e2511ee75bc7038874ea91d3a6c964a21f`), `input/upstream-methods.md` (SHA-256 `508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`), `results/summary.json` (SHA-256 `34765e34ed05ddee7264252caeb9bb4605c76eb63c6d76ffc33d605018c0d7d3`), `results/participant_qc.tsv` (SHA-256 `069c6529fd395b0af592783964a3fc7651d403c202b411d7b32d0d8526140bac`), `results/permutation_max_t.tsv.gz` and `results/fwe_clusters.tsv`, and `figures/whole_brain_fwe.png` / `figures/vmPFC_subject_estimates.png`.

## Scientific result and limitations

The worker reports 23 voxels in three posterior occipital-pole clusters at whole-brain FWE α=.05 (peak t=6.62, max-T FWE p=.0006), and no vmPFC voxel surviving correction. The vmPFC subject-mean estimate is −0.009 with a 95% t interval [−0.040, 0.022]. The independently defined Harvard-Oxford Frontal Medial Cortex subset (y≥0, z≤0) is 769 voxels; because atlas boundaries vary, that ROI summary is descriptive. The uncorrected map is explicitly for display and is not treated as hypothesis support.

The model gives participants equal weight because first-level variance maps are unavailable. The coefficient is not a currency-unit slope: the upstream gain modulator was mean-centered and variance-normalized, gain and loss were modeled separately, and potential-gain range was twice the potential-loss range. Whole-brain correction and the symmetric-error assumption limit sensitivity and inference. A null corrected result means this delivery does not establish a positive vmPFC effect; it does not show that the true effect is exactly zero or rule out a smaller or differently specified effect. No material inference error was identified in the reported group-stage conclusion.

## STAMPED evidence and verdicts

The required frozen runner check passed. Frozen probes are retained in `probes/probes.json`; they are evidence aids, not substitutes for item-level judgment. The probe missed the documented command in the report for `must/008`, and its ignored-file blindness matters for describing the complete stop state. Item verdicts are recorded in `response.json` and cite canonical-capture paths.

At worker stop the project used Git and git-annex for the 54 binary maps, but the analysis, report, results and figures were untracked, and `.codex/` and `.entire/` were ignored. I therefore find version control present but not sufficient to track the complete delivery (`must/004` unmet). The project separates `input/`, `analysis/`, `results/` and `figures/` in its actual tree, though there is no documented modular architecture and no separate environment module (`should/003` partial). The report documents `python analysis/group_analysis.py`, so a starting script/command is identifiable even though the runner's entry-point probe did not recognize it.

No tracked Python dependency specification, lockfile, container, system requirements, environment provenance record or environment-sharing instructions were found. Those deficiencies affect environment and sharing items; they do not invalidate the scientific contents. The analysis script imports NumPy, pandas, nibabel, SciPy, Nilearn and Matplotlib, and calls Nilearn atlas/template/mask loaders. Because the worker supplied no dependency declaration or reconstruction instructions, replay prerequisites cannot be established. Replay is recorded as not checked, not as a failure.

## Access and route check

Intended recipient: a researcher following the worker's declared source links. `input/sources.json` points to 54 individual NeuroVault map URLs and a pinned raw GitHub cohort table; its methods metadata also identifies the upstream methods source. A HEAD request to one representative NeuroVault map and to the pinned cohort-table URL returned HTTP 200 on 2026-10-16. This tests host/endpoint reachability only, not every map byte or checksum. The listed route covers the input maps and cohort metadata, but does not publish the worker's analysis code, report, generated results, or a reproducible environment. No worker-declared repository/archive route for the complete project was found, and coordinator delivery is not evidence of worker publication. Tested host scope: `neurovault.org` (one representative map URL) and `raw.githubusercontent.com` (pinned metadata URL). See `access-record.json` and preserved response headers under `commands/`.

## Exposure and attribution

The stopped workspace contains `.entire/` logs/session metadata. Their presence is recorded as an assistance-trace exposure; those contents and any assistance identifiers were not used as grading evidence. The worker-stop receipt, not later coordinator commits or delivery operations, is the basis for versioning, tracking, publication, and environment-sharing judgments. No treatment assignment was inferred or reported.

## Replay record

The documented candidate command is `python analysis/group_analysis.py` from the workspace root. Its declared generated outputs are listed in `replay-record.json`; only those paths would be selected for removal in a fresh copy. The required Python packages and remote Nilearn atlas/template/mask resources are not pinned or documented in the stopped delivery. Therefore no safe prerequisite could be established, no replay attempt was launched, and no shipped output is represented as replay evidence. The frozen replay helper's 7,200-second limit, 5 GB prefetch compatibility parameter and one-attempt allowance were not exercised.

## Assessment artifacts

The response, probes, checklist link, replay record, access record, validation logs, and scientific judgment record are in this assessment directory. The supplied scientific-journal validator was run against `scientific-judgment.json` and the canonical delivery manifest. The response was validated with the frozen external runner.
