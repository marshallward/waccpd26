"""Show the SCA27 continuity-correction tradeoff, separately from WACCPD timings.

Ordinary builds read the local CSV. --import-data ROOT prints a replacement
CSV extracted from the SCA27-paper-data checkout, without modifying it.
"""
import argparse
import csv
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator


def import_data(root, records):
    writer = csv.DictWriter(sys.stdout, fieldnames=records[0].keys(), lineterminator="\n")
    writer.writeheader()
    for record in records:
        for repeat in range(1, 6):
            path = root / "data/raw" / record["source_directory"] / f'{record["prefix"]}_064_r{repeat}.out'
            clocks = {}
            for line in path.read_text().splitlines():
                for name in ("(Ocean continuity correction)", "Ocean dynamics"):
                    if line.startswith(name):
                        fields = line[len(name):].split()
                        clocks[name] = float(fields[0]), float(fields[3])
            milliseconds = 1000 * clocks["(Ocean continuity correction)"][1]
            steps = clocks["Ocean dynamics"][0] / 2
            record[f"run{repeat}_ms"] = f"{milliseconds / steps:.9f}"
        writer.writerow(record)


def plot(records, output):
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"]})
    layer, column, white = "#91CDD1", "#F0C477", "#FFFFFF"
    fig = plt.figure(figsize=(11.5, 4.9))

    # A structural sketch: row-wise worksharing versus a column per thread.
    for x, form, color in ((.035, "Layer-wise", layer), (.555, "Column-wise", column)):
        ax = fig.add_axes([x, .73, .12, .24])
        ax.set(xlim=(-.1, 4.1), ylim=(-.1, 4.1), aspect="equal")
        ax.axis("off")
        palette = ["#B9D1EA", "#B3DCDD", "#D2C9E5", "#F1D29B"]
        for k in range(4):
            for i in range(4):
                ax.add_patch(Rectangle((i, 3-k), 1, 1,
                             facecolor=palette[k if form == "Layer-wise" else i],
                             edgecolor="#557486", linewidth=.7))
        if form == "Column-wise":
            for i in range(4):
                ax.annotate("", (i+.5, .15), (i+.5, 3.85),
                            arrowprops=dict(arrowstyle="->", color="#B26020", lw=1.5))
        else:
            ax.annotate("", (3.9, 2.5), (.1, 2.5),
                        arrowprops=dict(arrowstyle="<->", color="#12364A", lw=1.5))
        fig.text(x+.14, .94, form, color=color, fontsize=17, weight="bold")
        fig.text(x+.14, .865,
                 "Newton → k → parallel (j,i)" if form == "Layer-wise"
                 else "parallel (j,i) → Newton → k",
                 color=white, fontsize=12)
        fig.text(x+.14, .795,
                 "Workshare each layer" if form == "Layer-wise"
                 else "Each thread owns a column",
                 color=white, fontsize=12)
    fig.text(.50, .89, "→", color=white, fontsize=27, ha="center")

    samples = {(r["platform"], r["form"]):
               min(float(r[f"run{i}_ms"]) for i in range(1, 6)) for r in records}
    titles = {"CPU": "CPU · 104-core Xeon node",
              "NVIDIA": "NVIDIA · H200", "AMD": "AMD · one MI250X GCD"}
    for index, platform in enumerate(("CPU", "NVIDIA", "AMD")):
        ax = fig.add_axes([.065 + index*.322, .20, .27, .43])
        values = [samples[platform, form] for form in ("layer", "column")]
        # A common log scale preserves the large AMD difference without
        # disguising the CPU regression; numeric labels give absolute times.
        ax.bar([0, 1], [v-1 for v in values], bottom=1,
               color=[layer, column], width=.58, edgecolor="#557486", linewidth=.7)
        ax.set_yscale("log")
        ax.set_ylim(1, 2300)
        ax.set_xlim(-.7, 1.7)
        ax.yaxis.set_major_locator(FixedLocator([1, 4, 16, 64, 256, 1024]))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        ax.yaxis.set_minor_locator(NullLocator())
        ax.set_xticks([0, 1], ["Layer-wise", "Column-wise"])
        ax.tick_params(colors=white, labelsize=10)
        ax.set_title(titles[platform], color=white, fontsize=12, pad=10)
        if index == 0:
            ax.set_ylabel("Correction time / step (ms; log scale)", color=white, fontsize=10)
        ax.grid(axis="y", linestyle=":", color=white, alpha=.25)
        for spine in ax.spines.values():
            spine.set_color("#AEC4D2")
            spine.set_alpha(.5)
        ax.set_axisbelow(True)
        for i, value in enumerate(values):
            ax.text(i, value*1.14, f"{value:.0f} ms", color=white, ha="center", fontsize=12)
        ratio = values[1]/values[0] if platform == "CPU" else values[0]/values[1]
        label = f'{ratio:.1f}× {"slower" if platform == "CPU" else "faster"}'
        fig.text(.20 + index*.322, .09, label, color=column if platform == "CPU" else layer,
                 fontsize=16, weight="bold", ha="center")

    fig.text(.5, .015,
             "SCA27 continuity correction · 512×512×100 · fastest of 5 runs · separate experiment",
             color=white, ha="center", fontsize=10)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, transparent=True)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("runs/sca27_continuity_256k.csv"))
    parser.add_argument("-o", "--output", type=Path, default=Path("img/portability_tradeoff.svg"))
    parser.add_argument("--import-data", type=Path, help="SCA27-paper-data root; print CSV instead of plotting")
    args = parser.parse_args()
    with args.data.open(newline="") as data:
        records = list(csv.DictReader(data))
    if args.import_data:
        import_data(args.import_data, records)
    else:
        plot(records, args.output)


if __name__ == "__main__":
    main()
