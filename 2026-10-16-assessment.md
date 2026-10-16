# STAMPED assessment: NARPS gain-effect group analysis

**Assessed object:** `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/targets/judgment-02` at `abf95b00c02fb55d16c4d269926c1428cedc0574`. The required `git rev-parse HEAD` returned that exact commit before inspection. The judgment products are outside the assessed checkout.

## Verdicts

- **MUST:** 11 met / 0 not-applicable / 3 partial / 3 unmet / 0 not-checked (17 total).
- **SHOULD:** 2 met / 1 not-applicable / 0 partial / 6 unmet / 0 not-checked (9 total).
- **MAY:** 1 met / 0 not-applicable / 3 partial / 1 unmet / 0 not-checked (5 total).

No overall score is assigned.

## What to address first

1. **Freeze the exact environment and record its identity with each result** → `pixi.toml` has open ranges and no lock, so the packages behind the reported maps are not exactly recoverable → must/006, must/015, must/014 and should/008.
2. **Make the documented reproduction command work on a clean clone** → `duct` stops when it finds committed logs with the same prefix; preserve old logs or use a new prefix and add a successful fresh run → must/007, must/017, should/004, should/006.
3. **Add short setup and usage instructions and explain the supported Pixi bootstrap** → the only invocation is embedded in `results/report.md`, with no instructions to obtain Pixi or start from a repository clone → must/007, must/012, must/017.
4. **Add a recurring check of the documented route and environment** → no CI configuration is tracked and environment reconstruction is not exercised regularly → should/002, should/006.

## What the object does well

- It tracks all 54 participant maps via git-annex, source metadata, code, outputs and run logs. The worker-end-state receipt records a clean worker stop at this commit with the tracked inventory; no source object changes were made during this assessment.
- `analyze.py` validates the 54 IDs, image grids, finite values and source checksums, then uses a prespecified 90% coverage mask and one-sided participant sign-flip max-T correction across that mask. `results/report.md` explains the assumptions and correctly keeps the vmPFC estimate descriptive while requiring whole-brain correction for support.
- The repository's current authorized Git and annex routes resolved during retrieval checks, and all 54 declared source map URLs returned bytes matching the manifest. See [access-retrieval.md](access-retrieval.md); these checks were run after the worker stop and are not attributed to the worker.

## Per-item assessment

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-files`, `input/data` | All project content is under the repository root; annex targets resolve within its .git/annex store. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `input/data` | All 54 maps and metadata are reachable through input/ within the root; maps are git-annex links. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `results/report.md` | Required analysis packages are declared in pixi.toml; execution uses the declared con-duct package. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/worker-end-state.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json` | The assessed commit tracks code, text, configuration, and records; worker-stop receipt reports a clean index and worktree. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json` | git-annex tracks the 54 large input maps; no large binary blobs are stored in Git. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `logs/group-analysis-final-verifiedinfo.json`, `results/summary.json#software`, `pixi.toml` | Run logs and hashes exist, but no exact environment lock is recorded for these results; pixi.toml has open version ranges. |
| must/007 | A.1 | unmet | probe:entry-point | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json`, `results/report.md` | No README.md or Makefile provides installation and usage instructions; the command appears only in results/report.md. |
| must/008 | A.1 | met | probe:entry-point+judgement | `analyze.py`, `results/report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json` | analyze.py is a runnable main script and results/report.md gives the full invocation; the entry-point probe missed it. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `analyze.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json` | Analysis paths are rooted at Path(__file__).resolve().parent; host paths occur only in recorded output. |
| must/010 | P.1 | met | judgement | `analyze.py`, `pixi.toml` | All analysis imports and invoked workflow tools are declared in pixi.toml; no undeclared analysis package was found. |
| must/011 | P.1 | met | judgement | `pixi.toml` | Supported host platforms are listed as macOS 14 ARM and linux-64; no other host service or hardware is required. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `results/report.md` | pixi.toml lists OS targets and packages, but documentation omits how to install the Pixi command used to run them. |
| must/013 | P.3 | met | probe:env-spec-tracked | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json` | pixi.toml is tracked with code and data at the assessed commit. |
| must/014 | P.3 | unmet | judgement | `pixi.toml` | No dependency update or lock regeneration process is documented; pixi.toml has no lockfile. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `pixi.toml`, `logs/group-analysis-final-verifiedinfo.json` | pixi.toml allows environment creation, but no frozen lock or container digest fixes the exact result environment. |
| must/016 | D.1 | met | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/remote-git-clone.rev-parse`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-fresh-rerun.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/neurovault-retrieval-verified.stdout` | An authorized researcher can retrieve the exact Git revision and Pixi spec; all annex maps were fetched in a fresh clone and all 54 source URLs hash-verified. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:fresh-rerun+judgement | `results/report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-fresh-rerun.json` | results/report.md documents the Pixi invocation, but not how to obtain Pixi or the repository; the sole replay stopped at existing log conflicts. |
| should/001 | T.2 | met | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json` | Git versions code, records and configuration; git-annex extends Git for map payloads. |
| should/002 | A.2 | unmet | probe:ci-present | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json` | No CI configuration or other recurring instruction test is tracked. |
| should/003 | M.1 | met | probe:modules-separated | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json` | Inputs, analysis code, results, and environment spec occupy distinct paths. |
| should/004 | E.1 | unmet | probe:fresh-rerun | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-fresh-rerun.json` | The one fresh-clone replay did not reach analysis; no successful clean-environment run is recorded. |
| should/005 | E.1 | unmet | judgement | `results/report.md`, `pixi.toml` | The documented Pixi invocation reuses its environment; no per-run disposable environment is created. |
| should/006 | D.2 | unmet | probe:ci-present+probe:fresh-rerun | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-fresh-rerun.json` | No recurring environment rebuild check exists, and the sole fresh replay failed before analysis. |
| should/007 | D.2 | unmet | judgement | `pixi.toml`, `git ls-files` | Only a Pixi manifest is archived; no resolved lock, package cache, or environment image is included. |
| should/008 | D.2 | unmet | judgement | `pixi.toml` | No dependency update or lock regeneration process is documented; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: no restricted data or software component is identified; all inputs are retrievable from public source URLs. |
| may/001 | M.2 | unmet | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json` | External maps are git-annex content, not separate submodules or linked subdatasets. |
| may/002 | M.2 | partial | judgement | `results/report.md` | The report explains input, result and environment roles, but no separate modular composition guide is provided. |
| may/003 | M.2 | partial | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json`, `results/report.md` | Input, code, results and environment paths are separated, but changing them is not documented as independent. |
| may/004 | M.2 | met | judgement | `analyze.py`, `results/report.md` | analyze.py composes the input maps, participant table and Pixi environment into results through one command. |
| may/005 | M.2 | partial | judgement | `results/report.md`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/judgment/2026-10-16-probes.json` | The report names principal outputs, but no README or navigation guide orients readers to the repository layout. |

## Flagged items

- **must/006 — `mapping-questioned`:** the probe says there are no run records, but `logs/` and `results/summary.json` do record execution and input hashes. The unmet verdict is instead because no exact lock or environment digest ties the run to its environment.
- **must/008 — `probe-overridden`:** the entry-point probe missed the top-level `analyze.py` and its documented full command in `results/report.md`; the script is a clear starting point.
- **must/009 — `mapping-questioned`:** the path probe found absolute paths in recorded output, while the item asks whether scripts use relative paths. `analyze.py` roots inputs and outputs at its own file.
- **must/014 and should/008 — `upstream-duplicate`:** these pinned checklist items ask the same question verbatim and share the same unmet finding.
- **must/015 — `probe-overridden`:** the probe left this unchecked; inspection shows a manifest exists, but it is range-based without a lock, so the answer is partial.
- **must/016 — `probe-overridden`:** the probe could not verify remote content; the authorized Git clone and annex retrieval plus all 54 URL/hash checks establish access for the stated scope.
- **must/017 — `probe-overridden`:** the replay failed because pre-existing Duct logs conflict, but `results/report.md` does document a command. The remaining gap is setup/obtaining instructions, so this is partial.

## Not checked

None of the 31 checklist items remains `not-checked`. The replay did not reach the analysis, which is recorded as an unmet reproducibility check rather than as a not-checked item. Cross-host portability and whether an anonymous researcher can retrieve the object were outside the stated access requirement and are not claimed.

## Goals and kind

**Assumption (not confirmed with a human):** this is a **study** whose goal is to assess whether increasing potential gain is associated with a greater vmPFC fMRI response in the supplied 54-person NARPS equal-indifference group, using fixed upstream maps and whole-brain-corrected inference. This understanding comes from `input/study-task.md` and `input/upstream-methods.md`. The study emphasis is on tracked result provenance, self-contained inputs and portable/replayable analysis.

## Scientific adequacy — separate from STAMPED

**Classification: supported.** The reported conclusion is a defensible lack of support for a positive vmPFC finding under the required whole-brain family-wise error threshold. The analysis includes all 54 supplied participants without exclusion, checks map identity, checks common image shape/affine and finite values, and limits the search to voxels represented in at least 49 maps. It uses 9,999 participant-level sign flips and the maximum positive t statistic over the full coverage mask. No voxel in the independently defined 10-mm vmPFC sphere passed whole-brain max-T correction; the descriptive mean is −0.0095 map units, with a 95% t interval [−0.0377, 0.0187]. The corrected positive findings are small posterior occipital components, not vmPFC.

This supports “no corrected evidence for the hypothesized positive vmPFC response in these supplied maps,” not “the true effect is zero.” The report properly identifies the symmetric-null assumption of sign-flipping, absent participant variance maps, and the fact that gain copes are normalized-regressor coefficients rather than change per currency unit; separate gain/loss upstream models also limit interpretation. The anatomical sphere is specified independently and used descriptively, not to evade the required whole-brain correction. Because the single replay stopped before analysis, this scientific classification rests on inspection of the retained unchanged code, maps, summary and report; the reported numerical results were not independently regenerated in this assessment.

## Replay, access and worker-stop attribution

The one authorized fresh-clone attempt failed before analysis because `duct` refused to overwrite four tracked log files already present in the clone. The runner had removed the comparison output candidates and fetched 58 annex payloads first. It did not compare regenerated scientific outputs. The full runner receipt and clone remain under `replay-workspace/`; see [replay-record.md](replay-record.md) and [2026-10-16-fresh-rerun.json](2026-10-16-fresh-rerun.json).

The worker-end-state receipt at `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-03/judgment-02/worker-end-state.json` (SHA-256 `0b9a32f0325f154a2bfff6b739d0c2d845d4f6dc1008890e0c9fdfdef339dee2`) records that the worker exited successfully at this commit with a clean status and the committed inventory. It supports worker credit for the committed code, outputs, logs and version-control state. Retrieval checks in this judgment establish the routes available at assessment time, but the receipt does not establish that the worker performed those checks; later coordinator preservation or annex activity is not credited to the worker.

## Checklist URL and provenance stamp

Checklist URL: [open the filled checklist](2026-10-16-url.txt). Canonical response: [2026-10-16-response.json](2026-10-16-response.json). Probe output: [2026-10-16-probes.json](2026-10-16-probes.json). Retrieval evidence: [access-retrieval.md](access-retrieval.md).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259bad`), on the object at commit `abf95b00c02fb55d16c4d269926c1428cedc0574`, 2026-10-16, OpenAI Codex API / GPT-6 (specific variant not supplied). The coordinator-supplied runner reported source commit `b86e37ff9115e37541fd47aca73f49e13b5110bb`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`, and `pixi.lock` SHA-256 `f8fff1394fbeaa2ab1c4993fceb0dd6463fe0c08c81fcda397f3e752a72c4249`. The exact model variant was unavailable from the harness.
