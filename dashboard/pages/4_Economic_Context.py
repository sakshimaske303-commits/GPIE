import streamlit as st
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>💶 ECONOMIC & LAND CONTEXT</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>Control Variables Used in the Causal Model</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
### Why These Variables Matter

GPIE's causal-inference model doesn't just compare NO₂ before and after treatment — it also 
**controls for economic and environmental factors** that could otherwise confound the result. 
GDP accounts for economic activity levels (a major driver of emissions independent of policy), 
while land cover provides environmental baseline context.
""")

tab1, tab2 = st.tabs(["💶 GDP", "🌲 Land Cover"])

with tab1:
    st.markdown("""
    ### Gross Domestic Product (2019–2024 Average)

    GDP is used as a **control variable** in the Difference-in-Differences model, accounting for 
    each country's economic scale. Because GDP is highly right-skewed (a few large economies vastly 
    outsize most others), this map uses a **log₁₀ color scale** to make differences across all 
    30 countries visually interpretable.
    """)
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "gdp_choropleth_map.png"), use_container_width=True)
    st.markdown(
        "<p class='caption-text'>Source: Eurostat (EU-27), World Bank Open Data (control group)</p>",
        unsafe_allow_html=True,
    )

with tab2:
    st.markdown("""
    ### Dominant Land Cover Class (EU-27)

    Each country is shaded by its single largest ESA WorldCover land cover class, providing 
    environmental baseline context. Land cover is a **static, time-invariant variable** — in the 
    causal model, it is fully absorbed by country fixed effects rather than entered as an explicit 
    regressor.
    """)
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "land_cover_dominant_class_map.png"), use_container_width=True)
    st.markdown(
        "<p class='caption-text'>Source: ESA WorldCover 10m v200 (2021) — EU-27 only</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)