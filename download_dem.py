import os
import math
import time
import requests
from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT

DEM_RAW_DIR = "data/earth_observation/dem/raw"
BASE_URL = "https://copernicus-dem-30m.s3.amazonaws.com"
NOT_FOUND_CACHE_PATH = os.path.join(DEM_RAW_DIR, "_not_found_cache.txt")


def generate_tile_name(lat, lon):
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    lat_str = f"{abs(lat):02d}"
    lon_str = f"{abs(lon):03d}"
    return f"Copernicus_DSM_COG_10_{ns}{lat_str}_00_{ew}{lon_str}_00_DEM"


def get_remote_size(url):
    try:
        response = requests.head(url, timeout=30)
        if response.status_code == 200:
            return int(response.headers.get("Content-Length", 0))
        return None
    except Exception:
        return None


def is_complete_local_file(filepath, expected_size):
    if not os.path.exists(filepath):
        return False
    if expected_size is None or expected_size == 0:
        return False
    return os.path.getsize(filepath) == expected_size


def load_not_found_cache():
    if os.path.exists(NOT_FOUND_CACHE_PATH):
        with open(NOT_FOUND_CACHE_PATH) as f:
            return set(line.strip() for line in f)
    return set()


def save_to_not_found_cache(tile_name):
    with open(NOT_FOUND_CACHE_PATH, "a") as f:
        f.write(tile_name + "\n")


def download_tile(lat, lon, not_found_cache, max_retries=3):
    tile_name = generate_tile_name(lat, lon)
    url = f"{BASE_URL}/{tile_name}/{tile_name}.tif"

    os.makedirs(DEM_RAW_DIR, exist_ok=True)
    filepath = os.path.join(DEM_RAW_DIR, f"{tile_name}.tif")

    if os.path.exists(filepath) and os.path.getsize(filepath) > 1_000_000:
        #print(f"Skipping (local file exists): {tile_name}")
        return "skipped"

    if tile_name in not_found_cache:
        return "not_found"

    expected_size = get_remote_size(url)

    if expected_size is None:
        save_to_not_found_cache(tile_name)
        return "not_found"

    if is_complete_local_file(filepath, expected_size):
        print(f"Skipping (already complete): {tile_name}")
        return "skipped"

    if os.path.exists(filepath):
        os.remove(filepath)

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, stream=True, timeout=120)

            if response.status_code != 200:
                print(f"Attempt {attempt}: Failed ({response.status_code}) for {tile_name}")
                time.sleep(3)
                continue

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            if is_complete_local_file(filepath, expected_size):
                print(f"Downloaded successfully: {tile_name}")
                return "downloaded"
            else:
                print(f"Attempt {attempt}: Incomplete download for {tile_name}, retrying...")
                if os.path.exists(filepath):
                    os.remove(filepath)
                time.sleep(3)

        except Exception as e:
            print(f"Attempt {attempt}: Error downloading {tile_name}: {e}")
            time.sleep(3)

    print(f"FAILED after {max_retries} attempts: {tile_name}")
    return "failed"


def download_dem_for_bbox(min_lon, min_lat, max_lon, max_lat):
    lat_start = math.floor(min_lat)
    lat_end = math.floor(max_lat)
    lon_start = math.floor(min_lon)
    lon_end = math.floor(max_lon)

    not_found_cache = load_not_found_cache()

    total_checked = 0
    downloaded = 0
    skipped = 0
    not_found = 0
    failed = 0

    for lat in range(lat_start, lat_end + 1):
        for lon in range(lon_start, lon_end + 1):
            total_checked += 1
            result = download_tile(lat, lon, not_found_cache)
            if total_checked % 50 == 0:
                print(f"Progress: {total_checked} tiles checked so far...")

            if result == "downloaded":
                downloaded += 1
            elif result == "skipped":
                skipped += 1
            elif result == "not_found":
                not_found += 1
            elif result == "failed":
                failed += 1

    print("\n" + "=" * 50)
    print("DEM DOWNLOAD SUMMARY")
    print("=" * 50)
    print(f"Total tiles checked : {total_checked}")
    print(f"Newly downloaded    : {downloaded}")
    print(f"Already complete    : {skipped}")
    print(f"Not found (ocean)   : {not_found}")
    print(f"Failed               : {failed}")


def main():
    download_dem_for_bbox(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)


if __name__ == "__main__":
    main()