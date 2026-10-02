"""I stress-test my NO2 DiD: stronger fixed effects, timing checks, few-cluster inference
and COVID / energy-crisis confounding."""
import json
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

DATA_PATH = "data/master_dataset_control.csv"
MET_PATH = "data/era5_wind_blh_country_monthly.csv"          # optional
OXCGRT_PATH = "data/covid/oxcgrt_stringency_national.csv"   # optional
OUT_PATH = "data/identification_checks.json"

TREATMENT_DATE = pd.Timestamp("2021-06-30")   # July 2021 = first post month
BASE_CONTROLS = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
SEED = 12345
N_BOOT = 9999
N_PERM = 2000

EEA_UK = ["NO", "IS", "CH", "UK"]              # these follow much of EU climate law
BALKANS = ["AL", "BA", "ME", "MK", "RS"]

ISO3 = {"AT": "AUT", "BE": "BEL", "BG": "BGR", "HR": "HRV", "CY": "CYP", "CZ": "CZE", "DK": "DNK",
        "EE": "EST", "FI": "FIN", "FR": "FRA", "DE": "DEU", "EL": "GRC", "HU": "HUN", "IE": "IRL",
        "IT": "ITA", "LV": "LVA", "LT": "LTU", "LU": "LUX", "MT": "MLT", "NL": "NLD", "PL": "POL",
        "PT": "PRT", "RO": "ROU", "SK": "SVK", "SI": "SVN", "ES": "ESP", "SE": "SWE", "UK": "GBR",
        "NO": "NOR", "CH": "CHE", "IS": "ISL", "AL": "ALB", "BA": "BIH", "ME": "MNE", "MK": "MKD",
        "RS": "SRB"}


# Data
def load():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))
    df["ym"] = df["time"].dt.strftime("%Y-%m")
    df["post"] = (df["time"] > TREATMENT_DATE).astype(float)
    df["eu"] = df["treatment_group"].astype(float)
    df["did"] = df["eu"] * df["post"]
    # months since July 2021 (July 2021 = 0)
    df["rel_month"] = (df["time"].dt.year - 2021) * 12 + (df["time"].dt.month - 7)
    df["event_year"] = np.floor(df["rel_month"] / 12).astype(int)   # -3 .. 3
    df["t_years"] = df["rel_month"] / 12.0

    if os.path.exists(MET_PATH):
        met = pd.read_csv(MET_PATH)
        df = df.merge(met, on=["country", "year", "month"], how="left")
    if os.path.exists(OXCGRT_PATH):
        ox = pd.read_csv(OXCGRT_PATH, low_memory=False,
                         usecols=["CountryCode", "Jurisdiction", "Date", "StringencyIndex_Average"])
        ox = ox[ox["Jurisdiction"] == "NAT_TOTAL"].copy()
        ox["Date"] = pd.to_datetime(ox["Date"].astype(str), format="%Y%m%d")
        ox["year"], ox["month"] = ox["Date"].dt.year, ox["Date"].dt.month
        m = ox.groupby(["CountryCode", "year", "month"])["StringencyIndex_Average"].mean().reset_index()
        back = {v: k for k, v in ISO3.items()}
        m["country"] = m["CountryCode"].map(back)
        m = m.dropna(subset=["country"]).rename(columns={"StringencyIndex_Average": "stringency"})
        df = df.merge(m[["country", "year", "month", "stringency"]], on=["country", "year", "month"], how="left")
        covered = set(m["country"])
        # The index only covers 2020-2022. Outside that I set it to 0 (no measures).
        outside = (df["year"] < 2020) | (df["year"] > 2022)
        df.loc[outside & df["country"].isin(covered), "stringency"] = 0.0
    return df


# Model building
def build(d, time_fe=True, group_season=True, controls=BASE_CONTROLS, extra=None, eu_col="eu"):
    """Design matrix. 'did' is always the first column after the constant."""
    parts = [d[["did"]].astype(float)]
    if extra is not None:
        parts.append(extra.astype(float))
    if controls:
        parts.append(d[controls].astype(float))
    parts.append(pd.get_dummies(d["country"], prefix="c", drop_first=True).astype(float))
    if time_fe:
        parts.append(pd.get_dummies(d["ym"], prefix="t", drop_first=True).astype(float))
    else:
        parts.append(d[["post"]].astype(float))
        parts.append(pd.get_dummies(d["month"], prefix="m", drop_first=True).astype(float))
    if group_season:
        gs = pd.get_dummies(d["month"], prefix="eu_m", drop_first=True).astype(float)
        parts.append(gs.mul(d[eu_col].values, axis=0))
    X = pd.concat(parts, axis=1)
    X.insert(0, "const", 1.0)
    return X


def drop_collinear(X):
    """Drop columns that are exact linear combinations of earlier ones."""
    A = X.values
    q, r = np.linalg.qr(A)
    keep = np.abs(np.diag(r)) > 1e-9 * np.abs(np.diag(r)).max()
    return X.loc[:, keep]


def fit(d, outcome="mean_no2", **kw):
    X = drop_collinear(build(d, **kw))
    res = sm.OLS(d[outcome].astype(float).values, X).fit(cov_type="cluster", cov_kwds={"groups": d["country"].values})
    return res, X


def summ(res, name="did"):
    ci = res.conf_int().loc[name].values
    return {"coefficient": float(res.params[name]), "se": float(res.bse[name]), "p_value": float(res.pvalues[name]),
            "ci_low": float(ci[0]), "ci_high": float(ci[1]), "n": int(res.nobs)}


def show(label, s):
    print(f"  {label:<58s} {s['coefficient']: .3e}  p={s['p_value']:.3f}  n={s['n']}")


# Few-cluster inference
def _scale(X):
    """Unit-norm columns. GDP is ~1e5-1e6 next to 0/1 dummies, which makes X'X badly
    conditioned. Scaling does not change the t statistics."""
    return X / np.sqrt((X ** 2).sum(axis=0))


def _cluster_t(X, y, groups_idx, n_groups, k):
    """beta_k and its unscaled cluster-robust t statistic. X must be column-scaled."""
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    u = y - X @ beta
    z = X @ XtX_inv[:, k]                      # influence weights for beta_k
    s = np.bincount(groups_idx, weights=z * u, minlength=n_groups)
    return beta[k], beta[k] / np.sqrt((s ** 2).sum())


def wild_cluster_bootstrap(d, n_boot=N_BOOT, seed=SEED, **kw):
    """Restricted wild cluster bootstrap-t (Cameron, Gelbach & Miller 2008), H0: did = 0."""
    Xdf = drop_collinear(build(d, **kw))
    X = _scale(Xdf.values)
    y = d["mean_no2"].astype(float).values * 1e6
    k = list(Xdf.columns).index("did")
    codes, groups_idx = np.unique(d["country"].values, return_inverse=True)
    G = len(codes)
    _, t_obs = _cluster_t(X, y, groups_idx, G, k)

    Xr = np.delete(X, k, axis=1)               # restricted model imposes did = 0
    br = np.linalg.solve(Xr.T @ Xr, Xr.T @ y)
    fitted_r, u_r = Xr @ br, y - Xr @ br

    XtX_inv = np.linalg.inv(X.T @ X)
    P = XtX_inv @ X.T
    z = X @ XtX_inv[:, k]
    rng = np.random.default_rng(seed)
    t_star = np.empty(n_boot)
    for b in range(n_boot):
        w = rng.choice([-1.0, 1.0], size=G)[groups_idx]
        ys = fitted_r + u_r * w
        beta = P @ ys
        u = ys - X @ beta
        s = np.bincount(groups_idx, weights=z * u, minlength=G)
        t_star[b] = beta[k] / np.sqrt((s ** 2).sum())
    return float((np.abs(t_star) >= abs(t_obs)).mean())


def randomization_inference(d, n_perm=N_PERM, seed=SEED, **kw):
    """I give the 'EU' label to random sets of countries (same group sizes) and refit."""
    obs, _ = fit(d, **kw)
    b_obs = obs.params["did"]
    countries = np.array(sorted(d["country"].unique()))
    n_treated = int(d.groupby("country")["eu"].first().sum())
    rng = np.random.default_rng(seed)
    y = d["mean_no2"].astype(float).values
    draws = np.empty(n_perm)
    for i in range(n_perm):
        fake = set(rng.choice(countries, size=n_treated, replace=False))
        dd = d.copy()
        dd["eu_fake"] = dd["country"].isin(fake).astype(float)
        dd["did"] = dd["eu_fake"] * dd["post"]
        X = drop_collinear(build(dd, eu_col="eu_fake", **kw)).values
        k = 1  # const, did
        norms = np.sqrt((X ** 2).sum(axis=0))
        beta = np.linalg.lstsq(X / norms, y, rcond=None)[0]
        draws[i] = beta[k] / norms[k]
    return float((np.abs(draws) >= abs(b_obs)).mean())


def main():
    df = load()
    d = df.dropna(subset=["mean_no2"] + BASE_CONTROLS).copy()
    out = {"n_countries": int(d["country"].nunique()), "n_obs": int(len(d))}
    pre_mean_eu = d[(d["eu"] == 1) & (d["post"] == 0)]["mean_no2"].mean()
    out["eu_pre_treatment_mean"] = float(pre_mean_eu)

    # A. Specification
    print("\nA. SPECIFICATION")
    specs = {
        "S0 headline: country FE + common month-of-year FE + post": dict(time_fe=False, group_season=False),
        "S1 country FE + year-month FE": dict(time_fe=True, group_season=False),
        "S2 S1 + EU-specific month-of-year effects": dict(time_fe=True, group_season=True),
        "S3 S2 without GDP": dict(time_fe=True, group_season=True, controls=["avg_temp_c", "avg_precip_mm"]),
        "S4 S2 without any controls": dict(time_fe=True, group_season=True, controls=[]),
    }
    out["specifications"] = {}
    for label, kw in specs.items():
        res, _ = fit(d, **kw)
        s = summ(res)
        s["pct_of_eu_pre_mean"] = 100 * s["coefficient"] / pre_mean_eu
        out["specifications"][label] = s
        show(label, s)

    dl = d[d["mean_no2"] > 0].copy()
    dl["log_no2"] = np.log(dl["mean_no2"])
    res, _ = fit(dl, outcome="log_no2")
    out["specifications"]["S2 log outcome"] = summ(res)
    show("S2 log outcome", out["specifications"]["S2 log outcome"])

    met_cols = [c for c in ["wind_speed_ms", "blh_m"] if c in d.columns]
    if met_cols:
        dm = d.dropna(subset=met_cols)
        res, _ = fit(dm, controls=BASE_CONTROLS + met_cols)
        out["specifications"]["S5 S2 + wind speed + boundary-layer height"] = summ(res)
        show("S5 S2 + wind speed + boundary-layer height", out["specifications"]["S5 S2 + wind speed + boundary-layer height"])
        out["met_coefficients"] = {c: {"coefficient": float(res.params[c]), "p_value": float(res.pvalues[c])} for c in met_cols}
    else:
        print("  (S5 wind/boundary-layer controls skipped: data/era5_wind_blh_country_monthly.csv not found)")

    # B. Timing
    print("\nB. TIMING (under S2)")
    ev = pd.get_dummies(d["event_year"], prefix="ev").astype(float)
    ev = ev.drop(columns=["ev_-1"]).mul(d["eu"].values, axis=0)        # ref = Jul 2020 - Jun 2021
    dd = d.copy()
    dd["did"] = 0.0                                                    # placeholder, dropped as collinear
    X = drop_collinear(pd.concat([build(dd).drop(columns=["did"]), ev], axis=1))
    res = sm.OLS(d["mean_no2"].values, X).fit(cov_type="cluster", cov_kwds={"groups": d["country"].values})
    labels = {-3: "Jan-Jun 2019", -2: "Jul 2019-Jun 2020", 0: "Jul 2021-Jun 2022", 1: "Jul 2022-Jun 2023",
              2: "Jul 2023-Jun 2024", 3: "Jul-Dec 2024"}
    out["event_time_12m_blocks"] = {"reference": "Jul 2020-Jun 2021"}
    for k, lab in labels.items():
        s = summ(res, f"ev_{k}")
        out["event_time_12m_blocks"][lab] = s
        show(("pre  " if k < 0 else "post ") + lab, s)
    pre_names = [f"ev_{k}" for k in (-3, -2)]
    R = np.zeros((2, len(res.params)))
    for i, nme in enumerate(pre_names):
        R[i, list(X.columns).index(nme)] = 1
    w = res.wald_test(R, scalar=True, use_f=False)
    out["event_time_12m_blocks"]["pre_trend_joint_p"] = float(w.pvalue)
    print(f"  joint test of the two pre-period blocks: p={float(w.pvalue):.3f}")

    extra = pd.DataFrame({"eu_trend": d["eu"] * d["t_years"]}, index=d.index)
    res, _ = fit(d, extra=extra)
    out["eu_specific_trend"] = {"did": summ(res), "trend_per_year": summ(res, "eu_trend")}
    show("DiD with EU-specific linear trend", out["eu_specific_trend"]["did"])
    show("  EU-specific trend (per year)", out["eu_specific_trend"]["trend_per_year"])

    out["date_shifts"] = {}
    for shift in (-12, -6, 0, 6, 12):
        cut = TREATMENT_DATE + pd.DateOffset(months=shift)
        dd = d.copy()
        dd["post"] = (dd["time"] > cut).astype(float)
        dd["did"] = dd["eu"] * dd["post"]
        res, _ = fit(dd)
        out["date_shifts"][f"{shift:+d} months"] = summ(res)
        show(f"treatment date shifted {shift:+d} months", out["date_shifts"][f"{shift:+d} months"])

    out["pre_period_placebos"] = {}
    pre = d[d["post"] == 0]
    for cut in ("2020-01-31", "2020-06-30", "2020-12-31"):
        dd = pre.copy()
        dd["post"] = (dd["time"] > pd.Timestamp(cut)).astype(float)
        dd["did"] = dd["eu"] * dd["post"]
        res, _ = fit(dd)
        out["pre_period_placebos"][cut] = summ(res)
        show(f"pre-period-only placebo at {cut}", out["pre_period_placebos"][cut])

    # C. Inference. Only 9 of my 36 clusters are controls, so I also bootstrap and permute.
    print("\nC. INFERENCE WITH FEW CONTROL CLUSTERS")
    out["inference"] = {}
    for label, kw in (("S0", dict(time_fe=False, group_season=False)), ("S2", dict())):
        res, _ = fit(d, **kw)
        p_wcb = wild_cluster_bootstrap(d, **kw)
        p_ri = randomization_inference(d, **kw)
        out["inference"][label] = {"cluster_robust_p": float(res.pvalues["did"]),
                                   "wild_cluster_bootstrap_p": p_wcb, "randomization_inference_p": p_ri,
                                   "n_boot": N_BOOT, "n_perm": N_PERM}
        print(f"  {label}: cluster-robust p={res.pvalues['did']:.3f} | wild cluster bootstrap p={p_wcb:.3f} "
              f"| randomization inference p={p_ri:.3f}")

    out["leave_one_control_out"] = {}
    for c in sorted(d[d["eu"] == 0]["country"].unique()):
        res, _ = fit(d[d["country"] != c])
        out["leave_one_control_out"][c] = summ(res)
        show(f"S2 without control country {c}", out["leave_one_control_out"][c])

    out["control_subgroups"] = {}
    for label, keep in (("EU-27 vs NO, IS, CH, UK", EEA_UK), ("EU-27 vs Western Balkans (AL, BA, ME, MK, RS)", BALKANS)):
        sub = d[(d["eu"] == 1) | d["country"].isin(keep)]
        res, _ = fit(sub)
        out["control_subgroups"][label] = summ(res)
        show("S2 " + label, out["control_subgroups"][label])

    # D. Confounding
    print("\nD. COVID / ENERGY-CRISIS CONFOUNDING (under S2)")
    out["confounding"] = {}
    if "stringency" in d.columns:
        ds = d.dropna(subset=["stringency"])
        res0, _ = fit(ds)
        res1, _ = fit(ds, controls=BASE_CONTROLS + ["stringency"])
        out["confounding"]["same sample, no stringency control"] = summ(res0)
        out["confounding"]["with COVID stringency control"] = summ(res1)
        out["confounding"]["stringency_coefficient"] = summ(res1, "stringency")
        out["confounding"]["stringency_countries"] = int(ds["country"].nunique())
        show(f"S2 on the {ds['country'].nunique()} countries with stringency data", summ(res0))
        show("S2 + COVID stringency index", summ(res1))
        show("  stringency coefficient (per index point)", summ(res1, "stringency"))
    else:
        print("  (stringency control skipped: OxCGRT file not found)")

    for label, mask in (
        ("excluding all of 2020", d["year"] != 2020),
        ("excluding Mar 2020 - Jun 2021 (COVID window)", ~((d["time"] >= "2020-03-01") & (d["time"] <= "2021-06-30"))),
        ("excluding Jul 2021 - Dec 2022 (energy-crisis months)", ~((d["time"] >= "2021-07-01") & (d["time"] <= "2022-12-31"))),
        ("excluding 2023 - 2024", d["year"] <= 2022),
    ):
        res, _ = fit(d[mask])
        out["confounding"][label] = summ(res)
        show("S2 " + label, out["confounding"][label])

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()
