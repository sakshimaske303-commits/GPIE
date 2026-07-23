# Independent Verification of the European Climate Law's Effect on Nitrogen Dioxide Pollution: A Satellite-Derived, Difference-in-Differences Analysis

# Sakshi D. Maske
Independent Geospatial Researcher

## Abstract

Governments frequently claim environmental policy success through self-reported administrative data, yet independent verification using observational evidence remains uncommon in EU climate policy assessment. This study tests whether the European Climate Law (Regulation (EU) 2021/1119, effective 30 June 2021) produced a statistically distinguishable reduction in tropospheric nitrogen dioxide (NO₂) pollution across EU-27 countries, using Sentinel-5P TROPOMI satellite observations (2019–2024) and a Difference-in-Differences (DiD) causal-inference framework. An initial single-cohort model found a statistically significant reduction (p = 0.026); however, a placebo test using a counterfactual treatment date revealed this result reflected a general, ongoing European pollution-decline trend rather than a policy-specific effect. Following this finding, a genuine external control group — the United Kingdom, Norway, and Switzerland — was constructed, enabling a properly identified two-group DiD model. The corrected model found no statistically significant EU-specific effect (coefficient = −1.40 × 10⁻⁶, p = 0.632), independently confirmed via a 23-quarter event-study analysis showing no significant deviation in any individual period. These findings suggest that observed EU-wide NO₂ declines over the study period reflect a broader European trend rather than a measurable, policy-specific effect distinguishable at current sample sizes. The study's validation methodology — particularly the use of a placebo test to detect a flawed initial specification — is presented as a methodological contribution as significant as the substantive finding itself.

**Keywords**: Difference-in-Differences, satellite remote sensing, air pollution, European Green Deal, causal inference, policy evaluation

## 1. Introduction

The European Green Deal represents one of the most ambitious environmental policy programs globally, with the European Climate Law establishing a legally binding target of climate neutrality by 2050. Yet the question of whether such legislation produces measurable, attributable environmental improvement — as opposed to reflecting or coinciding with pre-existing trends — is rarely tested with the rigor that causal-inference methodology permits. Existing air quality assessments in Europe often rely on administrative self-reporting or simple before-after comparisons, both of which are vulnerable to confounding by broader technological, economic, and behavioral trends that would have occurred independent of any specific legislative act.

This study addresses that gap directly: it tests whether the European Climate Law produced a statistically distinguishable reduction in NO₂ pollution — a well-established indicator of combustion-related emissions from transport and industry — using independently observed satellite data rather than administrative claims. This "trust, but verify" approach treats policy effectiveness as a hypothesis to be tested against evidence, not a fact to be assumed.

## 2. Literature Review

### 2.1 Satellite-Based Monitoring of NO₂ and Policy Impact

The Sentinel-5P TROPOMI instrument, operated by the European Space Agency since 2017, has become a standard tool for independently observing tropospheric NO₂ concentrations at fine spatial and temporal resolution. A substantial body of research has used TROPOMI data to assess the atmospheric impact of discrete policy events, most extensively during the COVID-19 pandemic. Multiple studies documented double-digit percentage reductions in NO₂ during lockdown periods across European and Asian cities, comparing satellite-observed concentrations against pre-lockdown baselines. Some of this literature has specifically cautioned that simple before-after or year-over-year satellite comparisons risk conflating policy effects with meteorological variability, given the substantial interannual variation in weather conditions relative to the still-limited historical record of the TROPOMI instrument. This concern directly informed the present study's decision to include temperature and precipitation as explicit control variables rather than relying on a raw pollution-level comparison.

Separately, TROPOMI-based work has extended beyond acute lockdown events to structural urban policy: a recent causal-inference evaluation of London's Ultra Low Emission Zone found statistically significant reductions in NO₂ and NOₓ following the policy's initial implementation, though not following a subsequent expansion phase, illustrating that satellite-derived causal evaluation can detect genuine, policy-specific effects when methodologically well-identified — reinforcing that a null result under similar methodology is a meaningful finding rather than evidence of the method's insensitivity.

### 2.2 Difference-in-Differences Methodology and Its Limitations

Difference-in-Differences remains among the most widely used quasi-experimental designs in policy evaluation research, valued for isolating a treatment's effect by comparing outcome changes between a treated and untreated group rather than relying on a single group's before-after comparison alone. Recent methodological literature has emphasized that DiD designs face specific challenges when treatment is not clearly randomized or when the design's core parallel-trends assumption cannot be adequately verified, particularly in settings involving simultaneous, universal policy rollout.

The parallel trends assumption — that treatment and comparison groups would have followed similar trajectories in the absence of intervention — is foundational to DiD's causal validity, yet is frequently difficult to establish empirically, especially over short panels. A widely cited methodological guide recommends placebo regressions, applying the DiD framework to pre-treatment data specifically to confirm that no spurious "treatment effect" is detected before treatment has actually occurred — a diagnostic this study applies directly, with results that proved decisive in revising the analytical approach.

Event-study extensions, which disaggregate an average treatment effect into period-specific estimates, are similarly established practice for testing both pre-trend validity and effect-timing dynamics. Research on pre-treatment significance testing frames event-study coefficients on pre-intervention periods as a direct placebo mechanism, artificially assigning treatment status to periods before the actual intervention to test for spurious differences — the same logic underlying this study's 23-quarter event-study robustness check.

### 2.3 The Single-Cohort Identification Problem

A methodological challenge specific to EU-wide legislation is that policies frequently apply to all member states simultaneously, leaving no naturally occurring untreated EU comparison group. This is a widely recognized limitation of DiD applications to universal policy rollouts, distinct from settings (such as sub-national or staggered implementation) where genuine within-study controls exist. The present study's initial model encountered this limitation directly, motivating the subsequent introduction of a non-EU comparison group — a design choice consistent with established practice of seeking geographically and structurally comparable jurisdictions outside a policy's legal jurisdiction when no internal control exists.

## 3. Data and Methodology

### 3.1 Study Design

This study evaluates the causal effect of the European Climate Law (effective 30 June 2021) on tropospheric NO₂ concentration using a panel Difference-in-Differences design across 30 European countries: the EU-27 (treatment group) and three non-EU comparator countries — the United Kingdom, Norway, and Switzerland (control group) — selected for geographic proximity, economic development comparability, and explicit non-applicability of EU Green Deal legislation.

**Figure 1. Difference-in-Differences study design showing the treatment group (EU-27) and the non-EU control group (United Kingdom, Norway, and Switzerland).**

<p align="center">
  <img src="outputs/plots/control_group_design_map.png" width="700">
</p>

### 3.2 Data Sources

| Variable | Source | Resolution |
|---|---|---|
| NO₂ (outcome) | Sentinel-5P TROPOMI, via Sentinel Hub Statistical API | Monthly, country-level |
| NDVI (secondary outcome) | Copernicus Global Land Service | Monthly, country-level |
| Temperature, precipitation (controls) | ERA5 Reanalysis, Copernicus Climate Data Store | Monthly, country-level |
| GDP (control) | Eurostat (EU-27); World Bank (control group) | Annual, country-level |
| Administrative boundaries | Eurostat GISCO (NUTS); GADM (control group) | — |

The panel spans January 2019 to December 2024 (72 months), providing 30 months of pre-treatment and 42 months of post-treatment observation.

### 3.3 Model Specification

The final model estimates:

$$NO2_{it} = \beta_0 + \beta_1 (Treatment_i \times Post_t) + \beta_2 Post_t + \gamma X_{it} + \alpha_i + \delta_m + \varepsilon_{it}$$

where $Treatment_i$ indicates EU-27 membership, $Post_t$ indicates observations after 30 June 2021, $X_{it}$ is a vector of time-varying controls (temperature, precipitation, GDP), $\alpha_i$ are country fixed effects, and $\delta_m$ are calendar-month fixed effects controlling for seasonality. The coefficient of interest, $\beta_1$, captures the EU-specific effect of the Climate Law, net of any trend common to both treatment and control groups.

### 3.4 Robustness Checks

Two robustness procedures were applied prior to accepting any result: a **placebo test**, re-estimating the model with an artificial treatment date (30 June 2020) at which no comparable policy event occurred, and an **event-study specification**, replacing the single post-treatment indicator with 23 quarter-specific interaction terms (2019Q1–2024Q4, relative to a 2021Q2 reference period) to test both pre-treatment parallel trends and potential delayed treatment effects.

## 4. Results

### 4.1 Initial Single-Cohort Model

A first model, comparing all 27 EU countries before and after treatment without an external control group, found a statistically significant NO₂ reduction (coefficient = −2.29 × 10⁻⁶, p = 0.026, 95% CI [−4.30 × 10⁻⁶, −2.69 × 10⁻⁷]).

### 4.2 Placebo Test

Re-estimating the identical model with the treatment date shifted to 30 June 2020 produced a coefficient of −3.29 × 10⁻⁶ with p = 0.002 — a result more statistically significant than the genuine treatment date. This outcome is inconsistent with a correctly identified policy effect and indicates the original model was capturing a general, ongoing pollution-decline trend rather than an effect specific to the Climate Law. Adding an explicit linear time trend to the original model confirmed this: the coefficient at the true treatment date became statistically indistinguishable from zero (p = 0.408) once the underlying trend was controlled for directly.

### 4.3 Corrected Two-Group Model

Following construction of the non-EU control group, the corrected DiD model produced:

| Statistic | Value |
|---|---|
| DiD coefficient | −1.40 × 10⁻⁶ |
| P-value | 0.632 |
| 95% Confidence Interval | [−7.12 × 10⁻⁶, +4.32 × 10⁻⁶] |
| R² | 0.386 |
| N | 1,930 |

**Figure 2.** Average NO₂ concentrations before (2019–2020) and after (2021–2024) the European Climate Law for the EU-27 treatment group and the non-EU control group. Both groups exhibit a similar decline, visually supporting the Difference-in-Differences estimate that no statistically distinguishable EU-specific treatment effect was detected.

<p align="center">
  <img src="outputs/plots/eu_vs_control_bar_chart.png" width="700">
</p>

The interaction term is not statistically significant, and its confidence interval spans zero.

### 4.4 Event-Study Validation

All 23 quarterly interaction coefficients were non-significant (p-values ranging from approximately 0.18 to 0.94), with no discernible pattern before or after the treatment quarter. Pre-treatment quarters showed no significant divergence between groups, supporting the parallel-trends assumption; post-treatment quarters showed no delayed effect emerging at any point through the end of 2024.

**Figure 3.** Event-study estimates showing quarter-specific Difference-in-Differences coefficients relative to the 2021Q2 reference period. Error bars represent 95% confidence intervals. No quarter exhibits a statistically significant deviation from zero before or after the European Climate Law.

<p align="center">
  <img src="outputs/plots/event_study_plot.png" width="700">
</p>

### 4.5 Secondary Outcome (NDVI)

A parallel model using NDVI (vegetation health) as the outcome likewise found no significant effect (coefficient = −0.0059, p = 0.128), consistent with the expectation that vegetation-health outcomes respond to land-use policy on longer timescales than atmospheric pollutants respond to emissions policy.

**Figure 4.** Average NDVI before (2019–2020) and after (2021–2024) across the EU-27 study area. Visual inspection suggests no substantial change in vegetation health over the study period, consistent with the non-significant Difference-in-Differences estimate.

<p align="center">
  <img src="outputs/plots/ndvi_before_after_map.png" width="700">
</p>

### 4.6 Transferability Validation

To provide direct evidence for this framework's applicability beyond the EU-27 study region — rather than presenting transferability as an unverified design claim — the NO₂ acquisition pipeline was independently tested on India (2019–2024), using identical Sentinel Hub Statistical API infrastructure with no modification to the core acquisition logic. All six years were retrieved successfully, returning physically realistic NO₂ concentrations consistent with the range observed across the EU-27 dataset. This is presented as a standalone architectural validation, not a comparative causal analysis; establishing India as a genuine study case would require the same rigor (control-group construction, placebo testing) applied to the EU-27 analysis in this paper.

**Figure 5.** Transferability validation using India as an independent test case. The identical Sentinel Hub acquisition pipeline successfully retrieved physically realistic NO₂ observations for 2019–2024 without modification, demonstrating that the framework is geographically transferable beyond the original EU-27 study area.

<p align="center">
  <img src="outputs/plots/india_transferability_trend.png" width="700">
</p>

## 5. Discussion

**Figure 6.** Average tropospheric NO₂ concentrations across the EU-27 in 2019 (pre-treatment) and 2024 (post-treatment). Although a visual reduction is evident, visual change alone cannot establish causality. The Difference-in-Differences analysis demonstrates that a similar decline occurred in the non-EU control group, indicating the observed reduction reflects a broader European trend rather than a statistically distinguishable effect of the European Climate Law.

<p align="center">
  <img src="outputs/plots/no2_before_after_map.png" width="700">
</p>

The corrected model's finding — no statistically distinguishable EU-specific NO₂ reduction attributable to the Climate Law — should be interpreted against the demonstrated capacity of this same broad methodological family to detect genuine policy effects: comparable satellite-based DiD analyses of sub-national policy interventions, such as London's low-emission zone, have found clear, significant effects. This makes it more plausible that the present null result reflects a genuine absence of a detectable EU-specific effect, rather than a general insensitivity of satellite-based DiD methodology to real policy impacts.

The result is also consistent with the possibility that observed European NO₂ decline over the study period is substantially driven by factors common to both EU and non-EU countries alike — vehicle fleet modernization, broader decarbonization of electricity generation, and pre-existing regulatory momentum predating the Climate Law specifically — none of which would be captured as an EU-specific effect in this design.

## 6. Limitations

Several limitations should be considered when interpreting these findings. First, the control group comprises only three countries, a comparatively small comparison group for a panel model with extensive fixed-effects structure; the resulting confidence interval is wide rather than tightly bounded around zero, meaning the null result is consistent with either a genuinely negligible effect or insufficient statistical power to detect a real but modest one. Second, the treatment date was anchored to a single, most legally significant instrument (the European Climate Law) rather than a comprehensive measure of cumulative Green Deal policy intensity, since available policy-database records did not support a more granular, country-differentiated treatment measure. Third, currency conversion for the control group's GDP data relied on approximate annual exchange rates rather than precise historical rates, an acceptable approximation for a control variable but not for a variable of primary interest.

## 7. Conclusion

This study finds no statistically distinguishable, EU-specific reduction in NO₂ pollution attributable to the European Climate Law, once rigorously tested against a genuine non-EU control group and validated through placebo testing and event-study disaggregation. This null result followed directly from a validation process that identified and corrected a flawed initial specification — itself demonstrating the practical necessity of placebo testing in policy evaluation research applying single-cohort designs to universally applied legislation. The framework developed here is directly transferable to future evaluations of EU environmental policy, and to other jurisdictions facing the same structural identification challenge of legislation without a naturally occurring internal comparison group — a claim supported empirically in this study by a successful standalone acquisition test on India (Section 4.6), rather than asserted without evidence.

## References

Bekes, G., & Kezdi, G. (2021). Impact evaluation using Difference-in-Differences. *RAUSP Management Journal*, 54(4), 519–532.

Bikbov, A. et al. (2024). Estimating lockdown-induced European NO2 changes using satellite and surface observations and air quality models. *Atmospheric Chemistry and Physics*.

Callaway, B., Goodman-Bacon, A., & Sant'Anna, P. (2024). Difference-in-Differences with a continuous treatment. *NBER Working Paper*.

Nature Publishing Group. (2025). Further improvement in London's air quality demands more than the Ultra Low Emission Zone policy. *npj Clean Air*.

Riveros-Gavilanes, J. (2023). Testing Parallel Trends in Differences-in-Differences and Event Study Designs: A Research Approach Based on Pre-Treatment Period Significance.

Roth, J., Sant'Anna, P., Bilinski, A., & Poe, J. (2023). What's Trending in Difference-in-Differences? A Synthesis of the Recent Econometrics Literature. *Journal of Econometrics*.

Scientific Reports. (2024). Unveiling urban air quality dynamics during COVID-19: a Sentinel-5P TROPOMI hotspot analysis.

Wang, P. et al. (2020). Nitrogen Dioxide (NO2) Pollution Monitoring with Sentinel-5P Satellite Imagery over Europe during the Coronavirus Pandemic Outbreak. *Remote Sensing*, 12(21), 3575.

Zeldow, B., & Hatfield, L. (2024). Advances in Difference-in-Differences Methods for Policy Evaluation Research. *PMC*.

-----------------------------------------------------------------------------------------------------

**Full dataset, code, and reproducible pipeline**: [github.com/sakshimaske303-commits/GPIE](https://github.com/sakshimaske303-commits/GPIE)
**Live interactive dashboard**: [f5cf6fijj9gm564r6aapt6.streamlit.app](https://f5cf6fijj9gm564r6aapt6.streamlit.app/)
