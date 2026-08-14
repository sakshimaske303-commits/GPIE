"""
GPIE — builds the expanded control-group dataset: the original 30-country
panel plus Iceland, Albania, Bosnia and Herzegovina, Montenegro, North
Macedonia and Serbia, with Norway's NO2 series replaced by the clean
re-fetch (fixes the 29/72-month gap the original file had).

Same flatten/lookup logic as master_merge_control.py, just overlaying the
*_control_expansion.json/csv files on top of the originals before the
final merge. Doesn't touch master_dataset_control.csv - writes a new file
so the original stays available for comparison.

    python master_merge_control_expanded.py
"""
import json
import csv
import os
from datetime import datetime

NO2_ORIGINAL_PATH = "data/earth_observation/no2/final/no2_stats_all_countries.json"
NO2_EXPANSION_PATH = "data/earth_observation/no2/final/no2_stats_control_expansion.json"

NDVI_ORIGINAL_PATH = "data/earth_observation/ndvi/final/ndvi_stats_all_countries_v2.json"
NDVI_EXPANSION_PATH = "data/earth_observation/ndvi/final/ndvi_stats_control_expansion.json"

CLIMATE_ORIGINAL_PATH = "data/earth_observation/climate/final/era5_stats_all_countries_monthly.json"
CLIMATE_EXPANSION_PATH = "data/earth_observation/climate/final/era5_stats_control_expansion_monthly.json"

GDP_EU_PATH = "data/earth_observation/economy/final/gdp_by_country_year.csv"
GDP_CONTROL_PATH = "data/earth_observation/economy/final/gdp_control_countries.csv"
GDP_EXPANSION_PATH = "data/earth_observation/economy/final/gdp_control_expansion.csv"

OUTPUT_PATH = "data/master_dataset_control_expanded.csv"

EU27_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
}
CONTROL_COUNTRIES = {"UK", "NO", "CH", "IS", "AL", "BA", "ME", "MK", "RS"}


def load_json(path):
    if not os.path.exists(path):
        print(f"Missing: {path}")
        return []
    with open(path) as f:
        return json.load(f)


def flatten_nested_stats(raw_data, variable_key):
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


def overlay_by_key(original_flat, expansion_flat, variable_key):
    """Expansion records win on (country, year, month) collisions - this is
    how Norway's re-fetched NO2 replaces its gappy original series."""
    merged = {}
    for r in original_flat:
        merged[(r["country"], r["year"], r["month"])] = r
    for r in expansion_flat:
        merged[(r["country"], r["year"], r["month"])] = r
    return list(merged.values())


def overlay_climate(original_data, expansion_data):
    lookup = {}
    for r in original_data:
        year_str, month_str = r["month"].split("-")
        lookup[(r["NUTS_ID"], int(year_str), int(month_str))] = r
    for r in expansion_data:
        year_str, month_str = r["month"].split("-")
        lookup[(r["NUTS_ID"], int(year_str), int(month_str))] = r
    return lookup


def load_combined_gdp_lookup():
    lookup = {}

    for path in (GDP_EU_PATH, GDP_CONTROL_PATH, GDP_EXPANSION_PATH):
        if not os.path.exists(path):
            print(f"Missing: {path}")
            continue
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["geo"], int(row["year"]))
                lookup[key] = float(row["gdp_million_eur"])

    return lookup


def build_master_dataset():
    no2_original = flatten_nested_stats(load_json(NO2_ORIGINAL_PATH), "no2")
    no2_expansion = flatten_nested_stats(load_json(NO2_EXPANSION_PATH), "no2")
    no2_flat = overlay_by_key(no2_original, no2_expansion, "no2")

    ndvi_original = flatten_nested_stats(load_json(NDVI_ORIGINAL_PATH), "ndvi")
    ndvi_expansion = flatten_nested_stats(load_json(NDVI_EXPANSION_PATH), "ndvi")
    ndvi_flat = overlay_by_key(ndvi_original, ndvi_expansion, "ndvi")

    print(f"NO2: {len(no2_original)} original + {len(no2_expansion)} expansion -> {len(no2_flat)} merged")
    print(f"NDVI: {len(ndvi_original)} original + {len(ndvi_expansion)} expansion -> {len(ndvi_flat)} merged")

    ndvi_lookup = {(r["country"], r["year"], r["month"]): r for r in ndvi_flat}
    climate_lookup = overlay_climate(load_json(CLIMATE_ORIGINAL_PATH), load_json(CLIMATE_EXPANSION_PATH))
    gdp_lookup = load_combined_gdp_lookup()

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

    countries = sorted(set(r["country"] for r in master_rows))
    print(f"\nExpanded master dataset built: {len(master_rows)} rows")
    print(f"Countries ({len(countries)}): {countries}")
    print(f"Control-group countries: {sorted(c for c in countries if c not in EU27_COUNTRIES)}")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_master_dataset()
