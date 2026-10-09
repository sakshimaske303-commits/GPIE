import json
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()


# I read every number on this page from my model outputs, so it can't drift from the code.
def load_json(name):
    with open(os.path.join(PROJECT_ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


ident = load_json("identification_checks.json")
stress = load_json("stress_tests.json")
extra = load_json("additional_checks.json")
real_gdp = load_json("real_gdp_checks.json")
grid_checks = load_json("grid_baseline_checks.json")
country = stress["country_level"]
pixel = stress["pixel_level"]


def e6(x):
    """mol/m2 -> 1e-6 mol/m2."""
    return x * 1e6


def row_ident(label, s):
    return [label, f"{e6(s['coefficient']):+.2f}", f"{e6(s['ci_low']):+.2f} to {e6(s['ci_high']):+.2f}", f"{s['p_value']:.3f}"]


def row_stress(label, s):
    return [label, f"{s['coefficient']:+.2f}", f"{s['ci_t_low']:+.2f} to {s['ci_t_high']:+.2f}", f"{s['p_t']:.3f}"]


def row_extra(label, s, digits=2):
    return [label, f"{s['coefficient']:+.{digits}f}", f"{s['ci_low']:+.{digits}f} to {s['ci_high']:+.{digits}f}",
            f"{s['p_value']:.3f}"]


spec = ident["specifications"]
main = spec["S2 S1 + EU-specific month-of-year effects"]
pct = 100 * main["coefficient"] / ident["eu_pre_treatment_mean"]

st.markdown("<h1 style='text-align: center;'>🔬 RESULTS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>What Does a Country-Level DiD on Satellite NO₂ Identify?</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
**Research question.** When treated and comparison countries differ in baseline pollution, what does a
country-level difference-in-differences on satellite NO₂ identify? **RQ1:** how much of the country-level
estimate is explained by the difference in pre-treatment NO₂ between the groups? **RQ2:** when EU and
comparison areas are compared at the same starting level, where did NO₂ fall?

The European Climate Law (July 2021) is used as a negative-control case: it has a clear date and border but no
plausible dated effect on NO₂, so an estimate that looks like an effect needs another explanation.
""")

st.markdown("---")

# 1. Country-level estimate
st.markdown("### 1. The Country-Level Estimate")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("EU × post (main model)", f"{e6(main['coefficient']):.2f} × 10⁻⁶ mol/m²",
              f"{abs(pct):.1f}% of the EU pre-treatment mean", delta_color="off")
with col2:
    st.metric("p-value", f"{main['p_value']:.3f}", "t distribution, clusters − 1 df", delta_color="off")
with col3:
    st.metric("95% CI (10⁻⁶ mol/m²)", f"{e6(main['ci_low']):.2f} to {e6(main['ci_high']):.2f}", "")

st.markdown(
    "<p class='caption-text'>Main model: country and year-month fixed effects, an EU-specific seasonal cycle, "
    "temperature, precipitation and GDP controls, standard errors clustered by country. EU-27 against nine non-EU "
    "countries, January 2019 – December 2024, July 2021 as the first post-treatment month.</p>",
    unsafe_allow_html=True,
)

conf = ident["confounding"]
rows = [
    row_ident("Baseline: country and common calendar-month FE", spec["S0 headline: country FE + common month-of-year FE + post"]),
    row_ident("Country and year-month FE", spec["S1 country FE + year-month FE"]),
    row_ident("Main model: + EU-specific calendar-month effects", main),
    row_ident("+ wind speed and boundary-layer height", spec["S5 S2 + wind speed + boundary-layer height"]),
    row_ident("+ COVID-19 stringency (34 countries)", conf["with COVID stringency control"]),
    row_ident("Excluding March 2020 – June 2021", conf["excluding Mar 2020 - Jun 2021 (COVID window)"]),
    row_ident("Excluding July 2021 – December 2022", conf["excluding Jul 2021 - Dec 2022 (energy-crisis months)"]),
    row_ident("Excluding 2023 – 2024", conf["excluding 2023 - 2024"]),
    row_stress("2020 – 2024 only", country["2020-2024 only"]),
    row_stress("Without November – February", country["without Nov-Feb"]),
    row_stress("Without December – February", country["without Dec-Feb"]),
    row_stress("May – September only", country["May-Sep only"]),
    row_stress("Without December 2023", country["without December 2023"]),
    row_extra("Without the eight non-positive country-months", extra["country_level"]["without non-positive country-months"]),
    row_stress("Country-months with at least 10% valid pixel-days", country["country-months with at least 10% valid pixel-days"]),
    row_stress("Countries weighted by area", country["countries weighted by area (pixels)"]),
    row_stress("Log GDP in place of GDP", country["log GDP instead of GDP level"]),
    row_stress("No GDP", country["no GDP"]),
    row_extra("Real GDP per capita (PPP) in place of GDP", real_gdp["country_level"]["real GDP per capita, PPP"]),
    row_extra("Log real GDP per capita (PPP) in place of GDP", real_gdp["country_level"]["log real GDP per capita, PPP"]),
]
log_row = country["log outcome"]
rows.append(["Log outcome (log points)", f"{log_row['coefficient']:+.3f}",
             f"{log_row['ci_t_low']:+.3f} to {log_row['ci_t_high']:+.3f}", f"{log_row['p_t']:.3f}"])
st.dataframe(pd.DataFrame(rows, columns=["Specification", "EU × post (10⁻⁶ mol/m²)", "95% CI", "p"]),
             hide_index=True, width="stretch")

ri = country["randomization_inference"]
st.info(
    f"**Stable under the usual checks, fragile under others.** Year-month fixed effects, weather and COVID-19 controls, "
    f"excluding the COVID-19 or energy-crisis months, leaving out any one comparison country and a wild cluster "
    f"bootstrap (p = {ident['inference']['S2']['wild_cluster_bootstrap_p']:.3f}) leave it in place. Without the winter "
    f"months, with area weights, or with log GDP or real GDP per capita it is no longer significant, and randomization inference gives "
    f"p = {ri['p_coefficient']:.2f} on the coefficient (p = {ri['p_t_statistic']:.3f} on the t-statistic)."
)

st.markdown("---")

# 2. Timing
st.markdown("### 2. Timing")
st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "block_event_study.png"), width="stretch")
blocks = ident["event_time_12m_blocks"]
shifts = ident["date_shifts"]
trend = ident["eu_specific_trend"]["did"]
shift_p = [shifts[k]["p_value"] for k in ("-12 months", "-6 months", "+6 months", "+12 months")]
st.markdown(
    f"""
Relative to July 2020 – June 2021, the two pre-treatment blocks are not significant (joint p = {blocks['pre_trend_joint_p']:.2f}),
the first two years after the law show no change (p = {blocks['Jul 2021-Jun 2022']['p_value']:.2f} and
{blocks['Jul 2022-Jun 2023']['p_value']:.2f}), and the estimate comes from July 2023 – June 2024
({e6(blocks['Jul 2023-Jun 2024']['coefficient']):+.2f} × 10⁻⁶, p = {blocks['Jul 2023-Jun 2024']['p_value']:.3f}).
Without November – February the post-treatment blocks become a gradual drift that starts before the law.
Shifting the treatment date by ±6 or ±12 months is also significant (p between {min(shift_p):.3f} and {max(shift_p):.3f}),
and with an EU-specific linear trend the treatment coefficient is {e6(trend['coefficient']):+.2f} × 10⁻⁶ (p = {trend['p_value']:.2f}).
The relative decline is not tied to July 2021.
"""
)

st.markdown("---")

# 3. Composition (RQ1)
st.markdown("### 3. Baseline Composition (RQ1)")
st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "placebo_assignments.png"), width="stretch")
lvl = country["with pre-treatment level x post"]
ec = extra["country_level"]
st.markdown(
    f"""
Across {ri['n_perm']} random assignments of the treatment label to 27 of the 36 countries, the DiD estimate follows
how much more polluted the labelled group was before treatment (r = {ri['correlation_estimate_with_pre_level_gap']:.2f}),
and the EU-27's estimate is what its pre-treatment gap ({ri['real_assignment']['pre_level_gap']:.1f} × 10⁻⁶) predicts.
Random labels are significant at 5% in {100 * ri['share_of_random_assignments_significant_at_5pct']:.1f}% of draws,
because groups that differ in starting level diverge for the same reason.
"""
)
comp_rows = [
    row_stress("+ pre-treatment level × post: EU × post", lvl["did"]),
    row_extra("Without the Netherlands and Belgium", ec["without NL and BE"]),
    row_extra(f"Common support (countries no more polluted than the UK; drops {', '.join(ec['common support']['dropped_countries'])})",
              ec["common support"]),
]
lg = ec["log outcome with log pre-level x post"]
comp_rows.append(["Log outcome + log pre-level × post: EU × post (log points)", f"{lg['did']['coefficient']:+.3f}",
                  f"{lg['did']['ci_low']:+.3f} to {lg['did']['ci_high']:+.3f}", f"{lg['did']['p_value']:.3f}"])
st.dataframe(pd.DataFrame(comp_rows, columns=["Country-level check", "Estimate (10⁻⁶ mol/m²)", "95% CI", "p"]),
             hide_index=True, width="stretch")

st.markdown("#### Pixel level: comparing like with like")
st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "no2_change_by_baseline.png"), width="stretch")
allnine = pixel["EU-27 vs all nine comparison countries"]
um, mt = allnine["not_matched"], allnine["matched_on_baseline"]
diff = pixel["unmatched_minus_matched"]
covid = extra["pixel_level"]["without Mar 2020 - Jun 2021"]["matched_on_baseline"]
px_rows = [
    ["Not matched on pre-treatment class", f"{um['coefficient']:+.2f}", f"{um['ci_t'][0]:+.2f} to {um['ci_t'][1]:+.2f}", f"{um['p_t']:.3f}"],
    ["Matched on pre-treatment class", f"{mt['coefficient']:+.2f}", f"{mt['ci_t'][0]:+.2f} to {mt['ci_t'][1]:+.2f}", f"{mt['p_t']:.3f}"],
    ["Difference, unmatched minus matched (cluster bootstrap)", f"{diff['difference']:+.2f}", f"{diff['ci_low']:+.2f} to {diff['ci_high']:+.2f}", "—"],
    ["Matched, without March 2020 – June 2021", f"{covid['coefficient']:+.2f}", f"{covid['ci_low']:+.2f} to {covid['ci_high']:+.2f}", f"{covid['p_value']:.3f}"],
]
st.dataframe(pd.DataFrame(px_rows, columns=["Model (country × class × month cells)", "EU × post (10⁻⁶ mol/m²)", "95% CI", "p"]),
             hide_index=True, width="stretch")
mb = extra["pixel_level"]["12-month blocks, matched"]
st.markdown(
    f"""
On {grid_checks['pixels']['eu'] + grid_checks['pixels']['control']:,} pixels, the decline grows with the pixel's
pre-treatment level in both groups. Comparing EU pixels only with comparison-group pixels of the same class removes
about {100 * (1 - mt['coefficient'] / um['coefficient']):.0f}% of the estimate. In 12-month blocks the matched
estimate shows no break at the law (all blocks p ≥ {min(v['p_value'] for v in mb.values()):.2f}). Its interval still
admits a relative decline of up to about half the country-level estimate, so the data do not require an effect at
the EU border but cannot rule one out.
"""
)

st.markdown("---")

# 4. Geography (RQ2)
st.markdown("### 4. Where NO₂ Fell (RQ2)")
st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "no2_change_by_country.png"), width="stretch")
st.markdown("""
Polluted pixels lost about 15–25% of their NO₂ in north-western Europe, including the non-EU United Kingdom and
Switzerland, and 0–6% in south-eastern Europe, including EU members and Serbia; polluted western Turkey, outside the
sample, did not decline. The regional contrast depends partly on winter retrievals, and its cause is not identified.
Full detail is on the *Pixel Level Check* page.
""")

st.markdown(
    "<p class='caption-text'>The highly polluted comparison pixels are mostly in the United Kingdom, which shares "
    "EU-derived vehicle emission standards, so this check separates EU membership from pollution level, not EU-origin "
    "regulation from its absence.</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# 5. Positive control
st.markdown("### 5. Positive Control")
st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "positive_control.png"), width="stretch")
pc = load_json("positive_control.json")
fmt_p = lambda v: "<0.001" if v < 0.001 else f"{v:.3f}"
pc_rows = []
for r in pc["reductions"]:
    k = f"{r:.3f}"
    c, p = pc["country_real"][k], pc["pixel_real"][k]
    pc_rows.append(["None (observed data)" if r == 0 else f"{100 * r:g}%",
                    "—" if r == 0 else f"{c['added_reduction']:+.2f}", f"{c['coefficient']:+.2f}", fmt_p(c['p_value']),
                    "—" if r == 0 else f"{p['added_reduction']:+.2f}", f"{p['matched']['coefficient']:+.2f}",
                    fmt_p(p['matched']['p_value'])])
st.dataframe(pd.DataFrame(pc_rows, columns=["Reduction added", "Added (country)", "Country model", "p",
                                            "Added (pixel cells)", "Matched pixel model", "p "]),
             hide_index=True, width="stretch")
rand = pc["country_random"]
st.markdown(
    f"""
A known proportional reduction is added to EU-27 NO₂ from July 2021 and the models are run again. The country model
recovers it in full; the matched pixel model recovers about four-fifths, because it gives the less polluted classes
more weight. A 2.5% reduction moves the matched estimate to {pc['pixel_real']['0.025']['matched']['coefficient']:+.2f}
× 10⁻⁶ (p = {pc['pixel_real']['0.025']['matched']['p_value']:.3f}), and with 80% power it detects a uniform reduction of
{pc['pixel_real']['matched_mde_as_uniform_reduction_pct']:.1f}% ({pc['pixel_real']['matched_minimum_detectable_effect_80pct_power']:.2f} × 10⁻⁶). So the near-zero
matched estimate is not a matter of low power. Across 999 random groups of 27 countries, a 5% reduction is detected
in {100 * rand['0.050']['share_significant_negative']:.0f}% and a 10% reduction in
{100 * rand['0.100']['share_significant_negative']:.0f}%.
"""
)

st.markdown("---")

# Raw group means
st.markdown("### EU-27 vs. Comparison Group — Average NO₂")


@st.cache_data
def load_comparison_data():
    return pd.read_csv(os.path.join(PROJECT_ROOT, "data", "master_dataset_control.csv"))


comp_df = load_comparison_data()
# Same split as the model: July 2021 is the first post-treatment month.
comp_df["period"] = ((comp_df["year"] * 100 + comp_df["month"]) <= 202106).map(
    {True: "Pre (Jan 2019 – Jun 2021)", False: "Post (Jul 2021 – Dec 2024)"})
grouped = comp_df.groupby(["treatment_group", "period"])["mean_no2"].mean().reset_index()
grouped["group_label"] = grouped["treatment_group"].map({1: "EU-27", 0: "Comparison group"})

fig_bar = go.Figure()
colors = {"Pre (Jan 2019 – Jun 2021)": "#7c3aed", "Post (Jul 2021 – Dec 2024)": "#00d4ff"}
for period in ["Pre (Jan 2019 – Jun 2021)", "Post (Jul 2021 – Dec 2024)"]:
    period_data = grouped[grouped["period"] == period]
    fig_bar.add_trace(go.Bar(x=period_data["group_label"], y=period_data["mean_no2"], name=period,
                             marker_color=colors[period]))
fig_bar.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#cbd5e1"),
    barmode="group",
    yaxis_title="Mean NO₂ (mol/m²)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    height=450,
    margin=dict(t=60, b=40, l=40, r=40),
)
st.plotly_chart(fig_bar, width="stretch")
st.markdown(
    "<p class='caption-text'>Raw group means (descriptive). The EU-27 started out about 50% more polluted than the "
    "comparison group, which is the difference the composition checks above are about.</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# Supplementary analyses
with st.expander("Supplementary analyses from earlier stages (not part of the paper)"):
    st.markdown("""
These use the **baseline model** (country and common calendar-month fixed effects), not the main model above.

- **Quarterly event study** (`causal_inference_event_study.py`): with a seasonal cycle common to both groups,
  5 of the 9 pre-treatment quarters and 7 of the 14 post-treatment quarters differ significantly from 2021Q2,
  in a seasonal pattern (positive in Q1/Q4, negative in Q2/Q3). Giving the EU its own seasonal cycle (12-month
  blocks above) removes the pre-treatment differences.
- **Higher/lower-baseline split** (`causal_inference_robustness_checks.py`): the decline is concentrated in the
  14 EU members with higher pre-treatment NO₂. The split is defined by the outcome and was chosen after seeing the
  result; the composition checks above are the formal version of this point.
- **Synthetic control** (`synthetic_control.py`): post-treatment gap −1.45 × 10⁻⁶; the EU-27 ranks 2nd of 10 in
  the in-space placebo (1st by gap relative to pre-treatment fit). With ten units this is weak evidence either way.
- **NDVI** (`causal_inference_ndvi.py`): −0.0194 (p = 0.008). An exploratory association, not evidence that the
  Climate Law affected vegetation: land-use change, drought and agricultural policy are not controlled for.
""")
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "event_study_plot.png"), width="stretch")
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "synthetic_control_gap.png"), width="stretch")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine | Numbers on this page "
    "are read from data/identification_checks.json, data/stress_tests.json, data/additional_checks.json, "
    "data/grid_baseline_checks.json, data/positive_control.json and data/real_gdp_checks.json</p>",
    unsafe_allow_html=True,
)
