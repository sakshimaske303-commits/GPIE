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

GPIE compiles eight data sources for 2019–2024 (36 countries: EU-27 + a 9-country non-EU comparison
group — UK, Norway, Switzerland, Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia,
Serbia). The headline model uses NO₂, ERA5 temperature/precipitation and GDP; NDVI is a secondary
outcome; land cover, elevation and EUR-Lex records are descriptive context. A ninth source, WorldPop
population, was acquired for 2019–2020 only and is not used:
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    - **NO₂** — Sentinel-5P TROPOMI (Sentinel Hub Process API, daily rasters)
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

# Proof popover buttons. They show my screenshots from outputs/proof_screenshots/.
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
    with st.popover("View"):
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
        (adopted 30 June 2021, in force 29 July 2021; July 2021 = first post month), using country and
        seasonal fixed effects. This found a statistically significant
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

        **Reproducing this figure**: `causal_inference.py` was later extended with an explicit
        `time_trend` diagnostic control (see Step 2 rationale below), so it no longer reproduces this
        p = 0.026 / p = 0.041 result on its own. The original specification — identical data and fixed
        effects, without `time_trend` — lives in `causal_inference_initial_model.py`.
        """)
with s1b:
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    proof_popover("01_causal_inference_vscode.png", "causal_inference.py open in VS Code, showing the time_trend diagnostic control added after this initial single-cohort result — see causal_inference_initial_model.py for the original specification.")

s2a, s2b = st.columns([0.94, 0.06])
with s2a:
    with st.expander("**Step 2 — Placebo Test**", expanded=False):
        st.markdown("""
        To test the result's credibility, the identical model was re-run with the treatment date
        artificially shifted to 30 June 2020 — a date with no relevant policy event.

        **The result**: the placebo model found an equally significant "effect" (p = 0.004, cluster-robust) — even
        more significant than the real result. This showed the single-cohort design could not separate a
        policy-dated break from Europe's continuing NO₂ decline. Adding an explicit linear time trend points
        the same way: with the trend controlled for, the original estimate is no longer significant
        (p = 0.186, cluster-robust). (The placebo was run on the full 2019–2024 panel, not on pre-treatment
        data only.)
        """)
with s2b:
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    proof_popover("02_causal_inference_placebo_vscode.png", "causal_inference_placebo.py open in VS Code — the placebo test with the treatment date artificially shifted to 30 June 2020.")

with st.expander("**Step 3 — Building an External Comparison Group**", expanded=False):
    st.markdown("""
    Nine non-EU European countries were added as a comparison group — **UK, Norway, Switzerland,
    Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, and Serbia** —
    selected for being geographically and economically comparable to the EU-27 and not directly bound
    by the Climate Law. They are not fully untreated by EU climate policy: Norway and Iceland are in
    the EU ETS via the EEA, Switzerland's ETS has been linked to the EU ETS since 2020, and the Western
    Balkans committed to align with the Green Deal in the 2020 Sofia Green Agenda. This required:
    - New boundary data (GADM Level 0 for UK/Norway/Switzerland; NUTS directly for the remaining six)
    - Extended satellite data acquisition for all 36 countries
    - A second GDP data source (World Bank API) for non-EU countries

    This enabled the two-group Difference-in-Differences model presented on the *Causal Results* page.
    """)

with st.expander("**Step 4 — Event-Study Robustness Check**", expanded=False):
    st.markdown("""
    The overall DiD result was further validated by estimating the treatment effect separately for
    23 quarters (2019Q1–2024Q4, relative to 2021Q2), rather than as a single average. Seven of the nine
    pre-treatment quarters differ significantly from the reference quarter, so the parallel-trends
    assumption is not supported. The coefficients follow a seasonal pattern (positive in Q1/Q4, negative
    in Q2/Q3) before and after treatment — consistent with a larger seasonal NO₂ cycle in the more
    polluted EU countries — rather than a response dated to the law. The 23 coefficients come from one
    regression, so they are not independent tests.
    """)

s5a, s5b = st.columns([0.94, 0.06])
with s5a:
    with st.expander("**Step 5 — Cluster-Robust Standard Errors & Further Robustness Checks**", expanded=False):
        st.markdown("""
        All models were re-estimated with standard errors clustered by country, the standard
        correction for panel data where a country's repeated monthly observations are serially
        correlated (uncorrected OLS standard errors understate true uncertainty).

        Further robustness checks were run against the pooled NO₂ model (−1.52 × 10⁻⁶, p = 0.013).
        Removing GDP barely moves the coefficient (−1.49 × 10⁻⁶, p = 0.053; a sensitivity check, not a
        formal bad-control test). The log-outcome model gives −4.2% (p = 0.034). Shifting the treatment date
        by ±6/±12 months gives a significant estimate at **every** date (p between 0.004 and 0.028),
        including two dates before the law existed — by the logic of Step 2, the design does not tie the
        EU-specific decline to the Climate Law's date. Adding an EU-specific linear trend removes the
        treatment-date effect (+8.7 × 10⁻⁷, p = 0.243) while the trend itself is significant (−7.9 × 10⁻⁷
        per year, p = 0.016): a steady faster decline, not a step. A post-hoc split by baseline pollution
        finds the decline in the 14 higher-baseline countries (p = 0.002; log −6.4%, p = 0.006) and none in
        the 13 lower-baseline countries (p = 0.758). The minimum detectable *pooled* effect at 80% power is
        ~5.5% of the EU-27's pre-treatment NO₂.

        The **secondary NDVI outcome** shows a significant relative decline under the two-group design
        (see *Causal Results* page). Its initial single-cohort model, re-estimated with cluster-robust
        standard errors, was already significant (p = 0.0017, not the originally reported p = 0.128). Full details and all
        reported numbers are in the Research Paper document in the project repository.
        """)
with s5b:
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    proof_popover("04_causal_inference_final_did_vscode.png", "causal_inference_final_did.py open in VS Code — the final two-group Difference-in-Differences model with cluster-robust standard errors, the headline model behind the Causal Results page.")

st.markdown("---")

st.markdown("### Additional Checks: Synthetic Control &amp; Spatial Diagnostics")

st.markdown("""
The control group's construction invites two specific objections: that equal weighting might
mismatch the treated series' true counterfactual trajectory, and that country-level readings
might not be spatially independent observations. Both were tested directly rather than left as
theoretical concerns.

**Synthetic control** (Abadie, Diamond &amp; Hainmueller, 2010) fits convex donor weights to match the
EU-27's pre-treatment NO₂ series, plus a constant (intercept) adjustment. (An earlier version called this
a ridge-augmented synthetic control; the ridge term reduced to that constant shift, so it is now labelled
as what it does.) All nine comparison countries are donors (weights: Serbia 40%, Switzerland 32%, UK 28%).
Using the 27 pre / 36 post months where every series is observed, the post-treatment gap is −8.1×10⁻⁷ and
the pre-treatment fit error (RMSPE) is 2.56×10⁻⁶. The EU-27 gap ranks 5th of 10 in the in-space placebo, so
it does not stand out from the gaps of untreated countries.

**Moran's I spatial-autocorrelation diagnostic** (KNN-4 weights on country centroids, used because
Cyprus, Malta and Iceland have no land neighbours in the sample) checks for cross-border dependence,
which country-clustered standard errors do not handle. Raw NO₂ levels are strongly clustered (Global
Moran's I = 0.578, p = 0.001). The DiD residuals, tested month by month, are also clustered (median
I = 0.347; significant in 59 of 72 months), so the fixed effects do not remove the spatial dependence and
the clustered p-values are likely too small. (An earlier version reported I = 0.069, p = 0.135 on
country-averaged residuals; with country fixed effects those averages are exactly zero, so that test was
uninformative.) Local Moran's I (LISA) identifies a
High-High cluster (Benelux, Germany, Switzerland, UK) and a Low-Low cluster (Estonia, Finland, Sweden,
Norway, Iceland), with Denmark and Ireland as significant Low-High outliers.

Neither check supports reading the pooled estimate as a Climate Law effect: the synthetic control
finds nothing distinctive about the EU-27, and the spatial result means the reported p-values are too small.
""")

st.markdown("---")

st.markdown("### Honest Limitations")

st.warning("""
**Data correction**: earlier versions of this project built "monthly" NO₂ from Sentinel Hub's
Statistical API with monthly intervals. Sentinel Hub clips Sentinel-5P requests to the last 24 hours of
each interval, so those values were effectively end-of-month snapshots — which explained the patchy
coverage and impossible values (negative country means on 31 December 2023). The NO₂ series is now built
from one raster per day (Process API, 0.1° grid, QA ≥ 0.75) pooled into true monthly means, and NDVI from
monthly means of the dekadal composites. Every number on this dashboard was re-estimated; the earlier
pooled null (p = 0.101) is superseded.

**What the result does and does not show**: NO₂ fell about 5% more in the EU-27 than in the comparison
group, and the pooled estimate is significant (p = 0.013). The honest conclusion is not *"the Climate Law
worked"*: pre-treatment quarters already differ, every alternative date is significant, and an EU-specific
trend absorbs the effect. The design shows a gradual faster decline in the EU-27, not a break at the law.
With nine comparison clusters and spatially correlated residuals, the p-values are also likely too small.
""")

st.warning("""
**The NDVI secondary-outcome finding is exploratory, not causal.** Once given the same
control-group correction as NO₂, NDVI shows a statistically significant relative decline
(−0.0194, p = 0.005) — but this analysis does not control for land-use change, drought/precipitation-driven
vegetation stress, or agricultural-policy shifts between treatment and control regions, any of
which could plausibly drive the result independent of the Climate Law. It is reported as an
exploratory association, not as evidence the Climate Law affected vegetation.
""")

st.info("""
**Module 9 (Economic Efficiency Ranking) was deliberately scoped out.** Ranking policies by
"cost-per-unit-environmental-improvement" presupposes a measurable improvement to rank against —
since Module 8 did not establish an NO₂ improvement attributable to a specific policy, constructing such a ranking would
require manufacturing significance the data does not support. This decision is itself treated as
a finding consistent with GPIE's "Trust, But Verify" design principle.
""")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine | Developed by Sakshi D. Maske</p>",
    unsafe_allow_html=True,
)