# Prospective NARPS assistance comparison

Draft for sealing before any new scientific launch.
This is a new comparison, provisionally `narps-neutral-v1`; the completed `narps-v1` round is development evidence and is excluded from its outcome estimates.
No launch, readiness claim or source pin is authorized by this draft alone.

## Scientific task and fixed resources

Keep the original scientific task verbatim: group inference about a positive gain response in vmPFC, with whole-brain correction, from the same 54 AO86 equal-indifference participant effect maps.
Preprocessing and participant modeling remain fixed.
The original study commit is `c7a135f92f92df15c379f7c2d9231f13981d76e4`, with input tree `a484f41db2095ef116f08d359f9b95ad41981698`.
Preserve all 58 input paths and verify materialized bytes against the source inventory before every launch.
The maps occupy 96,387,264 bytes; no time-series scans or new participant data are needed.

Every worker receives the same materialized inputs, an isolated writable workspace, the same scientific software availability, reference/network access, model settings and per-worker compute limits.
A frozen resource sheet supplies executable locations and access facts, without a preferred workflow or study answers.
Workers choose their analysis, software, directory layout and delivery practices.
The common prompt does not require Pixi, Git, DataLad, annex, Duct, a lock file, a `results/` directory, commits or publication.
Coordinator scaffolding and supplied packages are recorded as common inputs and earn no worker credit.
Existing tooling can remain available without being a required worker practice.

Freeze the worker-visible starting files, executable/package inventory, environment variables, available tools and global instructions. Exclude coordinator history, earlier results, assessment guidance, assignment records and unassigned research skills. Independent workspaces must not share writable caches, Git object stores or discoverable sibling outputs. Preserve and disclose unavoidable visibility, including process metadata and provider/model drift; do not claim perfect blinding or independence.

## Assignment, replication and sequence

Use the four existing strategies and their exact additional prompts in `conditions.json`: baseline, general skill discovery, scientific/reproducibility skill discovery, and explicit pinned STAMPED.
Baseline has no supplied research skills or discovery instruction.
Spontaneous discovery stays baseline.
Failed discovery or installation stays in its assigned strategy.
Record search, selection, exact retrieved contents, installation, reading and observed application separately.

Run exactly three new rounds with six independent fresh workers per strategy per round: 24 per round, 72 total.
Each worker receives one primary independent judgment.
Two workers per strategy per round are selected before launch for one additional independent judgment: eight duplicates per round, 24 total, 96 assigned judgments.
Duplicate judgments are measurements of the same workers, not additional research replicates.
First assigned judgment is primary regardless of outcome.
The allocation file fixes all assignments, launch order and duplicate selections before research.

Use four scheduled waves of six workers per round.
Every wave contains all four strategies; each strategy appears twice in two waves and once in two waves.
Randomize the balanced wave composition and order using the recorded allocation seed.
All six receive matched limits and begin in the recorded order; do not refill a wave with the next strategy when one worker finishes.
Start the next wave after all six have stopped.
This controls scheduling imbalance without claiming identical instantaneous contention.
No disposable capacity tests are added.
Judgment order is separately randomized in the allocation; judges receive no treatment labels.

The input maps alone require about 0.58 GB for six separate concurrent copies, or 6.94 GB for all 72 retained copies before storage deduplication.
This is an inventory calculation, not proof of sufficient RAM, disk, CPU or native-service capacity.
Environments, derived images, transcripts and complete archives require additional storage.
The completed development round supplies rough effort context, not a runtime promise or stopping budget.
Use the selected host's existing resource evidence and ordinary preflight to establish the frozen envelope.

Retain the existing intended model setting, `gpt-6-luna` with high reasoning, subject to verification of its exact resolved identity before sealing.
Freeze each role's exact runtime, model resolution, settings and resources across strategies and all three rounds.
Worker and judge runtimes may differ if their distinct role-specific identities remain fixed.
For Typhon, the declared intended worker runtime series is 0.163; the exact build, executable hash and native integration remain unresolved and must not be inferred from that series label.
Matched local execution is an acceptable host choice before sealing.
Typhon service integration is unproven and is not a cluster-debugging prerequisite for a local comparison.

Freeze the common prompt, scientific judging guidance, assessor source, response schema, replay policy and coordinator preservation procedure before round one.
Only the explicit research-guidance revision may change between rounds.
Freeze its complete delivered content and hashes before each round; fixed supporting skills remain fixed unless their change is explicitly part of that round's research-guidance revision.
Discovery is intentionally open-ended: exact discovered contents are captured per worker, not falsely described as prospectively pinned.
Keep the discovery instruction and opportunity fixed.

Reflect after round one to select round two's skill revision, then after round two to select the final revision.
Round three evaluates that final revision without further tuning on its results.
If evidence justifies no change, retain the same revision and say so.
A necessary change to common setup or assessment after launches is a documented break in comparability, not a silent amendment or a skill-only effect.

## Completion and interruption rules

There is no overall spending, token or elapsed-time cap.
The fixed sample is the stopping rule: finish the 72 assigned attempts and 96 assigned judgments, preserve failures and missing measurements, then synthesize.
Do not add workers, change the duplicate selection, choose a better judgment, or extend rounds to obtain favorable scores.
Review sessions at 90 minutes for operational state only; productive work can finish.
Do not give scientific hints or request improvements after a worker's natural final delivery.
A final response or a declared inability to continue ends the worker attempt, irrespective of scientific quality, publication state or replay success.

A launcher failure before the task is delivered is an operational nonlaunch.
Once a worker has received the task, any failure, interruption or partial output belongs to that assigned attempt.
Retain the same session identity if a transient transport disconnect can resume without changing inputs or instructions; do not silently replace it with a fresh worker.
An irrecoverable interruption remains an interrupted outcome.
Assess available original evidence and retain unavailable measures.
Missing judgments remain explicit assigned slots with failure evidence; a supplementary retry never substitutes for a primary or duplicate.

On Typhon, stop the active worker wave and further dispatch upon NEW CPU throttling: a positive delta from the immediate pre-wave baseline in available worker-cgroup or ancestor-cgroup throttled-event/time counters, or a new OS-reported thermal throttling event/status.
Retain counter paths, units, sampling times and observed deltas.
Historical nonzero counters alone are not new throttling.
Missing counter access is unknown, not zero; the actual readable monitoring set must be fixed before launch.
Preserve interrupted sessions and leave restart or host-change decisions explicit.
Do not diagnose the cluster or run capacity probes.
A host change after launch is a common-setting change and cannot be pooled as an unchanged comparison.

## Delivery, preservation and independent judgment

At worker stop, atomically preserve the complete original delivery: tracked, staged, unstaged, untracked and ignored files; native transcript and tool calls; relevant environment; Git metadata if present; and local or remote publication state.
Record a content manifest and the worker's final message before coordinator intervention.
Preserve even incomplete delivery.
Keep assignment and coordinator evidence outside the scientific workspace supplied to judges; provide a sanitized attribution receipt without strategy labels.
Retain the unredacted original separately.
Any authorized redaction is documented and cannot silently remove scientific evidence.

Coordinator retention may use Git, DataLad, annex, environment snapshots and separate archival commits without asking workers to adopt them.
Capture the requested execution evidence consistently outside the worker's instructions, including coordinator Duct capture where implemented.
State whether measurements cover the entire native session, child computation or individual commands; do not infer missing per-command measurements.
Coordinator packaging, upload, retrieval or environment repair earns no worker-practice credit.
A complete preservation failure remains a coordinator limitation, not a poor worker grade.

Independent fresh judges receive the frozen assessor, original scientific guidance, the original complete delivery and its sanitized stop receipt.
They inspect evidence across tools and file forms, including uncommitted or ignored scientific material.
They separately assess scientific adequacy and the frozen STAMPED items, attributing version control, sharing and archival practices to the worker's actual stop state.
The full judge prompt specifies one conditional replay from an untouched copy and protects inputs from output deletion.
All raw responses remain immutable.
Evidence-specific harness invalidity is recorded separately as unavailable; it does not turn into a worker failure or justify choosing a favorable replacement.

## Outcomes and interpretation

Report scientific adequacy as supported, qualified, not supported or unable to assess, separately from whether the gain hypothesis is supported.
Preserve all item verdicts, applicability decisions, evidence and not-checked values.
Do not invent a summed STAMPED score.
Show completion, delivery/access coverage, replay availability and result, attributable worker practices, skill use, intervention, elapsed time and available usage/resource measurements with their denominators and scopes.

For each strategy and round, show all six worker outcomes, category counts, proportions and medians/ranges. Show 95% Wilson intervals for binary proportions with the explicit small-sample/independence caveat; these are exploratory, not a powered efficacy test.
Show primary/duplicate disagreement by scientific category and item with paired valid denominators, without adjudicating away differences.
Report both all-assigned outcomes and the availability of each measure; do not silently use complete-case denominators.
Avoid significance claims, causal rankings based on this small single-study series, or pooling different anatomical estimates as independent biological replications.

Within-round contrasts concern assistance strategies, including their prompt effects and actual discovery behavior.
Cross-round changes in explicit STAMPED are descriptive and use contemporaneous comparison strategies; time, model service changes and changing discovered skills limit attribution.
The same 54 participants are reused throughout, so worker replication measures analysis/workflow variability, not new participant evidence.
Earlier development scores cannot establish a clean skill progression into this setup.
Report favorable, null and adverse outcomes equally.
The final fresh assessment of the whole workshop is supplementary and outside these 96 assigned judgments.
