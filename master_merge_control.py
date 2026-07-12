import json
import csv
import os
from datetime import datetime

# Input paths
NO2_PATH = "data/earth_observation/no2/final/no2_stats_all_countries.json"
NDVI_PATH = "data/earth_observation/ndvi/final/ndvi_stats_all_countries_v2.json"
CLIMATE_PATH = "data/earth_observation/climate/final/era5_stats_all_countries_monthly.json"
GDP_EU_PATH = "data/earth_observation/economy/final/gdp_by_country_year.csv"
GDP_CONTROL_PATH = "data/earth_observation/economy/final/gdp_control_countries.csv"

OUTPUT_PATH = "data/master_dataset_control.csv"

EU27_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
}
CONTROL_COUNTRIES = {"UK", "NO", "CH"}


def flatten_nested_stats(raw_data, variable_key):
    """
    Flattens the raw nested Sentinel Hub Statistical API response
    (used for both NO2 and NDVI) into per-country-year-month records.
    variable_key is "no2" or "ndvi", matching the evalscript output id.
    """
    flat_records = []
    for country_year_record in raw_data:
        country_code = country_year_record["NUTS_ID"]
        year = country_year_record["year"]
        monthly_entries = country_year_record["data"]["data"]

        for entry in monthly_entries:
            start_date = entry["interval"]["from"]
            month = datetime.fromisoformat(start_date.replace("Z", "+00:00")).month
            stats = entry["outputs"][variable_key]["bands"]["B0"]["stats"]

            flat_records.append({
                "country": country_code,
                "year": year,
                "month": month,
                f"mean_{variable_key}": stats.get("mean"),
            })

    return flat_records


def load_json(path):
    with open(path) as f:
        return json.load(f)


def load_combined_gdp_lookup():
    """Combines EU-27 (Eurostat) and control-group (World Bank) GDP into one lookup."""
    lookup = {}

    with open(GDP_EU_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["geo"], int(row["year"]))
            lookup[key] = float(row["gdp_million_eur"])

    with open(GDP_CONTROL_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["geo"], int(row["year"]))
            lookup[key] = float(row["gdp_million_eur"])

    return lookup


def build_master_dataset():
    no2_raw = load_json(NO2_PATH)
    ndvi_raw = load_json(NDVI_PATH)
    climate_data = load_json(CLIMATE_PATH)
    gdp_lookup = load_combined_gdp_lookup()

    no2_flat = flatten_nested_stats(no2_raw, "no2")
    ndvi_flat = flatten_nested_stats(ndvi_raw, "ndvi")

    print(f"NO2 flattened: {len(no2_flat)} records")
    print(f"NDVI flattened: {len(ndvi_flat)} records")

    ndvi_lookup = {(r["country"], r["year"], r["month"]): r for r in ndvi_flat}

    climate_lookup = {}
    for r in climate_data:
        year_str, month_str = r["month"].split("-")
        key = (r["NUTS_ID"], int(year_str), int(month_str))
        climate_lookup[key] = r

    master_rows = []

    for row in no2_flat:
        country = row["country"]
        year = row["year"]
        month = row["month"]

        merged_row = {
            "country": country,
            "year": year,
            "month": month,
            "treatment_group": 1 if country in EU27_COUNTRIES else 0,
            "mean_no2": row.get("mean_no2"),
        }

        ndvi_row = ndvi_lookup.get((country, year, month))
        merged_row["mean_ndvi"] = ndvi_row["mean_ndvi"] if ndvi_row else None

        climate_row = climate_lookup.get((country, year, month))
        merged_row["avg_temp_c"] = climate_row["avg_temperature_c"] if climate_row else None
        merged_row["avg_precip_mm"] = climate_row["avg_precipitation_mm"] if climate_row else None

        merged_row["gdp_million_eur"] = gdp_lookup.get((country, year))

        master_rows.append(merged_row)

    if master_rows:
        fieldnames = list(master_rows[0].keys())
        with open(OUTPUT_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(master_rows)

    print(f"\nMaster dataset (control-group) built: {len(master_rows)} rows")
    print(f"Countries: {sorted(set(r['country'] for r in master_rows))}")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_master_dataset()