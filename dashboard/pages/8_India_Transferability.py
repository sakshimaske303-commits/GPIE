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
### Transferability Validation

GPIE's original design goal was a **globally transferable methodology**, not one limited to the
EU-27 study region. As a first step, the NO₂ acquisition step was run on **India's national
boundary** (GADM 4.1, 2019–2024) using the same request builder, evalscript and QA threshold as
the EU-27 study (`s5p_process_daily.py`: one Process API raster per day, pooled into monthly means). An earlier version used a rectangular bounding box that
also covered neighbouring countries and ocean; that output is superseded.
""")

st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "india_transferability_trend.png"), use_container_width=True)

st.markdown(
    "<p class='caption-text'>The test script records how many months returned data and how the values "
    "compare with the EU-27 distribution (data/global_transferability_test/india_no2_sanity_check.json). "
    "Result: all 72 months returned data; India's monthly national mean ranged from 2.27 × 10⁻⁵ to 4.16 × 10⁻⁵ mol/m² (median 3.32 × 10⁻⁵), with no negative months, and all 72 values fall inside the 5th–95th percentile range of EU-27 country-months (1.34 × 10⁻⁵ to 6.34 × 10⁻⁵ mol/m²). "
    "This shows the data pipeline runs outside Europe; it is not a causal or comparative analysis.</p>",
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)
