"""5 additional robustness checks on the DiD result: GDP removed,
log-transformed outcome, treatment-date sensitivity, baseline-pollution
split, minimum detectable effect.
"""
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

DATA_PATH = "data/master_dataset_control.csv"
TRUE_TREATMENT_DATE = pd.Timestamp("2021-06-30")


def load_base():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))
    df["month_of_year"] = df["month"]
    return df


def fit_did(model_df, outcome_col, controls, treatment_col="did_interaction"):
    country_dummies = pd.get_dummies(model_df["country"], prefix="country", drop_first=True).astype(float)
    month_dummies = pd.get_dummies(model_df["month_of_year"], prefix="month", drop_first=True).astype(float)

    X = pd.concat([
        model_df[[treatment_col, "post"] + controls].astype(float),
        country_dummies,
        month_dummies,
    ], axis=1)
    X = sm.add_constant(X)
    y = model_df[outcome_col].astype(float)

    model = sm.OLS(y, X)
    return model.fit(cov_type="cluster", cov_kwds={"groups": model_df["country"]})


def check_gdp_removed(df):
    print("\n--- GDP removed ---")
    controls = ["avg_temp_c", "avg_precip_mm"]
    d = df.copy()
    d["post"] = (d["time"] > TRUE_TREATMENT_DATE).astype(float)
    d["did_interaction"] = d["treatment_group"] * d["post"]
    model_df = d.dropna(subset=["mean_no2"] + controls).copy()
    print(f"Rows: {len(model_df)}")
    results = fit_did(model_df, "mean_no2", controls)
    coef = results.params["did_interaction"]
    pval = results.pvalues["did_interaction"]
    print(f"Coefficient: {coef:.4e}  p={pval:.3f}")
    return {"coefficient": coef, "p_value": pval, "n": int(results.nobs)}


def check_log_transform(df):
    print("\n--- Log-transformed outcome ---")
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
    d = df.copy()
    d["post"] = (d["time"] > TRUE_TREATMENT_DATE).astype(float)
    d["did_interaction"] = d["treatment_group"] * d["post"]
    model_df = d.dropna(subset=["mean_no2"] + controls).copy()

    n_nonpositive = (model_df["mean_no2"] <= 0).sum()
    print(f"Non-positive mean_no2 observations excluded: {n_nonpositive} of {len(model_df)}")
    model_df = model_df[model_df["mean_no2"] > 0].copy()
    model_df["log_no2"] = np.log(model_df["mean_no2"])

    results = fit_did(model_df, "log_no2", controls)
    coef = results.params["did_interaction"]
    pval = results.pvalues["did_interaction"]
    print(f"Coefficient: {coef:.4f}  p={pval:.3f}  (rows: {len(model_df)})")
    return {"coefficient": coef, "p_value": pval, "n": int(results.nobs), "n_excluded_nonpositive": int(n_nonpositive)}


def check_treatment_date_sensitivity(df):
    print("\n--- Treatment-date sensitivity ---")
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
    dates = {
        "-12mo": pd.Timestamp("2020-06-30"),
        "-6mo": pd.Timestamp("2020-12-31"),
        "true": TRUE_TREATMENT_DATE,
        "+6mo": pd.Timestamp("2021-12-31"),
        "+12mo": pd.Timestamp("2022-06-30"),
    }
    results_out = {}
    for label, date in dates.items():
        d = df.copy()
        d["post"] = (d["time"] > date).astype(float)
        d["did_interaction"] = d["treatment_group"] * d["post"]
        model_df = d.dropna(subset=["mean_no2"] + controls).copy()
        results = fit_did(model_df, "mean_no2", controls)
        coef = results.params["did_interaction"]
        pval = results.pvalues["did_interaction"]
        print(f"{label} ({date.date()}): coefficient={coef:.4e}  p={pval:.3f}")
        results_out[label] = {"date": str(date.date()), "coefficient": coef, "p_value": pval}
    return results_out


def check_baseline_split(df):
    print("\n--- Heterogeneity by baseline pollution level ---")
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
    d = df.copy()
    d["post"] = (d["time"] > TRUE_TREATMENT_DATE).astype(float)
    d["did_interaction"] = d["treatment_group"] * d["post"]

    pre = d[(d["time"] <= TRUE_TREATMENT_DATE) & (d["treatment_group"] == 1)]
    baseline = pre.groupby("country")["mean_no2"].mean()
    median_baseline = baseline.median()
    higher = set(baseline[baseline >= median_baseline].index)
    lower = set(baseline[baseline < median_baseline].index)
    print(f"Higher-baseline EU countries ({len(higher)}): {sorted(higher)}")
    print(f"Lower-baseline EU countries ({len(lower)}): {sorted(lower)}")

    out = {}
    for label, eu_subset in [("higher_baseline", higher), ("lower_baseline", lower)]:
        subset_df = d[(d["treatment_group"] == 0) | (d["country"].isin(eu_subset))].copy()
        model_df = subset_df.dropna(subset=["mean_no2"] + controls).copy()
        results = fit_did(model_df, "mean_no2", controls)
        coef = results.params["did_interaction"]
        pval = results.pvalues["did_interaction"]
        print(f"{label}: coefficient={coef:.4e}  p={pval:.3f}  (n={len(model_df)})")
        out[label] = {"coefficient": coef, "p_value": pval, "n": int(results.nobs), "countries": sorted(eu_subset)}
    return out


def check_minimum_detectable_effect(df, headline_coef):
    print("\n--- Minimum detectable effect ---")
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
    d = df.copy()
    d["post"] = (d["time"] > TRUE_TREATMENT_DATE).astype(float)
    d["did_interaction"] = d["treatment_group"] * d["post"]
    model_df = d.dropna(subset=["mean_no2"] + controls).copy()
    results = fit_did(model_df, "mean_no2", controls)

    se = results.bse["did_interaction"]
    # 80% power, two-sided 5% test: MDE = SE * (z_{1-alpha/2} + z_{power})
    mde = se * (1.959964 + 0.841621)

    baseline_mean = model_df.loc[model_df["treatment_group"] == 1, "mean_no2"].mean()
    mde_pct = abs(mde / baseline_mean) * 100
    print(f"Standard error: {se:.4e}")
    print(f"Minimum detectable effect (80% power): {mde:.4e}")
    print(f"Baseline EU-27 mean NO2: {baseline_mean:.4e}")
    print(f"MDE as % of baseline: {mde_pct:.1f}%")
    return {"se": se, "mde": mde, "baseline_mean": baseline_mean, "mde_pct_of_baseline": mde_pct}


def main():
    df = load_base()
    print(f"Dataset shape: {df.shape}")

    out = {}
    out["gdp_removed"] = check_gdp_removed(df)
    out["log_transform"] = check_log_transform(df)
    out["treatment_date_sensitivity"] = check_treatment_date_sensitivity(df)
    out["baseline_pollution_split"] = check_baseline_split(df)
    out["minimum_detectable_effect"] = check_minimum_detectable_effect(
        df, headline_coef=out["treatment_date_sensitivity"]["true"]["coefficient"]
    )

    with open("data/robustness_checks.json", "w") as f:
        json.dump(out, f, indent=2, default=float)
    print("\nSaved data/robustness_checks.json")


if __name__ == "__main__":
    main()
