# NARPS participant group-inference study

This study asks workers to assess NARPS Hypothesis 1 using 54 fixed participant gain-effect maps and cohort metadata.
The task, source URLs, checksums and upstream modeling context are in `input/`.
The coordinator supplies this package unchanged to independent workers.

`source-version.json` records the source repository, study commit and exact input tree.
This repository starts with a parentless study commit; historical preparation and results remain in the source repository.
`coordinator-guidance/judging.md` retains the scientific assessment criteria without prior answers or rehearsal artifacts.
Select that file as the formal rubric; it has no additional guidance dependencies.
Future completed experiments belong in independently published submodules under `results/<run>/`, added only when results exist.

## Retrieve and verify inputs

Use the study's Pixi environment:

```bash
pixi run check-input
pixi run get-input
pixi run verify-input
```

`check-input` verifies the frozen metadata and all 54 lazy annex links without downloading maps.
`get-input` initializes the local annex store, configures the declared public CON Hub remote and retrieves only missing input keys, then checks byte counts and SHA256 hashes.
`verify-input` checks local bytes without downloading or running a scientific analysis.
To check retrieval of one representative map, use `pixi run get-input --path data/sub-001_hypo1_cope.nii.gz`.

`retrieval.json` declares the existing store at `https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git`, its annex endpoint and UUID, and the 54 input keys.
Original NeuroVault URLs remain available in `input/sources.json`.
Access uses the host's approved credential provider; credentials and host configuration are not project files.
The helper transfers keys directly because a fresh annex store has no historical location records.
It does not fetch source Git history, regenerate inputs, or change annex keys.
The existing MD5E keys remain unchanged; new annexed content uses SHA256E.

Initialize annex before accessing the study's links, including after installing it as a Git submodule.
Keep working `pixi.lock` files ignored; retain any validated environment snapshot separately from the study's main history.

`coordinator-guidance/readiness.json` records preparation of the input package only.
The coordinator must verify retrieval and its required host resources before sealing or launching a formal comparison.

## Research deliveries

The current `narps-neutral-v1` comparison registers independently retrieved deliveries under `results/narps-neutral-*/`.
See [current comparison status](https://github.com/leej3/stamped-in-practice/blob/codex/iteration-narps-neutral-v1/STATUS.md) and `neutral-retention-publications.json` for published identities.
The exact original delivery is preserved in `coordinator/delivery-01/delivery.tar.gz`, including dirty, untracked and ignored files within the declared capture roots.
Its manifest digest identifies those bytes; the actual worker Git HEAD may still be the supplied input seed.
Later coordinator preservation commits do not become worker scientific revisions or earn worker-practice credit.
Judgments and supplementary execution evidence are added separately as they finish.
The separately registered operational-copy assessments are retained under `coordinator/assessment-series/narps-neutral-r1-operational-v4/`; the original judgments remain in their earlier paths.
The registry records each series, slot, procedure and publication identity separately.
Keep experiment submodules uninitialized until needed.

## Historical development comparison

The completed `narps-v1` development results occupy `results/narps-r1-*/`; their [synthesis and evidence links](https://github.com/leej3/stamped-in-practice/blob/851f3905ab26d0a9ac6deb7c52f85bd085cc54ff/replay/RESULTS.md) remain separate from the current comparison.
`retention-publications.json` preserves the initial six publication records from that development phase, including their scientific and coordinator retention revisions and independent checks.
Those historical archives and their `coordinator/retention-01/indexable/` reports use the earlier retention layout.
