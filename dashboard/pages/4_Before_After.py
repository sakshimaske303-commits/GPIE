import streamlit as st
import streamlit.components.v1 as components
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE


def render_map(png_name, html_name, height=560):
    # I always show the PNG from my map_*.py scripts. The old HTML maps use outdated data.
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", png_name), width="stretch")

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>📊 BEFORE vs. AFTER</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>NO₂ and NDVI Levels: 2019 vs. 2024</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
### Visual Comparison Across the Study Period

These side-by-side comparisons show conditions across all 36 countries (EU-27 + 9-country comparison group)
in **2019** — the pre-treatment baseline year — versus **2024**, the most recent complete year
of data. Each pair of panels uses an **identical color scale**, so any visible color shift
represents a genuine change, not a scaling artifact.
""")

tab1, tab2 = st.tabs(["NO₂ (Nitrogen Dioxide)", "NDVI (Vegetation Health)"])

with tab1:
    render_map("no2_before_after_map.png", "no2_before_after_map.html")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        #### What the Map Shows

        Lower NO₂ is visible in 2024 than in 2019 across much of the EU-27, most clearly in the
        Benelux countries and Germany, while the Western Balkan comparison countries change little
        (country-level annual means; descriptive only).
        """)
    with col2:
        st.markdown("""
        #### Why This Matters

        A before/after map cannot show what the Climate Law did. The *Causal Results* page shows that
        the EU-27's decline is larger than the comparison group's at country level, that it is not timed to
        the law, and that most of it disappears when areas with the same starting pollution are compared.
        """)

with tab2:
    render_map("ndvi_before_after_map.png", "ndvi_before_after_map.html")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        #### What the Map Shows

        Vegetation health across Europe shows relatively stable patterns between 2019 and 2024, 
        with no dramatic shift comparable to the NO₂ decline visible in the other tab.
        """)
    with col2:
        st.markdown("""
        #### Why This Matters

        NDVI is context here and is not part of the research paper. An earlier supplementary model
        (baseline specification, same comparison group as NO₂) found a small relative decline in EU-27
        NDVI (−0.0194, p = 0.008). It is an exploratory association only: land-use change, drought and
        agricultural policy are not controlled for (see the *Methodology* page).
        """)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)