# Independent assessment: NARPS potential gains and vmPFC

## Scientific assessment

**Scientific adequacy: qualified.** The group analysis is appropriate for the supplied participant gain-effect maps and the question of a positive group mean: it uses all 54 equal-indifference participants, a common finite/nonzero support mask, a one-sample model, one-sided participant-level sign flips, and maximum-t whole-brain family-wise correction. The reported conclusion is appropriately bounded: **the supplied maps do not establish a positive vmPFC effect under the stated corrected criterion.** That is a lack of support for the positive hypothesis in this analysis, not evidence that the effect is exactly zero.

**Reported hypothesis outcome:** no positive vmPFC finding survived whole-brain FWE correction; the positive hypothesis was not supported. The analysis reports 24 corrected positive voxels in three posterior islands, with the strongest at (−26, −102, −3.6) mm (t(53)=6.62, pFWE=.0006), far outside its vmPFC display box. Within the box, the participant-summary mean was −0.0035 upstream units (95% CI −0.0229 to 0.0160), and no voxel passed whole-brain FWE. The interval is broad and is not an equivalence test.

The method accounts for the supplied maps as unstandardized participant contrast estimates for a mean-centered, variance-normalized gain modulator. It does not mislabel the contrast as a currency-unit slope or standardized statistic, and it notes that gain and loss were modeled separately. The coordinate box is explicitly descriptive rather than a search restriction. Max-t permutation inference is a defensible whole-brain method and the SciPy checks are reported. The task's whole-brain correction requirement is met. The supplied task and rubric specify this requirement; the cited original PDF itself timed out when opened by the assessor, so its full contents were not independently inspected.

Adequacy remains qualified because sign-flip inference assumes participant effects are symmetric under the null; no participant variance maps are supplied, so first-level uncertainty is not propagated; and zero-as-no-support is the analysis mask rule. The protocol, code and outputs are internally consistent about that rule, but the mask semantics are conditional on the supplied map construction. These limits weaken claims about the underlying neural response and small effects, without overturning the reported lack of corrected vmPFC support. Participant and map checks, no-extremity exclusions, MNI geometry, and gain scaling are documented in `protocol.md`, `scripts/group_analysis.py`, `results/summary.json`, `results/participant_qc.csv`, and `results/code-input-sha256.txt`.

## Delivery verification and attribution

The manifest and worker-stop receipt match: SHA-256 `62fae7a1b4cf57bb811b88cb718ed01596b5d9b784e996e678b4851cadefbd0d`; complete capture, 1,283 entries, no declared errors or omissions; worker stop commit `afb62884c70115b6e46a92ddcd1d17bbf4f33544`. The frozen snapshot validator confirmed the capture hash and commit. The stop receipt lists supplied source inputs separately from the worker's later files. The complete stopped workspace includes uncommitted and untracked material, and the analysis was assessed from that complete workspace rather than from the commit alone.

At worker stop, Git existed and git-annex pointer records cover 54 participant maps. The analysis script, runner, report, protocol, retrieved `data/`, figures and results are untracked. Thus the commit does not track the complete scientific delivery. The stop receipt records a normally exited worker and the capture includes the generated analysis and reports. No worker-supplied environment lock or complete package declaration is present; the summary records selected software versions, and the runner defaults to an absolute interpreter path outside the object. The coordinator's preserved capture and delivery to the assessor establish retention here, not worker publication or sharing of the research object. No worker-declared public project route was identified.

The worker-declared data route is `scripts/retrieve_maps.py`, called by `bash run_analysis.sh`. It lists 54 NeuroVault maps in `input/sources.json`, retrieves 96,387,264 bytes in total, and checks each size and SHA-256. The retained `results/retrieval-manifest.txt` records all 54 map checks at worker stop. The assessor tested one URL (`sub-001`) by HTTP HEAD from the assessor host; NeuroVault returned HTTP 200 and the expected content length. The other 53 URLs and full payload download were not tested by the assessor. The intended recipient is a researcher using that declared route; anonymous access is not required. Required coverage for full reproduction also includes participant metadata, code and a usable Python environment, which the data route alone does not provide. See `access-record.json`.

## Replay and measurement availability

**Scientific replay: not checked; zero attempts.** Before deciding, the documented entrypoint, prerequisites, outputs and comparison rule were recorded in `replay-record.json`. The entrypoint is `bash run_analysis.sh`; it depends by default on an external absolute Python path, and the delivery contains no `pixi.toml`, lockfile, requirements declaration or container. The declared environment therefore cannot be reconstructed from worker-supplied instructions without following an external path or adding missing dependencies, both outside this assessment scope. No code or inputs were changed and no shipped outputs are represented as replay evidence. This is a missing-prerequisite measurement limit, not target execution failure or scientific failure.

The STAMPED probes were run with the frozen external assessor and retained in `2026-10-16-probes.json`. Probe findings were interpreted against the full stop-state delivery, especially where untracked files or equivalent documentation fell outside the probe's tracked-path heuristics. The response contains per-item verdicts and citations; scientific adequacy, hypothesis outcome, checklist attainment, and measurement availability are separate judgments.

## STAMPED checklist

MUST: 4 met / 5 partial / 8 unmet / 0 not-checked / 0 not-applicable (17 total). SHOULD: 1 met / 1 partial / 6 unmet / 0 not-checked / 1 not-applicable (9 total). MAY: 4 met / 1 partial / 0 unmet / 0 not-checked / 0 not-applicable (5 total). These are per-item counts, not an overall score. `partial` does not satisfy a MUST.

### What to address first

- Track the analysis, runner, report, retrieved inputs and results at a reviewed worker commit; this closes the gap between the recorded commit and the scientific delivery (must/004).
- Supply and track a complete, pinned Python environment, record its identity with the run, and document installation/host requirements; this enables reproduction and closes must/003, must/006, must/007, must/009–017 and should/005–008.
- Replace the external absolute interpreter default with a documented, portable invocation; this makes the entrypoint usable outside the worker host (must/007, must/009, must/011–012, must/017).
- Add recurring workflow and fresh-environment checks tied to the declared environment; this would establish continued execution and reconstitution evidence (should/002, should/004, should/006).

### Existing strengths

The method is explicit about estimand, effect scaling, exclusions, mask, null assumption and whole-brain correction (`protocol.md`, `REPORT.md`). The participant set and map geometry are checked in code, the participant is the sampling unit, and independent test checks are recorded (`scripts/group_analysis.py`, `results/summary.json`). The report links code, input provenance, figures, tables and maps, and the delivery uses git-annex for large map files (`REPORT.md`, `input/data/`, `results/retrieval-manifest.txt`).

### Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `protocol.md`, `results/summary.json` | One workspace root contains code, inputs, data, results, figures and documentation. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `scripts/group_analysis.py`, `data/`, `input/data/` | The 54 maps are included and referenced by the relative source manifest used by the analysis. |
| must/003 | S.1 | unmet | probe:env-spec-tracked+judgement | `scripts/group_analysis.py`, `run_analysis.sh`, `probe:env-spec-tracked` | Python runtime dependencies are imported but no delivered environment declaration supplies them. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `probe:tree-clean`, `worker-end-state.json` | Git tracks some inputs and configuration, but the report, analysis code, retrieved data and results remained untracked at worker stop. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex`, `input/data/` | git-annex pointer records cover the large participant maps; map payloads are retained in the delivery. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `results/summary.json`, `results/code-input-sha256.txt`, `run_analysis.sh`, `probe:run-env-linked` | The run summary records software versions and outputs, but no exact environment specification is linked to the generated results. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `REPORT.md`, `run_analysis.sh`, `probe:entry-point` | REPORT.md gives a runnable usage command, but it does not provide installable environment instructions or a dependency specification. |
| must/008 | A.1 | met | probe:entry-point+judgement | `REPORT.md`, `run_analysis.sh` | The documented run_analysis.sh entrypoint calls retrieval and group analysis in sequence. |
| must/009 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:no-abs-paths+judgement | `run_analysis.sh`, `probe:no-abs-paths` | Most paths are relative, but the delivered runner hardcodes an absolute default Python path. |
| must/010 | P.1 | unmet | probe:env-spec-tracked | `scripts/group_analysis.py`, `probe:env-spec-tracked` | No environment specification declares the required Python packages. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `REPORT.md`, `run_analysis.sh` | The report names a provided common Python environment, but the host-specific interpreter path and setup requirements are not documented. |
| must/012 | P.2 | unmet | judgement | `REPORT.md`, `probe:platform-assumptions` | No README or environment specification lists reproducible system and package requirements. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked` | No environment definition is versioned with the project. |
| must/014 | P.3 | unmet | probe:env-spec-tracked+judgement | `probe:env-spec-tracked`, `run_analysis.sh` | No environment update or lockfile regeneration process is declared. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `results/summary.json`, `probe:run-env-linked` | Selected package versions in the summary do not constitute a complete pinned environment specification. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `probe:env-spec-tracked` | No environment artifact is supplied for recipients to obtain and use. |
| must/017 | D.1 | unmet | judgement | `REPORT.md`, `run_analysis.sh` | The report offers no procedure for obtaining or using a reproducible environment. |
| should/001 | T.2 | met | judgement | `probe:large-in-annex`, `probe:tree-clean` | Git and git-annex are used together for the workspace and large map payloads. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `results/attempts/`, `results/run.stdout`, `probe:ci-present` | The captured evidence shows a successful run and an earlier failed attempt, but no recurring or scheduled workflow tests. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input/`, `scripts/`, `results/`, `figures/`, `probe:modules-separated` | Inputs, code, results and figures have separate directories, while environment files are absent and the main code/results are untracked. |
| should/004 | E.1 | unmet | judgement | `results/run.stdout`, `run_analysis.sh` | No evidence shows execution in a fresh container, batch job, clean VM or cloud instance. |
| should/005 | E.1 | unmet | judgement | `run_analysis.sh`, `probe:env-spec-tracked` | The workflow invokes an existing Python interpreter and does not create a disposable environment. |
| should/006 | D.2 | unmet | probe:ci-present+probe:env-spec-tracked+judgement | `probe:ci-present`, `probe:env-spec-tracked` | No exact environment specification exists to test for reconstitution. |
| should/007 | D.2 | unmet | judgement | `probe:env-spec-tracked` | No environment artifact is archived with the project. |
| should/008 | D.2 | unmet | probe:env-spec-tracked+judgement | `probe:env-spec-tracked` | No declared process exists for updating environment specifications. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the supplied public dataset and software have no identified restricted component. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `scripts/retrieve_maps.py` | The independently maintained NeuroVault dataset is identified, retrievable by exact URLs, and bounded to 54 maps. |
| may/002 | M.2 | met | judgement | `REPORT.md`, `protocol.md` | The report and protocol explain the data, analysis code and outputs and link the supporting artifacts. |
| may/003 | M.2 | partial | judgement | `input/`, `scripts/`, `results/`, `run_analysis.sh` | The directory boundaries are clear, but absent environment declarations and untracked deliverables limit independent module updates. |
| may/004 | M.2 | met | judgement | `run_analysis.sh` | run_analysis.sh composes the retrieval and group-analysis steps. |
| may/005 | M.2 | met | judgement | `REPORT.md` | REPORT.md serves as an artifact guide with links to code, data records, figures and results. |

### Flagged probe overrides

- must/002: the subdataset probe did not recognize the manifest/annex layout; inspection found manifest-listed maps and internal annex links in the complete capture.
- must/006: no recognized environment-linked run record exists, but the summary records selected software versions and input/code hashes; that evidence is partial, not an exact environment pin.
- must/007–008: the filename probe missed equivalent usage instructions in `REPORT.md` and the `run_analysis.sh` entrypoint; installation instructions remain incomplete.
- must/009: the probe scanned tracked text only and missed an absolute default interpreter path in the untracked runner.
- may/001: the subdataset probe did not model a manifest-listed, independently maintained external dataset; inspection found a bounded NeuroVault dataset route with exact retrieval URLs.
- should/002: no recognized CI exists, but the complete delivery also shows one failed attempt and one successful run; this is insufficient evidence of regular testing.
- should/003: the probe recognized only the `input/` module; inspection also found separate script, results and figure directories, but no environment module.
- must/014 and should/008 are duplicate environment-update questions and repeat the same finding by design.

### Not checked and scope limits

- Replay remains not checked for the missing in-delivery environment specification described above.
- Retrieval reachability was checked for one map URL only; the assessor did not download all 54 payloads.
- The original NARPS PDF could not be retrieved during this assessment; whole-brain correction is assessed against the task and rubric supplied with this assignment.

### Goals and project kind

The supplied goal is a concise group-stage scientific assessment of a positive gain effect in vmPFC among the 54 equal-indifference participants, conditional on fixed participant gain-effect maps. This is a computational study with scientific derivatives and methods, assessed as a `study`.

### Checklist link, response and provenance

Checklist application: [open the filled checklist](2026-10-16-url.txt). Machine-readable answers and citations: [2026-10-16-response.json](2026-10-16-response.json). Replay and access details: [replay-record.json](replay-record.json), [access-record.json](access-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the captured workspace at commit `afb62884c70115b6e46a92ddcd1d17bbf4f33544`, 2026-10-16, Codex API / gpt-6.1-sol. Capture manifest SHA-256: `62fae7a1b4cf57bb811b88cb718ed01596b5d9b784e996e678b4851cadefbd0d`. Probe output: `2026-10-16-probes.json`.
