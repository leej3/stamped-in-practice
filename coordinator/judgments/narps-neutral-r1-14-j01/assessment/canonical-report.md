# Independent assessment — NARPS potential-gain effect

## Scientific assessment

**Scientific adequacy: supported.** The reported conclusion is appropriately bounded: the analysis did not support a positive gain effect in vmPFC under the required whole-brain-corrected test. The reported hypothesis outcome is **no corrected vmPFC support**; this is not evidence that the true effect is exactly zero.

The worker analyzed 54 equal-indifference participants using supplied gain-effect contrast estimates, not participant t/z maps. The code checks each map's hash, cohort membership, finiteness and common shape/affine, then tests a positive one-sample group mean on the strict all-participant nonzero-coverage mask. Its 9,999 participant-level sign flips use the maximum positive t over 198,029 voxels for one-sided whole-brain FWE control. This is a defensible group model conditional on the supplied, run-averaged inputs; the report states the symmetry assumption for sign flipping and that participant variance maps are absent. The 10-mm sphere at MNI (0, 40, -10) gives an inspectable vmPFC operational definition without using it to replace whole-brain correction.

The reported results show no FWE-significant overlap with the vmPFC sphere. The descriptive sphere mean is -0.0061, with 95% t interval [-0.0342, 0.0221], which spans both signs. The 24 corrected voxels occur in small posterior clusters and do not support the vmPFC hypothesis. The report properly avoids interpreting the supplied normalized gain coefficients as currency-unit slopes and explains limits imposed by fixed upstream modeling, spatial localization, sample size and ROI choice. A lack of support here means the analysis did not establish the predicted positive vmPFC response; it does not establish no response.

A single permitted replay used the worker-documented command and the exact prepared interpreter path documented in `report.md`, on a fresh writable copy of the complete captured workspace. The selected generated files were `results/summary.json`, `results/fwe_clusters.csv`, `results/map_qc.csv`, `results/vmPFC_participant_values.csv` and `results/permutation_max_t.csv`. The frozen runner reports all five byte-identical after replay (rtol 1e-6 for tabular numerical comparison; JSON exact); runtime was 17.95 seconds. This supports reproducibility of those outputs in this host's prepared environment. NIfTI maps and figures were outside the helper's numerical comparison capability and are not claimed as replay-compared. See [replay record](replay/replay.json), [declared plan](replay/replay-plan.md), and preserved [stdout](replay/workdir/replay.stdout) and [stderr](replay/workdir/replay.stderr).

## Delivery integrity, attribution and scope

The manifest reports `capture_status: complete`, with no errors or omissions. The frozen replay adapter validated the capture SHA-256 `5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153` before and after the copied replay. The complete stopped workspace includes substantial uncommitted/untracked content: analysis code, report, maps and results. Thus the recorded Git commit (`ad3956ae64dcbdd1eec6af4ed21e0b168e478106`) is not the whole worker delivery. The worker stop receipt records process return code 0 and a complete inventory; Git probes and the receipt show the worker's analysis artifacts were untracked at stop. The retained task file matches the coordinator brief SHA-256 `e92bf2e0c0db4cc49688cce9f9dfff8a236fc4ec151c09961719f49f31310cc8`. Later coordinator preservation is not credited as worker tracking or publication.

The worker-stop receipt is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/runs/narps-neutral-r1-14/judgments/narps-neutral-r1-14-j01/attempt-01/worker-end-state.json`; the capture manifest is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/judge-targets/narps-neutral-r1-14-j01/manifest.json`. The original workspace was not modified. The captured `.git` is a directory; its config records an absolute hooks path. The replay helper disabled hooks only through an environment overlay in the replay copy, leaving captured config unchanged. No external `.git` pointer was followed. No delivery mismatch was found.

The worker-declared NeuroVault route in `input/sources.json` was checked from the assessment host: the collection API and one direct participant-map URL returned HTTP 200. This verifies only that host's route and the sampled endpoints, not access from other hosts. It covers source maps, not the complete report, analysis, generated results/figures and environment needed for reproduction. No worker-published route for the full delivery was established. See [access record](access-record.json) and retained [API](access-neurovault-api.txt) and [map](access-neurovault-image.txt) responses. The coordinator's delivery of the workspace is not evidence of worker sharing.

The retained `.entire` session prompt and event log reveal AI-assistant involvement and the common task context. This exposure is recorded but was not used as grading evidence. No treatment assignment was inferred or reported.

## STAMPED checklist

MUST: **5 met / 4 partial / 8 unmet / 0 not-checked** (17 items).

SHOULD: **0 met / 2 partial / 6 unmet / 0 not-checked / 1 not-applicable** (9 items).

MAY: **3 met / 2 partial / 0 unmet / 0 not-checked** (5 items).

These are per-item checklist verdicts, not an overall score. The frozen scripted probes are retained in [probes.json](probes/probes.json); probe evidence was interpreted against the complete stopped workspace, including untracked material. In particular, the entry-point probe did not see untracked analysis/report files; direct inspection establishes a script and report, so must/008 is met and must/007 is partial. The tree-clean probe establishes that important results were untracked, but does not by itself negate Git use; must/004 and should/001 are partial. The modules probe missed the code/results directories and is overridden to partial on should/003.

The main worker-practice gaps are an absent environment specification and dependency installation route, absent linkage between this run and an exact environment capture, and untracked analysis/report/results at stop. Positive evidence includes the annex-backed participant maps, relative paths in the script, transparent scientific reporting, the main analysis entrypoint, and retrievable source-map URLs.

The per-item evidence, reasons, probe sources and flags are in [response JSON](2026-10-16-response.json); it validates against checklist 0.3.1. The generated [checklist-app link](2026-10-16-url.txt) opens those answers. Not-checked was retained only where evidence was insufficient; none remained after direct inspection. should/009 is not-applicable because no restricted data or software component was identified.

### Stamp

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the captured study workspace at commit `ad3956ae64dcbdd1eec6af4ed21e0b168e478106`, 2026-10-16, Codex API / GPT-6. The assessed boundary is the original complete delivery verified by manifest SHA-256 `5e9f3c61bf3b4a0c12292ea55a48a22845d3c6bd27ee091592ef4c87e62ed153`, captured 2026-10-16T07:07:52.262235Z. Probe output: [probes/probes.json](probes/probes.json).
