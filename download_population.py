import os
import requests
from get_eu_country_list import get_eu_country_codes

POP_RAW_DIR = "data/earth_observation/population/raw"

# Verified WorldPop REST API pattern (Global 1 dataset: 2000-2020)
REST_API_URL = "https://www.worldpop.org/rest/data/pop/wpgp"


def get_download_url(iso3, year):
    """
    Queries the WorldPop REST API for a country's population file URL.
    Returns the https download URL, or None if not found.
    """
    try:
        response = requests.get(REST_API_URL, params={"iso3": iso3}, timeout=30)
        if response.status_code != 200:
            return None

        data = response.json()
        for entry in data.get("data", []):
            if str(year) in entry.get("title", ""):
                ftp_url = entry["files"][0]
                # Convert ftp:// to https:// (WorldPop mirrors both)
                https_url = ftp_url.replace(
                    "ftp://ftp.worldpop.org.uk",
                    "https://data.worldpop.org"
                )
                return https_url
        return None
    except Exception as e:
        print(f"Error querying metadata for {iso3} {year}: {e}")
        return None


def download_country_population(iso3, year):
    """
    Downloads one country's population GeoTIFF for a given year.
    Skips if already downloaded. Returns True on success.
    """
    os.makedirs(POP_RAW_DIR, exist_ok=True)
    filename = f"{iso3.lower()}_ppp_{year}.tif"
    filepath = os.path.join(POP_RAW_DIR, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print(f"Skipping (already exists): {filename}")
        return True

    url = get_download_url(iso3, year)
    if url is None:
        print(f"Error: URL not found for {iso3} in year {year}")
        return False

    try:
        response = requests.get(url, stream=True, timeout=180)
        if response.status_code != 200:
            print(f"Failed ({response.status_code}): {filename}")
            return False

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"Downloaded successfully: {filename}")
        return True

    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False


def download_all_eu_population(years):
    """
    Downloads population data for all 27 EU countries for the verified years.
    """
    countries = get_eu_country_codes()
    total = len(countries) * len(years)
    done = 0

    for year in years:
        for iso3 in countries:
            done += 1
            print(f"[{done}/{total}] Ingesting: {iso3} - Year: {year}")
            download_country_population(iso3, year)

    print("\nVerified Population Data Ingestion Step Complete.")


def main():
    # Only executing for verified, scientifically reliable years.
    # 2021-2024 data allocation is explicitly left as an open task for future HDX/STAC integration.
    verified_years = [2019, 2020]
    download_all_eu_population(years=verified_years)


if __name__ == "__main__":
    main()