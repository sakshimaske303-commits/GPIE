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
2019–2024 (36 countries: EU-27 + a 9-country non-EU control group — UK, Norway, Switzerland,
Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, Serbia) — a ninth,
WorldPop population, was also acquired but excluded as a model input (see Limitations below):
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
        Nine non-EU European countries were added as a control group — **UK, Norway, Switzerland,
        Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, and Serbia** —
        selected for being geographically and economically comparable to the EU-27 while not being
        subject to EU Green Deal legislation, spanning both established Western European economies
        and EU-accession-candidate economies in the Western Balkans. This required:
        - New boundary data (GADM Level 0 for UK/Norway/Switzerland; NUTS directly for the remaining six)
        - Extended satellite data acquisition for all 36 countries
        - A second GDP data source (World Bank API) for non-EU countries

        This enabled a genuine two-group Difference-in-Differences model — the version presented on
        the *Causal Results* page.
        """)
with s3b:
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    proof_popover("03_control_group_boundaries_qgis.png", "EU-27 (NUTS boundaries) plus the nine control countries (GADM for UK/Norway/Switzerland, NUTS for the rest) — loaded together in QGIS, showing the full 36-country treatment-vs-control footprint.")

with st.expander("**Step 4 — Event-Study Robustness Check**", expanded=False):
    st.markdown("""
    The overall DiD result was further validated by estimating the treatment effect separately for
    all 23 individual quarters (2019Q1–2024Q4), rather than as a single average. Every pre-treatment
    quarter is non-significant, supporting the parallel-trends assumption. Four post-treatment
    quarters (2022Q2, 2023Q2, 2024Q2, 2024Q3) are nominally significant, all negative, all falling
    in Q2 or Q3 — a consistent pattern, not scattered noise, corroborating the heterogeneity check below.
    """)

s5a, s5b = st.columns([0.94, 0.06])
with s5a:
    with st.expander("**Step 5 — Cluster-Robust Standard Errors & Further Robustness Checks**", expanded=False):
        st.markdown("""
        All models were re-estimated with standard errors clustered by country, the standard
        correction for panel data where a country's repeated monthly observations are serially
        correlated (uncorrected OLS standard errors understate true uncertainty).

        Five further robustness checks were run against the corrected, pooled NO₂ model. Removing
        GDP entirely barely moves the coefficient (rules out GDP as a biasing "bad control"); shifting
        the assumed treatment date by ±6/±12 months finds one alternate date (−6 months) nominally
        significant on its own (p = 0.021), flagged honestly as a genuine dating-uncertainty signal
        rather than smoothed over; splitting EU-27 countries by baseline pollution level finds a
        **statistically significant effect in the 14 higher-baseline countries** (p = 0.003) and none
        in the 13 lower-baseline countries; a log-transformed outcome shrinks toward zero, consistent
        with the effect being concentrated rather than a uniform percentage decline everywhere; and a
        formal minimum-detectable-effect calculation found this design can reliably detect a *pooled*
        effect of ~12.7% of baseline NO₂ or larger.

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

st.markdown("### 🎯 Independent Corroboration: Synthetic Control &amp; Spatial Diagnostics")

st.markdown("""
The control group's construction invites two specific objections: that equal weighting might
mismatch the treated series' true counterfactual trajectory, and that country-level readings
might not be spatially independent observations. Both were tested directly rather than left as
theoretical concerns.

**Augmented Synthetic Control** (Abadie, Diamond &amp; Hainmüller, 2010; ridge-augmented per
Ben-Michael, Feller &amp; Rothstein, 2021) fits convex donor weights to match the EU-27's
pre-treatment NO₂ trajectory, rather than averaging control countries equally. Norway's and
Iceland's NO₂ series both have real, high-latitude coverage gaps that persist even after a clean
re-fetch — Norway 43% pre-treatment coverage, Iceland 70% — so the donor pool is the remaining
seven control countries (UK, Switzerland, Albania, Bosnia and Herzegovina, Montenegro, North
Macedonia, Serbia). The post-treatment gap between actual and synthetic EU-27 is −1×10⁻⁶ — the same
sign and order of magnitude as the pooled DiD coefficient (−2.22×10⁻⁶), reached through a method
that doesn't rely on the DiD model's fixed-effects specification at all. With 7 donors, the
in-space placebo is a genuine permutation-style check: the real EU-27 gap ranks 2nd of 8 by size.

**Moran's I spatial-autocorrelation diagnostic** (KNN-4 weights on country centroids, robust to
island geometries like Cyprus, Malta, Ireland, and Iceland) tests whether country-clustered standard
errors are missing cross-border spatial dependence. Raw NO₂ levels are strongly clustered (Global
Moran's I = 0.570, p = 0.001) — expected for an atmospheric pollutant. The DiD model's own
residuals are not significantly clustered (I = 0.069, p = 0.135): the country and month fixed
effects already absorb the large majority of that dependence. Local Moran's I (LISA) identifies a
High-High cluster (Benelux, Germany, Denmark, UK) and a Low-Low cluster (Nordic/Baltic countries
plus Iceland), with Switzerland and Ireland as significant Low-High outliers.

Neither check overturns the pooled null result — that was never the point. Both close off a
specific way the control group's construction could otherwise be second-guessed, though neither
speaks directly to the higher-baseline heterogeneity finding above, since both evaluate the pooled
EU-27 aggregate.
""")

st.markdown("---")

st.markdown("### ⚠️ Honest Limitations")

st.warning("""
**Statistical power**: Even with a 9-country control group (7 for the synthetic control
specification above, since Norway's and Iceland's NO₂ coverage remain too incomplete to use as
donors even after a clean re-fetch), the pooled model's confidence interval — [-4.87 × 10⁻⁶, +4.32 × 10⁻⁷]
— still spans zero. Quantified directly: at 80% power, this design's minimum detectable effect for
the pooled estimate is roughly **12.7% of the EU-27's pre-treatment average NO₂**, down
substantially from what a smaller control group could resolve. This means the honest conclusion is
not *"the policy had no effect"* nor *"the policy worked,"* but rather: the pooled, EU-wide average
effect is not conventionally significant, while a real effect concentrated in higher-baseline
member states and specific post-treatment quarters is — a genuinely open finding this design can
characterize but not fully resolve without a longer panel or sub-national data. The synthetic
control reaches the same pooled conclusion through weighted rather than equal donor weighting,
now with a real 7-donor permutation-style placebo — corroborating, not resolving, the underlying
question of how far the effect extends beyond the higher-baseline subgroup.
""")

st.warning("""
**The NDVI secondary-outcome finding is exploratory, not causal.** Once given the same
control-group correction as NO₂, NDVI shows a statistically significant relative decline
(p = 0.007) — but this analysis does not control for land-use change, drought/precipitation-driven
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