import streamlit as st
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>💶 CONTROL VARIABLES & CONTEXT</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>Economic, Environmental & Climate Controls Used in the Causal Model</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
### Why These Variables Matter

GPIE's causal-inference model doesn't just compare NO₂ before and after treatment — it also 
**controls for economic, climatic, and environmental factors** that could otherwise confound the 
result. GDP accounts for economic activity levels, temperature and precipitation account for 
weather-driven pollution variation, and land cover / elevation provide environmental baseline context.
""")

tab1, tab2, tab3, tab4 = st.tabs(["GDP", "Land Cover", "Elevation", "Climate"])

with tab1:
    st.markdown("""
    ### Gross Domestic Product (2019–2024 Average)

    GDP is used as a **control variable** in the Difference-in-Differences model, accounting for
    each country's economic scale. Because GDP is highly right-skewed (a few large economies vastly
    outsize most others), this map uses a **log₁₀ color scale** to make differences across all
    36 countries visually interpretable.
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

with tab3:
    st.markdown("""
    ### Mean Elevation (EU-27)

    Elevation provides topographic context — terrain can influence local pollution dispersion and 
    settlement patterns. Like land cover, elevation is a **static, time-invariant variable**, fully 
    absorbed by country fixed effects in the causal model rather than entered as an explicit regressor.
    """)
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "dem_elevation_map.png"), use_container_width=True)
    st.markdown(
        "<p class='caption-text'>Source: Copernicus DEM GLO-30 — EU-27 only</p>",
        unsafe_allow_html=True,
    )

with tab4:
    st.markdown("""
    ### Mean Temperature (2019–2024 Average)

    Temperature and precipitation are used as **time-varying control variables** in the causal model, 
    accounting for weather-driven variation in NO₂ concentration independent of policy effects — for 
    example, colder months tend to show higher pollution readings due to heating-related emissions.
    """)
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "climate_temperature_map.png"), use_container_width=True)
    st.markdown(
        "<p class='caption-text'>Source: ERA5 Reanalysis, Copernicus Climate Data Store</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)