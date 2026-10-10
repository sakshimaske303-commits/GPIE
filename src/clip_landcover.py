import os
from osgeo import gdal

WORLDCOVER_PROCESSED_DIR = "data/earth_observation/land_cover/processed"
VRT_PATH = os.path.join(WORLDCOVER_PROCESSED_DIR, "worldcover_2021_mosaic.vrt")

NUTS_BOUNDARY_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"

CLIPPED_OUTPUT_PATH = os.path.join(WORLDCOVER_PROCESSED_DIR, "worldcover_2021_clipped.tif")


def clip_to_eu_boundary():
    """Clip the WorldCover mosaic to the NUTS country boundaries (drops ocean and North Africa)."""
    if not os.path.exists(NUTS_BOUNDARY_PATH):
        print(f"NUTS boundary file not found at: {NUTS_BOUNDARY_PATH}")
        return None

    print("Clipping WorldCover mosaic to EU boundary... (this may take a few minutes)")

    result = gdal.Warp(
        CLIPPED_OUTPUT_PATH,
        VRT_PATH,
        cutlineDSName=NUTS_BOUNDARY_PATH,
        cropToCutline=True,
        dstNodata=0,
    )

    result = None  # flush to disk

    print(f"Clipped raster created: {CLIPPED_OUTPUT_PATH}")
    return CLIPPED_OUTPUT_PATH


if __name__ == "__main__":
    clip_to_eu_boundary()