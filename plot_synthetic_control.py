"""
GPIE — Synthetic control gap plot: EU-27 actual NO2 vs. the augmented
synthetic control (7-country donor composite). Run
synthetic_control.py first.

    python plot_synthetic_control.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

DATA_PATH = "data/synthetic_control_results.csv"
OUTPUT_PATH = "outputs/plots/synthetic_control_gap.png"
TREATMENT_DATE = pd.Timestamp("2021-06-30")


def make_plot():
    os.makedirs("outputs/plots", exist_ok=True)
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])

    fig, axes = plt.subplots(2, 1, figsize=(11, 9), sharex=True, gridspec_kw={"height_ratios": [2, 1]})

    ax = axes[0]
    ax.plot(df["date"], df["eu27_actual"], color="#2c7fb8", linewidth=2, label="EU-27 (actual)")
    ax.plot(df["date"], df["synthetic_control"], color="#d7301f", linewidth=2, linestyle="--",
            label="Synthetic control (7-country donor composite, augmented)")
    ax.axvline(TREATMENT_DATE, color="#1a1a1a", linestyle=":", linewidth=1.5)
    ax.text(TREATMENT_DATE, ax.get_ylim()[1] * 0.95, "  Climate Law\n  effective", fontsize=9, va="top")
    ax.set_ylabel("Mean NO₂ (mol/m²)")
    ax.set_title(
        "Augmented Synthetic Control: EU-27 vs. a 7-Country Weighted Composite\n"
        "Post-treatment average gap = -0.000001 — same near-zero direction as the DiD estimate (-2.22e-06, p=0.101)",
        fontsize=12, fontweight="bold"
    )
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)

    ax2 = axes[1]
    colors = ["#999999" if d <= TREATMENT_DATE else "#2c7fb8" for d in df["date"]]
    ax2.bar(df["date"], df["gap"], width=20, color=colors)
    ax2.axhline(0, color="#1a1a1a", linewidth=1)
    ax2.axvline(TREATMENT_DATE, color="#1a1a1a", linestyle=":", linewidth=1.5)
    ax2.set_ylabel("Gap (actual − synthetic)")
    ax2.set_xlabel("Date")
    ax2.grid(alpha=0.3)

    plt.figtext(0.5, 0.01,
                "Green Policy Intelligence Engine (GPIE) — Augmented SCM, 7-country donor pool "
                "(Norway and Iceland excluded, high-latitude NO2 coverage gaps)",
                ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_plot()
