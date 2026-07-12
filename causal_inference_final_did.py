import pandas as pd
import numpy as np
import statsmodels.api as sm

DATA_PATH = "data/master_dataset_control.csv"


def load_and_prepare():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))

    treatment_date = pd.Timestamp("2021-06-30")
    df["post"] = (df["time"] > treatment_date).astype(float)

    # The core DiD term: 1 only for EU countries AFTER the policy date
    df["did_interaction"] = df["treatment_group"] * df["post"]

    df["month_of_year"] = df["month"]
    return df


def run_did_model(df):
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
    model_df = df.dropna(subset=["mean_no2"] + controls).copy()
    print(f"Rows after dropna: {len(model_df)}")

    country_dummies = pd.get_dummies(model_df["country"], prefix="country", drop_first=True).astype(float)
    month_dummies = pd.get_dummies(model_df["month_of_year"], prefix="month", drop_first=True).astype(float)

    # Note: treatment_group and post are included as main effects (standard
    # DiD practice), alongside the interaction term which is the actual
    # causal estimate of interest. Country fixed effects absorb the
    # treatment_group main effect's country-level component; post's
    # variation is captured via month dummies plus this explicit term.
    X = pd.concat([
        model_df[["did_interaction", "post"] + controls].astype(float),
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

    print("\n=== DiD TREATMENT EFFECT (EU x Post-2021) ===")
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