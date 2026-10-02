import json
import os
import sys

import pandas as pd
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE, embed_html

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>🔎 PIXEL-LEVEL CHECK</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>Pollution Level or EU Membership?</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
The country-level model finds that NO₂ fell more in the EU-27 than in the comparison group. A country
average cannot say **where** inside a country that happened. So every daily 0.1° raster was kept
(2,192 days) and the question was asked again at pixel level: does NO₂ fall more where the EU is, or
where pollution was high to begin with?
""")

with open(os.path.join(PROJECT_ROOT, "data", "grid_baseline_checks.json"), encoding="utf-8") as f:
    checks = json.load(f)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("PIXELS COMPARED", f"{checks['pixels']['eu'] + checks['pixels']['control']:,}", "0.1° grid")
with col2:
    st.metric("NOT MATCHED", "−1.34 × 10⁻⁶", "p = 0.012", delta_color="off")
with col3:
    st.metric("MATCHED ON POLLUTION LEVEL", "−0.21 × 10⁻⁶", "p = 0.341", delta_color="off")

st.warning(
    "**Result: the decline is regional, not institutional.** It grows with how polluted a pixel was before "
    "treatment, and it is large in north-western Europe on both sides of the EU border (Germany −21%, United "
    "Kingdom −20%, Switzerland −18%) and small in south-eastern Europe on both sides of it (Romania −4%, "
    "Serbia 0%). A country average turns that regional pattern into an apparent EU effect."
)

st.markdown("---")
st.markdown("### Change by Starting Pollution Level")

chart = os.path.join(PROJECT_ROOT, "outputs", "interactive", "no2_change_by_baseline.html")
if os.path.exists(chart):
    with open(chart, "r", encoding="utf-8") as f:
        embed_html(f.read(), height=570, scrolling=False)
else:
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "no2_change_by_baseline.png"), use_container_width=True)

rows = pd.DataFrame(checks["change_by_baseline_class"])
table = rows.pivot(index="baseline_class_1e-5", columns="group", values=["pixels", "change_from_jul2023_pct"])
order = ["<1.5", "1.5-2", "2-2.5", "2.5-3", "3-4", "4-5", "5-7", ">7"]
table = table.reindex(order)
show = pd.DataFrame({
    "Pre-treatment NO₂ (10⁻⁵ mol/m²)": order,
    "EU-27 pixels": [f"{int(v):,}" for v in table[("pixels", "EU-27")]],
    "EU-27 change": [f"{v:+.1f}%" for v in table[("change_from_jul2023_pct", "EU-27")]],
    "Comparison pixels": [f"{int(v):,}" for v in table[("pixels", "control")]],
    "Comparison change": [f"{v:+.1f}%" for v in table[("change_from_jul2023_pct", "control")]],
})
st.dataframe(show, hide_index=True, use_container_width=True)

reg = checks["pixel_regression_change_from_jul2023"]
st.markdown(
    "<p class='caption-text'>Change is July 2023 – December 2024 against January 2019 – June 2021, balanced by "
    f"calendar month. Across all {reg['n_pixels']:,} pixels the change is {reg['pre']['coefficient']:.3f} per unit "
    f"of pre-treatment NO₂ (R² = {reg['r_squared']:.2f}). Once the starting level is accounted for, EU pixels "
    f"do not differ from comparison pixels (p = {reg['eu']['p_value']:.3f}).</p>",
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown("### The DiD, Comparing Like with Like")

main = checks["classes from Jan 2019 - Jun 2021, all months"]
alt = checks["classes from 2019 only, estimated on 2020-2024"]
fmt = lambda r: (f"{r['coefficient']:+.2f} × 10⁻⁶".replace("-", "−"), f"{r['p_value']:.3f}")
did = pd.DataFrame([
    ["Not matched on pre-treatment level", *fmt(main["not_matched"])],
    ["Matched on pre-treatment level", *fmt(main["matched_on_baseline"])],
    ["Matched, Jul 2021 – Jun 2023", *fmt(main["matched_jul2021_jun2023"])],
    ["Matched, from Jul 2023", *fmt(main["matched_from_jul2023"])],
    ["Matched, classes from 2019 only, estimated on 2020–2024", *fmt(alt["matched_on_baseline"])],
], columns=["Model (country × class × month cells)", "EU × post (mol/m²)", "p"])
st.dataframe(did, hide_index=True, use_container_width=True)

st.markdown("""
Without matching, the cell-level model returns the country-level estimate. With pixels compared only
against comparison-group pixels of the same pollution class, most of it disappears and what remains is
not significant.
""")

st.markdown("---")
st.markdown("### Country by Country: a Regional Pattern")

st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "no2_change_by_country.png"), use_container_width=True)

with open(os.path.join(PROJECT_ROOT, "data", "stress_tests.json"), encoding="utf-8") as f:
    stress = json.load(f)["pixel_level"]

def _row(label, key, part="matched_on_baseline"):
    r = stress[key][part]
    return [label, f"{r['coefficient']:+.2f} × 10⁻⁶".replace("-", "−"), f"{r['p_t']:.3f}"]

regions = pd.DataFrame([
    _row("North-west: EU members vs United Kingdom, Switzerland", "north-west: EU members vs UK, CH"),
    _row("South-east: EU members vs Western Balkans", "south-east: EU members vs Western Balkans"),
    _row("Inside the EU: north-west vs south-east members", "inside the EU: north-west vs south-east members"),
    _row("EU-27 vs United Kingdom, Norway, Switzerland, Iceland", "EU-27 vs UK, NO, CH, IS"),
    _row("EU-27 vs Western Balkans", "EU-27 vs Western Balkans"),
    _row("Comparison halves: UK, NO, CH, IS vs Western Balkans", "placebo: UK, NO, CH, IS vs Western Balkans"),
    _row("EU-27 vs all nine, without November–February", "EU-27 vs all nine, without Nov-Feb"),
], columns=["Matched model (same pollution class)", "Estimate (mol/m²)", "p"])
st.dataframe(regions, hide_index=True, use_container_width=True)

st.markdown("""
Within the north-west and within the south-east, the EU border makes no detectable difference. Between the
two regions, inside the EU, the difference is larger than any EU-versus-comparison estimate. The two halves
of the comparison group also differ from each other, so the overall matched estimate averages two opposite
comparisons. Winter months carry much of the size of these estimates; in percentage terms the regional
gradient is still there in March–October (the dots in the chart).
""")

st.markdown("---")
st.markdown("### Where NO₂ Fell")

pixel_map = os.path.join(PROJECT_ROOT, "outputs", "interactive", "no2_pixel_change_map.html")
if os.path.exists(pixel_map):
    with open(pixel_map, "r", encoding="utf-8") as f:
        embed_html(f.read(), height=600, scrolling=False)
else:
    st.image(os.path.join(PROJECT_ROOT, "outputs", "plots", "no2_change_map.png"), use_container_width=True)

st.markdown(
    "<p class='caption-text'>Blue = NO₂ fell, red = NO₂ rose. The decline covers the polluted belt from England "
    "through the Low Countries and western Germany to the Po Valley, plus large cities, and it does not stop at "
    "the EU border.</p>",
    unsafe_allow_html=True,
)

st.info(
    "**Caveat:** the highly polluted comparison pixels are almost all in the United Kingdom, with some in "
    "Switzerland and Serbia. The United Kingdom kept EU-derived vehicle and industrial emission standards, so "
    "this check separates EU membership from pollution level, not EU-origin regulation from its absence."
)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)
