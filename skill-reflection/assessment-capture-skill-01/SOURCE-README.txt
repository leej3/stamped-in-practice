# Capture-preserving assessment helpers

Published source: [con/skills `55f5b51`](https://github.com/con/skills/commit/55f5b5123dc1e300ebea6098e1616080c3a7905c), branch `codex/assessment-capture-drafts`.
The [independent trial records](https://github.com/con/skills/tree/7869a62fbe948b894f546cf576837f18314226ae/stamped/blind-runs/2026-10-16-capture-draft) were published before the parent gitlink.
An empty Git receiver independently retrieved and verified five changed source files and all 48 changed evaluation files.

The helpers now protect a supplied capture response from probe-draft replacement, fill a missing assessment date, and check remote module revisions in a disposable bare repository.
Report examples include not-applicable counts and the probe's correct license key.
Only three lines were added to the assessment skill's main instructions; the substantive safeguards are in scripts.

Two independent full skill-use trials completed all 31 items while preserving response capture and Git identifiers.
They used different fixtures and sequential snapshots, so this is not a model comparison.
Case A exposed the missing date default.
Case B exposed a probe write into `.git/FETCH_HEAD`; that failed integrity result and the agent's incorrect runtime stamp remain unchanged.
The original fixture and all scientific files stayed intact.
A fresh, narrow case C exercised the fixed remote probe on a new copy: the unavailable revision was detected and canonical capture validation passed with an unchanged inventory.
The case-C reader's wrapper-directory comparison limitation is retained alongside the canonical check.

[Final source and test record](final-validation-summary-02.json): 158 tests passed, 28 skipped, 26 recorded evaluations passed, all 18 injected defects detected; 27 skills validated with no errors and 10 existing warnings.
[Publication verification](publication-verification.json) binds exact remote commits and retrieved bytes.
These checks do not establish grading reliability or a STAMPED skill benefit.
No formal NARPS result was regraded and no scientific replay occurred in these skill-use trials.

This directory retains the exact prompts, copied skills, original fixtures and Git histories, complete command logs, native agent sessions, independent reviews, tests and test environment, publication receipts, and failed attempts.
Earlier snapshots and summaries remain available; `final-validation-summary-02.json` is the completed candidate record.
The original fast root-verification failure was removed by duct's default failure threshold; its command/error remain in the parent native transcript and `case-b/root-verification-attempt-01.json`.
Subsequent checks retain quick failures with `--fail-time 0`.
