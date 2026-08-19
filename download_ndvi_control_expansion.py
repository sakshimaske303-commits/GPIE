"""NDVI acquisition for the expanded control group plus a clean Norway
re-fetch, same pattern as download_ndvi_sentinelhub.py.
"""
import os
import json
import time
import requests
from auth_sentinelhub import get_sentinelhub_token
from country_boundaries import load_country_geometry
from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT

STATISTICAL_API_URL = "https://sh.dataspace.copernicus.eu/api/v1/statistics"
BYOC_COLLECTION_ID = "6303088f-3c19-4967-9038-119267c6d090"
OUTPUT_DIR = "data/earth_observation/ndvi/final"

EXPANSION_COUNTRIES = ["IS", "AL", "BA", "ME", "MK", "RS", "NO"]


def request_ndvi_stats(access_token, country_code, geometry, year):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    evalscript = """
    //VERSION=3
    function setup() {
      return {
        input: [{ bands: ["NDVI", "dataMask"] }],
        output: [
          { id: "ndvi", bands: 1, sampleType: "FLOAT32" },
          { id: "dataMask", bands: 1 }
        ]
      };
    }
    function evaluatePixel(sample) {
      let dn = sample.NDVI;
      if (dn > 250) {
        // 252=unknown, 253=snow, 254=water, 255=missing - exclude these
        return { ndvi: [NaN], dataMask: [0] };
      }
      let realNdvi = (dn * 0.004) - 0.08;
      return { ndvi: [realNdvi], dataMask: [sample.dataMask] };
    }
    """

    payload = {
        "input": {
            "bounds": {
                "geometry": geometry,
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
            },
            "data": [
                {
                    "type": "byoc-" + BYOC_COLLECTION_ID,
                    "dataFilter": {
                        "timeRange": {
                            "from": f"{year}-01-01T00:00:00Z",
                            "to": f"{year + 1}-01-01T00:00:00Z"
                        }
                    },
                }
            ],
        },
        "aggregation": {
            "timeRange": {
                "from": f"{year}-01-01T00:00:00Z",
                "to": f"{year + 1}-01-01T00:00:00Z"
            },
            "aggregationInterval": {"of": "P1M"},
            "evalscript": evalscript,
        },
    }

    response = requests.post(STATISTICAL_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"Failed for {country_code}, {year} ({response.status_code}): {response.text[:300]}")
        return None

    return response.json()


def main():
    access_token = get_sentinelhub_token()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_results = []

    for country_code in EXPANSION_COUNTRIES:
        geometry = load_country_geometry(country_code, clip_to_bbox=(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT))
        if geometry is None:
            print(f"No geometry found for {country_code}, skipping.")
            continue

        for year in range(2019, 2025):
            print(f"Requesting NDVI stats: {country_code}, {year}")
            result = request_ndvi_stats(access_token, country_code, geometry, year)
            if result:
                all_results.append({"NUTS_ID": country_code, "year": year, "data": result})
            time.sleep(1)

    output_path = os.path.join(OUTPUT_DIR, "ndvi_stats_control_expansion.json")
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nSaved: {output_path}")
    print(f"Total records: {len(all_results)}")


if __name__ == "__main__":
    main()
