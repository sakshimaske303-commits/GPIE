import os
import requests

GADM_RAW_DIR = "data/earth_observation/boundaries/raw"

# GADM 4.1, country level (level 0), GeoJSON. I use these for the UK, Norway and Switzerland,
# and India for the supplementary transferability test. GADM files may not be redistributed,
# so they are not in the repository and this script fetches them.
GADM_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{iso3}_0.json"
COUNTRIES = ["GBR", "NOR", "CHE", "IND"]


def download_gadm_country(iso3):
    """One GADM level-0 file. Returns the file path, or None."""
    os.makedirs(GADM_RAW_DIR, exist_ok=True)
    filename = f"gadm41_{iso3}_0.json"
    filepath = os.path.join(GADM_RAW_DIR, filename)

    if os.path.exists(filepath):
        print(f"Already exists: {filename}")
        return filepath

    response = requests.get(GADM_URL.format(iso3=iso3), timeout=120)

    if response.status_code != 200:
        print(f"Failed to download {filename} ({response.status_code})")
        return None

    with open(filepath, "wb") as f:
        f.write(response.content)

    print(f"Downloaded: {filename}")
    return filepath


def main():
    for iso3 in COUNTRIES:
        download_gadm_country(iso3)


if __name__ == "__main__":
    main()
