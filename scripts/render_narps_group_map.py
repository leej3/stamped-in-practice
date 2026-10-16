#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Regenerate poster SVG/PNG figures from the checked-in, hashed NARPS snapshot.

No remote data or running worker state is used. See map-inputs/example/provenance.json for
original source revisions, input-map URLs and analysis methods. The figures
summarize saved worker outputs; this is not a new participant-level analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "experiments/narps-poster/map-inputs/example"
OUT = ROOT / "experiments/narps-poster/figures"
INK = "#17344c"
TEAL = "#007e87"
ORANGE = "#cf731d"
PALE = "#e8eef1"


def save(fig, stem):
    try:
        for extension in ("svg", "png"):
            with tempfile.NamedTemporaryFile(dir=OUT, suffix=f".{extension}", delete=False) as handle:
                temporary = Path(handle.name)
            try:
                fig.savefig(
                    temporary, format=extension, dpi=150, facecolor="white",
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


def verify_snapshot(meta):
    for relative, source in meta["sources"].items():
        digest = hashlib.sha256((DATA / relative).read_bytes()).hexdigest()
        if digest != source["sha256"]:
            raise ValueError(f"Snapshot hash mismatch: {relative}")
    if meta["representative_map_run"] != "narps-r1-09":
        raise ValueError("This illustrative display is bound to run09")


def maps(meta):
    files = {
        "t": "one_sample_t.nii.gz", "coverage": "common_brain_mask.nii.gz",
        "fwe": "max_t_fwe_p05_mask.nii.gz", "roi": "vmPFC_AAL_medial_orbitofrontal_mask.nii.gz",
        "anatomy": "anatomical-context.nii.gz",
    }
    images = {key: nib.load(DATA / "maps" / name) for key, name in files.items()}
    ref = images["t"]
    for img in images.values():
        if img.shape != ref.shape or not np.allclose(img.affine, ref.affine):
            raise ValueError("Snapshot map geometry mismatch")
    if not np.allclose(ref.affine[:3, :3], np.diag(np.diag(ref.affine[:3, :3]))):
        raise ValueError("This display expects an axis-aligned map grid")
    data = {key: img.get_fdata() for key, img in images.items()}
    mask = data["coverage"].astype(bool)
    sig = data["fwe"].astype(bool)
    roi = data["roi"].astype(bool)
    if mask.sum() != 198029 or sig.sum() != 24 or (sig & roi).sum() != 0:
        raise ValueError("Saved map counts differ from run09 summary")
    if np.any(sig & ~mask) or np.any(roi & ~mask):
        raise ValueError("Corrected result or ROI outside analysis coverage")

    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad((0, 0, 0, 0))
    cmap.set_under(cmap(0))
    cmap.set_over(cmap(1))
    norm = Normalize(-6, 6, clip=True)
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 6.4))
    fig.subplots_adjust(left=.012, right=.985, top=.80, bottom=.30, wspace=.045)
    cuts = meta["map_display"]["slice_centers_mni_mm"]
    titles = ["Sagittal", "Coronal", "Axial"]
    for dim, (ax, mm) in enumerate(zip(axes, cuts)):
        index = int(round((mm - ref.affine[dim, 3]) / ref.affine[dim, dim]))
        actual_mm = ref.affine[dim, dim] * index + ref.affine[dim, 3]
        remaining = [i for i in range(3) if i != dim]
        xdim, ydim = remaining
        extent = [
            ref.affine[xdim, 3] - ref.affine[xdim, xdim] / 2,
            ref.affine[xdim, 3] + ref.affine[xdim, xdim] * (ref.shape[xdim] - .5),
            ref.affine[ydim, 3] - ref.affine[ydim, ydim] / 2,
            ref.affine[ydim, 3] + ref.affine[ydim, ydim] * (ref.shape[ydim] - .5),
        ]
        take = lambda a: np.take(a, index, axis=dim).T
        background = take(data["anatomy"])
        ax.imshow(background, origin="lower", extent=extent, cmap="gray", vmin=0, vmax=.9, interpolation="nearest")
        values = np.ma.masked_where(~take(mask), take(data["t"]))
        ax.imshow(values, origin="lower", extent=extent, cmap=cmap, norm=norm, alpha=.82, interpolation="nearest")
        for contour, color, linewidth in ((roi, "#ffd54a", 2.5), (sig, "#4effe0", 2.8)):
            plane = take(contour)
            if plane.any():
                ax.contour(plane, levels=[.5], origin="lower", extent=extent,
                           colors=[color], linewidths=linewidth)
        ax.set_facecolor("black")
        if dim == 0:
            ax.set_xlim(-114, 84)
            ax.set_ylim(-63, 89)
            corners = ("P", "A")
        else:
            ax.set_xlim(-86, 86)
            ax.set_ylim((-63, 89) if dim == 1 else (-114, 84))
            corners = ("L", "R")
        ax.set_title(f"{titles[dim]}\n{'xyz'[dim]} = {actual_mm:g} mm", fontsize=24, pad=13)
        for x, letter in zip((.035, .965), corners):
            ax.text(x, .055, letter, transform=ax.transAxes, ha="center", color="white", fontsize=24, weight="bold")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    cax = fig.add_axes([.055, .135, .31, .032])
    colorbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation="horizontal", ticks=[-6, 0, 6])
    colorbar.ax.set_xticklabels(["≤−6", "0", "≥6"])
    colorbar.ax.tick_params(labelsize=24, length=0, pad=7)
    colorbar.ax.set_title("Unthresholded group t", fontsize=24, pad=13, loc="left")
    fig.legend(handles=[
        Line2D([], [], color="#d7a700", linewidth=4, label="vmPFC region"),
        Line2D([], [], color="#00a88e", linewidth=4, label="Positive FWE p ≤ .05"),
    ], loc="lower right", bbox_to_anchor=(.985, .07), frameon=False, fontsize=24)
    fig.text(.055, .018, "Gray anatomy: outside common coverage", fontsize=24, color=INK)
    save(fig, "narps-group-map")


def main():
    global DATA, OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=DATA)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    DATA, OUT = args.inputs.resolve(), args.output.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": ["Arial", "DejaVu Sans", "sans-serif"], "font.size": 24, "text.color": INK,
        "axes.labelcolor": INK, "axes.titlecolor": INK,
        "xtick.color": INK, "ytick.color": INK,
        "svg.fonttype": "none", "svg.hashsalt": "stamped-narps-poster-2026-10-15",
    })
    meta = json.loads((DATA / "provenance.json").read_text())
    verify_snapshot(meta)
    OUT.mkdir(exist_ok=True)
    maps(meta)
    outputs = [OUT / "narps-group-map.svg", OUT / "narps-group-map.png"]
    (OUT / "narps-group-map-manifest.json").write_text(json.dumps({
        "input_provenance_sha256": hashlib.sha256((DATA / "provenance.json").read_bytes()).hexdigest(),
        "render_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "software": {"numpy": np.__version__, "matplotlib": matplotlib.__version__, "nibabel": nib.__version__},
        "output_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs},
    }, indent=2) + "\n")
    print("Verified snapshot hashes and map counts; rendered the illustrative group map as SVG and PNG.")


if __name__ == "__main__":
    main()
