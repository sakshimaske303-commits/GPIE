import json
import geopandas as gpd
from shapely.geometry import shape
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import os

NUTS_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"
LANDCOVER_PATH = "data/earth_observation/land_cover/final/landcover_stats_by_country.json"
OUTPUT_PATH = "outputs/plots/land_cover_dominant_class_map.png"

EU27_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
}

# Standard, distinguishable colors per land cover class
CLASS_COLORS = {
    "Tree cover": "#1a7a1a",
    "Shrubland": "#a8a832",
    "Grassland": "#90ee90",
    "Cropland": "#e8c547",
    "Built-up": "#c0392b",
    "Bare/sparse vegetation": "#c9b896",
    "Snow and ice": "#e0f7fa",
    "Permanent water bodies": "#1f6fb2",
    "Herbaceous wetland": "#6b8e6b",
    "Mangroves": "#3d5c3d",
    "Moss and lichen": "#8a9a5b",
}


def build_geometry_gdf():
    records = []
    with open(NUTS_PATH, encoding="utf-8") as f:
        nuts_data = json.load(f)
    for feature in nuts_data["features"]:
        nid = feature["properties"].get("NUTS_ID")
        if nid in EU27_COUNTRIES:
            records.append({"country": nid, "geometry": shape(feature["geometry"])})
    return gpd.GeoDataFrame(records, crs="EPSG:4326")


def load_dominant_class():
    with open(LANDCOVER_PATH) as f:
        data = json.load(f)

    results = []
    for record in data:
        country = record["NUTS_ID"]
        classes = record["land_cover_percent"]
        dominant = max(classes, key=classes.get)
        results.append({"country": country, "dominant_class": dominant, "dominant_pct": classes[dominant]})

    return results


def make_map():
    os.makedirs("outputs/plots", exist_ok=True)

    gdf = build_geometry_gdf()
    dominant_data = load_dominant_class()

    dominant_df = pd.DataFrame(dominant_data)
    merged = gdf.merge(dominant_df, on="country", how="left")

    merged["color"] = merged["dominant_class"].map(CLASS_COLORS)
    merged["color"] = merged["color"].fillna("#cccccc")  # grey fallback for any unmatched/missing entry

    bounds = (-25, 34, 35, 72)

    fig, ax = plt.subplots(figsize=(13, 12))

    merged.plot(ax=ax, color=merged["color"], edgecolor="#333333", linewidth=0.6)

    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_axis_off()

    classes_present = sorted(merged["dominant_class"].dropna().unique())
    legend_patches = [mpatches.Patch(color=CLASS_COLORS[c], label=c) for c in classes_present]
    ax.legend(handles=legend_patches, loc="lower left", fontsize=10, frameon=True,
              framealpha=0.95, title="Dominant Land Cover Class")

    ax.set_title(
        "Dominant Land Cover Class by Country (EU-27)\n"
        "Each country shaded by its single largest ESA WorldCover class (2021)",
        fontsize=13, fontweight="bold", pad=15
    )

    plt.figtext(0.5, 0.02, "Green Policy Intelligence Engine (GPIE) — Source: ESA WorldCover 10m v200",
                ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_map()