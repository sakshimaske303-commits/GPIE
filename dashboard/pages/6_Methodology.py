import streamlit as st
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>📖 METHODOLOGY & LIMITATIONS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>The Full Scientific Validation Journey</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
### Data Sources

GPIE integrates eight independently-sourced datasets, all acquired at the country level for
2019–2024 (30 countries: EU-27 + UK, Norway, Switzerland) — a ninth, WorldPop population, was
also acquired but excluded as a model input (see Limitations below):
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    - **NO₂** — Sentinel-5P TROPOMI (Sentinel Hub Statistical API)
    - **NDVI** — CGLS 300m (Sentinel Hub Statistical API)
    - **Climate** — ERA5 Reanalysis (temperature, precipitation)
    - **GDP** — Eurostat (EU-27) + World Bank (control group)
    """)
with col2:
    st.markdown("""
    - **Land Cover** — ESA WorldCover 10m v200
    - **Elevation** — Copernicus DEM GLO-30
    - **Policy Records** — EUR-Lex (EU Green Deal legislation)
    - **Administrative Boundaries** — Eurostat GISCO (NUTS) + GADM
    """)

st.markdown("---")

# ============================================================
# PROOF-OF-WORK POPOVERS — tiny, pulsing "📸" buttons next to the
# exact validation step they back up. Click to reveal the
# screenshot inline; nothing pushes the page layout around. Drop
# the PNGs into outputs/proof_screenshots/ (see filenames below)
# and these activate automatically — until then each falls back to
# a quiet "not added yet" note instead of breaking the page.
# ============================================================
st.markdown(f"""
<style>
    div[data-testid="stPopover"] button {{
        animation: proof-blink 1.8s ease-in-out infinite;
        border: 3px solid {PALETTE['coral']} !important;
        width: 32px !important;
        height: 32px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        min-height: unset !important;
        min-width: unset !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div[data-testid="stPopover"] button p {{
        margin: 0 !important;
        font-size: 0.95rem !important;
        line-height: 1 !important;
    }}
    @keyframes proof-blink {{
        0%, 100% {{ box-shadow: 0 0 0px rgba(248, 131, 121, 0); }}
        50% {{ box-shadow: 0 0 12px rgba(248, 131, 121, 0.85); }}
    }}
</style>
""", unsafe_allow_html=True)

PROOF_DIR = os.path.join(PROJECT_ROOT, "outputs", "proof_screenshots")

def proof_popover(filename, caption):
    path = os.path.join(PROOF_DIR, filename)
    with st.popover("📸"):
        if os.path.exists(path):
            st.image(path, caption=caption, use_container_width=True)
        else:
            st.caption(f"Screenshot not added yet — save it as `outputs/proof_screenshots/{filename}`.")

st.markdown("### The Validation Sequence")

s1a, s1b = st.columns([0.94, 0.06])
with s1a:
    with st.expander("**Step 1 — Initial Single-Cohort Model**", expanded=False):
        st.markdown("""
        The first causal model compared all 27 EU countries before vs. after the European Climate Law
        (30 June 2021), using country and seasonal fixed effects. This found a statistically significant
        reduction in NO₂ (p = 0.026, as originally computed with classical/non-clustered standard errors).

        **A later verification correction**: this initial-model figure had not been re-estimated with the
        cluster-robust standard errors this project applies everywhere else (Step 5 below). Re-estimated
        cluster-robust, the same NO₂ coefficient yields p = 0.041 — still significant at 5%, so this
        doesn't change the conclusion below. It does matter more for the secondary NDVI outcome's initial
        model (see the *Causal Results* page): its originally-reported p = 0.128 (not significant) becomes
        p = 0.0017 (significant) once corrected the same way.

        **The problem**: because all 27 countries were treated simultaneously, there was no untreated
        comparison group — making it mathematically impossible to distinguish a genuine policy effect
        from a general, ongoing pollution-decline trend, regardless of which standard-error type is used.
        """)
with s1b:
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    proof_popover("01_causal_inference_vscode.png", "causal_inference.py open in VS Code — the initial single-cohort model (all 27 EU countries, before vs. after the Climate Law).")

s2a, s2b = st.columns([0.94, 0.06])
with s2a:
    with st.expander("**Step 2 — Placebo Test**", expanded=False):
        st.markdown("""
        To test the result's credibility, the identical model was re-run with the treatment date
        artificially shifted to 30 June 2020 — a date with no relevant policy event.

        **The result**: the placebo model found an equally significant "effect" (p = 0.004, cluster-robust) — even
        more significant than the real result. This proved the original model was capturing a general
        trend, not a policy-specific effect. Adding an explicit linear time trend confirmed this: once
        the trend was controlled for, the original "significant" effect disappeared entirely (p = 0.186, cluster-robust).
        """)
with s2b:
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    proof_popover("02_causal_inference_placebo_vscode.png", "causal_inference_placebo.py open in VS Code — the placebo test with the treatment date artificially shifted to 30 June 2020, proving the original model was capturing a general trend.")

s3a, s3b = st.columns([0.94, 0.06])
with s3a:
    with st.expander("**Step 3 — Building a Genuine Control Group**", expanded=False):
        st.markdown("""
        Three non-EU European countries were added as a control group — the **UK, Norway, and
        Switzerland** — selected for being geographically and economically comparable to the EU-27
        while not being subject to EU Green Deal legislation. This required:
        - New boundary data (GADM Level 0)
        - Extended satellite data acquisition for all 30 countries
        - A second GDP data source (World Bank API) for non-EU countries

        This enabled a genuine two-group Difference-in-Differences model — the version presented on
        the *Causal Results* page.
        """)
with s3b:
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    proof_popover("03_control_group_boundaries_qgis.png", "EU-27 (NUTS boundaries) plus the three control countries — UK, Norway, Switzerland (GADM boundaries) — loaded together in QGIS, showing the full 30-country treatment-vs-control footprint.")

with st.expander("**Step 4 — Event-Study Robustness Check**", expanded=False):
    st.markdown("""
    The overall DiD result was further validated by estimating the treatment effect separately for
    all 23 individual quarters (2019Q1–2024Q4), rather than as a single average — confirming the
    null result held consistently across every quarter, both before and after treatment.
    """)

s5a, s5b = st.columns([0.94, 0.06])
with s5a:
    with st.expander("**Step 5 — Cluster-Robust Standard Errors & Further Robustness Checks**", expanded=False):
        st.markdown("""
        All models were re-estimated with standard errors clustered by country, the standard
        correction for panel data where a country's repeated monthly observations are serially
        correlated (uncorrected OLS standard errors understate true uncertainty). This made the null
        NO₂ result *more* solid (p = 0.632 → 0.663), not less.

        Five further robustness checks were run against the corrected NO₂ model, all reinforcing the
        null finding: removing GDP entirely (rules out GDP as a biasing "bad control"); a
        log-transformed outcome (rules out functional-form artifacts); shifting the assumed treatment
        date by ±6/±12 months (no shifted date reaches significance); splitting EU-27 countries by
        baseline pollution level (neither subgroup is significant); and a formal minimum-detectable-effect
        calculation, which found this design can reliably detect an effect of ~28% of baseline NO₂ or
        larger — the observed coefficient (~4.4% of baseline) is well below that threshold.

        Applying this same rigor to the **secondary NDVI outcome** — which had only ever been tested
        with the original, single-cohort design — produced a statistically significant relative decline
        once the same control-group correction was applied (see *Causal Results* page). A verification
        pass later found that outcome's own initial single-cohort model was, once correctly re-estimated
        with cluster-robust standard errors, already significant too (p = 0.0017, not the originally
        reported p = 0.128) — so the control-group correction's role for NDVI is better identification
        of an EU-specific effect, not first-time detection of significance. Full details and all
        reported numbers are in the Research Paper and Project Report documents in the project repository.
        """)
with s5b:
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    proof_popover("04_causal_inference_final_did_vscode.png", "causal_inference_final_did.py open in VS Code — the final two-group Difference-in-Differences model with cluster-robust standard errors, the headline model behind the Causal Results page.")

st.markdown("---")

st.markdown("### ⚠️ Honest Limitations")

st.warning("""
**Statistical power**: The control group consists of only 3 countries. The overall model's
confidence interval — [-7.68 × 10⁻⁶, +4.88 × 10⁻⁶] — is reasonably wide, not tightly clustered
around zero. Quantified directly: at 80% power, this design's minimum detectable effect is
roughly **28% of the EU-27's pre-treatment average NO₂** — this study can rule out an effect of
that size or larger, but not a smaller one. This means the honest conclusion is not simply
*"the policy had no effect,"* but rather: *with this study's sample size and three-country
control group, no effect of at least ~28% could be detected* — consistent with either a
genuinely negligible effect, or a real but more modest effect this design lacks the power to see.
""")

st.warning("""
**The NDVI secondary-outcome finding is exploratory, not causal.** Once given the same
control-group correction as NO₂, NDVI shows a statistically significant relative decline
(p = 0.012) — but this analysis does not control for land-use change, drought/precipitation-driven
vegetation stress, or agricultural-policy shifts between treatment and control regions, any of
which could plausibly drive the result independent of the Climate Law. It is reported as a
genuine, robust finding meriting further investigation, not as evidence the Climate Law affected
vegetation.
""")

st.info("""
**Module 9 (Economic Efficiency Ranking) was deliberately scoped out.** Ranking policies by
"cost-per-unit-environmental-improvement" presupposes a measurable improvement to rank against —
since Module 8 found no statistically significant effect, constructing such a ranking would
require manufacturing significance the data does not support. This decision is itself treated as
a finding consistent with GPIE's "Trust, But Verify" design principle.
""")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine | Developed by Sakshi D. Maske</p>",
    unsafe_allow_html=True,
)