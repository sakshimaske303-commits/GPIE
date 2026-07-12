import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    st.metric("P-value", "0.632", "Not significant")
with col3:
    st.metric("95% CI", "spans zero", "[-7.12e-6, +4.32e-6]")

st.warning(
    "**Result: No statistically distinguishable EU-specific effect detected.** "
    "Once genuinely compared against a non-EU control group, the NO₂ decline observed in EU-27 "
    "countries is not statistically different from the decline observed in the United Kingdom, "
    "Norway, and Switzerland over the same period."
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
**Finding**: All 23 quarters — both before and after the 30 June 2021 treatment date — show 
confidence intervals spanning zero. No single quarter shows a statistically significant effect, 
reinforcing that this is a consistent null result rather than an artifact of time-averaging.
""")

st.markdown("---")

st.markdown("### How This Result Was Reached")

st.markdown("""
This finding was not the project's first result — it emerged only after a rigorous validation 
process that fundamentally changed the analytical approach:
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.error("**1️⃣ Initial Model**\n\nSingle-cohort design (all EU countries, no control group) found a seemingly significant effect (p=0.026)")
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
    "P-value": ["0.632", "—", "—", "—", "—"],
    "Interpretation": [
        "Core causal estimate — not significant",
        "Common trend, shared by both groups",
        "Control variable",
        "Control variable",
        "Control variable",
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
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine | Full methodology on the next page</p>",
    unsafe_allow_html=True,
)