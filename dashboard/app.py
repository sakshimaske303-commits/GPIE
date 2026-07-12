import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from styles import apply_custom_style, PALETTE

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
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>Independently Verifying Environmental Policy Claims Using Satellite Data</h3>",
    unsafe_allow_html=True,
)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("COUNTRIES", "30", "EU-27 + Control")
with col2:
    st.metric("STUDY PERIOD", "2019–2024", "6 years")
with col3:
    st.metric("DATASETS", "7", "Multi-source")
with col4:
    st.metric("METHOD", "DiD", "Causal Inference")

st.markdown("---")

st.markdown("""
### System Overview

**GPIE** is a geospatial decision-intelligence framework that independently evaluates whether 
the **European Green Deal** and its flagship legislation, the **European Climate Law**, 
produced a measurable environmental effect — using satellite-derived evidence rather than 
relying solely on self-reported government claims.

Rather than assuming a policy worked, GPIE follows a **"Trust, But Verify"** protocol: 
integrating Earth Observation data (Sentinel-5P TROPOMI, Sentinel-2/CGLS), climate 
reanalysis (ERA5), economic indicators, and rigorous causal-inference methodology to 
test policy claims against independently observed evidence.

### Navigate the Analysis

Use the sidebar to explore:
- **Study Design** — the treatment vs. control comparison architecture  
- **Environmental Data** — NO₂ and vegetation health across Europe  
- **Before vs. After** — pollution levels, 2019 vs. 2024  
- **Economic Context** — GDP and land cover as control variables  
- **Causal Results** — the project's core statistical findings  
- **Methodology & Limitations** — the full validation journey, including a placebo test that reshaped the entire analytical approach
""")

st.markdown("---")

st.markdown(
    f"""
    <div style="text-align: center; padding: 25px; background: rgba(0, 212, 255, 0.04); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 12px;">
        <p style="color: {PALETTE['text_muted']}; text-transform: uppercase; letter-spacing: 2px; font-size: 0.8rem;">Developed by</p>
        <h2 style="color: {PALETTE['cyan']}; margin: 5px 0;">SAKSHI D. MASKE</h2>
        <p style="color: {PALETTE['purple']}; font-weight: 600;">Independent Geospatial Researcher</p>
    </div>
    """,
    unsafe_allow_html=True,
)