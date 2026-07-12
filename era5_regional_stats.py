import os
import json
import xarray as xr
import geopandas as gpd
from shapely.geometry import mapping
from rasterio import features
import numpy as np

PROCESSED_DIR = "data/earth_observation/climate/processed"
NUTS_BOUNDARY_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"

# GADM boundaries for the 3 non-EU control-group countries
GADM_PATHS = {
    "UK": "data/earth_observation/boundaries/raw/gadm41_GBR_0.json",
    "NO": "data/earth_observation/boundaries/raw/gadm41_NOR_0.json",
    "CH": "data/earth_observation/boundaries/raw/gadm41_CHE_0.json",
}

OUTPUT_PATH = "data/earth_observation/climate/final/era5_stats_all_countries_monthly.json"


def load_all_country_geometries():
    """
    Combines NUTS (EU-27) and GADM (UK, NO, CH) boundaries into a single
    list of (country_code, geometry-mapping) pairs, so the zonal-stats
    loop below can treat all 30 countries identically.
    """
    geometries = []

    control_codes = set(GADM_PATHS.keys())  # UK, NO, CH — will be added from GADM instead

    nuts = gpd.read_file(NUTS_BOUNDARY_PATH)
    for _, row in nuts.iterrows():
        nuts_id = row["NUTS_ID"]
        if nuts_id in control_codes:
            # Skip — NUTS also contains EFTA members (Norway, Switzerland),
            # but we use the GADM version for these to keep the boundary
            # source consistent with the rest of the control-group pipeline.
            continue
        geometries.append((nuts_id, mapping(row["geometry"])))

    for country_code, path in GADM_PATHS.items():
        gadm = gpd.read_file(path)
        # GADM level-0 files contain a single feature covering the whole country
        geom = gadm.iloc[0]["geometry"]
        geometries.append((country_code, mapping(geom)))

    return geometries


def compute_regional_stats(year, country_geometries):
    """
    Computes average temperature and total precipitation per country
    (EU-27 via NUTS + UK/NO/CH via GADM), for each month of the given year.
    """
    file_path = os.path.join(PROCESSED_DIR, f"era5_processed_{year}.nc")
    if not os.path.exists(file_path):
        print(f"Missing processed file for {year}, skipping.")
        return []

    ds = xr.open_dataset(file_path)

    results = []

    for month_idx in range(ds.dims["valid_time"]):
        month_data = ds.isel(valid_time=month_idx)
        month_date = str(month_data["valid_time"].values)[:7]  # YYYY-MM

        temp_array = month_data["temperature_c"].values
        precip_array = month_data["precipitation_mm"].values

        lat = ds["latitude"].values
        lon = ds["longitude"].values

        transform = features.Affine(
            (lon[-1] - lon[0]) / (len(lon) - 1), 0, lon[0],
            0, (lat[-1] - lat[0]) / (len(lat) - 1), lat[0]
        )

        for country_code, geom in country_geometries:
            mask = features.geometry_mask(
                [geom],
                out_shape=temp_array.shape,
                transform=transform,
                invert=True,
            )

            if not mask.any():
                continue

            avg_temp = float(np.nanmean(temp_array[mask]))
            total_precip = float(np.nansum(precip_array[mask]) / mask.sum())

            results.append({
                "NUTS_ID": country_code,
                "month": month_date,
                "avg_temperature_c": round(avg_temp, 2),
                "avg_precipitation_mm": round(total_precip, 2),
            })

    print(f"Computed stats for {year}: {len(results)} country-month records")
    return results


def main():
    country_geometries = load_all_country_geometries()
    print(f"Loaded geometries for {len(country_geometries)} countries")

    all_results = []
    for year in range(2019, 2025):
        all_results.extend(compute_regional_stats(year, country_geometries))

    os.makedirs("data/earth_observation/climate/final", exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nSaved: {OUTPUT_PATH}")
    print(f"Total records: {len(all_results)}")


if __name__ == "__main__":
    main()