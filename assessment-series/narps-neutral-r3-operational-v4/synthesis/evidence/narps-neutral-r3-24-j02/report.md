# Independent assessment — NARPS Hypothesis 1

Assessment date: 2026-10-16. Project kind: computational study. Scope: complete stopped delivery, including uncommitted and ignored files; scientific assessment conditional on supplied group-stage participant maps.

## Scientific adequacy and conclusion

**Scientific adequacy: supported.** The report's conclusion that the supplied analysis does not support a positive vmPFC gain response at whole-brain corrected significance is supported by its stated model and results. The reported outcome is: “In the 54 equal-indifference participants, the supplied gain-effect maps do **not support a positive vmPFC response** at the required whole-brain-corrected level.” This is an absence of corrected support, not evidence that the effect is exactly zero.

The worker uses all 54 equal-indifference participants and describes source checksum, finite-value, image-grid and coverage checks (`analysis.py`, `results/participant_qc.tsv`, `input/participants.tsv`). The group model is a one-sample, positive one-sided voxelwise t test over the intersection of common nonzero supports, with Bonferroni familywise correction across 198,029 voxels. The report separates the broad Harvard–Oxford medial/subcallosal/orbital vmPFC proxy from whole-brain inference. It reports no corrected voxel in that proxy; corrected positive voxels are occipital. Its ROI-only p value is explicitly secondary and uncorrected. This follows the task's whole-brain requirement and avoids treating an ROI-only result as confirmatory.

The scientific conclusion is appropriately limited. The supplied images are first-level contrast estimates, not test statistics; gain coefficients are not per-currency response slopes because the upstream modulator was centered and variance-normalized. Participant variance maps are absent, so the unweighted group t test cannot incorporate first-level precision. Independent participants, approximate group-level normality, and the chosen atlas proxy remain assumptions/limitations. The report explains that a null vmPFC result does not establish a zero effect. The broad atlas proxy and cluster labeling are inspectable in `analysis.py`, `results/results.json`, `results/whole_brain_fwe_clusters.tsv`, and the three figures. The code says the atlas labels were selected before result inspection, but no dated preregistration or independent plan establishes that timing.

## STAMPED assessment

**MUST: 5 met / 0 partial / 12 unmet / 0 not-checked / 0 not-applicable (17 items).**  
**SHOULD: 1 met / 1 partial / 3 unmet / 4 not-checked / 0 not-applicable (9 items).**  
**MAY: 1 met / 1 partial / 0 unmet / 0 not-checked / 3 not-applicable (5 items).**

### Highest-priority improvements

1. Add a tracked environment specification with pinned dependencies and a reproducible update command; the analysis imports NumPy, SciPy, NiBabel, pandas, Matplotlib and Nilearn, and Nilearn fetches atlas/template resources at run time. This closes must/003, must/010–017 and should/006–008.
2. Track the analysis script, report, notebook and results in Git or an equivalent history. At worker stop they were untracked, so the captured HEAD did not identify the delivered analysis. This closes must/004 and strengthens should/001.
3. Add installation, usage and output instructions, including the need for network access or a retained atlas/template copy. The report identifies `analysis.py` but gives no setup instructions. This closes must/007.
4. Record the analysis invocation, output set and exact environment alongside results. Current result tables summarize the model but do not bind the run to an environment. This closes must/006.
5. State reuse terms and any restricted-data status. No license is declared, so downstream reuse rights are unclear.

### What is already strong

- Group-level inference is aligned with the positive vmPFC hypothesis and whole-brain correction, and the output explicitly distinguishes corrected whole-brain findings from the secondary ROI-only result (`report.md`, `analysis.py`, `results/results.json`).
- The inputs are retained through Git-annex, while per-participant QC and checksums make the supplied maps and cohort visible (`input/sources.json`, `results/participant_qc.tsv`).
- The report interprets the maps as first-level parameter estimates, explains the gain-scaling and variance-map limitations, and avoids interpreting non-significance as proof of zero (`report.md`, `input/upstream-methods.md`).

### Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `report.md`, `input/participants.tsv` | All supplied artifacts are nested under the common project root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `input/data/sub-001_hypo1_cope.nii.gz` | The participant inputs are included and resolve to annex objects inside the common root. |
| must/003 | S.1 | unmet | judgement | `analysis.py` | External analysis packages are neither declared in an environment spec nor supplied as project modules. |
| must/004 | T.1,T.3,T.5 | unmet | probe:tree-clean | `analysis.py`, `report.md`, `results/results.json` | The stopped HEAD omits the untracked analysis, report, notebook and results. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data/sub-001_hypo1_cope.nii.gz`, `input/sources.json` | Git-annex carries the 54 participant map contents. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `results/results.json`, `analysis.py` | The delivered results are not linked to a recorded exact environment or execution record. |
| must/007 | A.1 | unmet | probe:entry-point+judgement | `report.md` | No installation and usage instructions are supplied. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analysis.ipynb`, `report.md` | The notebook calls analysis.py from the project root, and the report identifies it as the reproduction script. |
| must/009 | P.1 | met | probe:no-abs-paths | `analysis.py`, `analysis.ipynb` | Analysis paths are derived from the script location or project root, not a user-specific absolute path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `analysis.py` | No environment specification lists the imported dependencies. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `analysis.py`, `report.md` | The analysis fetches atlas/template resources and requires network access, but host assumptions are undocumented. |
| must/012 | P.2 | unmet | probe:platform-assumptions+judgement | `analysis.py`, `report.md` | No README, environment file or equivalent dependency list states system requirements. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `analysis.py` | No environment specification is present in the delivered workspace. |
| must/014 | P.3 | unmet | judgement | `report.md`, `analysis.py` | No runnable process for updating and tracking environment specifications is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked | `analysis.py` | No frozen package manifest, container digest or other exact environment specification is included. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `report.md` | There is no environment specification to publish or share. |
| must/017 | D.1 | unmet | judgement | `report.md` | The report gives no instructions for obtaining or using an environment specification. |
| should/001 | T.2 | met | probe:large-in-annex+judgement | `.git/config`, `input/data/sub-001_hypo1_cope.nii.gz` | Git and Git-annex are used in the same workspace for source files and participant data. |
| should/002 | A.2 | not-checked | probe:ci-present | `report.md` | No regular test history is supplied; worker test records would settle this. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/participants.tsv`, `results/results.json`, `analysis.py` | Input and results directories separate data and outputs; code and environment are not separate modules. |
| should/004 | E.1 | not-checked | judgement | `report.md` | No fresh-container, clean-VM, batch or cloud test record is supplied. |
| should/005 | E.1 | not-checked | judgement | `analysis.ipynb` | No disposable-environment-per-run mechanism is documented. |
| should/006 | D.2 | unmet | probe:run-env-linked+judgement | `analysis.py`, `report.md` | No exact environment specification exists to reconstitute or test against. |
| should/007 | D.2 | unmet | probe:env-spec-tracked | `analysis.py` | No environment artifacts are archived in the research object. |
| should/008 | D.2 | unmet | judgement | `report.md` | No environment update process is declared; this repeats must/014 by checklist design. |
| should/009 | M.4 | not-checked | judgement | `input/sources.json` | Sources are identified, but restriction status is not declared; a restriction/access inventory would settle this. |
| may/001 | M.2 | not-applicable | judgement | — | N/A: external inputs are bundled in the study root; no separately composed project component is identified. |
| may/002 | M.2 | partial | judgement | `report.md` | The report names inputs, code and results, but does not document how separate modules can be recombined. |
| may/003 | M.2 | not-applicable | judgement | — | N/A: no independently updateable project modules are declared. |
| may/004 | M.2 | not-applicable | judgement | — | N/A: no separate modules require a composition mechanism. |
| may/005 | M.2 | met | judgement | `report.md` | The report maps the named input, analysis and output artifacts to their project paths. |

### Flagged items

- `must/002`: the subdataset probe returned not-checked because there are no submodules; complete-delivery inspection found all participant maps linked to annex objects inside the workspace.
- `must/006`: the derived-record probe returned not-applicable based on tracked HEAD only; complete delivery contains untracked scientific results without environment-linked execution records.
- `must/008`: the entry-point probe missed the untracked analysis files; the complete delivery documents `analysis.py` in the notebook and report.
- `must/011` and `must/012`: the platform probe searched command tokens, not host assumption documentation or dependency lists; inspection found runtime network retrieval and no setup requirements.
- `should/006`: the run-environment probe was not-checked; inspection found no exact environment specification to reconstitute.
- `should/008`: this duplicates must/014 in the pinned checklist.


### Access, replay and attribution

The intended recipient is a researcher authorized to use the materials. No worker-declared route to retrieve this research object was found or tested, and its required artifact coverage for an outside recipient and tested host scope are therefore unknown. The URLs in `input/sources.json` document sources for inputs; they are not a route for obtaining the analysis object. See `access-record.json`.

Replay is **not checked** (zero attempts). The report and notebook document `python analysis.py` as the entrypoint, and the script explicitly names its generated result files. However, no installation instructions or environment declaration are present, and the script imports third-party packages and fetches atlas/template assets. I did not use the assessor environment to fill those gaps or initiate retrieval. The shipped outputs remain inspected worker artifacts, not replay evidence. See `replay-record.json`.

The worker-stop receipt identifies a complete capture with no omissions and HEAD `0acda2e09b35799b07d22052122402c9e54c8965`; the canonical capture SHA-256 is `35c62952400477cd4e8cc48fc293e6bebc488198068bd8c8c2ed60ac3b683048`. At that stop, `analysis.py`, `analysis.ipynb`, `report.md`, `results/` and `.codex/` were untracked; the code and scientific report/results therefore were not represented by the captured HEAD. The 54 map pointer paths resolve inside the captured `.git/annex/objects` store. The Git configuration records a hooks path outside the object; it was inspected as captured text and not followed. No integrity mismatch was observed in the initial canonical/operational manifest identity; final target integrity is subject to the launcher's post-assessment verification. Any inspection-induced annex database metadata is not treated as worker evidence.

The commit metadata contains a Codex co-author identifier, which is recorded here solely as assistance exposure. It was not used as evidence for any verdict. Supplied coordinator materials, this assessment, and coordinator preservation do not earn worker-practice credit.

### Not checked and limitations

- `should/002`, `should/004` and `should/005`: no regular test history, fresh-host test or disposable-environment record was established. Test/release records from the worker would settle these.
- `should/009`: source URLs identify upstream data, but no restriction declaration is present; an access/restriction inventory would settle this.
- Scientific conclusions are conditional on the supplied participant maps and their upstream fixed model. No first-level variance maps were supplied; no original task-time-series or preprocessing inference was assessed.
- The independent scientific replay was not attempted for the dependency/prerequisite reason above; the shipped code and outputs were reviewed but not independently regenerated.

### Goals and checklist record

The stated goal, from the retained task brief and `input/study-task.md`, is group-stage inference for the positive potential-gain effect in vmPFC in the equal-indifference cohort, using supplied participant maps and whole-brain correction. This is a computational study; portability and provenance of its analysis and results are central. Item-level verdicts, evidence, and the generated checklist-app URL are in the response record and [checklist link](checklist-url.txt). The machine-readable scientific judgment is in `scientific-judgment.json`.

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the complete original capture SHA-256 `35c62952400477cd4e8cc48fc293e6bebc488198068bd8c8c2ed60ac3b683048`, original HEAD `0acda2e09b35799b07d22052122402c9e54c8965`, captured 2026-10-16; harness: OpenAI Codex; model identifier was not exposed by the frozen assessment runtime. Probe output: `probes.json`.
