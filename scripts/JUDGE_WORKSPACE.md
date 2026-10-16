# Judge session workspace

`prepare_launch.py --role judge` keeps `--clone-path` as the exact research target.
It creates a separate parentless Git repository at `EVIDENCE/judgment`, or at the explicit `--judge-workspace` path.
The initial commit contains only `.gitignore` and `judge-target.json`, recording the target path, commit and tree.
The workspace contains no imported research history.

Native hooks, project trust and the provenance chain are prepared in this workspace.
Both the native session's working directory and `STAMPED_JUDGE_OUTPUT` name that repository.
`STAMPED_JUDGE_TARGET` names the separate assessed checkout.
Native launch logs remain in `EVIDENCE/native`.

Before launch, the workspace must still be its clean seed, and the target must match its recorded identity and be clean.
The original worker-stop artifact check still applies to the target.
After judging, the launcher checks the target again and retains a failure if its commit, tree or working state changed.
The result receipt records the session's starting commit separately from the target identity.

The launcher leaves judgment artifacts uncommitted.
After the native session stops, the coordinator can preserve them with an ordinary attributed commit in the judgment repository, allowing Entire's native hooks to condense the real session.
Verify the resulting native and hosted checkpoint with the existing capture workflow.
Fixture tests establish repository isolation and execution routing; they do not establish live Entire capture.
