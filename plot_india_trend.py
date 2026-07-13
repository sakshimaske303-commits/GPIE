import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os

INPUT_PATH = "data/global_transferability_test/india_no2_test.json"
OUTPUT_PATH = "outputs/plots/india_transferability_trend.png"


def flatten_india_data():
    with open(INPUT_PATH) as f:
        raw_data = json.load(f)

    flat_records = []
    for year_record in raw_data:
        year = year_record["year"]
        monthly_entries = year_record["data"]["data"]

        for entry in monthly_entries:
            start_date = entry["interval"]["from"]
            month = datetime.fromisoformat(start_date.replace("Z", "+00:00")).month
            stats = entry["outputs"]["no2"]["bands"]["B0"]["stats"]

            flat_records.append({
                "year": year,
                "month": month,
                "mean_no2": stats.get("mean"),
            })

    return pd.DataFrame(flat_records)


def make_plot():
    os.makedirs("outputs/plots", exist_ok=True)

    df = flatten_india_data()
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))
    df = df.sort_values("time")

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df["time"], df["mean_no2"], marker="o", color="#e34a33", linewidth=2, markersize=5)

    ax.set_title(
        "GPIE Transferability Test: India NO₂ Trend (2019–2024)\n"
        "Standalone proof-of-concept — same acquisition pipeline built for the EU-27 study",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Mean Tropospheric NO₂ (mol/m²)")
    ax.grid(alpha=0.3)

    plt.figtext(0.5, 0.01, "Green Policy Intelligence Engine (GPIE) — Source: Sentinel-5P TROPOMI, Sentinel Hub Statistical API",
                ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_plot()