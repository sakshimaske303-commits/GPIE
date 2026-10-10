"""Positive control: I add a known reduction to the real NO2 data and check whether my models find it.
The reduction is proportional (a policy that cuts emissions by r % lowers NO2 by about r %) and starts
in July 2021. I do this for the real EU-27 at country and pixel level, and for 999 random groups of
27 countries to see how often a reduction of each size is detected."""
import json
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import analyse_no2_grid_baseline as grid
import causal_inference_identification_checks as cic
from country_boundaries import get_all_country_codes, load_country_geometry
from s5p_process_daily import RES_DEG, build_masks

OUT_PATH = "data/positive_control.json"
OUT_PLOT = "outputs/plots/positive_control.png"
REDUCTIONS = [0.0, 0.025, 0.05, 0.10]
N_PERM = 999
SEED = 12345

warnings.filterwarnings("ignore", category=RuntimeWarning)


def t_ci(b, se, g):
    half = stats.t.ppf(0.975, g - 1) * se
    return {"coefficient": float(b), "se": float(se), "p_value": float(2 * stats.t.sf(abs(b / se), g - 1)),
            "ci_low": float(b - half), "ci_high": float(b + half)}


def injected(y, treated_post, r):
    """Outcome with the reduction added, and the size of that reduction averaged over treated post months."""
    y_new = np.where(treated_post, y * (1 - r), y)
    return y_new, float(-(r * y[treated_post]).mean())


def country_real(d):
    """Real EU-27, main model (Table 2, row 2)."""
    out = {}
    y = d["mean_no2"].astype(float).values
    tp = (d["did"] == 1).values
    g = d["country"].nunique()
    for r in REDUCTIONS:
        dd = d.copy()
        dd["mean_no2"], true = injected(y, tp, r)
        res, _ = cic.fit(dd)
        s = t_ci(res.params["did"] * 1e6, res.bse["did"] * 1e6, g)
        s["added_reduction"] = true * 1e6
        out[f"{r:.3f}"] = s
    base = out[f"{REDUCTIONS[0]:.3f}"]["coefficient"]
    for v in out.values():
        v["change_from_no_reduction"] = v["coefficient"] - base
        v["share_recovered"] = v["change_from_no_reduction"] / v["added_reduction"] if v["added_reduction"] else None
    return out


def country_random(d):
    """Random groups of 27 countries, the same draws as in my randomization inference."""
    codes, gidx = np.unique(d["country"].values, return_inverse=True)
    g = len(codes)
    y = d["mean_no2"].astype(float).values * 1e6
    post = d["post"].values == 1
    n_obs, n_par = len(d), cic.drop_collinear(cic.build(d)).shape[1]
    correction = np.sqrt(g / (g - 1) * (n_obs - 1) / (n_obs - n_par))
    crit = stats.t.ppf(0.975, g - 1)
    n_treated = int(d.loc[d["eu"] == 1, "country"].nunique())
    countries = np.array(sorted(d["country"].unique()))
    rng = np.random.default_rng(SEED)
    rows = []
    for i in range(N_PERM):
        fake = set(rng.choice(countries, size=n_treated, replace=False))
        dd = d.copy()
        dd["eu_fake"] = dd["country"].isin(fake).astype(float)
        dd["did"] = dd["eu_fake"] * dd["post"]
        Xdf = cic.drop_collinear(cic.build(dd, eu_col="eu_fake"))
        k = list(Xdf.columns).index("did")
        norm = np.sqrt((Xdf["did"].values ** 2).sum())
        X = cic._scale(Xdf.values)
        tp = (dd["did"] == 1).values
        for r in REDUCTIONS:
            y_r, true = injected(y, tp, r)
            b, t = cic._cluster_t(X, y_r, gidx, g, k)
            rows.append({"draw": i, "reduction": r, "estimate": b / norm, "t": t / correction, "added_reduction": true})
    draws = pd.DataFrame(rows)
    out = {}
    for r, grp in draws.groupby("reduction"):
        base = draws.loc[draws["reduction"] == 0, "estimate"].values
        out[f"{r:.3f}"] = {
            "mean_added_reduction": float(grp["added_reduction"].mean()),
            "mean_estimate": float(grp["estimate"].mean()),
            "mean_share_recovered": float(((grp["estimate"].values - base) / grp["added_reduction"].values).mean())
            if r > 0 else None,
            "share_significant_negative": float((grp["t"] < -crit).mean()),
            "share_significant_either_sign": float((grp["t"].abs() > crit).mean())}
    return out


def pixel_real():
    """Real EU-27, pixel-level model matched on the pre-treatment class (Table 4)."""
    monthly, year, month = grid.load_grid()
    t = year * 12 + month
    codes = get_all_country_codes()
    masks = build_masks(grid.BBOX, {c: load_country_geometry(c, clip_to_bbox=grid.BBOX) for c in codes}, RES_DEG)
    base = grid.period_mean(monthly, month, t <= grid.CUTOFF)
    ok = np.isfinite(base)
    d = grid.cell_panel(monthly * 1e6, year, month, masks, np.digitize(base * 1e5, grid.EDGES), ok, np.ones(len(t), bool))
    g = d["country"].nunique()
    y = d["no2"].values.copy()
    tp = (d["did"] == 1).values
    out = {"countries": int(g)}
    for r in REDUCTIONS:
        dd = d.copy()
        dd["no2"], _ = injected(y, tp, r)
        # weighted like the model, so the added reduction is on the same scale as the estimate
        w = dd.loc[tp, "w"].values
        true = float(-(r * y[tp] * w).sum() / w.sum())
        res = grid.matched_did(dd)
        out[f"{r:.3f}"] = {"matched": t_ci(res["matched_on_baseline"]["coefficient"], res["matched_on_baseline"]["se"], g),
                           "not_matched": t_ci(res["not_matched"]["coefficient"], res["not_matched"]["se"], g),
                           "added_reduction": true}
    se = out[f"{REDUCTIONS[0]:.3f}"]["matched"]["se"]
    mde = (stats.t.ppf(0.975, g - 1) + stats.t.ppf(0.80, g - 1)) * se
    out["matched_minimum_detectable_effect_80pct_power"] = float(mde)
    # The matched model recovers only part of a proportional reduction, so I also express this as the
    # uniform reduction (in %) that would move the matched estimate by that much.
    per_pct = (out["0.000"]["matched"]["coefficient"] - out["0.050"]["matched"]["coefficient"]) / 5.0
    out["matched_mde_as_uniform_reduction_pct"] = float(mde / per_pct)
    return out


def plot(country, rand, pixel):
    rs = [r for r in REDUCTIONS if r > 0]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    ax = axes[0]
    x = np.arange(len(rs))
    w = 0.26
    added = [-country[f"{r:.3f}"]["added_reduction"] for r in rs]
    found_c = [-country[f"{r:.3f}"]["change_from_no_reduction"] for r in rs]
    found_p = [-(pixel[f"{r:.3f}"]["matched"]["coefficient"] - pixel["0.000"]["matched"]["coefficient"]) for r in rs]
    ax.bar(x - w, added, w, color="#bdbdbd", label="added to EU-27 data (country level)")
    ax.bar(x, found_c, w, color="#2c7fb8", label="found by the country model")
    ax.bar(x + w, found_p, w, color="#d95f0e", label="found by the matched pixel model")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{100 * r:g}% reduction" for r in rs])
    ax.set_ylabel("Reduction in NO$_2$ (10$^{-6}$ mol/m$^2$)")
    ax.set_title("Real EU-27 data with a reduction added")
    ax.legend(fontsize=8, frameon=False)

    ax = axes[1]
    xs = [100 * r for r in REDUCTIONS]
    ax.plot(xs, [100 * rand[f"{r:.3f}"]["share_significant_negative"] for r in REDUCTIONS], "o-", color="#2c7fb8")
    ax.axhline(2.5, color="grey", ls=":", lw=1)
    ax.set_xlabel("Reduction added to the randomly labelled group (%)")
    ax.set_ylabel("Significant negative estimates (%)")
    ax.set_title(f"{N_PERM} random groups of 27 countries")
    ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(OUT_PLOT, dpi=200)
    print(f"Saved: {OUT_PLOT}")


def main():
    d = cic.load()
    d = d.dropna(subset=["mean_no2"] + cic.BASE_CONTROLS).copy()
    country = country_real(d)
    print("\nCOUNTRY LEVEL, real EU-27 (1e-6 mol/m2)")
    for r, v in country.items():
        print(f"  {100 * float(r):4.1f}%  added {v['added_reduction']:+.2f}  estimate {v['coefficient']:+.2f} "
              f"[{v['ci_low']:+.2f}, {v['ci_high']:+.2f}] p={v['p_value']:.3f}  change {v['change_from_no_reduction']:+.2f}")

    rand = country_random(d)
    print(f"\nCOUNTRY LEVEL, {N_PERM} random groups")
    for r, v in rand.items():
        print(f"  {100 * float(r):4.1f}%  added {v['mean_added_reduction']:+.2f}  mean estimate {v['mean_estimate']:+.2f}  "
              f"significant negative {100 * v['share_significant_negative']:.1f}%  either sign {100 * v['share_significant_either_sign']:.1f}%")

    pixel = pixel_real()
    print(f"\nPIXEL LEVEL, real EU-27 ({pixel['countries']} countries)")
    for r in REDUCTIONS:
        v = pixel[f"{r:.3f}"]
        m = v["matched"]
        print(f"  {100 * r:4.1f}%  added {v['added_reduction']:+.2f}  matched {m['coefficient']:+.2f} "
              f"[{m['ci_low']:+.2f}, {m['ci_high']:+.2f}] p={m['p_value']:.3f}  not matched {v['not_matched']['coefficient']:+.2f}")
    print(f"  matched model, smallest effect detected with 80% power: {pixel['matched_minimum_detectable_effect_80pct_power']:.2f} "
          f"(a uniform reduction of {pixel['matched_mde_as_uniform_reduction_pct']:.1f}%)")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"reductions": REDUCTIONS, "country_real": country, "country_random": rand, "pixel_real": pixel}, f, indent=2)
    print(f"\nSaved: {OUT_PATH}")
    plot(country, rand, pixel)


if __name__ == "__main__":
    main()
