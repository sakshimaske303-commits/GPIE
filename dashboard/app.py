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
        <a href="https://doi.org/10.5281/zenodo.21756661" target="_blank" class="doi-badge-link" style="text-decoration:none;">
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
                        <span>ARCHIVED &amp; CITABLE ON ZENODO</span>
                        <span style="opacity:0.8; font-size:0.95rem;">↗</span>
                    </div>
                    <div style="color:{PALETTE['text']}; font-family:'Inter',sans-serif; font-weight:900; font-size:1.35rem; margin-top:2px;">
                        DOI: 10.5281/zenodo.21756661
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
    st.metric("DATASETS", "8", "Multi-source")
with col4:
    st.metric("METHOD", "DiD", "Causal Inference")

st.markdown("---")

st.markdown(
    f"""
    <div style="padding: 20px 26px; margin: 4px 0 20px 0; background: rgba(248, 131, 121, 0.06);
                border: 1px solid rgba(0, 135, 149, 0.3); border-left: 4px solid {PALETTE['coral']};
                border-radius: 10px;">
        <p style="color:{PALETTE['coral']}; text-transform:uppercase; letter-spacing:1.5px;
                  font-weight:700; font-size:0.85rem; margin-bottom:8px;">Why This Matters</p>
        <p style="color:{PALETTE['text']}; font-size:1rem; line-height:1.6; margin:0;">
            Governments announce landmark climate policy and then report their own progress against it —
            that self-reported progress is rarely independently audited against physical, satellite-observed
            evidence. GPIE builds that independent audit layer for the EU's Climate Law. Its most important
            result is a disciplined <strong>distinction</strong>: satellite data show NO₂ falling about 5%
            more in the EU-27 than in neighbouring non-EU countries, but the timing checks show a gradual
            EU-wide trend, not a step change at the Climate Law. "Pollution fell" and "this law made it fall"
            are different claims, and only the first is supported. Along the way the project corrected itself
            twice — a placebo test rejected its first model, and its satellite aggregation was rebuilt from
            end-of-month snapshots into true monthly means (see Methodology).
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
### System Overview

**GPIE** is a geospatial decision-intelligence framework that independently evaluates whether 
the **European Green Deal** and its flagship legislation, the **European Climate Law**, 
produced a measurable environmental effect — using satellite-derived evidence rather than 
relying solely on self-reported government claims.

Rather than assuming a policy worked, GPIE follows a **"Trust, But Verify"** protocol: 
integrating Earth Observation data (Sentinel-5P TROPOMI, CGLS NDVI), climate 
reanalysis (ERA5), economic indicators, and rigorous causal-inference methodology to 
test policy claims against independently observed evidence.

### Navigate the Analysis

Use the sidebar to explore:
- **Study Design** — the treatment vs. comparison-group architecture
- **Theoretical Foundations** — the retrieval physics behind the NO₂ column, and what makes it an independent outcome
- **Environmental Data** — NO₂ and vegetation health across Europe
- **Before After** — country-level NO₂ and NDVI, 2019 vs. 2024
- **Control Variables** — GDP and climate controls, plus land cover and elevation as context
- **Methodology** — the full validation journey and limitations, including the placebo test that reshaped the analysis
- **Causal Results** — the project's core statistical findings
- **India Transferability** — running the acquisition step on a non-EU country
- **Interactive Maps** — hoverable, zoomable versions of the main maps and charts
- **Explore Trends** — country-by-country NO₂ and NDVI time series
- **About Data** — the master dataset and data sources
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

_all_docs = [
    {"label": "Executive Summary", "filename": "GPIE_Executive_Summary.pdf"},
    {"label": "Research Paper", "filename": "GPIE_Research_Paper.pdf"},
    {"label": "Development Log", "filename": "GPIE_Development_Log.pdf"},
]
_existing = [d for d in _all_docs if os.path.exists(os.path.join(BASE_DIR, "static", d["filename"]))]
_missing = [d for d in _all_docs if d not in _existing]

if _existing:
    _cols = st.columns(len(_existing))
    for _col, _d in zip(_cols, _existing):
        with _col:
            with open(os.path.join(BASE_DIR, "static", _d["filename"]), "rb") as _f:
                st.download_button(
                    label=f"⬇ {_d['label']}",
                    data=_f.read(),
                    file_name=_d["filename"],
                    mime="application/pdf",
                    use_container_width=True,
                )
for d in _missing:
    st.warning(f"{d['filename']} not found.")

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