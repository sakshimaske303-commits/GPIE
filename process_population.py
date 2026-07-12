import os
import json
import numpy as np
from osgeo import gdal

POP_RAW_DIR = "data/earth_observation/population/raw"
POP_FINAL_DIR = "data/earth_observation/population/final"
OUTPUT_PATH = os.path.join(POP_FINAL_DIR, "population_stats_by_country.json")

# ISO3 (lowercase, matches WorldPop filenames) -> NUTS_ID (ISO2, matches project convention)
ISO3_TO_NUTS = {
    "aut": "AT", "bel": "BE", "bgr": "BG", "hrv": "HR", "cyp": "CY",
    "cze": "CZ", "dnk": "DK", "est": "EE", "fin": "FI", "fra": "FR",
    "deu": "DE", "grc": "EL", "hun": "HU", "irl": "IE", "ita": "IT",
    "lva": "LV", "ltu": "LT", "lux": "LU", "mlt": "MT", "nld": "NL",
    "pol": "PL", "prt": "PT", "rou": "RO", "svk": "SK", "svn": "SI",
    "esp": "ES", "swe": "SE",
}

YEARS = [2019, 2020]


def compute_country_population(filepath):
    """
    Sums all valid pixel values in a per-country population raster using GDAL
    directly (bypasses a rasterio/NumPy 2.5 compatibility issue observed
    with certain multi-tile/multi-strip TIFF structures).
    """
    try:
        dataset = gdal.Open(filepath)
        if dataset is None:
            print(f"GDAL could not open: {filepath}")
            return None

        band = dataset.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        data = band.ReadAsArray()

        if data is None:
            print(f"GDAL opened but could not read array: {filepath}")
            dataset = None
            return None

        if nodata is not None:
            valid_mask = data != nodata
        else:
            valid_mask = ~np.isnan(data)

        total_population = float(np.sum(data[valid_mask]))
        dataset = None  # close file
        return round(total_population)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


def process_all_population():
    os.makedirs(POP_FINAL_DIR, exist_ok=True)
    results = []

    for iso3, nuts_id in ISO3_TO_NUTS.items():
        for year in YEARS:
            filename = f"{iso3}_ppp_{year}.tif"
            filepath = os.path.join(POP_RAW_DIR, filename)

            if not os.path.exists(filepath):
                print(f"Missing file, skipping: {filename}")
                continue

            total_pop = compute_country_population(filepath)

            if total_pop is not None:
                results.append({
                    "NUTS_ID": nuts_id,
                    "year": year,
                    "total_population": total_pop,
                })
                print(f"{nuts_id} {year}: {total_pop:,}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nProcessed {len(results)} country-year records.")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    process_all_population()