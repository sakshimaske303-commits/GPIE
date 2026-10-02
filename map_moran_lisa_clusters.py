"""I map the LISA clusters (Local Moran's I) of average NO2 level."""

import json
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

DATA_PATH = "data/country_no2_for_moran.geojson"
OUTPUT_PATH = "outputs/plots/moran_lisa_cluster_map.png"

CLUSTER_COLORS = {
    "High-High": "#d7301f",
    "Low-Low": "#2c7fb8",
    "Low-High": "#a6cee3",
    "High-Low": "#fdbf6f",
    "Not significant": "#dddddd",
}


def make_map():
    os.makedirs("outputs/plots", exist_ok=True)
    gdf = gpd.read_file(DATA_PATH)
    with open("data/spatial_autocorrelation_summary.json") as f:
        summ = json.load(f)
    lvl = summ["level_full_period"]
    res = summ["did_residuals_monthly"]

    bounds = (-25, 34, 35, 72)
    fig, ax = plt.subplots(figsize=(13, 12))

    for cluster, color in CLUSTER_COLORS.items():
        subset = gdf[gdf["cluster"] == cluster]
        if len(subset):
            subset.plot(ax=ax, color=color, edgecolor="#333333", linewidth=0.6)

    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_axis_off()

    handles = [mpatches.Patch(color=c, label=k) for k, c in CLUSTER_COLORS.items()]
    ax.legend(handles=handles, loc="lower left", title="LISA cluster (p<0.05)", fontsize=9, title_fontsize=10)

    ax.set_title(
        "Local Moran's I: Where NO₂ Levels Cluster Spatially (Full-Period Average, 36 Countries)\n"
        f"Global Moran's I on average NO₂ level = {lvl['I']:.3f} (p = {lvl['p_sim']:.3f});\n"
        f"DiD residuals, month by month: median I = {res['median_I']:.3f}, significantly positive in "
        f"{res['n_months_significant_positive_p05']} of {res['n_months']} months",
        fontsize=12, fontweight="bold", pad=15
    )

    plt.figtext(0.5, 0.01, "Green Policy Intelligence Engine (GPIE) — Local Moran's I (esda), KNN-4 spatial weights on country centroids",
                ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=220)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_map()
