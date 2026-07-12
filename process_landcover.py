import os
import glob
from osgeo import gdal

WORLDCOVER_RAW_DIR = "data/earth_observation/land_cover/raw"
WORLDCOVER_PROCESSED_DIR = "data/earth_observation/land_cover/processed"

VRT_PATH = os.path.join(WORLDCOVER_PROCESSED_DIR, "worldcover_2021_mosaic.vrt")


def build_mosaic_vrt():
    """
    Builds a Virtual Raster (VRT) mosaic from all downloaded WorldCover tiles.
    This does not duplicate pixel data - it's a lightweight index file
    that lets GDAL/QGIS/Python treat all tiles as one continuous raster.
    """
    os.makedirs(WORLDCOVER_PROCESSED_DIR, exist_ok=True)

    tile_paths = glob.glob(os.path.join(WORLDCOVER_RAW_DIR, "*.tif"))

    if not tile_paths:
        print("No tiles found in raw directory.")
        return None

    print(f"Found {len(tile_paths)} tiles. Building VRT mosaic...")

    vrt = gdal.BuildVRT(VRT_PATH, tile_paths)
    vrt = None  # flush to disk

    print(f"VRT mosaic created: {VRT_PATH}")
    return VRT_PATH


if __name__ == "__main__":
    build_mosaic_vrt()