"""Compare CPU and GPU work regions in the loop-pattern diagram style."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import FancyBboxPatch, Polygon

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-o", "--output", type=Path, default=Path("img/block_regions.svg"))
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"]})
INK = "#12364A"
NI, NJ, NK = 6, 4, 4


def project(i, j, k):
    return .65 + .43*i + .22*j, 2.65 + .12*j - .36*k


fig, axes = plt.subplots(1, 2, figsize=(10, 3.7))
fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=.10)
for ax, kind in zip(axes, ("cpu", "gpu")):
    ax.set(xlim=(.1, 4.5), ylim=(.05, 3.55))
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((.18, .13), 4.24, 3.30,
                 boxstyle="round,pad=.02,rounding_size=.10",
                 facecolor="#EDF5F6", edgecolor="none"))

    def face(vertices, k, side):
        selected = kind == "gpu" or k == 1
        rgb = tuple(min(1, v * (1, .84, 1.06)[side])
                    for v in to_rgb("#91CDD1"))
        ax.add_patch(Polygon([project(*v) for v in vertices], closed=True,
                     facecolor=rgb if selected else "none",
                     edgecolor="#557486" if selected else "#91A6B4",
                     linewidth=.85, alpha=1 if selected else .40))

    for k in range(NK):
        for i in range(NI):
            face([(i, 0, k), (i+1, 0, k), (i+1, 0, k+1), (i, 0, k+1)], k, 0)
        for j in range(NJ):
            face([(NI, j, k), (NI, j+1, k), (NI, j+1, k+1), (NI, j, k+1)], k, 1)
    for i in range(NI):
        for j in range(NJ):
            face([(i, j, 0), (i+1, j, 0), (i+1, j+1, 0), (i, j+1, 0)], 0, 2)

    ax.text(2.3, 3.24, "CPU" if kind == "cpu" else "GPU",
            color=INK, fontsize=19, weight="bold", ha="center")
    ax.text(2.3, .88, "Cache-friendly parts" if kind == "cpu" else "Larger kernel work region",
            color=INK, fontsize=16, ha="center")
    ax.text(2.3, .50, "Layer-sized region" if kind == "cpu" else "Compiler maps work to threads",
            color=INK, fontsize=12, ha="center")

fig.savefig(args.output, transparent=True)
plt.close(fig)
