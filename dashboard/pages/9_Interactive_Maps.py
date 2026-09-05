import streamlit as st
import streamlit.components.v1 as components
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>🗺️ INTERACTIVE MAPS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>Hover, Zoom, and Explore the Data Directly</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

MAPS = {
    "Study Design: Treatment vs. Control": "control_group_map.html",
    "NO2 Concentration": "no2_map.html",
    "Vegetation Health (NDVI)": "ndvi_map.html",
    "Temperature": "climate_map.html",
    "GDP": "gdp_map.html",
    "Moran's I Spatial Clusters": "moran_lisa_map.html",
    "Event-Study Plot": "event_study.html",
    "Synthetic Control Gap": "synthetic_control.html",
    "Explore Trends by Country": "explore_trends.html",
}

choice = st.selectbox("Pick a map", list(MAPS.keys()))
map_path = os.path.join(PROJECT_ROOT, "outputs", "interactive", MAPS[choice])

if os.path.exists(map_path):
    with open(map_path, "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=650, scrolling=True)
else:
    st.warning(f"Map not found: outputs/interactive/{MAPS[choice]} — run build_interactive_maps.py first.")

st.markdown("---")
st.markdown(
    "<p class='caption-text'>Choropleth maps need an internet connection to load their base tiles. "
    "Same underlying data as the static maps elsewhere in this dashboard, just hoverable and zoomable.</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)
