"""I fetch CGLS 300 m NDVI for all 36 countries, 2019-2024, as true monthly means of the
10-day composites."""
import os
import json
import time
from auth_sentinelhub import get_sentinelhub_token
from country_boundaries import load_country_geometry, get_all_country_codes
from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT
from sentinelhub_stats import request_monthly_stats

OUTPUT_DIR = "data/earth_observation/ndvi/final"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "ndvi_stats_monthly_mean_36.json")


def main():
    access_token = get_sentinelhub_token()
    country_codes = get_all_country_codes()  # 36 countries
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_results, failures = [], []
    for country_code in country_codes:
        geometry = load_country_geometry(country_code, clip_to_bbox=(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT))
        if geometry is None:
            print(f"No geometry for {country_code}, skipping.")
            failures.append((country_code, "all"))
            continue
        for year in range(2019, 2025):
            print(f"Requesting NDVI monthly-mean stats: {country_code}, {year}")
            result = request_monthly_stats(access_token, geometry, year, "ndvi")
            if result:
                all_results.append({"NUTS_ID": country_code, "year": year, "data": result})
            else:
                failures.append((country_code, year))
            time.sleep(1)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved: {OUTPUT_PATH}  ({len(all_results)} country-year records)")
    if failures:
        print(f"FAILED requests (the output is incomplete until these are fetched): {failures}")


if __name__ == "__main__":
    main()
