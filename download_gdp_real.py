import csv
import os

import requests

OUTPUT_PATH = "data/earth_observation/economy/final/gdp_per_capita_real.csv"

# One source for all 36 countries, so EU and comparison countries are measured the same way.
# NY.GDP.PCAP.PP.KD: GDP per capita, PPP, constant 2021 international $ (my main real measure)
# NY.GDP.PCAP.KD:    GDP per capita, constant 2015 US$ (a second real measure, as a check)
INDICATORS = {"NY.GDP.PCAP.PP.KD": "gdp_pc_ppp_const", "NY.GDP.PCAP.KD": "gdp_pc_const_usd"}
WORLD_BANK_URL = "https://api.worldbank.org/v2/country/{codes}/indicator/{indicator}"

# My two-letter codes (Eurostat style: EL for Greece, UK for the United Kingdom) -> ISO3
ISO3 = {"AT": "AUT", "BE": "BEL", "BG": "BGR", "HR": "HRV", "CY": "CYP", "CZ": "CZE", "DK": "DNK",
        "EE": "EST", "FI": "FIN", "FR": "FRA", "DE": "DEU", "EL": "GRC", "HU": "HUN", "IE": "IRL",
        "IT": "ITA", "LV": "LVA", "LT": "LTU", "LU": "LUX", "MT": "MLT", "NL": "NLD", "PL": "POL",
        "PT": "PRT", "RO": "ROU", "SK": "SVK", "SI": "SVN", "ES": "ESP", "SE": "SWE", "UK": "GBR",
        "NO": "NOR", "CH": "CHE", "IS": "ISL", "AL": "ALB", "BA": "BIH", "ME": "MNE", "MK": "MKD",
        "RS": "SRB"}
YEARS = range(2019, 2025)


def fetch(indicator):
    params = {"date": f"{YEARS[0]}:{YEARS[-1]}", "format": "json", "per_page": 1000}
    url = WORLD_BANK_URL.format(codes=";".join(ISO3.values()), indicator=indicator)
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    if len(data) < 2 or data[1] is None:
        raise RuntimeError(f"No data returned for {indicator}: {data[0]}")
    return data[1]


def main():
    back = {v: k for k, v in ISO3.items()}
    table = {(geo, year): {} for geo in ISO3 for year in YEARS}
    for indicator, column in INDICATORS.items():
        for record in fetch(indicator):
            geo, year = back.get(record["countryiso3code"]), int(record["date"])
            if geo is not None and year in YEARS:
                table[(geo, year)][column] = record["value"]

    missing = [(g, y, c) for (g, y), v in table.items() for c in INDICATORS.values() if v.get(c) is None]
    for g, y, c in missing:
        print(f"  missing: {g} {y} {c}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["geo", "year"] + list(INDICATORS.values()))
        writer.writeheader()
        for (geo, year), values in sorted(table.items()):
            writer.writerow({"geo": geo, "year": year, **values})

    print(f"Saved: {OUTPUT_PATH} ({len(table)} country-years, {len(missing)} missing values)")


if __name__ == "__main__":
    main()
