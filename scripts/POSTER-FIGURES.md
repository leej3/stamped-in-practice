# Scientific figures for STAMPED in Practice

This benchmark owns the scientific figure code, frozen inputs and provenance used by the poster.
The presentation repository keeps SVG and PNG display copies and a binding to the benchmark revision that produced them.
The current spatial figures use the 48 original research deliveries from rounds two and three of `narps-neutral-v1`: six analyses per condition per round.
The round-progression chart displays the existing retained primary outcome summaries for all three rounds.

## Reproduce the published figures

From the benchmark root, retrieve the annexed inputs using the repository's retrieval instructions and run:

```sh
pixi install
pixi run datalad get experiments/narps-poster/map-inputs
git submodule update --init assessment
pixi run datalad get experiments/retained-round-reporting/round-*/input.tar.gz \
  experiments/retained-round-reporting/round-*/analysis/judgments.jsonl \
  experiments/retained-round-reporting/round-*/analysis/issues.tsv
pixi run poster-figures
```

Rendering uses only the frozen local inputs.
No study submodules, participant images, research workers, new judgments or external services are needed once those payloads and the frozen assessor source have been retrieved.
The assessor is used only for its pinned checklist URL encoder; it does not run an assessment.
The root environment supplies NumPy, Matplotlib, SciPy and NiBabel; Nilearn is used when refreshing captured inputs.

The spatial figures were validated with the lock preserved on the companion [environment snapshot branch](https://github.com/leej3/stamped-in-practice/tree/codex/env-stamped-poster-analysis-20261016).
Retrieve that `pixi.lock` and use `pixi install --locked` when reproducing that exact environment.
Keep the lock ignored in ordinary task history.
Fonts use Arial when available and DejaVu Sans otherwise; byte-identical figure replay was checked with Arial.

The outputs are under [`experiments/narps-poster/figures/`](../experiments/narps-poster/figures/):

| File | Meaning |
| --- | --- |
| `narps-group-map.svg` | Original round-two run 09 group t map, native coverage and anatomical vmPFC proxy |
| `narps-spatial-agreement.svg` | Native positive-FWE detection frequency across 48 R2/R3 analyses, pooled by assigned condition |
| `narps-spatial-summary.json` | Shared support, per-run detection counts, round membership and condition frequencies |
| `round-progression.svg` | Scientific adequacy and evaluated checklist items met by condition across rounds one to three |
| `round-progression-manifest.json` | Summary and run input hashes, skill revisions, plotted values, interval methods, available denominators and rendering provenance |
| `narps-group-map-manifest.json` | Input, generator, software and output hashes for the example |
| `narps-spatial-manifest.json` | Input, generator, software, summary and output hashes for the spatial comparison |
| `poster-figure-manifest.json` | Portable export binding for presentation repositories |

PNG versions accompany all three SVGs.
The spatial and group-map figures use at least 28-point text at a width of 13.5 inches, retaining more than 24 points when placed at 12.5 inches.
The progression chart uses at least 24-point text at a width of 14 inches; display it at 1,344 CSS pixels or wider to retain that print minimum.
The individual tasks are `pixi run poster-group-map`, `pixi run poster-spatial-map` and `pixi run poster-progression`.
Their scripts accept `--inputs` and `--output` for isolated offline replay without overwriting retained outputs.
The progression renderer also accepts `--runs` for its original per-run measurements.
`pixi run poster-checklists` exports filled-checklist links and exact response copies under `experiments/narps-poster/checklists/`.

## Round-specific outcomes

The progression renderer reads [`poster-outcomes.json`](../experiments/retained-round-reporting/pooled/poster-outcomes.json) and [`run-outcomes.json`](../experiments/retained-round-reporting/pooled/run-outcomes.json), cross-checking original per-run values against the existing `round_conditions` rows.
It performs no new assessment or scientific analysis.
Scientific adequacy is the percentage of assessed primary judgments marked supported; this is distinct from support for the neuroscience hypothesis.
Its bars are 95% Wilson score intervals from SciPy's `binomtest(...).proportion_ci(method="wilson")`.
These intervals assume independent runs with a common success probability within each condition and round, conditional on the available judgments.
Checklist attainment is the equal-run mean of `met/(met+partial+unmet)` among available primary responses.
Not-checked and not-applicable items are excluded from that evaluated-item denominator, with their counts retained in the manifest.
Small points show the 68 individual valid primary scores; large markers and bars show the mean and plus/minus one sample standard deviation (`ddof=1`).
Sample SD describes observed worker-score variation, not a confidence interval or standard error.
Neither panel's bars capture judge disagreement, missing or excluded judgments, shared-host or model dependence, or other design uncertainties.

Each condition has six assigned workers per round.
Scientific n is five for round-two research discovery and round-three STAMPED, and six otherwise.
Checklist n is four for round-one baseline, five for those same two groups, and six otherwise.
Missing responses are not plotted as zero.
The lines connect fresh groups of workers and describe differences across rounds; they do not track individual workers or establish a causal skill effect.
Fixed horizontal offsets make coincident points and bars visible without changing their values; individual points use deterministic offsets ordered by run ID.
SD endpoints are not clipped to the percentage domain; the axis expands if needed.

The label “No supplied research skills” describes the baseline assignment; common runtime system skills remained available.
The scientific source records retain their original labels, while generated display summaries use the clarified presentation label.

## Filled checklists and the separate all-item score

The poster's pooled checklist table uses the app-compatible all-item mean, a separate measure from the evaluated-item progression plot.
For each valid primary response, that score is `100 * met / 31`.
Each condition's pooled value averages these unrounded percentages equally across admitted runs; missing responses are not zeroes.
The checklist app displays each individual score rounded to a whole percentage.

The [checklist lists](../experiments/narps-poster/checklists/README.md) retain all 72 run slots and link 68 valid scores to filled forms, with exact raw response JSON beside each link.
Four scores remain unavailable: round-one runs 16 and 23, round-two run 05, and round-three run 20.
Their original excluded responses and the retained reasons remain available for inspection.
No duplicate judgment substitutes for a primary.

The exporter joins the pooled run table to its selected primary judgment, verifies the retained archive and response hashes, and copies the canonical response bytes without changing an answer.
It verifies that each admitted response reproduces the original evaluated score, then invokes the encoder from frozen assessor commit `9852d8360f9519d21d11099b45f5deb8ba80cb28`.
All app links are newly derived display projections of those original answers.
This avoids missing URLs and the stale round-one run-08 URL, whose `must/005` value disagrees with its canonical response.
The recovered round-three run-19 response is selected from the retained archive's `corrections/` member.

The app maps met to Yes, partial/unmet to No, and not-checked/not-applicable to blank.
It drops evidence and assessor metadata, truncates reasons to 250 characters and shows reasons only for No. The exact raw response remains authoritative for verdict distinctions and evidence.
`checklists/index.json` provides both per-run score definitions, four pooled all-item means, friendly per-condition list links, validity and source identities.
`checklists/manifest.json` binds the encoder revision and files, original inputs, exporter and every output.
The reader-facing links use the named benchmark branch; the poster's import binding records the exact benchmark commit and file hashes.

`tests/test_poster_progression.py` checks reference Wilson endpoints, sample-SD interpretation, equal run weighting, source agreement and deterministic replay.
`tests/test_poster_checklist_export.py` checks all original response bytes, URL answers, scores, missingness, stale-link correction and deterministic export, and rejects an altered archive identity.

## Scientific meaning and coverage

The spatial comparison uses 168,285 voxels in the intersection of certified tested supports across all 48 original analyses.
Within this domain, each condition has the same denominator of 12 analyses.
Color shows the fraction with a native positive whole-brain FWE decision at alpha .05; gray means no positive detections, and hatching indicates unavailable shared coverage.
Unsupported locations are never filled with negative findings.
Analyses with zero detections remain in the denominator.

Each worker's primary correction and computation are retained as delivered.
Pilots, sensitivity analyses and assessment replays do not replace those primary outputs.
The saved fields include different standardizations and numerical results, so no assertion of identical t fields or pooled t-SD is made.
This is a descriptive comparison of delivered spatial decisions, not new group inference or a causal estimate of the assistance condition's effect.

The illustrative map comes entirely from `narps-neutral-r2-09`, the first STAMPED round-two delivery in run order with both a saved analysis mask and a saved anatomical vmPFC proxy.
It includes 54 participants and 9,999 sign flips for one-sided maximum-t correction.
Its 24 corrected positive voxels do not overlap its retained Harvard–Oxford vmPFC proxy.
The anatomical background comes from a retained round-three image and is used only for display.

## Frozen inputs and their identity

[`map-inputs/example/`](../experiments/narps-poster/map-inputs/example/) contains the illustrative run's t map, native analysis mask, corrected-positive mask, vmPFC proxy, display anatomy and provenance.
[`map-inputs/spatial/`](../experiments/narps-poster/map-inputs/spatial/) contains:

- `selection.json`: the adapter for each run's primary statistic, decision and support path, plus the retained native positive-voxel count.
- `spatial-inputs.npz`: all 48 per-run tested-support masks and positive decisions, their shared-support mask, the native affine and display anatomy.
  Array order follows the provenance `records` list.
- `provenance.json`: original capture and stop identities, assigned conditions, coordinator revisions, selected-file hashes and each support derivation.
- `sources/<run>/`: complete capture manifests, original stop records, condition assignments, closure bindings and any available delivery-package index.
  Readable copies of original scripts, reports and numerical summaries are under each run's `workspace/` directory.
  Captured Markdown is excluded from Snapper so the source bytes remain unchanged.

Native masks are used wherever retained.
Other supports follow the worker's recorded rule and matching participant-map identities, or are recovered exactly from finite nonzero statistics when the retained code guarantees zero outside the mask and the count equals the original reported mask size.
Round-two run 01 has five zero-statistic voxels with unresolved template-mask membership.
Its 196,115 other voxels are certified as tested by the saved code and field; only that certified subset contributes to shared coverage.
No currently installed template is substituted.
Each distinction is recorded per run in provenance.

Renderers verify hashes, geometry, support and result counts before writing figures.
The spatial numerical summary is recomputed from the NPZ on every render, with round-specific membership preserved behind pooled results.
`tests/test_narps_spatial_snapshot.py` checks source identities, original decision counts, denominators, the example maps and byte-identical offline rendering.
The earlier development-only prototype and its relocation records remain in repository history; they are not inputs to the current spatial figures.

## Refresh from preserved original deliveries

Capture is separate from rendering.
It reads completed, hash-bound original deliveries and their iteration closure records.
It never reads mutable research worktrees or executes the delivered analysis programs.

[`extract_narps_spatial.py`](extract_narps_spatial.py) accepts these arguments:

| Argument | Required layout or destination |
| --- | --- |
| `--runs-root` | Retained or restored launcher runs, each with `<run>/attempt-01/native/` |
| `--iteration-root` | The matching `iterations/narps-neutral-v1` checkout with round closure records |
| `--output` | Spatial candidate directory containing the reviewed `selection.json`; defaults to the canonical spatial-input directory |
| `--example-output` | Companion illustrative-map candidate directory; defaults to the canonical example-input directory |

The native directory must contain `worker-end-state.json`, `condition-assignment.json`, and `original-delivery/manifest.json`, with selected scientific payloads at their recorded paths under `original-delivery/content/workspace/`.
This can be the retained native capture layout or the same layout restored from a preserved delivery archive and its sidecar records.
The command does not retrieve or unpack archives automatically.
For archived delivery packages, unpack the original-delivery tree into that layout and restore the corresponding original stop and assignment records; do not substitute a later preservation checkout or a judge's replay outputs.

The current `selection.json` adapts all 48 primary file layouts.
The extractor checks each complete capture against its original stop receipt and the retained round closure binding.
Where a delivery-package index exists, it checks that binding too.
It verifies selected source bytes, participant payload identities, map geometry, support reconstruction and all native positive-decision counts.
A missing binding or inconsistent count stops capture rather than creating a zero observation.

For a candidate refresh, first copy the reviewed `selection.json` into a new spatial output directory, then run:

```sh
pixi run poster-capture-spatial \
  --runs-root /path/to/restored/runs \
  --iteration-root /path/to/iterations/narps-neutral-v1 \
  --output /path/to/candidate/spatial \
  --example-output /path/to/candidate/example
pixi run poster-spatial-map \
  --inputs /path/to/candidate/spatial --output /path/to/candidate/figures
pixi run poster-group-map \
  --inputs /path/to/candidate/example --output /path/to/candidate/figures
```

`poster-capture-example` invokes the same capture workflow because the example and spatial comparison share their provenance.
Omitting the two output options refreshes the canonical inputs.
Adding rounds or changing eligible scientific outputs requires reviewing the selection adapters, source bindings and condition denominators together; a planned allocation row is not an observed analysis.

## Export to the poster

Run `pixi run poster-figures` and copy the six SVG/PNG assets listed in `poster-figure-manifest.json` into the poster's display-assets directory.
Verify their SHA-256 values against that manifest and record the benchmark checkout revision in the presentation's binding.
The same binding includes the checklist index, readable lists, all original response copies and their export manifest.
Regenerate the manifest whenever its bound code or root Pixi manifest changes.

Keep scientific generators, input snapshots and provenance in this benchmark.
Reader-facing links should open the named benchmark branch and its source records; exact revisions and hashes remain in the machine-readable provenance.
