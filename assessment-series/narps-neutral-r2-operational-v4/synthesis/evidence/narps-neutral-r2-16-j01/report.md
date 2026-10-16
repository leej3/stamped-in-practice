# Independent assessment — NARPS gain effect and STAMPED practice

## Scientific assessment

**Scientific adequacy: qualified.** The group analysis is a defensible test of the stated positive gain-effect hypothesis conditional on the supplied participant maps. It uses the complete 54-person equal-indifference cohort, a one-sided intercept-only group model, and 5,000 sign-flip permutations with whole-mask maximum-*t* family-wise correction. The recorded checks cover input hashes, participant IDs, finite values, and common grids. The result is transparently limited by the intersection mask: only 198,029 voxels (21.9% of the grid) had finite nonzero estimates in every map, and upstream masks were unavailable to confirm that zeros always meant missing model support. The vmPFC definition is a narrow coordinate proxy, not a unique anatomical boundary; no corrected voxels fell in it. The maps are unweighted effect estimates with no participant variance maps, and the gain coefficients are not effects per monetary unit because the upstream gain modulator was variance-normalized. These limitations qualify the scope of the null result but do not invalidate the reported whole-brain-corrected inference.

**Reported hypothesis conclusion (verbatim):** The supplied maps do not support a greater gain-related response in vmPFC after whole-brain correction.

The positive corrected voxels were posterior occipital, outside the vmPFC proxy. The result means the supplied data did not provide whole-brain-corrected evidence for a positive gain effect in vmPFC under this analysis; it does not establish a zero effect, equivalence, or the absence of a smaller effect. The uncorrected proxy interval is descriptive and is not a second corrected hypothesis test. The report also appropriately notes that separate gain and loss models cannot recover a joint gain/loss contribution.

Scientific evidence is from the canonical capture `c14716c206718ffb8136a4586992f445eb47077fed10fc232fd26e5aa8109df1`, with capture-relative paths below: `content/workspace/REPORT.md` (file SHA-256 `162dfc1ce4304ae4467f2a518935ddf18cf38d21c1ce18cb2e5f235aa5c91e03`), `content/workspace/analysis/protocol.md` (`b020279c94225a9014a953b68f85b239e424868c330dc7e00e6d56c22939f8d9`), `content/workspace/analysis/run_analysis.py` (`9d15a2baaa4a5dd64a94824c223a995de7dbece35d319021ee9dccbbd6f89b2a`), `content/workspace/analysis/make_figures.py` (`f57b40306661c3fc7b06019e34fcd750d8bd9e2bb5bc2d3d0d692bd68af22bc8`), `content/workspace/analysis/validate_results.py` (`a8befb1f8c29b909775d1015745af04290bbb5434c65bb3d5d036ad83ca2c1e4`), `content/workspace/results/primary_summary.json` (`c310c804df8e086d55e541cc6b07f065e5c9e0aac767fbc6e3c1a6aaaf492c46`), `content/workspace/results/primary_vmPFC_proxy_summary.json` (`a2eb5107cbb79929ad3bbaf996bc902cb63dc1f7ad7664401161c8f00f7d06dc`), `content/workspace/results/primary_group_arrays.npz` (`bf7c168ba59217a88e2e0d423fca9f9397783686801b2dd97cbb4fd143867682`), `content/workspace/results/validation.json` (`4ab4ccbc71689a0e6ce01a33cc51cb78160cf4f1eb0537df3a6d031fa9726631`), `content/workspace/figures/primary_whole_brain_maxt.png` (`bd68f23a7d1e0fd3f66321dee021144e07c881754f6d79b12100edf2bcf5ae90`), and `content/workspace/figures/primary_vmPFC_proxy.png` (`f1c6899d3a7203e33082ee2d6d15aae28bca6765d0b683f686f81f54ea2ed41a`). The report and protocol contain the full method and interpretation; the summary and validation JSON give machine-readable results.

## STAMPED assessment

**MUST: 4 met / 4 partial / 9 unmet / 0 not-checked (17 total).**  
**SHOULD: 0 met / 3 partial / 5 unmet / 0 not-checked / 1 not-applicable (9 total).**  
**MAY: 1 met / 2 partial / 0 unmet / 0 not-checked / 2 not-applicable (5 total).**

### What to address first

1. Track the worker-produced report, analysis code, figures, and results in the project's version control → otherwise the Git snapshot does not identify the delivered scientific state → MUST/004, SHOULD/001.
2. Include a portable, pinned environment declaration and its setup instructions → the recorded route currently depends on a separately supplied absolute interpreter path → MUST/003, /006, /007, /010, /011–/017; SHOULD/006–/008.
3. Publish an authorized route to the complete project state, with the code, required inputs, and results covered → no worker-declared route to this delivery was found → access record; MUST/016 and the reproducibility items above.
4. Record an explicit input-support mask or provenance that establishes the meaning of exact-zero map voxels → this would strengthen the common-support inference and clarify its spatial scope → scientific limitation, not a separate checklist item.

### What the delivery does well

- It provides a clear analysis entrypoint, a detailed report, an analysis protocol, and participant-level QC and validation records in the complete stopped workspace (`REPORT.md`, `analysis/protocol.md`, `analysis/run_analysis.py`, `results/validation.json`; canonical capture cited above).
- The group inference uses whole-mask maximum-*t* correction and reports the cohort, mask rule, uncertainty, gain scaling, and limitations rather than treating the lack of vmPFC support as proof of no effect (`REPORT.md`, `analysis/run_analysis.py`, `results/primary_summary.json`).
- The captured inputs include all 54 effect maps and participant metadata, with checksums and source provenance (`input/sources.json`, `input/participants.tsv`). The annex representation was already present in the coordinator-supplied starting state; it is not credited as a worker action.

### Per-item results

See the item-by-item table in [`item-table.md`](item-table.md), generated from `response.json`. The frozen probes are retained in [`probes.json`](probes.json); their results are interpreted against the complete delivery, including untracked and ignored files.

### Probe disagreements and attribution flags

- **MUST/005:** the probe sees 54 annex pointers, but the tracked annex state belongs to the coordinator-supplied input commit. It is not evidence of a worker annex action.
- **MUST/006:** the probe did not recognize a run record; `results/runlog.md` does record the primary command, output, and listed package versions, so this is partial rather than not-checked. A complete environment specification is still absent.
- **MUST/007 and MUST/008:** the tracked-path probe missed untracked worker report/code. The complete delivery does include reproduction instructions and a clear `analysis/run_analysis.py` starting point; installation remains non-portable.
- **MUST/011 and /012:** the probe's command scan found no platform-specific command. The documented absolute shared-environment path and package list provide partial host/runtime disclosure, not a complete system/environment specification.
- **SHOULD/002:** absence of recognized CI did not settle this item. The worker log documents a pilot, a primary run, and a numerical validation, but not regular testing over time; partial.
- **SHOULD/003:** the probe scanned tracked paths only. The complete delivery separates `input/`, `analysis/`, `results/`, and `figures/`, but has no environment module; partial.

### Not checked

No checklist item remains not-checked. The replay is a separate measurement with a partial result, not a checklist verdict.

### Goals, kind, and emphasis

The stated goal is to assess a positive parametric potential-gain effect in vmPFC for the NARPS equal-indifference group using the supplied 54 participant maps, with whole-brain correction; this comes from the retained task at `input/study-task.md` and its methods context at `input/upstream-methods.md`. The object is a computational study. The assessment emphasizes tracked scientific state, complete inputs, environment capture, execution provenance, and access for a researcher following an authorized route.

### Access and worker-stop attribution

The intended recipient is a researcher using the worker-declared authorized route. No worker-declared delivery or publication route was found in the stopped workspace; no host was tested for retrieval. `input/sources.json` records where upstream maps and metadata originated, but that is input provenance, not a route to this worker's report, code, results, and environment. Required coverage is the complete delivered workspace: report, code, figures, results, participant metadata, and all 54 maps, together with a usable environment declaration. Coordinator delivery to the assessor does not establish worker access. See [`access-record.json`](access-record.json).

The worker-stop receipt records an exited worker with return code 0 at 2026-10-16T15:42:24Z and identifies the same complete canonical capture (receipt SHA-256 `d10a07af5580d7c9263773b648a7ed48ebc82a0965800cf2c3c8e988a143671f`). The original captured HEAD is `8c6a78dcf33d4e58f7f2b9e276b5c42bccb797fa`; the captured worktree has `REPORT.md`, `analysis/`, `figures/`, and `results/` untracked, so this commit does not contain the worker's scientific delivery. The commit message identifies its purpose as supplying materialized scientific inputs. Coordinator-created commits, annex state, retained artifacts, and access routes receive no worker-practice credit. The captured commit metadata contains a Codex co-author/runtime identifier; this assistance exposure is recorded only and was not used as grading evidence.

### Replay and measurement limits

Before execution, the declared command was the worker-documented absolute interpreter followed by `analysis/run_analysis.py --n-perm 5000`; only the nine primary files written by that script were selected for removal/comparison in a separate copy. The frozen helper made the copy from the canonical original delivery, preserved supplied inputs and source, disabled hooks only in the replay copy, used no adapter input retrieval, and completed in 84.9 seconds. Seven numerical outputs/tables were byte-identical, including the unthresholded *t* map, FWE map, group arrays, summary, QC table, and vmPFC proxy table. The replay invoked the documented first-stage command `analysis/run_analysis.py --n-perm 5000`. The report documents a three-command workflow that then runs `analysis/make_figures.py` and `analysis/validate_results.py`; those later steps were not included in this single replay attempt. The two selected PNGs therefore compare the first-stage figures against final figures that the worker later regenerated with `make_figures.py`; the differing dimensions are expected from these different plotting commands and do not indicate a change in inferential quantities. The frozen helper consequently reports **partial**, and this is an incomplete replay of the full documented sequence. No second attempt was made. The replay record, stdout, stderr, and RGB dimension comparison are retained in `replay.json`, `replay-copy/replay.stdout`, `replay-copy/replay.stderr`, and `figure-compare.json`. Replay is evidence about this assessor run, not worker action.

### Checklist link and provenance

Checklist URL: [`checklist-url.txt`](checklist-url.txt). Machine-readable judgments: [`response.json`](response.json). Scientific record: [`scientific-judgment.json`](scientific-judgment.json).

Produced with the frozen `assess-alignment-with-stamped-principles` assessor 0.1.0 and `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259bad`), on the canonical capture SHA-256 `c14716c206718ffb8136a4586992f445eb47077fed10fc232fd26e5aa8109df1`, original HEAD `8c6a78dcf33d4e58f7f2b9e276b5c42bccb797fa`, 2026-10-16. Probe output: `probes.json`. The response retains the capture manifest identity and original commit.

### Operational-copy integrity

The operational manifest has the same canonical SHA-256 `c14716c206718ffb8136a4586992f445eb47077fed10fc232fd26e5aa8109df1`. A corrected comparison of its 1,110 workspace entries against the inspection copy found no content, link, mode, index, ref, object, or configuration changes. The one allowed regular-file exception was `.git/annex/keysdb/db`; it is classified as operational metadata, and logical database equivalence was not established. The first custom comparison is retained with a note explaining its capture-root/workspace-root mapping error; it was not used as integrity evidence. Operational metadata changes are inspection observations, not worker actions.

Custom assessment-check errors are documented separately in [`assessment-errors.md`](assessment-errors.md), with their failed outputs retained. They were not treated as target behavior or as evidence for the scientific conclusion.

### Reference-limit scope

The supplied `judge-target.json` reference limits prohibit following the captured absolute/external skill links. I inspected the retained link and dependency-mapping records but did not follow those external targets or run Git through any external `.git` pointer. Conclusions about those linked resources are out of scope.
