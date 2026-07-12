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
    results = model.fit()
    print("Model fit complete!")

    print("\n=== TREATMENT EFFECT ===")
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