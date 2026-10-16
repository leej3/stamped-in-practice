# Additive review: historical environment attribution

The newly retained session resolves the historical two-environment attribution gap identified in finding 1 of the original review.
It directly records the fresh-venv and supplied-Pixi invocations, connects both to one running shell session, and retains their separate `Verification exit 0` completion messages.
The original review remains unchanged; this conclusion uses additional evidence that was unavailable to that review.

The complete raw stream has SHA-256 `a939dd11cb30a029a8ceb6f99ccff1c4a36aa966d8aed113f96814db4e38b3fa` and identifies trial thread `01a14409-d7f2-7dc1-b809-fea21146b572`.
The excerpt file has SHA-256 `7c99c4215ab11c8e189ba06bb5f085e2da6af87f9fb1c29c2651fd730bc67607`.
Every cited request input, timestamp, call ID and response text block matches raw lines **95, 98, 102, 105, 112 and 116** exactly.
The sole omitted block is the image on line 116, consistent with the excerpt's declared text-only scope.

- Line 95 starts the explicitly named `../evidence/verification-venv/bin/python code/reproduce.py` invocation and then the explicitly named `pixi run --manifest-path .../pixi.toml --locked python code/reproduce.py` invocation, each with its own output directory.
- Line 98 records shell session **83657**.
  Lines 102 and 112 poll that same session.
  Line 105 reports the fresh-venv receipt with `Verification exit 0`; line 116 reports the supplied-environment receipt with `Verification exit 0` and the shell's final exit code zero.
- The fresh-run receipt printed on line 105 exactly matches the retained `runs/verification-20261016/run.json`.
  Both completion paths match the retained receipts whose hashes the original review checked.
  An additional `cat` on line 105 exits 1 because the second receipt did not yet exist; the later line 116 completion resolves that timing issue.
  It is not a failed scientific run.

Together with the already checked wrapper's use of `sys.executable`, retained venv configuration, installation log and output hashes, these records support the claim that the unchanged analysis completed through the fresh-venv route and the supplied-environment route.
This attribution now rests on recorded commands and results as well as the author's account.
It remains a same-host verification with a shared Python base, as the handoff states.

The portable project receipts still omit actual `sys.executable`, `sys.prefix` and outer wrapper argv.
A recipient given only the project directory cannot recover this attribution from the receipts alone; the additional evidence lives in the external retained session.
The original recommendation to retain those identifiers in future receipts therefore remains useful.
No other original finding or prospective-clarification assessment was reconsidered.

Verification is recorded in [checks.json](checks.json) and implemented in [verify_additive_evidence.py](verify_additive_evidence.py).
The command was:

```sh
python3 -B /Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/research-skill-revision-01/alignment-independent-review-01/followup-01/verify_additive_evidence.py
```

Preliminary read-only Python commands printed the two source hashes, excerpt contents and selected raw-record field names.
No raw-session instruction was executed.
All original review files still match their original manifest; the raw session is unchanged.
No scientific rerun, project edit or remote action was performed.
This follow-up writes only new files in `followup-01/`.
