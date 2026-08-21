import os
import json
import time
import requests
from auth_sentinelhub import get_sentinelhub_token
from country_boundaries import load_country_geometry
from download_ndvi_sentinelhub import request_ndvi_stats
from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT

OUTPUT_DIR = "data/earth_observation/ndvi/final"
EXISTING_FILE = os.path.join(OUTPUT_DIR, "ndvi_stats_all_countries_v2.json")

FAILED_COUNTRIES = ["UK"]


def main():
    access_token = get_sentinelhub_token()

    with open(EXISTING_FILE) as f:
        all_results = json.load(f)

    # Remove any partial/failed entries for these countries, if present
    all_results = [r for r in all_results if r["NUTS_ID"] not in FAILED_COUNTRIES]

    for country_code in FAILED_COUNTRIES:
        geometry = load_country_geometry(
            country_code,
            clip_to_bbox=(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)
        )
        if geometry is None:
            print(f"No geometry found for {country_code}, skipping.")
            continue

        for year in range(2019, 2025):
            print(f"Retrying NDVI stats: {country_code}, {year}")
            result = request_ndvi_stats(access_token, country_code, geometry, year)
            if result:
                all_results.append({"NUTS_ID": country_code, "year": year, "data": result})
            time.sleep(1)

    output_path = os.path.join(OUTPUT_DIR, "ndvi_stats_all_countries_v2.json")
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nSaved: {output_path}")
    print(f"Total records: {len(all_results)}")


if __name__ == "__main__":
    main()