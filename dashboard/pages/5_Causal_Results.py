import streamlit as st
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
    "Genuine External Control Group (9 non-EU countries)",
    "Placebo Test (caught &amp; fixed a flawed initial design)",
    "23-Quarter Event-Study Check",
    "Baseline-Pollution Heterogeneity Check (significant)",
    "5 Additional Robustness Checks",
    "Augmented Synthetic Control (Independent Method)",
    "Moran's I Spatial-Autocorrelation Check",
    "Minimum Detectable Effect Quantified (12.7%)",
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
    st.metric("DiD Coefficient (Pooled)", "−2.22 × 10⁻⁶")
with col2:
    st.metric("P-value", "0.101", "Not significant")
with col3:
    st.metric("95% CI", "spans zero", "[-4.87e-6, +4.32e-7]")

st.markdown(
    "<p class='caption-text'>Standard errors are clustered by country to account for "
    "within-country serial correlation in this panel (Bertrand, Duflo & Mullainathan, 2004).</p>",
    unsafe_allow_html=True,
)

st.warning(
    "**Result: No statistically distinguishable pooled, EU-wide effect detected at the conventional 5% level.** "
    "Once genuinely compared against a 9-country non-EU control group, the pooled NO₂ decline observed in EU-27 "
    "countries is not statistically different from the decline observed in the control group over the same period — "
    "though the p-value (0.101) is noticeably closer to conventional significance than a smaller control group's "
    "estimate. At 80% statistical power, this design can reliably detect a pooled effect of roughly 12.7% of "
    "baseline EU NO₂ or larger. A heterogeneity check below finds the pooled null conceals a statistically "
    "significant effect concentrated in higher-baseline, more industrialized EU countries."
)

st.markdown("---")

st.markdown("""
### Event-Study Validation

To test this result's robustness, the treatment effect was estimated **separately for every 
individual quarter** from 2019 to 2024, rather than as a single average. This serves two purposes: 
verifying that EU and control-group countries followed similar trends **before** treatment 
(supporting the model's core assumption), and checking whether a delayed effect might have been 
hidden by averaging across the full post-treatment period.
""")

st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "event_study_plot.png"), use_container_width=True)

st.markdown("""
**Finding**: Under cluster-robust standard errors, 19 of the 23 quarters — both before and after
the 30 June 2021 treatment date — show no statistically significant effect, and every pre-treatment
quarter is non-significant, supporting the model's parallel-trends assumption. Four post-treatment
quarters are nominally significant (2022Q2, 2023Q2, 2024Q2, 2024Q3) — more than the ~1 false
positive expected by chance across 23 independent tests — and, unlike a thinner control group's
event study, these four form a consistent pattern: all negative, all falling in the second or
third calendar quarter. This corroborates the heterogeneity finding below rather than the pooled
average alone.
""")

st.markdown("---")

st.markdown("### Heterogeneity by Baseline Pollution Level")

st.markdown("""
The pooled EU-27 estimate could mask an effect concentrated in a subset of countries. Splitting
the treatment group at the median pre-treatment NO₂ level into 14 higher-baseline (more
industrialized, largely Western/Central European) and 13 lower-baseline countries, each
re-estimated separately against the full control group:
""")

hcol1, hcol2 = st.columns(2)
with hcol1:
    st.metric("Higher-Baseline Subgroup", "−5.46 × 10⁻⁶", "p = 0.003 — significant")
with hcol2:
    st.metric("Lower-Baseline Subgroup", "+1.53 × 10⁻⁶", "p = 0.189 — not significant")

st.error(
    "**This is the clearest single piece of evidence that the pooled null is averaging a real, "
    "concentrated effect together with little-to-no effect elsewhere, rather than reflecting a "
    "genuine absence of any EU-specific effect.** It does not overturn the pooled estimate as this "
    "study's headline, conservative result, and a subgroup split roughly halves the statistical "
    "power available to the pooled model — but it is corroborated by the event-study pattern above "
    "and is reported as a substantive finding in its own right."
)

st.markdown("---")

st.markdown("### Independent Corroboration: Synthetic Control &amp; Spatial Diagnostics")

st.markdown("""
Two further checks target the pooled estimate directly, using methods structurally
independent of the DiD specification itself.
""")

sc1, sc2 = st.columns(2)
with sc1:
    st.markdown("**Augmented Synthetic Control**")
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "synthetic_control_gap.png"), use_container_width=True)
    st.markdown(
        "<p class='caption-text'>Donor pool: 7 countries (UK, Switzerland, Albania, Bosnia and "
        "Herzegovina, Montenegro, North Macedonia, Serbia), weighted rather than averaged equally. "
        "Norway and Iceland excluded — both still show substantial NO₂ coverage gaps even after a "
        "clean re-fetch, a genuine high-latitude satellite limitation. "
        "Post-treatment gap = −1×10⁻⁶, same sign and order of magnitude as the pooled DiD coefficient "
        "(−2.22×10⁻⁶), reached through a method that doesn't use the DiD model's fixed effects at all. "
        "With 7 donors, the in-space placebo is a genuine permutation check: the real EU-27 gap ranks "
        "2nd of 8 by size.</p>",
        unsafe_allow_html=True,
    )
with sc2:
    st.markdown("**Moran's I Spatial Autocorrelation**")
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "moran_lisa_cluster_map.png"), use_container_width=True)
    st.markdown(
        "<p class='caption-text'>Raw NO₂ levels are strongly spatially clustered (I=0.570, p=0.001) — "
        "expected, pollution crosses borders. The DiD model's residuals are not significantly "
        "clustered (I=0.069, p=0.135): country and month fixed effects already absorb most of it, "
        "directly testing rather than assuming the country-clustered standard errors are adequate.</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

st.markdown("### How This Result Was Reached")

st.markdown("""
This finding was not the project's first result — it emerged only after a rigorous validation 
process that fundamentally changed the analytical approach:
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.error("**1️⃣ Initial Model**\n\nSingle-cohort design (all EU countries, no control group) found a seemingly significant effect (p=0.026 as originally computed with classical SEs; p=0.041 cluster-robust, still significant — see Methodology)")
with col2:
    st.error("**2️⃣ Placebo Test Failed**\n\nTesting a fake treatment date found an equally 'significant' effect — revealing the original result was actually a general pollution-decline trend")
with col3:
    st.success("**3️⃣ Control Group Added**\n\nA genuine non-EU comparison group was built, producing this project's honest, rigorously validated finding")

st.markdown("---")

st.markdown("### Full Regression Output")

coef_data = {
    "Variable": ["DiD Interaction (treatment_group × post)", "Post (main effect)",
                 "Average Temperature", "Average Precipitation", "GDP"],
    "Coefficient": ["−2.22 × 10⁻⁶", "—", "—", "—", "—"],
    "P-value (cluster-robust)": ["0.101", "—", "—", "—", "—"],
    "Interpretation": [
        "Core causal estimate (pooled) — not significant at 5%; significant in the higher-baseline subgroup",
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
comp_df["period"] = comp_df["year"].apply(lambda y: "Pre-2021 (2019–2020)" if y <= 2020 else "Post-2021 (2021–2024)")

grouped = comp_df.groupby(["treatment_group", "period"])["mean_no2"].mean().reset_index()
grouped["group_label"] = grouped["treatment_group"].map({1: "EU-27 (Treatment)", 0: "Control Group"})

fig_bar = go.Figure()
colors = {"Pre-2021 (2019–2020)": "#7c3aed", "Post-2021 (2021–2024)": "#00d4ff"}

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
    "<p class='caption-text'>Both groups show a similar decline pattern from the pre- to post-treatment period — "
    "visually consistent with the DiD model's non-significant interaction term.</p>",
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
policy-specific effect from a general trend, so the control-group correction below remains the
trustworthy result — its role here is better identification, not first-time significance:
""")

ncol1, ncol2, ncol3 = st.columns(3)
with ncol1:
    st.metric("NDVI DiD Coefficient", "−0.0145")
with ncol2:
    st.metric("P-value", "0.007", "Significant")
with ncol3:
    st.metric("95% CI", "excludes zero", "[-0.0250, -0.0039]")

st.error(
    "**A statistically significant relative decline in EU-27 vegetation health versus the "
    "control group, following the Climate Law's effective date.** This is not interpreted as "
    "evidence the Climate Law itself reduced vegetation health — the Climate Law is an "
    "emissions-focused instrument, not a land-use policy, and this analysis does not control for "
    "land-use change, drought/precipitation-driven vegetation stress, or agricultural-policy "
    "shifts between treatment and control regions. It is reported as an honest, statistically "
    "robust secondary finding meriting further investigation, not a causal claim."
)

st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "ndvi_eu_vs_control_bar_chart.png"), use_container_width=True)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine | Full methodology on the following pages</p>",
    unsafe_allow_html=True,
)