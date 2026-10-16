# Retrieve a NARPS experiment

GitHub holds the versioned experiment trees, readable reports and small figures.
Large payloads are stored in git-annex on the CON Hub; accessing them requires an authorized Hub account through your host's credential provider.
The store retains its earlier `stamped-ai-research-next` name.

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
Each experiment's `coordinator/README.md` links its original capture, execution records and manifests; retrieve those annex paths the same way.
Git's remote configuration is local to a clone, so it must be established for each selected experiment.
Never put credentials in remote URLs or tracked files.

The [run 20 retrieval record](https://github.com/leej3/stamped-in-practice/blob/b1e9d12ec5158036eadfb6ff06a7f8b240ef80e0/coordinator/browsable-copy-01/evidence/fresh-check-01/result.json) verified all 58 supplied inputs and all 15 published scientific files through this route in a fresh Git store.
That check used an authorized account on the same host; it establishes payload retrieval, not scientific replay or access from another host.
