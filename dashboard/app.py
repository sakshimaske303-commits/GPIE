import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from styles import apply_custom_style, PALETTE

# I build paths from this file so they work both locally and on Streamlit Cloud.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # .../dashboard
ROOT_DIR = os.path.dirname(BASE_DIR)                      # repo root

st.set_page_config(
    page_title="GPIE — Green Policy Intelligence Engine",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_style()

st.markdown(
    "<h1 style='text-align: center;'>🛰️ GREEN POLICY INTELLIGENCE ENGINE</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<h3 style='text-align: center; color: {PALETTE['coral']}; font-weight: 400;'>Independently Verifying Environmental Policy Claims Using Satellite Data</h3>",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <style>
        .doi-badge-link {{ text-decoration:none; }}
        .doi-badge-card {{ transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease; cursor: pointer; }}
        .doi-badge-link:hover .doi-badge-card {{ transform: translateY(-3px) scale(1.02); box-shadow: 0 10px 32px rgba(248, 131, 121, 0.6); filter: brightness(1.08); }}
    </style>
    <div style="display:flex; justify-content:center; flex-wrap:wrap; gap:16px; margin: 10px 0 18px 0;">
        <a href="https://eartharxiv.org/repository/view/14824/" target="_blank" class="doi-badge-link" style="text-decoration:none;">
            <div class="doi-badge-card" style="
                display:flex; align-items:center; gap:18px;
                background: linear-gradient(145deg, #052226, {PALETTE['slate']});
                border: 2px solid {PALETTE['coral']};
                border-radius: 14px;
                padding: 16px 32px;
                box-shadow: 0 4px 20px rgba(248, 131, 121, 0.35);
            ">
                <div style="text-align:left;">
                    <div style="color:{PALETTE['chantilly']}; font-family:'Inter',sans-serif; font-weight:800; font-size:1.05rem; letter-spacing:0.4px; display:flex; align-items:center; gap:8px;">
                        <span>PREPRINT ON EARTHARXIV</span>
                        <span style="opacity:0.8; font-size:0.95rem;">↗</span>
                    </div>
                    <div style="color:{PALETTE['text']}; font-family:'Inter',sans-serif; font-weight:900; font-size:1.35rem; margin-top:2px;">
                        Read the preprint
                    </div>
                </div>
            </div>
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("COUNTRIES", "36", "EU-27 + 9-Country Control")
with col2:
    st.metric("STUDY PERIOD", "2019–2024", "6 years")
with col3:
    st.metric("DAILY RASTERS", "2,192", "Sentinel-5P TROPOMI NO₂, 0.1°")
with col4:
    st.metric("METHOD", "DiD", "Country and pixel level")

st.markdown("---")

st.markdown(
    f"""
    <div style="padding: 20px 26px; margin: 4px 0 20px 0; background: rgba(248, 131, 121, 0.06);
                border: 1px solid rgba(0, 135, 149, 0.3); border-left: 4px solid {PALETTE['coral']};
                border-radius: 10px;">
        <p style="color:{PALETTE['coral']}; text-transform:uppercase; letter-spacing:1.5px;
                  font-weight:700; font-size:0.85rem; margin-bottom:8px;">Why This Matters</p>
        <p style="color:{PALETTE['text']}; font-size:1rem; line-height:1.6; margin:0;">
            Satellite NO₂ makes it easy to compare pollution in countries that adopted a policy with countries
            that did not. GPIE asks what such a comparison identifies when the two groups start at different
            pollution levels, using the European Climate Law as a negative-control case. A country-level
            difference-in-differences finds NO₂ fell about 4% more in the EU-27 than in nine neighbouring
            non-EU countries, but the estimate is fragile and appears only two years after the law. Most of it
            reflects that the EU-27 was more polluted to begin with: comparing EU and comparison-group pixels
            that started at the same level leaves an estimate close to zero. The data do not require an effect
            at the EU border, but they cannot rule one out. NO₂ fell most in the polluted north-west, inside and
            outside the EU, for reasons the data cannot identify.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
### System Overview

**GPIE** is a geospatial workflow that turns 2,192 daily Sentinel-5P TROPOMI NO₂ rasters into monthly
country and pixel panels and tests a policy-evaluation design on them. It compares a country-level
difference-in-differences with a pixel-level comparison of areas that started at the same pollution level,
and describes where NO₂ fell across Europe. The research paper is the reference for every result.

**Research question:** when treated and comparison countries differ in baseline pollution, what does a
country-level DiD on satellite NO₂ identify?

### Navigate the Analysis

Use the sidebar to explore:
- **Study Design** — the treatment vs. comparison-group architecture
- **Theoretical Foundations** — the retrieval physics behind the NO₂ column, and what makes it an independent outcome
- **Environmental Data** — NO₂ (and, as context, vegetation health) across Europe
- **Before After** — country-level NO₂ and NDVI, 2019 vs. 2024
- **Control Variables** — GDP and climate controls used in the model, plus land cover and elevation as context
- **Methodology** — how the analysis developed, its corrections and its limitations
- **Causal Results** — the paper's results: country-level estimate, timing, composition and geography
- **India Transferability** — running the acquisition step on a non-EU country (supplementary)
- **Interactive Maps** — hoverable, zoomable versions of the main maps and charts
- **Explore Trends** — country-by-country NO₂ and NDVI time series
- **About Data** — the master dataset and data sources
- **Pixel Level Check** — whether NO₂ fell where the EU is, or where pollution was high
""")

st.markdown("---")

# Full project documentation
st.markdown(
    f"""
    <p style="text-align:center; color:{PALETTE['coral']}; text-transform:uppercase;
              letter-spacing:1.5px; font-weight:700; font-size:0.95rem; margin-bottom:14px;">
        Full Project Documentation
    </p>
    """,
    unsafe_allow_html=True,
)

# I offer the PDFs in static/ if they are there, otherwise the Markdown files from the repo root.
_all_docs = [
    {"label": "Executive Summary", "stem": "GPIE_Executive_Summary"},
    {"label": "Research Paper", "stem": "GPIE_Research_Paper"},
    {"label": "Development Log", "stem": "GPIE_Development_Log"},
]
_available = []
for _d in _all_docs:
    _pdf = os.path.join(BASE_DIR, "static", _d["stem"] + ".pdf")
    _md = os.path.join(ROOT_DIR, _d["stem"] + ".md")
    if os.path.exists(_pdf):
        _available.append((_d["label"], _pdf, "application/pdf"))
    elif os.path.exists(_md):
        _available.append((_d["label"], _md, "text/markdown"))

if _available:
    _cols = st.columns(len(_available))
    for _col, (_label, _path, _mime) in zip(_cols, _available):
        with _col:
            with open(_path, "rb") as _f:
                st.download_button(
                    label=f"⬇ {_label}",
                    data=_f.read(),
                    file_name=os.path.basename(_path),
                    mime=_mime,
                    width="stretch",
                )

st.markdown(
    f"""
    <div style="text-align: center; padding: 16px; margin: 18px 0; background: rgba(0, 135, 149, 0.06); border: 1px solid rgba(248, 131, 121, 0.25); border-radius: 10px;">
        <strong style="color: {PALETTE['text']};">GitHub Repository:</strong>
        <a href="https://github.com/sakshimaske303-commits/GPIE" target="_blank" style="color: {PALETTE['coral']};">github.com/sakshimaske303-commits/GPIE</a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

st.markdown(
    f"""
    <div style="text-align: center; padding: 25px; background: rgba(0, 135, 149, 0.06); border: 1px solid rgba(248, 131, 121, 0.25); border-radius: 12px;">
        <p style="color: {PALETTE['text_muted']}; text-transform: uppercase; letter-spacing: 2px; font-size: 0.8rem;">Developed by</p>
        <h2 style="color: {PALETTE['lagoon']}; margin: 5px 0;">SAKSHI D. MASKE</h2>
        <p style="color: {PALETTE['coral']}; font-weight: 600;">Independent Geospatial Researcher</p>
    </div>
    """,
    unsafe_allow_html=True,
)