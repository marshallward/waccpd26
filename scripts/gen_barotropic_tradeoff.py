"""SCA27 barotropic loop-order comparison, without async/nowait changes.

Normal builds use the local CSV. --import-data ROOT re-extracts its samples
from SCA27-paper-data to stdout, without modifying either repository.
"""
import argparse
import csv
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def import_data(root, records):
    writer = csv.DictWriter(sys.stdout, fieldnames=records[0].keys(), lineterminator="\n")
    writer.writeheader()
    for record in records:
        path = root / "data/raw" / record["source_directory"] / f'{record["prefix"]}_064_r{record["repeat"]}.out'
        clocks = {}
        for line in path.read_text().splitlines():
            for name in ("(Ocean barotropic mode stepping)", "Ocean dynamics"):
                if line.startswith(name):
                    fields = line[len(name):].split()
                    clocks[name] = float(fields[0]), float(fields[3])
        hits = clocks["Ocean dynamics"][0]
        record["dynamics_hits"] = f"{hits:g}"
        record["time_ms"] = f'{1000 * clocks["(Ocean barotropic mode stepping)"][1] / (hits / 2):.9f}'
        writer.writerow(record)


def plot(records, output):
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"]})
    teal, amber, white = "#91CDD1", "#F0C477", "#FFFFFF"
    fig = plt.figure(figsize=(11.5, 4.9))
    palette = ["#B9D1EA", "#B3DCDD", "#D2C9E5", "#F1D29B"]
    for x, column in ((.035, False), (.555, True)):
        ax = fig.add_axes([x, .73, .12, .24])
        ax.set(xlim=(-.1, 4.1), ylim=(-.1, 4.1), aspect="equal")
        ax.axis("off")
        for k in range(4):
            for i in range(4):
                ax.add_patch(Rectangle((i, 3-k), 1, 1,
                             facecolor=palette[i if column else k],
                             edgecolor="#557486", linewidth=.7))
        if column:
            for i in range(4):
                ax.annotate("", (i+.5, .15), (i+.5, 3.85),
                            arrowprops=dict(arrowstyle="->", color="#B26020", lw=1.5))
        else:
            ax.annotate("", (3.9, 2.5), (.1, 2.5),
                        arrowprops=dict(arrowstyle="<->", color="#12364A", lw=1.5))
        fig.text(x+.14, .94, "Column-per-thread" if column else "CPU-friendly order",
                 color=amber if column else teal, fontsize=17, weight="bold")
        fig.text(x+.14, .865, "j–i–k" if column else "j–k–i", color=white, fontsize=16)
        fig.text(x+.14, .795,
                 "parallel (j,i) → serial k" if column else "parallel j → serial k → parallel i",
                 color=white, fontsize=11)
    fig.text(.50, .89, "→", color=white, fontsize=27, ha="center")

    values = {}
    for record in records:
        key = record["platform"], record["form"]
        values[key] = min(values.get(key, float("inf")), float(record["time_ms"]))
    for index, (platform, title) in enumerate((
            ("CPU", "CPU · 104-core Xeon node"), ("AMD", "AMD · one MI250X GCD"))):
        ax = fig.add_axes([.085 + index*.49, .23, .35, .38])
        original, reordered = values[platform, "jki"], values[platform, "jik"]
        ratio = reordered / original
        ax.bar([0, 1], [1, ratio], color=[teal, amber], width=.58,
               edgecolor="#557486", linewidth=.7)
        ax.set(ylim=(0, 1.8), xlim=(-.65, 1.65))
        ax.set_xticks([0, 1], ["j–k–i", "j–i–k"])
        ax.set_yticks([0, .5, 1, 1.5], ["0", "0.5×", "1×", "1.5×"])
        ax.tick_params(colors=white, labelsize=11)
        ax.set_title(title, color=white, fontsize=13, pad=10)
        if index == 0:
            ax.set_ylabel("Time relative to own j–k–i case", color=white, fontsize=10)
        ax.axhline(1, color=white, linestyle="--", linewidth=.8, alpha=.5)
        ax.grid(axis="y", linestyle=":", color=white, alpha=.25)
        ax.set_axisbelow(True)
        for spine in ax.spines.values():
            spine.set_color("#AEC4D2")
            spine.set_alpha(.5)
        for i, (height, ms) in enumerate(((1, original), (ratio, reordered))):
            ax.text(i, height+.06, f"{ms:.1f} ms", color=white, fontsize=13, ha="center")
        label = f"{(ratio-1)*100:.0f}% slower" if platform == "CPU" else f"{1/ratio:.1f}× faster"
        fig.text(.26+index*.49, .12, label, color=amber if platform == "CPU" else teal,
                 fontsize=18, weight="bold", ha="center")

    fig.text(.5, .055, "SCA27 barotropic · 512×512×100 · loop-order change only; no async/nowait",
             color=white, ha="center", fontsize=10)
    fig.text(.5, .015, "CPU: fastest of 5 · AMD: one 20-step run per form · historical compiler-specific results",
             color=white, ha="center", fontsize=9)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, transparent=True)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("runs/sca27_barotropic_256k.csv"))
    parser.add_argument("-o", "--output", type=Path, default=Path("img/barotropic_tradeoff.svg"))
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
