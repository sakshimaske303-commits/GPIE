"""I plot one day of my daily NO2 rasters with country borders, for the dashboard's physics page."""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT

DAY = sys.argv[1] if len(sys.argv) > 1 else "2023-09-08"    # my day with the most valid pixels
DAY_PATH = os.path.join("data", "earth_observation", "no2", "gridded", "daily", f"{DAY}.npz")
NUTS_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"
GADM_PATHS = ["data/earth_observation/boundaries/raw/gadm41_GBR_0.json",
              "data/earth_observation/boundaries/raw/gadm41_NOR_0.json",
              "data/earth_observation/boundaries/raw/gadm41_CHE_0.json"]
OUT_PATH = "outputs/plots/tropomi_example_day.png"


def rings(geometry):
    """Outer rings of a GeoJSON polygon or multipolygon."""
    polys = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    return [np.asarray(p[0])[:, :2] for p in polys]


def main():
    with np.load(DAY_PATH) as z:
        no2 = z["no2"].astype("float64")
    fig, ax = plt.subplots(figsize=(10, 9))
    im = ax.imshow(no2 * 1e6, extent=(MIN_LON, MAX_LON, MIN_LAT, MAX_LAT), cmap="viridis",
                   vmin=0, vmax=100, aspect=1.5, interpolation="nearest")
    with open(NUTS_PATH, encoding="utf-8") as f:
        features = json.load(f)["features"]
    for path in GADM_PATHS:
        with open(path, encoding="utf-8") as f:
            features += json.load(f)["features"]
    for feat in features:
        if feat["properties"].get("NUTS_ID") in ("UK", "NO", "CH"):
            continue                                  # I take these three from GADM
        for ring in rings(feat["geometry"]):
            ax.plot(ring[:, 0], ring[:, 1], color="#444444", linewidth=0.4)
    ax.set_xlim(-12, 35)
    ax.set_ylim(34, 71.5)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"One day of Sentinel-5P TROPOMI tropospheric NO₂, {DAY}\n"
                 "0.1° raster, quality value ≥ 0.75; white = no valid retrieval (cloud, or gaps between orbits)", fontsize=11)
    cb = plt.colorbar(im, ax=ax, shrink=0.6, extend="max")
    cb.set_label("Tropospheric NO₂ column (10⁻⁶ mol/m²)")
    plt.figtext(0.5, 0.01, "Contains modified Copernicus Sentinel data (2023), processed by Sentinel Hub",
                ha="center", fontsize=8, color="gray")
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    plt.savefig(OUT_PATH, dpi=200)
    plt.close()
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
