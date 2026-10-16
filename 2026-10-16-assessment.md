# STAMPED assessment — NARPS potential-gain group analysis

**MUST:** 8 met / 5 partial / 3 unmet / 1 not-checked (17 total). **SHOULD:** 2 met / 0 partial / 6 unmet / 0 not-checked / 1 not-applicable (9 total). **MAY:** 3 met / 1 partial / 1 unmet (5 total). No overall score is assigned.

**Scope.** Assessed committed state `2ad7c466615141d11b81720ff97d61c2d7c23f73` in the target checkout, remote retrieval, and one authorized fresh-clone replay using `pixi run python scripts/analyze_gain.py`. The target HEAD was verified before inspection and remained unchanged. The assessment output, retrieval clone and replay clone are outside the target.

## What to fix first

1. Commit a frozen Pixi lock and record its identity in each run record; add a runnable dependency-update process → connects results to the exact software environment (**must/006, must/015, must/014, should/008**).
2. Add a short README with Pixi installation, supported host requirements, network-fetched atlas/template inputs, and the execution command → lets a new researcher prepare and run the project (**must/007, must/010–012, must/017**).
3. Preserve worker-time publication evidence and document the authorized annex retrieval route → establishes that a researcher could retrieve the complete object at delivery (**must/016**).
4. Make the report reproducible or record its generation step; the replay regenerated 12/14 candidate outputs, but did not recreate `results/report.md` and changed the timestamp-bearing `results/results.json`.
5. Test the documented workflow in CI and a fresh isolated environment → catches environment drift and tests the execution instructions (**should/002, should/004, should/006**).

## What the project already does well

- The target includes the full 54-person analysis cohort, source manifest, code, environment declaration, results and run logs under one Git root; the 59 large binary payloads use git-annex (`2026-10-16-probes.json`, `input/sources.json`).
- The report distinguishes participant copes from currency-unit slopes, justifies the whole-brain corrected test and anatomical ROI, and describes uncertainty and the absence of first-level variance maps (`results/report.md`, `results/results.json`).
- The analysis script checks cohort IDs, input checksums, finite values and image geometry before inference. The replay reproduced the main maps, tables and figures byte-for-byte (`scripts/analyze_gain.py`, `2026-10-16-fresh-rerun.json`).

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-tree -r HEAD` | All project files are nested under the checkout root. |
| must/002 | S.1 | met | judgement | `input/sources.json`, `scripts/analyze_gain.py` | The 54 maps and metadata are inside input/; the script resolves inputs relative to the checkout root. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `scripts/analyze_gain.py` | The analysis libraries are specified in the tracked Pixi environment. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-09/judgment-01/worker-end-state.json` | The worker-stop receipt records a clean tracked state at the assessed commit. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `2026-10-16-probes-2.json` | Git-annex tracks 59 binary payloads; none is a large Git blob. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `logs/group-analysis-releaseinfo.json`, `.gitignore`, `pixi.toml` | Duct logs record commands and exits, but no exact lock is recorded; pixi.lock is absent and ignored. |
| must/007 | A.1 | unmet | probe:entry-point | `git ls-files`, `results/report.md` | There is no README.md or Makefile with installation and usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md`, `scripts/analyze_gain.py`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-09/judgment-01/judgment/2026-10-16-fresh-rerun.json` | The report names pixi run python scripts/analyze_gain.py, and that script is the analysis entrypoint. |
| must/009 | P.1 | met | probe:no-abs-paths | `2026-10-16-probes-2.json` | The tracked-text scan found no host-specific absolute paths. |
| must/010 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `scripts/analyze_gain.py` | Analysis imports are declared, but Pixi itself and fetched atlas/template resources are not pinned as project dependencies. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `results/results.json`, `results/report.md` | Supported platforms and run host are recorded, but Pixi installation and network resource access are not documented as host prerequisites. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `results/report.md` | The environment lists Python and analysis packages and supported platforms, but omits Pixi installation and network setup. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | pixi.toml is tracked at the assessed commit. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `.gitignore` | No dependency-update or lock regeneration command is declared; pixi.lock is ignored and absent. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `.gitignore` | pixi.toml is available, but no committed lock or exact package snapshot freezes the environment. |
| must/016 | D.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-09/judgment-01/judgment/attempts/remote-checks/exit-codes.txt`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-09/judgment-01/worker-end-state.json` | Exact Git commit and all 59 annex payloads are retrievable now; the worker-stop receipt lacks remote-state evidence to attribute publication to the worker. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/report.md`, `pixi.toml` | The report gives the Pixi run command, but not how to install Pixi or obtain a frozen environment. |
| should/001 | T.2 | met | judgement | `git ls-tree -r HEAD` | Code, text, configuration and annex pointers are versioned in one Git repository. |
| should/002 | A.2 | unmet | probe:ci-present | `2026-10-16-probes-2.json` | No CI configuration regularly tests the documented workflow. |
| should/003 | M.1 | met | probe:modules-separated | `2026-10-16-probes-2.json` | Inputs, code, results and environment declarations occupy separate paths. |
| should/004 | E.1 | unmet | judgement | `logs/group-analysis-releaseinfo.json`, `/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-09/judgment-01/judgment/2026-10-16-fresh-rerun.json` | Recorded runs and the replay use the same host; no fresh container, batch job, clean VM or cloud run is evidenced. |
| should/005 | E.1 | unmet | judgement | `results/report.md`, `scripts/analyze_gain.py` | Pixi runs in its persistent project environment; the workflow does not create a disposable environment per run. |
| should/006 | D.2 | unmet | probe:ci-present | `2026-10-16-probes-2.json`, `pixi.toml` | No regular test rebuilds the exact environment used for a result set. |
| should/007 | D.2 | unmet | judgement | `git ls-files` | The environment is specified but package artifacts are not archived in the research object. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `.gitignore` | No dependency-update process is declared or tracked; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: all included data/software are public; there is no restricted component to isolate. |
| may/001 | M.2 | unmet | judgement | `.gitmodules`, `2026-10-16-probes-2.json` | No submodules link external source datasets or software; inputs are annexed in the root repository. |
| may/002 | M.2 | met | judgement | `results/report.md` | The report explains input, code, output and environment roles and links the figures. |
| may/003 | M.2 | partial | judgement | `scripts/analyze_gain.py`, `2026-10-16-probes-2.json` | Directories separate components, but they share one Git boundary and fixed paths in one analysis script. |
| may/004 | M.2 | met | judgement | `results/report.md`, `scripts/analyze_gain.py` | The documented Pixi command composes the environment, script, inputs and outputs. |
| may/005 | M.2 | met | judgement | `results/report.md`, `input/sources.json` | The report and source manifest explain the analysis and let readers navigate inputs and figures. |
## Flagged items

- **must/006 — `mapping-questioned`:** the probe found no run records, but committed duct logs do record commands and exits. The unmet verdict is instead because those records do not identify an exact frozen environment; `pixi.lock` is ignored and absent.
- **must/008 — `probe-overridden`:** the probe did not recognize the documented command in `results/report.md`; that command starts `scripts/analyze_gain.py`, which ran successfully in replay.
- **must/016 — `unverified-claim`:** full current retrieval succeeded, but the worker-stop receipt has no remote annex location/push timestamp. Current availability cannot establish worker publication at stop.
- **must/014 and should/008 — `upstream-duplicate`:** these two checklist questions are verbatim duplicates; both use the same evidence.

**Extra finding outside the pinned 31 items:** the probe found no license or reuse terms in the object; `license-declared` is `unmet`.

## Not checked

- **must/016:** the exact Git commit and all annex payloads were retrievable during this assessment, but publication by the worker before the recorded stop is not established. A worker-time remote location log or publication receipt would settle attribution.

## Goals and kind

The supplied task asks whether greater potential gain produces a greater vmPFC response in the equal-indifference group, using the fixed 54 participant maps, whole-brain correction, and a concise report with supporting code/results. These goals come from the retained task brief, whose SHA-256 matches `e92bf2e0c0db4cc49688cce9f9dfff8a236fc4ec151c09961719f49f31310cc8`. No human was attached, so this is an explicit, unconfirmed assumption. The primary kind is **study**: a scientific question answered through group analysis and reported results. The emphasis is on tracked inputs and result provenance, an actionable entrypoint, a portable environment and retrievable components.

## Scientific assessment (separate from STAMPED)

**Scientific adequacy: supported, with a bounded conclusion.** The analysis supports the reported conclusion that these data do not provide evidence for a positive vmPFC gain effect under whole-brain family-wise correction. It does not establish that the true effect is exactly zero.

The primary test is a one-sided one-sample group model over 198,029 voxels with 10,000 sign flips and max-t whole-brain FWE correction at α=.05. The report defines vmPFC independently of observed effects as bilateral AAL SPM12 medial orbitofrontal parcels, resampled to the supplied MNI152NLin2009cAsym maps and intersected with common coverage. There are 24 FWE-significant positive voxels, in posterior patches; none overlaps the ROI. In the ROI, the mean participant cope is −0.0079 (95% t interval −0.0346 to 0.0188; n=54); the one-sided uncorrected p=.723 is explicitly descriptive. These findings do not support a positive vmPFC response.

The quality checks retain all 54 intended participants and check map identity, dimensions, affines and finite values. The common mask uses voxels nonzero and finite in all maps; this assumes zero-valued locations indicate no coverage, so any meaningful exact zeros would be excluded. Sign-flip inference assumes a sufficiently symmetric null distribution. Participant variance maps are not supplied, so the group analysis is unweighted and does not propagate first-level uncertainty. The gain regressor was mean-centered and variance-normalized upstream, so copes are not per-currency-unit slopes. The report correctly treats the ROI test as descriptive and says absence of corrected voxels is not evidence of an exactly zero effect. The figures are legible and distinguish the uncorrected display map from corrected whole-brain findings.

Evidence: [`results/report.md`](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-09/targets/judgment-01/results/report.md), [`results/results.json`](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-09/targets/judgment-01/results/results.json), [`scripts/analyze_gain.py`](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-09/targets/judgment-01/scripts/analyze_gain.py), and [retrieved group-inference figure](/Users/johnlee/.local/state/stamped-in-practice/narps-v1/narps-r1-09/judgment-01/judgment/attempts/remote-checks/retrieval-clone/results/figures/gain_group_inference.png).

## Retrieval and worker-stop attribution

**Intended recipient:** a researcher authorized to use the recorded Git/annex route; anonymous access was not required. **Git route:** `https://github.com/leej3/stamped-in-practice.git`, where `refs/heads/codex/narps-r1-09` resolved to the exact assessed commit. **Annex route:** `con-hub` at `https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git` with annex endpoint `annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp`. In a separate clone, after setting that route, retrieval succeeded for all **59/59 annex payloads** (participant maps, annexed result images/maps and run usage data); the other **42/42 regular files** matched the receipt inventory. The declared source-manifest entries were also checked: 57/57 retrieved files matched their listed SHA-256 values. This verifies current access to the required object. The retrieval and replay occurred on the same host, so they do not establish cross-host portability.

The supplied worker-stop receipt hash matches the coordinator-supplied SHA-256. It records return code 0, a clean worker index/worktree, the requested HEAD, and 101 paths. Its inventory matches the retained checkout: 42 regular-file hashes match, and the 59 annex payload hashes match the retrieved contents. This supports attribution of the delivered tracked artifacts to the worker. The receipt does not capture remote annex publication time or remote configuration at stop. Current Git/annex retrieval is therefore recorded as an observed access result, not credited as proven worker publication. No treatment assignment is inferred or reported. The named analytic cohort is visible in the supplied task and metadata; it was used only to check the requested cohort.

## Checklist, response and provenance

Checklist link: [open the completed checklist](/Users/johnlee/.local/state/stamped-in-practice/narps-r1-09/judgment-01/judgment/2026-10-16-url.txt). Machine-readable answers: [response JSON](/Users/johnlee/.local/state/stamped-in-practice/narps-r1-09/judgment-01/judgment/2026-10-16-response.json). Probe output: [probes JSON](/Users/johnlee/.local/state/stamped-in-practice/narps-r1-09/judgment-01/judgment/2026-10-16-probes.json). Replay receipt: [fresh-rerun JSON](/Users/johnlee/.local/state/stamped-in-practice/narps-r1-09/judgment-01/judgment/2026-10-16-fresh-rerun.json). All attempts, commands, stdout/stderr, retrieval clone and replay workspace are retained under [`attempts/`](/Users/johnlee/.local/state/stamped-in-practice/narps-r1-09/judgment-01/judgment/attempts/) and [`replay-work/`](/Users/johnlee/.local/state/stamped-in-practice/narps-r1-09/judgment-01/judgment/replay-work/).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on the target at commit `2ad7c466615141d11b81720ff97d61c2d7c23f73`, 2026-10-16, Codex API / GPT-6 (exact runtime identifier unavailable). Probe output: `2026-10-16-probes.json`.
