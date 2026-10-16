# Reproduce the round-one tables and figures

The retained `extraction/index.json` binds the original stop/capture/native receipts and exact report/response bytes for all 24 completed workers and 32 judgments. Its `analysis/` preserves the full registered 72-worker/96-slot accounting, with later rounds pending.
`tables/` is the round-one subset; `summary.json` and `condition-summary.tsv` are deterministic summaries produced by `code/prepare-synthesis.py`.
That script also records the original host-side preservation paths and is not a portable data-discovery interface.

Use coordinator source commit `5473a6d` with its declared Pixi environment and exact external assessor `9852d8360f9519d21d11099b45f5deb8ba80cb28`.
The validated coordinator lock is preserved separately at `719a729d565a7886d906d227a8f1936020a75a9b`; its SHA-256 is `f8fff1394fbeaa2ab1c4993fceb0dd6463fe0c08c81fcda397f3e752a72c4249`.
Do not merge the environment branch into source.
The four analysis/rendering scripts and assessment pin are copied under `code/`, and `validation.json` binds their bytes. Initialize the selected iteration and assessor only; retrieve annexed table/figure sources as needed using the coordinator's [retrieval guide](https://github.com/leej3/stamped-in-practice/blob/main/RETRIEVAL.md).

From the coordinator checkout, with `iteration` set to the initialized iteration dataset and `out` set to a new directory outside retained evidence:

```sh
pixi run --locked python scripts/aggregate_comparison.py \
  --allocation "$iteration/allocation.json" \
  --index "$iteration/rounds/round-01/synthesis/extraction/index.json" \
  --output "$out/analysis" \
  --assessor assessment --assessment-pin assessment-version.json \
  --assessment-procedure-sha256 b011f6e68dc6838e736f1ae2ad70d52896dab9b848d6f33950b4d35dd86b1521
```

Expected exit status is **2**, with exactly eleven `target_unchanged: True was expected` provenance issues.
That is the preserved measurement result.
Do not remove those errors or modify the source responses to force success.
The aggregate must still contain all 72 workers and 96 assigned slots.

```sh
pixi run --locked python scripts/render_round_summary.py \
  --analysis "$out/analysis" --round 1 \
  --assessor assessment --assessment-pin assessment-version.json \
  --skill-observations "$iteration/rounds/round-01/skill-observations" \
  --output "$out/figures"
```

The attrition figure additionally uses the exact retained per-judge `target-as-found-01` delta and verification records.
Their copies are under `attrition/evidence/`; the original renderer invocation and its source are retained in the analysis evidence.
This classification only explains unavailable measurements; it never admits an excluded judgment.

Host paths inside unmodified reports and native receipts are historical citations.
The extraction's own relative references resolve within its directory; complete underlying attempt trees and native logs are in each experiment's coordinator support archive.
GitHub PNGs here are small ordinary-Git previews of the actual rendered results.
Original vector outputs and raw records are preserved alongside them.
