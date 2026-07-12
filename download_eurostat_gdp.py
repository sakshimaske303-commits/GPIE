import os
import json
import requests

EUROSTAT_RAW_DIR = "data/earth_observation/economy/raw"

# Verified Eurostat REST API (Statistics API, JSON-stat format)
EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

# Regional GDP at NUTS 2 level (verified dataset code)
GDP_DATASET_CODE = "nama_10r_2gdp"


def download_regional_gdp(start_year=2019, end_year=2024):
    """
    Downloads the full regional GDP dataset (NUTS 2 level) from Eurostat,
    filtered to the study period, as JSON-stat format.
    Returns the filepath on success, None on failure.
    """
    os.makedirs(EUROSTAT_RAW_DIR, exist_ok=True)
    filename = f"{GDP_DATASET_CODE}_{start_year}_{end_year}.json"
    filepath = os.path.join(EUROSTAT_RAW_DIR, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print(f"Skipping (already exists): {filename}")
        return filepath

    url = f"{EUROSTAT_BASE_URL}/{GDP_DATASET_CODE}"

    params = {
        "format": "JSON",
        "lang": "EN",
        "sinceTimePeriod": start_year,
        "untilTimePeriod": end_year,
    }

    try:
        response = requests.get(url, params=params, timeout=60)

        if response.status_code != 200:
            print(f"Failed to download GDP dataset (HTTP {response.status_code})")
            return None

        data = response.json()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)

        print(f"Downloaded successfully: {filename}")
        return filepath

    except Exception as e:
        print(f"Error downloading GDP dataset: {e}")
        return None


def main():
    download_regional_gdp(start_year=2019, end_year=2024)


if __name__ == "__main__":
    main()