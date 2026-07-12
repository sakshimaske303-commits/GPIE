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
OUTPUT_PATH = "outputs/plots/ndvi_before_after_map.png"

EU27_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
}
CONTROL_COUNTRIES = {"UK", "NO", "CH"}


def build_geometry_gdf():
    records = []
    with open(NUTS_PATH, encoding="utf-8") as f:
        nuts_data = json.load(f)
    for feature in nuts_data["features"]:
        nid = feature["properties"].get("NUTS_ID")
        if nid in EU27_COUNTRIES:
            records.append({"country": nid, "geometry": shape(feature["geometry"])})
    for country_code, path in GADM_PATHS.items():
        with open(path, encoding="utf-8") as f:
            gadm_data = json.load(f)
        geom = shape(gadm_data["features"][0]["geometry"])
        records.append({"country": country_code, "geometry": geom})
    return gpd.GeoDataFrame(records, crs="EPSG:4326")


def compute_yearly_avg_ndvi():
    df = pd.read_csv(DATA_PATH)
    yearly = df.groupby(["country", "year"])["mean_ndvi"].mean().reset_index()
    return yearly


def make_map():
    os.makedirs("outputs/plots", exist_ok=True)

    gdf = build_geometry_gdf()
    yearly = compute_yearly_avg_ndvi()

    ndvi_2019 = yearly[yearly["year"] == 2019][["country", "mean_ndvi"]].rename(columns={"mean_ndvi": "ndvi_2019"})
    ndvi_2024 = yearly[yearly["year"] == 2024][["country", "mean_ndvi"]].rename(columns={"mean_ndvi": "ndvi_2024"})

    merged = gdf.merge(ndvi_2019, on="country", how="left").merge(ndvi_2024, on="country", how="left")

    # Shared color scale across both panels for direct visual comparability
    vmin = min(merged["ndvi_2019"].min(), merged["ndvi_2024"].min())
    vmax = max(merged["ndvi_2019"].max(), merged["ndvi_2024"].max())

    bounds = (-25, 34, 35, 72)

    fig, axes = plt.subplots(1, 2, figsize=(22, 12))

    for ax, col, year_label in zip(axes, ["ndvi_2019", "ndvi_2024"], ["2019", "2024"]):
        merged.plot(
            column=col,
            cmap="YlGn",
            linewidth=0.6,
            edgecolor="#333333",
            ax=ax,
            vmin=vmin,
            vmax=vmax,
            missing_kwds={"color": "#888888", "edgecolor": "#333333", "hatch": "///", "label": "No data"},
        )
        control_gdf = merged[merged["country"].isin(CONTROL_COUNTRIES)]
        control_gdf.boundary.plot(ax=ax, color="#1a1a1a", linewidth=1.8)

        ax.set_xlim(bounds[0], bounds[2])
        ax.set_ylim(bounds[1], bounds[3])
        ax.set_axis_off()
        ax.set_title(f"NDVI — {year_label}", fontsize=18, fontweight="bold", pad=10)

    sm = plt.cm.ScalarMappable(cmap="YlGn", norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=axes, orientation="horizontal", shrink=0.4, pad=0.04)
    cbar.set_label("Mean NDVI (Vegetation Health Index)", fontsize=10)
    cbar.ax.tick_params(labelsize=10)

    fig.suptitle(
        "NDVI (Vegetation Health) Before vs. After the European Climate Law: EU-27 and Control Group (2019 vs. 2024)\n"
        "Thick borders mark non-EU control-group countries (UK, Norway, Switzerland)",
        fontsize=13, fontweight="bold"
    )

    plt.figtext(0.5, 0.02, "Green Policy Intelligence Engine (GPIE) — Source: CGLS NDVI 300m, Sentinel Hub Statistical API",
                ha="center", fontsize=8, color="gray")

    plt.subplots_adjust(wspace=0.05)
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_map()