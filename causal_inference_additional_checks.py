"""I check the composition explanation further: without NL and BE, on common support with the UK,
in logs with a pre-level x post term, with country trends, and at pixel level without the COVID months
and in 12-month blocks."""
import json
import warnings

import numpy as np
import pandas as pd
from scipy import stats

import analyse_no2_grid_baseline as grid
import causal_inference_identification_checks as cic
from country_boundaries import get_all_country_codes, load_country_geometry
from s5p_process_daily import RES_DEG, build_masks

OUT_PATH = "data/additional_checks.json"
COVID_START = 2020 * 12 + 3                     # March 2020
BLOCKS = {-3: "Jan-Jun 2019", -2: "Jul 2019-Jun 2020", 0: "Jul 2021-Jun 2022", 1: "Jul 2022-Jun 2023",
          2: "Jul 2023-Jun 2024", 3: "Jul-Dec 2024"}

warnings.filterwarnings("ignore", category=RuntimeWarning)


def summ(res, name, n_clusters, scale=1e6):
    """Coefficient in 1e-6 mol/m2 (scale=1 for logs), with a t(G-1) interval."""
    b, se = float(res.params[name]) * scale, float(res.bse[name]) * scale
    half = stats.t.ppf(0.975, n_clusters - 1) * se
    return {"coefficient": b, "se": se, "p_value": float(2 * stats.t.sf(abs(b / se), n_clusters - 1)),
            "ci_low": b - half, "ci_high": b + half, "n": int(res.nobs), "countries": int(n_clusters)}


def show(label, s):
    print(f"  {label:<62s} {s['coefficient']:+.3f}  [{s['ci_low']:+.2f}, {s['ci_high']:+.2f}]  p={s['p_value']:.3f}  "
          f"countries={s['countries']}")


def country_level():
    out = {}
    d = cic.load()
    d = d.dropna(subset=["mean_no2"] + cic.BASE_CONTROLS).copy()
    G = lambda x: x["country"].nunique()
    print("\nCOUNTRY LEVEL (main model; 1e-6 mol/m2)")

    res, _ = cic.fit(d)
    out["main model"] = summ(res, "did", G(d))
    show("main model", out["main model"])

    sub = d[~d["country"].isin(["NL", "BE"])]
    res, _ = cic.fit(sub)
    out["without NL and BE"] = summ(res, "did", G(sub))
    show("without NL and BE", out["without NL and BE"])

    pre = d[d["post"] == 0].groupby("country")["mean_no2"].mean()
    ceiling = pre[d.groupby("country")["eu"].first() == 0].max()
    keep = pre[pre <= ceiling].index
    sub = d[d["country"].isin(keep)]
    res, _ = cic.fit(sub)
    out["common support"] = summ(res, "did", G(sub))
    out["common support"]["dropped_countries"] = sorted(set(d["country"]) - set(keep))
    out["common support"]["ceiling_pre_mean_1e-6"] = float(ceiling * 1e6)
    show("common support (pre-treatment level <= UK)", out["common support"])

    dl = d[d["mean_no2"] > 0].copy()
    dl["log_no2"] = np.log(dl["mean_no2"])
    log_pre = dl[dl["post"] == 0].groupby("country")["log_no2"].mean()
    extra = pd.DataFrame({"log_level_x_post": dl["country"].map(log_pre) * dl["post"]}, index=dl.index)
    res, _ = cic.fit(dl, outcome="log_no2", extra=extra)
    out["log outcome with log pre-level x post"] = {"did": summ(res, "did", G(dl), scale=1.0),
                                                    "log_level_x_post": summ(res, "log_level_x_post", G(dl), scale=1.0)}
    show("log outcome + log pre-level x post: EU x post (log points)", out["log outcome with log pre-level x post"]["did"])
    show("  log pre-level x post", out["log outcome with log pre-level x post"]["log_level_x_post"])

    t_c = (d["time"].dt.year * 12 + d["time"].dt.month)
    t_c = (t_c - t_c.mean()) / 12.0
    trends = pd.get_dummies(d["country"], prefix="trend").astype(float).mul(t_c.values, axis=0).iloc[:, 1:]
    res, _ = cic.fit(d, extra=trends)
    out["country-specific linear trends"] = summ(res, "did", G(d))
    show("country-specific linear trends", out["country-specific linear trends"])

    sub = d[d["mean_no2"] > 0]
    res, _ = cic.fit(sub)
    out["without non-positive country-months"] = summ(res, "did", G(sub))
    show("without the 8 non-positive country-months", out["without non-positive country-months"])

    loo = {}
    for c in sorted(d.loc[d["eu"] == 1, "country"].unique()):
        sub = d[d["country"] != c]
        res, _ = cic.fit(sub)
        loo[c] = summ(res, "did", G(sub))
    out["leave one EU member out"] = loo
    lo = min(loo, key=lambda c: loo[c]["coefficient"])
    hi = max(loo, key=lambda c: loo[c]["coefficient"])
    print(f"  leave one EU member out: {loo[lo]['coefficient']:+.2f} (without {lo}) to {loo[hi]['coefficient']:+.2f} "
          f"(without {hi}); p from {min(v['p_value'] for v in loo.values()):.3f} to {max(v['p_value'] for v in loo.values()):.3f}")
    return out


def pixel_blocks(d, matched):
    rel = (d["year"] - 2021) * 12 + (d["month"] - 7)
    event_year = np.floor(rel / 12).astype(int)
    names = []
    for k in BLOCKS:
        d[f"ev_{k}"] = d["eu"] * (event_year == k)
        names.append(f"ev_{k}")
    dummies = lambda col, p: pd.get_dummies(d[col], prefix=p, drop_first=True).astype(float)
    eu_season = dummies("month", "eum").mul(d["eu"].values, axis=0)
    base = [d[grid.WEATHER], dummies("cb", "cb"), eu_season]
    time_fe = dummies("bym", "bt") if matched else dummies("ym", "t")
    r = grid.fit(d, [d[names]] + base + [time_fe], names)
    g = d["country"].nunique()
    out = {}
    for k, label in BLOCKS.items():
        b, se = r[f"ev_{k}"]["coefficient"], r[f"ev_{k}"]["se"]
        half = stats.t.ppf(0.975, g - 1) * se
        out[label] = {"coefficient": b, "se": se, "p_value": float(2 * stats.t.sf(abs(b / se), g - 1)),
                      "ci_low": b - half, "ci_high": b + half}
    return out


def pixel_level():
    out = {}
    monthly, year, month = grid.load_grid()
    t = year * 12 + month
    codes = get_all_country_codes()
    masks = build_masks(grid.BBOX, {c: load_country_geometry(c, clip_to_bbox=grid.BBOX) for c in codes}, RES_DEG)
    base = grid.period_mean(monthly, month, t <= grid.CUTOFF)
    ok = np.isfinite(base)
    d = grid.cell_panel(monthly * 1e6, year, month, masks, np.digitize(base * 1e5, grid.EDGES), ok, np.ones(len(t), bool))
    out["countries_in_cell_panel"] = int(d["country"].nunique())
    out["countries_dropped_from_cell_panel"] = sorted(set(codes) - set(d["country"]))
    print(f"\nPIXEL LEVEL ({out['countries_in_cell_panel']} countries; dropped: {out['countries_dropped_from_cell_panel']})")

    tt = d["year"] * 12 + d["month"]
    sub = d[~((tt >= COVID_START) & (tt <= grid.CUTOFF))].copy()
    r = grid.matched_did(sub)
    g = sub["country"].nunique()
    for key in ("not_matched", "matched_on_baseline"):
        b, se = r[key]["coefficient"], r[key]["se"]
        half = stats.t.ppf(0.975, g - 1) * se
        r[key].update({"p_value": float(2 * stats.t.sf(abs(b / se), g - 1)), "ci_low": b - half, "ci_high": b + half})
    out["without Mar 2020 - Jun 2021"] = {"not_matched": r["not_matched"], "matched_on_baseline": r["matched_on_baseline"]}
    print(f"  without Mar 2020 - Jun 2021: not matched {r['not_matched']['coefficient']:+.3f} "
          f"(p={r['not_matched']['p_value']:.3f}) | matched {r['matched_on_baseline']['coefficient']:+.3f} "
          f"(p={r['matched_on_baseline']['p_value']:.3f})")

    for label, matched in (("12-month blocks, matched", True), ("12-month blocks, not matched", False)):
        out[label] = pixel_blocks(d.copy(), matched)
        print(f"  {label}: " + " | ".join(f"{k} {v['coefficient']:+.2f} (p={v['p_value']:.2f})" for k, v in out[label].items()))
    return out


def main():
    out = {"reference_block": "Jul 2020-Jun 2021", "country_level": country_level(), "pixel_level": pixel_level()}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()
