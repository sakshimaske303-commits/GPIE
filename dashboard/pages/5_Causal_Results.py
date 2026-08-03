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

st.markdown("### The Final Model: Two-Group Difference-in-Differences")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("DiD Coefficient", "−1.40 × 10⁻⁶")
with col2:
    st.metric("P-value", "0.663", "Not significant")
with col3:
    st.metric("95% CI", "spans zero", "[-7.68e-6, +4.88e-6]")

st.markdown(
    "<p class='caption-text'>Standard errors are clustered by country to account for "
    "within-country serial correlation in this panel (Bertrand, Duflo & Mullainathan, 2004).</p>",
    unsafe_allow_html=True,
)

st.warning(
    "**Result: No statistically distinguishable EU-specific effect detected.** "
    "Once genuinely compared against a non-EU control group, the NO₂ decline observed in EU-27 "
    "countries is not statistically different from the decline observed in the United Kingdom, "
    "Norway, and Switzerland over the same period. At 80% statistical power, this design can "
    "reliably detect an effect of roughly 28% of baseline EU NO₂ or larger — this result rules "
    "out an effect of that size, but cannot rule out a smaller true effect."
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
**Finding**: Under cluster-robust standard errors, 20 of the 23 quarters — both before and after
the 30 June 2021 treatment date — show no statistically significant effect. Three quarters are
nominally significant (2020Q1 pre-treatment, plausibly reflecting COVID-19 lockdown timing
differences rather than a real pre-trend; and 2023Q1/2023Q3 post-treatment with opposite-signed
coefficients, not forming a consistent pattern) — close to the ~1 false positive expected by
chance across 23 independent tests. Overall, this supports the model's parallel-trends assumption
and does not indicate a delayed effect emerging at any point through 2024.
""")

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
    st.success("**3️⃣ Control Group Added**\n\nA genuine non-EU comparison group was built, producing this session's honest, rigorously validated finding")

st.markdown("---")

st.markdown("### 📊 Full Regression Output")

coef_data = {
    "Variable": ["DiD Interaction (treatment_group × post)", "Post (main effect)",
                 "Average Temperature", "Average Precipitation", "GDP"],
    "Coefficient": ["−1.40 × 10⁻⁶", "—", "—", "—", "—"],
    "P-value (cluster-robust)": ["0.663", "—", "—", "—", "—"],
    "Interpretation": [
        "Core causal estimate — not significant",
        "Common trend, shared by both groups",
        "Control variable",
        "Control variable",
        "Control variable (removing GDP entirely makes the estimate even more null — see Methodology page)",
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

st.markdown("### 📉 EU-27 vs. Control Group — Average NO₂ Comparison")


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

st.markdown("### 🌿 Secondary Outcome: NDVI (Vegetation Health)")

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
    st.metric("NDVI DiD Coefficient", "−0.0210")
with ncol2:
    st.metric("P-value", "0.012", "Significant")
with ncol3:
    st.metric("95% CI", "excludes zero", "[-0.0372, -0.0047]")

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
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine | Full methodology on the next page</p>",
    unsafe_allow_html=True,
)