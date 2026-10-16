# Finding your way around this research object

Start with [the project overview](../README.md) or [the results guide](results.md).
This page explains the structure you encounter when following their evidence links.

## Why a link leaves main

The project keeps several independently versioned datasets in one GitHub repository.
The `main` branch contains the overview and coordinator tools.
Other branches contain a scientific study, an iteration of the comparison, or an individual agent's research delivery.
A Git submodule connects these datasets at an exact recorded commit.
On GitHub, opening a submodule can therefore change both the selected revision and the files shown at the repository root.
This is expected: you have opened a component of the research object.

These dataset branches are not simply unfinished edits awaiting a merge.
Keeping their histories separate allows the project to preserve inputs, original deliveries and later assessment without mixing them into the coordinator's files.
A branch name helps you browse a component; a commit hash identifies the exact version used as evidence.
The parent repository's submodule link records that exact version even when the branch later advances.

## Choose a destination

| What you want | Where to go | How to interpret it |
| --- | --- | --- |
| Overall question and findings | [Project overview](../README.md), [results guide](results.md) | Reader-facing summaries on `main` |
| Scientific question and input data | [NARPS study introduction](https://github.com/leej3/stamped-in-practice/blob/codex/study-narps/README.md) | The `codex/study-narps` dataset, linked locally as `studies/narps/`; its `input/` contains the worker task and data sources |
| Completed three-round comparison | [Completed study introduction](../iterations/narps-study-runs/) | The `codex/iteration-narps-neutral-v1` dataset, linked as `iterations/narps-study-runs/`; its introduction explains the completed outcomes and supporting records |
| Design and assignment of runs | [Registered design](https://github.com/leej3/stamped-in-practice/blob/codex/iteration-narps-neutral-v1/registration.md) | The planned comparison; later amendments and reporting changes must also be considered |
| Original research deliveries | [Study's delivery guide](https://github.com/leej3/stamped-in-practice/blob/codex/study-narps/README.md#research-deliveries) | `results/<run>/` links to independent experiment repositories; later coordinator records are separate from the agent's work |
| Poster summaries and plotting inputs | [Poster guide](poster.md) | The `codex/stamped-poster-analysis` branch holds reporting and presentation work derived from retained deliveries |
| Research guidance and assessor | [Skills guide](skills.md) | Separate research and assessment revisions in `con/skills`, selected by `skills/` and `assessment/` |
| Earlier development work | [Development trial introduction](../iterations/trial-with-failed-results-reporting/) | `iterations/trial-with-failed-results-reporting/` used different workflow requirements; do not pool it with the three-round comparison |

The descriptive submodule names are the current navigation names.
Historical branch names and run IDs remain unchanged so old evidence links continue to resolve.
See [the trial history](trials.md) for the relationship between these completed datasets.

## Read a run in context

Choose a run from the [per-run outcome records](https://github.com/leej3/stamped-in-practice/blob/codex/stamped-poster-analysis/experiments/retained-round-reporting/pooled/run-outcomes.json), then find its experiment under the study's `results/` directory.
For example, `narps-neutral-r2-09` identifies round two, run nine.
A run number alone does not identify its assistance condition; use the recorded assignment.

Read the agent's report alongside its code and results.
The experiment's `coordinator/README.md` explains the retained original delivery and later assessment records.
Coordinator copies, figures and archive uploads help others inspect the work, but are not practices performed by the original research agent.
The [retrieval guide](../RETRIEVAL.md) explains how to obtain files that GitHub displays only as annex pointers.

## Other kinds of branches and links

Branches named `codex/env-*` preserve an exact dependency lock for a particular run or build.
They are environment snapshots, deliberately kept out of the coordinator's main history.
Use the snapshot associated with the work you intend to replay, rather than assuming the latest environment is equivalent.

Implementation and repair branches preserve how the tools evolved.
Their presence does not mean that a change was used in the completed comparison: the iteration records identify the versions actually used.
Likewise, older preparation notes can describe a state that was later superseded.
For the completed comparison, start with the [results guide](results.md), then follow the historical record for the specific question you are investigating.

The CON Hub store still uses the earlier name `stamped-ai-research-next`.
It stores large payloads for this project; the old store name does not identify a different scientific comparison.
GitHub source availability and payload download availability are separate, as explained in [retrieval and access](../RETRIEVAL.md).
