#!/usr/bin/env python3
"""
Compara timpii de rulare ai unor programe pe matrice de diferite dimensiuni.
Ruleaza: python3 plot_times.py
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.rcParams.update({"font.size": 12})

SIZES = [400, 600, 800, 1000, 1200]
COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"]


def read_times(label):
    times = []
    for n in SIZES:
        while True:
            try:
                val = float(input(f"  [{label}] N={n}: "))
                times.append(val)
                break
            except ValueError:
                print("  Introdu un numar valid.")
    return times


def plot(implementations, title):
    x = np.arange(len(SIZES))
    n = len(implementations)
    width = 0.8 / n

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, (label, times) in enumerate(implementations):
        offset = (i - n / 2 + 0.5) * width
        bars = ax.bar(
            x + offset, times, width,
            label=label,
            color=COLORS[i % len(COLORS)],
            edgecolor="white",
        )
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.3f}s",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=8,
            )

    ax.set_xlabel("Dimensiunea matricei (N×N)", fontsize=13)
    ax.set_ylabel("Timp de rulare (s)", fontsize=13)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s}×{s}" for s in SIZES])
    ax.legend()
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()

    save = input("\nSalvezi graficul? (lasa gol pentru nu, sau scrie numele fisierului, ex: grafic.png): ").strip()
    if save:
        plt.savefig(save, dpi=150, bbox_inches="tight")
        print(f"Salvat in: {save}")
    else:
        plt.show()


def main():
    print("=== Comparare timpi de rulare ===")
    print(f"Dimensiuni matrice: {SIZES}\n")

    title = input("Titlu grafic (Enter pentru implicit): ").strip()
    if not title:
        title = "Comparare timpi de rulare"

    while True:
        try:
            nr = int(input("Cate implementari vrei sa compari? "))
            if nr >= 1:
                break
            print("Trebuie cel putin 1.")
        except ValueError:
            print("Introdu un numar intreg.")

    implementations = []
    for i in range(nr):
        default_label = f"Implementarea {i + 1}"
        label = input(f"\nNume implementarea {i + 1} (Enter pentru '{default_label}'): ").strip()
        if not label:
            label = default_label
        print(f"Introdu timpii (in secunde) pentru '{label}':")
        times = read_times(label)
        implementations.append((label, times))

    plot(implementations, title)


if __name__ == "__main__":
    main()
