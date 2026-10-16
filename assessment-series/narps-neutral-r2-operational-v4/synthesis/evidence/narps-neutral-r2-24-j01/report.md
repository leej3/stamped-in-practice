# Independent assessment — NARPS potential gains and vmPFC activity

**MUST:** 4 met / 5 partial / 8 unmet / 0 not-checked. **SHOULD:** 0 met / 2 partial / 4 unmet / 2 not-checked / 1 not-applicable. **MAY:** 1 met / 1 partial / 2 unmet / 0 not-checked / 1 not-applicable. These are item verdicts, not an overall score.

**Capture:** canonical original manifest SHA-256 `492185653c9ab5f7f20b9e71eeb3f56ea536c40a27ac456aa5de569fa1ac8cef`; captured HEAD `4116f766db315cb4bfde25ce6ac75d672961906a`. Paths below are relative to that complete captured workspace unless explicitly identified as external records.

**Scientific adequacy: supported.** The worker’s bounded conclusion that these data do not support a positive vmPFC effect surviving whole-brain correction is supported by the reported analysis. The conclusion does not establish a zero effect.

## What to address first

1. Track the worker’s analysis, report and generated outputs, and link each result to a complete run record. The stop inventory shows these central artifacts were untracked, so the captured HEAD alone does not reproduce the delivered result (`must/004`, `must/006`).
2. Supply a complete, pinned environment and installation instructions, then link it from the run record. The report names versions for only some imported dependencies and says to use a “prepared” environment (`must/003`, `must/007`, `must/010`–`must/017`).
3. Publish a worker-controlled route that gives a researcher the full required artifact set. No worker retrieval route or remote is recorded (`must/016`; see `access-record.json`).

## What is already strong

- The scientific report states the target group, keeps all 54 supplied participant maps, documents geometry/finite-value checks, and reports the no-exclusion decision (`report.md`, `analysis.py`, `output/participant_qc.tsv`).
- The primary inference uses a one-sided sign-flip max-statistic test over the whole common-support mask and discloses its exchangeability/symmetry assumption, permutation count and seed (`analysis.py`, `output/results.json`).
- Inputs, analysis code and generated products have clear directories, the paths in the script are relative, and the supplied maps resolve to annex objects inside the root (`input/`, `analysis.py`, `output/`). The annexed source maps were coordinator-supplied; this is not worker credit for annexing them.

## Scientific assessment

The analysis is a defensible group-stage test of the 54 independent participant gain-effect estimates. It verifies per-map checksums and matching dimensions/affines, tests finite values, excludes nobody, and defines common support from nonzero coverage in at least 90% of maps. It smooths the maps at 6 mm and uses a one-sample positive t statistic with 5,000 participant sign flips and the maximum positive statistic across the full support mask. This supplies whole-brain family-wise error control as required by the brief. Its sign-flip interpretation depends on approximate symmetry/exchangeability of participant errors; the report makes that assumption visible (`analysis.py`; `output/results.json`).

The reported whole-brain maximum is outside the described vmPFC box (t=6.61, max-T FWER p=.0004); zero voxels in that box pass the FWER threshold. The descriptive vmPFC mean is −0.000061 model units, with 95% t interval [−0.01364, 0.01352] and unadjusted one-sided p=.504 (`output/results.json`). The approximate MNI-coordinate box is transparent and not used to restrict the primary correction family, though the anatomical label remains approximate (`report.md`; `analysis.py`).

The maps are participant contrast estimates, not standardized statistics; their gain modulator was normalized within person, and separate gain/loss models plus the fixed upstream task model condition their meaning. Thus the effect is not a BOLD slope per currency unit or a causal effect of changing money. First-level variance maps are absent, so the equal-weight group analysis cannot account for participant-specific first-level precision. These limits are correctly acknowledged in `input/upstream-methods.md` and `report.md`. Given the methods and explicit qualifications, the “no corrected support” conclusion is supported; it does not mean the true effect is exactly zero, and it does not establish absence under every defensible pipeline.

**Hypothesis outcome (verbatim from the worker report):** “We found **no whole-brain corrected support** for the predicted positive gain effect in vmPFC.”

## Replay and access

Replay was **not checked**. The delivered command is `python analysis.py` from the workspace root. Its prerequisites are described only as a “prepared Python environment”; the report lists Python and several package versions but no complete dependency declaration or installation route (including imports such as pandas and threadpoolctl). I therefore did not reconstruct from the assessor host or run the script. The planned scientific output selection and comparison rule, and the reason for not attempting the one permitted replay, are retained in `replay-record.json`. Shipped output files are inspected evidence, not replay evidence.

The intended recipient is a researcher reproducing the study. No worker-declared delivery route for the analysis and its results was present at stop; the operational Git remote list is empty. `input/sources.json` identifies data-provenance URLs, but it was supplied source metadata and is not a worker publication route. No host route was therefore tested. Required recipient coverage would include the maps and participant metadata, analysis script, report, generated outputs and usable environment specification. See `access-record.json`.

## Worker stop state and scope

The worker stop receipt records a complete, cleanly exited stop with no capture errors or omissions, HEAD `4116f766db315cb4bfde25ce6ac75d672961906a`, and the analysis script, report and output directory among untracked worker files. `output/` includes the report’s maps, tables, figures, log and notebook. The initial tracked commit supplies the scientific inputs and base project; its commit is not evidence that worker-generated results were committed. Later coordinator preservation does not earn worker-practice credit.

Inspection of the operational copy found no mismatch against its initial manifest among 1,110 workspace entries, except that `.git/annex/keysdb/db` changed during inspection. This is one of the specifically classified operational metadata files; its original SHA-256 was `f6f8fd7af99434db59fadc6da021051789c6aaa271ebf878c54dafc6c9fde5ca`, and its post-inspection SHA-256 was `233c0be3e02857e0fbf47b00b8a94de3e9126529bee41b2491286aef7372be80`. No logical database equivalence is claimed. The runner’s probe results and this metadata change are assessment observations, not worker evidence. The captured Git configuration contains an absolute hooks path; it was not followed. Replay helper policy disables original hooks in its environment overlay; the source configuration remains intact.

## STAMPED checklist

The pinned item responses and their evidence are in [2026-10-16-response.json](2026-10-16-response.json); scripted results are in [2026-10-16-probes.json](2026-10-16-probes.json). Probe misses for entry point and modules were reviewed against the complete untracked delivery. The entry-point probe was overridden because it only saw tracked paths; the report documents the command and root-level script. The modules probe was overridden because it likewise missed `analysis.py` and `output/`.

### Flagged items

- `must/007` and `must/008`: probe path was limited to tracked README/Makefile/script paths; complete delivery has a report-documented command and untracked script. Install instructions remain missing, so `must/007` is partial.
- `should/003`: the probe saw only tracked `input/`; the complete delivery also separates code at root and results under `output/`, but has no environment module.
- `must/014` and `should/008`: duplicate pinned question; both remain unmet because no environment-spec update process is declared.

### Not checked

- `should/002`: no repeated test record; a repeated manual or scheduled test history would settle it.
- `should/004`: no fresh-environment execution record; a completed isolated run would settle it.
- Replay: incomplete environment prerequisites prevent a faithful attempt.
- Access: no worker delivery route was recorded, so no route/host test was possible.

### Goals and kind

Assumption (no human guidance was attached): this is a **study** whose goal is to assess the positive parametric gain effect in vmPFC in the NARPS equal-indifference group using the fixed 54 participant maps and whole-brain-corrected group inference. This follows the coordinator-supplied `input/study-task.md` and the worker’s `report.md`; the scientific aim and the worker’s implementation are assessed separately.

Checklist-app link: [2026-10-16-url.txt](2026-10-16-url.txt). The response is the machine-readable record and carries the capture identity and original commit.

Assessment stamp: frozen external runner source commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`, checklist 0.3.1, Codex/GPT-6, 2026-10-16. Probe output: [2026-10-16-probes.json](2026-10-16-probes.json).
