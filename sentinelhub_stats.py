"""Sentinel Hub Statistical API helpers. I use them for monthly NDVI country means."""
import json
import time
import requests

# CDSE moved the endpoints from /api/v1/<service> to /<service>/v1, so I try both paths.
STATISTICAL_API_URLS = [
    "https://sh.dataspace.copernicus.eu/statistics/v1",
    "https://sh.dataspace.copernicus.eu/api/v1/statistics",
]
STATISTICAL_API_URL = STATISTICAL_API_URLS[0]

# CGLS NDVI 300 m BYOC collection
NDVI_BYOC_COLLECTION_ID = "6303088f-3c19-4967-9038-119267c6d090"

# I set the grid in degrees. Without it the API uses 256 x 256 px per country bbox,
# which gives every country a different resolution.
NO2_RES_DEG = 0.05    # ~5 km, close to TROPOMI's 3.5 x 5.5 km pixel
NDVI_RES_DEG = 0.02   # ~2 km; NDVI source is 300 m, country means only

NO2_EVALSCRIPT_MONTHLY_MEAN = """
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

NDVI_EVALSCRIPT_MONTHLY_MEAN = """
//VERSION=3
function setup() {
  return {
    input: [{ bands: ["NDVI", "dataMask"] }],
    output: [
      { id: "ndvi", bands: 1, sampleType: "FLOAT32" },
      { id: "dataMask", bands: 1 }
    ],
    mosaicking: "ORBIT"
  };
}
function evaluatePixel(samples) {
  // CGLS NDVI digital numbers: 0-250 valid, 251-255 flags
  // (252 unknown, 253 snow, 254 water, 255 missing) -> excluded.
  let sum = 0, n = 0;
  for (let i = 0; i < samples.length; i++) {
    const s = samples[i];
    if (s.dataMask === 1 && s.NDVI <= 250) { sum += (s.NDVI * 0.004) - 0.08; n++; }
  }
  if (n === 0) { return { ndvi: [NaN], dataMask: [0] }; }
  return { ndvi: [sum / n], dataMask: [1] };
}
"""


SIMPLE_EVALSCRIPTS = {
    # One mosaic per interval. I only use these with daily intervals.
    "no2": """
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
""",
    "ndvi": """
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
  if (sample.NDVI > 250) { return { ndvi: [NaN], dataMask: [0] }; }
  return { ndvi: [(sample.NDVI * 0.004) - 0.08], dataMask: [sample.dataMask] };
}
""",
}
ORBIT_EVALSCRIPTS = {"no2": NO2_EVALSCRIPT_MONTHLY_MEAN, "ndvi": NDVI_EVALSCRIPT_MONTHLY_MEAN}
RES_DEG = {"no2": NO2_RES_DEG, "ndvi": NDVI_RES_DEG}


def _range(start, end):
    return {"from": f"{start}T00:00:00Z", "to": f"{end}T00:00:00Z"}


def _year_range(year):
    # Half-open interval: I end at Jan 1 of the next year so December is kept.
    return _range(f"{year}-01-01", f"{year + 1}-01-01")


def _month_starts(year):
    return [f"{year}-{m:02d}-01" for m in range(1, 13)] + [f"{year + 1}-01-01"]


def _payload(geometry, time_range, variable, method, use_res):
    """method is 'ORBIT' (per-pixel monthly mean, P1M) or 'DAILY' (one SIMPLE mosaic per day, P1D)."""
    if variable == "no2":
        data = {"type": "sentinel-5p-l2", "dataFilter": {"timeRange": time_range},
                "processing": {"minQa": 75}}  # ESA recommends qa_value >= 0.75
    elif variable == "ndvi":
        data = {"type": "byoc-" + NDVI_BYOC_COLLECTION_ID, "dataFilter": {"timeRange": time_range}}
    else:
        raise ValueError(variable)
    aggregation = {
        "timeRange": time_range,
        "aggregationInterval": {"of": "P1M" if method == "ORBIT" else "P1D"},
        "evalscript": ORBIT_EVALSCRIPTS[variable] if method == "ORBIT" else SIMPLE_EVALSCRIPTS[variable],
    }
    if use_res:
        aggregation["resx"] = RES_DEG[variable]
        aggregation["resy"] = RES_DEG[variable]
    return {
        "input": {
            "bounds": {"geometry": geometry,
                       "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}},
            "data": [data],
        },
        "aggregation": aggregation,
    }


def _post(access_token, payload, retries=3, verbose=True):
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    last = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(STATISTICAL_API_URL, headers=headers, json=payload, timeout=600)
        except requests.RequestException as e:
            last = str(e)
            if verbose:
                print(f"  attempt {attempt} network error: {e}")
            time.sleep(5 * attempt)
            continue
        if r.status_code == 200:
            body = r.json()
            # The Statistical API can return HTTP 200 with per-interval errors.
            errs = [d.get("error") for d in body.get("data", []) if d.get("error")]
            if errs and len(errs) == len(body.get("data", [])):
                last = f"all intervals errored: {str(errs[0])[:200]}"
            else:
                return body, None
        else:
            last = f"{r.status_code}: {r.text[:300]}"
        if verbose:
            print(f"  attempt {attempt} failed ({last})")
        time.sleep(5 * attempt)
    return None, last


def _band_stats(entry, variable):
    try:
        return entry["outputs"][variable]["bands"]["B0"]["stats"]
    except (KeyError, TypeError):
        return None


def aggregate_daily_to_monthly(daily_body, year, variable):
    """Monthly mean = sum(daily mean * valid pixels) / sum(valid pixels), in the P1M response shape."""
    import math
    months = {m: {"sum": 0.0, "valid": 0, "samples": 0, "days": 0} for m in range(1, 13)}
    for entry in daily_body.get("data", []):
        start = entry["interval"]["from"]
        if int(start[:4]) != year:
            continue
        m = int(start[5:7])
        st = _band_stats(entry, variable)
        if not st:
            continue
        sample = st.get("sampleCount") or 0
        valid = sample - (st.get("noDataCount") or 0)
        mean = st.get("mean")
        try:
            mean = float(mean)
        except (TypeError, ValueError):
            continue
        if valid <= 0 or math.isnan(mean):
            continue
        months[m]["sum"] += mean * valid
        months[m]["valid"] += valid
        months[m]["samples"] += sample
        months[m]["days"] += 1
    starts = _month_starts(year)
    out = []
    for m in range(1, 13):
        v = months[m]
        mean = v["sum"] / v["valid"] if v["valid"] else None
        out.append({
            "interval": {"from": f"{starts[m - 1]}T00:00:00Z", "to": f"{starts[m]}T00:00:00Z"},
            "outputs": {variable: {"bands": {"B0": {"stats": {
                "mean": mean,
                "validPixelDays": v["valid"],
                "daysWithData": v["days"],
                "sampleCount": v["samples"],
                "noDataCount": v["samples"] - v["valid"],
            }}}}},
        })
    return {"data": out, "status": "OK", "aggregationMethod": "daily SIMPLE mosaics pooled to monthly means"}


# Method selection. I prefer ORBIT, but Sentinel Hub can reject it with a 500 error.
# I probe once and use the same method for the whole run, so methods are never mixed.
_CHOSEN = {}

# For NDVI I try ORBIT with monthly intervals first, then DAILY.
# I get NO2 from the Process API (s5p_process_daily.py), not from here.
CANDIDATES = {
    "no2": [("DAILY", True), ("DAILY", False)],
    "ndvi": [("ORBIT", True), ("ORBIT", False), ("DAILY", True), ("DAILY", False)],
}


def choose_method(access_token, geometry, variable, probe_year=2019):
    global STATISTICAL_API_URL
    if variable in _CHOSEN:
        return _CHOSEN[variable]
    print(f"\nProbing Sentinel Hub for {variable} (January {probe_year}, one country)...")
    for url in STATISTICAL_API_URLS:
      STATISTICAL_API_URL = url
      for method, use_res in CANDIDATES[variable]:
        # A P1M request only returns complete months, so I probe ORBIT on a whole month.
        tr = (_range(f"{probe_year}-01-01", f"{probe_year}-02-01") if method == "ORBIT"
              else _range(f"{probe_year}-01-01", f"{probe_year}-01-08"))
        body, err = _post(access_token, _payload(geometry, tr, variable, method, use_res), retries=1, verbose=False)
        label = f"{method}{' + explicit grid' if use_res else ' (default grid)'} @ {url.split('.eu')[1]}"
        if body is None:
            print(f"  {label}: FAILED ({err[:120]})")
            continue
        if method == "DAILY":
            body = aggregate_daily_to_monthly(body, probe_year, variable)
        entries = body.get("data") or []
        st = (_band_stats(entries[0], variable) or {}) if entries else {}
        mean = st.get("mean")
        try:
            ok = mean is not None and float(mean) == float(mean)  # not None / not NaN
        except (TypeError, ValueError):
            ok = False
        if not ok:
            print(f"  {label}: no usable value returned ({json.dumps(body)[:150]})")
            continue
        print(f"  {label}: OK  (Jan {probe_year} probe mean = {mean})")
        _CHOSEN[variable] = (method, use_res)
        print(f"Using {label} for every request in this run.\n")
        return _CHOSEN[variable]
    raise RuntimeError("No Sentinel Hub method worked for the probe request - send the output above for debugging.")


def request_monthly_stats(access_token, geometry, year, variable, retries=3):
    """Monthly statistics for one country-year, with the method picked by choose_method()."""
    method, use_res = choose_method(access_token, geometry, variable)
    if method == "ORBIT":
        body, err = _post(access_token, _payload(geometry, _year_range(year), variable, method, use_res), retries)
        if body is not None:
            body["aggregationMethod"] = "ORBIT mosaicking, per-pixel monthly mean"
        return body
    # DAILY: I try the whole year in one request, then fall back to month by month.
    body, err = _post(access_token, _payload(geometry, _year_range(year), variable, method, use_res), retries=1)
    if body is None:
        starts = _month_starts(year)
        merged = {"data": []}
        for m in range(12):
            part, err = _post(access_token, _payload(geometry, _range(starts[m], starts[m + 1]), variable,
                                                     method, use_res), retries)
            if part is None:
                print(f"  month {m + 1} failed: {err}")
                return None
            merged["data"].extend(part.get("data", []))
            time.sleep(0.5)
        body = merged
    return aggregate_daily_to_monthly(body, year, variable)
