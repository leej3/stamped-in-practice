#!/usr/bin/env bash
set -euo pipefail
PYTHON=${PYTHON:-/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python}
"$PYTHON" scripts/retrieve_maps.py > results/retrieval-manifest.txt
"$PYTHON" scripts/group_analysis.py > results/run.stdout 2> results/run.stderr
