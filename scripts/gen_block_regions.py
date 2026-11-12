"""Compare CPU and GPU work regions in the loop-pattern diagram style."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-o", "--output", type=Path, default=Path("img/block_regions.svg"))
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"]})
INK = "#FFFFFF"
NI, NJ, NK = 4, 3, 5


def project(i, j, k):
    return .85 + .60*i + .2875*j, 2.70 + .15*j - .30*k


fig, axes = plt.subplots(1, 2, figsize=(10, 3.7))
fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=.10)
for ax, kind in zip(axes, ("cpu", "gpu")):
    ax.set(xlim=(.1, 4.5), ylim=(.05, 3.55))
    ax.axis("off")

    def face(vertices, selected, side, foreground=False):
        shades = ["#91CDD1", "#62B1B8", "#B5E2E4"]
        ax.add_patch(Polygon([project(*v) for v in vertices], closed=True,
                     facecolor=shades[side] if selected else "none",
                     edgecolor="#087E8B" if selected else "#AEC4D2",
                     linewidth=.85,
                     alpha=(.45 if kind == "cpu" and side == 2 else 1) if selected
                           else (.65 if foreground else .30),
                     zorder=2 if selected else (3 if foreground else 1)))

    if kind == "cpu":
        # Rear shell, then a complete interior slab, then the transparent front.
        for k in range(NK):
            for i in range(NI):
                face([(i, NJ, k), (i+1, NJ, k), (i+1, NJ, k+1), (i, NJ, k+1)], False, 0)
            for j in range(NJ):
                face([(0, j, k), (0, j+1, k), (0, j+1, k+1), (0, j, k+1)], False, 1)
        for i in range(NI):
            for j in range(NJ):
                face([(i, j, NK), (i+1, j, NK), (i+1, j+1, NK), (i, j+1, NK)], False, 2)

        for i in range(NI):
            face([(i, 0, 1), (i+1, 0, 1), (i+1, 0, 2), (i, 0, 2)], True, 0)
        for j in range(NJ):
            face([(NI, j, 1), (NI, j+1, 1), (NI, j+1, 2), (NI, j, 2)], True, 1)
        for i in range(NI):
            for j in range(NJ):
                face([(i, j, 1), (i+1, j, 1), (i+1, j+1, 1), (i, j+1, 1)], True, 2)

    for k in range(NK):
        for i in range(NI):
            face([(i, 0, k), (i+1, 0, k), (i+1, 0, k+1), (i, 0, k+1)], kind == "gpu", 0, foreground=True)
        for j in range(NJ):
            face([(NI, j, k), (NI, j+1, k), (NI, j+1, k+1), (NI, j, k+1)], kind == "gpu", 1, foreground=True)
    for i in range(NI):
        for j in range(NJ):
            face([(i, j, 0), (i+1, j, 0), (i+1, j+1, 0), (i, j+1, 0)], kind == "gpu", 2, foreground=True)

    ax.text(2.3, 3.24, "CPU" if kind == "cpu" else "GPU",
            color=INK, fontsize=19, weight="bold", ha="center")
    ax.text(2.3, .88, "Cache-friendly parts" if kind == "cpu" else "Larger kernel work region",
            color=INK, fontsize=16, ha="center")
    ax.text(2.3, .50, "Layer-sized region" if kind == "cpu" else "Compiler maps work to threads",
            color=INK, fontsize=12, ha="center")

fig.savefig(args.output, transparent=True)
plt.close(fig)
