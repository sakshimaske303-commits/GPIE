import streamlit as st
import pandas as pd
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>📂 ABOUT & DATA ACCESS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>Raw Data, Reproducibility & Contact</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("### 📊 Download the Master Dataset")
st.markdown("""
The complete, cleaned dataset used for this project's causal-inference model — 30 countries, 
2019–2024, monthly resolution — is available below for independent verification or reuse.
""")

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "master_dataset_control.csv")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()

st.dataframe(df.head(50), use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Full Dataset (CSV)",
    data=csv,
    file_name="gpie_master_dataset.csv",
    mime="text/csv",
)

st.markdown(f"<p class='caption-text'>Showing first 50 of {len(df):,} total rows.</p>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 📚 Data Sources & Citations")
st.markdown("""
| Dataset | Provider | Access Method |
|---|---|---|
| NO₂ (Sentinel-5P) | European Space Agency / Copernicus | Sentinel Hub Statistical API |
| NDVI (CGLS) | Copernicus Land Monitoring Service | Sentinel Hub Statistical API |
| Climate (ERA5) | ECMWF / Copernicus Climate Data Store | CDS API |
| Land Cover | ESA WorldCover | AWS Open Data |
| Elevation (DEM) | Copernicus DEM GLO-30 | AWS Open Data |
| GDP (EU-27) | Eurostat | REST Statistics API |
| GDP (Control Group) | World Bank | Open Data API |
| Administrative Boundaries | Eurostat GISCO (NUTS), GADM | Direct Download |
| Policy Records | EUR-Lex | Web Scraping |
""")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)