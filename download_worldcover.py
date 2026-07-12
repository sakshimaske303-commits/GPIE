import os
import math
import time
import requests
from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT

WORLDCOVER_RAW_DIR = "data/earth_observation/land_cover/raw"

# Public AWS Open Data bucket (no authentication required)
BASE_URL = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map"


def generate_tile_name(lat, lon):
    """
    Builds the ESA WorldCover tile name for the 3x3 degree cell
    whose lower-left corner is (lat, lon), rounded down to the
    nearest multiple of 3.
    """
    lat_floor = (lat // 3) * 3
    lon_floor = (lon // 3) * 3

    ns = "N" if lat_floor >= 0 else "S"
    ew = "E" if lon_floor >= 0 else "W"

    lat_str = f"{abs(lat_floor):02d}"
    lon_str = f"{abs(lon_floor):03d}"

    tile_name = f"ESA_WorldCover_10m_2021_v200_{ns}{lat_str}{ew}{lon_str}_Map"
    return tile_name


def download_tile(lat, lon, max_retries=3):
    """
    Downloads a single WorldCover tile if it exists and isn't already complete.
    Returns "downloaded", "skipped", "not_found", or "failed".
    """
    tile_name = generate_tile_name(lat, lon)
    url = f"{BASE_URL}/{tile_name}.tif"

    os.makedirs(WORLDCOVER_RAW_DIR, exist_ok=True)
    filepath = os.path.join(WORLDCOVER_RAW_DIR, f"{tile_name}.tif")

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print(f"Skipping (already exists): {tile_name}")
        return "skipped"

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, stream=True, timeout=120)

            if response.status_code == 404:
                return "not_found"

            if response.status_code != 200:
                print(f"Attempt {attempt}: Failed ({response.status_code}) for {tile_name}")
                time.sleep(3)
                continue

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Downloaded: {tile_name}")
            return "downloaded"

        except Exception as e:
            print(f"Attempt {attempt}: Error downloading {tile_name}: {e}")
            time.sleep(3)

    print(f"FAILED after {max_retries} attempts: {tile_name}")
    return "failed"


def download_worldcover_for_bbox(min_lon, min_lat, max_lon, max_lat):
    """
    Downloads all WorldCover tiles intersecting the given bounding box.
    Iterates in steps of 3 degrees (WorldCover's native tile grid).
    """
    lat_start = int((min_lat // 3) * 3)
    lat_end = int((max_lat // 3) * 3)
    lon_start = int((min_lon // 3) * 3)
    lon_end = int((max_lon // 3) * 3)

    total_checked = 0
    downloaded = 0
    skipped = 0
    not_found = 0
    failed = 0

    for lat in range(lat_start, lat_end + 1, 3):
        for lon in range(lon_start, lon_end + 1, 3):
            total_checked += 1
            result = download_tile(lat, lon)

            if result == "downloaded":
                downloaded += 1
            elif result == "skipped":
                skipped += 1
            elif result == "not_found":
                not_found += 1
            elif result == "failed":
                failed += 1

    print("\n" + "=" * 50)
    print("WORLDCOVER DOWNLOAD SUMMARY")
    print("=" * 50)
    print(f"Total tiles checked : {total_checked}")
    print(f"Newly downloaded    : {downloaded}")
    print(f"Already complete    : {skipped}")
    print(f"Not found           : {not_found}")
    print(f"Failed              : {failed}")


def main():
    download_worldcover_for_bbox(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)


if __name__ == "__main__":
    main()