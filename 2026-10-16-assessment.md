# STAMPED assessment: NARPS gain group study

**Object:** `42e957201315aa8221ba60fbe614119e22639ce8` at `https://github.com/leej3/stamped-in-practice` (verified GitHub clone). **Assessment date:** 2026-10-16 UTC. The target HEAD was verified before inspection; the target checkout was not changed.

**MUST:** 9 met / 5 partial / 3 unmet / 0 not-checked / 0 not-applicable (17). **SHOULD:** 2 met / 1 partial / 5 unmet / 0 not-checked / 1 not-applicable (9). **MAY:** 4 met / 0 partial / 1 unmet / 0 not-checked / 0 not-applicable (5). No overall score is assigned.

## What to fix first

1. Track a frozen environment lock and a repeatable update procedure, then record that exact lock in each run record → makes the generated inference recreatable and its provenance attributable → `must/006`, `must/014`, `must/015`, `should/006`, `should/008`.
2. Publish retrievable annex content or document a working public retrieval route for every required artifact → a researcher currently retrieves the revision and all input maps, but not annexed result maps → `must/016`, `should/007`.
3. Add a top-level setup guide that explains how to install Pixi, create the environment and run the script on the declared platforms → the report has a command but readers must supply an undocumented host tool → `must/007`, `must/011`, `must/012`, `must/017`.
4. Handle absent map coverage as missing observations and report a sensitivity analysis using complete coverage or voxel-specific valid participant counts → the current 90% mask treats absent observations as zero and feeds them into the t statistics → scientific adequacy (not a checklist item).
5. Add a clean-environment check to the documented workflow → there is no successful fresh-clone replay or recurring check → `should/002`, `should/004`, `should/005`, `should/006`.

## What the project already does well

- It separates fixed inputs, analysis code, results and environment specification; the code uses paths relative to its root (`input/`, `scripts/`, `results/`, `pixi.toml`).
- The report is scientifically transparent about the standardized gain coefficient, absent first-level variance maps, broad atlas localization, uncertainty and the distinction between no corrected support and a true zero effect (`input/upstream-methods.md`, `results/report.md`).
- At the worker stop, the supplied complete receipt identifies this exact HEAD with an empty status, matching tracked inventory, and origin/con-hub refs at the same commit. The worker retained successful and failed run logs, including the final Duct record and earlier presentation failures (`logs/`, `logs/run-metadata.json`). Those refs establish Git publication at stop, but not public availability of annex payloads. The receipt hash matches the coordinator-supplied SHA-256; later coordinator preservation is not counted as worker work.

## Per-item table

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input`, `scripts/analyze_gain.py`, `pixi.toml` | Core inputs, script, environment and results are under one repository root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/judgment/2026-10-16-attempt-01/remote-retrieval/neurovault-map-attempt-02.json` | Maps are under input/data and all 54 source URLs in input/sources.json retrieved with matching byte counts and SHA-256. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `results/report.md` | Analysis libraries and Duct are declared in pixi.toml; the documented Pixi command invokes the script. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/worker-end-state.json`, `git status --short` | Worker-stop receipt records a clean index and worktree at the assessed commit. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex`, `.gitattributes` | Large binary maps and atlas files use git-annex pointers; the probe found 71 pointers and no oversized Git binary blobs. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `logs/gain-group-release-2026.10.15T21.48.19-53798_info.json`, `logs/run-metadata.json`, `pixi.toml` | Duct records exist, but logs/run-metadata.json names only a lock hash and no pixi.lock is tracked to identify the exact environment. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `results/report.md`, `probe:entry-point` | results/report.md gives a Pixi command, but no README or Makefile explains installing Pixi and setting up the environment. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md`, `scripts/analyze_gain.py` | The report names scripts/analyze_gain.py and gives its executable Pixi command. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | The tracked text scan found no host-specific absolute paths. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `scripts/analyze_gain.py`, `pixi.toml` | Every imported library and invoked analysis tool is declared in pixi.toml, including con-duct for duct. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `pixi.toml`, `results/report.md` | pixi.toml lists macOS arm64 and Linux x86-64, but the report does not explain the required Pixi host installation. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `pixi.toml`, `results/report.md` | The environment lists runtime packages and platforms, but no setup instructions or Pixi installation requirement are provided. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | pixi.toml is tracked with the analysis code. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/judgment/2026-10-16-attempt-01/lock-history.stdout` | No dependency update or lock regeneration procedure is documented; no tracked lockfile update exists. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `pixi.toml`, `logs/run-metadata.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/judgment/2026-10-16-attempt-01/tracking-audit.stdout` | pixi.toml uses ranges and wildcards; the referenced lock hash has no retrievable lockfile in the assessed commit. |
| must/016 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/judgment/2026-10-16-attempt-01/remote-retrieval/checkout.stdout`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/judgment/2026-10-16-attempt-01/remote-retrieval/neurovault-map-attempt-02.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/judgment/2026-10-16-attempt-01/remote-retrieval/annex-whereis.stdout` | A researcher can clone the exact GitHub commit and retrieve all 54 inputs from NeuroVault; annexed result maps have no public retrieval location. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/report.md`, `pixi.toml` | The report gives a Pixi run command, but does not explain how to obtain Pixi or recover the exact environment. |
| should/001 | T.2 | met | judgement | `probe:tree-clean`, `probe:large-in-annex` | Git tracks code and text while git-annex tracks large binary content in the same repository. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present` | No CI or other recurring check tests whether the documented route still works. |
| should/003 | M.1 | met | probe:modules-separated | `probe:modules-separated` | Inputs, code, derived results and environment are stored in separate directories or files. |
| should/004 | E.1 | unmet | probe:fresh-rerun+judgement | `logs/gain-group-release-2026.10.15T21.48.19-53798_info.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/judgment/2026-10-16-attempt-01/2026-10-16-fresh-rerun.json` | The only recorded analysis ran on the worker host; the fresh-clone attempt could not retrieve required annex inputs and did not execute. |
| should/005 | E.1 | unmet | judgement | `results/report.md`, `pixi.toml` | Pixi run reuses the project environment; the documented workflow does not create a disposable environment for each run. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `probe:ci-present`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/judgment/2026-10-16-attempt-01/2026-10-16-fresh-rerun.json` | No recurring environment rebuild or successful clean-clone test is recorded. |
| should/007 | D.2 | partial | judgement | `pixi.toml`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/judgment/2026-10-16-attempt-01/tracking-audit.stdout` | pixi.toml is archived, but no lockfile or built environment artifact is included. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/judgment/2026-10-16-attempt-01/lock-history.stdout` | No dependency update or lock regeneration procedure is documented; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/judgment/2026-10-16-attempt-01/remote-retrieval/neurovault-map-attempt-02.json` | N/A: no restricted data or software are present; all 54 source maps were publicly retrievable. |
| may/001 | M.2 | unmet | judgement | `git ls-files .gitmodules`, `probe:subdatasets-resolvable` | External data are represented by annex pointers and source URLs; no external dataset or software is linked as a Git submodule. |
| may/002 | M.2 | met | judgement | `results/report.md` | The report describes the relationship between fixed inputs, group analysis, outputs and anatomical reference. |
| may/003 | M.2 | met | judgement | `scripts/analyze_gain.py`, `pixi.toml` | The script reads input/data and writes results, with the environment separately specified. |
| may/004 | M.2 | met | judgement | `results/report.md`, `scripts/analyze_gain.py` | A Pixi command composes the environment, Duct capture and analysis script. |
| may/005 | M.2 | met | judgement | `results/report.md`, `input/study-task.md`, `input/sources.json` | The report, task brief, source manifest and script make the object navigable. |
## Flagged items

- `must/002` (`probe-overridden`): the probe left the item open because it found no submodules; review found the 54 inputs under `input/data`, source URLs in `input/sources.json`, and 54/54 NeuroVault downloads matching declared bytes and SHA-256.
- `must/006` (`mapping-questioned`): the derived-file probe reported no run record, but `logs/` contains Duct records. The item remains unmet because `run-metadata.json` gives only a lock hash and no tracked `pixi.lock` supplies that environment.
- `must/007` (`probe-overridden`): the probe found no README/Makefile, but `results/report.md` does include a reproduction command; setup is still incomplete, so the item is partial.
- `must/008` (`probe-overridden`): the entry-point probe missed the documented `scripts/analyze_gain.py` command; it is a clear starting point.
- `must/010` (`probe-overridden`): the probe left dependency completeness unchecked; inspection found the script imports and Duct command covered by `pixi.toml` (including `con-duct` for `duct`).
- `must/011` and `must/012` (`probe-overridden`): the command scan did not judge host requirements; the environment lists macOS arm64 and Linux x86-64, but the documentation assumes an installed Pixi executable and omits setup details.
- `must/015` (`probe-overridden`): the run-environment probe did not find an environment pin; inspection confirms only an orphaned lock hash, not a frozen lock artifact.
- `must/016` (`mapping-questioned`): the probe had not fetched the remote revision; the exact GitHub revision and all 54 inputs were retrieved, but annex result maps still resolve only to host-local stores, so access remains partial.
- `should/004` (`probe-overridden`): the fresh-clone action could not retrieve annex inputs and never ran the entrypoint; there is no successful fresh-environment test in the committed records.
- `must/014` and `should/008` (`upstream-duplicate`): the pinned checklist repeats the same environment-update question; both answers are unmet for the same missing procedure.

The probe output remains unchanged at [2026-10-16-probes.json](2026-10-16-probes.json); the response records the overrides and mapping questions.

## Not checked

No checklist item remains `not-checked`; all 31 have a verdict. The one authorized replay itself is `not-checked`: its same-host clone could not fetch 71 annex objects, including the two requested group maps, so it did not execute the documented command or establish output agreement. The full receipt is in [the replay record](2026-10-16-fresh-rerun.json) and `2026-10-16-attempt-01/replay/work/`. A fresh clone with retrievable annex content would settle execution. This local clone checks the recorded local retrieval route only; it establishes no cross-host portability.

Access recipient: a researcher with ordinary HTTPS access to GitHub and NeuroVault. The verified route was tested from the current macOS assessment host: an HTTPS GitHub clone at the exact commit plus HTTPS GETs of all 54 map URLs in `input/sources.json`. Coverage verified: code, metadata and all required participant maps (54/54 byte counts and SHA-256 values). `git-annex whereis` in that public clone identifies host-local copies for annexed result images and no public content URL; those required results were not verified accessible to the researcher, hence partial rather than met on `must/016`. This verifies those routes from this host, not cross-host portability. See `2026-10-16-attempt-01/remote-retrieval/` for commands, outputs and downloaded payloads.

The probe also reports an extra finding outside the pinned checklist: no reuse license is declared (`license-declared`, unmet). The `inputs-untouched` extra is not applicable because there are no linked modules. These extras do not change checklist totals.

## Scientific assessment (separate from STAMPED)

**Scientific adequacy: not supported.** The reported conclusion is that these maps show no whole-brain-corrected positive vmPFC evidence. The method otherwise has defensible elements: it includes the 54 intended participants, checks grid/finite values, uses a one-sample positive test with 5,000 participant-level sign flips and a whole-brain maximum-*t* correction, and identifies vmPFC independently with Harvard–Oxford Frontal Medial plus Subcallosal labels. It reports no corrected vmPFC voxels, a reference-region peak *t*(53)=4.19 with whole-brain *p*FWE=.801, and a descriptive mean 0.0062 (95% *t* interval −0.0204 to 0.0327). Its 24 corrected voxels are in three occipital-pole clusters, not vmPFC (`results/report.md`, `results/analysis_summary.json`, `results/whole_brain_fwe_clusters.tsv`).

However, the analysis treats zero-valued voxels as map coverage and then includes every participant at every voxel passing the 90% coverage threshold. Independent inspection of the 54 source maps verified from their recorded URLs found 12,939 of 210,968 tested voxels with incomplete coverage (49–53 of 54 maps); the code substitutes zero for absent observations there. The vmPFC reference includes 216 of 1,638 voxels with incomplete coverage, also zero-filled in participant ROI averages. All 24 reported significant voxels have full coverage, but the corrected maximum-*t* distribution was computed over the full mask including partially observed voxels. The report contains no missingness-aware sensitivity analysis, so the reported p-values and absence of a corrected vmPFC finding are not sufficiently supported by this group model. The coverage audit and its retained attempts are in `2026-10-16-attempt-01/nifti-coverage-audit-attempt-02.json` and `nifti-coverage-audit-attempt-03.stdout`.

The scientific conclusion should remain narrowly phrased as “no whole-brain-corrected support in this analysis,” not as proof of no vmPFC effect. The interval includes both signs and no equivalence margin was set. Coefficients are modulation by a standardized gain regressor, not change per currency unit; gain and loss were fit in separate upstream models, so this does not estimate a directly comparable gain-versus-loss slope. Participant variance maps are absent, so the unweighted group test is conditional on fixed first-level estimates and cannot use precision-weighted mixed-effects inference. QC cannot revisit upstream motion or fit diagnostics (`input/upstream-methods.md`).

**Supported reported findings, with those limits:** the model's reported whole-brain corrected foci lie in occipital pole and none lie in the named vmPFC reference; the report correctly avoids interpreting this as evidence of a zero effect. This classification does not adopt prior teams' answers as ground truth.

**Blinding limitation:** the retained files expose cohort labels and the target hypothesis. No treatment assignment was inferred, reported or used as grading evidence.

## Goals and kind

Assumption (not confirmed with a human): the goal is to answer the supplied NARPS Hypothesis 1 group-stage question using the 54 fixed participant maps and metadata, while reporting whole-brain-corrected evidence and the limits of the upstream model. The primary kind is a **study**: it combines external participant effects, analysis code and a group-level scientific report. This places emphasis on tracked inputs/results, executable analysis and environment portability.

## Checklist, stamp and response

[Open the filled checklist](2026-10-16-url.txt). The canonical, validated per-item record is [2026-10-16-response.json](2026-10-16-response.json); the decoded app payload is also retained at [2026-10-16-decoded-response.json](2026-10-16-decoded-response.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on `https://github.com/leej3/stamped-in-practice` at commit `42e957201315aa8221ba60fbe614119e22639ce8`, 2026-10-16 UTC, Codex assessment runner / GPT-6 (specific variant unavailable). The assessor runtime was verified by the supplied runner: environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`; details are in `2026-10-16-attempt-01/runner-check.stdout`. Probe output: `2026-10-16-attempt-01/2026-10-16-probes.json`. Worker-stop receipt: `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-08/judgment-01/worker-end-state.json` (SHA-256 `37b6cb7641223b20738096045a9b82ac7cadc864b4e196e7ac8235793949433b`).
