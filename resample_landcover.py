import os
from osgeo import gdal

INPUT_VRT = "data/earth_observation/land_cover/processed/worldcover_2021_mosaic.vrt"
OUTPUT_PATH = "data/earth_observation/land_cover/processed/worldcover_2021_500m.tif"


def resample_for_stats():
    """
    Resamples the 10m WorldCover mosaic to 100m resolution.
    Country-level land cover percentages don't need 10m precision,
    and this reduces the data volume by ~100x, making zonal statistics
    computation feasible without exhausting memory.
    """
    print("Resampling to 100m resolution... (this will take a few minutes)")

    result = gdal.Warp(
        OUTPUT_PATH,
        INPUT_VRT,
        xRes=0.005,  # roughly 500m in degrees
        yRes=0.005,
        resampleAlg="near",  # nearest-neighbor: preserves categorical class values
        creationOptions=["COMPRESS=LZW"],
    )

    if result is None:
        print("Resampling FAILED.")
        return None

    result = None  # flush to disk
    print(f"Resampled raster created: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    resample_for_stats()