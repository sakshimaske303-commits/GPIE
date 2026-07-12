import json
import shutil
import pandas as pd
from filter_eu27 import get_eu27_iso2_list

EU27 = set(get_eu27_iso2_list())
CONTROL_GROUP_COUNTRIES = ["UK", "NO", "CH"]


def filter_climate():
    path = "data/earth_observation/climate/final/era5_stats_by_country_monthly.json"
    backup_path = path.replace(".json", "_full.json")

    shutil.copy(path, backup_path)

    with open(path) as f:
        data = json.load(f)

    filtered = [d for d in data if d["NUTS_ID"] in EU27]

    with open(path, "w") as f:
        json.dump(filtered, f, indent=2)

    print(f"Climate: {len(data)} -> {len(filtered)} records (EU-27 only). Backup: {backup_path}")


def filter_landcover():
    path = "data/earth_observation/land_cover/final/landcover_stats_by_country.json"
    backup_path = path.replace(".json", "_full.json")

    shutil.copy(path, backup_path)

    with open(path) as f:
        data = json.load(f)

    filtered = [d for d in data if d["NUTS_ID"] in EU27]

    with open(path, "w") as f:
        json.dump(filtered, f, indent=2)

    print(f"Land Cover: {len(data)} -> {len(filtered)} records (EU-27 only). Backup: {backup_path}")


def filter_gdp():
    path = "data/earth_observation/economy/final/gdp_by_country_year.csv"
    backup_path = path.replace(".csv", "_full.csv")

    shutil.copy(path, backup_path)

    df = pd.read_csv(path)

    filtered = df[df["geo"].isin(EU27)]

    filtered = filtered.rename(columns={"value": "gdp_million_eur"})

    filtered.to_csv(path, index=False)

    print(f"GDP: {len(df)} -> {len(filtered)} records (EU-27, MIO_EUR only). Backup: {backup_path}")


def filter_dem():
    path = "data/earth_observation/dem/final/dem_stats_by_country.json"
    backup_path = path.replace(".json", "_full.json")

    shutil.copy(path, backup_path)

    with open(path) as f:
        data = json.load(f)

    filtered = [d for d in data if d["NUTS_ID"] in EU27]

    with open(path, "w") as f:
        json.dump(filtered, f, indent=2)

    print(f"DEM: {len(data)} -> {len(filtered)} records (EU-27 only). Backup: {backup_path}")


def filter_no2():
    path = "data/earth_observation/no2/final/no2_stats_by_country_monthly.json"
    backup_path = path.replace(".json", "_full.json")

    shutil.copy(path, backup_path)

    with open(path) as f:
        data = json.load(f)

    filtered = [d for d in data if d["NUTS_ID"] in EU27]

    with open(path, "w") as f:
        json.dump(filtered, f, indent=2)

    print(f"NO2: {len(data)} -> {len(filtered)} records (EU-27 only). Backup: {backup_path}")


def filter_climate_all_countries():
    """
    Filters the all-countries (EU-27 + UK/NO/CH) climate file down to
    exactly those 30 countries, excluding other non-EU NUTS entities
    (Turkey, Iceland, Kosovo, etc.) that aren't part of the causal-
    inference control-group design.
    """
    path = "data/earth_observation/climate/final/era5_stats_all_countries_monthly.json"
    backup_path = path.replace(".json", "_full.json")

    with open(path) as f:
        data = json.load(f)

    shutil.copy(path, backup_path)

    valid_countries = EU27 | set(CONTROL_GROUP_COUNTRIES)
    filtered = [r for r in data if r["NUTS_ID"] in valid_countries]

    with open(path, "w") as f:
        json.dump(filtered, f, indent=2)

    print(f"Climate (all countries): {len(data)} -> {len(filtered)} records (EU-27 + control-group). Backup: {backup_path}")


if __name__ == "__main__":
    filter_climate()
    filter_landcover()
    filter_gdp()
    filter_dem()
    filter_no2()
    filter_climate_all_countries()