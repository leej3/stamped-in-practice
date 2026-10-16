#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Render spatial reproducibility and recompute its numerical summary offline."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import matplotlib
matplotlib.use("Agg")
from matplotlib.colors import BoundaryNorm, ListedColormap, LinearSegmentedColormap
import matplotlib.pyplot as plt
import numpy as np
from summarize_poster_outcomes import LABELS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "experiments/narps-poster/map-inputs/spatial"
OUT = ROOT / "experiments/narps-poster/figures"
INK = "#17344c"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(fig, stem):
    try:
        for extension in ("svg", "png"):
            with tempfile.NamedTemporaryFile(dir=OUT, suffix=f".{extension}", delete=False) as handle:
                temporary = Path(handle.name)
            try:
                fig.savefig(
                    temporary, format=extension, dpi=160, facecolor="white",
                    metadata={"Date": None} if extension == "svg" else {},
                )
                if extension == "svg":
                    temporary.write_text("\n".join(line.rstrip() for line in temporary.read_text().splitlines()) + "\n")
                # Replace the directory entry, never write through an annex link.
                temporary.replace(OUT / f"{stem}.{extension}")
            finally:
                temporary.unlink(missing_ok=True)
    finally:
        plt.close(fig)


def main():
    global DATA, OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=DATA)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    DATA, OUT = args.inputs.resolve(), args.output.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    meta = json.loads((DATA / "provenance.json").read_text())
    if digest(DATA / "spatial-inputs.npz") != meta["npz_sha256"]:
        raise ValueError("Spatial input hash mismatch")
    arrays = np.load(DATA / "spatial-inputs.npz")
    shared = arrays["shared_support"]
    native = arrays["native_masks"]
    positive = arrays["native_positive"]
    if not np.array_equal(shared, native.all(axis=0)):
        raise ValueError("Shared support is not the recorded intersection")
    if np.any(positive & ~native):
        raise ValueError("Positive decision outside native tested support")
    groups = [[i for i, row in enumerate(meta['records']) if row['condition'] == c['id']]
              for c in meta['conditions']]
    if [len(ids) for ids in groups] != [12] * 4:
        raise ValueError('Expected 12 original R2/R3 deliveries per condition')
    frequency = np.stack([positive[ids].sum(axis=0) for ids in groups])
    denominators = np.stack([native[ids].sum(axis=0) for ids in groups])
    if not np.all(denominators[:, shared] == 12):
        raise ValueError('Incomplete denominator on displayed shared support')
    summary = {
        'comparison': meta['comparison'], 'rounds': meta['rounds'], 'total_original_deliveries': 48,
        "shared_support_voxels": int(shared.sum()),
        "conditions": [],
        "interpretation": "Descriptive spatial agreement of delivered positive whole-brain FWE decisions. Each condition pools six original analyses from each of rounds 2 and 3. Native methods and computation differences are preserved; no new group inference or causal comparison is performed.",
    }
    for k, condition in enumerate(meta["conditions"]):
        ids = groups[k]
        summary["conditions"].append({
            **condition, "label": LABELS[condition["id"]],
            "runs": [meta['records'][i]['run'] for i in ids], 'n': len(ids),
            "positive_in_n_runs_voxel_counts": {str(n): int(np.sum(shared & (frequency[k] == n))) for n in range(13)},
            "native_positive_voxels_per_run": [int(v.sum()) for v in positive[ids]],
            "shared_positive_voxels_per_run": [int((v & shared).sum()) for v in positive[ids]],
            "positive_voxels_outside_shared_support_per_run": [int((v & ~shared).sum()) for v in positive[ids]],
            'rounds': [{ 'round': r, 'runs': [meta['records'][i]['run'] for i in ids if meta['records'][i]['round'] == r],
                        'native_positive_voxels': [int(positive[i].sum()) for i in ids if meta['records'][i]['round'] == r] }
                       for r in meta['rounds']],
        })
    (OUT / "narps-spatial-summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    plt.rcParams.update({
        "font.family": ["Arial", "DejaVu Sans", "sans-serif"], "font.size": 28, "text.color": INK,
        "axes.titlecolor": INK, "xtick.color": INK, "ytick.color": INK,
        "svg.fonttype": "none", "svg.hashsalt": "stamped-narps-spatial",
        "hatch.color": "#8197a5", "hatch.linewidth": .6,
    })
    fig, axes = plt.subplots(4, 3, figsize=(13.5, 9.4))
    fig.subplots_adjust(left=.245, right=.99, top=.88, bottom=.27, wspace=.045, hspace=.14)
    cmap = LinearSegmentedColormap.from_list('agreement', ['#ffe8a3', '#ef9553', '#d65065', '#6d176d'])
    cmap = ListedColormap(['#b5b8ba'] + [cmap(x) for x in np.linspace(0, 1, 12)])
    norm = BoundaryNorm(np.arange(-.5, 13.5), cmap.N)
    anatomy, affine = arrays["anatomy"], arrays["affine"]
    if not np.allclose(affine[:3, :3], np.diag(np.diag(affine[:3, :3]))):
        raise ValueError("This display requires an axis-aligned native image grid")
    extent = [affine[0, 3] - affine[0, 0] / 2,
              affine[0, 3] + affine[0, 0] * (shared.shape[0] - .5),
              affine[1, 3] - affine[1, 1] / 2,
              affine[1, 3] + affine[1, 1] * (shared.shape[1] - .5)]
    labels = ["No supplied\nresearch skills", "Find useful\nskills", "Find research\nskills", "Use STAMPED\nskills"]
    for row in range(4):
        for col, mm in enumerate(meta["display"]["z_cuts_mni_mm"]):
            ax = axes[row, col]
            z = int(round((mm - affine[2, 3]) / affine[2, 2]))
            brain = anatomy[:, :, z].T
            available = shared[:, :, z].T
            ax.imshow(brain, extent=extent, origin="lower", cmap="gray", vmin=0, vmax=.9, interpolation="nearest")
            missing = (~available) & (brain > .04)
            ax.contourf(missing, levels=[.5, 1.5], origin="lower", extent=extent,
                        colors="none", hatches=["////"], alpha=.8)
            values = frequency[row, :, :, z].T
            display = np.ma.masked_where((values == 0) | ~available, values)
            ax.imshow(display, extent=extent, origin="lower", cmap=cmap, norm=norm, interpolation="nearest")
            ax.set_xlim(*meta["display"]["xlim_mni_mm"])
            ax.set_ylim(*meta["display"]["ylim_mni_mm"])
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_facecolor("black")
            for spine in ax.spines.values():
                spine.set_visible(False)
            if row == 0:
                ax.set_title(f"z = {mm:g} mm", fontsize=28, pad=14)
                for x, letter in ((.045, "L"), (.955, "R")):
                    ax.text(x, .06, letter, transform=ax.transAxes, ha="center", va="bottom", color="white", fontsize=28)
    fig.canvas.draw()
    for row, label in enumerate(labels):
        box = axes[row, 0].get_position()
        fig.text(.015, (box.y0 + box.y1) / 2, label, fontsize=28, va="center", weight="bold")
    fig.text(.245, .955, "Posterior axial slices · rounds 2 + 3", fontsize=28)
    fig.text(.245, .22, "Analyses with a positive FWE result", fontsize=28)
    cax = fig.add_axes([.245, .16, .68, .035])
    colorbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax,
                            orientation="horizontal", ticks=[0, 3, 6, 9, 12])
    colorbar.ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    colorbar.ax.tick_params(labelsize=28, length=0, pad=7)
    colorbar.outline.set_visible(False)
    fig.text(.015, .065, "12 analyses per condition · 6 from each round", fontsize=28)
    fig.text(.015, .015, "Gray: 0% · hatched: outside shared coverage", fontsize=28)
    OUT.mkdir(exist_ok=True)
    save(fig, "narps-spatial-agreement")
    (OUT / "narps-spatial-manifest.json").write_text(json.dumps({
        "input_provenance_sha256": digest(DATA / "provenance.json"),
        "script_sha256": digest(Path(__file__)),
        "derived_summary_sha256": digest(OUT / "narps-spatial-summary.json"),
        "figure_sha256": {ext: digest(OUT / f"narps-spatial-agreement.{ext}") for ext in ("svg", "png")},
        "software": {"numpy": np.__version__, "matplotlib": matplotlib.__version__},
    }, indent=2) + "\n")
    print(
        f"Verified 48 original deliveries and {shared.sum():,} shared voxels. "
        "Rendered spatial agreement and saved its numerical summary."
    )


if __name__ == "__main__":
    main()
