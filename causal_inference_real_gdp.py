"""I re-estimate the main country model and the matched pixel model with real GDP per capita in place of
nominal GDP. Real GDP per capita comes from one source (World Bank) for all 36 countries."""
import json
import warnings

import numpy as np
import pandas as pd
from scipy import stats

import analyse_no2_grid_baseline as grid
import causal_inference_identification_checks as cic
from country_boundaries import get_all_country_codes, load_country_geometry
from s5p_process_daily import RES_DEG, build_masks

GDP_PATH = "data/earth_observation/economy/final/gdp_per_capita_real.csv"
OUT_PATH = "data/real_gdp_checks.json"
NOMINAL = "gdp_million_eur"

warnings.filterwarnings("ignore", category=RuntimeWarning)


def t_ci(b, se, g, n):
    half = stats.t.ppf(0.975, g - 1) * se
    return {"coefficient": float(b), "se": float(se), "p_value": float(2 * stats.t.sf(abs(b / se), g - 1)),
            "ci_low": float(b - half), "ci_high": float(b + half), "n": int(n), "countries": int(g)}


def add_real_gdp(d):
    gdp = pd.read_csv(GDP_PATH).rename(columns={"geo": "country"})
    d = d.merge(gdp, on=["country", "year"], how="left")
    d["log_gdp_pc_ppp_const"] = np.log(d["gdp_pc_ppp_const"])
    return d


def show(label, s):
    print(f"  {label:<52s} {s['coefficient']:+.2f}  [{s['ci_low']:+.2f}, {s['ci_high']:+.2f}]  p={s['p_value']:.3f}  n={s['n']}")


def country_level():
    d = add_real_gdp(cic.load())
    d = d.dropna(subset=["mean_no2", "avg_temp_c", "avg_precip_mm", NOMINAL, "gdp_pc_ppp_const", "gdp_pc_const_usd"]).copy()
    g = d["country"].nunique()
    weather = ["avg_temp_c", "avg_precip_mm"]
    specs = {"nominal GDP (main model)": weather + [NOMINAL],
             "real GDP per capita, PPP": weather + ["gdp_pc_ppp_const"],
             "log real GDP per capita, PPP": weather + ["log_gdp_pc_ppp_const"],
             "real GDP per capita, constant US$": weather + ["gdp_pc_const_usd"],
             "no GDP": weather}
    out = {}
    print("\nCOUNTRY LEVEL, main model (1e-6 mol/m2)")
    for label, controls in specs.items():
        res, _ = cic.fit(d, controls=controls)
        out[label] = t_ci(res.params["did"] * 1e6, res.bse["did"] * 1e6, g, res.nobs)
        show(label, out[label])
    return out


def pixel_level():
    monthly, year, month = grid.load_grid()
    t = year * 12 + month
    codes = get_all_country_codes()
    masks = build_masks(grid.BBOX, {c: load_country_geometry(c, clip_to_bbox=grid.BBOX) for c in codes}, RES_DEG)
    base = grid.period_mean(monthly, month, t <= grid.CUTOFF)
    d = grid.cell_panel(monthly * 1e6, year, month, masks, np.digitize(base * 1e5, grid.EDGES), np.isfinite(base),
                        np.ones(len(t), bool))
    d = add_real_gdp(d)
    g = d["country"].nunique()
    original = list(grid.WEATHER)
    out = {}
    print(f"\nPIXEL LEVEL, matched on pre-treatment class ({g} countries)")
    try:
        for label, gdp_col in (("nominal GDP (Table 4)", NOMINAL), ("real GDP per capita, PPP", "gdp_pc_ppp_const"),
                               ("log real GDP per capita, PPP", "log_gdp_pc_ppp_const")):
            grid.WEATHER = ["avg_temp_c", "avg_precip_mm", gdp_col]
            r = grid.matched_did(d)
            out[label] = {k: t_ci(r[k]["coefficient"], r[k]["se"], g, r["rows"])
                          for k in ("not_matched", "matched_on_baseline")}
            show(label + ", not matched", out[label]["not_matched"])
            show(label + ", matched", out[label]["matched_on_baseline"])
    finally:
        grid.WEATHER = original
    return out


def main():
    out = {"source": "World Bank WDI: NY.GDP.PCAP.PP.KD (PPP, constant 2021 international $) and NY.GDP.PCAP.KD "
                     "(constant 2015 US$); annual values used for every month of the year",
           "country_level": country_level(), "pixel_level": pixel_level()}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()
