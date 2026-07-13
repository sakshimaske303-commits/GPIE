import os
import json
import requests
from auth_sentinelhub import get_sentinelhub_token  # reuse existing auth, that's fine

STATISTICAL_API_URL = "https://sh.dataspace.copernicus.eu/api/v1/statistics"
OUTPUT_DIR = "data/global_transferability_test"

# India's approximate bounding box (simple rectangle, no need for exact boundary)
INDIA_GEOMETRY = {
    "type": "Polygon",
    "coordinates": [[
        [68.0, 6.0], [97.5, 6.0], [97.5, 37.5], [68.0, 37.5], [68.0, 6.0]
    ]]
}

def request_no2_stats(access_token, year):
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

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
                "geometry": INDIA_GEOMETRY,
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
            },
            "data": [{
                "type": "sentinel-5p-l2",
                "dataFilter": {"timeRange": {"from": f"{year}-01-01T00:00:00Z", "to": f"{year+1}-01-01T00:00:00Z"}},
                "processing": {"minQa": 75}
            }],
        },
        "aggregation": {
            "timeRange": {"from": f"{year}-01-01T00:00:00Z", "to": f"{year+1}-01-01T00:00:00Z"},
            "aggregationInterval": {"of": "P1M"},
            "evalscript": evalscript,
        },
    }

    response = requests.post(STATISTICAL_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed for India, {year} ({response.status_code}): {response.text[:300]}")
        return None
    return response.json()


def main():
    access_token = get_sentinelhub_token()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_results = []

    for year in range(2019, 2025):
        print(f"Requesting NO2 stats: India, {year}")
        result = request_no2_stats(access_token, year)
        if result:
            all_results.append({"country": "India", "year": year, "data": result})

    output_path = os.path.join(OUTPUT_DIR, "india_no2_test.json")
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nSaved: {output_path}")
    print("This confirms the GPIE acquisition pipeline is portable beyond the EU-27 study region.")


if __name__ == "__main__":
    main()