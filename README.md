# NARPS equal-indifference gain group analysis

This project tests whether the supplied gain-effect maps show a positive group effect in ventromedial prefrontal cortex (vmPFC). It performs group inference only. The participant maps and upstream modeling are fixed inputs; no time-series scans are used or downloaded. See [REPORT.md](REPORT.md) for the scientific result and [analysis/PROTOCOL.md](analysis/PROTOCOL.md) for the prespecified group analysis and interpretation limits.

## Requirements

Install [Pixi](https://pixi.sh/) and Git with git-annex. Network access is needed to retrieve annexed inputs and install the locked environment. The Pixi lock targets macOS 14 on Apple Silicon and Linux x86-64. The analysis itself runs in the project Pixi environment; it needs no scanner data, license server, GPU, or site-specific mount.

## Retrieve and run

Check out the environment snapshot branch. It contains the task source tree and the exact lock file as its only additional commit:

```sh
git clone --branch codex/env-narps-r1-12-20261015 https://github.com/leej3/stamped-in-practice.git
cd stamped-in-practice
git annex init
git remote add con-hub https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git
git config remote.con-hub.annexurl annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp
git config remote.con-hub.annex-uuid 6215ce45-8f0f-4062-9bc0-d04781b4cd11
git config remote.con-hub.fetch '+refs/heads/*:refs/remotes/con-hub/*'
git annex enableremote con-hub
git annex sync --no-push con-hub
git annex get input/data input/atlas results/group-analysis
pixi install --locked
pixi run validate-results
pixi run group-analysis -- --permutations 9999 --output-dir results/replay
pixi run python analysis/compare_replay.py results/group-analysis results/replay
```

The GitHub remote carries the Git branches; the configured `con-hub` annex remote carries large-file content and its location records. `git annex sync --no-push` retrieves those records without publishing changes from the clone.

The primary inference uses 9,999 sign flips with seed 20261015. Accepted outputs are under `results/group-analysis/`; the documented replay writes fresh outputs to `results/replay/` and compares them with the accepted files. This protects annexed outputs in a fresh clone. `logs/` contains duct command metadata, standard output and error, and sampled resource use. [`results/group-analysis/provenance.json`](results/group-analysis/provenance.json) records the code revision, exact lock checksum, input-manifest hashes, command, and clean-checkout replay. Inputs and their checksums are described in `input/sources.json` and `input/atlas/sources.json`.

## Updating the environment

Change dependency ranges in `pixi.toml`, run `pixi lock`, and confirm the environment with `pixi install --locked` and the documented validation task. Commit the task changes first. Then create or refresh the matching `codex/env-<run>` branch at the task commit, force-add `pixi.lock`, commit that lock snapshot as the sole environment commit, and return to the task branch. Record the task commit, environment commit, and lock SHA256 with any new result run. Keep the working `pixi.lock` ignored on the task branch.

The group model, mask, vmPFC definition, QC, and report interpretation are described in [analysis/PROTOCOL.md](analysis/PROTOCOL.md). Earlier development outputs are retained but marked superseded in [results/README.md](results/README.md).
