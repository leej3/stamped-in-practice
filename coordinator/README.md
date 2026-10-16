# Coordinator retention for narps-neutral-r1-20

The authoritative scientific delivery is the complete verified [capture archive](delivery-01/delivery.tar.gz).
It retains dirty, untracked and ignored files, environment bytes, literal links and workspace Git metadata.
The [original manifest](original-manifest.json), [package index](delivery-01/index.json) and [stop receipt](native-attempt-01/native/worker-end-state.json) identify those exact bytes.

This publisher starts from the actual worker Git history; its checkout does not reconstruct uncommitted scientific outputs.
Dataset creation, retention and publication are coordinator actions.
The [identity record](retention.json) keeps the original capture SHA and worker HEAD separate from later retention commits.

Closed native attempt records and outer execution logs are retained under `native-attempt-01/`.
No full native profile or authentication store is included.
Archives preserve external links literally; verification streams members without extracting or following links.
