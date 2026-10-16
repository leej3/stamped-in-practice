# Run history

1. Initial attempt: data integrity checks passed, but the run stopped before group inference when Nilearn could not download Harvard–Oxford from NITRC because the host certificate was reported expired. No group result was produced by this attempt.
2. Method revision: removed the network-dependent atlas step and operationalized vmPFC with an independent, literature-defined 5 mm MNI sphere centered at [2, 46, -8] (see protocol and report). This revision was made before inference outputs were available.
3. Accepted analysis: `python analysis/group_analysis.py`; all 54 map checks passed and the registered sign-flip max-t inference completed. The script also compares the observed statistic and fixed signed statistics against SciPy's one-sample t implementation.
4. Replay: the same command was run again from the workspace root with the same environment and seed. Selected scientific outputs were compared by SHA-256 and matched exactly (see `results/replay-check.txt`).
