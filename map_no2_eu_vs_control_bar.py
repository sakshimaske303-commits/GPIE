import pandas as pd
import matplotlib.pyplot as plt
import os

# NO2 companion to the NDVI EU-vs-control bar chart, same two-group DiD design.
DATA_PATH = "data/master_dataset_control.csv"
OUTPUT_PATH = "outputs/plots/eu_vs_control_bar_chart.png"


def make_chart():
    os.makedirs("outputs/plots", exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    df["period"] = df["year"].apply(lambda y: "Pre-2021\n(2019-2020)" if y <= 2020 else "Post-2021\n(2021-2024)")
    df["group_label"] = df["treatment_group"].map({1: "EU-27 (Treatment)", 0: "Control Group"})

    grouped = df.groupby(["group_label", "period"])["mean_no2"].mean().reset_index()

    periods = ["Pre-2021\n(2019-2020)", "Post-2021\n(2021-2024)"]
    groups = ["EU-27 (Treatment)", "Control Group"]
    colors = {"EU-27 (Treatment)": "#2c7fb8", "Control Group": "#e34a33"}

    fig, ax = plt.subplots(figsize=(9, 6.5))

    x = range(len(periods))
    width = 0.35

    for i, group in enumerate(groups):
        vals = [
            grouped[(grouped["group_label"] == group) & (grouped["period"] == p)]["mean_no2"].values[0]
            for p in periods
        ]
        offset = (i - 0.5) * width
        bars = ax.bar([xi + offset for xi in x], vals, width, label=group, color=colors[group], edgecolor="#1a1a1a")
        for xi, v in zip(x, vals):
            ax.text(xi + offset, v + v * 0.01, f"{v:.2e}", ha="center", fontsize=9)

    ax.set_xticks(list(x))
    ax.set_xticklabels(periods)
    ax.set_ylabel("Mean NO2 (mol/m²)")
    ax.set_title(
        "NO2: EU-27 vs. 9-Country Control Group, Before vs. After the European Climate Law\n"
        "Two-group DiD model: coefficient = -2.22e-06, p = 0.101 (cluster-robust) -\n"
        "no significant pooled effect, though a baseline-pollution split finds one in higher-baseline countries",
        fontsize=11, fontweight="bold"
    )
    ax.legend(loc="lower right")
    ax.grid(axis="y", alpha=0.3)

    plt.figtext(0.5, 0.01, "Green Policy Intelligence Engine (GPIE) - Source: Sentinel-5P TROPOMI, Sentinel Hub Statistical API",
                ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_chart()
