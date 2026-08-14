"""
GPIE — builds the master dataset: EU-27 vs. a 9-country non-EU control
group (UK, Norway, Switzerland, Iceland, Albania, Bosnia and Herzegovina,
Montenegro, North Macedonia, Serbia), 2019-2024 monthly.

NO2/NDVI/climate/GDP each come from two source files per variable (a base
fetch and a supplementary fetch covering the Balkans + Iceland + a clean
Norway re-pull); the overlay functions merge them on (country, year, month),
with the supplementary file winning on any collision.

    python master_merge_control.py
"""
import json
import csv
import os
from datetime import datetime

# Input paths
NO2_BASE_PATH = "data/earth_observation/no2/final/no2_stats_all_countries.json"
NO2_SUPP_PATH = "data/earth_observation/no2/final/no2_stats_control_expansion.json"

NDVI_BASE_PATH = "data/earth_observation/ndvi/final/ndvi_stats_all_countries_v2.json"
NDVI_SUPP_PATH = "data/earth_observation/ndvi/final/ndvi_stats_control_expansion.json"

CLIMATE_BASE_PATH = "data/earth_observation/climate/final/era5_stats_all_countries_monthly.json"
CLIMATE_SUPP_PATH = "data/earth_observation/climate/final/era5_stats_control_expansion_monthly.json"

GDP_EU_PATH = "data/earth_observation/economy/final/gdp_by_country_year.csv"
GDP_CONTROL_PATH = "data/earth_observation/economy/final/gdp_control_countries.csv"
GDP_SUPP_PATH = "data/earth_observation/economy/final/gdp_control_expansion.csv"

OUTPUT_PATH = "data/master_dataset_control.csv"

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


def overlay_by_key(base_flat, supp_flat):
    """Supplementary records win on (country, year, month) collisions -
    this is how Norway's clean-refetch NO2 replaces its original series."""
    merged = {}
    for r in base_flat:
        merged[(r["country"], r["year"], r["month"])] = r
    for r in supp_flat:
        merged[(r["country"], r["year"], r["month"])] = r
    return list(merged.values())


def overlay_climate(base_data, supp_data):
    lookup = {}
    for r in base_data:
        year_str, month_str = r["month"].split("-")
        lookup[(r["NUTS_ID"], int(year_str), int(month_str))] = r
    for r in supp_data:
        year_str, month_str = r["month"].split("-")
        lookup[(r["NUTS_ID"], int(year_str), int(month_str))] = r
    return lookup


def load_combined_gdp_lookup():
    """Combines EU-27 (Eurostat) and control-group (World Bank) GDP into one lookup."""
    lookup = {}

    for path in (GDP_EU_PATH, GDP_CONTROL_PATH, GDP_SUPP_PATH):
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
    no2_base = flatten_nested_stats(load_json(NO2_BASE_PATH), "no2")
    no2_supp = flatten_nested_stats(load_json(NO2_SUPP_PATH), "no2")
    no2_flat = overlay_by_key(no2_base, no2_supp)

    ndvi_base = flatten_nested_stats(load_json(NDVI_BASE_PATH), "ndvi")
    ndvi_supp = flatten_nested_stats(load_json(NDVI_SUPP_PATH), "ndvi")
    ndvi_flat = overlay_by_key(ndvi_base, ndvi_supp)

    print(f"NO2 flattened: {len(no2_flat)} records")
    print(f"NDVI flattened: {len(ndvi_flat)} records")

    ndvi_lookup = {(r["country"], r["year"], r["month"]): r for r in ndvi_flat}
    climate_lookup = overlay_climate(load_json(CLIMATE_BASE_PATH), load_json(CLIMATE_SUPP_PATH))
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
    print(f"\nMaster dataset (control-group) built: {len(master_rows)} rows")
    print(f"Countries ({len(countries)}): {countries}")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_master_dataset()
