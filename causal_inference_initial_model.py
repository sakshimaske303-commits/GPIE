"""Reproduces the "Initial Model" result cited by README.md, GPIE_Project_Report.md
("Initial model." section), GPIE_Research_Paper.md (Section 4.1), and the dashboard's
5_Causal_Results.py error-box: the first single-cohort DiD model (all 27 EU countries,
before vs. after 30 June 2021, no external control group), BEFORE the later linear
time_trend diagnostic control was added.

Why this file exists: `causal_inference.py` was edited after this project's docs were
written to add an explicit `time_trend` control as a robustness diagnostic (see its
own docstring). That is a legitimate, separately-documented result in its own right
(GPIE_Research_Paper.md's discussion of the time-trend-controlled specification) - but
it means running the CURRENT `causal_inference.py` no longer reproduces the "Initial
Model, p = 0.041 (cluster-robust) / p = 0.026 (classical, as originally computed)"
figure that README/Project Report/Research Paper/dashboard all attribute to the
project's first model, and that no separate script on disk reproduced. This file
restores that traceability: it is `causal_inference.py`'s original specification
(identical data, identical fixed effects, identical controls) with only the later
`time_trend` addition removed, so the documented Initial Model figure has a script
that reproduces it exactly again.

Cross-checked independently (from-scratch OLS + cluster-robust SE, outside
statsmodels): coefficient = -2.285028e-06, p = 0.0263 (classical/homoskedastic
SEs), p = 0.0414 (cluster-robust, clustered by country) - matching the
documented p = 0.026 / p = 0.041 to 3+ significant figures.
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm

DATA_PATH = "data/master_dataset.csv"


def load_and_prepare():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))
    treatment_date = pd.Timestamp("2021-06-30")
    df["treatment"] = (df["time"] > treatment_date).astype(float)
    df["month_of_year"] = df["month"]
    return df


def run_did_model(df):
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
    model_df = df.dropna(subset=["mean_no2"] + controls).copy()
    print(f"Rows after dropna: {len(model_df)}")

    country_dummies = pd.get_dummies(model_df["NUTS_ID"], prefix="country", drop_first=True).astype(float)
    month_dummies = pd.get_dummies(model_df["month_of_year"], prefix="month", drop_first=True).astype(float)

    X = pd.concat([
        model_df[["treatment"] + controls].astype(float),
        country_dummies,
        month_dummies,
    ], axis=1)
    X = sm.add_constant(X)
    y = model_df["mean_no2"].astype(float)

    print(f"Design matrix shape: {X.shape}")
    print("Fitting model...")

    model = sm.OLS(y, X)

    # As originally computed: classical (non-clustered) standard errors.
    results_classical = model.fit()
    print("\n=== TREATMENT EFFECT (classical SEs, as originally computed) ===")
    print("Coefficient:", results_classical.params["treatment"])
    print("P-value:", results_classical.pvalues["treatment"])

    # Cluster-robust standard errors, clustered by country - the corrected
    # figure used everywhere else in this project (see Dev Log for the
    # correction, and causal_inference_final_did.py for the final two-group
    # model this initial single-cohort result was superseded by).
    results = model.fit(cov_type="cluster", cov_kwds={"groups": model_df["NUTS_ID"]})
    print("\n=== TREATMENT EFFECT (cluster-robust SEs) ===")
    print("Coefficient:", results.params["treatment"])
    print("P-value:", results.pvalues["treatment"])
    print("95% CI:", results.conf_int().loc["treatment"].values)
    print(f"\nR-squared: {results.rsquared:.4f}")
    print(f"N observations: {results.nobs}")

    return results


def main():
    df = load_and_prepare()
    print(f"Dataset shape: {df.shape}")
    print(f"Countries: {df['NUTS_ID'].nunique()}")
    print()
    run_did_model(df)


if __name__ == "__main__":
    main()
