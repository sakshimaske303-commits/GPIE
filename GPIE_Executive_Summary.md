# GPIE — Green Policy Intelligence Engine

*Independently Verifying Environmental Policy Claims Using Satellite Data*

**Executive Summary** · DOI: 10.5281/zenodo.21756661 · Sakshi D. Maske

---

## Project Overview

Creating GPIE was a response to the question, which is seldom addressed in the EU climate discussion: did the European Climate Law actually impact the pollution situation – not only through a government assessment of success, but through an objective physical verification? The project was very much a case of two origin stories: first a EUR-Lex scraping job to nail down the exact moment in time at which the law became "legal," and second, NO₂ readings from the Sentinel-5P satellite to determine if the NO₂ trend really did "bend" at that date. My first model said yes, simply, and I almost stopped there — but a placebo test on a fake treatment date came back equally strong, meaning I had actually found a trend of overall pollution decline across Europe unrelated to the Climate Law specifically, so that "positive" result had to be treated as a design failure rather than pushed forward as a finding. Correcting it meant building a real outside comparison group instead of accepting the false positive: I started with three non-EU countries close enough to Europe to be genuinely comparable — the UK, Norway, and Switzerland — then judged three too thin to trust the result against and expanded it to nine by adding Iceland and five Western Balkan EU-accession candidates. That expanded, nine-country control group is what the estimates above are ultimately built on. If I had to name the project's real headline, it isn't the null result or the significant subgroup finding on its own — it's that the validation process caught and fixed a wrong answer before that wrong answer became the reported one.

## Overview

In GPIE's research philosophy, claims made by the government are hypotheses, in the sense that in order to test this, they must be confronted with observational evidence rather than taken as fact, and the whole framework is based on the concept of “Trust but verify.” GPIE is a geospatial causal-inference tool designed to define its own metrics and measure the environmental impact of the European Green Deal and its flagship legislation – the European Climate Law Regulation (EU) 2021/1119 – in accordance with a robust statistical approach, instead of relying on self-reported government statements on policy success.

This method is designed to be applicable to any country or policy environment: the European Green Deal has been selected as the case study because of its broad policy scope, the wide availability of high-quality open data and its international nature.

## The Question

Governments report on their own climate results, and they often do not actually measure independent results from these policies, GPIE is an audit on top of this based on satellite data and not on the assumption that the policy was met. The specific question it answers: Does the European Union (EU-27) Climate Law (30 June 2021) have any measurable statistically significant impact on NO₂ air pollution beyond natural variations?

## The Method

Standard errors are clustered by country throughout a two-group Difference-in-Differences (DiD) design that compares EU-27 countries against a deliberately constructed 9-country non-EU control group — UK, Norway, Switzerland, Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, and Serbia — across 8 independently-sourced datasets (NO₂ via Sentinel-5P TROPOMI, NDVI via CGLS, climate via ERA5, GDP via Eurostat/World Bank, land cover, elevation, administrative boundaries, and EU policy records), spanning 36 countries and 2019–2024. Two independent checks, through structurally different methods, corroborate the pooled DiD result: an augmented synthetic control (weighted 7-country donor pool) and a Moran's I spatial-autocorrelation diagnostic.

## The Finding

This project's core finding is really about reporting a nuanced result honestly — a pooled null that is consistent with a real, concentrated effect — rather than the flawed "significant" result an earlier single-cohort design had produced. Once compared against the 9-country non-EU control group, no statistically distinguishable pooled, EU-wide reduction in NO₂ was detected at the conventional 5% level; but a heterogeneity check splitting the EU-27 by baseline pollution level finds a statistically significant reduction concentrated in the 14 higher-baseline, more industrialized member states (p=0.003), corroborated by a 23-quarter event-study finding four significant post-treatment quarters, all negative, clustering in Q2/Q3 of 2022–2024. An augmented synthetic control corroborates the pooled near-zero estimate through a methodologically distinct approach, and a spatial-autocorrelation test confirms the model's fixed effects absorb most of the spatial clustering present in raw pollution levels.

| Metric | NO2 (Primary, Pooled) | NO2 (Higher-Baseline Subgroup) | NDVI (Secondary) |
|---|---|---|---|
| DiD Coefficient | -2.22e-6 | -5.46e-6 | -0.0145 |
| P-value (cluster-robust) | 0.101 — not significant | 0.003 — significant | 0.007 — significant |
| 95% Confidence Interval | [-4.87e-6, +4.32e-7] | — | [-0.0250, -0.0039] |

The NDVI result is only a secondary finding and thus isn't conclusive evidence of changes in vegetation health caused by the Climate Law — because this analysis doesn't factor in changes of land use or drought-induced changes in vegetation stress.

## Validation & Robustness Checklist

- ✓ Cluster-robust standard errors, clustered by country (Bertrand, Duflo & Mullainathan, 2004)
- ✓ Deliberately constructed external control group - 9 countries (UK, Norway, Switzerland, Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, Serbia)
- ✓ Placebo test — caught and fixed a flawed initial single-cohort design (which had wrongly shown significance)
- ✓ 23-quarter event-study validation — supports the parallel-trends assumption (every pre-treatment quarter non-significant) and finds 4 significant, same-signed post-treatment quarters
- ✓ 5 additional robustness checks — GDP removed, log-transformed outcome, treatment-date shifted ±6/±12 months, pollution-level subgroup split (significant), and a formal minimum-detectable-effect calculation
- ✓ Augmented synthetic control (7-country donor pool, weighted) — reaches the same near-zero, same-sign pooled estimate through a method that is methodologically distinct from the DiD specification
- ✓ Moran's I spatial-autocorrelation test — raw NO2 is spatially clustered (I=0.570, p=0.001) as expected, but DiD residuals are not significantly clustered (I=0.069, p=0.135)
- ✓ Honest, nuanced result reported — pooled null and concentrated significant subgroup effect both disclosed, neither smoothed over

## Honest Limitation

The honest conclusion here is not "the policy had no effect" nor "the policy worked" — it's that the pooled EU-wide average across all 27 member states is not conventionally significant, while a real effect concentrated in higher-baseline member states and specific post-treatment quarters is, a genuinely open finding this design can characterize but not fully resolve without a longer panel or sub-national data. Even with a 9-country control group (7 for the synthetic control specification, since Norway's and Iceland's NO2 coverage remain too incomplete to use as donors even after a clean re-fetch), the pooled model's confidence interval still spans zero; at 80% statistical power, this design can reliably detect a pooled effect of roughly 12.7% of baseline EU NO₂ or larger.

## Global Transferability

This framework's architecture is portable beyond a single region, not a one-country tool — confirmed by separately testing the NO₂ acquisition pipeline, using the same Sentinel Hub infrastructure and evalscript logic with no modification to the core acquisition logic, on India (2019–2024), which returned physically realistic values consistent with the EU-27 dataset's observed range.

---

**GitHub:** github.com/sakshimaske303-commits/GPIE | **Live Dashboard:** f5cf6fijj9gm564r6aapt6.streamlit.app | **Zenodo DOI:** 10.5281/zenodo.21756661

Sakshi D. Maske — Independent Geospatial Researcher
