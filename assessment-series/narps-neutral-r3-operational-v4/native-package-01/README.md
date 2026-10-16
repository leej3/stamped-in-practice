# Complete round-three native retention

All 24 research native/availability captures and 32 stopped judge captures passed the existing independent byte audits with source equality.
The [closure receipt](retention-closure.json) and [capture index](local-capture-index.json) bind the exact sources and audit records.

The [complete archive](native-retention.tar.gz) contains 315,909 entries, including 231,274 regular files (17,185,471,148 bytes) and 15,226 literal symlinks.
The [member manifest](manifest.json) and [verification](verification.json) confirm every member's bytes, mode and link text; the source inventory remained unchanged before and after packaging.
No files were excluded, and original stopped sources and logs remain retained.

The archive is 13,613,934,495 bytes, SHA256 `402f8a59d909fc332c3b1e9cff02abefea712756fad860f0433fea2c35948a06`.
The manifest SHA256 is `85f1b737735f2624ca45ea5a10e5f98e6c8d369240ef4bac7189270a4f9146ab`.
The existing [packaging method](package.py) and [task-local command evidence](command-evidence/) are retained.
Literal absolute links may require relocation on another host; no automatic cross-host execution claim is made.

Archive and manifest are retained locally in annex.
Remote upload and independent payload retrieval remain pending; hosted Entire verification is not established for this round.
See the [publication-state summary](../../../final-synthesis/PUBLICATION.md).
