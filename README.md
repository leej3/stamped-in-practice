# MRIQC scan-quality study

A proposed HPC neuroscience study for the STAMPED research comparison.
**Design only: not launch-ready.** No imaging payload retrieval, compute-node pilot, container execution, runtime calibration or hub delivery has been verified here.
The coordinator launcher must reject this revision using `coordinator-guidance/readiness.json`.

- `input/` is the worker package: scientific task, pinned source manifest and verbatim upstream metadata.
- `coordinator-guidance/` holds preparation, evaluation and delivery checks; never export it to workers.
- Future `results/<run>/` submodules retain independent experiment repositories, including failures.

Use `pixi run verify-design` for internal manifest and metadata consistency.
This is a design check, not a scientific validation or retrieval test.
Workers use their own experiment-root Pixi environment, supplied by the coordinator.
Keep working locks ignored; preserve each final validated lock on a separate snapshot branch.

See [protocol](coordinator-guidance/protocol.md), [judging](coordinator-guidance/judging.md) and [preparation gates](coordinator-guidance/preparation.md).
This study shares ds000102 with the other proposed HPC study: they are separate tasks, not independent dataset replications or evidence of transfer outside neuroscience.
