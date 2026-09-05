"""Single-cohort DiD model (all 27 EU countries, before vs. after 30 June 2021,
no external control group) WITH an explicit linear time_trend control added as a
robustness diagnostic (see the comment on `time_trend` below). This is the
time-trend-controlled specification discussed in GPIE_Research_Paper.md's
treatment-of-secular-trend discussion (coefficient becomes statistically
indistinguishable from zero once the trend is controlled for).

Note for reproducibility: this file previously WAS the project's "Initial Model"
(before `time_trend` was added) - the p = 0.041 (cluster-robust) / p = 0.026
(classical) figure that README.md, GPIE_Research_Paper.md,
and the dashboard's 7_Causal_Results.py error-box all attribute to "the Initial
Model" is NOT reproduced by running this file as it stands today. That original,
pre-time_trend specification now lives in `causal_inference_initial_model.py`
instead, added specifically to restore that traceability.
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

    # Explicit linear time trend, so the treatment coefficient captures
    # deviation from the ongoing secular trend rather than absorbing
    # the entire multi-year declining-trend itself.
    df["time_trend"] = (df["time"] - df["time"].min()).dt.days.astype(float)

    return df


def run_did_model(df):
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur", "time_trend"]
    model_df = df.dropna(subset=["mean_no2"] + controls).copy()
    print(f"Rows after dropna: {len(model_df)}")

    # Build dummies manually and force float dtype explicitly,
    # avoiding a suspected bool-dtype incompatibility with this
    # environment's numpy/patsy linear algebra routines.
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

    # Cluster-robust standard errors, clustered by country (see
    # causal_inference_final_did.py for rationale) - kept consistent across
    # every model in this project.
    results = model.fit(cov_type="cluster", cov_kwds={"groups": model_df["NUTS_ID"]})
    print("Model fit complete!")

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