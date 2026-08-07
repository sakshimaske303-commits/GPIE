import streamlit as st
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>🌍 TRANSFERABILITY VALIDATION</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>Testing the Framework Beyond the EU-27</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
### 🌍 Transferability Validation

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
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)
