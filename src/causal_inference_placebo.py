import pandas as pd
import numpy as np
import statsmodels.api as sm

import sys

# Default is my original EU-27 panel. --corrected uses the EU-27 rows of the current panel.
CORRECTED = "--corrected" in sys.argv
DATA_PATH = "data/master_dataset_control.csv" if CORRECTED else "data/master_dataset.csv"


def load_and_prepare(fake_treatment_date):
    df = pd.read_csv(DATA_PATH)
    if CORRECTED:
        df = df[df["treatment_group"] == 1].rename(columns={"country": "NUTS_ID"}).copy()
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))

    # Placebo: I use a fake cutoff. A significant effect here would mean my real result
    # is picking up a trend and not the policy.
    df["treatment"] = (df["time"] > fake_treatment_date).astype(float)
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

    print("Fitting model...")
    model = sm.OLS(y, X)

    # I cluster by country because monthly errors within a country are correlated.
    results = model.fit(cov_type="cluster", cov_kwds={"groups": model_df["NUTS_ID"]})
    print("Model fit complete!")

    print("\n=== PLACEBO TREATMENT EFFECT (should be non-significant, cluster-robust SEs) ===")
    print("Coefficient:", results.params["treatment"])
    print("P-value:", results.pvalues["treatment"])
    print("95% CI:", results.conf_int().loc["treatment"].values)

    return results


def main():
    # Fake date is one year before the real cutoff. No Green Deal policy event falls on it.
    fake_date = pd.Timestamp("2020-06-30")

    df = load_and_prepare(fake_date)
    print(f"Testing placebo treatment date: {fake_date.date()}")
    print()
    run_did_model(df)


if __name__ == "__main__":
    main()