import streamlit as st
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>📖 METHODOLOGY & LIMITATIONS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>The Full Scientific Validation Journey</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
### Data Sources

GPIE integrates seven independently-sourced datasets, all acquired at the country level for 
2019–2024 (30 countries: EU-27 + UK, Norway, Switzerland):
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    - **NO₂** — Sentinel-5P TROPOMI (Sentinel Hub Statistical API)
    - **NDVI** — CGLS 300m (Sentinel Hub Statistical API)
    - **Climate** — ERA5 Reanalysis (temperature, precipitation)
    - **GDP** — Eurostat (EU-27) + World Bank (control group)
    """)
with col2:
    st.markdown("""
    - **Land Cover** — ESA WorldCover 10m v200
    - **Elevation** — Copernicus DEM GLO-30
    - **Policy Records** — EUR-Lex (EU Green Deal legislation)
    """)

st.markdown("---")

st.markdown("### The Validation Sequence")

with st.expander("**Step 1 — Initial Single-Cohort Model**", expanded=False):
    st.markdown("""
    The first causal model compared all 27 EU countries before vs. after the European Climate Law 
    (30 June 2021), using country and seasonal fixed effects. This found a statistically significant 
    reduction in NO₂ (p = 0.026).

    **The problem**: because all 27 countries were treated simultaneously, there was no untreated 
    comparison group — making it mathematically impossible to distinguish a genuine policy effect 
    from a general, ongoing pollution-decline trend.
    """)

with st.expander("**Step 2 — Placebo Test**", expanded=False):
    st.markdown("""
    To test the result's credibility, the identical model was re-run with the treatment date 
    artificially shifted to 30 June 2020 — a date with no relevant policy event.

    **The result**: the placebo model found an equally significant "effect" (p = 0.002) — even 
    more significant than the real result. This proved the original model was capturing a general 
    trend, not a policy-specific effect. Adding an explicit linear time trend confirmed this: once 
    the trend was controlled for, the original "significant" effect disappeared entirely (p = 0.408).
    """)

with st.expander("**Step 3 — Building a Genuine Control Group**", expanded=False):
    st.markdown("""
    Three non-EU European countries were added as a control group — the **UK, Norway, and 
    Switzerland** — selected for being geographically and economically comparable to the EU-27 
    while not being subject to EU Green Deal legislation. This required:
    - New boundary data (GADM Level 0)
    - Extended satellite data acquisition for all 30 countries
    - A second GDP data source (World Bank API) for non-EU countries

    This enabled a genuine two-group Difference-in-Differences model — the version presented on 
    the *Causal Results* page.
    """)

with st.expander("**Step 4 — Event-Study Robustness Check**", expanded=False):
    st.markdown("""
    The overall DiD result was further validated by estimating the treatment effect separately for 
    all 23 individual quarters (2019Q1–2024Q4), rather than as a single average — confirming the 
    null result held consistently across every quarter, both before and after treatment.
    """)

st.markdown("---")

st.markdown("### ⚠️ Honest Limitations")

st.warning("""
**Statistical power**: The control group consists of only 3 countries. The overall model's 
confidence interval — [-7.12 × 10⁻⁶, +4.32 × 10⁻⁶] — is reasonably wide, not tightly clustered 
around zero. This means the honest conclusion is not simply *"the policy had no effect,"* but 
rather: *with this study's sample size and three-country control group, no statistically 
distinguishable EU-specific effect could be detected* — a result consistent with either a 
genuinely negligible effect, or a control group too small to provide adequate statistical power 
to detect a real but modest effect.
""")

st.info("""
**Module 9 (Economic Efficiency Ranking) was deliberately scoped out.** Ranking policies by 
"cost-per-unit-environmental-improvement" presupposes a measurable improvement to rank against — 
since Module 8 found no statistically significant effect, constructing such a ranking would 
require manufacturing significance the data does not support. This decision is itself treated as 
a finding consistent with GPIE's "Trust, But Verify" design principle.
""")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine | Developed by Sakshi D. Maske</p>",
    unsafe_allow_html=True,
)