# Authorized replay record — 2026-10-16

- **Scope:** one attempt in a separate fresh clone, using the documented command from `results/report.md`; 7,200 second timeout; `--max-get-gb 5`; `--rtol 1e-6`; shipped outputs removed by the runner before execution.
- **Entry:** `pixi run duct -p logs/group-analysis-final-verified -c all -o all -t all --sample-interval 1 --report-interval 10 --message 'Final validated NARPS group inference; source SHA-256 checks enforced' pixi run python analyze.py --permutations 9999 --seed 20261015`
- **Outcome:** runner status `unmet`; exit 1. The entry did not reach the analysis because `duct` found the committed `logs/group-analysis-final-verified{stdout,stderr,usage.jsonl,info.json}` already existed and requested `--clobber`. Runner removed four output candidates before execution, not those log files.
- **Retrieval before execution:** fresh clone succeeded; 58 annex payloads were fetched (0.1 GiB); the runner removed the shipped comparison candidates. The attempted command's failure is unrelated to statistical output comparison because no regenerated results were produced.
- **Host scope:** same host as source; the runner found a `con-hub` annex route. This is not cross-host portability evidence.
- **Retained evidence:** `2026-10-16-fresh-rerun.json`, `fresh-rerun.stdout`, `fresh-rerun.stderr`, `replay-workspace/` (clone and retained runner artifacts), and `2026-10-16-replay-entry.txt`.
