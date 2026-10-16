# Current-series evidence availability

Only round1:24 workers/32 judgments; primary24/duplicate8. Full original allocation72/96 retained; future48/64 outside current-series missingness.

Counts describe retained evidence and frozen validation gates. They are not new grades. Native completion, admission, checklist validity, scientific extraction and replay are separate; duplicate observations never replace primaries.

| Group | Assigned | Closed | Admitted | Checklist valid | Checklist invalid | Science available | Replay record | Same-event replay entrypoint |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| All current slots | 32 | 32 | 32 | 30 | 2 | 32 | 32 | 7 |
| primary | 24 | 24 | 24 | 22 | 2 | 24 | 24 | 6 |
| duplicate | 8 | 8 | 8 | 8 | 0 | 8 | 8 | 1 |
| baseline | 8 | 8 | 8 | 6 | 2 | 8 | 8 | 2 |
| baseline / primary | 6 | 6 | 6 | 4 | 2 | 6 | 6 | 2 |
| baseline / duplicate | 2 | 2 | 2 | 2 | 0 | 2 | 2 | 0 |
| discover-general | 8 | 8 | 8 | 8 | 0 | 8 | 8 | 0 |
| discover-general / primary | 6 | 6 | 6 | 6 | 0 | 6 | 6 | 0 |
| discover-general / duplicate | 2 | 2 | 2 | 2 | 0 | 2 | 2 | 0 |
| discover-science | 8 | 8 | 8 | 8 | 0 | 8 | 8 | 3 |
| discover-science / primary | 6 | 6 | 6 | 6 | 0 | 6 | 6 | 3 |
| discover-science / duplicate | 2 | 2 | 2 | 2 | 0 | 2 | 2 | 0 |
| stamped-explicit | 8 | 8 | 8 | 8 | 0 | 8 | 8 | 2 |
| stamped-explicit / primary | 6 | 6 | 6 | 6 | 0 | 6 | 6 | 1 |
| stamped-explicit / duplicate | 2 | 2 | 2 | 2 | 0 | 2 | 2 | 1 |

Replay records can declare non-attempt or unavailable states. The automated replay column requires exact same-event helper output binding and an explicit entrypoint return code; outer shell exit is insufficient. A separately reviewed redirection chain is reported additively in the final evidence brief and does not change this automated count. The command-candidate inventory includes mentions and is not an attempt count.

## Preselected duplicate pairs

| Object | Condition | Checklist comparable items | Checklist disagreements | Primary science category | Duplicate science category | Science pair available | Science disagreement |
|---|---|---:|---:|---|---|---|---|
| narps-neutral-r1-08 | baseline | 31 | 10 | supported | supported | True | False |
| narps-neutral-r1-11 | discover-science | 31 | 8 | qualified | supported | True | True |
| narps-neutral-r1-03 | discover-science | 31 | 7 | supported | supported | True | False |
| narps-neutral-r1-15 | discover-general | 31 | 5 | supported | supported | True | False |
| narps-neutral-r1-07 | stamped-explicit | 31 | 9 | qualified | supported | True | True |
| narps-neutral-r1-22 | baseline | 31 | 10 | supported | qualified | True | True |
| narps-neutral-r1-05 | stamped-explicit | 31 | 11 | qualified | supported | True | True |
| narps-neutral-r1-06 | discover-general | 31 | 7 | supported | qualified | True | True |

These are repeated measurements of eight existing objects. Item comparisons are nested within objects and do not increase worker sample size. Schema and integrity success do not establish grading reliability; these disagreements are retained without adjudication or claims of reduced variance.

## Retained checker issues

- narps-neutral-r1-23 / response: object.capture differs from the original delivery capture
- narps-neutral-r1-16 / response: assessor/skill: None is not of type 'string'; assessor/version: None is not of type 'string'; assessor/dependencies: [] should be non-empty

Raw records and frozen acceptance criteria are unchanged. Independent science remains governed by its separate structured-record and report/capture bindings.

## Source identities

- `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/round-01-operational-extraction-01/snapshot-batch-11/index.json`: `2737380bb88b4ac609736fefc496e3ad1a98c1ecc72d434c7011b33b0622ad13`
- `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/round-01-operational-extraction-01/snapshot-batch-11/snapshot.json`: `b6c7cce2ee5a1d314f8e098f7104301f87a4e9c57cec5f81ae100bbd54afe97e`
- `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/round-01-operational-extraction-01/snapshot-batch-11/round-01-availability.json`: `5d86b7e28804bec43d9c0ebcd89ab7358f97fc4f9cb4bac8114f0f04cdcb841d`
- `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/round-01-operational-extraction-01/snapshot-batch-11/replay-native-observations.json`: `8482f52279be46d42f109e4c7c415839aa4641d7ba7f45f22d829ef0c383c2b4`
- `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/round-01-operational-extraction-01/snapshot-batch-11/source-manifest.json`: `70e500701144b3219334cbf3af96a0078c3d8d0261d82909253a2cb6abf02159`
- `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/round-01-operational-extraction-01/snapshot-batch-11/analysis/aggregation.json`: `3c716d2ae67db2f39dae7f35893f31a9c92db02dad5b6aca40928caca0f5cc01`
- `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/round-01-operational-extraction-01/snapshot-batch-11/analysis/judgments.jsonl`: `913293575d82499aef62cbd46300c66baff30a568d24f7825dcb521a24466683`
- `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/round-01-operational-extraction-01/snapshot-batch-11/analysis/pairs.jsonl`: `4587ac871933b36a37cb716da7a5b5515888d5090813fb512d786d1f49a2e500`
- `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/round-01-operational-extraction-01/snapshot-batch-11/analysis/disagreement.jsonl`: `6d981fa609a8b94cdcc66be2c4d85c36c578052b946a9d6fc614ec520c45d86c`
- `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/round-01-operational-extraction-01/snapshot-batch-11/analysis/issues.jsonl`: `8ab4129e6fed4aa855c7c6ac919b28cd2a708398748fa263c581409776c64fdd`
