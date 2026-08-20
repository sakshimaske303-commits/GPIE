import streamlit as st
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>🛰️ ENVIRONMENTAL DATA</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>NO₂ Pollution & Vegetation Health Across Europe</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

tab1, tab2 = st.tabs(["NO₂ (Nitrogen Dioxide)", "NDVI (Vegetation Health)"])

with tab1:
    st.markdown("""
    ### Tropospheric NO₂ Concentration

    Nitrogen dioxide (NO₂) is a key indicator of combustion-related air pollution — primarily from 
    vehicle traffic and industrial activity. This map shows the **2019–2024 average** tropospheric 
    NO₂ column density, derived from **Sentinel-5P TROPOMI** satellite observations.
    """)
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "no2_choropleth_map.png"), use_container_width=True)
    st.markdown(
        "<p class='caption-text'>Source: Sentinel-5P TROPOMI, accessed via Sentinel Hub Statistical API</p>",
        unsafe_allow_html=True,
    )

with tab2:
    st.markdown("""
    ### NDVI — Normalized Difference Vegetation Index

    NDVI measures vegetation health and density from satellite imagery, ranging from -1 (no 
    vegetation / water) to +1 (dense, healthy vegetation). This map shows the **2019–2024 average** 
    NDVI, derived from **Copernicus Global Land Service (CGLS)** data.
    """)
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "ndvi_choropleth_map.png"), use_container_width=True)
    st.markdown(
        "<p class='caption-text'>Source: CGLS NDVI 300m, accessed via Sentinel Hub Statistical API</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)