"""GDP acquisition for the expanded control group (World Bank API); Norway
skipped since its GDP data was already clean.
"""
import os
import csv
import requests

OUTPUT_PATH = "data/earth_observation/economy/final/gdp_control_expansion.csv"

COUNTRIES = {
    "ISL": "IS",
    "ALB": "AL",
    "BIH": "BA",
    "MNE": "ME",
    "MKD": "MK",
    "SRB": "RS",
}

WORLD_BANK_URL = "https://api.worldbank.org/v2/country/{code}/indicator/NY.GDP.MKTP.CD"

# Same approximate annual USD/EUR averages used in download_gdp_control_countries.py,
# kept identical for consistency across the control-group GDP series.
USD_TO_EUR_RATE = {
    2019: 1.12,
    2020: 1.14,
    2021: 1.18,
    2022: 1.05,
    2023: 1.08,
    2024: 1.08,
}


def fetch_gdp(iso3_code):
    params = {
        "date": "2019:2024",
        "format": "json",
        "per_page": 100,
    }
    response = requests.get(WORLD_BANK_URL.format(code=iso3_code), params=params)

    if response.status_code != 200:
        print(f"Failed to fetch GDP for {iso3_code}: {response.status_code}")
        return []

    data = response.json()

    if len(data) < 2 or data[1] is None:
        print(f"No data returned for {iso3_code}")
        return []

    return data[1]


def main():
    all_records = []

    for iso3_code, geo_code in COUNTRIES.items():
        print(f"Fetching GDP for {geo_code} ({iso3_code})...")
        records = fetch_gdp(iso3_code)

        for record in records:
            year = int(record["date"])
            value_usd = record["value"]

            if value_usd is None:
                print(f"  {geo_code} {year}: no data available, skipping")
                continue

            if year not in USD_TO_EUR_RATE:
                print(f"  {geo_code} {year}: no exchange rate defined, skipping")
                continue

            value_eur_million = (value_usd / USD_TO_EUR_RATE[year]) / 1_000_000

            all_records.append({
                "geo": geo_code,
                "year": year,
                "gdp_million_eur": round(value_eur_million, 2),
            })
            print(f"  {geo_code} {year}: {round(value_eur_million, 2):,} million EUR")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["geo", "year", "gdp_million_eur"])
        writer.writeheader()
        writer.writerows(all_records)

    print(f"\nSaved: {OUTPUT_PATH}")
    print(f"Total records: {len(all_records)}")


if __name__ == "__main__":
    main()
