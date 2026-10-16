# NARPS spatial results for the STAMPED poster

The current figures describe all 48 original research deliveries in rounds two and three of `narps-neutral-v1`: six analyses per condition per round.
No research worker or judge was rerun to produce these figures.
Original computations and native correction choices are preserved, including analyses with no detections.

## Replay the figures

Retrieve the annex payloads under this directory using the benchmark's retrieval instructions, then run `pixi run poster-figures` at the repository root.
Rendering is offline: the frozen inputs, source records and plotting code are all here.
The generated SVG and PNG files belong to this benchmark; the poster repository imports display copies using `figures/poster-figure-manifest.json`.

- [Spatial selection](map-inputs/spatial/selection.json) identifies each primary statistic, decision and support source.
  It excludes pilots and sensitivity analyses from the primary figure.
- [Spatial provenance](map-inputs/spatial/provenance.json) binds the original stop receipts, completed capture manifests, source-file hashes, conditions and revisions.
  Readable original scripts, reports and numerical summaries are retained under `map-inputs/spatial/sources/<run>/workspace/`.
- [Frozen masks and decisions](map-inputs/spatial/spatial-inputs.npz) contain `native_masks`, `native_positive`, `shared_support`, `affine` and `anatomy`.
  The first array dimension follows the provenance `records` order.
  Each mask record distinguishes native support, exact derivation and certified partial support.
  NumPy opens the archive without pickle or any external dependency beyond the root environment.
- [Numerical summary](figures/narps-spatial-summary.json) retains per-run counts and round-specific membership behind the pooled condition maps.
- [Example provenance](map-inputs/example/provenance.json) binds the complete group-map illustration to the original round-two run 09, including its native coverage and Harvard–Oxford anatomical vmPFC proxy.

## What the spatial figure measures

Color is the fraction of 12 analyses per condition with a native positive whole-brain FWE decision at alpha .05.
The displayed domain is the intersection of certified tested supports across all 48 analyses: 168,285 voxels.
Gray means no positive detections on that domain; hatching means the location is outside shared coverage.
Unsupported voxels are never filled with negative decisions.
Native maps and per-run support are retained so other summaries can be derived without losing the underlying observations.

The figure describes delivered spatial agreement.
Native algorithms, correction choices and computational differences are not homogenized.
In particular, an RMS-standardized field and observed numerical differences prevent interpreting all saved fields as interchangeable t statistics; no pooled t-SD is reported.
There is no new participant-level inference and no causal comparison of the conditions in this rendering step.

Most support masks are native or reconstructed from the same 54 input identities and the worker's retained rule.
Six masks can be recovered exactly because their nonzero finite statistics are confined to the native mask and their count equals the retained native mask count.
Round-two run 01 has five zero-statistic voxels whose template-mask membership cannot be recovered uniquely.
Its other 196,115 voxels are certified by the retained code and field.
Only those certified locations enter the common domain; no current software template is substituted.

## Refresh from preserved deliveries

The capture command requires an explicit root of completed native launcher runs and the matching iteration records.
It verifies capture hashes against original stop receipts and retained closure records, verifies selected source bytes and participant payload identities, checks map geometry, and checks all 48 native positive-decision counts before writing a replacement snapshot.

```sh
pixi run poster-capture-spatial --runs-root /path/to/retained/runs \
  --iteration-root /path/to/iterations/narps-neutral-v1
pixi run poster-figures
```

`poster-capture-example` invokes the same capture because the example and spatial figures share their provenance.
Capture is descriptive extraction from immutable original deliveries, not execution of their analysis programs.
It never reads a mutable worker worktree.
The earlier development-only prototype is preserved in Git history and is not a source for the current figures.
