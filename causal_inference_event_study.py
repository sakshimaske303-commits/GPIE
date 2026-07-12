import pandas as pd
import numpy as np
import statsmodels.api as sm

DATA_PATH = "data/master_dataset_control.csv"


def load_and_prepare():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))

    # Bin time into quarters relative to the treatment date, for a
    # manageable number of event-time dummies (24 monthly periods would
    # be too many to interpret cleanly; quarters give a readable trend).
    df["quarter"] = df["time"].dt.to_period("Q").astype(str)

    df["month_of_year"] = df["month"]
    return df


def run_event_study(df):
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
    model_df = df.dropna(subset=["mean_no2"] + controls).copy()
    print(f"Rows after dropna: {len(model_df)}")

    # Reference quarter: 2021Q2 (the quarter just before treatment,
    # 30 June 2021 falls at the end of Q2) - all effects are measured
    # relative to this baseline quarter.
    reference_quarter = "2021Q2"

    quarters = sorted(model_df["quarter"].unique())
    quarters_to_include = [q for q in quarters if q != reference_quarter]

    # Build EU x quarter interaction dummies (only for EU/treatment_group=1 rows
    # will these be non-zero, since treatment_group=0 rows get multiplied by 0)
    event_dummies = pd.DataFrame(index=model_df.index)
    for q in quarters_to_include:
        col_name = f"eu_x_{q}"
        event_dummies[col_name] = (
            (model_df["quarter"] == q).astype(float) * model_df["treatment_group"]
        )

    country_dummies = pd.get_dummies(model_df["country"], prefix="country", drop_first=True).astype(float)
    quarter_dummies = pd.get_dummies(model_df["quarter"], prefix="q", drop_first=True).astype(float)

    X = pd.concat([
        event_dummies,
        model_df[controls].astype(float),
        country_dummies,
        quarter_dummies,
    ], axis=1)
    X = sm.add_constant(X)
    y = model_df["mean_no2"].astype(float)

    print(f"Design matrix shape: {X.shape}")
    print("Fitting model...")

    model = sm.OLS(y, X)
    results = model.fit()
    print("Model fit complete!")

    print("\n=== EVENT-STUDY COEFFICIENTS (EU x Quarter, relative to 2021Q2) ===")
    event_cols = [c for c in event_dummies.columns]
    for col in event_cols:
        coef = results.params[col]
        pval = results.pvalues[col]
        sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else ""
        print(f"{col}: {coef:.2e}  (p={pval:.3f}) {sig}")

    return results, event_cols


def main():
    df = load_and_prepare()
    print(f"Dataset shape: {df.shape}")
    print(f"Quarters available: {sorted(df['quarter'].unique())}")
    print()
    run_event_study(df)


if __name__ == "__main__":
    main()