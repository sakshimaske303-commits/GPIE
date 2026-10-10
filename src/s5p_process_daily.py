"""I pull one NO2 raster per day from the Process API and pool them into monthly country means."""
import io
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

import numpy as np
import requests

PROCESS_URLS = [
    "https://sh.dataspace.copernicus.eu/process/v1",
    "https://sh.dataspace.copernicus.eu/api/v1/process",
]

EVALSCRIPT = """//VERSION=3
function setup() {
  return {
    input: [{ bands: ["NO2", "dataMask"] }],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(s) {
  if (s.dataMask === 0) { return [NaN]; }
  return [s.NO2];
}
"""

RES_DEG = 0.1
START = date(2019, 1, 1)
END = date(2024, 12, 31)


class TokenManager:
    """CDSE tokens expire after a few minutes, so I refresh them early."""

    def __init__(self, get_token, max_age_s=240):
        self._get = get_token
        self._max_age = max_age_s
        self._lock = threading.Lock()
        self._token, self._t = None, 0.0

    def get(self, force=False):
        with self._lock:
            if force or self._token is None or time.time() - self._t > self._max_age:
                self._token, self._t = self._get(), time.time()
            return self._token


def grid_shape(bbox, res=RES_DEG):
    min_lon, min_lat, max_lon, max_lat = bbox
    return int(round((max_lon - min_lon) / res)), int(round((max_lat - min_lat) / res))


def build_masks(bbox, geometries, res=RES_DEG):
    """One boolean pixel mask per country on the request grid."""
    from rasterio.features import geometry_mask
    from rasterio.transform import from_bounds
    width, height = grid_shape(bbox, res)
    transform = from_bounds(*bbox, width, height)
    masks = {}
    for code, geom in geometries.items():
        m = ~geometry_mask([geom], out_shape=(height, width), transform=transform, all_touched=False)
        if not m.any():  # very small country: I fall back to all-touched pixels
            m = ~geometry_mask([geom], out_shape=(height, width), transform=transform, all_touched=True)
        masks[code] = m
    return masks


def request_day(tokens, bbox, day, res=RES_DEG, retries=4, timeliness=None):
    """One day of NO2 as an array. timeliness is None, "RPRO", "OFFL" or "NRTI"."""
    width, height = grid_shape(bbox, res)
    nxt = day + timedelta(days=1)
    payload = {
        "input": {
            "bounds": {"bbox": list(bbox), "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}},
            "data": [{
                "type": "sentinel-5p-l2",
                "dataFilter": {"timeRange": {"from": f"{day.isoformat()}T00:00:00Z",
                                             "to": f"{nxt.isoformat()}T00:00:00Z"}},
                "processing": {"minQa": 75},
            }],
        },
        "output": {"width": width, "height": height,
                   "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]},
        "evalscript": EVALSCRIPT,
    }
    if timeliness:
        payload["input"]["data"][0]["dataFilter"]["timeliness"] = timeliness
    last = None
    for attempt in range(1, retries + 1):
        url = PROCESS_URLS[(attempt - 1) % len(PROCESS_URLS)]
        try:
            r = requests.post(url, headers={"Authorization": f"Bearer {tokens.get()}",
                                            "Content-Type": "application/json",
                                            "Accept": "image/tiff"},
                              json=payload, timeout=300)
        except requests.RequestException as e:
            last = str(e)
            time.sleep(5 * attempt)
            continue
        if r.status_code == 200:
            import rasterio
            with rasterio.MemoryFile(io.BytesIO(r.content)) as mem, mem.open() as src:
                return src.read(1).astype("float64"), None
        if r.status_code == 401:
            tokens.get(force=True)
        last = f"{r.status_code}: {r.text[:200]}"
        time.sleep(10 * attempt if r.status_code == 429 else 3 * attempt)
    return None, last


def _done_days(log_path):
    done = set()
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                try:
                    done.add(json.loads(line)["date"])
                except Exception:
                    pass
    return done


def run_daily(get_token, bbox, geometries, log_path, res=RES_DEG, workers=4, start=START, end=END):
    """Fetch each day once and append per-country sums and counts to the log."""
    masks = build_masks(bbox, geometries, res)
    print(f"Grid {grid_shape(bbox, res)} px at {res} deg; pixels per country: "
          + ", ".join(f"{c}={int(m.sum())}" for c, m in masks.items()))
    tokens = TokenManager(get_token)
    done = _done_days(log_path)
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    todo = [d for d in days if d.isoformat() not in done]
    print(f"{len(days)} days total, {len(done)} already done, {len(todo)} to fetch")
    lock = threading.Lock()
    failures = []

    def work(day):
        arr, err = request_day(tokens, bbox, day, res)
        if arr is None:
            return day, None, err
        rec = {"date": day.isoformat(), "countries": {}}
        valid_all = np.isfinite(arr)
        for code, m in masks.items():
            sel = m & valid_all
            n = int(sel.sum())
            rec["countries"][code] = {"sum": float(arr[sel].sum()) if n else 0.0,
                                      "valid": n, "pixels": int(m.sum())}
        return day, rec, None

    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    with ThreadPoolExecutor(max_workers=workers) as ex, open(log_path, "a", encoding="utf-8") as log:
        futures = [ex.submit(work, d) for d in todo]
        for i, fut in enumerate(as_completed(futures), start=1):
            day, rec, err = fut.result()
            if rec is None:
                failures.append((day.isoformat(), err))
                print(f"  {day} FAILED: {err}")
                continue
            with lock:
                log.write(json.dumps(rec) + "\n")
                log.flush()
            if i % 50 == 0 or i == len(futures):
                print(f"  {i}/{len(futures)} days fetched")
    if failures:
        print(f"\n{len(failures)} days failed. A second run fetches only the missing days.")
    return failures


def monthly_from_log(log_path, codes, variable="no2", start=START, end=END):
    """Monthly means from the daily log, in the same shape as a Statistical API P1M response."""
    acc = {}
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            y, m = int(rec["date"][:4]), int(rec["date"][5:7])
            for code, v in rec["countries"].items():
                a = acc.setdefault((code, y, m), {"sum": 0.0, "valid": 0, "pixels": 0, "days": 0})
                a["sum"] += v["sum"]
                a["valid"] += v["valid"]
                a["pixels"] += v["pixels"]
                a["days"] += 1 if v["valid"] > 0 else 0
    out = []
    for code in codes:
        for y in range(start.year, end.year + 1):
            entries = []
            for m in range(1, 13):
                a = acc.get((code, y, m), {"sum": 0.0, "valid": 0, "pixels": 0, "days": 0})
                nxt = f"{y + (m == 12)}-{(m % 12) + 1:02d}-01"
                entries.append({
                    "interval": {"from": f"{y}-{m:02d}-01T00:00:00Z", "to": f"{nxt}T00:00:00Z"},
                    "outputs": {variable: {"bands": {"B0": {"stats": {
                        "mean": a["sum"] / a["valid"] if a["valid"] else None,
                        "validPixelDays": a["valid"],
                        "daysWithData": a["days"],
                        "sampleCount": a["pixels"],
                        "noDataCount": a["pixels"] - a["valid"],
                    }}}}},
                })
            out.append({"NUTS_ID": code, "year": y,
                        "data": {"data": entries, "status": "OK",
                                 "aggregationMethod": f"Process API daily FLOAT32 rasters at {RES_DEG} deg, "
                                                      "pooled valid pixel-days per month (minQa 75)"}})
    return out
