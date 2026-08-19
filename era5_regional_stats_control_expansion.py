"""Climate stats for the expanded control group via the existing ERA5 grid
files (Iceland/Balkans already fall inside the same bbox).
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
