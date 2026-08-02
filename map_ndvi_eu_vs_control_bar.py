import pandas as pd
import matplotlib.pyplot as plt
import os

# NDVI equivalent of the existing NO2 EU-vs-control bar chart. Added after
# the corrected two-group NDVI DiD model (causal_inference_ndvi.py) found a
# statistically significant relative decline - this chart gives that finding
# a visual companion, the same way the NO2 result already has one.
DATA_PATH = "data/master_dataset_control.csv"
OUTPUT_PATH = "outputs/plots/ndvi_eu_vs_control_bar_chart.png"


def make_chart():
    os.makedirs("outputs/plots", exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    df["period"] = df["year"].apply(lambda y: "Pre-2021\n(2019-2020)" if y <= 2020 else "Post-2021\n(2021-2024)")
    df["group_label"] = df["treatment_group"].map({1: "EU-27 (Treatment)", 0: "Control Group"})

    grouped = df.groupby(["group_label", "period"])["mean_ndvi"].mean().reset_index()

    periods = ["Pre-2021\n(2019-2020)", "Post-2021\n(2021-2024)"]
    groups = ["EU-27 (Treatment)", "Control Group"]
    colors = {"EU-27 (Treatment)": "#2c7fb8", "Control Group": "#e34a33"}

    fig, ax = plt.subplots(figsize=(9, 6.5))

    x = range(len(periods))
    width = 0.35

    for i, group in enumerate(groups):
        vals = [
            grouped[(grouped["group_label"] == group) & (grouped["period"] == p)]["mean_ndvi"].values[0]
            for p in periods
        ]
        offset = (i - 0.5) * width
        bars = ax.bar([xi + offset for xi in x], vals, width, label=group, color=colors[group], edgecolor="#1a1a1a")
        for xi, v in zip(x, vals):
            ax.text(xi + offset, v + 0.003, f"{v:.3f}", ha="center", fontsize=9)

    ax.set_xticks(list(x))
    ax.set_xticklabels(periods)
    ax.set_ylabel("Mean NDVI (Vegetation Health Index)")
    ax.set_title(
        "NDVI: EU-27 vs. Control Group, Before vs. After the European Climate Law\n"
        "Corrected two-group DiD model: coefficient = -0.021, p = 0.012 (cluster-robust) -\n"
        "a statistically significant relative decline, not visible in NO2's equivalent comparison",
        fontsize=11, fontweight="bold"
    )
    ax.legend(loc="lower right")
    ax.grid(axis="y", alpha=0.3)

    plt.figtext(0.5, 0.01, "Green Policy Intelligence Engine (GPIE) - Source: CGLS NDVI 300m, Sentinel Hub Statistical API",
                ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_chart()
