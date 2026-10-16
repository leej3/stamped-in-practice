# Worker stop evidence and attribution

The native research launcher writes `worker-end-state.json` outside the worker checkout immediately after the native process stops, before joining log streams or collecting skill observations.
It records successful, failed and timed-out workers; handled launcher interruptions also retain a receipt.
`result.json` links the receipt by relative path and SHA-256.
No worker prompt changes, commits, staging, repairs, fetches or publication occur during capture.

Schema version 1 has `kind: worker-end-state`, capture start/end timestamps, `capture_status`, `errors`, and `worker` termination metadata.
Repository fields are `head_commit`, `head_ref`, local `refs`, exact NUL-delimited porcelain v1 status encoded as `status_porcelain_v1_z_base64`, staged `index` entries, and `worktree` entries.
Each index entry retains its Git mode, object ID and conflict stage.
Each file entry retains its relative path, tracked status, type and SHA-256; regular files also retain size and executable status.
Missing tracked files remain explicit.
Initialized `submodules` and untracked `embedded_repositories` have recursive repository observations; uninitialized modules retain their index commit.

Git's standard exclusions govern untracked discovery, so ignored `.pixi` environments and caches are not traversed.
Explicitly tracked ignored files remain included.
Generic symlinks retain their target string and the SHA-256 of that string, without reading the target.
Recognized annex links additionally record their key and, when locally available, the payload size and SHA-256 from that exact annex object.
This distinguishes link representation from scientific content without materializing missing annex objects.
Unsupported files, failed Git commands and detected concurrent changes produce partial evidence rather than a falsely complete observation.

Formal judge integration passes `--worker-end-state PATH`, retains the original receipt bytes and hash in external judge evidence, and calls `validate_retained_artifacts(receipt, result_checkout)` before launching the judge.
That helper requires a complete receipt, a clean result checkout, unchanged scientific material and a result commit descended from the worker's recorded HEAD.
It returns the worker HEAD and judged result commit separately.
Coordinator evidence belongs outside the judged scientific result commit and may be retained in a later commit.

Preservation can commit previously untracked output or move regular output into annex without changing its bytes.
Available annex payloads are compared by content hash and size.
Unavailable SHA256/SHA256E payloads can establish content identity by key digest and size; `annex_identity_without_local_payload` explicitly records this weaker check.
For other backends such as MD5E, an unchanged exact annex key and symlink target can establish retained reference identity when either payload is unavailable; `annex_reference_identity_without_local_payload` records this separately.
That reference check establishes neither content verification nor retrieval, and never overrides a detectable SHA256 mismatch.
Both available payloads still require matching SHA-256 content hashes; converting a regular file to a non-SHA256 annex key requires available payload bytes for verification.
Clean unchanged submodules can match by commit without initialization; those checks appear in `submodule_identity_without_checkout`.
Dirty nested results require a retained, materialized matching snapshot.
None of these identity checks demonstrates independent retrieval or remote availability.

Judges assess scientific artifacts in the exact result commit, but attribute Git/versioning/publication behavior to the worker stop receipt and execution evidence.
A coordinator preservation commit, annex conversion or later push earns no worker credit for those actions.
The original dirty status, index, untracked outputs and worker HEAD remain relevant even when the preserved result is clean.
Local refs and a clean working tree alone do not prove that the worker published or independently verified retrieval.

Capture is a timed observation, not an atomic filesystem snapshot.
Detached descendants and a launcher killed before its cleanup can prevent a complete receipt; the launcher records its process-containment limitation.
Ignored outputs are outside the inventory.
Historical results lacking this receipt keep that limitation; do not reconstruct a stop-time observation from a later preservation commit.
