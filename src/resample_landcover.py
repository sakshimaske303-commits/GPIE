import os
from osgeo import gdal

INPUT_VRT = "data/earth_observation/land_cover/processed/worldcover_2021_mosaic.vrt"
OUTPUT_PATH = "data/earth_observation/land_cover/processed/worldcover_2021_500m.tif"


def resample_for_stats():
    """Resample the 10m WorldCover mosaic to a coarser grid so the zonal stats fit in memory."""
    print("Resampling to about 500m resolution... (this will take a few minutes)")

    result = gdal.Warp(
        OUTPUT_PATH,
        INPUT_VRT,
        xRes=0.005,  # roughly 500m in degrees
        yRes=0.005,
        resampleAlg="near",  # nearest-neighbor keeps the class codes intact
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