# Coordinator retention for narps-neutral-r1-24

The authoritative scientific delivery is the complete verified [capture archive](delivery-01/delivery.tar.gz).
It retains dirty, untracked and ignored files, environment bytes, literal links and workspace Git metadata.
The [original manifest](original-manifest.json), [package index](delivery-01/index.json) and [stop receipt](native-attempt-01/native/worker-end-state.json) identify those exact bytes.

This publisher starts from the actual worker Git history; its checkout does not reconstruct uncommitted scientific outputs.
Dataset creation, retention and publication are coordinator actions.
The [identity record](retention.json) keeps the original capture SHA and worker HEAD separate from later retention commits.

Closed native attempt records and outer execution logs are retained under `native-attempt-01/`.
The original raw transcript and native capture witnesses are retained separately under `native-capture-01/`.
Historical Entire attachment is performed only on this later coordinator commit and earns no worker credit.
No full native profile or authentication store is included.
Archives preserve external links literally; verification streams members without extracting or following links.

## Browsable original files

Original scientific files are also available at their unchanged workspace paths.
The [copy manifest](browsable-copy-01/manifest.json) records exact source hashes, original modes and storage choices.
These are coordinator presentation copies; the complete archive remains authoritative.
The input tree matches the [shared retrieval proof](browsable-copy-01/shared-input-route-proof.json); its 58 payloads were independently retrieved in the cited run 20 check.
No scientific execution or worker credit is implied.
