"""I debug Sentinel Hub 500 "Processing error" replies with small requests that each
change one thing, and print which ones succeed."""
import json
import requests
from auth_sentinelhub import get_sentinelhub_token
from country_boundaries import load_country_geometry
from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT

URL = "https://sh.dataspace.copernicus.eu/api/v1/statistics"
URL_NEW = "https://sh.dataspace.copernicus.eu/statistics/v1"
PROCESS_URLS = ["https://sh.dataspace.copernicus.eu/process/v1", "https://sh.dataspace.copernicus.eu/api/v1/process"]

# The exact evalscript from my first NO2 acquisition.
OLD_NO2 = """
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

ORBIT_NO2 = """
//VERSION=3
function setup() {
  return {
    input: [{ bands: ["NO2", "dataMask"] }],
    output: [
      { id: "no2", bands: 1, sampleType: "FLOAT32" },
      { id: "dataMask", bands: 1 }
    ],
    mosaicking: "ORBIT"
  };
}
function evaluatePixel(samples) {
  let sum = 0, n = 0;
  for (let i = 0; i < samples.length; i++) {
    const s = samples[i];
    if (s.dataMask === 1 && isFinite(s.NO2)) { sum += s.NO2; n++; }
  }
  if (n === 0) { return { no2: [NaN], dataMask: [0] }; }
  return { no2: [sum / n], dataMask: [1] };
}
"""

S2_NDVI = """
//VERSION=3
function setup() {
  return { input: [{ bands: ["B04", "B08", "dataMask"] }],
           output: [{ id: "ndvi", bands: 1, sampleType: "FLOAT32" }, { id: "dataMask", bands: 1 }] };
}
function evaluatePixel(s) {
  return { ndvi: [(s.B08 - s.B04) / (s.B08 + s.B04)], dataMask: [s.dataMask] };
}
"""

VIENNA = {"type": "Polygon", "coordinates": [[[16.2, 48.1], [16.6, 48.1], [16.6, 48.3], [16.2, 48.3], [16.2, 48.1]]]}


def payload(geometry, start, end, evalscript, interval="P1M", s5p=True, timeliness=None, res=None, s2=False):
    tr = {"from": f"{start}T00:00:00Z", "to": f"{end}T00:00:00Z"}
    if s2:
        data = {"type": "sentinel-2-l2a", "dataFilter": {"timeRange": tr}}
    else:
        data = {"type": "sentinel-5p-l2", "dataFilter": {"timeRange": tr}, "processing": {"minQa": 75}}
        if timeliness:
            data["dataFilter"]["timeliness"] = timeliness
    agg = {"timeRange": tr, "aggregationInterval": {"of": interval}, "evalscript": evalscript}
    if res:
        agg["resx"] = res
        agg["resy"] = res
    return {"input": {"bounds": {"geometry": geometry,
                                 "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}},
                      "data": [data]},
            "aggregation": agg}


def run(token, label, body, url=URL):
    r = requests.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                      json=body, timeout=300)
    if r.status_code != 200:
        print(f"[FAIL {r.status_code}] {label}\n      {r.text[:250]}")
        return
    out = r.json()
    d = out.get("data", [])
    first = d[0] if d else {}
    if first.get("error"):
        print(f"[FAIL in-body] {label}\n      {json.dumps(first['error'])[:250]}")
        return
    try:
        st = first["outputs"][list(first["outputs"])[0]]["bands"]["B0"]["stats"]
        print(f"[OK] {label}  mean={st.get('mean')}  sampleCount={st.get('sampleCount')}  noData={st.get('noDataCount')}")
    except Exception:
        print(f"[OK?] {label}  unexpected body: {json.dumps(out)[:250]}")


def main():
    token = get_sentinelhub_token()
    at = load_country_geometry("AT", clip_to_bbox=(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT))

    tests = [
        ("1  OLD method, Austria, Jan 2019 (exactly what worked before)", payload(at, "2019-01-01", "2019-02-01", OLD_NO2)),
        ("2  OLD method, Austria, Jan 2024", payload(at, "2024-01-01", "2024-02-01", OLD_NO2)),
        ("3  OLD method, Austria, Jan 2019, timeliness=OFFL", payload(at, "2019-01-01", "2019-02-01", OLD_NO2, timeliness="OFFL")),
        ("4  OLD method, Austria, Jan 2019, timeliness=RPRO", payload(at, "2019-01-01", "2019-02-01", OLD_NO2, timeliness="RPRO")),
        ("5  OLD method, small Vienna box, Jan 2019", payload(VIENNA, "2019-01-01", "2019-02-01", OLD_NO2)),
        ("6  OLD method, small Vienna box, Jan 2024", payload(VIENNA, "2024-01-01", "2024-02-01", OLD_NO2)),
        ("7  DAILY (P1D), Vienna box, 1-7 Jan 2024", payload(VIENNA, "2024-01-01", "2024-01-08", OLD_NO2, interval="P1D")),
        ("8  ORBIT, Vienna box, Jan 2024", payload(VIENNA, "2024-01-01", "2024-02-01", ORBIT_NO2)),
        ("9  ORBIT, Vienna box, Jan 2024, timeliness=OFFL", payload(VIENNA, "2024-01-01", "2024-02-01", ORBIT_NO2, timeliness="OFFL")),
        ("10 ORBIT, Austria, Jan 2024, timeliness=OFFL, 0.05 deg grid", payload(at, "2024-01-01", "2024-02-01", ORBIT_NO2, timeliness="OFFL", res=0.05)),
        ("11 Account check: Sentinel-2 NDVI, Vienna box, Jan 2024", payload(VIENNA, "2024-01-01", "2024-02-01", S2_NDVI, s2=True, res=0.001)),
    ]
    for label, body in tests:
        try:
            run(token, label, body)
        except requests.RequestException as e:
            print(f"[NETWORK ERROR] {label}: {e}")

    # The newer Statistical API path.
    try:
        run(token, "12 NEW path /statistics/v1: DAILY, Vienna box, 1-7 Jan 2024",
            payload(VIENNA, "2024-01-01", "2024-01-08", OLD_NO2, interval="P1D"), url=URL_NEW)
    except requests.RequestException as e:
        print(f"[NETWORK ERROR] 12: {e}")

    # One Process API image request tells me if S5P itself is down or only the Statistical API.
    proc = {
        "input": {"bounds": {"bbox": [16.2, 48.1, 16.6, 48.3],
                             "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}},
                  "data": [{"type": "sentinel-5p-l2",
                            "dataFilter": {"timeRange": {"from": "2024-01-15T00:00:00Z", "to": "2024-01-16T00:00:00Z"}}}]},
        "output": {"width": 16, "height": 16, "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]},
        "evalscript": """//VERSION=3
function setup(){return {input:["NO2","dataMask"], output:{bands:1, sampleType:"FLOAT32"}};}
function evaluatePixel(s){return [s.NO2];}""",
    }
    for i, purl in enumerate(PROCESS_URLS, start=13):
        try:
            r = requests.post(purl, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                              json=proc, timeout=300)
            ok = "OK" if r.status_code == 200 else f"FAIL {r.status_code}"
            print(f"[{ok}] {i} Process API {purl.split('.eu')[1]}: S5P NO2 image, Vienna, 15 Jan 2024"
                  + ("" if r.status_code == 200 else f"\n      {r.text[:250]}"))
        except requests.RequestException as e:
            print(f"[NETWORK ERROR] {i}: {e}")


if __name__ == "__main__":
    main()
