"""I check where the EU's relative NO2 decline sits: I compare EU and control pixels that
started at the same pollution level, using my gridded monthly NO2."""
import json
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT
from country_boundaries import (CONTROL_COUNTRIES, EXPANSION_CONTROL_COUNTRIES,
                                get_all_country_codes, load_country_geometry)
from s5p_process_daily import RES_DEG, build_masks

GRID_PATH = "data/earth_observation/no2/gridded/no2_grid_monthly.npz"
MASTER_PATH = "data/master_dataset_control.csv"
OUT_JSON = "data/grid_baseline_checks.json"
OUT_BINS = "outputs/plots/no2_change_by_baseline.png"
OUT_MAP = "outputs/plots/no2_change_map.png"

BBOX = (MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)
CONTROLS = set(CONTROL_COUNTRIES) | set(EXPANSION_CONTROL_COUNTRIES)
MIN_DAYS = 3                                     # valid days a pixel needs in a month
EDGES = [1.5, 2, 2.5, 3, 4, 5, 7]                # baseline classes, 1e-5 mol/m2
LABELS = ["<1.5", "1.5-2", "2-2.5", "2.5-3", "3-4", "4-5", "5-7", ">7"]
CUTOFF = 2021 * 12 + 6                           # June 2021, so July 2021 is my first post month
LATE = 2023 * 12 + 6                             # the decline shows up after June 2023
WEATHER = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]

warnings.filterwarnings("ignore", category=RuntimeWarning)   # all-NaN pixels over sea


def load_grid():
    z = np.load(GRID_PATH)
    total, count = z["sum"].astype("float64"), z["count"].astype("float64")
    monthly = np.where(count >= MIN_DAYS, total / np.maximum(count, 1), np.nan)
    year = np.array([int(m[:4]) for m in z["months"]])
    month = np.array([int(m[5:]) for m in z["months"]])
    return monthly, year, month


def period_mean(monthly, month, sel, need=9):
    """Mean over the selected months, balanced by calendar month so seasons weigh the same."""
    by_month = []
    for k in range(1, 13):
        idx = np.where(sel & (month == k))[0]
        by_month.append(np.nanmean(monthly[idx], axis=0) if len(idx) else np.full(monthly.shape[1:], np.nan))
    by_month = np.array(by_month)
    enough = np.isfinite(by_month).sum(axis=0) >= need
    return np.where(enough, np.nanmean(by_month, axis=0), np.nan)


def fit(d, parts, names):
    X = pd.concat(parts, axis=1)
    X.insert(0, "const", 1.0)
    q, r = np.linalg.qr(X.values / np.sqrt((X.values ** 2).sum(axis=0)))
    X = X.loc[:, np.abs(np.diag(r)) > 1e-9]      # drop collinear columns
    res = sm.WLS(d["no2"].values, X, weights=d["w"].values).fit(
        cov_type="cluster", cov_kwds={"groups": d["country"].values})
    return {n: {"coefficient": float(res.params[n]), "p_value": float(res.pvalues[n])}
            for n in names if n in res.params.index}


def cell_panel(monthly, year, month, masks, bins, usable, est_sel):
    """Country x baseline-class x month means. Each country gets the same total weight."""
    master = pd.read_csv(MASTER_PATH)[["country", "year", "month"] + WEATHER]
    rows = []
    for code, mask in masks.items():
        for i in range(len(LABELS)):
            sel = mask & usable & (bins == i)
            if sel.sum() < 5:
                continue
            values = monthly[:, sel]
            n_valid = np.isfinite(values).sum(axis=1)
            means = np.nanmean(values, axis=1)
            for j in np.where(est_sel)[0]:
                if n_valid[j] >= max(3, 0.3 * sel.sum()):
                    rows.append((code, i, year[j], month[j], means[j], sel.sum()))
    d = pd.DataFrame(rows, columns=["country", "bin", "year", "month", "no2", "w"])
    d = d.merge(master, on=["country", "year", "month"], how="left").dropna()
    d["w"] = d["w"] / d.groupby(["country", "year", "month"])["w"].transform("sum")
    t = d["year"] * 12 + d["month"]
    d["eu"] = (~d["country"].isin(CONTROLS)).astype(float)
    d["did"] = d["eu"] * (t > CUTOFF)
    d["did_early"] = d["eu"] * ((t > CUTOFF) & (t <= LATE))
    d["did_late"] = d["eu"] * (t > LATE)
    d["ym"] = d["year"].astype(str) + "-" + d["month"].astype(str)
    d["cb"] = d["country"] + "_" + d["bin"].astype(str)
    d["bym"] = d["bin"].astype(str) + "_" + d["ym"]
    return d


def matched_did(d):
    dummies = lambda col, p: pd.get_dummies(d[col], prefix=p, drop_first=True).astype(float)
    eu_season = dummies("month", "eum").mul(d["eu"].values, axis=0)
    base = [d[WEATHER], dummies("cb", "cb"), eu_season]
    out = {"cells": int(d["cb"].nunique()), "rows": int(len(d))}
    out["not_matched"] = fit(d, [d[["did"]]] + base + [dummies("ym", "t")], ["did"])["did"]
    out["matched_on_baseline"] = fit(d, [d[["did"]]] + base + [dummies("bym", "bt")], ["did"])["did"]
    split = fit(d, [d[["did_early", "did_late"]]] + base + [dummies("bym", "bt")], ["did_early", "did_late"])
    out["matched_jul2021_jun2023"], out["matched_from_jul2023"] = split["did_early"], split["did_late"]
    return out


def main():
    monthly, year, month = load_grid()
    t = year * 12 + month
    codes = get_all_country_codes()
    masks = build_masks(BBOX, {c: load_country_geometry(c, clip_to_bbox=BBOX) for c in codes}, RES_DEG)
    eu = np.zeros(monthly.shape[1:], bool)
    control = eu.copy()
    for code, mask in masks.items():
        (control if code in CONTROLS else eu).__ior__(mask)

    pre = period_mean(monthly, month, t <= CUTOFF)
    early = period_mean(monthly, month, (t > CUTOFF) & (t <= LATE))
    late = period_mean(monthly, month, t > LATE)
    usable = np.isfinite(pre) & np.isfinite(early) & np.isfinite(late)
    bins = np.digitize(pre * 1e5, EDGES)
    out = {"pixels": {"eu": int((eu & usable).sum()), "control": int((control & usable).sum())}}

    # 1. Change by baseline class
    table = []
    for group, gmask in (("EU-27", eu), ("control", control)):
        for i, lab in enumerate(LABELS):
            sel = gmask & usable & (bins == i)
            if sel.sum() == 0:
                continue
            table.append({"group": group, "baseline_class_1e-5": lab, "pixels": int(sel.sum()),
                          "pre_mean_1e-6": float(pre[sel].mean() * 1e6),
                          "change_jul2021_jun2023_pct": float(100 * (early - pre)[sel].mean() / pre[sel].mean()),
                          "change_from_jul2023_pct": float(100 * (late - pre)[sel].mean() / pre[sel].mean())})
    out["change_by_baseline_class"] = table
    print(pd.DataFrame(table).round(2).to_string(index=False))

    # 2. Pixel-level: does the change follow the baseline level or EU membership?
    px = pd.concat([pd.DataFrame({"country": c, "pre": pre[m & usable] * 1e6,
                                  "change": (late - pre)[m & usable] * 1e6}) for c, m in masks.items()])
    px["eu"] = (~px["country"].isin(CONTROLS)).astype(float)
    X = sm.add_constant(pd.DataFrame({"eu": px["eu"], "pre": px["pre"],
                                      "eu_x_pre": px["eu"] * (px["pre"] - px["pre"].mean())}))
    res = sm.OLS(px["change"], X).fit(cov_type="cluster", cov_kwds={"groups": px["country"]})
    out["pixel_regression_change_from_jul2023"] = {
        "n_pixels": int(len(px)), "r_squared": float(res.rsquared),
        **{k: {"coefficient": float(res.params[k]), "p_value": float(res.pvalues[k])} for k in ("eu", "pre", "eu_x_pre")}}
    print(f"\nPixel regression: slope on baseline {res.params['pre']:.3f} (p={res.pvalues['pre']:.2g}), "
          f"EU {res.params['eu']:+.3f}e-6 (p={res.pvalues['eu']:.3f}), "
          f"EU x baseline {res.params['eu_x_pre']:+.4f} (p={res.pvalues['eu_x_pre']:.3f}), R2={res.rsquared:.2f}")

    # 3. DiD with and without matching on the baseline class
    every = np.ones(len(t), bool)
    for label, base_sel, est_sel in (("classes from Jan 2019 - Jun 2021, all months", t <= CUTOFF, every),
                                     ("classes from 2019 only, estimated on 2020-2024", year == 2019, year >= 2020)):
        base = period_mean(monthly, month, base_sel)
        ok = np.isfinite(base)
        d = cell_panel(monthly * 1e6, year, month, masks, np.digitize(base * 1e5, EDGES), ok, est_sel)
        r = matched_did(d)
        out[label] = r
        print(f"\n{label}\n  not matched:         {r['not_matched']['coefficient']:+.3f}e-6  p={r['not_matched']['p_value']:.3f}"
              f"\n  matched on baseline: {r['matched_on_baseline']['coefficient']:+.3f}e-6  p={r['matched_on_baseline']['p_value']:.3f}"
              f"\n  matched, Jul 2021 - Jun 2023: {r['matched_jul2021_jun2023']['coefficient']:+.3f}e-6  p={r['matched_jul2021_jun2023']['p_value']:.3f}"
              f"\n  matched, from Jul 2023:       {r['matched_from_jul2023']['coefficient']:+.3f}e-6  p={r['matched_from_jul2023']['p_value']:.3f}")

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {OUT_JSON}")

    # Figure 1: change by baseline class
    tab = pd.DataFrame(table)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(LABELS))
    for k, (group, color) in enumerate((("EU-27", "#2c7fb8"), ("control", "#d95f0e"))):
        g = tab[tab["group"] == group].set_index("baseline_class_1e-5").reindex(LABELS)
        ax.bar(x + (k - 0.5) * 0.38, g["change_from_jul2023_pct"], width=0.38, color=color,
               label=f"{group} pixels")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(LABELS)
    ax.set_xlabel("Pre-treatment NO₂ level of the pixel (10⁻⁵ mol/m²)")
    ax.set_ylabel("Change in NO₂ from Jul 2023 vs. pre-treatment (%)")
    ax.set_title("NO₂ fell in proportion to how polluted a place was, inside and outside the EU\n"
                 "0.1° pixels, Jul 2023 – Dec 2024 against Jan 2019 – Jun 2021", fontsize=12)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.3)
    plt.figtext(0.5, 0.01, "Green Policy Intelligence Engine (GPIE) - Source: Sentinel-5P TROPOMI, Sentinel Hub Process API",
                ha="center", fontsize=8, color="gray")
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    plt.savefig(OUT_BINS, dpi=200)
    plt.close()

    # Figure 2: map of the change
    change = np.where((eu | control) & usable, (late - pre) * 1e6, np.nan)
    fig, ax = plt.subplots(figsize=(11, 8))
    im = ax.imshow(change, extent=(MIN_LON, MAX_LON, MIN_LAT, MAX_LAT), cmap="RdBu_r", vmin=-15, vmax=15)
    ax.set_xlim(-12, 32)
    ax.set_ylim(34, 62)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Change in tropospheric NO₂: Jul 2023 – Dec 2024 minus Jan 2019 – Jun 2021\n"
                 "36 study countries, 0.1° pixels", fontsize=12)
    cb = plt.colorbar(im, ax=ax, shrink=0.75)
    cb.set_label("Change in NO₂ (10⁻⁶ mol/m²)")
    plt.figtext(0.5, 0.01, "Green Policy Intelligence Engine (GPIE) - Source: Sentinel-5P TROPOMI, Sentinel Hub Process API",
                ha="center", fontsize=8, color="gray")
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    plt.savefig(OUT_MAP, dpi=200)
    plt.close()
    print(f"Saved: {OUT_BINS}\nSaved: {OUT_MAP}")


if __name__ == "__main__":
    main()
