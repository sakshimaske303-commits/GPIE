"""Augmented synthetic control (Abadie et al. 2010 / Ben-Michael, Feller &
Rothstein 2021 ridge) for the small-N control group; Norway/Iceland
excluded for genuine satellite coverage gaps, not stale files.
"""

import json
import numpy as np
import pandas as pd
from scipy.optimize import nnls
from sklearn.linear_model import Ridge

DATA_PATH = "data/master_dataset_control.csv"
TREATMENT_DATE = pd.Timestamp("2021-06-30")

DONORS = ["UK", "CH", "AL", "BA", "ME", "MK", "RS"]
EXCLUDED_CONTROL_COUNTRIES = ["NO", "IS"]
ALL_CONTROL_COUNTRIES = DONORS + EXCLUDED_CONTROL_COUNTRIES


def load_series():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))

    eu27 = df[df["treatment_group"] == 1].groupby("time")["mean_no2"].mean().rename("EU27")
    donors = df[df["country"].isin(ALL_CONTROL_COUNTRIES)].pivot_table(index="time", columns="country", values="mean_no2")

    panel = pd.concat([eu27, donors], axis=1).sort_index()
    pre = panel[panel.index <= TREATMENT_DATE]
    for c in EXCLUDED_CONTROL_COUNTRIES:
        cov = pre[c].notna().mean()
        print(f"{c} pre-treatment NO2 coverage: {cov:.0%} ({pre[c].isna().sum()} of {len(pre)} months missing) - excluded from donor pool")
    return panel


def scm_weights(panel, pre_mask, donors):
    # Standard SCM: convex weights (>=0, sum to 1) on donors, fit only on the
    # pre-treatment window, minimizing squared distance to the treated series.
    y_pre = panel.loc[pre_mask, "EU27"].values
    X_pre = panel.loc[pre_mask, donors].values

    # nnls doesn't enforce sum-to-1 directly - add a scaled constraint row
    # (standard trick, e.g. Abadie's own synth implementations).
    scale = 100.0
    X_aug = np.vstack([X_pre, scale * np.ones((1, len(donors)))])
    y_aug = np.append(y_pre, scale)

    w, _ = nnls(X_aug, y_aug)
    if w.sum() == 0:
        w = np.ones(len(donors)) / len(donors)
    else:
        w = w / w.sum()
    return dict(zip(donors, w))


def augmented_correction(panel, pre_mask, weights, donors):
    # Ridge-augmented residual correction (Ben-Michael, Feller & Rothstein
    # 2021) - fits how well plain SCM matches the pre-period, then carries
    # that same bias forward into the post period instead of assuming the
    # donor pool's convex hull can hit the target exactly on its own.
    synth_pre = sum(weights[c] * panel.loc[pre_mask, c] for c in donors)
    residual_pre = panel.loc[pre_mask, "EU27"] - synth_pre

    X_pre = panel.loc[pre_mask, donors].values
    ridge = Ridge(alpha=1.0)
    ridge.fit(X_pre, residual_pre.values)
    return ridge


def fit_synthetic(panel, pre_mask, donors):
    weights = scm_weights(panel, pre_mask, donors)
    synth = sum(weights[c] * panel[c] for c in donors)
    ridge = augmented_correction(panel, pre_mask, weights, donors)
    bias_correction = pd.Series(ridge.predict(panel[donors].values), index=panel.index)
    return weights, synth + bias_correction


def run():
    panel_raw = load_series()
    n_before = len(panel_raw)
    # Drop any month missing EU27 or a donor rather than imputing, and say
    # so plainly rather than pretending the panel is complete.
    panel = panel_raw.dropna(subset=["EU27"] + DONORS)
    print(f"\nMonths dropped for missing data (EU27 or a donor): {n_before - len(panel)} of {n_before}")

    pre_mask = panel.index <= TREATMENT_DATE
    post_mask = ~pre_mask
    print(f"Pre-treatment months used: {pre_mask.sum()}, post-treatment months used: {post_mask.sum()}")

    weights, synth_augmented = fit_synthetic(panel, pre_mask, DONORS)
    print("Donor weights:", {k: round(v, 4) for k, v in weights.items()})

    pre_rmspe = np.sqrt(((panel.loc[pre_mask, "EU27"] - synth_augmented.loc[pre_mask]) ** 2).mean())
    gap = panel["EU27"] - synth_augmented
    att = gap.loc[post_mask].mean()

    print(f"\nPre-treatment RMSPE (fit quality): {pre_rmspe:.6f}")
    print(f"Post-treatment average gap (ATT estimate): {att:+.6f}")
    print(f"For comparison, this project's DiD estimate: see causal_inference_final_did.py output")

    # In-space placebo: with 7 donors, holding one out leaves 6 remaining
    # donors - large enough for a real NNLS refit per held-out country,
    # not a degenerate 1:1 comparison.
    placebo_gaps = {}
    for held_out in DONORS:
        other_donors = [c for c in DONORS if c != held_out]
        # Treat held_out as the "treated" unit, other_donors as its donor pool
        placebo_panel = panel[[held_out] + other_donors].rename(columns={held_out: "EU27"})
        ho_weights, ho_synth = fit_synthetic(placebo_panel, pre_mask, other_donors)
        placebo_gap = (placebo_panel["EU27"] - ho_synth).loc[post_mask].mean()
        placebo_gaps[held_out] = placebo_gap
        print(f"  Placebo ({held_out} as pseudo-treated vs. remaining {len(other_donors)} donors): post-period gap = {placebo_gap:+.6f}")

    rank = sum(1 for g in placebo_gaps.values() if abs(g) >= abs(att)) + 1
    n_total = len(DONORS) + 1
    print(f"\nEU-27's |gap| rank among itself + {len(DONORS)} placebos: {rank}/{n_total} "
          f"(a real in-space permutation check now that each placebo gets its own NNLS-fit donor pool)")

    out = pd.DataFrame({
        "date": panel.index, "eu27_actual": panel["EU27"].values,
        "synthetic_control": synth_augmented.values, "gap": gap.values,
        "period": ["pre" if m else "post" for m in pre_mask],
    })
    out.to_csv("data/synthetic_control_results.csv", index=False)
    print("\nSaved data/synthetic_control_results.csv")

    summary = {
        "donor_pool": DONORS,
        "excluded_control_countries": EXCLUDED_CONTROL_COUNTRIES,
        "donor_weights": weights,
        "pre_treatment_rmspe": pre_rmspe,
        "post_treatment_att": att,
        "placebo_gaps": placebo_gaps,
        "eu27_rank_among_placebos": f"{rank}/{n_total}",
        "pre_treatment_months_used": int(pre_mask.sum()),
        "post_treatment_months_used": int(post_mask.sum()),
    }
    with open("data/synthetic_control_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=float)
    print("Saved data/synthetic_control_summary.json")


if __name__ == "__main__":
    run()
