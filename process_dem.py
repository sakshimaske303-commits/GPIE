import os
import glob
from osgeo import gdal
import rasterstats
import json

DEM_RAW_DIR = "data/earth_observation/dem/raw"
DEM_PROCESSED_DIR = "data/earth_observation/dem/processed"
DEM_FINAL_DIR = "data/earth_observation/dem/final"

VRT_PATH = os.path.join(DEM_PROCESSED_DIR, "dem_mosaic.vrt")
RESAMPLED_PATH = os.path.join(DEM_PROCESSED_DIR, "dem_500m.tif")

NUTS_BOUNDARY_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"
OUTPUT_JSON_PATH = os.path.join(DEM_FINAL_DIR, "dem_stats_by_country.json")


def build_mosaic_vrt():
    """
    Builds a Virtual Raster mosaic from all downloaded DEM tiles,
    same lightweight-index approach used for DS04 Land Cover.
    """
    os.makedirs(DEM_PROCESSED_DIR, exist_ok=True)

    tile_paths = glob.glob(os.path.join(DEM_RAW_DIR, "*.tif"))

    if not tile_paths:
        print("No DEM tiles found in raw directory.")
        return None

    print(f"Found {len(tile_paths)} DEM tiles. Building VRT mosaic...")

    vrt = gdal.BuildVRT(VRT_PATH, tile_paths)
    vrt = None

    print(f"VRT mosaic created: {VRT_PATH}")
    return VRT_PATH


def resample_for_stats():
    """
    Resamples the DEM mosaic to 500m using bilinear resampling.
    Unlike DS04 (categorical land cover, nearest-neighbor required),
    elevation is a continuous variable, so averaging-based resampling
    (bilinear) is scientifically appropriate here.
    """
    print("Resampling DEM to 500m resolution...")

    result = gdal.Warp(
        RESAMPLED_PATH,
        VRT_PATH,
        xRes=0.005,
        yRes=0.005,
        resampleAlg="bilinear",
        creationOptions=["COMPRESS=LZW"],
    )

    if result is None:
        print("Resampling FAILED.")
        return None

    result = None
    print(f"Resampled DEM created: {RESAMPLED_PATH}")
    return RESAMPLED_PATH


def compute_elevation_stats():
    """
    Computes elevation statistics (mean, min, max, std) per NUTS country.
    """
    print("Computing zonal elevation statistics per NUTS region...")

    stats = rasterstats.zonal_stats(
        NUTS_BOUNDARY_PATH,
        RESAMPLED_PATH,
        stats=["mean", "min", "max", "std"],
        geojson_out=True,
    )

    results = []
    for feature in stats:
        props = feature["properties"]
        results.append({
            "NUTS_ID": props.get("NUTS_ID"),
            "elevation_mean_m": round(props.get("mean"), 2) if props.get("mean") is not None else None,
            "elevation_min_m": round(props.get("min"), 2) if props.get("min") is not None else None,
            "elevation_max_m": round(props.get("max"), 2) if props.get("max") is not None else None,
            "elevation_std_m": round(props.get("std"), 2) if props.get("std") is not None else None,
        })

    os.makedirs(DEM_FINAL_DIR, exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved: {OUTPUT_JSON_PATH}")
    return results


def main():
    build_mosaic_vrt()
    resample_for_stats()
    compute_elevation_stats()


if __name__ == "__main__":
    main()