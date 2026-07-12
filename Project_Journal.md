# GREEN POLICY INTELLIGENCE ENGINE (GPIE)
## Project Journal — Final Version

---

## Project Overview

The Green Policy Intelligence Engine (GPIE) is a geospatial causal-inference framework designed to independently evaluate whether the European Green Deal — specifically its flagship legislation, the European Climate Law (Regulation (EU) 2021/1119) — produced a measurable environmental effect. Rather than relying on self-reported government claims of policy success, GPIE integrates satellite-derived Earth Observation data, climate reanalysis, and economic indicators into a rigorous statistical framework, following a "Trust, But Verify" research philosophy: government policy claims are treated as hypotheses to be independently tested against observational evidence, not facts to be assumed.

The European Green Deal was selected as the demonstration case due to its comprehensive policy scope, high-quality open data availability, and global relevance. The underlying methodology, however, is designed to be transferable to any country or policy context.

## Problem Statement

Governments invest heavily in environmental and climate policy, yet independently verifying whether such investments produce measurable outcomes remains difficult. Administrative self-reporting is inconsistent across countries, and simple before-after comparisons of environmental indicators cannot distinguish a policy's true effect from broader trends that would have occurred regardless. GPIE addresses this gap by building a reproducible, satellite-driven framework capable of testing policy effectiveness with the statistical rigor required to support a genuine causal claim — rather than a correlational one.

## Aim

To develop a geospatial framework that independently and rigorously tests whether the European Climate Law produced a statistically distinguishable reduction in air pollution across the EU-27, using satellite observations, causal inference methodology, and transparent, reproducible code.

## Research Question

Did the European Climate Law (effective 30 June 2021) produce a measurable, EU-specific reduction in tropospheric NO₂ pollution, once independently tested against a genuine non-EU comparison group using satellite-derived evidence?

---

## Data Sources

GPIE integrates seven independently-sourced datasets across 30 countries (EU-27 plus a three-country control group), spanning 2019–2024:

| Dataset | Provider | Purpose |
|---|---|---|
| NO₂ (Sentinel-5P TROPOMI) | ESA/Copernicus | Primary outcome variable |
| NDVI (CGLS) | Copernicus Land Monitoring Service | Secondary outcome variable (vegetation health) |
| Climate (ERA5) | ECMWF | Control variables (temperature, precipitation) |
| GDP | Eurostat (EU-27), World Bank (control group) | Control variable (economic activity) |
| Land Cover (ESA WorldCover) | ESA | Environmental context |
| Elevation (Copernicus DEM) | ESA/Copernicus | Environmental context |
| Policy Records | EUR-Lex | Policy timeline reference |
| Administrative Boundaries | Eurostat GISCO (NUTS), GADM | Spatial framework |

All satellite and climate datasets were acquired via the Sentinel Hub Statistical API and the Copernicus Climate Data Store, using automated, reproducible Python pipelines rather than manual downloads.

---

## Methodology

### Phase 1 — Policy Database (Module 1)

An automated web-scraping pipeline was built to extract structured European Green Deal policy records from EUR-Lex, capturing policy type, publication year, legal status, and thematic classification. This established the "policy claims" side of the project's core comparison, and identified the European Climate Law as the study's treatment event.

### Phase 2 — Earth Observation Data Acquisition (Module 2)

NO₂, NDVI, and climate data were acquired for all 30 countries via the Sentinel Hub Statistical API, chosen over raw satellite tile download for its scalability — server-side aggregation avoided the storage and processing burden of handling raw multi-terabyte satellite imagery. Static datasets (elevation, land cover) were acquired for the EU-27 only, since these are absorbed by country-level fixed effects in the causal model and were not required for the control group. GDP was sourced from Eurostat for EU-27 countries and the World Bank for the three control-group countries, since Eurostat does not cover non-EU nations.

### Phase 3 — Preprocessing and Standardization (Module 3)

All datasets were converted into a standardized, country-month structure. Two master datasets were constructed: an EU-27-only dataset (1,944 rows) used for exploratory analysis, and a 30-country dataset (2,160 rows) — including EU-27 and the control group — used for the project's final causal-inference model.

### Phase 4 — Causal Inference: Design and Validation (Module 8)

This module constitutes GPIE's core scientific contribution and underwent a rigorous, multi-stage validation process rather than a single model-and-report approach.

**Initial model.** A first Difference-in-Differences model, comparing all 27 EU countries before and after 30 June 2021 using country and seasonal fixed effects, found a statistically significant reduction in NO₂ (p = 0.026).

**Placebo test.** Before accepting this result, the identical model was re-run using a fake treatment date (30 June 2020), where no relevant policy event occurred. This placebo test found an equally significant "effect" (p = 0.002) — revealing that the original model was detecting a general, ongoing pollution-decline trend rather than an effect specific to the Climate Law. This is a well-documented limitation of any single-cohort design applied to a policy affecting an entire study population simultaneously, with no untreated comparison group available to isolate the policy-specific effect from the underlying trend.

**Methodological correction.** In response, a genuine external control group was constructed: the United Kingdom, Norway, and Switzerland — three non-EU European countries that are geographically and economically comparable to the EU-27 but not subject to EU Green Deal legislation. This required acquiring new boundary data (GADM), extending satellite data acquisition to all 30 countries, and sourcing a second GDP dataset for the control group. A proper two-group Difference-in-Differences model was then estimated, with the interaction between EU-27 membership and the post-treatment period as the core causal estimator.

**Final result.** The corrected model found **no statistically significant EU-specific effect** (coefficient = −1.40 × 10⁻⁶, p = 0.632, 95% confidence interval spanning zero). An event-study extension — testing the effect separately across all 23 individual quarters from 2019 to 2024 — found no significant effect in any single quarter, both confirming the model's parallel-trends assumption (no pre-treatment divergence between groups) and ruling out a delayed effect masked by averaging.

**Honest limitation.** The control group consists of only three countries, and the model's confidence interval is reasonably wide rather than tightly clustered around zero. The rigorous conclusion is therefore not simply "the policy had no effect," but that **no statistically distinguishable EU-specific effect could be detected given this study's sample size and control-group scale** — a result consistent with either a genuinely negligible effect, or a control group too small to provide adequate statistical power to detect a real but modest one.

### Phase 5 — Economic Efficiency Ranking (Module 9): Deliberately Scoped Out

Module 9 was originally planned to rank environmental policies by cost-effectiveness. This was deliberately not pursued, for a specific, principled reason: ranking interventions by "cost per unit of environmental improvement" presupposes a measurable improvement to rank against. Since Module 8's validated finding is that no statistically significant effect was detected, constructing such a ranking would require either manufacturing significance the data does not support, or ranking against an effect size indistinguishable from zero — neither of which is scientifically defensible. This decision is itself consistent with GPIE's core design principle: verification should not be bent to produce results convenient for a downstream module.

### Phase 6 — Geospatial Visualization (Module 10)

Seven geospatial and statistical visualizations were produced using a Python-based mapping pipeline (`geopandas` and `matplotlib`), covering NO₂ distribution, a 2019-vs-2024 before/after comparison, the treatment/control study design, land cover, NDVI, GDP, and the event-study result. Each visualization was independently verified for correctness before finalization.

### Phase 7 — Interactive Dashboard and Deployment (Module 11)

The complete project was packaged into an eight-page interactive Streamlit dashboard, covering the study design, environmental data, before/after comparison, economic context, causal results, full methodology, an interactive country-level trend explorer, and downloadable raw data. The full codebase, documentation, and reproducible pipeline were published as an open-source GitHub repository.

---

## Final Findings

1. **No statistically significant EU-specific reduction in NO₂** was detected attributable to the European Climate Law, once rigorously tested against a genuine non-EU control group.
2. **NDVI (vegetation health)** likewise showed no statistically significant treatment effect, consistent with vegetation-health outcomes typically responding to policy on longer timescales than atmospheric pollutants.
3. **The validation process itself — placebo test, control-group construction, and event-study disaggregation — is as significant a project output as the substantive result.** An initial, seemingly positive finding was actively tested and shown to be unreliable before a more rigorous, honestly null result was reached.
4. **This is reported as a credible scientific finding, not a project shortfall.** GPIE's purpose was to independently verify a policy claim, not to confirm it — and a rigorously validated null result fulfills that purpose exactly as much as a positive one would have.

## Limitations

- The control group (3 countries) is small relative to the treatment group (27 countries), limiting statistical power to detect a modest true effect.
- The EUR-Lex policy database returned a limited number of formally scraped records; the treatment date was instead anchored to the single most legally significant instrument (the European Climate Law) rather than a comprehensive policy-intensity measure.
- WorldPop population data was only available for 2019–2020 within the accessible dataset version; population was reclassified as a supporting/descriptive variable rather than a model input, given its incomplete temporal coverage relative to the study period.
- GDP for the control group required a currency conversion (USD to EUR) using approximate annual average exchange rates rather than precise historical rates, an acceptable approximation for a control variable but not for a primary variable of interest.

## Deliverables

- A fully automated, reproducible Python data-acquisition and processing pipeline across seven datasets and 30 countries
- Two clean, merged master datasets (EU-27-only and 30-country control-group versions)
- A rigorously validated causal-inference model, including placebo-test and event-study robustness checks
- Seven publication-quality geospatial and statistical visualizations
- An interactive, publicly deployed Streamlit dashboard
- Complete open-source codebase and documentation, published on GitHub

## Current Status

**Complete.** All eleven planned project modules have been executed, with Module 9 formally and transparently scoped out for a documented scientific reason rather than left incomplete. The project is deployed as a public GitHub repository and an interactive dashboard, ready for portfolio and academic presentation.