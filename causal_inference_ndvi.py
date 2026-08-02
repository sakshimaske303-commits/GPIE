import pandas as pd
import numpy as np
import statsmodels.api as sm

# Two-group control DiD (matches causal_inference_final_did.py's design for NO2).
# The original version of this file ran a single-cohort model (EU-27 only, no
# external control group) on master_dataset.csv -- the exact design that the
# placebo test proved unreliable for the primary NO2 outcome. This was an
# oversight: the same control-group correction applied to NO2 was never
# carried over to the NDVI secondary outcome. Fixed here to use the genuine
# 30-country control dataset and the same did_interaction specification.
DATA_PATH = "data/master_dataset_control.csv"


def load_and_prepare():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))

    treatment_date = pd.Timestamp("2021-06-30")
    df["post"] = (df["time"] > treatment_date).astype(float)
    df["did_interaction"] = df["treatment_group"] * df["post"]
    df["month_of_year"] = df["month"]
    return df


def run_did_model(df):
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]

    # Outcome is mean_ndvi instead of mean_no2
    model_df = df.dropna(subset=["mean_ndvi"] + controls).copy()
    print(f"Rows after dropna: {len(model_df)}")

    country_dummies = pd.get_dummies(model_df["country"], prefix="country", drop_first=True).astype(float)
    month_dummies = pd.get_dummies(model_df["month_of_year"], prefix="month", drop_first=True).astype(float)

    X = pd.concat([
        model_df[["did_interaction", "post"] + controls].astype(float),
        country_dummies,
        month_dummies,
    ], axis=1)
    X = sm.add_constant(X)
    y = model_df["mean_ndvi"].astype(float)

    print(f"Design matrix shape: {X.shape}")
    print("Fitting model...")

    model = sm.OLS(y, X)

    # Cluster-robust standard errors, clustered by country: with panel data
    # (repeated monthly observations per country), errors are serially
    # correlated within a country over time, so default OLS standard errors
    # understate true uncertainty (Bertrand, Duflo & Mullainathan, 2004).
    # This matches the same correction applied to the NO2 models.
    results = model.fit(cov_type="cluster", cov_kwds={"groups": model_df["country"]})
    print("Model fit complete!")

    print("\n=== DiD TREATMENT EFFECT ON NDVI (EU x Post-2021, cluster-robust SEs) ===")
    print("Coefficient:", results.params["did_interaction"])
    print("P-value:", results.pvalues["did_interaction"])
    print("95% CI:", results.conf_int().loc["did_interaction"].values)
    print(f"\nR-squared: {results.rsquared:.4f}")
    print(f"N observations: {results.nobs}")

    return results


def main():
    df = load_and_prepare()
    print(f"Dataset shape: {df.shape}")
    print()
    run_did_model(df)


if __name__ == "__main__":
    main()
