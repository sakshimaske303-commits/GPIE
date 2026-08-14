import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
import matplotlib.pyplot as plt
import os

NUTS_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"
GADM_PATHS = {
    "UK": "data/earth_observation/boundaries/raw/gadm41_GBR_0.json",
    "NO": "data/earth_observation/boundaries/raw/gadm41_NOR_0.json",
    "CH": "data/earth_observation/boundaries/raw/gadm41_CHE_0.json",
}
DATA_PATH = "data/master_dataset_control.csv"
OUTPUT_PATH = "outputs/plots/ndvi_choropleth_map.png"

EU27_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
}
CONTROL_COUNTRIES_NUTS = {"IS", "AL", "BA", "ME", "MK", "RS"}
CONTROL_COUNTRIES = set(GADM_PATHS.keys()) | CONTROL_COUNTRIES_NUTS


def build_geometry_gdf():
    records = []
    with open(NUTS_PATH, encoding="utf-8") as f:
        nuts_data = json.load(f)
    for feature in nuts_data["features"]:
        nid = feature["properties"].get("NUTS_ID")
        if nid in EU27_COUNTRIES or nid in CONTROL_COUNTRIES_NUTS:
            records.append({"country": nid, "geometry": shape(feature["geometry"])})
    for country_code, path in GADM_PATHS.items():
        with open(path, encoding="utf-8") as f:
            gadm_data = json.load(f)
        geom = shape(gadm_data["features"][0]["geometry"])
        records.append({"country": country_code, "geometry": geom})
    return gpd.GeoDataFrame(records, crs="EPSG:4326")


def compute_avg_ndvi():
    df = pd.read_csv(DATA_PATH)
    avg_ndvi = df.groupby("country")["mean_ndvi"].mean().reset_index()
    avg_ndvi.columns = ["country", "avg_ndvi"]
    return avg_ndvi


def make_map():
    os.makedirs("outputs/plots", exist_ok=True)

    gdf = build_geometry_gdf()
    avg_ndvi = compute_avg_ndvi()

    merged = gdf.merge(avg_ndvi, on="country", how="left")

    bounds = (-25, 34, 35, 72)

    fig, ax = plt.subplots(figsize=(13, 12))

    merged.plot(
        column="avg_ndvi",
        cmap="YlGn",  # yellow-to-green, intuitive for vegetation health
        linewidth=0.6,
        edgecolor="#333333",
        ax=ax,
        legend=True,
        legend_kwds={
            "label": "Mean NDVI (Vegetation Health Index), 2019–2024 Average",
            "orientation": "horizontal",
            "shrink": 0.5,
            "pad": 0.02,
        },
        missing_kwds={"color": "#888888", "edgecolor": "#333333", "hatch": "///", "label": "No data"},
    )

    control_gdf = merged[merged["country"].isin(CONTROL_COUNTRIES)]
    control_gdf.boundary.plot(ax=ax, color="#1a1a1a", linewidth=1.8)

    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_axis_off()

    ax.set_title(
        "Vegetation Health (NDVI): EU-27 vs. 9-Country Control Group\n"
        "Thick borders mark non-EU control-group countries",
        fontsize=12, fontweight="bold", pad=15
    )

    plt.figtext(0.5, 0.01, "Green Policy Intelligence Engine (GPIE) — Source: CGLS NDVI 300m, Sentinel Hub Statistical API",
                ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=220)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_map()