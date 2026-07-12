import json
import pandas as pd

# Load all four processed datasets
with open("data/earth_observation/climate/final/era5_stats_by_country_monthly.json") as f:
    climate = pd.DataFrame(json.load(f))

with open("data/earth_observation/land_cover/final/landcover_stats_by_country.json") as f:
    landcover = pd.DataFrame(json.load(f))

with open("data/earth_observation/ndvi/final/ndvi_stats_by_country_monthly.json") as f:
    ndvi_raw = json.load(f)

gdp = pd.read_csv("data/earth_observation/economy/final/gdp_by_country_year.csv")

print("=" * 50)
print("DATASET SHAPES & SAMPLE NUTS_IDs")
print("=" * 50)
print(f"\nClimate: {climate.shape}")
print(climate["NUTS_ID"].unique()[:5])

print(f"\nLand Cover: {landcover.shape}")
print(landcover["NUTS_ID"].unique()[:5])

print(f"\nGDP: {gdp.shape}")
print(gdp["geo"].unique()[:5])

print(f"\nNDVI records: {len(ndvi_raw)}")
print([d["NUTS_ID"] for d in ndvi_raw[:5]])

# Check overlap between climate and landcover NUTS_IDs
climate_ids = set(climate["NUTS_ID"])
landcover_ids = set(landcover["NUTS_ID"])
print(f"\nNUTS_IDs in both climate & landcover: {len(climate_ids & landcover_ids)}")
print(f"In climate only: {climate_ids - landcover_ids}")
print(f"In landcover only: {landcover_ids - climate_ids}")