# Reading the results

[Project overview](../README.md) · [Repository map](repository-map.md) · [Poster guide](poster.md)

The comparison asks whether reusable research guidance helps agents produce scientifically sound, reproducible work.
It uses one neuroscience task, four assistance conditions and three rounds of fresh agents.
There are six research attempts per condition per round, for 72 attempts in total.
The 96 judgments include repeated assessments of selected research objects; those duplicates do not increase the number of research attempts.

The central finding is a distinction: documenting research practices and supporting a scientific conclusion are related goals, but neither measure substitutes for the other.
The descriptive results do not establish that STAMPED guidance caused better science, more reliable outcomes or improvements that transfer to other tasks.

## What the poster measures

| Measure | Meaning | What to watch for |
| --- | --- | --- |
| Science | Whether an assessment found the analysis fully supported its reported conclusion | A supported conclusion may be a negative finding about the neuroscience hypothesis |
| STAMPED items met | For each valid checklist, the fraction met among met, partial and unmet items; then averaged equally across runs | Not-checked and not-applicable items are outside this denominator; this is not certification of a whole research object |
| Replay | Complete matches of selected outputs among observed native reruns | Some runs were not replayed; partial matches and execution failures remain distinct |
| Round progression | Summaries for each condition in each round | Each round uses fresh agents, so lines are not trajectories of individual agents |
| Spatial agreement | How often analyses report a positive corrected finding at a brain location | Agents chose their methods; agreement is not a direct test of scientific correctness or a causal skill effect |

The [pooled results and denominator definitions](https://github.com/leej3/stamped-in-practice/blob/codex/stamped-poster-analysis/experiments/retained-round-reporting/pooled/README.md) lead to every run and round summary.
That page is on the presentation-analysis branch because it derives summaries from retained judgments; it does not replace the original research or assessment records.
See [the poster guide](poster.md) for the scientific figures and plotting sources.

## What we learned about doing this work

Assessment is part of the research system: its requirements can shape the work it is meant to evaluate.
It needs to recognize scientifically appropriate approaches without turning one preferred workflow into the definition of success.
Coordination needs equally careful design, with precise completion rules that prevent repeated repairs from trapping agents inside one round.

John's reflection is that the combined demands of science and STAMPED practices exceeded what Luna handled well here, despite the short core computation.
The next study should use more capable, calibrated judges and give every worker explicit guidance on established scientific libraries and recoverable dependencies.
Preparing tracking, directories and cluster access can help agents, but that coordinator effort is itself part of the cost of reusable science.

Read [the full lessons and next-study priorities](../LESSONS.md) for the implications for benchmarking, container isolation, comprehensive capture and skill evolution.

## Why there are original and corrected reports

The completed study retained all 72 research attempts and 96 operational judgments.
An original reporting check rejected the later rounds because it expected the first coordinator revision even though a research-skill revision had been registered between rounds.
Those rejections describe a reporting failure, not a finding that every later scientific analysis was invalid.

A subsequent correction checked the permitted source changes and extracted results from the existing judgments.
It did not rerun agents, change grades or replace individual failures.
The corrected readout contains **70 of 72 primary scientific assessments and 68 of 72 valid primary checklists**.
The original zero-availability tables remain as historical evidence and should not be mistaken for the corrected availability counts.

Read the [correction and its evidence](https://github.com/leej3/stamped-in-practice/blob/codex/iteration-narps-neutral-v1/final-synthesis/REPORTING-CORRECTION.md) first.
Use the linked original reports when investigating how the reporting failure happened.
The [detailed extraction report](https://github.com/leej3/stamped-in-practice/blob/codex/stamped-poster-analysis/experiments/retained-round-reporting/README.md) explains the correction's checks and exclusions.

## What limits the interpretation

The study is small and its development history is adaptive.
Research guidance changed between rounds, the workers shared a host, and scheduling changed during execution.
Judges also disagreed: in the retained round-one reassessment, five of eight duplicate pairs differed on scientific adequacy.
Successful blinding was not established.
These limitations matter when interpreting apparent changes or differences between conditions.

Replay evidence is also narrower than a blanket reproducibility claim.
Among admitted primary judgments, 21 native entrypoint executions were observed: 13 complete selected-output matches, five partial matches and three nonzero exits.
A selected-output match does not prove that every artifact can be recreated on another machine.

The [methodological lessons](../LESSONS.md) connect assessment design, model capability, coordination, dependency guidance and infrastructure support to the next experiment.
The [comparison plan](../comparison-plan.md) defines the intended distinctions between scientific outcomes, practices, effort and missing evidence.

## Completion and access

All assigned research runs and operational judgments are complete.
The [completed status record](https://github.com/leej3/stamped-in-practice/blob/codex/iteration-narps-neutral-v1/STATUS.md) describes that endpoint; historical controllers must not be restarted.

Readable source, reporting payloads and complete execution archives have different publication states.
The [publication record](https://github.com/leej3/stamped-in-practice/blob/codex/iteration-narps-neutral-v1/final-synthesis/PUBLICATION.md) distinguishes them.
The corrected reporting records verification of 113 reporting and figure payloads; that does not imply that every input, environment or full native archive is publicly downloadable.
For practical download steps, use [the retrieval guide](../RETRIEVAL.md).
