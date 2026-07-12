import json
import os
from datetime import datetime

INPUT_PATH = "data/earth_observation/no2/final/no2_stats_by_country_monthly.json"
OUTPUT_PATH = "data/earth_observation/no2/final/no2_stats_by_country_monthly_flat.json"


def flatten_no2():
    with open(INPUT_PATH) as f:
        raw_data = json.load(f)

    flat_records = []

    for country_year_record in raw_data:
        nuts_id = country_year_record["NUTS_ID"]
        year = country_year_record["year"]

        monthly_entries = country_year_record["data"]["data"]

        for entry in monthly_entries:
            # Extract month number from the interval start date
            start_date = entry["interval"]["from"]
            month = datetime.fromisoformat(start_date.replace("Z", "+00:00")).month

            stats = entry["outputs"]["no2"]["bands"]["B0"]["stats"]

            flat_records.append({
                "NUTS_ID": nuts_id,
                "year": year,
                "month": month,
                "mean_no2": stats.get("mean"),
                "min_no2": stats.get("min"),
                "max_no2": stats.get("max"),
                "stdev_no2": stats.get("stDev"),
                "sample_count": stats.get("sampleCount"),
                "no_data_count": stats.get("noDataCount"),
            })

    with open(OUTPUT_PATH, "w") as f:
        json.dump(flat_records, f, indent=2)

    print(f"Flattened {len(raw_data)} country-year records into {len(flat_records)} country-year-month records.")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    flatten_no2()