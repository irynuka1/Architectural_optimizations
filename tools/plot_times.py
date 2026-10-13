#!/usr/bin/env python3
"""
Plots running times per matrix size from one or more CSV files (solver,N,seconds).

Usage:
    python3 tools/plot_times.py results/zen2.csv -o results/zen2.png --title "Zen 2"
    python3 tools/plot_times.py results/haswell.csv results/zen2.csv -o results/compare.png
"""

import argparse
import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860"]


def load(paths):
    """Returns {series_label: {N: seconds}}; the label is prefixed with the file name when several files are given."""
    series = defaultdict(dict)
    for path in paths:
        prefix = os.path.splitext(os.path.basename(path))[0]
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                label = row["solver"] if len(paths) == 1 else f"{prefix}: {row['solver']}"
                series[label][int(row["N"])] = float(row["seconds"])
    return series


def plot(series, title, output):
    sizes = sorted({n for times in series.values() for n in times})
    x = np.arange(len(sizes))
    width = 0.8 / len(series)

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (label, times) in enumerate(series.items()):
        values = [times.get(n, 0.0) for n in sizes]
        offset = (i - len(series) / 2 + 0.5) * width
        bars = ax.bar(x + offset, values, width, label=label,
                      color=COLORS[i % len(COLORS)], edgecolor="white")
        for bar in bars:
            ax.annotate(f"{bar.get_height():.2f}",
                        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=7)

    ax.set_xlabel("Matrix size (N×N)")
    ax.set_ylabel("Running time (s)")
    ax.set_title(title, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{n}×{n}" for n in sizes])
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    print(f"Saved to {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv", nargs="+", help="CSV files with columns solver,N,seconds")
    parser.add_argument("-o", "--output", default="times.png")
    parser.add_argument("--title", default="Running time comparison")
    args = parser.parse_args()
    plot(load(args.csv), args.title, args.output)


if __name__ == "__main__":
    main()
