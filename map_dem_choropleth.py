import json
import geopandas as gpd
from shapely.geometry import shape
import matplotlib.pyplot as plt
import os

NUTS_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"
DEM_PATH = "data/earth_observation/dem/final/dem_stats_by_country.json"
OUTPUT_PATH = "outputs/plots/dem_elevation_map.png"

EU27_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
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


def load_dem_stats():
    import pandas as pd
    with open(DEM_PATH) as f:
        data = json.load(f)
    return pd.DataFrame(data).rename(columns={"NUTS_ID": "country"})


def make_map():
    os.makedirs("outputs/plots", exist_ok=True)

    gdf = build_geometry_gdf()
    dem_df = load_dem_stats()

    merged = gdf.merge(dem_df, on="country", how="left")

    bounds = (-25, 34, 35, 72)

    fig, ax = plt.subplots(figsize=(13, 12))

    merged.plot(
        column="elevation_mean_m",
        cmap="terrain",
        linewidth=0.6,
        edgecolor="#333333",
        ax=ax,
        legend=True,
        legend_kwds={
            "label": "Mean Elevation (meters)",
            "orientation": "horizontal",
            "shrink": 0.5,
            "pad": 0.02,
        },
        missing_kwds={"color": "#888888", "edgecolor": "#333333", "hatch": "///", "label": "No data"},
    )

    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_axis_off()

    ax.set_title(
        "Mean Elevation by Country (EU-27)\n"
        "Environmental/topographic context — Copernicus DEM GLO-30",
        fontsize=12, fontweight="bold", pad=15
    )

    plt.figtext(0.5, 0.01, "Green Policy Intelligence Engine (GPIE) — Source: Copernicus DEM GLO-30",
                ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=220)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_map()