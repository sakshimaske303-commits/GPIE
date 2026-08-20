import streamlit as st
import streamlit.components.v1 as components
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>🎯 STUDY DESIGN</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>Treatment vs. Control Group Architecture</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
### The Core Challenge

The European Green Deal and its Climate Law apply to **all 27 EU member states simultaneously** — 
meaning there is no EU country left "untreated" to compare against. Without a genuine comparison 
group, it is statistically impossible to distinguish a real policy effect from a general pollution 
trend that would have happened anyway.

### The Solution: An External Control Group

GPIE addresses this by introducing nine **non-EU European countries** as a control group —
geographically and economically comparable nations that are **not** subject to EU Green Deal
legislation, spanning both established Western European economies and EU-accession-candidate
economies in the Western Balkans:
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**United Kingdom**\n\nExited the EU in 2020 — outside EU regulatory scope from 2021 onward")
with col2:
    st.info("**Norway**\n\nNever an EU member — economically developed, geographically proximate")
with col3:
    st.info("**Switzerland**\n\nNever an EU member — comparable industrial base and climate")

col4, col5, col6 = st.columns(3)
with col4:
    st.info("**Iceland**\n\nNever an EU member — EEA-linked, high-latitude comparator")
with col5:
    st.info("**Albania**\n\nEU accession candidate — not yet subject to Green Deal legislation")
with col6:
    st.info("**Bosnia and Herzegovina**\n\nEU accession candidate — Western Balkans comparator")

col7, col8, col9 = st.columns(3)
with col7:
    st.info("**Montenegro**\n\nEU accession candidate — Western Balkans comparator")
with col8:
    st.info("**North Macedonia**\n\nEU accession candidate — Western Balkans comparator")
with col9:
    st.info("**Serbia**\n\nEU accession candidate — largest Western Balkans economy in the control group")

st.markdown("---")

st.markdown("### Geographic Distribution")
interactive_map_path = os.path.join(PROJECT_ROOT, "outputs", "plots", "control_group_design_map.html")
if os.path.exists(interactive_map_path):
    with open(interactive_map_path, "r", encoding="utf-8") as f:
        components.html(f.read(), height=560)
    st.markdown(
        "<p class='caption-text' style='text-align:center;'>Hover a country for its name and group. Toggle layers top-right.</p>",
        unsafe_allow_html=True,
    )
else:
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "control_group_design_map.png"), use_container_width=True)

st.markdown("---")

st.markdown("""
### The Difference-in-Differences (DiD) Logic

By comparing the *change* in each group rather than raw values, any general European-wide trend
(technology improvements, broader decarbonization) common to both groups cancels out — isolating
only the portion of change specifically attributable to being subject to EU climate legislation.

**Treatment date**: 30 June 2021 — the date the **European Climate Law** (Regulation (EU) 2021/1119) 
entered into force, establishing a legally binding EU-wide climate-neutrality target.
""")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)