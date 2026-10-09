import streamlit as st
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

st.set_page_config(page_title="Atmospheric Physics — GPIE", page_icon="🔬", layout="wide")
apply_custom_style()

st.markdown("<h1 style='text-align: center;'>🔬 THE PHYSICS BEHIND THE PIXEL</h1>", unsafe_allow_html=True)
st.markdown(
    f"<h3 style='text-align: center; color: {PALETTE['coral']}; font-weight: 400;'>"
    "How TROPOMI Actually Measures NO₂ From 800 km Above the Ground</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Diagram
IMG_PATH = os.path.join(PROJECT_ROOT, "outputs", "plots", "tropomi_example_day.png")
col_a, col_b, col_c = st.columns([0.2, 5.9, 0.2])
with col_b:
    if os.path.exists(IMG_PATH):
        st.image(IMG_PATH, width="stretch")
    else:
        st.warning("Figure not found at outputs/plots/tropomi_example_day.png")
    st.markdown(
        f"<p style='text-align:center; color:{PALETTE['text_muted']}; font-size:0.85rem; margin-top:6px;'>"
        "One day of the project's own data: the Sentinel-5P TROPOMI tropospheric NO₂ raster for 8 September 2023 "
        "(plot_tropomi_example_day.py). Every monthly mean in GPIE pools one month of daily rasters like this one.</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# Section 1: why NO2, why from space
st.markdown("### Why NO₂ Can Be “Seen” From Orbit at All")

st.markdown("""
GPIE's core evidence is a satellite-retrieved gas concentration, not a ground sensor reading — so
the causal claims in this project rest on trusting a genuine piece of atmospheric physics: **NO₂
absorbs sunlight at very specific wavelengths, and that absorption can be measured remotely.**

Sunlight travels down through the atmosphere, and any NO₂ molecules in its path absorb a portion
of it in the visible range (TROPOMI's NO₂ fit window is about 405–465 nm) — a structured pattern
of many narrow **absorption bands** distinctive enough to separate NO₂ from other trace gases. The remaining, partially-absorbed light
scatters off the Earth's surface and atmosphere back up toward space, where TROPOMI's
spectrometer on the Sentinel-5P satellite records it. The physical law governing how much light
is absorbed is the **Beer–Lambert law**:
""")

st.latex(r"I = I_0 \, e^{-\sigma N L}")

st.markdown("""
where **I₀** is the incoming solar intensity, **σ** is NO₂'s known absorption cross-section at a
given wavelength, **N** is the NO₂ number density, and **L** is the atmospheric path length the
light travelled through. Because σ is known from laboratory measurements (it varies with
wavelength and temperature), and
I₀ and I are what TROPOMI's spectrometer actually records, this equation can be inverted to solve
for **N·L** — the quantity actually retrieved, called a **slant column density**.
""")

st.markdown("---")

# Section 2: from slant column to a policy-relevant number
st.markdown("### From a Slant Column to a Number GPIE Can Use")

st.markdown("""
The retrieval described above measures NO₂ integrated along the **slant path** the sunlight
actually travelled — which depends on the sun's angle and the satellite's viewing angle, both of
which change from pixel to pixel and orbit to orbit. To make measurements comparable across
space and time, the slant column density is divided by an **air mass factor (AMF)** — a
radiative-transfer correction that accounts for viewing geometry, surface reflectivity, cloud
cover, and the vertical distribution of NO₂ itself — producing a geometry-independent
**vertical column density (VCD)**, reported in mol/m². The tropospheric column used in GPIE is what
remains after the stratospheric part of the column is estimated and removed. This is the number shown in
the figure above and the number GPIE's models use.

Two things about this process matter directly for GPIE's credibility as evidence: first, this is
a **calibrated physical measurement**, independent of any national reporting system or
government-submitted inventory — which is why it is useful as an independent outcome for testing
whether the European Climate Law changed real-world pollution levels, rather than merely changed
what governments chose to report. Independent is not the same as unbiased: the retrieval depends on
cloud screening, surface reflectivity, viewing geometry and assumed vertical NO₂ profiles, and these
errors vary by season and region. Second, TROPOMI's native pixel size (3.5 × 7 km until August 2019,
3.5 × 5.5 km since) is fine enough to resolve individual urban and industrial pollution hotspots —
visible in the figure above over the Low Countries, the Ruhr, London and the Po Valley — which is what
makes both the country-level and the 0.1° pixel-level analyses possible.
""")

st.markdown("---")

st.markdown(
    f"<p class='caption-text' style='text-align:center;'>GPIE — The Physics Behind the Policy Verdict</p>",
    unsafe_allow_html=True,
)
