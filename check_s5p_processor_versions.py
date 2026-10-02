"""I check if my NO2 series mixes TROPOMI processor versions (OFFL changed v1.4 -> v2.2 on
1 July 2021, my treatment month) by comparing default, RPRO and OFFL values on 24 sample days."""
import json
from datetime import date

import numpy as np
import requests

from auth_sentinelhub import get_sentinelhub_token
from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT
from country_boundaries import load_country_geometry, get_all_country_codes, CONTROL_COUNTRIES, EXPANSION_CONTROL_COUNTRIES
from s5p_process_daily import TokenManager, build_masks, request_day

CATALOG_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
BBOX = (MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)
OUT_PATH = "data/s5p_processor_check.json"
SAMPLE_DAYS = [date(y, m, 15) for y in range(2019, 2025) for m in (1, 4, 7, 10)]


def catalogue_versions(day):
    """Product class and processor version of the NO2 products covering 10E 50N on this day."""
    flt = ("Collection/Name eq 'SENTINEL-5P' and contains(Name,'L2__NO2___') "
           f"and ContentDate/Start gt {day.isoformat()}T00:00:00.000Z "
           f"and ContentDate/Start lt {day.isoformat()}T23:59:59.000Z "
           "and OData.CSC.Intersects(area=geography'SRID=4326;POINT(10 50)')")
    try:
        r = requests.get(CATALOG_URL, params={"$filter": flt, "$top": 100}, timeout=120)
        r.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)[:150]}
    found = {}
    for item in r.json().get("value", []):
        name = item["Name"]                       # e.g. S5P_OFFL_L2__NO2____start_end_orbit_CC_PPPPPP_proc.nc
        cls = name[4:8]
        parts = name.replace(".nc", "").split("_")
        version = next((p for p in parts if len(p) == 6 and p.isdigit()), "?")
        key = f"{cls} v{int(version[0:2])}.{int(version[2:4])}.{int(version[4:6])}" if version != "?" else cls
        found[key] = found.get(key, 0) + 1
    return found


def pooled_mean(arr, masks, codes):
    valid = np.isfinite(arr)
    total, n = 0.0, 0
    for c in codes:
        sel = masks[c] & valid
        total += float(arr[sel].sum())
        n += int(sel.sum())
    return (total / n if n else None), n


def main():
    codes = get_all_country_codes()
    controls = set(CONTROL_COUNTRIES) | set(EXPANSION_CONTROL_COUNTRIES)
    eu = [c for c in codes if c not in controls]
    ctrl = [c for c in codes if c in controls]
    geoms = {c: load_country_geometry(c, clip_to_bbox=BBOX) for c in codes}
    masks = build_masks(BBOX, geoms)
    tokens = TokenManager(get_sentinelhub_token)

    rows = []
    print(f"{'day':<11} {'catalogue (class version: orbits)':<46} {'default':>9} {'RPRO':>9} {'OFFL':>9}   default equals")
    for day in SAMPLE_DAYS:
        cat = catalogue_versions(day)
        row = {"date": day.isoformat(), "catalogue": cat}
        vals = {}
        for label, tl in (("default", None), ("RPRO", "RPRO"), ("OFFL", "OFFL")):
            arr, err = request_day(tokens, BBOX, day, timeliness=tl)
            if arr is None:
                row[label] = {"error": err}
                vals[label] = None
                continue
            m_eu, n_eu = pooled_mean(arr, masks, eu)
            m_ct, n_ct = pooled_mean(arr, masks, ctrl)
            row[label] = {"eu_mean": m_eu, "eu_valid_pixels": n_eu, "control_mean": m_ct, "control_valid_pixels": n_ct}
            vals[label] = m_eu

        def same(a, b):
            return a is not None and b is not None and abs(a - b) <= 1e-9 * max(abs(a), abs(b), 1e-12)

        if same(vals["default"], vals["RPRO"]) and same(vals["default"], vals["OFFL"]):
            verdict = "both (identical)"
        elif same(vals["default"], vals["RPRO"]):
            verdict = "RPRO"
        elif same(vals["default"], vals["OFFL"]):
            verdict = "OFFL"
        else:
            verdict = "neither / mixed"
        row["default_equals"] = verdict
        if vals["RPRO"] and vals["OFFL"]:
            row["offl_minus_rpro_pct_eu"] = 100 * (vals["OFFL"] - vals["RPRO"]) / vals["RPRO"]
        rows.append(row)

        cat_txt = ", ".join(f"{k}: {v}" for k, v in sorted(cat.items())) or "none"
        fmt = lambda v: f"{v * 1e6:9.3f}" if v is not None else f"{'-':>9}"
        print(f"{day.isoformat():<11} {cat_txt[:46]:<46} {fmt(vals['default'])} {fmt(vals['RPRO'])} {fmt(vals['OFFL'])}   {verdict}")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"\nValues are pooled EU-27 means in 1e-6 mol/m2. Saved: {OUT_PATH}")
    print("How to read it: if 'default equals' is RPRO up to mid-2022 and OFFL afterwards (and the catalogue")
    print("shows processor v2.4 or later on both sides), the series is version-consistent. If it says OFFL")
    print("for 2019-2021 while RPRO also exists and differs, the series mixes processor versions.")


if __name__ == "__main__":
    main()
