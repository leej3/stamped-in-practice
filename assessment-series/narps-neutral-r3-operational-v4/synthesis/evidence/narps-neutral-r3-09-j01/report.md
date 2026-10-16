# Independent assessment

## Identity and integrity

This assessment refers to canonical capture SHA-256 `794cdbd43e94970c2643887f261be89131d348e93c742f67f737491d9e2abfc1` and original captured HEAD `82443e43a1171f47c085c5e0fadc9e8132a12053`. The worker-stop receipt (SHA-256 `304303180d8b2361a1e12a948d9102c1139ec9ab1d6386445f143a44f5988e7e`) records an exited worker with no omissions. I assessed the operational copy against that complete stopped delivery, including its untracked scientific files.

A read-only exact inventory comparison checked 1,102 captured workspace entries. It found one hash difference, `.git/annex/keysdb/db`, and two additional regular files, `.git/annex/keysdb/db-shm` and `db-wal`. These are all within the specifically classified operational metadata; they are not evidence of worker changes or proof of logical database equivalence. No other content, path, type, symlink-target or mode mismatch was found. Git status confirms the report, analysis code, environment file, figures and results were untracked at worker stop; `.codex/` and `.entire/` are ignored. Probe and Git inspection are assessor observations, not worker evidence. No other mismatch was observed.

## Scientific judgment

**Scientific adequacy: qualified.** The report's conclusion is: “the supplied gain-effect estimates do not support a positive vmPFC response to increasing potential gain under whole-brain family-wise error correction.” The distinction is appropriate: this is no corrected support, not evidence of a zero effect.

The analysis uses all 54 equal-indifference participants, matches maps by participant ID, verifies source checksums, shape and affine, and treats each unthresholded cope as a participant-level effect estimate. It correctly explains that the upstream gain modulator was mean-centered and variance-normalized, so estimates are not a per-currency-unit slope, and notes that the supplied data omit first-level variance maps and the executable upstream pipeline (`input/upstream-methods.md`; `analysis/run_group.py`; `REPORT.md`). The reported geometry is consistent with MNI152NLin2009cAsym, and the broad vmPFC coordinate envelope is specified before inference. The primary test is a positive one-sample t field with 5,000 participant-level sign flips and a whole-support max-t threshold, rather than an ROI-only test. Reported significant voxels are posterior and do not overlap the envelope; a descriptive ROI mean and interval are provided. An independent numerical validation agrees on participant count, mask size, ROI summary, max-t threshold and significant-voxel count (`results/group_results.json`; `results/independent_validation.json`).

The qualification reflects inferential limits rather than a detected arithmetic error: the common-support mask is defined from finite nonzero values rather than an independent brain mask; sign-flip inference assumes independent participants and a symmetric null; and the broad coordinate box is only an approximate anatomical localization. The report identifies these limits and avoids interpreting the posterior findings as vmPFC evidence. The conclusion is adequately bounded to the supplied group estimates and fixed upstream choices. The task's gain-to-loss range context is not converted into an unsupported gain-versus-loss comparison.

The one frozen replay attempt used the documented command `python analysis/run_group.py --permutations 5000 --seed 20261016`, with outputs explicitly limited to the group JSON, permutation table, three NIfTI maps and three figures. The documented prerequisite was Python 3.13 plus the supplied `requirements.txt`; the declared comparison tolerance was relative `1e-6` for selected outputs, with timestamps/runtime fields treated as non-scientific. The entrypoint also writes `results/participant_qc.tsv`, which was not in the selected output list; because the command failed during import before writing any outputs, that omission did not cause a target change, but the replay measurement would not have covered that diagnostic file. The fresh complete-delivery replay copy failed before analysis at `import nibabel` (`ModuleNotFoundError`); no dependency installation or retry was made. Replay is therefore unmet as a reproduction measurement, not a scientific falsification. Preexisting output files are considered inspection evidence only, not replay evidence.

## STAMPED item judgments

The frozen probes are retained in `probes.json`. I considered their results alongside the actual files and worker-stop inventory; automated probe coverage is incomplete and does not override direct evidence.

| Item | Verdict | Basis |
|---|---|---|
| must/001 | met | Workspace artifacts share the repository root. |
| must/002 | met | Input maps and metadata are included under `input/`; analysis resolves paths relative to its root. |
| must/003 | met | Python dependencies are explicitly listed in `requirements.txt`. |
| must/004 | unmet | Git exists, but the scientific report, code, environment declaration, figures and results were untracked at stop. |
| must/005 | met | Large participant maps use git-annex at stop. |
| must/006 | partial | Results record runtime and package versions, but do not link the run to an immutable environment artifact. |
| must/007 | met | `analysis/README.md` documents installation and usage, though there is no root README. |
| must/008 | met | README and report identify `analysis/run_group.py` and exact commands. |
| must/009 | met | Analysis paths are derived from `__file__`; no hardcoded host paths were found. |
| must/010 | met | `requirements.txt` pins direct Python dependencies. |
| must/011 | partial | Runtime OS/architecture are recorded in results, but host assumptions are not comprehensively declared. |
| must/012 | met | README states Python 3.13; requirements lists the Python packages. |
| must/013 | unmet | The environment file was untracked at worker stop. |
| must/014 | unmet | No environment update process is documented. |
| must/015 | partial | Direct dependencies are pinned, but no lockfile captures a complete platform-specific environment. |
| must/016 | unmet | No worker-declared route for obtaining an archived or published environment was found. |
| must/017 | met | `analysis/README.md` explains how to install and use the requirements file. |
| should/001 | partial | Git/git-annex are used, but scientific files were not tracked at stop. |
| should/002 | partial | Pilot and independent numerical validation exist; no regular automated test process is documented. |
| should/003 | met | Inputs, analysis, results and figures are in distinct directories. |
| should/009 | not-applicable | No restricted data or software is identified. |
| should/004 | not-checked | No worker evidence of a fresh-container, batch or clean-VM test. |
| should/005 | not-checked | No disposable execution environment is documented. |
| should/006 | not-checked | The exact environment was not reconstituted in the one permitted replay. |
| should/007 | unmet | No archived environment artifact is included. |
| should/008 | unmet | No tracked environment update process is documented. |
| may/001 | not-applicable | No software/data submodule mechanism is used. |
| may/002 | partial | Directory structure separates components, but relations are only lightly documented. |
| may/003 | not-checked | Independent module update boundaries are not established. |
| may/004 | not-applicable | Workflow composition does not use separate modules requiring a composition mechanism. |
| may/005 | partial | README and report provide navigation to the main analysis artifacts. |

No overall score is assigned.

## Access record

Intended recipient: a researcher authorized to use the project and its inputs. Worker-declared route: none found; the captured Git configuration has no remote, and the source URLs in `input/sources.json` identify upstream inputs rather than a route to this completed research object. Required coverage is the report, analysis code, `requirements.txt`, all supplied inputs, figures and results. A route to retrieve that complete set could not be tested on any host. Coordinator retention/delivery of the captured object does not establish worker publication or accessibility.

## Scope and exposure

The nine absolute skill links listed in `judge-target.json` reference limits were not followed; their retained symlink objects were inspected only as paths/metadata. No treatment assignment was inferred or reported. The task-specific STOP receipt establishes supplied capture identity; this assessment used no prior judgment or other worker output.
