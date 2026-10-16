#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Write the portable binding for poster display copies of benchmark figures."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = Path("experiments/narps-poster")
FIGURES = EXPERIMENT / "figures"


def entry(relative: Path):
    path = ROOT / relative
    return {"path": relative.as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size}


def main():
    sources = [
        EXPERIMENT / "map-inputs/example/provenance.json",
        EXPERIMENT / "map-inputs/spatial/provenance.json",
        EXPERIMENT / "map-inputs/spatial/spatial-inputs.npz",
        FIGURES / "narps-group-map-manifest.json",
        FIGURES / "narps-spatial-manifest.json",
        FIGURES / "narps-spatial-summary.json",
        Path("pixi.toml"),
    ]
    sources.extend(Path("scripts") / name for name in (
        "render_narps_group_map.py", "render_narps_spatial.py",
        "extract_narps_spatial.py", "capture_narps_group_map.py",
        "narps_figure_sources.py", "narps_poster_figure_manifest.py",
    ))
    manifest = {
        "schema_version": 1,
        "repository": "https://github.com/leej3/stamped-in-practice",
        "branch": "codex/stamped-poster-analysis",
        "command": "pixi run poster-figures",
        "scope": "Scientific figure source of truth. Presentation repositories retain display copies; source data, code and scientific provenance remain here.",
        "figures": [entry(FIGURES / name) for name in (
            "narps-group-map.svg", "narps-group-map.png",
            "narps-spatial-agreement.svg", "narps-spatial-agreement.png",
        )],
        "sources": [entry(path) for path in sources],
    }
    output = ROOT / FIGURES / "poster-figure-manifest.json"
    output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
