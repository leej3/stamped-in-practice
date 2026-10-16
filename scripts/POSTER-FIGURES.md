# Scientific figures for STAMPED in Practice

This benchmark owns the scientific figure code, input snapshots and provenance used by the poster.
The presentation repository keeps SVG and PNG display copies of the two figures and a binding to the benchmark revision that produced them.
The existing assessment and reported-region figures remain separate; their historical source snapshots under `synthesis/analysis/` are unchanged.

## Reproduce the published figures

Run from the benchmark root:

```sh
pixi install
pixi run datalad get experiments/narps-poster/map-inputs
pixi run poster-figures
```

Rendering uses only the frozen local inputs.
No study submodules, participant images, external services, research workers or new assessments are needed.
The root environment supplies NumPy, Matplotlib and NiBabel; Nilearn is used when refreshing the captured inputs.

For the exact validated environment, retrieve `pixi.lock` from the companion [environment snapshot branch](https://github.com/leej3/stamped-in-practice/tree/codex/env-stamped-poster-analysis-20261016) and run `pixi install --locked` before rendering.
Keep that lock ignored in ordinary task history.
Font rendering follows Arial when available and DejaVu Sans otherwise; the migration was verified with the same Arial font as the poster.

The outputs are under [`experiments/narps-poster/figures/`](../experiments/narps-poster/figures/):

| File | Meaning |
| --- | --- |
| `narps-group-map.svg` | Illustrative group t map from development run 09; gray anatomy outside shared participant coverage |
| `narps-spatial-agreement.svg` | Corrected-positive frequency across the retained development runs, grouped by assistance condition |
| `narps-spatial-summary.json` | Recomputed support counts, detection frequencies and t-field agreement |
| `narps-group-map-manifest.json` | Input, generator, software and output hashes for the example |
| `narps-spatial-manifest.json` | Input, generator, software, summary and output hashes for the spatial comparison |
| `poster-figure-manifest.json` | Portable export binding for presentation repositories |

PNG versions are also generated and included in the portable export binding.
Both SVGs use at least 24-point text at a width of 13.5 inches.
The individual tasks are `pixi run poster-group-map` and `pixi run poster-spatial-map`.
Their scripts accept `--inputs` and `--output` for isolated replay without overwriting the retained outputs.

The current development pool contains twelve completed NARPS analyses, three per condition.
The spatial comparison uses 184,543 voxels in the intersection of all twelve native analysis masks and all-participant nonzero coverage.
Outside that support is missing comparison coverage, never a negative finding.
The figure retains each worker's native primary whole-brain correction: Bonferroni for runs 01/02 and permutation max-T for the other runs.
The t fields agree to numerical precision; differences in corrected detections describe analysis choices on the same participant data.

## Frozen inputs and their identity

[`map-inputs/example/`](../experiments/narps-poster/map-inputs/example/) contains the run-09 t map, coverage, corrected mask, anatomical region, anatomical background and source records.
Its original capture also retains eight historical summaries; only run 09 supplies the illustrative image.
[`map-inputs/spatial/`](../experiments/narps-poster/map-inputs/spatial/) contains the compact NPZ and its provenance.
The NPZ preserves all twelve native support masks and corrected-positive decisions, together with exact saved t values on shared support and anatomical context.
Identical t fields are stored once, with a per-run index; no rounding or averaging replaces the original values.

Renderers verify input hashes, shared-support rules and result counts before writing figures.
The spatial summary is recomputed from the NPZ on every render.
[`map-inputs/migration.json`](../experiments/narps-poster/map-inputs/migration.json) preserves the original poster repository revision and source hashes from this relocation.

## Refresh from retained research objects

Input capture is a separate, deliberate operation.
It reads the registered allocation, the synthesis index and the retained result submodules under `studies/narps/results/`.
It does not depend on private host capture directories or change any scientific analysis.
The source reader targets the retained directory structure on this branch; changes to that structure require updating the capture paths and adapters.

Initialize the selected NARPS study and only the result submodules needed for the capture.
Retrieve their referenced maps, summaries, source scripts, `input/sources.json` and retained `condition-assignment.json` files.
The original scientific result commit must also be available locally; a shallow retention checkout may need an explicit fetch of that commit.
The extractor reports the missing commit and fetch command when needed.

Run a candidate illustrative-map capture into new directories:

```sh
pixi run poster-capture-example --output /tmp/narps-example-inputs
pixi run poster-group-map --inputs /tmp/narps-example-inputs --output /tmp/narps-example-figures
```

Full spatial recapture is currently unsupported.
Run 11 did not retain its native analysis mask or the exact source-template/mask hash needed to validate a reconstruction.
Matching the reported voxel count cannot establish voxelwise equivalence.
`pixi run poster-capture-spatial` therefore stops before reading sources or writing outputs; enable it only after retaining exact mask provenance and adding a voxelwise comparison.
This limitation does not affect `pixi run poster-spatial-map`, which verifies and renders the frozen NPZ.

Both capture tasks accept `--results-root`, `--index` and `--allocation` when the retained checkout is elsewhere.
Defaults point inside this benchmark.
The shared source reader compares each retained file's Git object with the object at the original scientific result commit and records both scientific and retention revisions.
It verifies annex payload sizes and cryptographic hashes against their content-addressed keys, and requires ordinary files and assignments to match committed bytes.
Assigned conditions must match the registered allocation; assignment links point to the named retained branch.
Refreshing into the canonical directories uses the same tasks without `--output`, after reviewing the candidate capture.

The current adapters identify the twelve retained round-one analyses and their native file layouts.
Adding another development iteration requires adding its scientific-file adapters and explicitly expanding the frozen pool, denominator and common-support calculation.
An unlaunched allocation row is not an observed run, and empty conditions must not become zeros.

## Export to the poster

Run `pixi run poster-figures` and copy only the four SVG/PNG assets listed in `poster-figure-manifest.json` into the poster's display-assets directory.
Verify their SHA-256 values against the manifest, and record the benchmark checkout revision in the presentation's source binding.
Do not copy the scientific generators or input snapshots back into the presentation repository.
Links for readers should open the named benchmark branch and these scripts; exact revisions and hashes stay in machine-readable provenance.
