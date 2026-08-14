"""
GPIE — climate stats for the expanded control group, computed from the
ERA5 grid files already downloaded for the original 30-country run
(era5_processed_{year}.nc). Iceland and the Western Balkans both fall
inside the same Europe bounding box used for that download (config.py:
MIN_LON=-31.5, MAX_LON=35.0, MIN_LAT=27.5, MAX_LAT=71.5), so this is a
zonal-stats pass over existing data, not a new download.

Norway isn't re-processed here — its climate coverage was already fine,
only its NO2 had a gap.

    python era5_regional_stats_control_expansion.py
"""
import os
import json
import geopandas as gpd
from shapely.geometry import mapping
from era5_regional_stats import compute_regional_stats

NUTS_BOUNDARY_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"
OUTPUT_PATH = "data/earth_observation/climate/final/era5_stats_control_expansion_monthly.json"

EXPANSION_COUNTRIES = ["IS", "AL", "BA", "ME", "MK", "RS"]


def load_expansion_geometries():
    """All 6 new countries already have NUTS_ID geometry in the boundary
    file (no GADM fallback needed - confirmed against the existing
    NUTS_LEVL_0_2024_4326.geojson)."""
    nuts = gpd.read_file(NUTS_BOUNDARY_PATH)
    geometries = []

    for code in EXPANSION_COUNTRIES:
        match = nuts[nuts["NUTS_ID"] == code]
        if match.empty:
            print(f"No NUTS geometry for {code}, skipping.")
            continue
        geometries.append((code, mapping(match.iloc[0]["geometry"])))

    return geometries


def main():
    country_geometries = load_expansion_geometries()
    print(f"Loaded geometries for {len(country_geometries)} expansion countries")

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
