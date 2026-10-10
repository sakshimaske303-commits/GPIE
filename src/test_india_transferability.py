
import os
import json
import requests
import pandas as pd
from shapely.geometry import shape, mapping
import math
from auth_sentinelhub import get_sentinelhub_token
from s5p_process_daily import run_daily, monthly_from_log, RES_DEG

OUTPUT_DIR = "data/global_transferability_test"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "india_no2_test.json")
LOG_PATH = os.path.join(OUTPUT_DIR, "india_no2_daily_log.jsonl")
SUMMARY_PATH = os.path.join(OUTPUT_DIR, "india_no2_sanity_check.json")
GADM_IND_PATH = "data/earth_observation/boundaries/raw/gadm41_IND_0.json"
GADM_IND_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_IND_0.json"
MASTER_PATH = "data/master_dataset_control.csv"


def load_india_geometry():
    if not os.path.exists(GADM_IND_PATH):
        print(f"Downloading India boundary: {GADM_IND_URL}")
        r = requests.get(GADM_IND_URL, timeout=300)
        r.raise_for_status()
        os.makedirs(os.path.dirname(GADM_IND_PATH), exist_ok=True)
        with open(GADM_IND_PATH, "wb") as f:
            f.write(r.content)
    with open(GADM_IND_PATH, encoding="utf-8") as f:
        geom = shape(json.load(f)["features"][0]["geometry"])
    geom = geom.simplify(0.01, preserve_topology=True)
    return mapping(geom)


def flatten(results):
    rows = []
    for rec in results:
        for entry in rec["data"]["data"]:
            stats = entry["outputs"]["no2"]["bands"]["B0"]["stats"]
            rows.append({"date": entry["interval"]["from"][:10], "mean_no2": stats.get("mean")})
    return pd.DataFrame(rows)


def sanity_check(df):
    eu = pd.read_csv(MASTER_PATH)
    eu = eu[eu["treatment_group"] == 1]["mean_no2"].dropna()
    s = df["mean_no2"].dropna()
    summary = {
        "months_requested": int(len(df)),
        "months_with_data": int(len(s)),
        "india_min": float(s.min()), "india_median": float(s.median()), "india_max": float(s.max()),
        "india_negative_months": int((s < 0).sum()),
        "eu27_country_month_p5": float(eu.quantile(0.05)),
        "eu27_country_month_p95": float(eu.quantile(0.95)),
        "india_share_within_eu27_p5_p95": float(((s >= eu.quantile(0.05)) & (s <= eu.quantile(0.95))).mean()),
    }
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"Saved: {SUMMARY_PATH}")


def main():
    geometry = load_india_geometry()
    sh = shape(geometry)
    min_lon, min_lat, max_lon, max_lat = sh.bounds
    bbox = (math.floor(min_lon / RES_DEG) * RES_DEG, math.floor(min_lat / RES_DEG) * RES_DEG,
            math.ceil(max_lon / RES_DEG) * RES_DEG, math.ceil(max_lat / RES_DEG) * RES_DEG)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    failures = run_daily(get_sentinelhub_token, bbox, {"IN": geometry}, LOG_PATH)
    monthly = monthly_from_log(LOG_PATH, ["IN"], "no2")
    results = [{"country": "India", "year": r["year"], "data": r["data"]} for r in monthly]

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {OUTPUT_PATH}")
    if failures:
        print("Some days failed. The output is incomplete until a second run fills them.")
    sanity_check(flatten(results))


if __name__ == "__main__":
    main()
