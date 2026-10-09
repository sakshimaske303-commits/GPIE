"""I check the satellite NO2 against EEA ground stations. Three questions:
1. Do station and TROPOMI pixel values agree, in level and in change?
2. Does the same country-level DiD on station data give a similar estimate?
3. Do stations also show the December 2023 drop in the Nordic and Baltic countries?

Stage 1 reads the EEA parquet files (needs pyarrow) and writes station-month means.
Stage 2 runs the comparisons. Stage 1 is skipped if its output already exists."""
import glob
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd
from scipy import stats

import analyse_no2_grid_baseline as grid
import causal_inference_identification_checks as cic
from config import MAX_LAT, MIN_LON

RAW_DIR = "data/eea_no2"
STATION_MONTHLY = "data/eea_station_monthly.csv"
OUT_PATH = "data/eea_validation.json"
YEARS = range(2019, 2025)
EEA_TO_MINE = {"GR": "EL", "GB": "UK"}         # EEA uses GR and GB; my panel uses EL and UK
MIN_CAPTURE = 0.75                              # share of hours (or days) a station-month needs
MIN_MONTHS = 0.8                                # share of the 72 months a station needs to enter the panel
LATE = (2023, 7)                                # start of the late period in the paper
NORDIC_BALTIC = ["DK", "SE", "LV", "LT"]        # countries with negative satellite means in December 2023

warnings.filterwarnings("ignore", category=RuntimeWarning)


# Stage 1: station-month means from the raw files
def find_columns(names):
    lower = {n.lower(): n for n in names}
    want = {"point": "samplingpoint", "start": "start", "value": "value", "validity": "validity", "agg": "aggtype"}
    missing = [w for w in want.values() if w not in lower]
    if missing:
        raise SystemExit(f"Columns not found: {missing}. The file has: {list(names)}")
    return {k: lower[v] for k, v in want.items()}


def read_file(path, years):
    import pyarrow.parquet as pq
    names = pq.read_schema(path).names
    col = find_columns(names)
    d = pq.read_table(path, columns=list(col.values())).to_pandas()
    d.columns = list(col.keys())
    d["start"] = pd.to_datetime(d["start"])
    d["value"] = pd.to_numeric(d["value"], errors="coerce")       # unverified files store it as text
    d = d[d["start"].dt.year.isin(years) & (d["validity"] > 0) & d["value"].notna() & (d["value"] >= 0)]
    if d.empty:
        return None
    d["year"], d["month"] = d["start"].dt.year, d["start"].dt.month
    d["agg"] = d["agg"].fillna("hour").astype(str)
    g = d.groupby(["point", "agg", "year", "month"])["value"].agg(["mean", "count"]).reset_index()
    g["hours"] = pd.to_datetime(g["year"].astype(str) + "-" + g["month"].astype(str) + "-01").dt.days_in_month * 24
    g["expected"] = np.where(g["agg"].astype(str).str.lower().str.startswith("hour"), g["hours"], g["hours"] / 24)
    g = g[g["count"] >= MIN_CAPTURE * g["expected"]]
    return g[["point", "year", "month", "mean"]]


def build_station_monthly():
    parts = []
    # Verified files hold the whole reported history. The unverified files only hold the current year,
    # so I use them only for months the verified files do not cover.
    for source, years in (("verified", YEARS), ("unverified", YEARS)):
        files = sorted(glob.glob(os.path.join(RAW_DIR, source, "*", "*.parquet")))
        print(f"{source}: {len(files)} files")
        for i, path in enumerate(files):
            g = read_file(path, years)
            if g is not None:
                g["eea_country"] = os.path.basename(os.path.dirname(path))
                g["verified"] = source == "verified"
                parts.append(g)
            if (i + 1) % 500 == 0:
                print(f"  {i + 1} / {len(files)}")
    d = pd.concat(parts, ignore_index=True)
    has_verified = d[d["verified"]].groupby(["point", "year", "month"]).size().rename("v").reset_index()
    d = d.merge(has_verified, on=["point", "year", "month"], how="left")
    d = d[d["verified"] | d["v"].isna()]
    # one value per sampling point and month (a point can appear in more than one file)
    d = d.groupby(["eea_country", "point", "year", "month"], as_index=False)["mean"].mean()
    print("Station-months by year:", d.groupby("year").size().to_dict())
    d = d.rename(columns={"mean": "no2_ugm3"})

    meta = pd.concat([pd.read_csv(os.path.join(RAW_DIR, s, "metadata.csv"), low_memory=False,
                                  usecols=["Sampling Point Id", "Air Pollutant", "Longitude", "Latitude",
                                           "Air Quality Station Type", "Air Quality Station Area",
                                           "Air Quality Station EoI Code"])
                      for s in ("verified", "unverified") if os.path.exists(os.path.join(RAW_DIR, s, "metadata.csv"))])
    meta = meta[meta["Air Pollutant"] == "NO2"].drop_duplicates("Sampling Point Id")
    meta = meta.rename(columns={"Sampling Point Id": "point_id", "Longitude": "lon", "Latitude": "lat",
                                "Air Quality Station Type": "station_type", "Air Quality Station Area": "area",
                                "Air Quality Station EoI Code": "station"})
    d["point_id"] = d["point"].astype(str).str.split("/").str[-1]
    d = d.merge(meta[["point_id", "station", "lon", "lat", "station_type", "area"]], on="point_id", how="left")
    share = d["lon"].notna().mean()
    print(f"Sampling points matched to station metadata: {100 * share:.1f}% of station-months")
    if share < 0.5:
        print("Example ids from the data:", d["point"].drop_duplicates().head(5).tolist())
        print("Example ids from the metadata:", meta["point_id"].head(5).tolist())
        raise SystemExit("Too few matches; the id formats differ.")
    d = d.dropna(subset=["lon", "lat"])
    d["country"] = d["eea_country"].replace(EEA_TO_MINE)
    d.to_csv(STATION_MONTHLY, index=False)
    print(f"Saved: {STATION_MONTHLY} ({d['point_id'].nunique()} sampling points)")


# Stage 2: comparisons
def t_ci(b, se, g):
    half = stats.t.ppf(0.975, g - 1) * se
    return {"coefficient": float(b), "se": float(se), "p_value": float(2 * stats.t.sf(abs(b / se), g - 1)),
            "ci_low": float(b - half), "ci_high": float(b + half), "countries": int(g)}


def balanced_mean(values, month, sel, need=9):
    """Period mean balanced by calendar month, as for the pixels in the paper."""
    by_month = [np.nanmean(values[sel & (month == k)]) if (sel & (month == k)).any() else np.nan for k in range(1, 13)]
    by_month = np.array(by_month)
    return np.nanmean(by_month) if np.isfinite(by_month).sum() >= need else np.nan


def add_pixels(d):
    monthly, year, month = grid.load_grid()
    index = {(int(y), int(m)): i for i, (y, m) in enumerate(zip(year, month))}
    row = np.floor((MAX_LAT - d["lat"].values) / 0.1).astype(int)
    col = np.floor((d["lon"].values - MIN_LON) / 0.1).astype(int)
    inside = (row >= 0) & (row < monthly.shape[1]) & (col >= 0) & (col < monthly.shape[2])
    t = np.array([index.get((y, m), -1) for y, m in zip(d["year"], d["month"])])
    sat = np.full(len(d), np.nan)
    ok = inside & (t >= 0)
    sat[ok] = monthly[t[ok], row[ok], col[ok]] * 1e6           # 1e-6 mol/m2
    d["sat"] = sat
    return d


def agreement(d):
    out = {}
    both = d.dropna(subset=["no2_ugm3", "sat"])
    out["pooled_monthly_r"] = float(both["no2_ugm3"].corr(both["sat"]))
    out["pooled_monthly_n"] = int(len(both))
    per = both.groupby("point_id").filter(lambda g: len(g) >= 24).groupby("point_id").apply(
        lambda g: g["no2_ugm3"].corr(g["sat"]))
    out["median_within_station_r"] = float(per.median())
    out["stations_with_24_paired_months"] = int(per.notna().sum())
    pre = both[(both["year"] * 12 + both["month"]) <= grid.CUTOFF].groupby("point_id")[["no2_ugm3", "sat"]].mean()
    out["between_station_r_pre_period"] = float(pre["no2_ugm3"].corr(pre["sat"]))

    rows = []
    late = LATE[0] * 12 + LATE[1]
    for pid, g in both.groupby("point_id"):
        t = (g["year"] * 12 + g["month"]).values
        m = g["month"].values
        pre_sel, late_sel = t <= grid.CUTOFF, t >= late
        s0, s1 = balanced_mean(g["no2_ugm3"].values, m, pre_sel), balanced_mean(g["no2_ugm3"].values, m, late_sel)
        p0, p1 = balanced_mean(g["sat"].values, m, pre_sel), balanced_mean(g["sat"].values, m, late_sel)
        if np.isfinite([s0, s1, p0, p1]).all() and s0 > 0 and p0 > 0:
            rows.append({"point_id": pid, "country": g["country"].iloc[0], "station_pct": 100 * (s1 - s0) / s0,
                         "pixel_pct": 100 * (p1 - p0) / p0})
    ch = pd.DataFrame(rows, columns=["point_id", "country", "station_pct", "pixel_pct"])
    if ch.empty:
        print("  No station has enough months in both periods for the change comparison.")
        return out
    out["change_stations"] = int(len(ch))
    out["change_r"] = float(ch["station_pct"].corr(ch["pixel_pct"]))
    ch["eu"] = ~ch["country"].isin(grid.CONTROLS)
    out["median_change_pct"] = {
        "EU-27 stations": float(ch.loc[ch["eu"], "station_pct"].median()),
        "EU-27 pixels at the stations": float(ch.loc[ch["eu"], "pixel_pct"].median()),
        "comparison stations": float(ch.loc[~ch["eu"], "station_pct"].median()),
        "comparison pixels at the stations": float(ch.loc[~ch["eu"], "pixel_pct"].median())}
    return out


def country_panel(d, value):
    """Country-month means over a fixed set of stations, merged into my country panel."""
    m = d.groupby(["country", "year", "month"])[value].mean().rename("mean_no2").reset_index()
    base = cic.load().drop(columns=["mean_no2"])
    p = base.merge(m, on=["country", "year", "month"], how="inner")
    return p.dropna(subset=["mean_no2"] + cic.BASE_CONTROLS)


def did(p, scale, **kw):
    res, _ = cic.fit(p, **kw)
    g = p["country"].nunique()
    s = t_ci(res.params["did"] * scale, res.bse["did"] * scale, g)
    eu_pre = p[(p["eu"] == 1) & (p["post"] == 0)]["mean_no2"].mean() * scale
    s["pct_of_eu_pre_mean"] = float(100 * s["coefficient"] / eu_pre)
    s["n"] = int(res.nobs)
    return s


def show(label, s, unit):
    print(f"  {label:<58s} {s['coefficient']:+.2f} {unit} ({s['pct_of_eu_pre_mean']:+.1f}%)  "
          f"[{s['ci_low']:+.2f}, {s['ci_high']:+.2f}]  p={s['p_value']:.3f}  countries={s['countries']}")


def ground_did(d):
    out = {}
    print("\nCOUNTRY-LEVEL DiD, main model, background stations")
    p_st = country_panel(d, "no2_ugm3")
    p_sat = country_panel(d.dropna(subset=["sat"]), "sat")
    common = sorted(set(p_st["country"]) & set(p_sat["country"]))
    p_st, p_sat = p_st[p_st["country"].isin(common)], p_sat[p_sat["country"].isin(common)]
    # the panel loader expects mol/m2 for NO2, so I pass the scale explicitly
    out["stations"] = did(p_st, 1.0)
    out["satellite at the same stations"] = did(p_sat, 1.0)
    show("stations (ug/m3)", out["stations"], "ug/m3")
    show("satellite pixels at the same stations (1e-6 mol/m2)", out["satellite at the same stations"], "1e-6")

    winter = [11, 12, 1, 2]
    out["stations, without Nov-Feb"] = did(p_st[~p_st["month"].isin(winter)], 1.0)
    out["satellite at the same stations, without Nov-Feb"] = did(p_sat[~p_sat["month"].isin(winter)], 1.0)
    show("stations, without Nov-Feb", out["stations, without Nov-Feb"], "ug/m3")
    show("satellite at the same stations, without Nov-Feb", out["satellite at the same stations, without Nov-Feb"], "1e-6")

    for label, p, unit in (("stations", p_st, "ug/m3"), ("satellite at the same stations", p_sat, "1e-6")):
        pp = p[p["mean_no2"] > 0].copy()
        pp["log_no2"] = np.log(pp["mean_no2"])
        res, _ = cic.fit(pp, outcome="log_no2")
        out[f"{label}, log outcome"] = t_ci(res.params["did"], res.bse["did"], pp["country"].nunique())
        s = out[f"{label}, log outcome"]
        print(f"  {label + ', log outcome':<58s} {s['coefficient']:+.3f} log points  p={s['p_value']:.3f}")

        pre = pp[pp["post"] == 0].groupby("country")["mean_no2"].mean()
        extra = pd.DataFrame({"pre_level_x_post": pp["country"].map(pre) * pp["post"]}, index=pp.index)
        res, _ = cic.fit(pp, extra=extra)
        out[f"{label}, + pre-treatment level x post"] = t_ci(res.params["did"], res.bse["did"], pp["country"].nunique())
        s = out[f"{label}, + pre-treatment level x post"]
        print(f"  {label + ', + pre-level x post':<58s} {s['coefficient']:+.2f}  p={s['p_value']:.3f}")
    out["countries"] = common
    return out, p_st, p_sat


def december_2023(p_st, p_sat):
    out = {}
    print("\nDECEMBER 2023, relative to the mean of December 2022 and December 2024")
    for c in NORDIC_BALTIC:
        row = {}
        for label, p in (("stations", p_st), ("satellite", p_sat)):
            q = p[(p["country"] == c) & (p["month"] == 12)].set_index("year")["mean_no2"]
            if {2022, 2023, 2024} <= set(q.index):
                row[label] = float(100 * (q[2023] / ((q[2022] + q[2024]) / 2) - 1))
        out[c] = row
        print(f"  {c}: " + ", ".join(f"{k} {v:+.0f}%" for k, v in row.items()))
    return out


def main():
    if not os.path.exists(STATION_MONTHLY):
        build_station_monthly()
    d = pd.read_csv(STATION_MONTHLY)
    n_months = len(YEARS) * 12
    coverage = d.groupby("point_id").size() / n_months
    keep = coverage[coverage >= MIN_MONTHS].index
    d = d[d["point_id"].isin(keep) & d["country"].isin(cic.load()["country"].unique())]
    print(f"Sampling points with at least {100 * MIN_MONTHS:.0f}% of the 72 months: {d['point_id'].nunique()}")

    out = {"settings": {"monthly_capture_min": MIN_CAPTURE, "months_min_share": MIN_MONTHS,
                        "sources": "EEA verified data (E1a) 2019-2024; unverified (E2a) only for months the verified files lack; background stations for the main checks"}}
    counts = d.drop_duplicates("point_id").groupby(["country", "station_type"]).size().unstack(fill_value=0)
    out["sampling_points_by_country"] = counts.to_dict(orient="index")
    print(counts.to_string())

    d = add_pixels(d)
    bg = d[d["station_type"] == "background"].copy()
    print(f"\nBackground sampling points: {bg['point_id'].nunique()}")
    out["agreement_background"] = agreement(bg)
    a = out["agreement_background"]
    print(f"AGREEMENT: pooled monthly r = {a['pooled_monthly_r']:.2f} (n = {a['pooled_monthly_n']}); median within-station "
          f"r = {a['median_within_station_r']:.2f}; between stations (pre-period means) r = {a['between_station_r_pre_period']:.2f}; "
          f"change r = {a.get('change_r', float('nan')):.2f} over {a.get('change_stations', 0)} stations")
    print("  median % change from Jul 2023: " + ", ".join(f"{k} {v:+.1f}" for k, v in a.get("median_change_pct", {}).items()))

    out["did_background"], p_st, p_sat = ground_did(bg)
    out["december_2023"] = december_2023(p_st, p_sat)

    out["agreement_traffic"] = agreement(d[d["station_type"] == "traffic"].copy())
    print(f"\nTraffic stations: pooled r = {out['agreement_traffic']['pooled_monthly_r']:.2f}, "
          f"change r = {out['agreement_traffic'].get('change_r', float('nan')):.2f}")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()
