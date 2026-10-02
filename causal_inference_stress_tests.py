"""I stress-test my two main results: the country-level DiD and the pixel-level matched DiD.
I check seasons, weighting, GDP form, comparison sub-groups, inference and the synthetic control fit."""
import json
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from scipy.optimize import nnls

import analyse_no2_grid_baseline as grid
import causal_inference_identification_checks as cic
from country_boundaries import get_all_country_codes, load_country_geometry
from s5p_process_daily import RES_DEG, build_masks

OUT_PATH = "data/stress_tests.json"
OUT_PLOT = "outputs/plots/no2_change_by_country.png"
WINTER = [11, 12, 1, 2]
EEA_UK = ["UK", "NO", "CH", "IS"]
BALKANS = ["AL", "BA", "ME", "MK", "RS"]
NW_EU = ["NL", "BE", "LU", "DE", "DK", "FR", "AT", "IE"]      # north-west EU members
NW_OUT = ["UK", "CH"]                                          # their non-EU neighbours
SE_EU = ["HR", "HU", "RO", "BG", "EL", "SI"]                   # south-east EU members
N_PERM = 999

warnings.filterwarnings("ignore", category=RuntimeWarning)


# Country level
def cfit(d, weights=None, outcome="mean_no2", scale=1e6, **kw):
    """My stricter country model (country FE, year-month FE, EU-specific calendar months)."""
    X = cic.drop_collinear(cic.build(d, **kw))
    y = d[outcome].astype(float).values * scale
    w = np.ones(len(d)) if weights is None else weights
    res = sm.WLS(y, X, weights=w).fit(cov_type="cluster", cov_kwds={"groups": d["country"].values})
    return res, X


def report(res, n_clusters, name="did"):
    """Coefficient with a normal p-value and a t(G-1) p-value, which is safer with few clusters."""
    t = res.params[name] / res.bse[name]
    half = stats.t.ppf(0.975, n_clusters - 1) * res.bse[name]
    return {"coefficient": float(res.params[name]), "se": float(res.bse[name]),
            "p_normal": float(res.pvalues[name]), "p_t": float(2 * stats.t.sf(abs(t), n_clusters - 1)),
            "ci_t_low": float(res.params[name] - half), "ci_t_high": float(res.params[name] + half),
            "n": int(res.nobs)}


def line(label, r):
    print(f"  {label:<58s} {r['coefficient']:+.3f}  p(t)={r['p_t']:.3f}  n={r['n']}")


def coverage_table(monthly_count, days_present, months, masks):
    """Share of pixel-days with a valid retrieval, per country and month."""
    rows = []
    for code, mask in masks.items():
        valid = monthly_count[:, mask].sum(axis=1)
        possible = mask.sum() * days_present
        for i, label in enumerate(months):
            rows.append({"country": code, "year": int(label[:4]), "month": int(label[5:]),
                         "coverage": float(valid[i] / possible[i]) if possible[i] else np.nan,
                         "pixels": int(mask.sum())})
    return pd.DataFrame(rows)


def t_randomization(d, n_perm=N_PERM, seed=12345):
    """Randomization inference on the cluster t-statistic, not on the raw coefficient."""
    codes, gidx = np.unique(d["country"].values, return_inverse=True)
    y = d["mean_no2"].astype(float).values * 1e6

    def t_stat(dd, eu_col):
        X = cic.drop_collinear(cic.build(dd, eu_col=eu_col))
        k = list(X.columns).index("did")
        return cic._cluster_t(cic._scale(X.values), y, gidx, len(codes), k)

    b_obs, t_obs = t_stat(d, "eu")
    countries = np.array(sorted(d["country"].unique()))
    n_treated = int(d.groupby("country")["eu"].first().sum())
    rng = np.random.default_rng(seed)
    b, t = np.empty(n_perm), np.empty(n_perm)
    for i in range(n_perm):
        fake = set(rng.choice(countries, size=n_treated, replace=False))
        dd = d.copy()
        dd["eu_fake"] = dd["country"].isin(fake).astype(float)
        dd["did"] = dd["eu_fake"] * dd["post"]
        b[i], t[i] = t_stat(dd, "eu_fake")
    return {"p_coefficient": float((np.abs(b) >= abs(b_obs)).mean()),
            "p_t_statistic": float((np.abs(t) >= abs(t_obs)).mean()), "n_perm": n_perm}


def country_level(masks, count, days_present, months):
    out = {}
    df = cic.load()
    d = df.dropna(subset=["mean_no2"] + cic.BASE_CONTROLS).copy()
    G = d["country"].nunique()
    cov = coverage_table(count, days_present, months, masks)
    d = d.merge(cov, on=["country", "year", "month"], how="left")
    d["log_gdp"] = np.log(d["gdp_million_eur"])
    pre_mean = d[d["post"] == 0].groupby("country")["mean_no2"].mean()
    d["base_x_post"] = d["country"].map(pre_mean) * 1e6 * d["post"]
    no_gdp = ["avg_temp_c", "avg_precip_mm"]

    print("\nCOUNTRY LEVEL (coefficients in 1e-6 mol/m2)")
    variants = {
        "stricter model, all months": (d, {}),
        "without Nov-Feb": (d[~d["month"].isin(WINTER)], {}),
        "without Dec-Feb": (d[~d["month"].isin([12, 1, 2])], {}),
        "May-Sep only": (d[d["month"].between(5, 9)], {}),
        "without December 2023": (d[~((d["year"] == 2023) & (d["month"] == 12))], {}),
        "country-months with at least 10% valid pixel-days": (d[d["coverage"] >= 0.10], {}),
        "2020-2024 only": (d[d["year"] >= 2020], {}),
        "log GDP instead of GDP level": (d, {"controls": no_gdp + ["log_gdp"]}),
        "no GDP": (d, {"controls": no_gdp}),
    }
    for label, (dd, kw) in variants.items():
        res, _ = cfit(dd, **kw)
        out[label] = report(res, dd["country"].nunique())
        line(label, out[label])

    res, _ = cfit(d, weights=d["pixels"].values)
    out["countries weighted by area (pixels)"] = report(res, G)
    line("countries weighted by area (pixels)", out["countries weighted by area (pixels)"])

    res, _ = cfit(d, extra=d[["base_x_post"]])
    out["with pre-treatment level x post"] = {"did": report(res, G), "level_x_post": report(res, G, "base_x_post")}
    line("with pre-treatment level x post: EU term", out["with pre-treatment level x post"]["did"])
    line("  pre-treatment level x post", out["with pre-treatment level x post"]["level_x_post"])

    dl = d[d["mean_no2"] > 0].copy()
    dl["log_no2"] = np.log(dl["mean_no2"])
    for label, kw in (("log outcome", {}), ("log outcome, no GDP", {"controls": no_gdp})):
        res, _ = cfit(dl, outcome="log_no2", scale=1.0, **kw)
        out[label] = report(res, dl["country"].nunique())
        line(label, out[label])

    # 12-month blocks with and without winter
    def blocks(dd, tag):
        ev = pd.get_dummies(dd["event_year"], prefix="ev").astype(float).drop(columns=["ev_-1"]).mul(dd["eu"].values, axis=0)
        base = dd.copy()
        base["did"] = 0.0
        X = cic.drop_collinear(pd.concat([cic.build(base).drop(columns=["did"]), ev], axis=1))
        res = sm.OLS(dd["mean_no2"].values * 1e6, X).fit(cov_type="cluster", cov_kwds={"groups": dd["country"].values})
        labels = {-3: "Jan-Jun 2019", -2: "Jul 2019-Jun 2020", 0: "Jul 2021-Jun 2022", 1: "Jul 2022-Jun 2023",
                  2: "Jul 2023-Jun 2024", 3: "Jul-Dec 2024"}
        out[tag] = {lab: report(res, dd["country"].nunique(), f"ev_{k}") for k, lab in labels.items()}
        print(f"  {tag}: " + " | ".join(f"{lab} {r['coefficient']:+.2f} (p={r['p_t']:.2f})" for lab, r in out[tag].items()))

    blocks(d, "12-month blocks, all months")
    blocks(d[~d["month"].isin(WINTER)], "12-month blocks, without Nov-Feb")
    blocks(d[~((d["year"] == 2023) & (d["month"] == 12))], "12-month blocks, without December 2023")

    out["randomization_inference"] = t_randomization(d)
    r = out["randomization_inference"]
    print(f"  randomization inference: p = {r['p_coefficient']:.3f} on the coefficient, {r['p_t_statistic']:.3f} on the t-statistic")

    neg = d[d["mean_no2"] <= 0][["country", "year", "month", "mean_no2", "coverage"]]
    out["non_positive_country_months"] = neg.to_dict("records")
    print("  non-positive country-months: " + ", ".join(f"{r.country} {r.year}-{r.month:02d}" for r in neg.itertuples()))

    low = cov[(cov["coverage"] < 0.10)]
    out["country_months_below_10pct_coverage"] = int(len(low))
    return out


# Pixel level
def pixel_level(monthly, year, month, masks):
    out = {}
    t = year * 12 + month
    base = grid.period_mean(monthly, month, t <= grid.CUTOFF)
    ok = np.isfinite(base)
    every = np.ones(len(t), bool)

    def panel(edges):
        labels_backup, edges_backup = grid.LABELS, grid.EDGES
        grid.LABELS, grid.EDGES = [str(i) for i in range(len(edges) + 1)], edges
        try:
            return grid.cell_panel(monthly * 1e6, year, month, masks, np.digitize(base * 1e5, edges), ok, every)
        finally:
            grid.LABELS, grid.EDGES = labels_backup, edges_backup

    d = panel(grid.EDGES)
    G = d["country"].nunique()

    def show(label, dd):
        r = grid.matched_did(dd)
        g = dd["country"].nunique()
        for key in ("not_matched", "matched_on_baseline", "matched_from_jul2023"):
            tval = r[key]["coefficient"] / r[key]["se"]
            r[key]["p_t"] = float(2 * stats.t.sf(abs(tval), g - 1))
            half = stats.t.ppf(0.975, g - 1) * r[key]["se"]
            r[key]["ci_t"] = [r[key]["coefficient"] - half, r[key]["coefficient"] + half]
        out[label] = r
        m, l, u = r["matched_on_baseline"], r["matched_from_jul2023"], r["not_matched"]
        print(f"  {label:<42s} unmatched {u['coefficient']:+.2f} (p={u['p_t']:.3f}) | matched {m['coefficient']:+.2f} "
              f"(p={m['p_t']:.3f}) CI [{m['ci_t'][0]:+.2f}, {m['ci_t'][1]:+.2f}] | from Jul 2023 {l['coefficient']:+.2f} (p={l['p_t']:.3f})")

    print("\nPIXEL LEVEL, matched on pre-treatment class (coefficients in 1e-6 mol/m2)")
    show("EU-27 vs all nine comparison countries", d)
    show("EU-27 vs UK, NO, CH, IS", d[(d["eu"] == 1) | d["country"].isin(EEA_UK)])
    show("EU-27 vs Western Balkans", d[(d["eu"] == 1) | d["country"].isin(BALKANS)])
    show("EU-27 vs all nine, without Nov-Feb", d[~d["month"].isin(WINTER)])
    show("EU-27 vs Western Balkans, without Nov-Feb", d[((d["eu"] == 1) | d["country"].isin(BALKANS)) & ~d["month"].isin(WINTER)])

    p = d[d["eu"] == 0].copy()
    tt = p["year"] * 12 + p["month"]
    p["eu"] = p["country"].isin(EEA_UK).astype(float)
    p["did"] = p["eu"] * (tt > grid.CUTOFF)
    p["did_early"] = p["eu"] * ((tt > grid.CUTOFF) & (tt <= grid.LATE))
    p["did_late"] = p["eu"] * (tt > grid.LATE)
    show("placebo: UK, NO, CH, IS vs Western Balkans", p)

    # Does the EU border matter inside one region, and does the region matter inside the EU?
    show("north-west: EU members vs UK, CH", d[d["country"].isin(NW_EU + NW_OUT)])
    show("south-east: EU members vs Western Balkans", d[d["country"].isin(SE_EU + BALKANS)])
    r = d[d["country"].isin(NW_EU + SE_EU)].copy()
    tt = r["year"] * 12 + r["month"]
    r["eu"] = r["country"].isin(NW_EU).astype(float)
    r["did"] = r["eu"] * (tt > grid.CUTOFF)
    r["did_early"] = r["eu"] * ((tt > grid.CUTOFF) & (tt <= grid.LATE))
    r["did_late"] = r["eu"] * (tt > grid.LATE)
    show("inside the EU: north-west vs south-east members", r)
    show("inside the EU: north-west vs south-east, without Nov-Feb", r[~r["month"].isin(WINTER)])

    for label, edges in (("4 classes", [2, 3, 5]), ("16 classes", [1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.5, 4, 4.5, 5, 6, 7, 9])):
        show(f"EU-27 vs all nine, {label}", panel(edges))

    dl = d[d["no2"] > 0].copy()
    dl["no2"] = np.log(dl["no2"])
    show("log outcome, EU-27 vs all nine", dl)

    # Change in the polluted classes, country by country
    early = grid.period_mean(monthly, month, (t > grid.CUTOFF) & (t <= grid.LATE))
    late = grid.period_mean(monthly, month, t > grid.LATE)
    usable = ok & np.isfinite(early) & np.isfinite(late)
    warm = ~np.isin(month, WINTER)
    base_warm = grid.period_mean(monthly[warm], month[warm], (t <= grid.CUTOFF)[warm], need=6)
    late_warm = grid.period_mean(monthly[warm], month[warm], (t > grid.LATE)[warm], need=6)
    polluted = usable & (base * 1e5 > 3) & np.isfinite(base_warm) & np.isfinite(late_warm)
    rows = []
    for code, mask in masks.items():
        sel = mask & polluted
        if sel.sum() >= 20:
            rows.append({"country": code, "group": "comparison" if code in grid.CONTROLS else "EU-27",
                         "pixels_above_3e-5": int(sel.sum()), "pre_mean_1e-6": float(base[sel].mean() * 1e6),
                         "change_from_jul2023_pct": float(100 * (late - base)[sel].mean() / base[sel].mean()),
                         "change_mar_oct_only_pct": float(100 * (late_warm - base_warm)[sel].mean() / base_warm[sel].mean())})
    tab = pd.DataFrame(rows).sort_values("change_from_jul2023_pct")
    out["polluted_pixels_by_country"] = tab.to_dict("records")
    print("\n  Change from Jul 2023 in pixels that started above 3e-5 mol/m2:")
    print("  " + tab.round(1).to_string(index=False).replace("\n", "\n  "))

    # Slope of change on starting level, with a baseline that is not part of the change
    b19 = grid.period_mean(monthly, month, year == 2019)
    mid = grid.period_mean(monthly, month, (year >= 2020) & (t <= grid.CUTOFF))
    inside = np.any(list(masks.values()), axis=0)
    slopes = {}
    for label, x, y in (("change from pre-treatment mean, on that same mean", base, late - base),
                        ("change from 2020-Jun 2021, on the 2019 level", b19, late - mid),
                        ("pre-treatment change (2019 to 2020-Jun 2021), on the 2019 level", b19, mid - b19)):
        sel = inside & np.isfinite(x) & np.isfinite(y)
        fit = sm.OLS(y[sel] * 1e6, sm.add_constant(x[sel] * 1e6)).fit()
        slopes[label] = {"slope": float(fit.params[1]), "r_squared": float(fit.rsquared), "pixels": int(sel.sum())}
        print(f"  slope, {label}: {fit.params[1]:+.3f} (R2={fit.rsquared:.2f})")
    out["slope_of_change_on_starting_level"] = slopes
    return out


def plot_country_change(rows):
    tab = pd.DataFrame(rows).sort_values("change_from_jul2023_pct")
    colors = ["#d95f0e" if g == "comparison" else "#2c7fb8" for g in tab["group"]]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = np.arange(len(tab))
    ax.bar(x, tab["change_from_jul2023_pct"], color=colors)
    ax.scatter(x, tab["change_mar_oct_only_pct"], color="black", s=18, zorder=3, label="March-October only")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(tab["country"])
    ax.set_ylabel("Change in NO₂ from Jul 2023 vs. pre-treatment (%)")
    ax.set_title("Change in NO₂ in polluted pixels, by country\n"
                 "Pixels that started above 3 × 10⁻⁵ mol/m²; Jul 2023 – Dec 2024 against Jan 2019 – Jun 2021", fontsize=12)
    handles = [plt.Rectangle((0, 0), 1, 1, color="#2c7fb8"), plt.Rectangle((0, 0), 1, 1, color="#d95f0e"),
               plt.Line2D([], [], marker="o", color="black", linestyle="", markersize=4)]
    ax.legend(handles, ["EU-27 country", "comparison country", "March-October only"], frameon=False, loc="lower right")
    ax.grid(axis="y", alpha=0.3)
    plt.figtext(0.5, 0.01, "Green Policy Intelligence Engine (GPIE) - Source: Sentinel-5P TROPOMI, Sentinel Hub Process API",
                ha="center", fontsize=8, color="gray")
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    plt.savefig(OUT_PLOT, dpi=200)
    plt.close()
    print(f"Saved: {OUT_PLOT}")


# Synthetic control
def synthetic_control():
    import synthetic_control as sc
    panel = sc.load_series().dropna(subset=["EU27"] + sc.DONORS)
    pre = panel.index <= sc.TREATMENT_DATE

    def fit(p, donors, joint):
        y, X = p.loc[pre, "EU27"].values, p.loc[pre, donors].values
        if joint:                                    # weights fitted on demeaned series
            y, X = y - y.mean(), X - X.mean(axis=0)
        scale = 100.0 * np.abs(X).mean()
        w, _ = nnls(np.vstack([X, scale * np.ones((1, len(donors)))]), np.append(y, scale))
        w = w / w.sum() if w.sum() > 0 else np.ones(len(donors)) / len(donors)
        synth = p[donors].values @ w
        gap = p["EU27"].values - synth
        gap = gap - gap[pre].mean()
        return float(gap[~pre].mean()), float(np.sqrt((gap[pre] ** 2).mean())), dict(zip(donors, w))

    out = {}
    for joint, label in ((False, "weights on levels, then level shift"), (True, "weights and level shift fitted together")):
        att, rmspe, w = fit(panel, sc.DONORS, joint)
        gaps, ratios = {"EU27": att}, {"EU27": abs(att) / rmspe}
        for held in sc.DONORS:
            others = [c for c in sc.DONORS if c != held]
            g, r, _ = fit(panel[[held] + others].rename(columns={held: "EU27"}), others, joint)
            gaps[held], ratios[held] = g, abs(g) / r
        rank_gap = 1 + sum(abs(v) > abs(att) for k, v in gaps.items() if k != "EU27")
        rank_ratio = 1 + sum(v > ratios["EU27"] for k, v in ratios.items() if k != "EU27")
        out[label] = {"gap": att, "pre_rmspe": rmspe, "weights": {k: float(v) for k, v in w.items() if v > 0.005},
                      "rank_by_gap": f"{rank_gap}/{len(gaps)}", "rank_by_gap_over_rmspe": f"{rank_ratio}/{len(gaps)}"}
        print(f"  {label}: gap {att * 1e6:+.2f}, pre-RMSPE {rmspe * 1e6:.2f}, rank {rank_gap}/{len(gaps)} by gap, "
              f"{rank_ratio}/{len(gaps)} by gap/RMSPE, weights {out[label]['weights']}")
    return out


def main():
    z = np.load(grid.GRID_PATH)
    monthly, year, month = grid.load_grid()
    codes = get_all_country_codes()
    masks = build_masks(grid.BBOX, {c: load_country_geometry(c, clip_to_bbox=grid.BBOX) for c in codes}, RES_DEG)
    out = {"country_level": country_level(masks, z["count"].astype("float64"), z["days_present"].astype("float64"), z["months"]),
           "pixel_level": pixel_level(monthly, year, month, masks)}
    plot_country_change(out["pixel_level"]["polluted_pixels_by_country"])
    print("\nSYNTHETIC CONTROL")
    out["synthetic_control"] = synthetic_control()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()
