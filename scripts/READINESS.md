# Check required resources

Before research, translate the applicable user prompt, system skills and memory into explicit requirements.
The repository does not prescribe a service list.
A different user may need different storage, capture or compute resources, or none of these.
Keep this checklist outside worker inputs, and record where each requirement came from:

```json
{
  "schema_version": 1,
  "requirements": [
    {
      "id": "input-retrieval",
      "description": "Independently retrieve and verify a representative required input",
      "source": "User prompt: retain independently retrievable inputs"
    }
  ]
}
```

Save the selected requirements in the iteration record, for example `iterations/CHOSEN_ITERATION/requirements.json`.
IDs must be unique lowercase letters, numbers, hyphens or underscores, starting with a letter or number, at most 80 characters.
Use a nonempty list; when no resource checks apply, record that decision instead of claiming checks passed.

Configure how this host demonstrates each requirement in `~/.config/<repository-name>/readiness.json`:

```json
{
  "schema_version": 1,
  "checks": {
    "input-retrieval": {
      "argv": ["/absolute/path/to/approved-input-probe", "--verify-retrieval"],
      "cwd": "/absolute/path/to/coordinator",
      "timeout_seconds": 120,
      "artifacts": ["retrieval.json"]
    }
  }
}
```

Replace the illustrative probe with a real user-configured command.
It should exit zero only after demonstrating the described capability, and write the declared receipt to `$READINESS_ARTIFACT_DIR/retrieval.json`.
That environment variable names a new directory for each check; declared artifacts must be files inside it.
Artifacts are optional when retained command output supplies sufficient evidence.
Use an authenticated retrieval probe to establish retrieval, for example; finding an executable or printing its version only establishes installation.
Hosted capture may need an independently verified checkpoint, and compute may need an authorized scheduler round trip.
Such probes require the permissions their operations normally require; configuring a check does not grant additional authorization.
Do not submit a job or publish a checkpoint merely to satisfy a generic checklist.

The runner executes only IDs present in the requirements file, sequentially, without a shell.
Commands inherit the host environment, including the active Pixi environment.
An explicit `cwd` avoids dependence on the invoking directory; relative paths resolve from the host configuration's directory.
The timeout defaults to 60 seconds; on POSIX, timed-out checks and their process groups are killed.
Missing checks are reported, and other checks still run after a failure.
Unknown fields in selected requirements or checks are rejected before execution.

Run through the coordinator's Pixi task:

```sh
pixi run readiness \
  --requirements iterations/CHOSEN_ITERATION/requirements.json \
  --evidence /path/to/run-evidence/resource-check-001
```

Use `--host-config /path/to/readiness.json` to select another host configuration.
Keep host configuration and credentials outside the repository; retain command evidence and ordinary paths with the iteration.
Supply credentials through existing host providers, never command arguments, requirements or receipt contents.
The runner retains argv, stdout, stderr and declared artifacts exactly; configured probes must avoid emitting secrets.
It does not copy the host configuration or inherited environment.

The evidence directory must be new and is created with owner-only access.
It contains the exact `requirements.json`, a `result.json` summary, and a directory per requirement with `receipt.json`, output files and any artifacts.
Receipts retain the requirement source, effective argv and working directory, UTC start/end times, elapsed time, exit status, and SHA-256 hashes for outputs and declared artifacts. An absent declared artifact fails its check even if the command exits zero. An interrupted run remains `complete: false` and `ready: false`; preserve it and retry in a new directory. Exit status is 0 when all requested checks pass, 1 for unmet requirements, or 2 for invalid configuration/evidence paths.

Read `result.json` before proceeding and resolve every listed `unmet_requirements` item.
The result records what these commands demonstrated at that time; it cannot establish stronger readiness than their checks.
Retain receipts with the coordinator's iteration or launch evidence, review them before publication, and rerun when the resource or task changes.
The runner does not launch research or implicitly gate the native launcher.

`pixi run readiness-tests` exercises retained receipts, missing/failed checks, timeouts, artifacts and command handling using local fixtures.
