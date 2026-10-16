# Improving STAMPED research skills

<img src="assets/workbench.png" alt="STAMPED workbench" width="280">

This repository is a workshop for improving STAMPED research skills.
It compares four ways of assisting agents with scientific studies, evaluates the resulting research objects using a versioned assessment, and uses that evidence to revise the skills.
The question is whether the guidance helps agents do sound science with more thorough, efficient and consistent reproducibility.

Each iteration tests a pinned skill revision on selected studies: run matched agents, assess their work independently, compare outcomes and effort, then improve and compress the reusable guidance.
Study inputs and scientific outputs belong to study submodules; iteration subdatasets connect that work to changes in the skills.

The broader hypothesis concerns both humans and agents; this experiment tests agents.
Repeated baseline runs help distinguish improvements from ordinary variability.
Results from one study do not establish transfer to other studies.

| Condition | Added assistance |
| --- | --- |
| Baseline | No supplied research skills or discovery instruction |
| General discovery | Find, install and use skills useful for the task |
| Reproducible-science discovery | Find, install and use skills for scientific quality and reproducibility |
| Explicit pinned STAMPED | Invoke the supplied, versioned STAMPED workflows |

All conditions receive the same scientific task and common resources.
We record assigned assistance separately from what agents actually discover, install and use, including unsuccessful attempts.
These comparisons measure assistance strategies: wording can affect behavior even without skill use.
The explicit STAMPED condition directly tests the guidance we are improving.

During preparation, the assessor and its runtime can improve alongside the other skills.
Formal runs begin from a fresh clone with shallow history.
Comparable assessment series keep their assessor and runtime fixed; necessary repairs define a separate series.

To start or resume a coordinator, give it this repository and a request such as:

> Follow `prompt.md` using `studies/narps`.
> First read the selected iteration's pinned `STATUS.md` and reconcile any active runs.
> Continue its registered next step; select and seal a new registration only when no existing one applies.

| Location | Purpose |
| --- | --- |
| `prompt.md` | The research, assessment and skill-improvement loop |
| `AGENTS.md` | Instructions for the coordinator |
| `iterations/<iteration>/` | An iteration subdataset with revisions, linked trials, assessments, comparisons and reasons for changes |
| `studies/<study>/` | A versioned study submodule |
| `studies/<study>/input/` | The scientific prompt and verified data supplied to research workers |
| `studies/<study>/coordinator-guidance/` | Evaluation guidance and reference material for the coordinator and judges |
| `studies/<study>/results/<run>/` | An experiment submodule containing the worker's research object, assessments and execution records |
| `skills/` | Evolving `con/skills`; each iteration records the exact tested revision and development branch |
| `assessment/` | The selected assessor version, identified by `assessment-version.json` |

Keep iteration, study and experiment submodules uninitialized until needed.
Open selected paths and retrieve their required annex content; the coordinator tree retains their exact commits without expanding every experiment.
The [retrieval guide](RETRIEVAL.md) gives the current NARPS payload route and commands for a selected experiment.

The intended result is transferable guidance: an independent agent can use these skills with a researcher's own data and hypothesis to produce scientifically useful, rigorous and convenient research.
The products are improved shareable skills, evidence about their impact, and a STAMPED research object documenting the whole workshop.
Figures summarize scientific outcomes, reproducibility, effort and variability.

NARPS is the first formal study.
The tested source and preparation evidence are linked in [`source-version.json`](source-version.json); formal trials and skill iterations are recorded here.

The [completed NARPS development comparison](https://github.com/leej3/stamped-in-practice/blob/851f3905ab26d0a9ac6deb7c52f85bd085cc54ff/DATASET.md) contains twelve research workers, sixteen assigned judgments, figures and the resulting skill reflection.
Its workflow mandates and assessment changes are disclosed.
The [sealed tool-neutral comparison](https://github.com/leej3/stamped-in-practice/blob/5056bebf6eb33c2b9b02262efc39d084259424ce/registration.md) fixes 72 new workers and 96 judgments.
The [completed three-round readout](https://github.com/leej3/stamped-in-practice/blob/5e0a72417619ee50eac501222beaa84e527f5c26/final-synthesis/README.md) retains all 72 assigned research workers and 96 operational judgments, with the earlier original round-one assessment kept separately.
The frozen reporting gate rejected all judgments in rounds two and three because the registered worker source revisions differed from the original seal; those measures are unavailable, not zero scores or scientific failures.
Round-one duplicate judgments also showed substantial disagreement, and a supplied-procedure exposure limits blinding.
This comparison does not establish a skill benefit, reduced variability or transfer to another study.
The [lessons](https://github.com/leej3/stamped-in-practice/blob/5e0a72417619ee50eac501222beaa84e527f5c26/final-synthesis/LESSONS.md) explain what the retained evidence supports.

The tested research-skill revisions were `f2e74ea3`, `d83d7d66` and the final [`32660661`](https://github.com/con/skills/commit/326606610af6c261876c92032ca1f89f6d3ad1f1).
Operational assessor `9852d836`, source `4f72ef49` and Luna/high remained frozen; prospective changes retained on main were not adopted.
No further tuning or runs are pending.

The [publication record](https://github.com/leej3/stamped-in-practice/blob/5e0a72417619ee50eac501222beaa84e527f5c26/final-synthesis/PUBLICATION.md) distinguishes complete local captures, published Git references, hosted Entire verification and pending annex retrieval.
Read the [pinned completed status](https://github.com/leej3/stamped-in-practice/blob/5e0a72417619ee50eac501222beaa84e527f5c26/STATUS.md) before continuing; historical controllers must not be restarted.
