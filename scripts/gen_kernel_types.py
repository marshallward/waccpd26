"""Solver schematics adapted from gtc2026/scripts/kernel_types.py.

Uses the poster geometry and colors, with solid selections in a wireframe grid.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path, default=Path("img"))
args = parser.parse_args()
args.output_dir.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"]})
TEAL, AMBER, INK = "#087E8B", "#B26020", "#FFFFFF"

for kind in ("layer", "column", "slice"):
    fig, ax = plt.subplots(figsize=(3.65, 2.5))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set(xlim=(.35, 4), ylim=(0, 2.5))
    ax.axis("off")

    def project(i, j, k):
        return (1.15 + .48*i + .23*j, .65 + .12*j + .24*k)

    def face(vertices, selected, side, foreground=False, opacity=1):
        shades = (["#F0C477", "#D99539", "#F7D691"] if kind == "column"
                  else ["#91CDD1", "#62B1B8", "#B5E2E4"])
        edge = AMBER if kind == "column" else TEAL
        ax.add_patch(Polygon([project(*v) for v in vertices], closed=True,
                     facecolor=shades[side] if selected else "none",
                     edgecolor=edge if selected else "#AEC4D2", linewidth=.85,
                     alpha=opacity if selected else (.65 if foreground else .30),
                     zorder=2 if selected else (3 if foreground else 1)))

    # Rear grid planes are faint and sit behind the opaque selection.
    for k in range(5):
        for i in range(4):
            face([(i, 3, k), (i+1, 3, k), (i+1, 3, k+1), (i, 3, k+1)],
                 False, 0)
        for j in range(3):
            face([(0, j, k), (0, j+1, k), (0, j+1, k+1), (0, j, k+1)],
                 False, 1)
    for i in range(4):
        for j in range(3):
            face([(i, j, 0), (i+1, j, 0), (i+1, j+1, 0), (i, j+1, 0)],
                 False, 2)

    # Draw the selected cuboid itself, not only colored faces on the outer grid.
    # Interior-facing surfaces are translucent; outer faces remain opaque.
    # This exposes the full horizontal slab / vertical column / i-k slice.
    i0, i1, j0, j1, k0, k1 = {
        "layer": (0, 4, 0, 3, 2, 3),
        "column": (1, 2, 0, 1, 0, 5),
        "slice": (0, 4, 0, 1, 0, 5),
    }[kind]
    for k in range(k0, k1):
        for i in range(i0, i1):
            face([(i, j0, k), (i+1, j0, k),
                  (i+1, j0, k+1), (i, j0, k+1)], True, 0)
        for j in range(j0, j1):
            face([(i1, j, k), (i1, j+1, k),
                  (i1, j+1, k+1), (i1, j, k+1)], True, 1,
                 opacity=.45 if i1 < 4 else 1)
    for i in range(i0, i1):
        for j in range(j0, j1):
            face([(i, j, k1), (i+1, j, k1),
                  (i+1, j+1, k1), (i, j+1, k1)], True, 2,
                 opacity=.45 if k1 < 5 else 1)

    # The transparent front shell overlays the selected volume. Its stronger
    # outlines distinguish it from the faint, occluded rear grid planes.
    for k in range(5):
        for i in range(4):
            face([(i, 0, k), (i+1, 0, k), (i+1, 0, k+1), (i, 0, k+1)],
                 False, 0, foreground=True)
        for j in range(3):
            face([(4, j, k), (4, j+1, k), (4, j+1, k+1), (4, j, k+1)],
                 False, 1, foreground=True)
    for i in range(4):
        for j in range(3):
            face([(i, j, 5), (i+1, j, 5), (i+1, j+1, 5), (i, j+1, 5)],
                 False, 2, foreground=True)

    # k increases down through the ocean. The downward arrow denotes ordered
    # work, not a concurrent vertical dimension in the highlighted region.
    ax.annotate("", (.75, .69), (.75, 1.87),
                 arrowprops=dict(arrowstyle="->", color=INK, lw=1.8))
    ax.text(.55, 1.28, "k", color=INK, fontsize=20, ha="center", va="center")
    if kind == "layer":
        label = "Concurrent i, j · divided into layers"
    elif kind == "column":
        label = "Concurrent columns · full vertical extent"
    else:
        label = "Concurrent i · ordered k in each slice"
    ax.text(2.175, .29, label, color=INK, fontsize=12, ha="center", va="center")
    ax.annotate("", (3.08, .49), (1.15, .49),
                 arrowprops=dict(arrowstyle="->", color=INK, lw=1.4))
    ax.text(3.29, .49, "i", color=INK, fontsize=18, va="center")
    fig.savefig(args.output_dir / f"kernel_{kind}.svg", transparent=True)
    plt.close(fig)
