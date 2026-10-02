"""I pull one NO2 raster per day for Europe and pool them into true monthly means for all
36 countries (EU-27 plus 9 controls), 2019-2024."""
import json
import os
from auth_sentinelhub import get_sentinelhub_token
from country_boundaries import load_country_geometry, get_all_country_codes
from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT
from s5p_process_daily import run_daily, monthly_from_log

OUTPUT_DIR = "data/earth_observation/no2/final"
LOG_PATH = os.path.join(OUTPUT_DIR, "no2_daily_country_log.jsonl")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "no2_stats_monthly_mean_36.json")
BBOX = (MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)


def main():
    codes = get_all_country_codes()  # 36 countries
    geometries = {}
    for code in codes:
        g = load_country_geometry(code, clip_to_bbox=BBOX)
        if g is None:
            raise RuntimeError(f"No geometry for {code}")
        geometries[code] = g

    failures = run_daily(get_sentinelhub_token, BBOX, geometries, LOG_PATH)

    monthly = monthly_from_log(LOG_PATH, codes, "no2")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(monthly, f, indent=2)
    print(f"\nSaved: {OUTPUT_PATH}  ({len(monthly)} country-year records)")
    if failures:
        print("Some days are still missing. The monthly file is incomplete until a second run fills them.")


if __name__ == "__main__":
    main()
