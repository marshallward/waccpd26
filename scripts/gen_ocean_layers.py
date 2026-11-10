"""Ocean-layer schematic adapted from gtc2026/scripts/ocean_layers.py."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-o", "--output", type=Path, default=Path("img/ocean_layers.svg"))
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"]})
INK, TEAL, AMBER = "#12364A", "#087E8B", "#B26020"
fig, ax = plt.subplots(figsize=(5.5, 3.3))
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
ax.set(xlim=(0, 11), ylim=(0, 4))
ax.axis("off")
x = np.linspace(.9, 10.45, 400)
phase = (x - .9) / 9.55
interfaces = []
for k in range(6):
    amplitude = .18 if k == 0 else .21
    interfaces.append(3.1 - k*.43 + amplitude*np.sin(phase*2.5*np.pi + k*.45)
                      + (.06 if k else 0)*np.cos(phase*4*np.pi))

# Hatched ground follows the lowest interface.
ax.fill_between(x, np.min(interfaces[-1]) - .28, interfaces[-1],
                facecolor="#F3EFE7", edgecolor="#9C9385", hatch="///",
                linewidth=0)

# Wavy, non-crossing interfaces; five layers, one selected layer.
for k in range(5):
    ax.fill_between(x, interfaces[k+1], interfaces[k],
                    color="#81C9CE" if k == 2 else ["#EAF5F8", "#DFEEF3"][k % 2])
for k, y in enumerate(interfaces):
    ax.plot(x, y, color=TEAL if k in (2, 3) else "#8BAEBB",
            lw=1.5 if k in (2, 3) else 1)

# A vertical column samples every layer; its cells retain the local interfaces.
left, right = 7.15, 7.68
mask = (x >= left) & (x <= right)
for k in range(5):
    ax.fill_between(x[mask], interfaces[k+1][mask], interfaces[k][mask],
                    color="#F0C477", alpha=.85, zorder=4)
    ax.plot(x[mask], interfaces[k][mask], color=AMBER, lw=1.2, zorder=5)
for edge in (left, right):
    ax.plot([edge, edge], [np.interp(edge, x, interfaces[-1]),
                          np.interp(edge, x, interfaces[0])],
            color=AMBER, lw=1.5, zorder=5)
ax.plot(x[mask], interfaces[-1][mask], color=AMBER, lw=1.2, zorder=5)

ax.annotate("Layer", (3.2, np.interp(3.2, x, interfaces[2])-.2),
            (1.8, 3.62), fontsize=20, color=TEAL,
            arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.5), va="center")
ax.annotate("Column", (7.42, np.interp(7.42, x, interfaces[0])), (6.3, 3.62),
            fontsize=20, color=AMBER, va="center",
            arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.5))
# Crop unused canvas while retaining the labels, arrows, and hatched seabed.
crop = Bbox.from_extents(.75, np.min(interfaces[-1]) - .34, 10.6, 3.85)
crop_inches = ax.transData.transform_bbox(crop).transformed(fig.dpi_scale_trans.inverted())
fig.savefig(args.output, transparent=True, bbox_inches=crop_inches)
plt.close(fig)
