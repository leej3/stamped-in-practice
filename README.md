# NARPS gain-effect group analysis

Question, fixed inputs and methods are summarized in [`report/report.md`](report/report.md). The pre-analysis protocol is [`protocol/analysis-plan.md`](protocol/analysis-plan.md).

Run from the project root with the supplied interpreter:

```bash
/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python code/analyze.py --permutations 9999 --seed 240519
```

The script verifies all map checksums against `input/sources.json`, joins maps to the full pinned participant list, and writes group maps, summaries, QC tables, and figures. The group mask is the intersection of nonzero support across all 54 supplied maps. Confirmatory inference is a one-sided sign-flip max-T whole-brain FWE test. `results/permutation_max_t.npy` stores the permutation maxima. See the report for interpretation and limitations.

The principal result is summarized in the report. The invalid first full permutation attempt is preserved under `results/invalid-standard-deviation-denominator/` to make the method correction inspectable; its values must not be used. A 20-permutation pipeline pilot is under `results/pilot/`. The accepted full analysis is `results/summary.json`, with full output maps, `results/permutation_max_t.npy`, and figures in `figures/`.
