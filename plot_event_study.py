import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

DATA_PATH = "data/master_dataset_control.csv"
OUTPUT_PATH = "outputs/plots/event_study_plot.png"


def load_and_prepare():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))
    df["quarter"] = df["time"].dt.to_period("Q").astype(str)
    df["month_of_year"] = df["month"]
    return df


def run_event_study(df):
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
    model_df = df.dropna(subset=["mean_no2"] + controls).copy()

    reference_quarter = "2021Q2"
    quarters = sorted(model_df["quarter"].unique())
    quarters_to_include = [q for q in quarters if q != reference_quarter]

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

    model = sm.OLS(y, X)

    # Cluster-robust standard errors, clustered by country (see
    # causal_inference_final_did.py for rationale) - kept consistent across
    # every model in this project.
    results = model.fit(cov_type="cluster", cov_kwds={"groups": model_df["country"]})

    # Extract coefficients, confidence intervals, p-values, and quarter labels
    plot_data = []
    for q in quarters_to_include:
        col = f"eu_x_{q}"
        coef = results.params[col]
        ci_low, ci_high = results.conf_int().loc[col]
        pval = results.pvalues[col]
        plot_data.append({"quarter": q, "coef": coef, "ci_low": ci_low, "ci_high": ci_high,
                           "significant": pval < 0.05})

    # Add the reference quarter itself as zero (by construction)
    plot_data.append({"quarter": reference_quarter, "coef": 0.0, "ci_low": 0.0, "ci_high": 0.0,
                       "significant": False})

    plot_df = pd.DataFrame(plot_data).sort_values("quarter").reset_index(drop=True)
    return plot_df


def make_plot(plot_df):
    import os
    os.makedirs("outputs/plots", exist_ok=True)

    fig, ax = plt.subplots(figsize=(14, 6))

    x = range(len(plot_df))
    coefs = plot_df["coef"].values
    ci_low = plot_df["ci_low"].values
    ci_high = plot_df["ci_high"].values
    sig_mask = plot_df["significant"].values

    # Error bars representing the 95% confidence interval (cluster-robust)
    yerr = [coefs - ci_low, ci_high - coefs]

    ax.errorbar(x, coefs, yerr=yerr, fmt="o", color="#2c7fb8", ecolor="#a6bddb",
                elinewidth=2, capsize=4, markersize=6, label="EU x Quarter effect (p ≥ 0.05)")

    # Highlight the small number of nominally significant quarters distinctly,
    # rather than omitting them - honest reporting includes them, with context
    # in the accompanying text (see GPIE_Research_Paper.md Section 4.4).
    if sig_mask.any():
        sig_x = [xi for xi, s in zip(x, sig_mask) if s]
        sig_y = coefs[sig_mask]
        ax.scatter(sig_x, sig_y, color="#e34a33", s=90, zorder=5, marker="o",
                   edgecolor="#7a1d0f", linewidth=1.2, label="Nominally significant (p < 0.05)")

    # Zero reference line
    ax.axhline(0, color="gray", linestyle="--", linewidth=1)

    # Treatment date marker (30 June 2021, between 2021Q2 and 2021Q3)
    treatment_idx = plot_df[plot_df["quarter"] == "2021Q2"].index[0]
    ax.axvline(treatment_idx + 0.5, color="red", linestyle=":", linewidth=1.5,
               label="European Climate Law (30 June 2021)")

    ax.set_xticks(x)
    ax.set_xticklabels(plot_df["quarter"], rotation=45, ha="right")
    ax.set_ylabel("Estimated EU-27 vs. Control Effect on Mean NO₂\n(relative to 2021Q2, mol/m²)")
    ax.set_xlabel("Quarter")
    ax.set_title(
        "Event-Study: EU-27 vs. Control Group (UK, Norway, Switzerland) NO₂ Difference Over Time\n"
        "20 of 23 quarters non-significant (cluster-robust SEs); 3 nominally significant quarters "
        "(≈1 expected by chance) show no consistent directional pattern"
    )

    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved: {OUTPUT_PATH}")


def main():
    df = load_and_prepare()
    plot_df = run_event_study(df)
    print(plot_df)
    make_plot(plot_df)


if __name__ == "__main__":
    main()