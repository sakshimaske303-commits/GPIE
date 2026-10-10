import os
import requests

NUTS_RAW_DIR = "data/earth_observation/boundaries/raw"

# GISCO public API, no login needed.
# NUTS 2024, country level (LEVL_0), 1:20M resolution, EPSG:4326.
NUTS_URL = (
    "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/"
    "NUTS_RG_20M_2024_4326_LEVL_0.geojson"
)

NUTS_FILENAME = "NUTS_LEVL_0_2024_4326.geojson"


def download_nuts_country_boundaries():
    """Country-level NUTS boundaries as one GeoJSON file. Returns the file path, or None."""
    os.makedirs(NUTS_RAW_DIR, exist_ok=True)
    filepath = os.path.join(NUTS_RAW_DIR, NUTS_FILENAME)

    if os.path.exists(filepath):
        print(f"Already exists: {NUTS_FILENAME}")
        return filepath

    response = requests.get(NUTS_URL, timeout=60)

    if response.status_code != 200:
        print(f"Failed to download NUTS boundaries ({response.status_code})")
        return None

    with open(filepath, "wb") as f:
        f.write(response.content)

    print(f"Downloaded: {NUTS_FILENAME}")
    return filepath


def main():
    download_nuts_country_boundaries()


if __name__ == "__main__":
    main()