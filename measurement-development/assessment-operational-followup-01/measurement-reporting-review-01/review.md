# Reporting review

The draft supports a separate, descriptive remeasurement of the same deliveries.
The reviewed criteria do not define a numerical measurement-viability threshold.
No new-series outcomes were inspected; this review does not decide viability or authorize launch.
Source snapshots, hashes and allocation checks are retained in `evidence.json` and `sources/`; `retain_evidence.py` records the checks.

Two reporting details need to be made explicit before adopting the mechanism:

1. **Document the v4 reporting path.** The existing guide says the assessment seal references the same procedure bytes and that neutral research and assessment digests remain identical ([AGGREGATION.md:31](/Users/johnlee/code/CON/stamped-in-practice/scripts/AGGREGATION.md:31), [line 102](/Users/johnlee/code/CON/stamped-in-practice/scripts/AGGREGATION.md:102)).
   The implementation already accepts a v4 assessment seal embedding the exact original research procedure and allocation with the unchanged assessor pin ([aggregate_comparison.py:335](/Users/johnlee/code/CON/stamped-in-practice/scripts/aggregate_comparison.py:335)).
   Suggested clarification: “The original neutral series uses one research and assessment digest. A separately registered v4 assessment series uses its own assessment digest and embeds the exact original research procedure and allocation. Keep its extraction index and outputs separate; never substitute or pool it with the original measurements.”
   Attach the exact reporting command and source identity to the new series; preserve the frozen original records.
2. **Separate series and full-study denominators.** The repeated series has 24 workers, 24 primary and eight duplicate slots: six workers and two duplicate objects per condition.
   The full allocation remains 72 workers/96 judgments; future unlaunched rounds remain pending, outside this series, not failures. Report both scopes explicitly rather than labeling full-allocation pending rows as failures of this remeasurement ([original registration:38](/Users/johnlee/code/CON/stamped-in-practice/iterations/narps-neutral-v1/registration.md:38), [AGGREGATION.md:30](/Users/johnlee/code/CON/stamped-in-practice/scripts/AGGREGATION.md:30), [draft:3](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/repaired-series-preparation-01/registration-draft.md:3)).

Use this checklist for the descriptive report and recorded viability decision:

- **Identity and completion:** retain the sealed procedure/slot/session identity, original captures, admission decision and reasons for every attempt.
  All 32 attempts ending with available evidence retained is completion; favorable grades or replay success are not prerequisites.
  Preserve the original primary roles and all eight preselected pairs ([draft:19–23](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/repaired-series-preparation-01/registration-draft.md:19)).
- **Unavailable measurements:** show admission and checklist, scientific and replay availability separately by condition and role, with causes and assigned denominators.
  An invalid/missing scientific record is unavailable scientific evidence, not an explicit “unable to assess” verdict or automatically a lost checklist assessment. Preserve unaffected evidence and raw answers ([AGGREGATION.md:65–78](/Users/johnlee/code/CON/stamped-in-practice/scripts/AGGREGATION.md:65), [lines 96–101](/Users/johnlee/code/CON/stamped-in-practice/scripts/AGGREGATION.md:96), [aggregate_comparison.py:627](/Users/johnlee/code/CON/stamped-in-practice/scripts/aggregate_comparison.py:627)).
- **Checklist disagreement:** compare exact item statuses only within this version on mutually valid paired items; show both item and object denominators and incomplete pairs.
  Keep met, partial, unmet, not-checked and not-applicable separate, with applicable/full denominators and no overall score. Do not treat checklist items as independent workers ([AGGREGATION.md:131–137](/Users/johnlee/code/CON/stamped-in-practice/scripts/AGGREGATION.md:131)).
- **Scientific disagreement:** separately tabulate differences in explicit scientific-adequacy categories among valid same-version pairs.
  Keep report hashes and exact quotes, and retain hypothesis conclusions separately; different hypothesis directions or defensible methods alone do not establish inadequate science.
  Show missing scientific pairs separately from agreement ([comparison-plan.md:6–9](/Users/johnlee/code/CON/stamped-in-practice/comparison-plan.md:6), [lines 34–37](/Users/johnlee/code/CON/stamped-in-practice/comparison-plan.md:34), [scientific-judging.md:9–16](/Users/johnlee/code/CON/stamped-in-practice/iterations/narps-neutral-v1/scientific-judging.md:9), [aggregate_comparison.py:1079–1108](/Users/johnlee/code/CON/stamped-in-practice/scripts/aggregate_comparison.py:1079)).
- **Worker variability:** use only the new-series primary judgments of the original workers for condition summaries: individual observations, outcome counts and defensible medians/ranges. Omit checklist medians/ranges when valid item identities differ.
  Neither duplicates nor repeat-series observations add workers.
  Avoid reliable variance, significance or skill-improvement claims; cross-series changes are changes in measurement of fixed objects ([comparison-plan.md:25–37](/Users/johnlee/code/CON/stamped-in-practice/comparison-plan.md:25), [AGGREGATION.md:137](/Users/johnlee/code/CON/stamped-in-practice/scripts/AGGREGATION.md:137), [draft:27](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/repaired-series-preparation-01/registration-draft.md:27)).
- **Viability and effort:** record which planned descriptive comparisons the available measures support and which remain limited, including uneven missingness and duplicate availability.
  No registered cutoff justifies inventing a pass percentage or agreement threshold after outcomes.
  Keep subsequent research on hold until that reasoned decision is recorded.
  Separate reassessment/coordinator effort from original worker effort; absent or overlapping measurements cannot become totals ([draft:29](/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/repaired-series-preparation-01/registration-draft.md:29), [comparison-plan.md:18–28](/Users/johnlee/code/CON/stamped-in-practice/comparison-plan.md:18), [AGGREGATION.md:84–94](/Users/johnlee/code/CON/stamped-in-practice/scripts/AGGREGATION.md:84)).
