# Launch research workers and judges

This is the implementation guide for running new research workers and assessments.
For the completed study, start with [results and interpretation](../docs/results.md); for the branch and dataset layout, use the [repository map](../docs/repository-map.md).
The completed comparison's historical controllers must not be restarted.

The launcher gives each worker an independent repository containing the selected scientific inputs and its assigned guidance.
Judges inspect the retained delivery separately.
Use the sections below when preparing a new run, together with the [coordinator prompt](../prompt.md) and [comparison plan](../comparison-plan.md).

## Host setup

The native launcher defaults to `~/.config/<coordinator-directory-name>/launch.json`; use `--host-config` to select an explicit host file.
For a checkout named `stamped-in-practice`, the default is `~/.config/stamped-in-practice/launch.json`; existing `stamped-ai-research-next` checkouts retain their earlier default.
These identify the CLI, source environment, approved hooks, provenance resolver and annex remote.
Credentials stay with host providers.
Use [resource readiness checks](READINESS.md) for the requirements supplied by this user; retain their result before launching research.
Launches default to development mode and retain `development-unsealed` status.
The examples below are development launches; use the formal procedure for comparisons.

## Research workers

Initialize only the selected study, leaving its experiment submodules absent:

```sh
pixi run git submodule update --init -- studies/CHOSEN_STUDY
```

```sh
pixi run launch --study studies/CHOSEN_STUDY \
  --base COORDINATOR_COMMIT --branch codex/run-001 \
  --evidence /path/to/run-evidence/run-001/launch \
  --condition baseline
```

Select `baseline`, `discover-general`, `discover-science` or `stamped-explicit` with `--condition`.
The legacy `skills` value retains the earlier explicit treatment for existing records.
Add `--capture-execution` when duct logging is requested, including runs explicitly following the workshop prompt.
The explicit coordinator revision selects the study and skill gitlinks and common Pixi manifest.
Its `conditions.json` supplies the exact added instruction, retained with its hash in the worker's input receipt.
A study marked unavailable in its pinned `coordinator-guidance/readiness.json` stops before worker creation and reports the missing prerequisite.
The launcher copies only committed study inputs and shared environment declarations into a parentless, independent repository.
It records source revisions, blob identities and annex keys without importing coordinator or study history.
Baseline and discovery repositories start without supplied research skill files; explicit STAMPED repositories install the pinned skills submodule without its optional evaluation fixtures.

All conditions receive the same scientific prompt and common resources.
Discovery conditions ask agents to search for and install skills; availability alone is not discovery or evidence of use.
Retain unsuccessful attempts and distinguish assigned condition from observed behavior, including spontaneous discovery in baseline runs.
Each launch uses a separate native profile; task-local skill installations must not change another run's catalog.
Use retained transcripts and installed artifacts to establish searches, choices, source revisions, loading and application; an installed file alone does not establish use.
Coordinator-only Pixi tasks are removed from the worker manifest.
Workers can add dependencies and actionable tasks; each experiment retains its own root manifest.
Keep the evidence directory outside the worker checkout.
`--clone-path ABS` chooses its location; research launches reject `--kind worktree` because it would share excluded Git objects.

## Independent judges

```sh
pixi run judge --repo /absolute/path/to/worker-repository \
  --base RESULT_COMMIT --branch codex/judge-001 \
  --study studies/CHOSEN_STUDY \
  --reference studies/CHOSEN_STUDY/coordinator-guidance/judging.md \
  --evidence /path/to/run-evidence/run-001/judgment-01
```

Use the same study revision and evaluation guidance for matched judgments.
The launcher retains the scientific prompt and optional reference guidance with their hashes, independently of the submitted object.
Judges use the coordinator's frozen assessor and runtime outside the target; the target need not contain assessment tools.
A separate host profile makes the frozen judging skills discoverable without adding files to the assessed checkout.
Formal judges receive `STAMPED_JUDGE_RUNTIME` and its digest: a closed projection containing the validated assessor/runtime pin, runner hash, replay contract and only their own object bindings. The launcher validates the full procedure first and retains that seal and allocation as coordinator records; it never advertises the seal path to judges. Inherited `STAMPED_*` values are replaced for judges, and a local assessor pin is supplied beside the projection. The retained native evidence includes the projection bytes and digest. This is an explicit context boundary, not same-user host containment: assessor/runner locations, scientific guidance, current-object records and host access remain available.
Adopting these changed launcher/helper bytes requires a newly declared assessment procedure; it does not amend prior exposure, judgments or scientific criteria.
Research launch behavior is unchanged; any worker environment revision requires its own research boundary.
The judge works in a separate [output repository](JUDGE_WORKSPACE.md), where normal preservation commits capture its real Entire session; the assessed target remains unchanged.
The clone retains the result commit and its annex metadata, without other trial branches.
They inspect and replay the object's declared environment without repairing it first.
Keep duplicate judgments independently and use neutral result identifiers where practical.

## Formal procedure

Commit the scientific inputs, rubric, selected reference dependencies, public resource requirements and `comparison-plan.md` before sealing.
Keep the assessor source/runtime pin fixed; initialize `assessment` without recursively installing its optional development `evals` submodule. Run `pixi run assessment-check` to verify the assessor and prepare its recorded runtime. If the runtime commit belongs to another repository, `assessment-version.json` can declare `environment_repository`, for example `git@github.com:leej3/stamped-ai-research-next.git`. The runner fetches only the missing pinned commit with depth one, then verifies its manifest and lock hashes; older pins without this field use `origin`. This transport field does not change the source/runtime commits or their hashes.

When scientific execution logging is requested, including by this workshop prompt, add `--capture-execution` to both sealing and research launches; omit it for judges.

The common starting environment needs an immutable commit containing the exact coordinator `pixi.toml` and validated `pixi.lock`.
Use its commit as `STARTING_ENV_COMMIT`; a mutable working lock is not a version record.
Shallow clones fetch missing sealed coordinator and study commits from their respective `origin` remotes, and fetch the assessor runtime from its declared repository.
Starting snapshots use the coordinator's `origin`; pass `--environment-repository REPOSITORY` when sealing a snapshot hosted elsewhere.
Each fetch requests only the exact pinned commit with depth one, and content checks still apply.
Workers may subsequently evolve their own environments, and judges replay those recorded environments.

Run the committed public requirements against separately prepared host checks:

```sh
pixi run readiness \
  --requirements iterations/COMPARISON/requirements.json \
  --host-config /private/path/resource-checks.json \
  --evidence /path/to/run-evidence/COMPARISON/readiness
```

The readiness command configuration and launch configuration are separate host files.
Host paths and credentials stay outside the portable procedure.
Seal using the selected coordinator revision and the same prepared launch resources:

```sh
pixi run assessment-procedure seal \
  --host-config /private/path/launch.json \
  --base COORDINATOR_COMMIT --study studies/CHOSEN_STUDY \
  --comparison-id COMPARISON \
  --resources iterations/COMPARISON/requirements.json \
  --rubric coordinator-guidance/rubric.md \
  --reference coordinator-guidance/reference.md \
  --guidance-dependency coordinator-guidance/needed-reference.pdf \
  --environment-commit STARTING_ENV_COMMIT \
  --output iterations/COMPARISON/procedure.json
```

Omit `--reference` and `--guidance-dependency` when unnecessary; repeat the latter for each needed local dependency.
Rubric/reference paths are study-relative UTF-8 text files; dependencies may include other file types. Only explicitly selected files enter the judge's retained guidance directory. The launcher does not follow links into old judgments or expand historical preparation payloads. Selected SHA256/SHA256E annex files are pinned by Git blob and content key; obtain their payloads before launch so they can be verified and retained.

Retain the printed `procedure_sha256` as `PROCEDURE_SHA256` in the comparison registration and commit the manifest before formal launches.
The digest identifies the reviewed procedure; regenerating it defines a new procedure, not a repair to an existing comparison.
Check it before each round:

```sh
pixi run assessment-procedure check \
  --host-config /private/path/launch.json \
  --base ROUND_COORDINATOR_COMMIT --study studies/CHOSEN_STUDY \
  --procedure iterations/COMPARISON/procedure.json \
  --procedure-sha256 PROCEDURE_SHA256
```

Skill gitlinks and the working-skills branch hint may change between rounds.
Scientific inputs, selected guidance, assessment, control instructions, source URLs, starting environment and shared settings must still match the seal.
Model-cache refresh timestamps and display metadata are ignored; changes to the selected model's recorded instructions, tools or capabilities fail verification.

Launch every research condition with the same procedure and successful readiness receipt:

```sh
pixi run launch --host-config /private/path/launch.json \
  --run-mode formal --study studies/CHOSEN_STUDY \
  --base ROUND_COORDINATOR_COMMIT --branch codex/run-001 \
  --condition baseline \
  --procedure iterations/COMPARISON/procedure.json \
  --procedure-sha256 PROCEDURE_SHA256 \
  --resource-readiness /path/to/run-evidence/COMPARISON/readiness/result.json \
  --evidence /path/to/run-evidence/run-001/launch
```

At worker exit, retain `launch/native/worker-end-state.json` outside its checkout.
If coordinator retention is needed, preserve the recorded artifacts unchanged in a clean `RESULT_COMMIT` descended from the worker's final commit.
Keep launch/judgment receipts outside that commit until judging is complete. The judge validates the retained artifact inventory and grades worker versioning/publication practices at worker stop; later coordinator retention receives separate attribution.
Publish that exact result commit and its required annex payloads before launching the judge; otherwise deferred coordinator publication can prevent a valid retrieval or replay check.
Record the publisher and timing separately from worker-stop evidence.

```sh
pixi run judge --host-config /private/path/launch.json \
  --run-mode formal --repo /absolute/path/to/worker-repository \
  --base RESULT_COMMIT --branch codex/judge-001 \
  --study studies/CHOSEN_STUDY \
  --procedure iterations/COMPARISON/procedure.json \
  --procedure-sha256 PROCEDURE_SHA256 \
  --resource-readiness /path/to/run-evidence/COMPARISON/readiness/result.json \
  --worker-end-state /path/to/run-evidence/run-001/launch/native/worker-end-state.json \
  --evidence /path/to/run-evidence/run-001/judgment-01
```

Formal judges use the sealed rubric/reference; do not pass a separate `--reference` override.
The fixed replay allowance is one attempt in a fresh clone of the exact result commit, including an unsuccessful attempt.
Formal launches refuse missing or changed procedure inputs and retain `formal-verified` status; development pilots remain separate.

## Retaining experiments

Preserve the exact scientific `RESULT_COMMIT` used for judging.
The scientific result and its annex payloads must already be published for judging.
After research and judging, add launch and judging receipts to the experiment repository in a later commit that records that result identity.
Publish its branch and annex payloads, then register the final commit as `results/<run>` in the study's `.gitmodules` and Git index.
Registration does not require a checkout:

```sh
mkdir -p studies/CHOSEN_STUDY/results/run-001
pixi run git -C studies/CHOSEN_STUDY config -f .gitmodules submodule.results/run-001.path results/run-001
pixi run git -C studies/CHOSEN_STUDY config -f .gitmodules submodule.results/run-001.url PUBLISHED_REPOSITORY_URL
pixi run git -C studies/CHOSEN_STUDY update-index --add --cacheinfo 160000,PUBLISHED_COMMIT,results/run-001
pixi run git -C studies/CHOSEN_STUDY add .gitmodules
```

Commit and publish the study before updating its coordinator gitlink.
Initialize individual experiments when inspecting or replaying them; leave other experiments absent.
Fetch annex content separately as needed.

## Timing and checks

Pixi tasks select Luna with high reasoning effort; keep deliberate overrides fixed across the comparison.
There is no hard cutoff by default (`--seconds 0`).
At 90 minutes, `--review-seconds 5400` emits a review receipt without terminating useful work.
A nonzero `--seconds` requests an explicit limit.

The launcher retains prompts, source identities, hook preparation and native session streams, including stderr.
`--prepare-only` checks setup and effective skill exposure without executing the task.
Automatic `AGENTS.md` loading is disabled for workers and judges; effective-prompt checks reject injected project instructions.
See [Codex project instruction discovery](https://learn.chatgpt.com/docs/config-file/config-advanced#project-instructions-discovery).

`pixi run launcher-tests` checks input isolation, role separation, judging inputs, timing and response-helper forwarding with fixtures.
These checks do not establish scientific validity, workload timing or live judge performance.
