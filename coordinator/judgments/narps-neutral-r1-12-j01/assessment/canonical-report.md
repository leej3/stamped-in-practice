# Independent assessment: NARPS Hypothesis 1

**STAMPED verdicts:** MUST: 4 met / 4 partial / 9 unmet / 0 not-checked (17). SHOULD: 1 met / 1 partial / 4 unmet / 2 not-checked / 1 not-applicable (9). MAY: 3 met / 1 partial / 0 unmet / 0 not-checked / 1 not-applicable (5). No overall score is assigned.

## Scientific assessment

**Scientific adequacy: qualified. Reported hypothesis outcome: not supported by this analysis.** This is a sound whole-brain group test for the supplied fixed participant estimates, and the report correctly treats a non-significant vmPFC finding as lack of evidence under the stated criterion rather than evidence of a zero effect. The conclusion is bounded to these 54 maps, their upstream model, the tested common support, and the stated vmPFC coordinate zone.

The analysis verifies all 54 inputs against checksums, checks finite values and common shape/affine, retains all 54 equal-indifference participants, and excludes zero-valued locations from the intersection support instead of treating missing coverage as an observed zero. It tests a one-sample group mean in the positive direction and controls voxelwise whole-brain familywise error with a participant sign-flip max-T null. The 5,000 permutations yield a reported resolution of 1/5,001. This is defensible under the stated symmetry/exchangeability assumption, which the report discloses.

The reported maximum is t(53)=6.62 at MNI [−26, −102, −3.6] (max-T FWE p=.001); the vmPFC coordinate box has no whole-brain corrected voxels, a maximum t=4.19 below the 5.397 threshold, and mean estimate −0.00048 (95% t interval −0.0143 to 0.0133). The box is a transparent approximation rather than an atlas-defined anatomical boundary, and the inputs lack first-level variance maps; both limit precision and generalization. The report also correctly notes that upstream gain scaling was normalized and that these coefficients are not currency-unit effects. The appropriate interpretation is “the tested analysis does not support a positive vmPFC effect,” not “the effect is absent.”

Evidence: [report](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-12-j01/content/workspace/report.md), [analysis code](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-12-j01/content/workspace/analysis.py), [machine-readable results](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-12-j01/content/workspace/results/results.json), [participant table](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-12-j01/content/workspace/results/included_participants.tsv), [corrected clusters](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-12-j01/content/workspace/results/fwe_clusters.tsv), [figure](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-12-j01/content/workspace/results/figures/group_gain_effect.png), and [upstream methods](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-12-j01/content/workspace/input/upstream-methods.md). Input integrity was assessed using the unchanged delivery, whose manifest check is recorded below.

## Highest-leverage improvements

- Add a portable, exact environment specification and an install/run guide → lets another researcher obtain and reconstruct the analysis environment (must/003, 007, 010–017).
- Track the analysis, notebook, report and generated results in the worker’s version history, and remove the notebook’s absolute interpreter path → makes the delivered scientific result versioned and portable (must/004, 009).
- Link a completed run record to the exact environment, command, inputs and outputs → strengthens provenance and supports independent reruns (must/006; should/004, 006).

## What is already done well

- The complete delivered bytes, including annex objects, matched the coordinator’s signed inventory: 1,099 workspace entries checked; no mismatches, omissions or capture errors. See [verification record](delivery-verification.json) and [delivery manifest](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-12-j01/manifest.json).
- The scientific report includes a concise methods/results narrative, uncertainty and upstream limitations, with code and inspectable maps/tables/figure.
- Git-annex stores the large participant maps, while project inputs and derived results occupy distinct directories.

## Delivery and worker-stop attribution

The capture is marked complete. The worker stop receipt records exit code 0 and HEAD `e929d623d8de313d2ecdd97911ea8487077af580`; the manifest hash matches the `judge-target.json` capture hash. The scientific report, notebook, analysis script, and results directory were present but untracked at worker stop. The coordinator’s later preservation is not credited as worker tracking or publication.

No worker-declared project retrieval/publication route was found, so no remote route was available to check. The recipient considered is a researcher using the declared authorized route. Required coverage would include code/notebook, report/figures, results, maps/metadata, and an environment specification. The coordinator-local target was readable; no remote host or worker-authorized route was tested. See [access record](access-record.json). The [worker stop receipt](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/worker-end-state.json) is distinct from the [manifest verification](delivery-verification.json).

A notebook cell contains an absolute path to an external Python interpreter. I did not follow that path. No dependency specification is supplied. A `.task_skills/jupyter-notebook` path indicates a skill/resource exposure; it is recorded here only and was not used as grading evidence. No other assistance exposure was identified in inspected scientific files.

## Replay record

Replay was **not checked**, with zero attempts. The documented command is `python analysis.py --permutations 5000 --seed 20261016`. `analysis.py` identifies the generated results files listed in [replay-record.json](replay-record.json); the planned comparison is numerical with rtol 1e-6 for scientific outputs, excluding timestamps/log prose and figure encoding. The required Python packages and versions cannot be reconstructed from worker-supplied declarations, and the notebook’s external absolute interpreter path cannot be followed. No substitute environment was created. Thus replay is unavailable, not a target failure. The frozen limit was one attempt, 7,200 seconds and 5 GB retrieval.

The assessor runner’s `check` output matched the frozen version pin. No assessor malfunction occurred. The probe output is retained at [probes.json](probes.json); it searches recognized tracked formats and was therefore supplemented by direct inspection of the complete delivery. The [validated response](2026-10-16-response.json), [checklist URL](2026-10-16-url.txt), [access record](access-record.json), [replay record](replay-record.json), and [item table](item-table.md) are outside the target.

## Goals and kind assumption

The supplied task and report define the goal as group-level inference for the positive potential-gain effect in vmPFC using the fixed 54 participant maps. I assume the object kind is a **study**: it combines scientific inputs, analysis, results and interpretation. No human confirmation was attached; the assumption follows the retained task brief and worker report.

The captured `.git/config` also names a host-specific absolute `core.hooksPath`. That configuration was inspected as evidence and left unchanged. No Git hook or external path was run.

## Per-item checklist
| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/delivery-verification.json` | All captured workspace files, including the annex object store, are inside the workspace root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `analysis.py`, `input/data/`, `input/sources.json` | The 54 supplied maps and metadata are reachable through in-root annex links used by the relative-path analysis. |
| must/003 | S.1 | unmet | judgement | `analysis.py`, `results/results.json` | Python, NumPy, SciPy, pandas, nibabel and matplotlib are not declared in a delivered environment or linked module. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/worker-end-state.json` | Git tracks some inputs/configuration, but analysis, report, notebook and results were untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | judgement | `input/data/`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/delivery-verification.json` | The 54 large input maps use git-annex pointers with in-root annex content. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/results.json`, `report.md` | Results record parameters, input hashes and package versions, but no exact environment is linked to a completed run record. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `report.md`, `analysis_notebook.ipynb` | The report gives usage and a run command, but no installation instructions or dependency setup. |
| must/008 | A.1 | met | probe:entry-point+judgement | `report.md`, `analysis.py` | The report names analysis.py as the entry point and states the command to reproduce outputs. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `analysis.py`, `analysis_notebook.ipynb` | The main script uses relative paths, but the executable notebook hardcodes a host-specific absolute Python path. |
| must/010 | P.1 | unmet | judgement | `analysis.py`, `report.md` | No delivered dependency specification covers the imported Python packages. |
| must/011 | P.1 | unmet | judgement | `analysis_notebook.ipynb`, `report.md`, `.git/config` | The required host and runtime assumptions are not specified; the notebook relies on one absolute host path. |
| must/012 | P.2 | unmet | judgement | `report.md`, `analysis.py` | There is no clear installation or system-requirement list for the analysis dependencies. |
| must/013 | P.3 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/delivery-verification.json`, `analysis.py` | No environment specification is included alongside the code and data. |
| must/014 | P.3 | unmet | judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/delivery-verification.json` | No environment update or lockfile regeneration process is declared. |
| must/015 | D.1 | unmet | judgement | `results/results.json`, `analysis_notebook.ipynb` | No frozen package manifest, container digest or equivalent exact environment is supplied. |
| must/016 | D.1 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/worker-end-state.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/delivery-verification.json` | No worker-shared environment specification or archive is identified. |
| must/017 | D.1 | unmet | judgement | `report.md`, `analysis_notebook.ipynb` | The report does not tell readers how to obtain or reconstruct the referenced Python environment. |
| should/001 | T.2 | met | judgement | `.git/config`, `input/data/` | Git covers project text/configuration and git-annex covers the large maps within one repository. |
| should/002 | A.2 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/probes.json` | No recurring test history or equivalent schedule is available; a test record would settle this. |
| should/003 | M.1 | partial | judgement | `input/`, `results/`, `analysis.py` | Inputs and generated results are separated, but code sits at root and no environment module exists. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/replay-record.json` | No fresh-container/VM run was recorded, and replay prerequisites are unavailable; a clean-host execution record would settle this. |
| should/005 | E.1 | unmet | judgement | `analysis.py`, `report.md` | The workflow does not create disposable or isolated environments for each run. |
| should/006 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/delivery-verification.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/probes.json` | No exact environment specification exists to reconstitute and test. |
| should/007 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/delivery-verification.json` | No environment artifact is archived in the research object. |
| should/008 | D.2 | unmet | judgement | `report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/delivery-verification.json` | No declared dependency-update process exists to track. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the captured project declares no restricted data or software; supplied maps and metadata are included. |
| may/001 | M.2 | not-applicable | judgement | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-12/judgments/narps-neutral-r1-12-j01/attempt-01/judgment/delivery-verification.json` | N/A: the project has no independently maintained external project components; packages are runtime dependencies. |
| may/002 | M.2 | met | judgement | `report.md` | The report explains how input maps, analysis code and results fit together. |
| may/003 | M.2 | partial | judgement | `input/`, `results/`, `analysis.py` | Input and result directories are distinct, but code and environment are not independent components. |
| may/004 | M.2 | met | judgement | `analysis.py` | analysis.py directly composes the input maps into group inference and writes the results. |
| may/005 | M.2 | met | judgement | `report.md` | The report documents the entry point and identifies the input and results locations. |


## Flagged items

- **must/002:** the subdataset probe could not identify data linked through annex symlinks; direct inspection found all 54 inputs reachable within the root.
- **must/004:** the tree-clean probe measured uncommitted paths. Direct inspection established that the key deliverables were untracked, so versioning is partial rather than wholly absent.
- **must/007:** the entry-point probe only recognized README/Makefile routes; the report provides usage instructions, but no installation route, so the item is partial.
- **must/008:** the probe missed the untracked script; the report documents it as a start point, so the item is met.
- **must/009:** the probe scanned tracked text only; the untracked notebook includes a host-specific absolute interpreter path, so the item is partial.

## Not checked

- **should/002:** repeated/manual test history was not available in the stopped delivery; a recurring run record or schedule would settle it.
- **should/004:** no clean-container/VM execution record exists, and the replay prerequisite could not be reconstructed; a documented clean-host run would settle it.

---

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (stamped-checklist-schema@v0.3.1, af259bad), on the captured study at commit `e929d623d8de313d2ecdd97911ea8487077af580`, 2026-10-16, Codex API/GPT-6. Frozen runner pin: [assessment-version-check.json](assessment-version-check.json). Probe output: [probes.json](probes.json). Response: [2026-10-16-response.json](2026-10-16-response.json).

