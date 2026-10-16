# NARPS Hypothesis 1: gain effects in the equal-indifference group

This repository analyzes the 54 supplied participant gain-effect maps at the group stage. It does not rerun preprocessing or participant models. See [`protocol/analysis-plan.md`](protocol/analysis-plan.md) and [`input/upstream-methods.md`](input/upstream-methods.md) for the estimand and fixed upstream constraints.

## Run

The root Pixi environment supplies dependencies and the task:

```sh
pixi run group-analysis
pixi run validate-results
pixi run figures
```

The task reads `input/participants.tsv`, `input/sources.json`, and the 54 annexed NIfTI maps under `input/data/`. It writes maps and tables under `results/`; validation independently checks group statistics and corrected maps, and `figures` renders the whole-brain statistic distribution with corrected-result summary, coordinate localization, and participant effects. Duct records are retained under `logs/`. The analysis uses a one-sample group intercept and a positive-direction, whole-brain maximum-t sign-flip test. The coordinate-defined vmPFC box is descriptive only; it does not replace whole-brain correction.

## Inputs and provenance

The cohort and map source records, retrieval-byte checksums, and upstream methods are in `input/`. The maps are git-annex objects; retrieve them with `git annex get input/data/` when needed. Preprocessing and individual modeling are fixed. Participant variance maps are absent.
