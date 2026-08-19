"""NO2 acquisition for the expanded control group (Iceland, Albania, Bosnia
and Herzegovina, Montenegro, North Macedonia, Serbia) plus a Norway
re-fetch to fix its coverage gap.
"""
import os
import json
import time
import requests
from auth_sentinelhub import get_sentinelhub_token
from country_boundaries import load_country_geometry
from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT

STATISTICAL_API_URL = "https://sh.dataspace.copernicus.eu/api/v1/statistics"
OUTPUT_DIR = "data/earth_observation/no2/final"

# New non-EU control candidates + Norway (re-fetched clean to fix its gap)
EXPANSION_COUNTRIES = ["IS", "AL", "BA", "ME", "MK", "RS", "NO"]


def request_no2_stats(access_token, country_code, geometry, year):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    evalscript = """
    //VERSION=3
    function setup() {
      return {
        input: [{ bands: ["NO2", "dataMask"] }],
        output: [
          { id: "no2", bands: 1, sampleType: "FLOAT32" },
          { id: "dataMask", bands: 1 }
        ]
      };
    }
    function evaluatePixel(sample) {
      return { no2: [sample.NO2], dataMask: [sample.dataMask] };
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
                    "type": "sentinel-5p-l2",
                    "dataFilter": {
                        "timeRange": {
                            "from": f"{year}-01-01T00:00:00Z",
                            "to": f"{year + 1}-01-01T00:00:00Z",
                        }
                    },
                    "processing": {
                        "minQa": 75
                    }
                }
            ],
        },
        "aggregation": {
            "timeRange": {
                "from": f"{year}-01-01T00:00:00Z",
                "to": f"{year + 1}-01-01T00:00:00Z",
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
        geometry = load_country_geometry(
            country_code,
            clip_to_bbox=(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)
        )
        if geometry is None:
            print(f"No geometry for {country_code}, skipping.")
            continue

        for year in range(2019, 2025):
            print(f"Requesting NO2 stats: {country_code}, {year}")
            result = request_no2_stats(access_token, country_code, geometry, year)
            if result:
                all_results.append({"NUTS_ID": country_code, "year": year, "data": result})
            time.sleep(1)

    output_path = os.path.join(OUTPUT_DIR, "no2_stats_control_expansion.json")
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nSaved: {output_path}")
    print(f"Total records: {len(all_results)}")


if __name__ == "__main__":
    main()
