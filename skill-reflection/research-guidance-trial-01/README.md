# Proportionate research guidance

Round-one reflection motivated three generic research-loop changes: preserve exact scientific inputs through the chosen workflow, challenge inferential numerics independently, and match review effort to what a correction can affect.
The guidance separates available infrastructure and coordinator preservation from worker requirements.
The published source is [`eb8b454`](https://github.com/con/skills/commit/eb8b454b02ba171a821cc6725dfe98a7495f5126), based on the round-one working skill revision.
The assessor is versioned independently.

The complete [trial archive](trial.tar.gz), [file manifest](manifest.json) and [verification receipt](verification.json) retain exact prompts, supplied skill snapshots, original and completed synthetic targets, full native captures, observed friction, and the independent numerical check.
These are development followability checks, not NARPS outcomes or evidence of causal effectiveness.

- Case A, a fresh Luna/high agent, corrected a pooled-variance formula mislabeled as Welch, preserved the genuine zero and excluded the missing value, and reported uncertainty and a figure.
  Independent arithmetic confirmed its stated difference and interval.
  The agent interpreted the supplied-reference boundary too narrowly and did not read every referenced instruction; that harness ambiguity limits coverage and remains in the record.
- Held-out case B, a fresh Sol/high agent, corrected report units.
  Only `REPORT.md` changed; analysis, input and figure hashes remained unchanged.
  The corrected trial prompt explicitly allowed all supplied snapshot references.

No skill wording was tuned after these cases.
The exact three source files match the tested snapshot and the skill validator passed.
The targets were deliberately ordinary folders with no Git commits; completed-file manifests identify what was reviewed.
The next comparison will evaluate the guidance on new workers under a stable, declared setup.

The composed working bundle is [`f2e74ea`](https://github.com/con/skills/commit/f2e74ea3ed372f966c95692cb0826d56ad5e6a6c).
It retains other working skills from `c90252a`, the three tested research-loop changes, and exact assessor/conventions directories from `9852d836`; evaluation records are pinned at `95b8dd83`. The [composition and validation record](compatibility-01/composition.json) confirms 153 tests, 26 recorded evaluations and all 18 injected defects passed, with no structural errors and ten existing unrelated warnings.
