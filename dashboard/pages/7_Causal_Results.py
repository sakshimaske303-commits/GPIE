import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>🔬 CAUSAL INFERENCE RESULTS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>Did the European Climate Law Measurably Reduce NO₂?</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

_checks = [
    "Cluster-Robust SEs (country-clustered)",
    "External Comparison Group (9 non-EU countries)",
    "Placebo Test (exposed a flawed initial design)",
    "23-Quarter Event-Study Check",
    "Baseline-Pollution Split (post-hoc)",
    "Treatment-Date &amp; EU-Trend Checks",
    "Synthetic Control (intercept-adjusted)",
    "Moran's I Spatial-Autocorrelation Check",
    "Minimum Detectable Effect Quantified (~5.5%)",
    "Honest, Nuanced Result Disclosed",
]
_badges = "".join(
    f"""<span style="display:inline-flex; align-items:center; gap:6px; background:rgba(0,135,149,0.10);
        border:1px solid rgba(0,135,149,0.35); border-radius:20px; padding:6px 14px; margin:4px;
        font-size:0.82rem; color:{PALETTE['text']}; font-weight:600;">
        <span style="color:{PALETTE['lagoon']}; font-weight:800;">✓</span>{c}</span>"""
    for c in _checks
)
st.markdown(
    f"""
    <p style="color:{PALETTE['coral']}; text-transform:uppercase; letter-spacing:1.5px;
              font-weight:700; font-size:0.85rem; margin-bottom:6px;">Robustness At a Glance</p>
    <div style="display:flex; flex-wrap:wrap; margin-bottom: 6px;">{_badges}</div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

st.markdown("### The Final Model: Two-Group Difference-in-Differences")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("DiD Coefficient (Pooled)", "−1.52 × 10⁻⁶", "≈ 4.9% of EU pre-treatment mean", delta_color="off")
with col2:
    st.metric("P-value", "0.013", "Significant at 5%", delta_color="off")
with col3:
    st.metric("95% CI", "excludes zero", "[-2.73e-6, -3.16e-7]", delta_color="off")

st.markdown(
    "<p class='caption-text'>Standard errors are clustered by country to account for "
    "within-country serial correlation in this panel (Bertrand, Duflo & Mullainathan, 2004).</p>",
    unsafe_allow_html=True,
)

st.warning(
    "**Result: NO₂ fell more in the EU-27 than in the comparison group — but the timing does not point to the "
    "Climate Law.** The pooled estimate is significant (p = 0.013; −4.2% on the log scale, p = 0.034). However, "
    "nothing changes in the first two years after the law and the whole decline appears from July 2023, every "
    "alternative cutoff date (±6/±12 months) is also significant, and once a steady EU-specific trend is allowed "
    "the treatment-date effect disappears (+8.7 × 10⁻⁷, p = 0.243). The data fit a relative decline that emerges "
    "about two years after the law, not a step change at it. (Earlier versions of this dashboard reported a pooled null, p = 0.101; that was "
    "based on end-of-month NO₂ snapshots and is superseded — see Methodology.)"
)

st.markdown("---")

st.markdown("""
### Event Study

To check the timing of this result, the treatment effect was estimated **separately for every 
individual quarter** from 2019 to 2024, rather than as a single average. This serves two purposes: 
checking whether EU and comparison countries already diverged **before** treatment, and checking whether a delayed effect might have been 
hidden by averaging across the full post-treatment period.
""")

st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "event_study_plot.png"), use_container_width=True)

st.markdown("""
**Finding**: 7 of the 9 pre-treatment quarters differ significantly from the reference quarter, so the
EU-27 and the comparison group were **not** on parallel trends before the law. The coefficients follow a
seasonal pattern — positive in Q1/Q4, negative in Q2/Q3 — that continues after treatment (8 of 14
post-treatment quarters significant, 6 negative). This is what a larger seasonal NO₂ cycle in the more
polluted EU countries would produce; it is not a dated policy response. The coefficients come from a single
regression with a shared reference quarter, so they are not independent tests.
""")

st.markdown("---")

st.markdown("### Heterogeneity by Baseline Pollution Level")

st.markdown("""
The pooled EU-27 estimate could mask differences between countries. This post-hoc check splits
the EU-27 at the median pre-treatment NO₂ level into 14 higher-baseline and 13 lower-baseline
countries, each estimated separately against the full comparison group:
""")

hcol1, hcol2 = st.columns(2)
with hcol1:
    st.metric("Higher-Baseline Subgroup (level)", "−2.85 × 10⁻⁶", "p = 0.002", delta_color="off")
    st.caption("Log scale: −6.4%, p = 0.006")
with hcol2:
    st.metric("Lower-Baseline Subgroup (level)", "+0.09 × 10⁻⁶", "p = 0.758", delta_color="off")
    st.caption("Log scale: −1.5%, p = 0.409")

st.warning(
    "**The relative decline is concentrated in the more polluted member states, on both the level and the "
    "log scale.** This describes where NO₂ fell, not why: the split was chosen after seeing the pooled result, "
    "is defined by the outcome itself, and the same timing problems (pre-treatment differences, significant "
    "alternative dates, EU-specific trend) apply to it."
)

st.markdown("---")

st.markdown("### Additional Checks: Synthetic Control &amp; Spatial Diagnostics")

st.markdown("""
Two further checks on the pooled estimate.
""")

sc1, sc2 = st.columns(2)
with sc1:
    st.markdown("**Synthetic Control (intercept-adjusted)**")
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "synthetic_control_gap.png"), use_container_width=True)
    st.markdown(
        "<p class='caption-text'>Donor pool: all 9 comparison countries, weighted rather than averaged equally "
        "(weights: Serbia 40%, Switzerland 32%, UK 28%). Post-treatment gap = −8.1×10⁻⁷ over 36 complete-data "
        "months; pre-treatment fit error (RMSPE) = 2.56×10⁻⁶. In the in-space placebo the EU-27 gap ranks 5th of "
        "10 — it does not stand out from untreated countries.</p>",
        unsafe_allow_html=True,
    )
with sc2:
    st.markdown("**Moran's I Spatial Autocorrelation**")
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "moran_lisa_cluster_map.png"), use_container_width=True)
    st.markdown(
        "<p class='caption-text'>Raw NO₂ levels are strongly spatially clustered (I=0.578, p=0.001) — "
        "pollution crosses borders. The DiD residuals, tested month by month, are also clustered "
        "(median I = 0.347; significant in 59 of 72 months), so the fixed effects do not remove the "
        "cross-border dependence and the country-clustered p-values are likely too small.</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

st.markdown("### Identification and Inference Checks")

st.markdown("""
These checks re-estimate the two-group model with **year-month fixed effects** and an **EU-specific seasonal
cycle**, add meteorological and COVID-19 controls, and test the result with methods suited to a small number
of comparison countries (`causal_inference_identification_checks.py`).
""")

_checks = pd.DataFrame([
    ["Headline model (common seasonal cycle)", "−1.52 × 10⁻⁶", "0.013"],
    ["Year-month FE + EU-specific seasonality", "−1.34 × 10⁻⁶", "0.016"],
    ["  + wind speed and boundary-layer height", "−1.36 × 10⁻⁶", "0.016"],
    ["  + COVID-19 stringency index (34 countries)", "−1.48 × 10⁻⁶", "0.014"],
    ["  without GDP", "−1.31 × 10⁻⁶", "0.074"],
    ["  excluding Mar 2020 – Jun 2021 (COVID-19 window)", "−2.25 × 10⁻⁶", "0.011"],
    ["  excluding Jul 2021 – Dec 2022 (energy-crisis months)", "−2.08 × 10⁻⁶", "0.005"],
    ["  excluding 2023 – 2024", "−2.6 × 10⁻⁷", "0.545"],
], columns=["Specification", "Coefficient (mol/m²)", "p (cluster-robust)"])
st.dataframe(_checks, hide_index=True, use_container_width=True)

_blocks = pd.DataFrame([
    ["Jan – Jun 2019 (pre)", "+1.93 × 10⁻⁶", "0.168"],
    ["Jul 2019 – Jun 2020 (pre)", "+1.5 × 10⁻⁷", "0.773"],
    ["Jul 2020 – Jun 2021 (reference)", "0", "—"],
    ["Jul 2021 – Jun 2022", "+1 × 10⁻⁸", "0.982"],
    ["Jul 2022 – Jun 2023", "−5.1 × 10⁻⁷", "0.441"],
    ["Jul 2023 – Jun 2024", "−2.18 × 10⁻⁶", "0.008"],
    ["Jul – Dec 2024", "−1.25 × 10⁻⁶", "0.137"],
], columns=["12-month block", "EU vs. comparison (mol/m²)", "p"])
st.dataframe(_blocks, hide_index=True, use_container_width=True)

st.markdown(
    "<p class='caption-text'>With an EU-specific seasonal cycle the pre-treatment blocks are not significant "
    "(joint p = 0.292), so the quarterly pre-treatment differences were largely seasonal. But the first two "
    "post-treatment years show nothing, and the decline appears only from July 2023. Wild cluster bootstrap "
    "p = 0.018; randomization inference p = 0.16. The NO₂ values come from one consistent reprocessed record "
    "(v2.4.0) up to July 2022 and operational v2.4–2.7 products afterwards, so there is no processor change at "
    "the treatment date.</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

st.markdown("### Pixel-Level Check: Pollution Level or EU Membership?")

st.markdown("""
On a 0.1° grid, NO₂ fell in proportion to how polluted each pixel was before treatment, and it fell the same
way in comparison-group pixels with the same starting level. Comparing like with like removes most of the
country-level estimate, so that estimate is largely a **composition effect**: EU countries contain more highly
polluted areas (`analyse_no2_grid_baseline.py`).
""")

st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "no2_change_by_baseline.png"), use_container_width=True)

_matched = pd.DataFrame([
    ["Not matched on pre-treatment level", "−1.34 × 10⁻⁶", "0.012"],
    ["Matched on pre-treatment level", "−0.21 × 10⁻⁶", "0.341"],
    ["Matched, Jul 2021 – Jun 2023", "−0.00 × 10⁻⁶", "0.993"],
    ["Matched, from Jul 2023", "−0.52 × 10⁻⁶", "0.221"],
], columns=["Model (country × class × month cells)", "EU × post (mol/m²)", "p"])
st.dataframe(_matched, hide_index=True, use_container_width=True)

st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "no2_change_map.png"), use_container_width=True)

st.markdown(
    "<p class='caption-text'>The highly polluted comparison pixels are mostly in the United Kingdom, which kept "
    "EU-derived emission standards, so this check separates EU membership from pollution level, not EU-origin "
    "regulation from its absence.</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

st.markdown("### How This Result Was Reached")

st.markdown("""
This finding was not the project's first result — it emerged after two corrections that
changed the analysis:
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.error("**1️⃣ Initial Model**\n\nSingle-cohort design (all EU countries, no control group) found a seemingly significant effect (p=0.026 as originally computed with classical SEs; p=0.041 cluster-robust, still significant — see Methodology). Reproducible via `causal_inference_initial_model.py`.")
with col2:
    st.error("**2️⃣ Placebo Test Failed**\n\nTesting a fake treatment date found an equally 'significant' effect — the single-cohort design could not separate the policy date from Europe's ongoing NO₂ decline")
with col3:
    st.success("**3️⃣ Control Group Added, Data Corrected**\n\nA non-EU comparison group was built, and the NO₂ series was later rebuilt as true monthly means (it had been end-of-month snapshots). The estimates on this page use both corrections.")

st.markdown("---")

st.markdown("### Full Regression Output")

coef_data = {
    "Variable": ["DiD Interaction (treatment_group × post)", "Post (main effect)",
                 "Average Temperature", "Average Precipitation", "GDP"],
    "Coefficient": ["−1.52 × 10⁻⁶", "—", "—", "—", "—"],
    "P-value (cluster-robust)": ["0.013", "—", "—", "—", "—"],
    "Interpretation": [
        "Core estimate (pooled) — significant at 5%, but not robust to an EU-specific trend or alternative dates",
        "Common trend, shared by both groups",
        "Control variable",
        "Control variable",
        "Control variable (removing GDP barely moves the estimate — see Methodology page)",
    ],
}
coef_df = pd.DataFrame(coef_data)
st.dataframe(coef_df, use_container_width=True, hide_index=True)

st.markdown(
    "<p class='caption-text'>Full model includes country and calendar-month fixed effects "
    "(coefficients omitted here for readability — full output available in the project repository).</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

st.markdown("### EU-27 vs. Control Group — Average NO₂ Comparison")


@st.cache_data
def load_comparison_data():
    df = pd.read_csv(os.path.join(PROJECT_ROOT, "data", "master_dataset_control.csv"))
    return df


comp_df = load_comparison_data()
# Same split as the model: July 2021 is the first post-treatment month.
comp_df["period"] = ((comp_df["year"] * 100 + comp_df["month"]) <= 202106).map(
    {True: "Pre (Jan 2019 – Jun 2021)", False: "Post (Jul 2021 – Dec 2024)"})

grouped = comp_df.groupby(["treatment_group", "period"])["mean_no2"].mean().reset_index()
grouped["group_label"] = grouped["treatment_group"].map({1: "EU-27 (Treatment)", 0: "Control Group"})

fig_bar = go.Figure()
colors = {"Pre (Jan 2019 – Jun 2021)": "#7c3aed", "Post (Jul 2021 – Dec 2024)": "#00d4ff"}

for period in grouped["period"].unique():
    period_data = grouped[grouped["period"] == period]
    fig_bar.add_trace(go.Bar(
        x=period_data["group_label"],
        y=period_data["mean_no2"],
        name=period,
        marker_color=colors[period],
    ))

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

st.plotly_chart(fig_bar, use_container_width=True)

st.markdown(
    "<p class='caption-text'>Raw group means (descriptive): the EU-27 mean falls by about 5% while the comparison-group "
    "mean is almost unchanged. The DiD model confirms the difference is significant; the timing checks above show it "
    "is not tied to the Climate Law's date.</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

st.markdown("### Secondary Outcome: NDVI (Vegetation Health)")

st.markdown("""
The same two-group, control-adjusted design used for NO₂ was also applied to NDVI. An earlier
single-cohort NDVI model (mirroring NO₂'s already-invalidated original design) was originally
reported as finding no effect (p=0.128) — a later verification pass found that figure had used
classical, not cluster-robust, standard errors; correctly re-estimated, that same initial model
was already significant (p=0.0017). Either way, a single-cohort design can't reliably isolate a
policy-specific effect from a general trend, so the two-group estimate below is the one reported:
""")

ncol1, ncol2, ncol3 = st.columns(3)
with ncol1:
    st.metric("NDVI DiD Coefficient", "−0.0194")
with ncol2:
    st.metric("P-value", "0.005", "Significant", delta_color="off")
with ncol3:
    st.metric("95% CI", "excludes zero", "[-0.0330, -0.0058]", delta_color="off")

st.error(
    "**A statistically significant relative decline in EU-27 vegetation health versus the "
    "comparison group after the Climate Law date.** This is not interpreted as "
    "evidence the Climate Law itself reduced vegetation health — the Climate Law is an "
    "emissions-focused instrument, not a land-use policy, and this analysis does not control for "
    "land-use change, drought/precipitation-driven vegetation stress, or agricultural-policy "
    "shifts between treatment and control regions. It is reported as an exploratory association, "
    "not a causal claim."
)

st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "ndvi_eu_vs_control_bar_chart.png"), use_container_width=True)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine | Full methodology on the following pages</p>",
    unsafe_allow_html=True,
)