# Independent assessment — 2026-10-16

**STAMPED verdicts:** MUST: 6 met / 2 partial / 8 unmet / 1 not-checked (17 total); SHOULD: 0 met / 2 partial / 5 unmet / 1 not-checked / 1 not-applicable (9 total); MAY: 4 met / 1 partial / 0 unmet / 0 not-checked / 0 not-applicable (5 total). No overall score is assigned.

**Scientific adequacy: supported.** The delivered analysis supports its reported absence of whole-brain-corrected positive vmPFC evidence; this does not establish a zero effect. **Reported hypothesis outcome:** “The 54 supplied AO86 participant maps do not support a positive gain-related response in vmPFC.”

## Scope and evidence identity

Assessor/runtime check passed for the pinned assessor and runtime. The canonical original capture manifest SHA-256 is `2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456`; its `head_commit` is `bfe069501c140673f38778116f34bc8a5c36366f`. The operational manifest has the same SHA-256 and entries. I inspected only the operational copy, retained assessor guidance, supplied scientific brief, and worker-stop receipt; no other workers' outputs, prior judgments, coordinator summaries, or assignments were consulted. The launcher is responsible for its before/after integrity verification. No capture mismatch was observed in the manifests I compared. Original evidence citations below use canonical capture SHA `2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456`; unprefixed workspace paths are relative to `content/workspace/`. Worker-stop evidence is separately identified by its receipt hash.

The scope is the complete stopped workspace, including untracked analysis files and ignored `.codex/` and `.entire/` files. `HEAD` contains the supplied input layer, while `README.md`, `REPORT.md`, `protocol/analysis-plan.md`, `code/group_analysis.py`, `environment.md`, figures, and results were untracked in the stopped working tree. The ignored assistant/worktree configuration files disclose that such tooling was present; I record this exposure but did not use it to judge the scientific results or infer any treatment assignment.

The worker-stop receipt is SHA-256 `70599a0fd897834f872329ffcbb9dbfd74b55f856ca4e9c44f234b1bf72660bd`. Its stop state reports a normal worker exit. The captured Git commit is `bfe069501c140673f38778116f34bc8a5c36366f`, but the available record does not attribute the input-staging/annex commit to the worker. I therefore do not treat that commit or annex setup as worker practice. The worker's code, report, protocol, figures, and result files were present at stop but uncommitted. No worker publication URL or remote is recorded. The shared environment and the assessment-time replay are not worker environment capture or worker execution evidence.

## What to fix first

1. Put the worker-created code, protocol, report, figures, and numerical outputs under version control at the stopped version; this makes the scientific delivery identifiable and reviewable (must/004, should/001).
2. Include a portable, locked environment specification with an update process and retrieval instructions; the current project points to a host-specific shared installation (must/003, must/010, must/013–017; should/006–008).
3. Record each worker run with command, input identity, exact environment identity, and output links; this connects results to the computation that produced them (must/006).
4. Publish a recipient-authorized route to the complete project and required annex payloads, then test retrieval through that route (must/016).
5. Add a repeatable workflow test and fresh-environment check; assertions within the analysis are useful QC but do not show ongoing or isolated testing (should/002, should/004–005).

## What is already strong

- The analysis plan defines a participant-level, one-sided max-T sign-flip test with whole-brain family-wise correction, an explicit vmPFC coordinate sphere, and a stricter-support sensitivity check (`protocol/analysis-plan.md`, `code/group_analysis.py`).
- The report correctly distinguishes normalized gain-modulator coefficients from currency-scaled slopes, gives uncertainty and limitations, and does not turn a lack of support into proof of a zero effect (`REPORT.md`).
- The code checks participant IDs, image hashes, geometry, finite values, and independently checks sampled t statistics and sign-flip calculations; machine-readable summaries and figures are supplied (`code/group_analysis.py`, `results/summary.json`, `results/participant_qc.tsv`).

## Scientific assessment

The reported outcome is supported. The 54 participant maps are analyzed at the participant level with equal weights, appropriate to the lack of participant variance maps. The primary test is one-sided and uses the maximum t statistic across the nonzero-support mask, with 10,000 sign patterns and whole-brain FWE control. The 95% support-mask sensitivity result is reported as unchanged. The prespecified 10-mm sphere at MNI [0, 40, −8] is used descriptively rather than as an uncorrected confirmatory shortcut. The report states that the corrected posterior clusters do not overlap the sphere.

The results give a vmPFC-sphere mean of −0.0057, 95% t interval [−0.0326, 0.0211], and one-sided uncorrected p=.665; no corrected vmPFC evidence is claimed. A whole-brain corrected positive finding elsewhere is explicitly not interpreted as support for vmPFC. This is a defensible absence-of-support conclusion, not evidence that the effect is exactly zero.

The report and plan appropriately qualify the result: supplied maps are unthresholded gain coefficients from a fixed upstream model, not currency-unit slopes; gain and loss were modeled separately; participant variance maps and raw time series are unavailable; and the sign-flip method assumes independent participants and a symmetric null. Exact-zero support is treated as missing coverage, with that ambiguity disclosed. The affine is used for spatial interpretation while header spatial units are reported as unknown. These limits reduce certainty but do not undermine the stated conditional group inference. The scientific task allows defensible alternatives, and no particular atlas or model is required.

**Hypothesis conclusion (verbatim):** The 54 supplied AO86 participant maps do not support a positive gain-related response in vmPFC.

## Replay and measurement availability

The README documented this entrypoint: `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/group_analysis.py`. The one frozen-helper attempt used a separate copy of the canonical complete delivery and preserved the captured inputs and source. The declared output selection included nine actual generated artifacts plus `results/extra`, which is not an identifiable generated artifact. The helper ignored that unmatched selector and reported byte-identical reproduction of the nine matched artifacts (see `2026-10-16-fresh-rerun.json` and `replay-work/replay.stdout`). Because the submitted output list violated the required selection rule and the one-attempt limit is exhausted, replay measurement availability is **not-checked**; the helper's `met` label is retained as raw output but is not accepted as a compliant replay verdict. This is an assessor protocol deviation, not a target failure. It does not alter the scientific assessment, which is based on the unchanged stopped delivery.

The attempt used the captured inputs; the adapter initiated no input retrieval. Its 5 GB setting applied only to helper prefetch (none occurred), and the execution completed in about 36 seconds, below 7,200 seconds. `formal-replay-attempt.json`, stdout/stderr captures, exit code, replay copy, and helper output are retained. A replay record cannot be used as evidence that the worker ran the analysis.

## Access route and coverage

Intended recipient: a researcher using the worker-declared authorized route. The README says to obtain annex content with `git annex get input/data/` and run the script from the project root. `input/sources.json` also names the NeuroVault collection and direct URLs for all 54 maps; one representative URL returned HTTP 200 to a HEAD request without downloading data. The project has no configured Git remote, annex location, or way to obtain the shared environment. Required coverage is the complete project, all 54 map payloads, metadata, source code, and a reproducible environment. The captured delivery and replay copy contained the map payloads, but coordinator delivery to this assessment does not establish worker publication. Only the assessment host was tested, using captured payloads and the pre-provisioned shared environment; the one URL check was a HEAD request to NeuroVault. The route for an intended recipient on another authorized host is unverified; see `access-record.json`.

## Checklist findings

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/README.md#L1-L11` | Essential analysis inputs, code, report, and results are inside the captured workspace; annex payloads are rooted under its Git metadata. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/input/sources.json` | The 54 maps and metadata are addressed under input/ and stored through in-boundary annex pointers; replay consumed the captured payloads. |
| must/003 | S.1 | unmet | probe:env-spec-tracked+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/environment.md` | README and environment.md rely on a shared host Pixi environment outside the project; no environment declaration or linked software module is included. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/REPORT.md`, `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/.git/index` | Git tracks supplied input pointers and metadata, but the worker's code, protocol, report, and results remained untracked at stop. |
| must/005 | T.1,T.3,T.5 | not-checked | probe:large-in-annex+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/input/data; worker-end-state.json`, `worker-stop:70599a0fd897834f872329ffcbb9dbfd74b55f856ca4e9c44f234b1bf72660bd/worker-end-state.json` | The 54 annex pointers are present, but the stop record does not attribute their coordinator-supplied commit/annex setup to the worker; worker use is unestablished. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/results/summary.json` | Shipped summary lists package versions but no exact environment spec or run identity; no worker run record links action, result, and environment. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/README.md#L5-L11` | README gives usage and annex retrieval, but assumes an already installed environment at an absolute path and gives no installation procedure. |
| must/008 | A.1 | met | probe:entry-point+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/code/group_analysis.py` | README names code/group_analysis.py as a directly executable starting point and describes its inputs and output directories. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/code/group_analysis.py` | Analysis paths are built relative to the script's project root; no hard-coded host paths occur in the workflow code. |
| must/010 | P.1 | unmet | probe:env-spec-tracked+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/code/group_analysis.py; environment.md` | The imports require NumPy, pandas, NiBabel, SciPy, Matplotlib, and Nilearn, but the project has no dependency specification; a host environment is assumed. |
| must/011 | P.1 | met | probe:platform-assumptions+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/environment.md` | environment.md records macOS 27.0.1 arm64, the shared interpreter path, runtime versions, and the shared manifest location. |
| must/012 | P.2 | met | probe:platform-assumptions+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/environment.md` | environment.md states the operating system, architecture, Python version, and required scientific package versions. |
| must/013 | P.3 | unmet | probe:env-spec-tracked | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/environment.md` | No installable environment specification or lockfile is included in Git alongside the analysis. |
| must/014 | P.3 | unmet | probe:env-spec-tracked | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/environment.md` | No environment update/regeneration process or tracked specification is supplied. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/results/summary.json; environment.md` | Package version strings are reported, but no frozen manifest, lock hash, or immutable environment identity is supplied. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/README.md; environment.md` | No worker-declared authorized retrieval route for the environment or full project is recorded; the README's host paths are local to its original machine. |
| must/017 | D.1 | unmet | probe:entry-point+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/README.md#L5-L11` | README says to use a prepared environment but does not explain how a recipient obtains or reconstructs it. |
| should/001 | T.2 | partial | probe:tree-clean+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/REPORT.md` | Git covers the supplied input layer, while worker-created analysis code, documentation, and results were untracked at stop. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/code/group_analysis.py; results/summary.json` | The complete delivery has no recurring test or CI record; analysis assertions and a single result set do not show regular testing. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/README.md` | Inputs, code, and derived results have separate directories, but the environment is only referenced as an external shared installation. |
| should/004 | E.1 | not-checked | probe:fresh-rerun+judgement | `2026-10-16-fresh-rerun.json; formal-replay-attempt.json` | The only replay selector included a non-generated path, violating the frozen output-selection rule; no worker fresh-environment test is recorded. |
| should/005 | E.1 | unmet | judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/README.md; environment.md` | README runs each invocation in a shared, pre-provisioned environment; the workflow does not create a disposable environment. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/environment.md` | No environment specification exists to reconstitute and test; no worker records show recurring environment rebuild checks. |
| should/007 | D.2 | unmet | probe:env-spec-tracked+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/environment.md` | The environment binaries and manifest are referenced outside the research object and are not archived within it. |
| should/008 | D.2 | unmet | probe:env-spec-tracked+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/environment.md` | No environment update process is declared or tracked; this repeats must/014 by checklist design. |
| should/009 | M.4 | not-applicable | judgement | — | N/A: the supplied inputs and dependencies are public; no restricted data or software component is present. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/input/sources.json`, `neurovault:HEAD-sub-001` | The AO86 maps are bounded under input/ with per-file NeuroVault URLs and hashes; a representative HEAD request returned HTTP 200. |
| may/002 | M.2 | met | judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/README.md` | README maps input, code, protocol, and results directories and explains how the script connects them. |
| may/003 | M.2 | partial | judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/code/group_analysis.py; environment.md` | Inputs, analysis, and results are separated, but the external shared environment path limits independent updates. |
| may/004 | M.2 | met | judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/code/group_analysis.py` | One script reads the supplied inputs and composes them into named result and figure outputs. |
| may/005 | M.2 | met | judgement | `capture:2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456/content/workspace/README.md` | README gives a directory map and directs readers to the analysis plan, source metadata, code, report, and outputs. |

## Extra finding outside the checklist

- Reuse terms are not declared in the complete delivery (`license-declared`: unmet; captured `README.md` and the remaining workspace inventory contain no licence statement).

## Flagged items

- may/001: the subdataset probe did not recognize the per-file source map; `sources.json` identifies the independent AO86/NeuroVault input collection and a representative source URL returned HTTP 200.

- must/004: the tree probe saw uncommitted worker files; `partial` records that only the supplied input layer was tracked.
- must/005: the annex probe saw 54 pointers, but worker-stop attribution does not establish worker setup, so availability is `not-checked`.
- must/006: the run/environment probe did not recognize the untracked summary; direct inspection found package versions but no exact environment spec/run identity, supporting `unmet`.
- must/007: the entry-point probe omitted the untracked README; it documents usage but not installation, so `partial`.
- must/008: the entry-point probe omitted the untracked script; `code/group_analysis.py` is a clear executable start.
- must/011 and must/012: the platform probe only scanned commands; `environment.md` directly documents host assumptions and package requirements.
- should/004: the raw helper reports `met`, but its submitted output list included a non-generated selector; replay availability is not-checked.
- should/008: duplicate of must/014 by checklist wording; same answer by design.

## Not checked

- must/005: worker attribution for the coordinator-supplied annex setup is unavailable; a worker-authored stop record of setup would settle it.
- should/004: the single replay selector was not compliant; no further attempt is authorized by the frozen scope.
- Full project access beyond the assessment host: the sample map source URL is reachable, but complete repository/annex retrieval and environment access through a worker-declared authorized route remain unverified.

## Goals, kind, and access

Assumption (not human-confirmed): this is a **study** whose product is a group-level scientific answer with reproducible code, results, and figures. The task and `README.md` define the question and artifact layout; study emphasis therefore falls on the full delivery boundary, provenance, actionability, portability, and recipient access. The assessment host successfully read the captured input payloads and reports. The intended research recipient, authorized route, coverage, and tested host scope are stated above and in `access-record.json`.

## Checklist URL and provenance

Checklist app link: [open the filled checklist](2026-10-16-url.txt). Machine-readable answers: [2026-10-16-response.json](2026-10-16-response.json). Probe output: [2026-10-16-probes.json](2026-10-16-probes.json). Replay output: [2026-10-16-fresh-rerun.json](2026-10-16-fresh-rerun.json), with the availability limitation above. Scientific record: [scientific-judgment.json](scientific-judgment.json). Replay disposition: [replay-disposition.json](replay-disposition.json). Access details: [access-record.json](access-record.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the captured study at commit `bfe069501c140673f38778116f34bc8a5c36366f`, 2026-10-16, Codex; model identity unavailable from the harness. Probe output: `2026-10-16-probes.json`. Canonical capture SHA-256: `2b55f51d8f5c4cc64919590ebf961916ebfa380e5e21ba70afe081db57219456`.
