#!/usr/bin/env python3
"""Plot the original private-array curves from SCA27 figure 2."""

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", type=Path, default=ROOT / "img/viscosity_comparison.svg")
    args = parser.parse_args()
    with (ROOT / "runs/sca27_viscosity.csv").open() as source:
        rows = list(csv.DictReader(source))
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 16})
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_alpha(0)
    fig.subplots_adjust(left=.10, right=.98, bottom=.20, top=.96)
    for platform, label, color in [
        ("CPU node", "CPU · Xeon node", "#1f77b4"),
        ("H200", "NVIDIA · H200", "#ff7f0e"),
        ("MI250X GCD", "AMD · MI250X GCD", "#9467bd"),
    ]:
        points = [r for r in rows if r["platform"] == platform]
        ax.plot([int(r["columns"]) for r in points],
                [float(r["ms"]) for r in points],
                label=label, color=color, marker="o", linewidth=2.5, markersize=6)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ax.xaxis.set_major_locator(FixedLocator([4096, 16384, 65536, 262144, 1048576]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v ** .5)}²"))
    ax.yaxis.set_major_locator(FixedLocator([2, 8, 32, 128, 512]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_ylim(1, 600)
    ax.set_xlabel("Horizontal grid · 100 layers", color="white")
    ax.set_ylabel("Time per step (ms)", color="white")
    ax.tick_params(colors="white")
    ax.grid(axis="y", color="#d4e0e5")
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#c4ced4")
    ax.legend(loc="upper left", frameon=True, facecolor="white",
              edgecolor="#c4ced4", fontsize=12)
    fig.savefig(args.o)
    plt.close(fig)


if __name__ == "__main__":
    main()
