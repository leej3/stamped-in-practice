# STAMPED assessment — NARPS Hypothesis 1 group analysis

**Assumption (not confirmed with a human):** This is a computational study whose product is a group-level report, figures, code and results answering whether potential gain is positively associated with vmPFC activity in the equal-indifference group. Kind: **study**. Assessment is of committed state `d90a335549f43007eac05902859224e6ce2eaada`; `git rev-parse HEAD` matched before work began.

## Verdict

**MUST: 8/17 met; 5 partial; 4 unmet; 0 not-checked.** A partial does not satisfy a MUST. **SHOULD: 1 met; 1 partial; 6 unmet; 1 not-applicable. MAY: 2 partial; 3 unmet.** No overall score is assigned. Full item evidence is in [the response JSON](2026-10-16-response.json), and the scripted results are in [the probes file](2026-10-16-probes.json).

## What to address first

1. Add root-level setup and usage documentation that explains how to install Pixi, obtain inputs and run the analysis. The current entry command works, but a reader must infer host setup (`results/report.md`, `pixi.toml`).
2. Pin and link the complete environment used for results. `pixi.toml` contains open version ranges and there is no `pixi.lock` at this commit; run logs identify selected package versions but not a complete environment (`logs/group_gaininfo.json`, `results/analysis_summary.json`).
3. Document the host and network requirements and how environment updates are made. The manifest declares macOS 14/Linux and packages, but the Pixi bootstrap and retrieval route remain assumed.

## What is already in place

The study keeps code, inputs, outputs, methods and run records under one Git root. Git-annex carries large maps and results; source URLs and checksums are recorded in `input/sources.json`. The report states the execution command, the result, uncertainty and upstream limitations. Results include maps, correction outputs, quality summaries and figures. In the authorized replay, 10 of 11 selected outputs were byte-identical.

## Per-item assessment

| Item | Verdict | Evidence and reason |
|---|---|---|
| must/001 | met | Inputs, code, environment, results and records are under one Git root (`git ls-files`). |
| must/002 | met | Annex pointers are inside the root; source URLs and checksums are recorded (`input/data/`, `input/sources.json`). |
| must/003 | partial | Python packages are declared, but the Pixi bootstrap tool is assumed on the host (`pixi.toml`, `results/report.md`). |
| must/004 | met | Git tracks project files; worker-stop receipt records a clean tree at this commit. |
| must/005 | met | Git-annex pointers track large content; Git stores the pointers rather than large binary blobs (probe output, `git ls-files -s input/data/…`). |
| must/006 | partial | Run record exists, but it does not identify a complete locked environment (`logs/group_gaininfo.json`, `pixi.toml`). The derived-file probe missed the run record. |
| must/007 | unmet | No root `README.md` or `Makefile` gives install and use instructions (`git ls-files`). |
| must/008 | met | `results/report.md` gives the command; `scripts/group_gain.py` ran in the fresh clone, producing 10/11 identical selected outputs. The entry-point probe missed this documented route. |
| must/009 | met | Script derives paths from its own file (`scripts/group_gain.py`; absolute-path probe). |
| must/010 | partial | Analysis libraries are declared, but Pixi itself and the retrieval/bootstrap expectations are external assumptions (`pixi.toml`, `scripts/group_gain.py`). |
| must/011 | partial | Platform declarations exist, but Pixi installation and network retrieval assumptions are not fully documented (`pixi.toml`, `results/report.md`). |
| must/012 | partial | Python and package requirements are listed; system bootstrap and data retrieval requirements are not (`pixi.toml`). |
| must/013 | met | `pixi.toml` is versioned with the code and data. |
| must/014 | unmet | No environment update/regeneration process is documented (`pixi.toml`). |
| must/015 | unmet | Open version ranges and wildcards do not define an exact environment; no lockfile is tracked at this commit. |
| must/016 | met | The hub ref resolves to the assessed commit; the replay retrieved and used the environment file and required inputs through the configured route. Recipient: researcher with authorized hub/annex access. Route verified: Git ref at `https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git`, with annex content from `annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp`. Coverage: code, `pixi.toml`, all 54 input maps and atlas assets needed for analysis; 11 output candidates were fetched for comparison. Host scope: same host. This verifies that route and required inputs, not cross-host portability. |
| must/017 | unmet | The report gives a `pixi run` command but does not explain how to install Pixi or set up the environment (`results/report.md`; no root README). |
| should/001 | met | Git versions code/configuration and annex pointers in one repository; `pixi.toml` declares DataLad and git-annex. |
| should/002 | unmet | No CI workflow tests the instructions (CI probe; `git ls-files`). |
| should/003 | partial | Inputs, code, results and environment have separate locations, but they are not independently managed modules (`input/`, `scripts/`, `results/`, `pixi.toml`). The probe treated directory separation as module separation. |
| should/004 | unmet | Authorized replay used a fresh clone on the same host, with no container runtime; it was not a clean VM, batch job or cloud instance (`2026-10-16-fresh-rerun.json`). |
| should/005 | unmet | `pixi run` uses a project environment; no per-run disposable environment is defined (`results/report.md`, `pixi.toml`). |
| should/006 | unmet | No CI or scheduled job reconstitutes the environment (`git ls-files`; CI probe). |
| should/007 | unmet | The object contains an environment declaration, not an archived resolved environment or executable artifacts (`pixi.toml`). |
| should/008 | unmet | No tracked environment update process is documented (`pixi.toml`). This duplicates must/014. |
| should/009 | not-applicable | N/A: the object declares public inputs and software only; there is no restricted component to isolate (`input/sources.json`, `pixi.toml`). |
| may/001 | unmet | Inputs use annex/URLs and software uses Pixi; no submodules are declared (`git ls-files`, `input/sources.json`). |
| may/002 | unmet | No document explains how separate components relate or can be recombined. |
| may/003 | partial | Directory boundaries are visible, but independent updates and compatibility are not specified. |
| may/004 | unmet | One script connects root inputs and outputs; there is no module composition mechanism (`scripts/group_gain.py`). |
| may/005 | partial | The report names the entrypoint and key outputs, but there is no root navigation guide (`results/report.md`). |

## Flagged items

- **must/006:** Probe classified derived outputs as lacking any run record. `logs/group_gaininfo.json` records the final command and resource use, so the answer is partial: the missing part is an exact environment identity.
- **must/008:** The probe did not recognize a script mentioned in the report. The documented command exists and replayed successfully, so the answer is met.
- **must/010:** The manifest is present, but a reading of actual imports and bootstrap requirements shows remaining host assumptions.
- **must/016:** The probe left retrieval partial. The exact hub ref and successful same-host replay support access to the spec and required inputs; this does not show cross-host portability.
- **should/003:** The probe measured directory placement; the item asks about modules. The layout is separated, but no independently managed module boundaries are present.
- **must/014 and should/008:** These checklist items duplicate the same environment-update requirement; both carry the upstream-duplicate flag.

## Not checked and extras

All 31 checklist items received a verdict; none remain `not-checked`. The scripted extras report `license-declared` unmet (no license declaration), `clone-weight` met (no oversized text blobs), and `inputs-untouched` not-applicable (no input movement during this assessment). The runner's initial environment check reported a locally changed assessment-runtime lock; this concerns the supplied assessor runtime and does not alter the target.

## Scientific assessment (separate from STAMPED)

**Adequacy: qualified.** The committed report and code provide defensible evidence that the supplied participant gain-effect maps do **not support a positive vmPFC effect after whole-brain correction**. The primary one-sample test includes all 54 equal-indifference participants, uses a common in-brain support mask and a one-sided test of positive effects, and applies Bonferroni correction across 186,400 voxels. Eleven voxels survive that correction, none in the independently selected bilateral AAL3v2 Frontal_Med_Orb mask. The descriptive vmPFC participant-mean estimate is −0.0078, with a 95% interval from −0.0343 to 0.0187 (`results/report.md`, `results/analysis_summary.json`, `results/vmPFC_summary.json`). These are effect estimates, not t/z scores or per-currency-unit slopes (`input/upstream-methods.md`).

The qualification is that the sign-flip max-T sensitivity analysis holds the observed standard error fixed while permuting signs. Since that denominator is not invariant to sign flips, the reported sensitivity p-values are not a conventional studentized sign-flip randomization test and should not carry confirmatory weight (`scripts/group_gain.py`). The primary parametric t test remains interpretable under independent participants and its distributional assumptions, which the report acknowledges. The data also omit participant variance maps, so equal-weight inference cannot propagate first-level uncertainty. No corrected vmPFC result is evidence of lack of support at this threshold, not proof of a zero effect or absence of smaller/heterogeneous effects. The reported positive voxels are posterior, outside the hypothesis ROI. The fresh replay reproduced all selected inferential maps and figures exactly; only the elapsed-time-bearing `analysis_summary.json` differed (`2026-10-16-fresh-rerun.json`).

## Worker stop and later preservation

The supplied receipt hash `b47ba8a8b064f19d836bf3ebc90e1c4dd355a56f6c7a29e8bfa81f83bccd52da` records worker exit code 0, clean status and HEAD `d90a335549f43007eac05902859224e6ce2eaada`. This supports credit for committing and tracking the delivered code, data pointers, results and logs before stop. The receipt inventory was compared file-by-file with the retained checkout (169 tracked files, zero mismatches). It does not independently establish that the worker published the revision or annex payloads; current coordinator-preserved remotes and this replay are reported separately and are not credited as worker actions.

## Assessor stamp and scope

Assessed using frozen `assess-alignment-with-stamped-principles` 0.1.0 and `stamped-conventions` 0.1.0 (checklist 0.3.1), through the coordinator-supplied runner. Runner check records source commit `b86e37ff9115e37541fd47aca73f49e13b5110bb`, runtime commit `3552d5003a2485b6405805236d5c54e7ed42f097` and lock SHA-256 `f8fff1394fbeaa2ab1c4993fceb0dd6463fe0c08c81fcda397f3e752a72c4249`. Model recorded as GPT-6; exact deployment identifier was unavailable. Scope: committed-state inspection, remote retrieval checks and one authorized fresh clone replay at the documented entrypoint. The fresh clone used the same host; no cross-host portability claim is made. No changes were made to the target.

Checklist: [open the filled STAMPED checklist](2026-10-16-url.txt).
