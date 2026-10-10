"""I keep every daily 0.1 deg NO2 raster, so I can see where inside a country NO2 changed.
I then build monthly pixel sums and check them against my country monthly means."""
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

import numpy as np

from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT
from s5p_process_daily import END, RES_DEG, START, TokenManager, build_masks, grid_shape, request_day

BBOX = (MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)
GRID_DIR = "data/earth_observation/no2/gridded"
DAY_DIR = os.path.join(GRID_DIR, "daily")
MONTHLY_PATH = os.path.join(GRID_DIR, "no2_grid_monthly.npz")
META_PATH = os.path.join(GRID_DIR, "no2_grid_meta.json")
MASTER_PATH = "data/master_dataset_control.csv"


def all_days(start=START, end=END):
    return [start + timedelta(days=i) for i in range((end - start).days + 1)]


def day_path(day):
    return os.path.join(DAY_DIR, f"{day.isoformat()}.npz")


def save_day(day, arr):
    """Atomic write, so a stopped run never leaves a half-written file behind."""
    tmp = day_path(day) + ".tmp.npz"
    np.savez_compressed(tmp, no2=arr.astype("float32"))
    os.replace(tmp, day_path(day))


def load_day(day):
    with np.load(day_path(day)) as z:
        return z["no2"]


def download(get_token, workers=4):
    os.makedirs(DAY_DIR, exist_ok=True)
    days = all_days()
    todo = [d for d in days if not os.path.exists(day_path(d))]
    width, height = grid_shape(BBOX, RES_DEG)
    print(f"Grid {width} x {height} px at {RES_DEG} deg | {len(days)} days total, "
          f"{len(days) - len(todo)} already saved, {len(todo)} to fetch")
    if not todo:
        return []
    tokens = TokenManager(get_token)
    failures, lock, done = [], threading.Lock(), [0]

    def work(day):
        arr, err = request_day(tokens, BBOX, day, RES_DEG)
        if arr is None:
            return day, err
        if arr.shape != (height, width):
            return day, f"unexpected raster shape {arr.shape}"
        save_day(day, arr)
        return day, None

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(work, d) for d in todo]
        for fut in as_completed(futures):
            day, err = fut.result()
            with lock:
                done[0] += 1
                if err:
                    failures.append((day.isoformat(), err))
                    print(f"  {day} FAILED: {err}")
                if done[0] % 50 == 0 or done[0] == len(futures):
                    print(f"  {done[0]}/{len(futures)} days processed")
    if failures:
        print(f"\n{len(failures)} days failed. A second run fetches only the missing days.")
        if any("429" in e or "quota" in e.lower() or "403" in e for _, e in failures):
            print("Some failures look like a rate or quota limit. Saved days are kept, "
                  "so the run can continue after the quota resets.")
    return failures


def aggregate():
    """Per-pixel monthly sum of valid values and count of valid days."""
    days = [d for d in all_days() if os.path.exists(day_path(d))]
    if not days:
        raise RuntimeError("No daily files found - run the download step first.")
    width, height = grid_shape(BBOX, RES_DEG)
    months = sorted({(d.year, d.month) for d in all_days()})
    index = {m: i for i, m in enumerate(months)}
    total = np.zeros((len(months), height, width), dtype="float64")
    count = np.zeros((len(months), height, width), dtype="uint8")
    days_present = np.zeros(len(months), dtype="int16")
    for n, d in enumerate(days, start=1):
        arr = load_day(d).astype("float64")
        valid = np.isfinite(arr)
        i = index[(d.year, d.month)]
        total[i][valid] += arr[valid]
        count[i] += valid.astype("uint8")
        days_present[i] += 1
        if n % 500 == 0 or n == len(days):
            print(f"  aggregated {n}/{len(days)} days")
    labels = np.array([f"{y}-{m:02d}" for y, m in months])
    np.savez_compressed(MONTHLY_PATH, sum=total.astype("float32"), count=count,
                        months=labels, days_present=days_present)
    meta = {"bbox_min_lon_min_lat_max_lon_max_lat": list(BBOX), "resolution_deg": RES_DEG,
            "width": width, "height": height, "row_0_is": "north", "crs": "EPSG:4326",
            "units": "mol/m2 (tropospheric NO2 column)", "qa_threshold": 0.75,
            "monthly_mean": "sum / count where count > 0",
            "days_saved": len(days), "days_expected": len(all_days())}
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved: {MONTHLY_PATH}  ({len(months)} months, {len(days)}/{len(all_days())} days)")
    return total, count, labels


def validate(total, count, labels):
    """Country monthly means rebuilt from the grid must match my country series."""
    if not os.path.exists(MASTER_PATH):
        print("Validation skipped: master_dataset_control.csv not found.")
        return
    import pandas as pd
    from country_boundaries import get_all_country_codes, load_country_geometry
    codes = get_all_country_codes()
    masks = build_masks(BBOX, {c: load_country_geometry(c, clip_to_bbox=BBOX) for c in codes}, RES_DEG)
    rows = []
    for i, lab in enumerate(labels):
        y, m = int(lab[:4]), int(lab[5:7])
        for c in codes:
            n = int(count[i][masks[c]].sum())
            rows.append({"country": c, "year": y, "month": m,
                         "grid_mean": float(total[i][masks[c]].sum() / n) if n else np.nan})
    g = pd.DataFrame(rows)
    ref = pd.read_csv(MASTER_PATH)[["country", "year", "month", "mean_no2"]]
    j = g.merge(ref, on=["country", "year", "month"])
    both = j.dropna(subset=["grid_mean", "mean_no2"])
    rel = (both["grid_mean"] - both["mean_no2"]).abs() / both["mean_no2"].abs().clip(lower=1e-9)
    only_one = int((j["grid_mean"].isna() != j["mean_no2"].isna()).sum())
    print(f"Validation against the country series: {len(both)} country-months compared, "
          f"median difference {100 * rel.median():.4f}%, largest {100 * rel.max():.4f}%, "
          f"{only_one} country-months present in only one of the two.")
    if rel.max() < 1e-3 and only_one == 0:
        print("  -> the grid reproduces the country series.")
    else:
        print("  -> differences found. Small ones are expected only while some days are still missing "
              "from the grid.")


def main():
    failures = []
    if "--no-download" not in sys.argv:
        from auth_sentinelhub import get_sentinelhub_token
        failures = download(get_sentinelhub_token)
    total, count, labels = aggregate()
    validate(total, count, labels)
    if failures:
        print(f"\nNOTE: {len(failures)} days are still missing, so the grid is not complete yet.")


if __name__ == "__main__":
    main()
