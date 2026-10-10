"""I run the EU-27 before/after model (no control group) with a linear time trend added.
My first model without the trend is in causal_inference_initial_model.py."""
import pandas as pd
import numpy as np
import statsmodels.api as sm

import sys

# Default is my original EU-27 panel. --corrected uses the EU-27 rows of the current panel.
CORRECTED = "--corrected" in sys.argv
DATA_PATH = "data/master_dataset_control.csv" if CORRECTED else "data/master_dataset.csv"


def load_and_prepare():
    df = pd.read_csv(DATA_PATH)
    if CORRECTED:
        df = df[df["treatment_group"] == 1].rename(columns={"country": "NUTS_ID"}).copy()
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))
    # Cutoff 2021-06-30 makes July 2021 my first post-treatment month.
    treatment_date = pd.Timestamp("2021-06-30")
    df["treatment"] = (df["time"] > treatment_date).astype(float)
    df["month_of_year"] = df["month"]

    # I add a linear trend so the treatment term does not absorb the long-run NO2 decline.
    df["time_trend"] = (df["time"] - df["time"].min()).dt.days.astype(float)

    return df


def run_did_model(df):
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur", "time_trend"]
    model_df = df.dropna(subset=["mean_no2"] + controls).copy()
    print(f"Rows after dropna: {len(model_df)}")

    # I cast the dummies to float because bool columns gave me trouble in the OLS fit.
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

    # I cluster by country because monthly errors within a country are correlated.
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