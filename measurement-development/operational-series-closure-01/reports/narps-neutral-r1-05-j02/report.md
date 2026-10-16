# Independent assessment

Canonical capture SHA-256: 62fae7a1b4cf57bb811b88cb718ed01596b5d9b784e996e678b4851cadefbd0d  
Captured HEAD: afb62884c70115b6e46a92ddcd1d17bbf4f33544  
Worker stop receipt SHA-256: 2cbea3294b9b3c2e5985990c6c541f58aef039df1fd9e507cb685af2f2ccadb1  
Scope: complete stopped delivery, supplied metadata and results, declared retrieval route, frozen STAMPED probes, and one attempted frozen-helper replay. Original evidence citations identify the canonical capture digest and capture-relative paths.

## Scientific judgment

Scientific adequacy: supported.

The report's bounded conclusion is supported by the supplied maps and its group inference. It tests the positive mean of participant-level gain-effect estimates in the intended group, treats participants as independent units, and controls positive whole-brain voxelwise error with a one-sided maximum-t sign-flip procedure. It identifies vmPFC with an explicit coordinate display box without restricting the whole-brain search. No voxel in that box survives whole-brain correction; the observed box mean is slightly negative and its 95% interval crosses zero. The corrected positive islands are posterior, not vmPFC. The report correctly describes this as lack of evidence for a positive vmPFC effect, not evidence of exact zero or proof of absence.

The report and code clarify the estimand: supplied participant coefficients for a mean-centered, variance-normalized gain modulator, not a per-currency-unit sensitivity; gain and loss were fitted separately. The group model is unweighted because participant variance maps are absent. Sign-flip inference depends on symmetry under the null. Exact zero is treated as absent image support when constructing the common mask; the code checks matching shape and affine and finite values but does not independently validate that zero exclusively means no coverage. The coordinate box is an explicit approximation, not a universal anatomical boundary. These qualifications bound interpretation without overturning the stated regional conclusion.

Key captured evidence:
- content/workspace/REPORT.md (SHA-256 2431b4f9da678a818f62c0f056ce0a1e3fa209e3cb7892f037487ed936845601)
- content/workspace/protocol.md (SHA-256 57edbd99ff196301e14ffe50fbe634099241ce715762fef92fb125e3a3208042)
- content/workspace/scripts/group_analysis.py (SHA-256 6f2a4ba753982a2e29951eb762fdc9c0b21bb72dcbf703ce0c6daf111e33bfb6)
- content/workspace/results/summary.json (SHA-256 45174e412404231d9ce6c8be48b2864bbeb7c35e7963a47890699367a493fc78)
- content/workspace/results/fwe_clusters.csv (SHA-256 6478735dc6af6017f10251c55d4659b6e658d41ef9b3f7b708e0518c854d7fed)
- content/workspace/results/participant_qc.csv (SHA-256 2e6ef9d01087727849d9f72f5ce2f759203ba265e8f1ba2abcd7ff3e80f48da1)

Reported hypothesis outcome: “The supplied maps do not support a positive vmPFC gain effect in the NARPS equal-indifference group.” This is the report's conclusion, retained separately from the adequacy label.

## Scientific artifacts and analysis

The complete delivery contains 54 manifest-listed participant maps and 54 matching metadata rows. The code asserts unique IDs, exact ID set equality, the intended group label, common shape and affine, finite values, and a shared nonzero-support mask. It excludes no participant and reports per-map mean, standard deviation, nonzero fraction, and vmPFC-box mean. Results include mean, t and max-t FWE maps, a cluster table, participant QC, a summary, plotting source, PNG and SVG figures, input/code hashes, successful-run logs, and a retained failed attempt.

The report is appropriately cautious about participant-level uncertainty and upstream model limits. It reports 24 FWE-positive voxels in three posterior islands; the strongest coordinate is approximately (−26, −102, −3.6) mm. Eleven voxels also pass the Bonferroni reference, outside the vmPFC box. The box estimate is −0.00347 upstream units (95% CI −0.02293 to 0.01599), with zero whole-brain-FWE-positive box voxels. These are shipped outputs, not replay results. Figures and result files are present in the capture, although they were not regenerated in a successful replay.

## Delivery integrity and provenance

The canonical and initial operational manifests have the same SHA-256 identity (62fae7…fbd0d0), complete capture status, no manifest errors or omissions, and the same captured HEAD. The worker-stop receipt identifies the same capture. A post-inspection walk of all 1,201 workspace entries found no byte, path, link-target, or mode mismatches outside the specifically allowed annex keys database metadata. The regular files .git/annex/keysdb/db, db-shm, and db-wal changed or appeared and are recorded separately in integrity/operational-integrity.json; these inspection-copy metadata changes do not establish logical database equivalence. No captured scientific input, code, output, link, index, ref, object, or configuration mismatch was found.

The capture contains worker analysis files, generated maps, report and figures, but these were untracked at worker stop. The operational git status observation showed REPORT.md, protocol.md, data/, figures/, results/, run_analysis.sh, and scripts/ as untracked; the stop receipt inventory attributes the final workspace to worker stop. Captured HEAD is the starter/materialized-input commit, not a commit containing the analysis. Worker versioning/tracking credit is therefore limited to starter files and the 54 tracked annex pointers; later coordinator capture or retention does not establish worker commits or publication. The analysis code, report, results, figures, and generated data copies were outside Git at stop.

The worker-declared input route is the set of URLs in input/sources.json, implemented by scripts/retrieve_maps.py. A HEAD-only check tested all 54 NeuroVault image URLs on neurovault.org; all returned HTTP 200 and their manifest-declared content lengths. No map bytes were downloaded for this check. This route serves the 54 participant maps, not the worker report, analysis code, result maps, or environment specification. No worker-published repository or complete-object route is established by the captured .git/config or stop inventory. The intended recipient is a researcher using the declared authorized NeuroVault route; anonymous access was not required. Route details are in access/access-record.json.

The workspace contains .entire session log/metadata and .codex configuration artifacts indicating assistant tooling was present. Their contents and identifiers were not used as evidence for STAMPED or scientific judgments, and no assignment was inferred.

## Replay and measurement availability

The declared replay plan was bash run_analysis.sh in the frozen helper's new copy of the complete capture, using the worker-supplied common Python environment and existing data/ inputs. It selected only the three group NIfTI maps, fwe_clusters.csv, participant_qc.csv, and summary.json; the plan specified exact-byte checks for NIfTI/JSON and numeric CSV comparison at relative tolerance 1e-6. No source inputs or code were selected for removal. The plan and exact output list were recorded before execution in replay/replay-plan.md.

Replay is not checked. My first helper invocation mistakenly pre-created its required-new work directory. It failed before copying the capture or running the worker entrypoint. The frozen helper then refused a corrected invocation because its one-attempt allowance had already been consumed. The failed commands and outputs are retained under commands/replay*; the corrected invocation's stdout reports the allowance lock. No scientific replay ran, so no worker output is claimed as replay evidence and no scientific criterion is failed on this basis. This is an assessor setup/control limitation, not target execution failure or frozen-runner malfunction: my command pre-created a directory the helper requires to be new. The frozen runner check and probe actions completed; scientific conclusions rest on inspection of unchanged captured outputs.

## STAMPED checklist judgments

Verdicts concern worker stop state. Not-checked means available evidence does not establish attainment; it is not a negative scientific result. Evidence locations use capture://62fae7a1b4cf57bb811b88cb718ed01596b5d9b784e996e678b4851cadefbd0d/<capture-relative-path>, unless marked as a probe observation or assessment artifact. No aggregate score is assigned.

| Item | Status | Reason and evidence |
|---|---|---|
| must/001 | met | Workspace contents share the project root; input and analysis are nested there. content/workspace/input/sources.json; content/workspace/REPORT.md. |
| must/002 | met | Inputs resolve through annex content and manifest-listed URLs plus retrieval code; all 54 URLs responded with expected lengths. content/workspace/input/sources.json; content/workspace/scripts/retrieve_maps.py; access/access-record.json. |
| must/003 | unmet | Analysis depends on external Python packages, but the project includes no environment or linked software component containing them. content/workspace/scripts/group_analysis.py; capture inventory. |
| must/004 | unmet | Worker analysis, code, results, figures, and downloaded map copies were untracked at stop. Operational observation: probe:tree-clean; stop receipt; content/workspace/REPORT.md. |
| must/005 | met | The 54 supplied scientific input maps are annex pointers with retained annex content. content/workspace/input/data/; probe:large-in-annex. |
| must/006 | unmet | Run records and summary give versions but no exact specification linked to the run. content/workspace/results/summary.json; content/workspace/results/run.stdout; no environment lock in capture. |
| must/007 | unmet | No README or Makefile is present. The report documents use but does not supply the requested README/Makefile. content/workspace/REPORT.md; probe:entry-point. |
| must/008 | met | bash run_analysis.sh is a clear documented starting point and invokes retrieval and group analysis. content/workspace/REPORT.md; content/workspace/run_analysis.sh. |
| must/009 | unmet | The entry script defaults to a host-specific absolute Python path, despite allowing a PYTHON override. content/workspace/run_analysis.sh. |
| must/010 | unmet | No dependency/environment specification captures Python dependencies. The summary records versions, but not an installable specification. content/workspace/results/summary.json; content/workspace/scripts/group_analysis.py. |
| must/011 | partial | Summary records macOS and package versions and the runner reveals the fixed common-environment path, but host setup requirements are not clearly documented. content/workspace/results/summary.json; content/workspace/run_analysis.sh; content/workspace/REPORT.md. |
| must/012 | unmet | No clear system requirements and dependency list is supplied. content/workspace/REPORT.md; content/workspace/run_analysis.sh. |
| must/013 | unmet | No environment specification is tracked with code and data. Capture inventory; probe:env-spec-tracked. |
| must/014 | unmet | No environment specification or update process is supplied. Capture inventory; content/workspace/REPORT.md. |
| must/015 | unmet | Recorded package versions are not an exact frozen environment or container identity. content/workspace/results/summary.json; capture inventory. |
| must/016 | unmet | No worker-shared environment specification or published environment artifact is recorded. Capture inventory; content/workspace/.git/config. |
| must/017 | unmet | No environment specifications exist to obtain or use. content/workspace/REPORT.md; capture inventory. |
| should/001 | partial | Git and annex cover starter inputs, but worker analysis code, report, results and generated map copies were outside version control at stop. content/workspace/input/data/; probe:tree-clean; stop receipt. |
| should/002 | not-checked | One successful run and a retained failed attempt do not establish regular testing or cadence. content/workspace/results/run.stdout; content/workspace/results/attempts/README.md; probe:ci-present. |
| should/003 | partial | Inputs, scripts, results and figures have separate directories, but environment is absent and much of the organization was untracked. content/workspace/input/; content/workspace/scripts/; content/workspace/results/; content/workspace/figures/. |
| should/009 | not-applicable | No restricted data or software is identified in supplied study inputs. content/workspace/input/study-task.md; content/workspace/input/participants.tsv. |
| should/004 | not-checked | A fresh-container/VM run is not established; this assessment replay did not execute. content/workspace/results/summary.json; replay/replay-plan.md; commands/replay-01.stderr. |
| should/005 | not-checked | No disposable-environment workflow is supplied. content/workspace/run_analysis.sh; content/workspace/REPORT.md. |
| should/006 | not-applicable | No exact environment specification exists to reconstitute and test. Capture inventory; probe:run-env-linked. |
| should/007 | unmet | No archived environment artifact is supplied. Capture inventory; content/workspace/REPORT.md. |
| should/008 | unmet | No process for updating a dependency specification is supplied. Capture inventory. |
| may/001 | not-applicable | No separately maintained submodule/component exists; annexed study inputs are data, not software. Probe:subdatasets-resolvable; content/workspace/input/sources.json. |
| may/002 | partial | Report links inputs, code, results and figures, but does not explain independently recombinable module boundaries. content/workspace/REPORT.md; content/workspace/protocol.md. |
| may/003 | partial | Input and analysis paths are separated, but analysis expects fixed relative paths and no independent module interface is documented. content/workspace/scripts/group_analysis.py; content/workspace/run_analysis.sh. |
| may/004 | met | Entry script composes retrieval and analysis in sequence. content/workspace/run_analysis.sh. |
| may/005 | met | Report links protocol, code, manifest, results, QC and figures. content/workspace/REPORT.md. |

## Assumptions and scope limits

Retained original links to external or absolute skill targets were not followed, consistent with judge-target.json reference limits. No commands were run against the canonical capture. Git and annex inspections targeted only the operational copy and preserved GIT_OPTIONAL_LOCKS=0, annex.merge-annex-branches=false, and annex.alwayscommit=false. Coordinator retention activity is not treated as worker publication or version-control evidence. All findings remain conditional on supplied upstream AO86 maps and methods; time-series scans and participant variance maps were not supplied or requested.
