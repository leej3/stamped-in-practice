# Independent assessment: NARPS equal-indifference gain analysis

**Verdict line:** MUST: 9 met / 4 partial / 4 unmet / 0 not-checked; SHOULD: 0 met / 2 partial / 3 unmet / 3 not-checked / 1 not-applicable; MAY: 2 met / 1 partial / 0 unmet / 0 not-checked / 2 not-applicable.

**Scientific adequacy: supported.** The report's conclusion that the supplied maps do not provide whole-brain-corrected support for a positive vmPFC response is supported by the declared group analysis and reported results. This is not evidence of no vmPFC gain response: the ROI confidence interval includes zero and no equivalence bound was set. The positive hypothesis outcome is retained separately below.

**Reported hypothesis outcome:** “The supplied gain-effect maps do **not support a positive vmPFC response** in the NARPS equal-indifference group under whole-brain family-wise error (FWE) control.” [Canonical capture `content/workspace/report.md`, SHA-256 `ffc6c016c1d28ebfa1e41b458d38c43a2cb3bb91337d083103ae7b271b964ce4`]

The original complete capture is SHA-256 `9cfe9198ef0910fbf826de24e1df2123bccbf2cb1f955899613e9e1774b6b490`, captured at 2026-10-16 15:28:19 UTC, with original HEAD `767f76ed3d12c3a7ff9fb23989358c768b301bc5`. All scientific citations below use capture-relative paths under `content/workspace/`. The operational manifest initially matched that canonical capture. The launcher reported no mismatch; its exact before/after verification bounded inspection to the supplied operational copy. Original external skill links listed in `judge-target.json` were not followed. Internal input links point into this capture's annex objects. The final operational-copy comparison found only inspection-induced changes to `.git/annex/keysdb/db` and creation of `.git/annex/keysdb/db-shm` and `db-wal`; all three are regular-file operational metadata paths. No non-metadata differences were found. This does not establish logical database equivalence; see `operational-delta.json`.

## Scientific assessment

The protocol uses the 54 supplied independent participant contrast estimates as the sampling units, tests an unweighted one-sample mean against zero, and uses 9,999 participant sign flips plus the observed arrangement for positive max-T inference across the whole common-support brain mask. The reported 23 positive FWE-significant voxels are outside the independently defined vmPFC proxy; none overlap it. The ROI mean is 0.0058 contrast units (95% t interval −0.0123 to 0.0239; t(53)=0.64; one-sided uncorrected p=.262). These results support a lack of corrected evidence for the regional hypothesis, not a claim of equivalence or absence.

The input metadata and maps are appropriate to the requested complete equal-indifference group. The analysis checks all 54 IDs against metadata and source checksums, grid shape and affine, and finite values. It intersects all map support with an independent MNI152 brain mask, retaining 186,400 voxels and dropping 9,720 brain-mask voxels lacking support in at least one map; this maintains a fixed n rather than filling missing voxels with zero. Map effects are correctly treated as participant contrast estimates rather than standardized statistics or currency-unit BOLD effects. The report explains that the gain modulator was centered and variance-normalized upstream, that gain and loss were modeled separately, and that participant variance maps are absent.

The vmPFC definition is an explicit, effect-independent Harvard–Oxford anatomical proxy (subcallosal plus frontal orbital cortex, |x|≤20 mm), not a universal vmPFC label. Whole-brain max-T correction meets the stated inference requirement. The sign-flip test assumes sign symmetry under the zero-mean null; the ordinary one-sample model does not weight participant precision. The report makes those assumptions and the limits of the fixed upstream model visible. It has participant-level and whole-brain figures, cluster and QC tables, machine-readable summaries, provenance, and retained failed/superseded attempts. The figures/results and analysis script are documented in `content/workspace/report.md` (SHA `ffc6c016c1d28ebfa1e41b458d38c43a2cb3bb91337d083103ae7b271b964ce4`), `content/workspace/protocol.md` (SHA `4b171cdf329b1a4b930da697bfed3fd18d27e2cb92a7d341c26b261c1f56c3e6`), `content/workspace/analysis/run_analysis.py` (SHA `c599f79d318aad3061edefc29ba1265096c2e20e5c1d9468d95fd139e3a21b92`), and `content/workspace/results/summary.json` (SHA `14c6d2b2bf5345576f4758037b840c24887aacf7c5548952ed467815c61af862`). The supplied upstream-model description is `content/workspace/input/upstream-methods.md` (SHA `508d832c8787ed8303c3de101c2c76f40a3aa5dec53e6993dc2a49c4b7bcf90b`). The whole-brain correction figure is `content/workspace/results/figures/whole_brain_fwe.png` (SHA `d605dab0940c1ee49ce8b2530f7c7e031f2a37558ea1b9093add6d7c480a0057`); participant ROI effects are `content/workspace/results/figures/roi_participant_effects.png` (SHA `406a498c38178aaab9c77c1e71e0f3b68d1ae2a40e308d788d6a3cba50a989e2`); and descriptive slices are `content/workspace/results/figures/mean_effect_slices.png` (SHA `fd37fba7434dbbd47a2ff41d17ccfa42b773c46e46216ce9a5f0a45f3a04d679`). QC and cluster tables are `content/workspace/results/participant_qc.tsv` (SHA `2017e8b0dc3ab3bdd9123c60dea1af4d240be484aa2af35bf5cefc2aabf9aa16`) and `content/workspace/results/cluster_summary.tsv` (SHA `e7d442a0b11ac97bc73946f35e67d11f8edbce0d6d8f00577c132c2ec30e7537`).

Replay was declared before execution in `replay-plan.md`. The frozen helper copied the complete canonical delivery, removed only 15 named generated outputs, and ran the README entrypoint once with a 7,200-second limit. It exited 0 in 22.27 seconds; all 15 outputs matched by SHA-256, including maps, tables, JSON, and figures. The replay record and stdout/stderr are retained in `replay/replay.json`, `replay/workdir/replay.stdout`, and `replay/workdir/replay.stderr`. It used the supplied local Python environment and existing atlas/cache; the adapter fetched no scientific inputs. This is evidence for rerunning the group analysis in that host scope, not evidence of worker publication or a clean environment reconstruction.

## STAMPED evidence and worker-stop attribution

The external frozen probes are preserved in `probes.json`. They inspect tracked Git paths and report several apparent absences because the worker's report, code, environment file, and results were untracked. I inspected the complete stopped workspace and overrode those tracked-only readings where the actual item asks whether instructions or an entrypoint exist. The probe's tree-clean finding is retained: the worker's HEAD is the supplied seed commit, while `README.md`, `analysis/`, `environment.yml`, `protocol.md`, `report.md`, and `results/` were untracked at stop (`git status --short --branch` in the operational copy). Thus Git existed and tracked the supplied inputs, but did not track the worker's scientific code, report, environment declaration, or results. Coordinator preservation and this assessment's replay do not earn worker versioning or publication credit.

At stop, `environment.yml` specified Python 3.13.16 and pinned versions for NumPy, SciPy, pandas, Matplotlib, NiBabel, and Nilearn, but it was untracked and did not freeze transitive resolution. `results/provenance.json` recorded software versions and input/atlas hashes but did not identify/hash a complete environment lock. README documents an absolute path to a shared prepared interpreter and says the environment file can be used for a task-local environment, without an install command or a worker-declared retrieval/publication route. Therefore packages and a usable start script are present in the complete workspace; exact environment capture, provenance linkage, portability, and worker sharing remain limited.

The intended access recipient is a researcher authorized to use the worker's declared route. No worker-declared retrieval route, remote, or publication record was found, so that route and its required artifact coverage could not be tested. The coordinator supplied this complete capture to the assessment; on this local host, the documented route successfully accessed all 54 input maps, metadata, source, and selected generated artifacts. That tests only the coordinator-provided capture and host environment, not worker access for another authorized recipient. The access details are in `access-record.json`.

Native session files `.codex/hooks.json` and `.entire/logs/` plus `.entire/metadata/` show coding-assistant activity was present in the retained delivery. This exposure is recorded without using its content or identifiers as grading evidence.

### Checklist verdicts

Pinned checklist version 0.3.1. Statuses are item-level; there is no aggregate score.

| Level | Item | Status | Evidence and rationale |
|---|---|---|---|
| MUST | 001 | met | Complete workspace is rooted in the captured project. |
| MUST | 002 | met | Maps, metadata, source and annex payloads are internally reachable. |
| MUST | 003 | met | `environment.yml` declares the runtime packages. |
| MUST | 004 | unmet | Worker analysis and outputs were untracked at stop. |
| MUST | 005 | met | 54 large image inputs use git-annex pointers and payloads. |
| MUST | 006 | partial | Provenance records versions but not the exact environment specification identity. |
| MUST | 007 | met | README contains usage and reproducibility instructions. |
| MUST | 008 | met | README points to `analysis/run_analysis.py`, replayed successfully. |
| MUST | 009 | met | Script uses paths relative to its own project root. |
| MUST | 010 | met | Environment file enumerates direct Python software dependencies. |
| MUST | 011 | partial | README documents a host-specific shared interpreter path; assumptions are not fully portable. |
| MUST | 012 | met | README and environment file identify the runtime and package requirements. |
| MUST | 013 | unmet | Environment specification, code, and outputs were untracked at stop. |
| MUST | 014 | unmet | No declared environment update process with tracked updates. |
| MUST | 015 | partial | Direct versions are pinned, but no transitive lock or complete environment capture is linked. |
| MUST | 016 | unmet | No worker publication/access route for the environment was declared. |
| MUST | 017 | partial | README explains the prepared interpreter and mentions a task-local environment, but gives no install command. |
| SHOULD | 001 | unmet | Git did not track the worker-created analysis and results. |
| SHOULD | 002 | not-checked | Attempt logs show iterations, not a regular testing process. |
| SHOULD | 003 | partial | Inputs, analysis code, results, and environment have separate locations, but no distinct component boundaries. |
| SHOULD | 004 | not-checked | Worker records do not establish a fresh-container, job, VM, or cloud test. |
| SHOULD | 005 | unmet | Documented run uses a shared prepared interpreter; no disposable environment is spawned. |
| SHOULD | 006 | not-checked | No worker record shows regular environment reconstruction. |
| SHOULD | 007 | partial | A direct-dependency environment file is present, but no complete environment artifact is archived. |
| SHOULD | 008 | unmet | No environment update process is declared (duplicate of must/014). |
| SHOULD | 009 | not-applicable | No restricted data or software component is identified. |
| MAY | 001 | not-applicable | No independently maintained project component requires a submodule/subdataset boundary. |
| MAY | 002 | met | README and protocol explain inputs, analysis, outputs, and how they relate. |
| MAY | 003 | partial | Inputs, code, and outputs can be updated separately, though the project has no formal module interface. |
| MAY | 004 | not-applicable | No independently maintained modules need composition. |
| MAY | 005 | met | README contents list and linked files support navigation. |

The failed/superseded run logs were retained. The final accepted run log is `content/workspace/results/attempts/accepted_run.log`; its summary and the machine-readable results are scientific artifacts, while coordinator preservation and the replay are assessor evidence only. Probe statuses and inspection disagreements are reflected item by item in `response.json` and `probes.json`.

## Access, replay, and record references

- Access scope: see `access-record.json`.
- Declared replay plan: `replay-plan.md`; attempt result: `replay/replay.json`.
- Frozen assessor check, probe, replay, and validation stdout/stderr: `commands/`.
- Checklist app link: `checklist-link.txt`.
- Scientific adequacy record: `scientific-judgment.json`.
- Response object capture: canonical delivery manifest SHA-256 `9cfe9198ef0910fbf826de24e1df2123bccbf2cb1f955899613e9e1774b6b490`; original captured HEAD `767f76ed3d12c3a7ff9fb23989358c768b301bc5`.
