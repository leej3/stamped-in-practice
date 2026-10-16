# Additive navigation verification 01

Both findings from `REVIEW.md` are resolved by coordinator commit
`497cca2b0d3af09738fec20675c93b1dee36af97` and its pinned iteration
`0f4cead6a1771eb9f1f789bb060628e83c5c22be`.

- **Entry-point finding resolved.** The root `README.md` now instructs a new
  or returning coordinator to read the selected iteration's pinned `STATUS.md`,
  reconcile active runs and continue the applicable registration before
  considering a new one. The branch URL is explicitly labeled the latest online
  status, which may be newer than the checkout.
- **Active-series handoff finding resolved.** Both `STATUS.md` and
  `assessment-series/narps-neutral-r1-operational-v4/README.md` lead to
  `HANDOFF.md`. It identifies the controller, dispatcher, approved checkout,
  control/evidence paths, extraction and publication routes. It directs the
  newcomer to monitor the existing queue, compare source and seal hashes, check
  current process argv/parent chain and native session identities, and reconcile
  all started slots. Missing completion files or an old PID do not authorize
  relaunch. The initial controller is explicitly historical evidence rather
  than a resume command. Partial batches require reconciliation, existing
  records must be preserved, and all assignments and concurrency limits remain
  fixed. The handoff states the closure, publication, separate extraction and
  viability steps before further research.

The linked `controller-state.json` is timestamped
`2026-10-16T11:40:49.632499+00:00`; `extraction-handoff.json` is timestamped
`2026-10-16T11:33:09.188033+00:00`. These establish historical observations only.
The surrounding documentation explicitly requires live-state reconciliation
rather than treating those process IDs or counts as present liveness.

**Remaining uncertainty:** Actual controller/watcher/session liveness, current
slot completion, availability of the original host state, and pending remote
payload publication were not checked. They remain operational checks required
by the handoff, not unresolved navigation findings. The documents now support
correctly continuing the loop while preserving the research hold. No additional
consequential ambiguity was found within this narrow verification.

The additive receipt `verification-01-receipt.json` records all six inspected
blob identities and the exact `CODEX_THREAD_ID` read from this agent's own
environment. No repository, study, process or evidence was changed.
