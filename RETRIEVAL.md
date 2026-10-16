# Read and retrieve the research files

[Project overview](README.md) · [Repository map](docs/repository-map.md) · [Results guide](docs/results.md)

You can read the study and its findings without downloading the complete archive.
Start with the results guide, then choose a particular experiment or figure when you need its underlying files.
GitHub holds the versioned experiment trees, readable reports and small figures.
Large payloads are stored in git-annex on the CON Hub; accessing them requires an authorized Hub account through your host's credential provider.
The store retains its earlier `stamped-ai-research-next` name.

## Retrieve one experiment

The commands below are for a local clone of `stamped-in-practice` on `main`.
A submodule is a linked repository at a recorded revision; initializing it makes that component available locally.
There is no need to download all experiments to inspect one result.

From this repository's root, initialize only the selected study and experiment at their recorded commits:

```sh
git submodule update --init studies/narps
git -C studies/narps submodule update --init results/narps-neutral-r1-20
experiment=studies/narps/results/narps-neutral-r1-20
```

Configure the payload route once in that experiment's fresh clone.
Pixi supplies git-annex from this repository's environment; no recursive submodule update is needed.

```sh
pixi run git -C "$experiment" annex init
git -C "$experiment" config remote.origin.annex-ignore true
git -C "$experiment" remote add con-hub \
  https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git
git -C "$experiment" config remote.con-hub.annexurl \
  annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp
git -C "$experiment" fetch origin git-annex:refs/remotes/origin/git-annex
pixi run git -C "$experiment" annex merge
pixi run git -C "$experiment" annex get --from con-hub -- results/group_tstat.nii.gz
```

Replace the experiment and final file path with the ones you need.
Current tool-neutral experiments link their original captures, execution records and manifests from `coordinator/README.md`.
Older development experiments use `coordinator/retention-01/README.md`; retrieve the linked annex paths the same way.
Git's remote configuration is local to a clone, so it must be established for each selected experiment.
Never put credentials in remote URLs or tracked files.

The [run 20 retrieval record](https://github.com/leej3/stamped-in-practice/blob/b1e9d12ec5158036eadfb6ff06a7f8b240ef80e0/coordinator/browsable-copy-01/evidence/fresh-check-01/result.json) verified all 58 supplied inputs and all 15 published scientific files through this route in a fresh Git store.
That check used an authorized account on the same host; it establishes payload retrieval, not scientific replay or access from another host.

## Know what a download establishes

A successful download establishes access to those files through that route.
It does not by itself demonstrate that an analysis can be rerun, that every archive is available, or that the reported conclusion is supported.
The [completed comparison's publication record](https://github.com/leej3/stamped-in-practice/blob/codex/iteration-narps-neutral-v1/final-synthesis/PUBLICATION.md) distinguishes published source, verified payload retrieval and pending full archives.

For poster exports and derived figure inputs, begin with the [poster guide](docs/poster.md).
Those have their own directories and retrieval records; the single-experiment example above does not retrieve them.
