# Lessons for AI-assisted science

The promise of this approach is that research guidance can be tested and improved against real scientific work.
The challenge is that doing an analysis, making it reusable, coordinating agents and assessing the result all interact.
This study showed why improving any one of those pieces in isolation is insufficient.
The lessons below bring together the study records and John Lee's reflection on directing the work.

## Design assessment around the science we care about

The assessment apparatus influences both how research is produced and what counts as a successful result.
Prescribing a directory structure, tool or output can make assessment easier while quietly narrowing the practices being tested.
An inflexible assessor can also reject useful work because it does not fit the expected representation.

The next benchmark should define the scientific properties and reproducibility evidence it needs, while allowing scientifically defensible ways of providing them.
Rehearsals should include varied valid deliveries and a complete transition between skill revisions.
Keep the scientific criteria stable, but make the machinery flexible enough to recognize equivalent evidence.
Changes to that machinery should be explicit so flexibility does not become an excuse to favor particular outcomes.

## Give coordination precise completion rules

Agents need an unambiguous definition of when a milestone is complete and when to advance.
Repeated attempts to repair assessment or infrastructure can otherwise keep a coordinator inside one round indefinitely, postponing the next scientific test.

Specify the required deliverables, a bounded repair budget, escalation conditions and the disposition of unresolved problems before launching a round.
A round can finish with recorded failures.
Distinguish problems that invalidate the comparison from problems that can be retained and studied in the next iteration.
Coordination guidance should make that decision executable rather than repeatedly asking the agent to “finish” or “fix” the work.

## Match model capability to the combined task

John's assessment is that performance was poor relative to a core computation that takes about six seconds.
That is a reference for the numerical calculation, not a measured duration for the complete research workflow.
The much larger challenge was choosing an analysis, implementing it correctly, managing dependencies, documenting the work and satisfying reproducibility requirements together.
In this study, asking Luna to manage science and STAMPED practices simultaneously was too demanding.

We should have used more capable models for judging and invested more effort in calibrating their judgments against expert review.
Observed disagreement between judges makes that a substantive benchmark-design concern.
A stronger judge is a proposal to test, not an automatic guarantee of correctness.
Future comparisons should separate worker capability from judge capability and compare scientific adequacy, reproducibility and total cost at each level.

## Explain dependency expectations in the common task

“Self-contained” should mean that the inputs, dependencies and execution route are identified and recoverable.
It should not encourage agents to reimplement established scientific methods using only the Python standard library.
John observed substantial variation in approaches, including this interpretation of self-containment.
That variation adds implementation risk and makes it harder to understand what the assistance conditions are actually comparing.

Give every condition the same basic guidance: use appropriate established scientific libraries, declare dependencies and provide a practical setup recipe.
Distinguish that shared technical baseline from the research skills under test.
Then evaluate whether added guidance improves the science and the usability of its research object, rather than whether an agent guessed an unstated dependency preference.

## Treat infrastructure support as part of the experiment

Careful tracking is necessary, but the tracking system itself adds work.
Entire.io setup was difficult in this project, and cluster sandbox defaults complicated distributing tasks through Slurm.
A coordinator can remove much of that friction by preparing directories, access and cluster instructions.
That support is useful, but it changes the task: the worker no longer has to solve those parts of producing reusable science.

Decide deliberately which responsibilities belong to shared infrastructure and which belong to the research worker.
Record the coordinator's contribution and measure its effort alongside worker effort.
A supported benchmark can test scientific reasoning under reliable conditions; a more autonomous benchmark can test the broader ability to produce rigorous, efficient and reusable research.
Both are valuable, provided the support boundary is clear.

## Invest in the next benchmark, not only the next skill revision

The approach offers promise, but the next iteration needs a more deliberate experimental platform.
The priorities are:

- Establish a common baseline of tool, dependency and infrastructure guidance for all agents.
- Budget for benchmark design, representative rehearsals and stronger, calibrated judging.
- Evaluate containerized sandboxing for consistent isolation, and more tightly controlled environments for comprehensive execution capture.
- Measure the setup and operational cost of those environments as well as their capture coverage; additional machinery can introduce new failure modes.
- Explore existing skill-evolution tools as components of the scientific workflow, testing whether their revisions improve fresh research attempts on held-out tasks.

The goal is an arrangement in which scientific quality, reproducibility, agent capability and coordinator effort can be examined together.
Success should mean that another researcher can understand and use the work—not merely that an agent completed a checklist or that every tracking service produced a record.

## Supporting evidence

The [results guide](https://github.com/leej3/stamped-in-practice/blob/main/docs/results.md) explains the outcome measures and their interpretation.
The [retained comparison](README.md) includes judge disagreement and observed skill use; the [reporting correction](REPORTING-CORRECTION.md) explains the later extraction of existing judgments.
The [inspected environment documents](../skill-reflection/round-03-research-guidance-01/delivery-evidence.json) support the setup-recipe revision.
Detailed [publication and capture status](PUBLICATION.md) remains available for readers investigating the execution record.
