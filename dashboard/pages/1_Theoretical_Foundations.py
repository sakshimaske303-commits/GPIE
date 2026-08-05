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

# ============================================================
# DIAGRAM
# ============================================================
IMG_PATH = os.path.join(PROJECT_ROOT, "outputs", "plots", "img1.png")
col_a, col_b, col_c = st.columns([1, 4, 1])
with col_b:
    if os.path.exists(IMG_PATH):
        st.image(IMG_PATH, use_container_width=True)
    else:
        st.warning("Diagram not found at outputs/plots/img1.png")
    st.markdown(
        f"<p style='text-align:center; color:{PALETTE['text_muted']}; font-size:0.85rem; margin-top:6px;'>"
        "🤖 AI-generated diagram — visual only</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="background: rgba(0, 135, 149, 0.06); border: 1px solid rgba(248, 131, 121, 0.25);
                    border-radius: 10px; padding: 14px 20px; margin-top: 6px;">
            <p style="color:{PALETTE['text_muted']}; font-size:0.85rem; font-style:italic; margin:0; text-align:center;">
                Generated with an AI image tool from a fully-specified brief — every process, label, and
                physical relationship shown was authored by me from my own understanding of the
                retrieval physics; the AI was directed to illustrate it, not to originate it.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ============================================================
# SECTION 1 — WHY NO2, WHY FROM SPACE
# ============================================================
st.markdown("### Why NO₂ Can Be “Seen” From Orbit at All")

st.markdown("""
GPIE's core evidence is a satellite-retrieved gas concentration, not a ground sensor reading — so
the causal claims in this project rest on trusting a genuine piece of atmospheric physics: **NO₂
absorbs sunlight at very specific wavelengths, and that absorption can be measured remotely.**

Sunlight travels down through the atmosphere, and any NO₂ molecules in its path absorb a portion
of it in the near-UV and visible range (roughly 400–450 nm) — a **fingerprint absorption band**
unique enough to distinguish NO₂ from other trace gases. The remaining, partially-absorbed light
scatters off the Earth's surface and atmosphere back up toward space, where TROPOMI's
spectrometer on the Sentinel-5P satellite records it. The physical law governing how much light
is absorbed is the **Beer–Lambert law**:
""")

st.latex(r"I = I_0 \, e^{-\sigma N L}")

st.markdown("""
where **I₀** is the incoming solar intensity, **σ** is NO₂'s known absorption cross-section at a
given wavelength, **N** is the NO₂ number density, and **L** is the atmospheric path length the
light travelled through. Because σ is a known physical constant (measured in laboratories), and
I₀ and I are what TROPOMI's spectrometer actually records, this equation can be inverted to solve
for **N·L** — the quantity actually retrieved, called a **slant column density**.
""")

st.markdown("---")

# ============================================================
# SECTION 2 — FROM SLANT COLUMN TO A POLICY-RELEVANT NUMBER
# ============================================================
st.markdown("### From a Slant Column to a Number GPIE Can Use")

st.markdown("""
The retrieval described above measures NO₂ integrated along the **slant path** the sunlight
actually travelled — which depends on the sun's angle and the satellite's viewing angle, both of
which change from pixel to pixel and orbit to orbit. To make measurements comparable across
space and time, the slant column density is divided by an **air mass factor (AMF)** — a
radiative-transfer correction that accounts for viewing geometry, surface reflectivity, cloud
cover, and the vertical distribution of NO₂ itself — producing a geometry-independent
**vertical column density (VCD)**, reported in mol/m². This is the number visualized in the
diagram above and the number GPIE's dashboards actually use.

Two things about this process matter directly for GPIE's credibility as evidence: first, this is
a **calibrated physical measurement**, entirely independent of any national reporting system or
government-submitted inventory — which is precisely why it can serve as an unbiased dependent
variable for testing whether the European Climate Law changed real-world pollution levels,
rather than merely changed what governments chose to report. Second, TROPOMI's roughly 3.5 × 5.5
km native pixel resolution is fine enough to resolve individual urban pollution hotspots — visible
directly in the diagram's retrieved column-density map — which is what makes country-level and,
in principle, city-level aggregation for GPIE's causal model possible in the first place.
""")

st.markdown("---")

st.markdown(
    f"<p class='caption-text' style='text-align:center;'>GPIE — The Physics Behind the Policy Verdict</p>",
    unsafe_allow_html=True,
)
