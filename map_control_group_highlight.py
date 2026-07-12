import json
import geopandas as gpd
from shapely.geometry import shape
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

NUTS_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"
GADM_PATHS = {
    "UK": "data/earth_observation/boundaries/raw/gadm41_GBR_0.json",
    "NO": "data/earth_observation/boundaries/raw/gadm41_NOR_0.json",
    "CH": "data/earth_observation/boundaries/raw/gadm41_CHE_0.json",
}
OUTPUT_PATH = "outputs/plots/control_group_design_map.png"

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


def make_map():
    os.makedirs("outputs/plots", exist_ok=True)

    gdf = build_geometry_gdf()
    gdf["group"] = gdf["country"].apply(
        lambda c: "Treatment (EU-27, subject to Green Deal)" if c in EU27_COUNTRIES else "Control Group (non-EU)"
    )

    bounds = (-25, 34, 35, 72)

    fig, ax = plt.subplots(figsize=(13, 12))

    eu_gdf = gdf[gdf["group"] == "Treatment (EU-27, subject to Green Deal)"]
    control_gdf = gdf[gdf["group"] == "Control Group (non-EU)"]

    eu_gdf.plot(ax=ax, color="#2c7fb8", edgecolor="#1a1a1a", linewidth=0.6, alpha=0.85)
    control_gdf.plot(ax=ax, color="#e34a33", edgecolor="#1a1a1a", linewidth=1.8, alpha=0.9)

    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    ax.set_axis_off()

    legend_patches = [
        mpatches.Patch(color="#2c7fb8", label="Treatment Group — EU-27 (27 countries)"),
        mpatches.Patch(color="#e34a33", label="Control Group — UK, Norway, Switzerland (3 countries)"),
    ]
    ax.legend(handles=legend_patches, loc="lower left", fontsize=11, frameon=True, framealpha=0.95)

    ax.set_title(
        "GPIE Study Design: Treatment vs. Control Group\n"
        "Difference-in-Differences comparison — EU-27 (subject to the European Climate Law) vs. three non-EU comparator countries",
        fontsize=13, fontweight="bold", pad=15
    )

    plt.figtext(0.5, 0.02, "Green Policy Intelligence Engine (GPIE)",
                ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_map()