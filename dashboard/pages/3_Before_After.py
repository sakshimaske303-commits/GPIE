import streamlit as st
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>📊 BEFORE vs. AFTER</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>NO₂ Levels: 2019 vs. 2024</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
### Visual Comparison Across the Study Period

This side-by-side comparison shows tropospheric NO₂ concentration across all 30 countries 
(EU-27 + control group) in **2019** — the pre-treatment baseline year — versus **2024**, 
the most recent complete year of data. Both panels use an **identical color scale**, so any 
visible color shift represents a genuine change in pollution levels, not a scaling artifact.
""")

st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "no2_before_after_map.png"), use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    #### 🔵 What the Map Shows

    A general decline in NO₂ is visible across most of Europe between 2019 and 2024 — 
    including both EU-27 countries **and** the non-EU control group (UK, Norway, Switzerland).
    """)
with col2:
    st.markdown("""
    #### 🎯 Why This Matters

    The fact that **both groups show a similar decline pattern** is an important visual preview 
    of GPIE's core statistical finding — explored in full on the *Causal Results* page.
    """)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)