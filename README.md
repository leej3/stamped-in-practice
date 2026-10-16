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

## Completed experiment retention

`results/narps-r1-08` and `results/narps-r1-09` pin independently retrieved experiment repositories.
Each retention commit is a direct child of its unchanged scientific result and adds only coordinator evidence, with no worker credit.
The complete archive includes execution records, original assessments, failed attempts and environment snapshots; directly readable copies of key reports and receipts are under `coordinator/retention-01/indexable/`.
`retention-publications.json` identifies the separate scientific and retention revisions and hashes the independent publication checks retained by the coordinator.
Keep these experiment submodules uninitialized until needed.
