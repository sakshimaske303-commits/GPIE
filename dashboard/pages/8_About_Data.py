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

st.markdown("### 📄 Project Documentation")
st.markdown("""
Three documents accompany this project, each serving a different purpose:
""")

doc_col1, doc_col2, doc_col3 = st.columns(3)
with doc_col1:
    st.markdown("""
    **📘 Project Journal**

    Polished summary — methodology, findings, conclusions.

    [View →](https://github.com/sakshimaske303-commits/GPIE/blob/main/Project_Journal.md)
    """)
with doc_col2:
    st.markdown("""
    **📗 Research Paper**

    Formal academic write-up — literature review, statistics, discussion.

    [View →](https://github.com/sakshimaske303-commits/GPIE/blob/main/Research_Paper.md)
    """)
with doc_col3:
    st.markdown("""
    **📙 Development Log**

    Full technical log — every bug, debug session, iteration.

    [View →](https://github.com/sakshimaske303-commits/GPIE/blob/main/Devlopment_Log.md)
    """)

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

st.markdown("### 🔗 Full Reproducibility")
st.markdown("""
The complete codebase — data acquisition scripts, processing pipelines, causal-inference models, 
and this dashboard itself — is published as open-source on GitHub, including full documentation 
of the project's development process, debugging history, and methodological decisions.
""")

st.markdown("""
<div style="background: rgba(0, 212, 255, 0.06); border: 1px solid rgba(0, 212, 255, 0.25); border-radius: 10px; padding: 16px; margin: 10px 0;">
    <strong>GitHub Repository:</strong> <a href="https://github.com/sakshimaske303-commits/GPIE" style="color: #00d4ff;">github.com/sakshimaske303-commits/GPIE</a>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 🌍 Transferability Validation")
st.markdown("""
GPIE's original design goal was a **globally transferable methodology**, not one limited to the 
EU-27 study region. To provide direct evidence of this rather than leaving it as an unverified 
claim, the project's NO₂ acquisition pipeline was tested standalone on **India** (2019–2024) — 
using the same Sentinel Hub Statistical API infrastructure built for the EU-27 study, with zero 
modification to the core acquisition code.
""")

st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "india_transferability_trend.png"), use_container_width=True)

st.markdown(
    "<p class='caption-text'>All 6 years acquired successfully, returning physically realistic NO₂ "
    "values consistent with the EU-27 dataset's observed range. This is a standalone proof-of-concept "
    "confirming the framework's portability — not a comparative analysis.</p>",
    unsafe_allow_html=True,
)

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
    f"""
    <div style="text-align: center; padding: 25px; background: rgba(124, 58, 237, 0.06); border: 1px solid rgba(124, 58, 237, 0.25); border-radius: 12px;">
        <p style="color: {PALETTE['text_muted']}; text-transform: uppercase; letter-spacing: 2px; font-size: 0.8rem;">Project Author</p>
        <h2 style="color: {PALETTE['cyan']}; margin: 5px 0;">SAKSHI D. MASKE</h2>
        <p style="color: {PALETTE['purple']}; font-weight: 600;">Independent Geospatial Researcher</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)