# Independent assessment — NARPS Hypothesis 1

## Scientific assessment

**Scientific adequacy: supported, conditional on the supplied participant maps and upstream methods. Reported hypothesis outcome: not supported.** The analysis uses the complete 54-person equal-indifference sample, checks map checksums, geometry and finite values, fits the participant-level one-sample model, and controls positive whole-brain inference with 9,999 sign-flip maximum-t permutations. It defines vmPFC independently with a broad AAL3v2 medial orbital frontal/rectus proxy and reports that no proxy voxel survives whole-brain FWE (minimum corrected p = 0.788). The proxy mean is −0.0037 contrast units (95% CI −0.0287 to 0.0212); this is consistent with a lack of positive support, not proof of a zero effect. The reported whole-brain corrected clusters are posterior (peaks y = −94 to −102 mm), so they do not support the vmPFC hypothesis. See [report](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-21-j01/content/workspace/report/report.md), [analysis plan](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-21-j01/content/workspace/protocol/analysis-plan.md), [analysis code](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-21-j01/content/workspace/code/analyze.py), and [summary results](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-21-j01/content/workspace/results/summary.json).

This support is scoped to the effect estimates and model supplied: the gain regressor was normalized, maps are not currency-unit effects, variance maps are absent, and upstream preprocessing/modeling cannot be re-audited here. The common-support mask limits inference to 198,029 voxels shared by all maps; sign flips rely on a symmetric-null assumption. The broad vmPFC boundary is approximate. The script and reported result agree at inspection, but replay availability is **not-checked** because the frozen helper failed before the target command ran. No replay evidence is claimed.

The report transparently preserves the initial pilot and invalid denominator attempt and labels those results unusable. Its corrected permutation statistic uses the standard error denominator; the one-sided max-T procedure and secondary FDR are distinguished. It includes participant and ROI distributions, uncertainty, anatomical limitations and the interpretation of no corrected support. The FDR voxel in the proxy is properly not used as confirmatory evidence.

## Delivery verification and attribution

The complete captured workspace was verified against the manifest (SHA-256 `b177304a0a1e893757998b89ef8880db42f2639395a46d1d5570932971830f56`): 1,219 captured entries, no manifest omissions or errors, and no mismatch. The worker stop receipt records a successful exit and HEAD equal to the supplied seed commit `2906eaca49c5a00d3df4b0c2dcd59eba9c8a3fb8`; README, code, protocol, report, figures and results were uncommitted/untracked at stop. This assessment grades those complete-delivery bytes scientifically while crediting versioning only at the recorded worker stop. Coordinator preservation does not change those worker-practice findings. Supplied study inputs and the external Python environment are distinct from worker-created environment capture. The environment, results and sharing route were not captured as worker versioned/published objects.

`judge-target.json` lists nine original external skill links under `reference_limits`; I did not follow them. The retained `.git/config` was inspected as text; its absolute external hooksPath was not followed. The captured `.git` directory itself is present. No treatment assignment was inferred or reported.

## Access

Intended recipient: a researcher using the worker-declared authorized route. **No route was declared**, so there was no route to retrieve or test. The worker stop receipt has no repository/publication field, and captured `.git/config` contains no remote. Required coverage is code, protocol, report, all 54 maps and metadata, results/figures, plus a usable environment specification. The captured delivery contains the code, protocol, report, maps/metadata and results/figures, but no reconstructable environment specification. Local inspection was on the assessor host only; this does not establish worker access. Details: [access record](2026-10-16-access.json).

## Replay record

Before replay, the declared command was the README invocation with `--permutations 9999 --seed 240519`. Prerequisites named by the worker were the absolute external Python interpreter, its scientific Python packages, and Nilearn's AAL3v2 atlas/MNI template (the worker log shows an existing atlas cache). The explicit generated outputs and scientific comparison rule are recorded in [replay record](2026-10-16-replay.json). No inputs, participant metadata or source code were selected for deletion.

The first frozen-helper invocation failed because I had created its workdir before calling it (`Materialization requires a new destination`). I retained its command and output. The subsequent call reported that the formal one-attempt allowance was already consumed. No target command ran, no output was removed or regenerated, and no second/fallback replay was made. This is an assessor/setup malfunction; replay status and fresh-execution measures remain unavailable, not a target failure.

## STAMPED assessment

MUST items: **4 met / 5 partial / 8 unmet / 0 not-checked** (partial does not satisfy a MUST). SHOULD: **1 met / 1 partial / 3 unmet / 3 not-checked / 1 not-applicable**. MAY: **2 met / 2 partial / 0 unmet / 0 not-checked / 1 not-applicable**. No overall score is assigned. Probe results are retained unedited in [probes.json](probes.json); complete per-item answers and citations are in [response JSON](2026-10-16-response.json).

### What to improve first

- Add a pinned, installable environment and instructions to obtain it → makes the delivered analysis runnable by another researcher → must/003, 007, 010–013, 015, 017.
- Record the analysis command, exact environment and output list together in a run record → connects the results to their generating computation → must/006, 015; should/006.
- Commit the code, protocol, report and generated results at worker stop → preserves an attributable version of the scientific delivery → must/004.
- Document a worker-authorized retrieval route that covers inputs, outputs and environment → makes the project retrievable by its intended recipient → must/016 and access.

### What the project already does well

- All 54 participant maps are available through captured annex content and verified against the supplied checksums ([sources](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-21-j01/content/workspace/input/sources.json), [code](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-21-j01/content/workspace/code/analyze.py)).
- The protocol fixes the participant-level estimand, direction, mask, whole-brain max-T test, seed and uncertainty reporting before analysis ([analysis plan](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-21-j01/content/workspace/protocol/analysis-plan.md)).
- The report separates the hypothesis outcome from posterior findings and explains limits of the normalized effects and absent participant variance maps ([report](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-21-j01/content/workspace/report/report.md)).

### Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `README.md`, `input/data/` | Inputs and outputs are rooted here, but the documented interpreter lives outside the project root. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `code/analyze.py`, `.git/annex/objects/` | All 54 maps are included through relative annex links and checksum-checked by the analysis. |
| must/003 | S.1 | unmet | judgement | `code/analyze.py`, `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | The required Python packages are not declared in a delivered environment specification. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `.git/HEAD`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/worker-end-state.json` | Git tracks the supplied seed and inputs, while the analysis, report and results were uncommitted at worker stop. |
| must/005 | T.1,T.3,T.5 | met | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json`, `input/data/` | git-annex tracks the 54 large participant maps; payloads are present in the captured annex store. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+probe:run-env-linked+judgement | `results/run.log`, `results/summary.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | The report and run log identify the analysis and outputs, but no record binds them to an exact environment specification. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | README gives a usable analysis command, but omits installation steps for its external interpreter and dependencies. |
| must/008 | A.1 | met | probe:entry-point+judgement | `README.md`, `code/analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | README identifies code/analyze.py as the reproducible starting point. |
| must/009 | P.1 | met | judgement | `code/analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | The analysis uses project-relative paths for inputs and default outputs. |
| must/010 | P.1 | unmet | judgement | `code/analyze.py`, `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | The scientific script depends on packages in an external preinstalled environment with no delivered dependency declaration. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/summary.json`, `README.md`, `results/run.log` | Python and host package versions are recorded, but the required host setup and atlas retrieval assumptions are not documented. |
| must/012 | P.2 | unmet | judgement | `README.md`, `code/analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | README does not provide a system requirements or dependency list sufficient to provision the analysis. |
| must/013 | P.3 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/worker-end-state.json` | No environment specification is included in the worker delivery or worker-stop inventory. |
| must/014 | P.3 | unmet | judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | No environment update or lockfile-generation process is documented. |
| must/015 | D.1 | unmet | judgement | `results/summary.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | The results list package versions but no frozen manifest or environment digest that another researcher can recreate. |
| must/016 | D.1 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/worker-end-state.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | No worker-published environment specification or retrieval route is recorded. |
| must/017 | D.1 | unmet | judgement | `README.md` | The documented command assumes an externally provisioned interpreter and gives no route to obtain the environment. |
| should/001 | T.2 | met | judgement | `.git/config`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | Git and git-annex track code/input metadata and large maps within one repository. |
| should/002 | A.2 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json`, `results/run.log` | No repeated workflow or environment test record was established; a CI scan alone cannot settle manual testing. |
| should/003 | M.1 | partial | judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | Input, code, results and figures have separate directories, but the environment is external and not a delivered module. |
| should/004 | E.1 | not-checked | judgement | `results/run.log`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/records/replay.stderr.txt` | No worker evidence establishes execution in a fresh container, job or clean machine. |
| should/005 | E.1 | unmet | judgement | `README.md` | The documented workflow reuses a fixed external environment rather than creating a disposable one. |
| should/006 | D.2 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/records/replay.stderr.txt` | No delivered environment specification exists to verify reconstitution; the replay helper failed before execution. |
| should/007 | D.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/worker-end-state.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | The worker delivery does not archive an environment or executable software artifacts. |
| should/008 | D.2 | unmet | judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | No environment update process is documented; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the included cohort maps and metadata are identified as public source data; no restricted component is identified. |
| may/001 | M.2 | not-applicable | judgement | `input/sources.json`, `input/data/` | N/A: independently maintained project components are not part of this object; referenced maps are included as data inputs. |
| may/002 | M.2 | partial | judgement | `README.md`, `protocol/analysis-plan.md` | The README describes the input-to-analysis-to-results layout, but no formal module composition is defined. |
| may/003 | M.2 | unmet | judgement | `README.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-21/judgments/narps-neutral-r1-21-j01/attempt-01/judgment/probes.json` | The analysis, environment and outputs cannot be independently updated as modules because they share one unconfigured root and external runtime. |
| may/004 | M.2 | met | judgement | `README.md`, `code/analyze.py` | The analysis script composes supplied inputs into group results and figures from one documented command. |
| may/005 | M.2 | met | judgement | `README.md`, `protocol/analysis-plan.md`, `report/report.md` | README, protocol and report explain how to navigate the analysis and its scientific decisions. |
### Flagged items

- **must/006:** the run-record probes did not recognize the untracked summary and log. Full-delivery inspection found result/action records but no exact environment pin, so attainment is partial.
- **must/007, must/008:** the entry-point probe scanned tracked Git paths only; complete-delivery README and code provide a documented route. Item 007 remains partial because environment installation is missing; item 008 is met.
- **should/008:** repeats must/014 by design.

### Not checked

- **should/002:** no evidence settles repeated manual or automated workflow testing; a CI scan alone is insufficient.
- **should/004:** worker evidence does not establish testing in a clean environment; the assessor replay did not run.
- **should/006:** environment reconstitution could not be verified; no environment specification is delivered and replay was unavailable.

### Not applicable

- **should/009:** no restricted component is identified; the included source maps and metadata are publicly sourced.
- **may/001:** no independently maintained project module is part of the assessed object; the source maps are included as project data.

### Goals and kind

The documented goal is a group-stage test of the positive potential-gain effect in vmPFC for the 54-person equal-indifference group, using fixed AO86 participant maps and whole-brain corrected inference. This is a **study**: its product is a scientific conclusion supported by code, results and figures. Assumption: no human guidance was attached, so the goal and kind were not separately confirmed.

The response passed frozen validation against all 31 checklist items. The [checklist link](2026-10-16-url.txt) encodes the response. The [delivery verification](records/delivery-verification.json), [access record](2026-10-16-access.json), [replay record](2026-10-16-replay.json), and command/stdout/stderr records are retained alongside this report.

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the captured delivery at commit `2906eaca49c5a00d3df4b0c2dcd59eba9c8a3fb8`, 2026-10-16, OpenAI Codex / GPT-6. Probe output: [probes.json](probes.json).
