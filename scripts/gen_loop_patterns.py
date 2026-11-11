"""Draw Fortran loop-independence patterns beside the corresponding code."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
from matplotlib.colors import to_rgb

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path, default=Path("img"))
args = parser.parse_args()
args.output_dir.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"]})
TEAL, AMBER, INK = "#087E8B", "#B26020", "#12364A"
NI, NJ, NK = 4, 3, 5
CELL_COLORS = ["#B9D1EA", "#B3DCDD", "#D2C9E5", "#F1D29B", "#C6DDB5"]
COLUMNS = ["#B3DCDD", "#D2C9E5", "#F1D29B", "#B9D1EA"]


def project(i, j, k):
    # k explicitly increases downwards, as in the adjacent loop code.
    return 1.0 + .50*i + .23*j, 2.55 + .12*j - .32*k


for kind in ("points", "columns", "slices"):
    fig, ax = plt.subplots(figsize=(4.5, 3.6))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set(xlim=(.20, 4.15), ylim=(.1, 3.25))
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((.28, .18), 3.79, 2.98,
                 boxstyle="round,pad=.02,rounding_size=.10",
                 facecolor="#EDF5F6", edgecolor="none"))

    def face(vertices, i, j, k, side):
        selected = kind != "slices" or j == 0
        if kind == "points":
            color = CELL_COLORS[(i + 2*j + 3*k) % len(CELL_COLORS)]
        elif kind == "columns":
            color = COLUMNS[(i + 2*j) % len(COLUMNS)]
        else:
            color = "#91CDD1"
        rgb = tuple(min(1, v * (1, .84, 1.06)[side]) for v in to_rgb(color))
        ax.add_patch(Polygon([project(*v) for v in vertices], closed=True,
                     facecolor=rgb if selected else "none",
                     edgecolor="#557486" if selected else "#91A6B4",
                     linewidth=.85, alpha=1 if selected else .45, zorder=2))

    # Faint rear outlines show the unfilled depth of the selected slice.
    if kind == "slices":
        for k in range(NK + 1):
            for a, b in [((0, NJ, k), (NI, NJ, k)), ((0, 0, k), (0, NJ, k))]:
                ax.plot(*zip(project(*a), project(*b)), color="#91A6B4", alpha=.22, lw=.85)
        for i in range(NI + 1):
            ax.plot(*zip(project(i, NJ, 0), project(i, NJ, NK)), color="#91A6B4", alpha=.22, lw=.85)

    for k in range(NK):
        for i in range(NI):
            face([(i, 0, k), (i+1, 0, k), (i+1, 0, k+1), (i, 0, k+1)], i, 0, k, 0)
        for j in range(NJ):
            face([(NI, j, k), (NI, j+1, k), (NI, j+1, k+1), (NI, j, k+1)], NI-1, j, k, 1)
    for i in range(NI):
        for j in range(NJ):
            face([(i, j, 0), (i+1, j, 0), (i+1, j+1, 0), (i, j+1, 0)], i, j, 0, 2)

    depth_color = TEAL if kind == "points" else AMBER
    ax.annotate("", (.65, .95), (.65, 2.55),
                arrowprops=dict(arrowstyle="->", color=depth_color, lw=1.8), zorder=4)
    ax.text(.45, 1.75, "k", color=depth_color, fontsize=20, ha="center", va="center")
    ax.annotate("", (3.0, .70), (1.0, .70),
                arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.8), zorder=4)
    ax.text(2.0, .53, "i", color=TEAL, fontsize=20, ha="center", va="center")
    ax.annotate("", (3.87, 1.24), (3.18, .88),
                arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.8), zorder=4)
    ax.text(3.97, 1.30, "j", color=TEAL, fontsize=20, ha="center", va="center")
    if kind != "points":
        for i in range(NI):
            ax.annotate("", project(i+.5, 0, 4.6), project(i+.5, 0, .4),
                        arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.6), zorder=4)
    fig.savefig(args.output_dir / f"loop_{kind}.svg", transparent=True)
    plt.close(fig)
