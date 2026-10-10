import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# NO2 version of my NDVI EU-vs-control bar chart, same two-group DiD design.
DATA_PATH = "data/master_dataset_control.csv"
OUTPUT_PATH = "outputs/plots/eu_vs_control_bar_chart.png"


def make_chart():
    os.makedirs("outputs/plots", exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    # Same split as my DiD model: July 2021 is the first post month
    # (Climate Law adopted 30 June 2021, in force 29 July 2021).
    is_pre = (df["year"] * 100 + df["month"]) <= 202106
    df["period"] = is_pre.map({True: "Pre-treatment\n(Jan 2019 - Jun 2021)", False: "Post-treatment\n(Jul 2021 - Dec 2024)"})
    df["group_label"] = df["treatment_group"].map({1: "EU-27 (Treatment)", 0: "Control Group"})

    grouped = df.groupby(["group_label", "period"])["mean_no2"].mean().reset_index()

    periods = ["Pre-treatment\n(Jan 2019 - Jun 2021)", "Post-treatment\n(Jul 2021 - Dec 2024)"]
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
    with open("data/robustness_checks.json") as f:
        did = json.load(f)["treatment_date_sensitivity"]["true"]
    ax.set_title(
        "NO2: EU-27 vs. 9-Country Control Group, Before vs. After the European Climate Law\n"
        f"Raw group means (descriptive). Two-group DiD estimate: {did['coefficient']:.2e}, "
        f"p = {did['p_value']:.3f} (cluster-robust)",
        fontsize=11, fontweight="bold"
    )
    ax.legend(loc="lower right")
    ax.grid(axis="y", alpha=0.3)

    plt.figtext(0.5, 0.01, "Green Policy Intelligence Engine (GPIE) - Source: Sentinel-5P TROPOMI, Sentinel Hub Process API",
                ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_chart()
