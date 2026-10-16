# Preparation status before sealing

The design is resolved: unchanged task and inputs, four strategies, three rounds, six workers per cell, two preselected duplicate judgments per cell, 72 workers and 96 judgments.
The fixed sample is the completion rule; there is no spending cap and no tuning after the final round.

- Execution identity is verified by `resources/native-host-preflight-01/`: local native 0.162.0-alpha.17.2, `gpt-6-luna` with high reasoning and three concurrent sessions. The exact executable, normalized profile and model-contract hashes match a completed native judgment. No new model trial or cluster work was used.
- All 58 scientific inputs are materialized and byte-verified in `resources/input-preflight-01/result-complete.json`. The initial metadata-related retrieval failure remains retained.
- Optional scientific resources are prepared outside the coordinator checkout. The final resource sheet, manifest, validated lock and inventory will be sealed. There is no separately enforced per-worker CPU or memory quota.
- The prospective assessor is `9852d8360f9519d21d11099b45f5deb8ba80cb28`; round-one research guidance is `f2e74ea3ed372f966c95692cb0826d56ad5e6a6c`. Later explicit guidance revisions are selected only between rounds. The assessor remains fixed.
- Focused launcher integration remains in progress: neutral input-only seed, bounded original-delivery snapshot, condition-free attribution receipt, optional complete-copy replay and coordinator-side execution logging. Commit and seal the reviewed implementation and exact rendered prompts before any formal worker receives its task.

The replay bounds remain 7,200 seconds and 5 GB for the optional measurement, not a worker budget.
The judge must select generated outputs explicitly, protect inputs and use scientifically relevant comparisons.
Unavailable adapters or invalid measurements remain explicit; they do not justify replacing an assigned outcome.
The earlier six-worker schedule is preserved under `superseded-six-worker-waves/`; the active allocation has eight balanced three-worker waves per round, with the original assignments and duplicate selections unchanged.
