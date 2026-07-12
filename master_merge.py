import json
import csv
import os

# Input paths
NO2_PATH = "data/earth_observation/no2/final/no2_stats_by_country_monthly_flat.json"
NDVI_PATH = "data/earth_observation/ndvi/final/ndvi_stats_by_country_monthly_flat.json"
CLIMATE_PATH = "data/earth_observation/climate/final/era5_stats_by_country_monthly.json"
GDP_PATH = "data/earth_observation/economy/final/gdp_by_country_year.csv"
LANDCOVER_PATH = "data/earth_observation/land_cover/final/landcover_stats_by_country.json"
DEM_PATH = "data/earth_observation/dem/final/dem_stats_by_country.json"

OUTPUT_PATH = "data/master_dataset.csv"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def load_gdp_lookup():
    """GDP is country-year (no month) -> lookup dict keyed by (NUTS_ID, year)"""
    lookup = {}
    with open(GDP_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["geo"], int(row["year"]))
            lookup[key] = float(row["gdp_million_eur"])
    return lookup


def load_static_lookup(data, id_field="NUTS_ID"):
    """Land Cover / DEM are static (country only) -> lookup dict keyed by NUTS_ID"""
    lookup = {}
    for record in data:
        lookup[record[id_field]] = record
    return lookup


def build_master_dataset():
    no2_data = load_json(NO2_PATH)
    ndvi_data = load_json(NDVI_PATH)
    climate_data = load_json(CLIMATE_PATH)
    gdp_lookup = load_gdp_lookup()
    landcover_lookup = load_static_lookup(load_json(LANDCOVER_PATH))
    dem_lookup = load_static_lookup(load_json(DEM_PATH))

    # Build lookups for the monthly datasets, keyed by (NUTS_ID, year, month)
    ndvi_lookup = {(r["NUTS_ID"], r["year"], r["month"]): r for r in ndvi_data}

    climate_lookup = {}
    for r in climate_data:
        year_str, month_str = r["month"].split("-")
        key = (r["NUTS_ID"], int(year_str), int(month_str))
        climate_lookup[key] = r

    master_rows = []

    # NO2 is the base table (most granular, drives the merge)
    for row in no2_data:
        nuts_id = row["NUTS_ID"]
        year = row["year"]
        month = row["month"]

        merged_row = {
            "NUTS_ID": nuts_id,
            "year": year,
            "month": month,
            "mean_no2": row.get("mean_no2"),
        }

        # NDVI join
        ndvi_row = ndvi_lookup.get((nuts_id, year, month))
        merged_row["mean_ndvi"] = ndvi_row["mean_ndvi"] if ndvi_row else None

        # Climate join
        climate_row = climate_lookup.get((nuts_id, year, month))
        merged_row["avg_temp_c"] = climate_row["avg_temperature_c"] if climate_row else None
        merged_row["avg_precip_mm"] = climate_row["avg_precipitation_mm"] if climate_row else None

        # GDP join (country-year only, repeats across months of the same year)
        merged_row["gdp_million_eur"] = gdp_lookup.get((nuts_id, year))

        # Land Cover join (static, country only, repeats across all rows for that country)
        lc_row = landcover_lookup.get(nuts_id)
        if lc_row:
            for key, val in lc_row.items():
                if key == "NUTS_ID":
                    continue
                if isinstance(val, dict):
                    # This is the nested class-percentage dictionary — flatten it
                    for class_name, percent in val.items():
                        clean_name = class_name.lower().replace("/", "_").replace(" ", "_")
                        merged_row[f"landcover_{clean_name}"] = percent
                else:
                    merged_row[f"landcover_{key}"] = val

        # DEM join (static, country only, repeats across all rows for that country)
        dem_row = dem_lookup.get(nuts_id)
        if dem_row:
            for key, val in dem_row.items():
                if key != "NUTS_ID":
                    merged_row[key] = val

        master_rows.append(merged_row)

    # Write to CSV
    if master_rows:
        # Collect fieldnames from ALL rows (not just the first), since
        # different countries may have different land cover classes present.
        all_fieldnames = set()
        for row in master_rows:
            all_fieldnames.update(row.keys())

        # Keep a stable, readable column order: core fields first, then the rest alphabetically
        priority_fields = ["NUTS_ID", "year", "month", "mean_no2", "mean_ndvi", "avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
        remaining_fields = sorted(f for f in all_fieldnames if f not in priority_fields)
        fieldnames = priority_fields + remaining_fields

        # Land cover columns: missing means the class is genuinely absent (0%),
        # not unknown data — fill accordingly before writing.
        landcover_cols = [f for f in fieldnames if f.startswith("landcover_")]
        for row in master_rows:
            for col in landcover_cols:
                if col not in row or row[col] is None:
                    row[col] = 0.0

        with open(OUTPUT_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(master_rows)

    print(f"Master dataset built: {len(master_rows)} rows")
    print(f"Columns: {fieldnames}")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_master_dataset()