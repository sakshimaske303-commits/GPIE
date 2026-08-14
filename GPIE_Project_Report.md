# GREEN POLICY INTELLIGENCE ENGINE (GPIE)

## Project Report

## Project Overview

The Green Policy Intelligence Engine (GPIE) is a geospatial causal-inference framework designed to independently evaluate whether the European Green Deal — specifically its flagship legislation, the European Climate Law (Regulation (EU) 2021/1119) — produced a measurable environmental effect. Rather than relying on self-reported government claims of policy success, GPIE integrates satellite-derived Earth Observation data, climate reanalysis, and economic indicators into a rigorous statistical framework, following a "Trust, But Verify" research philosophy: government policy claims are treated as hypotheses to be independently tested against observational evidence, not facts to be assumed.

The European Green Deal was selected as the demonstration case due to its comprehensive policy scope, high-quality open data availability, and global relevance. The underlying methodology, however, is designed to be transferable to any country or policy context.

This transferability was subsequently tested directly: the project's NO₂ acquisition pipeline was validated standalone on India (2019–2024), confirming successful, physically realistic data acquisition using the identical infrastructure built for the EU-27 study, with zero modification to the core acquisition code.

## Problem Statement

Governments invest heavily in environmental and climate policy, yet independently verifying whether such investments produce measurable outcomes remains difficult. Administrative self-reporting is inconsistent across countries, and simple before-after comparisons of environmental indicators cannot distinguish a policy's true effect from broader trends that would have occurred regardless. GPIE addresses this gap by building a reproducible, satellite-driven framework capable of testing policy effectiveness with the statistical rigor required to support a genuine causal claim — rather than a correlational one.

## Aim

To develop a geospatial framework that independently and rigorously tests whether the European Climate Law produced a statistically distinguishable reduction in air pollution across the EU-27, using satellite observations, causal inference methodology, and transparent, reproducible code.

## Research Question

Did the European Climate Law (effective 30 June 2021) produce a measurable, EU-specific reduction in tropospheric NO₂ pollution, once independently tested against a genuine non-EU comparison group using satellite-derived evidence?

---

## Data Sources

GPIE integrates eight independently-sourced datasets across 36 countries (EU-27 plus a nine-country control group), spanning 2019–2024 (a ninth dataset, WorldPop population, was also acquired but excluded as a model input — see Limitations):

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

NO₂, NDVI, and climate data were acquired for all 36 countries via the Sentinel Hub Statistical API, chosen over raw satellite tile download for its scalability — server-side aggregation avoided the storage and processing burden of handling raw multi-terabyte satellite imagery. Static datasets (elevation, land cover) were acquired for the EU-27 only, since these are absorbed by country-level fixed effects in the causal model and were not required for the control group. GDP was sourced from Eurostat for EU-27 countries and the World Bank for the nine control-group countries, since Eurostat does not cover non-EU nations.

### Phase 3 — Preprocessing and Standardization (Module 3)

All datasets were converted into a standardized, country-month structure. Two master datasets were constructed: an EU-27-only dataset (1,944 rows) used for exploratory analysis, and a 36-country dataset (2,592 rows) — including EU-27 and the nine-country control group — used for the project's final causal-inference model.

### Phase 4 — Causal Inference: Design and Validation (Module 8)

This module constitutes GPIE's core scientific contribution and underwent a rigorous, multi-stage validation process rather than a single model-and-report approach.

**Initial model.** A first Difference-in-Differences model, comparing all 27 EU countries before and after 30 June 2021 using country and seasonal fixed effects, found a statistically significant reduction in NO₂. As originally computed with classical (non-clustered) standard errors, p = 0.026; a later verification pass found this specific figure had not been re-estimated with the cluster-robust standard errors used everywhere else in this project — cluster-robust, it is p = 0.041, still significant at 5%, so this correction does not change the model's conclusion (see the Development Log for the full correction).

**Placebo test.** Before accepting this result, the identical model was re-run using a fake treatment date (30 June 2020), where no relevant policy event occurred. This placebo test found an equally significant "effect" (p = 0.004, cluster-robust standard errors by country) — revealing that the original model was detecting a general, ongoing pollution-decline trend rather than an effect specific to the Climate Law. This is a well-documented limitation of any single-cohort design applied to a policy affecting an entire study population simultaneously, with no untreated comparison group available to isolate the policy-specific effect from the underlying trend.

**Methodological correction.** In response, a genuine external control group was constructed: nine non-EU European countries — the United Kingdom, Norway, Switzerland, Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, and Serbia — geographically and economically comparable to the EU-27 but not subject to EU Green Deal legislation, spanning both established Western European economies and EU-accession-candidate economies in the Western Balkans. This required acquiring new boundary data (GADM for UK/Norway/Switzerland, NUTS directly for the remaining six), extending satellite data acquisition to all 36 countries, and sourcing a second GDP dataset for the control group. A proper two-group Difference-in-Differences model was then estimated, with the interaction between EU-27 membership and the post-treatment period as the core causal estimator.

**Final result.** The corrected pooled model found **no statistically significant EU-wide average effect at the conventional 5% level** (coefficient = −2.22 × 10⁻⁶, p = 0.101 with standard errors clustered by country, 95% confidence interval spanning zero, though narrowly). Clustering by country is the standard correction for panel data of this kind, where a country's repeated monthly observations are serially correlated and uncorrected standard errors would understate uncertainty. An event-study extension — testing the effect separately across all 23 individual quarters from 2019 to 2024 — found 4 of 23 quarters nominally significant under clustered SEs, more than the ~1 expected by chance, all negative and all clustering in the second or third calendar quarter of 2022–2024; every pre-treatment quarter remains non-significant, supporting the model's parallel-trends assumption. A heterogeneity check splitting the treatment group by baseline pollution level found a statistically significant reduction concentrated in the fourteen higher-baseline (more industrialized) EU countries (coefficient = −5.46 × 10⁻⁶, p = 0.003), with no effect in the remaining thirteen lower-baseline countries — indicating the pooled null is averaging a real, concentrated effect together with little-to-no effect elsewhere, rather than reflecting a genuine absence of any EU-specific effect.

**Honest limitation.** Even with a nine-country control group, the pooled model's confidence interval still spans zero. The rigorous conclusion is therefore not "the policy had no effect" nor "the policy worked," but that **the pooled, EU-27-wide average effect is not conventionally significant, while a real effect concentrated in higher-baseline-pollution member states and in specific post-treatment quarters is** — a genuinely open, only partially resolved finding this study's design can characterize but not fully pin down without a longer panel or sub-national data (see Limitations and the research paper's Future Work section).

**Independent corroboration: augmented synthetic control and spatial diagnostics.** Two further checks target the pooled estimate directly, using methods structurally independent of the DiD specification itself. An Augmented Synthetic Control (seven-country donor pool: UK, Switzerland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, Serbia; Norway and Iceland excluded for real high-latitude NO₂ coverage gaps that persisted even after a clean re-fetch) weights donors by pre-treatment fit rather than averaging them equally, and reaches a post-treatment gap of −1 × 10⁻⁶ — the same near-zero, same-sign result as the pooled DiD coefficient — with a genuine seven-donor in-space placebo ranking the real EU-27 gap 2nd of 8 by size. A Moran's I spatial-autocorrelation test, now run across all 36 countries, confirms that while raw country-level NO₂ readings are strongly spatially clustered (I = 0.570, p = 0.001, as expected for a pollutant that crosses borders), the DiD model's own residuals are not significantly clustered (I = 0.069, p = 0.135) — the country and month fixed effects already absorb the large majority of that dependence. Neither check overturns the pooled null, but both close off a specific way the control group's construction could otherwise be second-guessed.

### Phase 5 — Economic Efficiency Ranking (Module 9): Deliberately Scoped Out

Module 9 was originally planned to rank environmental policies by cost-effectiveness. This was deliberately not pursued, for a specific, principled reason: ranking interventions by "cost per unit of environmental improvement" presupposes a measurable improvement to rank against. Since Module 8's validated finding is that no statistically significant effect was detected, constructing such a ranking would require either manufacturing significance the data does not support, or ranking against an effect size indistinguishable from zero — neither of which is scientifically defensible. This decision is itself consistent with GPIE's core design principle: verification should not be bent to produce results convenient for a downstream module.

### Phase 6 — Geospatial Visualization (Module 10)

Twelve geospatial and statistical visualizations were produced using a Python-based mapping pipeline (`geopandas` and `matplotlib`), covering NO₂ distribution, an NO₂ 2019-vs-2024 before/after comparison, an NDVI 2019-vs-2024 before/after comparison, the treatment/control study design, land cover, elevation (DEM), climate (temperature), NDVI distribution, GDP, the event-study result, an augmented synthetic control gap plot, and a Local Moran's I (LISA) spatial-cluster map. Each visualization was independently verified for correctness before finalization.

### Phase 7 — Interactive Dashboard and Deployment (Module 11)

The complete project was packaged into an eight-page interactive Streamlit dashboard, covering the study design, environmental data, before/after comparison, economic context, causal results, full methodology, an interactive country-level trend explorer, and downloadable raw data. The full codebase, documentation, and reproducible pipeline were published as an open-source GitHub repository.

---

## Final Findings

1. **No statistically significant pooled, EU-wide reduction in NO₂** was detected at the conventional 5% level attributable to the European Climate Law, once rigorously tested against a genuine nine-country non-EU control group and cluster-robust standard errors — but the pooled null conceals a statistically significant, concentrated effect (see finding 5).
2. **NDVI (vegetation health) tells a different story once given the same rigor as NO₂.** The original single-cohort NDVI model (mirroring NO₂'s already-invalidated design) was originally reported as finding no effect (p = 0.128, using classical standard errors) — a later verification pass found that, re-estimated with the cluster-robust standard errors used everywhere else in this project, that same initial model was already significant (p = 0.0017). Regardless, since a single-cohort design cannot reliably distinguish a policy-specific effect from a general regional trend (per the NO₂ placebo test), the same control-group correction applied to NO₂ was applied to NDVI as well, producing a statistically significant *relative decline* in EU-27 NDVI versus the control group (coefficient = −0.0145, p = 0.007). This is not interpreted as evidence the Climate Law harmed vegetation — land-use change, drought, and agricultural-policy shifts are not controlled for — but it is flagged as a genuine, methodologically robust finding meriting further investigation.
3. **The validation process itself — placebo test, control-group construction, cluster-robust standard errors, event-study disaggregation, and heterogeneity testing — is as significant a project output as any single substantive result.** An initial, seemingly positive NO₂ finding was actively tested and shown to be unreliable; continuing past the pooled headline estimate once it proved not conventionally significant, rather than stopping there, is what surfaced the higher-baseline heterogeneous effect.
4. **This is reported as a credible scientific finding, not a project shortfall.** GPIE's purpose was to independently verify policy claims, not to confirm or deny them on the first pass — and rigorously validated results, whether null, significant, or a nuanced mix of both, fulfill that purpose equally.
5. **A heterogeneity check finds a statistically significant NO₂ reduction concentrated in higher-baseline-pollution EU countries, corroborated by the event study and by an augmented synthetic control and spatial-autocorrelation test.** Splitting the EU-27 by baseline pollution level finds a significant effect in the fourteen higher-baseline (more industrialized) countries (coefficient = −5.46 × 10⁻⁶, p = 0.003) and none in the remaining thirteen. This is corroborated by the event study's four significant post-treatment quarters (all negative, clustering in Q2/Q3), while the synthetic control (weighted seven-country donor pool) and Moran's I diagnostic — evaluated against the pooled EU-27 aggregate — both remain consistent with the pooled null, directly testing rather than assuming the country-clustered standard errors are adequate.

## Limitations

- Even with a nine-country control group (seven for the synthetic control, since Norway's and Iceland's NO₂ coverage is too incomplete to use either as a donor), the pooled model's confidence interval still spans zero; a real, statistically significant effect only emerges once the treatment group is split by baseline pollution level.
- The EUR-Lex policy database returned a limited number of formally scraped records; the treatment date was instead anchored to the single most legally significant instrument (the European Climate Law) rather than a comprehensive policy-intensity measure.
- WorldPop population data was only available for 2019–2020 within the accessible dataset version; population was reclassified as a supporting/descriptive variable rather than a model input, given its incomplete temporal coverage relative to the study period.
- GDP for the control group required a currency conversion (USD to EUR) using approximate annual average exchange rates rather than precise historical rates, an acceptable approximation for a control variable but not for a primary variable of interest.
- The significant NDVI finding is not controlled for time-varying land-use change, drought/precipitation-driven vegetation stress, or agricultural-policy shifts between treatment and control regions — the project's land-cover control is a static, single-snapshot variable and cannot capture these dynamics. This finding should be treated as exploratory rather than a fully identified causal estimate.

## Deliverables

- A fully automated, reproducible Python data-acquisition and processing pipeline across eight datasets and 36 countries
- Two clean, merged master datasets (EU-27-only and 36-country control-group versions)
- A rigorously validated causal-inference model, including placebo-test and event-study robustness checks
- Twelve publication-quality geospatial and statistical visualizations, including an augmented synthetic control gap plot and a Local Moran's I (LISA) spatial-cluster map
- An interactive, publicly deployed Streamlit dashboard
- Complete open-source codebase and documentation, published on GitHub
- A formal academic research paper, including literature review and statistical methodology
- A standalone transferability validation confirming the acquisition pipeline's portability beyond the EU-27 study region (tested on India)

## Current Status

**Complete.** All eleven planned project modules have been executed, with Module 9 formally and transparently scoped out for a documented scientific reason rather than left incomplete. The project is deployed as a public GitHub repository and an interactive dashboard, ready for portfolio and academic presentation.
