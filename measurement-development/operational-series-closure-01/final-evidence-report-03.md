# Final operational assessment series

All **32/32 judgments closed and were admitted**: 24 primaries and eight preselected duplicates. Scientific records are available for 32/32; checklists are valid for 30/32. The two invalid primary checklists remain raw and excluded by the frozen checklist gate; their independent scientific records remain available. No current slots are pending.

This report covers round 1 only: 24 original workers and 32 fresh judgments. Full machine tables retain the original 72/96 allocation; future 48 workers/64 judgments are pending outside this series. Duplicates never replace primaries.

| Primary condition | Assigned/admitted | Checklist valid | Science available | Original science categories | Native replay entrypoints |
|---|---:|---:|---:|---|---:|
| Baseline | 6/6 | 4/6 | 6/6 | 6 supported | 2/6 |
| General discovery | 6/6 | 6/6 | 6/6 | 5 supported, 1 qualified | 0/6 |
| Science discovery | 6/6 | 6/6 | 6/6 | 3 supported, 2 qualified, 1 not supported | 3/6 |
| Explicit STAMPED | 6/6 | 6/6 | 6/6 | 4 supported, 2 qualified | 2 (1 redirected)/6 |

Duplicates: 8/8 admitted, checklist-valid and science-available; 1/8 has an observed replay entrypoint. Baseline 16-j01 lacks valid assessor metadata; 23-j01 lacks the required object.capture field. The capture URI in 23’s object.url is preserved without substitution. Neither issue is a scientific verdict. The frozen aggregator correctly retains exit 2 and both issues.

## All eight preselected duplicate pairs

Every pair has both scientific categories and 31 mutually valid checklist items.

| Object suffix | Condition | Primary science | Duplicate science | Item differences /31 |
|---|---|---|---|---:|
| 08 | Baseline | supported | supported | 10 |
| 11 | Science discovery | qualified | supported | 8 |
| 03 | Science discovery | supported | supported | 7 |
| 15 | General discovery | supported | supported | 5 |
| 07 | Explicit STAMPED | qualified | supported | 9 |
| 22 | Baseline | supported | qualified | 10 |
| 05 | Explicit STAMPED | qualified | supported | 11 |
| 06 | General discovery | supported | qualified | 7 |

**5/8 scientific pairs disagree**, all supported↔qualified; checklist differences total 67/248 nested item comparisons. The independent raw check reproduced all 32 categories/report bindings and all 248 paired item statuses. Items are not independent workers; admission and schema success do not establish grading reliability or reliable variance reduction.

## Native replay evidence

All 32 slots retain a replay record, declaring 8 met and 24 not-checked. Native evidence separately establishes **8 entrypoint executions: 7 exact same-event helper-output bindings plus 21-j01’s validated redirected-output chain**. All eight helper records report return 0 and agreement for their selected outputs; their exact output lists and capture/report hashes remain in the audit.

Across 12 slots, 15 observed invocations comprise 8 completed entrypoints, **4 setup failures before entrypoint** (20-j01, 01-j01, 05-j02, 12-j01), and 3 later calls refused because the allowance had been consumed (01-j01, 05-j02, 12-j01). The final additive audit corrected an earlier filter that omitted 12-j01’s completed events with failed command status; the earlier 3/2 count, raw records and frozen extraction remain retained. 12-j01’s should/004 already says not-checked and cites absent worker testing evidence; no verdict changed.

Only selected-output comparisons on this host are established. Captured caches and available external interpreters do not establish independent environment reconstruction or cross-host portability. Optional replay unavailability is separate from scientific failure.

A disclosed assessment-context exposure is also retained: 04-j01 native event 10 displayed the sealed procedure including embedded allocation/assignment records; report line 74 acknowledges the display and denies using those records for grading. This establishes exposure, not its influence. No assessment was changed or excluded. [Exact native/report binding](final-context-exposure-04-j01-01.json).

## Reproduction and presentation

The additive relocation proof passed with main reporting commit `2f641a9134b9740a3ee859d8f2bd2d7e487fe957`: all 36 JSONL/TSV tables are byte-identical, both aggregation runs return 2, all 1,064 copied files remain unchanged, and an audit guard blocks 1,882 original evidence paths. Only reporting-tool and explicit path-map provenance differ; frozen procedure/index identities and outputs are unchanged. This is same-host table reproduction.

All six final PNGs were visually inspected. The round 1 figures use 24 workers/32 judgments, distinguish scientific availability, show 22 valid primary checklists, and retain all 8 pairs. The effort figure separates original research from reassessment. The recurring-outcomes title now explicitly states round 1; earlier and frozen figures remain retained.

## Implications for a future registered series

- Validate response schema and exact identity fields before closure, addressing the 16/23 output defects without repairing this series.
- Check that the replay destination is fresh before consuming its allowance; the four setup failures are instrument limitations.
- Examine supported/qualified thresholds using retained evidence. In object 06, the supported primary states: “The lack of participant variance maps and the data-derived coverage mask limit interpretation but do not invalidate the cautious no-support conclusion.” The qualified duplicate says “The conclusion should remain qualified” and cites nonzero-derived coverage and sign exchangeability. Object 11 similarly overlaps on coverage concerns while differing in verification threshold. These two examples are descriptive, not adjudications or an explanation of every disagreement.

## Files and identities

- [Role and condition availability, with all pair rows](final-review-01/README.md).
- [Native replay audit and exact event bindings](final-replay-audit-01/result.json).
- [Relocation proof](final-relocation-01/result.json).
- [Final figures](final-round-01-summary-v2/README.md) and [visual QA](final-figure-qa-01.json).
- [Machine report with exact hashes and source identities](final-evidence-report-02.json).
- [Independent raw checker receipt](final-review-01/independent-root-result.json).
- [Exact report excerpts for the two limited disagreement examples](disagreement-interpretation-01.json).

Final index SHA-256: `2737380bb88b4ac609736fefc496e3ad1a98c1ecc72d434c7011b33b0622ad13`. Source-map SHA-256: `70e500701144b3219334cbf3af96a0078c3d8d0261d82909253a2cb6abf02159`. Assessment seal: `6f25ebbec5310442e8fd3fd20bd20682ecb5653b350362119af3e825a2668084`.

All work here is extraction, validation and presentation. Raw assessments, frozen gates and prior snapshots are preserved; publication is coordinator-owned.
