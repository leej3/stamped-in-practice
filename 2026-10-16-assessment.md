# STAMPED assessment: NARPS gain-effect study

**Assumption (not confirmed by a human):** The goal is the coordinator-supplied group-stage NARPS Hypothesis 1 analysis; the primary object kind is **study**. The report assesses committed state `284c8768140cbd816d983f8bd2697bd9b541eb25`, verified at target `HEAD`.

**Verdicts:** MUST: 16 met / 1 partial / 0 unmet / 0 not-checked (17). SHOULD: 4 met / 1 partial / 2 unmet / 1 not-checked / 1 not-applicable (9). MAY: 5 met / 0 partial / 0 unmet / 0 not-checked / 0 not-applicable (5). A partial MUST does not satisfy that item; there is no combined score.

## What to address first

- Link every retained result set, including interim snapshots, to its exact code and environment pins; the final replay is pinned, while historical result sets are not (must/006).
- Add a recurring check that rebuilds the documented workflow from a clean environment; no CI is present, and the per-run environment is reused (should/002, should/005, should/006).
- Treat the failed replay in this assessment as a harness issue: its cleanup removed tracked `input/participants.tsv`. The one-attempt limit was used; no second replay was run.

## What is already strong

- The analysis plan defines its participant-level estimand, assumptions, mask and one-sided whole-brain max-t permutation correction before interpreting results (`protocol/analysis-plan.md`).
- The report describes map scaling and upstream limits, shows uncertainty and post-selection caveats, and keeps the coordinate-defined vmPFC box descriptive (`results/report.md`, `results/summary.json`).
- Inputs, code, outputs and environment are organized separately; 54 input maps and large results use annex, and the documented entry point is an explicit Pixi task (`README.md`, `pixi.toml`, probe record).

## Per-item results

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `README.md` | The study files are bounded by one Git root; README documents input, code, results and environment components. |
| must/002 | S.1 | met | probe:subdatasets-resolvable | `.gitmodules` | The linked skills module resolves remotely; input maps are retrieved through the annex route. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `.gitmodules` | Pixi specifies external packages and skills is a pinned Git submodule. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git ls-files`, `git status --porcelain` | The committed text, code, configuration, and results use Git; worker stop receipt reports a clean index. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `git ls-tree -r -l HEAD`, `.datalad/config` | Large NIfTI inputs and derived maps use git-annex rather than Git blobs. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+judgement | `results/replay.json`, `results/first_primary/summary.json`, `logs/20261016T-final-validation2info.json` | The final replay record pins its code commit and lock hash; earlier result snapshots lack per-run environment linkage. |
| must/007 | A.1 | met | probe:entry-point | `README.md`, `scripts/group_analysis.py` | README gives Git, git-annex and Pixi setup plus reproduction commands. |
| must/008 | A.1 | met | probe:entry-point | `README.md`, `scripts/group_analysis.py` | README names scripts/group_analysis.py through the group-analysis Pixi task. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | The probe found no host-specific absolute paths in tracked text. |
| must/010 | P.1 | met | judgement | `pixi.toml`, `scripts/group_analysis.py`, `scripts/validate_results.py` | Imports used by the analysis scripts are provided by pixi.toml; nilearn supplies nibabel and the listed scientific stack. |
| must/011 | P.1 | met | judgement | `README.md`, `pixi.toml` | README states macOS 14+ and Linux-64 support; Pixi records both platforms and no extra host services or mounts are required. |
| must/012 | P.2 | met | judgement | `README.md#Install`, `pixi.toml` | README lists Git, git-annex and Pixi; the Pixi manifest supplies project dependencies. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml`, `skills` | pixi.toml is tracked alongside the code. |
| must/014 | P.3 | met | judgement | `README.md#Install`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-02/worker-end-state.json`, `2026-10-16-remote-checks.stdout` | README documents dependency updates and lock retention; the worker-stop receipt and remote show the environment snapshot branch. |
| must/015 | D.1 | met | judgement | `results/replay.json`, `2026-10-16-remote-checks.stdout`, `README.md#Install` | The recorded lock SHA is associated with a retrievable Git environment branch. |
| must/016 | D.1 | met | judgement | `2026-10-16-fresh-rerun.json`, `2026-10-16-remote-checks.stdout` | The hub Git and annex routes retrieved the assessed revision, all 54 maps and annexed results for an authorized researcher. |
| must/017 | D.1 | met | judgement | `README.md#Install` | README explains how to check out the environment branch, install locked dependencies, and retrieve annexed maps. |
| should/001 | T.2 | met | judgement | `.gitmodules`, `README.md#Inputs and provenance`, `pixi.toml` | The code, linked module and annex payloads use Git-family versioning. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present` | No CI configuration regularly checks the documented workflow. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `scripts`, `results`, `pixi.toml` | Inputs, scripts, results and environment are separated into distinct directories or manifest. |
| should/004 | E.1 | not-checked | probe:fresh-rerun+judgement | `2026-10-16-fresh-rerun.json`, `README.md#Run` | The single replay attempt was inconclusive: cleanup removed tracked input/participants.tsv before the entry point ran. |
| should/005 | E.1 | unmet | judgement | `README.md#Run`, `pixi.toml#tasks` | Pixi tasks reuse a checkout-local environment; the documented route does not create a disposable environment per run. |
| should/006 | D.2 | partial | probe:ci-present+judgement | `results/replay.json`, `2026-10-16-fresh-rerun.json` | One recorded locked replay succeeded, but no recurring check exists; this replay was blocked by harness cleanup. |
| should/007 | D.2 | met | judgement | `README.md#Install`, `2026-10-16-remote-checks.stdout` | The exact lock is archived on a companion Git branch in the same research repository. |
| should/008 | D.2 | met | judgement | `README.md#Install`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-11/judgment-02/worker-end-state.json` | The environment update and tracked lock process is documented and represented by the worker environment branch. |
| should/009 | M.4 | not-applicable | judgement | — | N/A: the object declares no restricted data or software; the restricted-component property has no instance here. |
| may/001 | M.2 | met | probe:subdatasets-resolvable | `.gitmodules` | The external skills repository is linked as a pinned submodule. |
| may/002 | M.2 | met | judgement | `README.md` | README maps the input, code, results and environment components and explains how to run them together. |
| may/003 | M.2 | met | judgement | `README.md#Run`, `pixi.toml#tasks` | Inputs, analysis scripts, outputs and environment can be updated in separate directories or branch while composed by Pixi tasks. |
| may/004 | M.2 | met | judgement | `.gitmodules`, `README.md#Inputs and provenance`, `pixi.toml#tasks` | Git submodule and annex links compose with the Pixi task entry point. |
| may/005 | M.2 | met | judgement | `README.md` | README links the analysis plan, fixed upstream methods and input provenance and describes outputs. |

## Additional probe findings

- `license-declared`: unmet extra finding; no reuse licence is declared in the tracked object.
- `inputs-untouched`: not checked by the probe because the linked `skills` module was not initialized in the assessed checkout.
- `clone-weight`: met extra finding; no text blob exceeds 10 MiB.

## Flagged items

- **must/006 — probe-overridden:** the derived-file probe missed `results/replay.json`, which pins the final replay, but older retained result snapshots still lack per-run environment linkage; verdict partial.
- **should/004 — probe-overridden:** the replay helper returned unmet after deleting `input/participants.tsv` from its fresh clone as a shipped output. This is inconclusive about the object, so the item is not-checked.
- **should/006 — probe-overridden:** the no-CI probe misses the worker-retained successful locked replay; one replay is evidence of a test, not recurring reconstitution, so the verdict is partial.
- **must/014 and should/008 — upstream-duplicate:** these checklist items ask the same question; the same environment-update evidence is intentionally repeated.

## Not checked

- **should/004:** a valid fresh-environment test would require preserving `input/participants.tsv` during cleanup and completing the documented entry point. The single authorized replay attempt has been used.

## Goals and kind

The assumed goal is the supplied question about whether potential gain has a positive group effect in vmPFC for the equal-indifference cohort, conditional on fixed participant maps. This is a **study** because the product is a scientific answer supported by analysis and results. The assumption was not confirmed because no human is attached.

## Scientific assessment (separate from STAMPED)

**Scientific adequacy for the reported conclusion: supported.** The defensible conclusion is that this analysis found **no whole-brain-corrected support for a positive vmPFC effect** in the supplied contrast. That is a supported absence of a positive finding under the stated model, not evidence of an exactly zero effect.

The analysis uses all 54 independent participant maps, treats them as unstandardized contrast estimates rather than t/z statistics or currency-unit slopes, and documents the upstream gain-modulator normalization and absence of participant variance maps (`input/upstream-methods.md`, `protocol/analysis-plan.md`). It applies a one-sided max-t sign-flip correction across 196,120 common-mask voxels, with the sign-symmetry assumption stated. The vmPFC box is explicit and descriptive; it does not shrink the correction family.

**Reported conclusion:** zero of 23 positive max-t FWE-significant voxels lie in the vmPFC box. The positive foci are posterior occipital. The descriptive vmPFC-box mean is −0.0022 map units (95% t interval −0.0215 to 0.0172); the selected vmPFC-box peak has max-t FWE p=.791. The uncorrected selected-peak result is correctly identified as post-selection and not used as support (`results/report.md`, `results/summary.json`, `results/selected_vmPFC_voxel.json`).

**Supported findings:** the supplied maps do not support a positive vmPFC effect after whole-brain correction. They do show 23 corrected positive voxels elsewhere, including a maximum t(53)=6.62 with familywise p=.0007; those posterior foci do not support the vmPFC hypothesis. Non-significance does not establish equivalence to zero, exclude an effect below available precision, or compare gain sensitivity with loss sensitivity. The normalized gain estimates are not per-currency-unit slopes, and participant-level variance maps are absent.

## Access, replay and worker attribution

**Access recipient and route:** a researcher using the declared authorized hub route; anonymous access is not required. The route is the hub Git remote `https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git` plus its `annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp` content endpoint. Remote checks resolved the assessed code commit and the environment branch. The retained worker replay logs describe a fresh public clone, 54 participant maps, validation and figures; the current runner clone contained 54 map files and logged annex retrieval before cleanup. This was a same-host check and does not establish cross-host portability. The worker-retained `results/replay.json` and `logs/20261016T-published-replay-*` are evidence of the worker's pre-stop retrieval and replay; present-day remote checks establish current reachability only.

**Authorized replay for this judgment:** one fresh clone, using the documented `pixi run group-analysis` entry point, on the same host. The command exited 1 because the runner's output-cleanup list included and removed `input/participants.tsv`; the replay JSON records its hash under `outputs_shipped`, and the clone then raised `FileNotFoundError`. The workspace is retained at `fresh-rerun-work/clone`; no retry was made. This run therefore does not verify successful reproduction or another-host portability.

**Worker stop:** the supplied receipt (SHA-256 `1f87c35600472021177124e6da4b93f2b2161975a2376d85e0f07d60265a72a6`) records a clean exit at 2026-10-16 04:17:40 UTC, return code 0, and the requested HEAD. Its 246 Git index entries exactly match the assessed checkout's index. It also records the environment branch ref. Worker-authored reports and logs are assessed as retained artifacts; later preservation is not used to attribute work to the worker. The receipt does not capture annex transfer timing, so publication credit rests on the retained pre-stop published-clone logs, not the later remote check.

## Checklist URL and provenance

[Open the completed checklist](2026-10-16-url.txt). The canonical machine-readable record is [2026-10-16-response.json](2026-10-16-response.json); raw probe findings are [2026-10-16-probes.json](2026-10-16-probes.json), and the replay receipt is [2026-10-16-fresh-rerun.json](2026-10-16-fresh-rerun.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on commit `284c8768140cbd816d983f8bd2697bd9b541eb25`, 2026-10-16, Codex API / model not exposed by harness. Frozen runner pin: assessment source `b86e37ff9115e37541fd47aca73f49e13b5110bb`, environment `3552d5003a2485b6405805236d5c54e7ed42f097`. Probe output: [2026-10-16-probes.json](2026-10-16-probes.json).
