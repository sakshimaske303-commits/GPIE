# GPIE — Green Policy Intelligence Engine

*Independently Verifying Environmental Policy Claims Using Satellite Data*

**Executive Summary** · DOI: 10.5281/zenodo.21756661 · Sakshi D. Maske

---

## Project Overview

GPIE started from a question that is seldom asked in the EU climate discussion: did the European Climate Law change pollution in a way that can be checked physically, not only through governments' own assessments? The project had two starting points: a EUR-Lex scraper to pin down the legal dates of the law, and Sentinel-5P NO₂ readings to see whether the NO₂ trend bent at that point. My first model said yes, and I almost stopped there — but a placebo test on a fake treatment date came back just as strong, which meant the model was picking up Europe's general NO₂ decline rather than anything specific to the Climate Law. So I built an outside comparison group: first three non-EU countries (UK, Norway, Switzerland), then nine, adding Iceland and five Western Balkan EU-accession candidates. The results below are built on that nine-country group. Later, a second correction changed the picture again: the satellite values themselves had been end-of-month snapshots rather than monthly means. The project's real headline is the validation process — three times it caught a wrong answer before that answer stayed the reported one.

## Overview

GPIE treats government claims as hypotheses to be tested against observational evidence ("Trust, but verify"). It is a geospatial causal-inference workflow that measures the environmental effect of the European Green Deal's flagship legislation — the European Climate Law, Regulation (EU) 2021/1119 — with a statistical design rather than relying on self-reported policy success. The European Green Deal was chosen as the case study because of its scope, the availability of open data and its international relevance.

## The Question

Did the European Climate Law (adopted 30 June 2021, in force 29 July 2021) produce a statistically distinguishable reduction in NO₂ pollution across the EU-27, beyond the change seen in comparable non-EU countries?

## The Method

A two-group Difference-in-Differences (DiD) design compares the EU-27 with a 9-country non-EU comparison group — UK, Norway, Switzerland, Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia and Serbia — on a monthly country panel, 2019–2024, with July 2021 as the first post-treatment month. NO₂ comes from Sentinel-5P TROPOMI as true monthly means (one raster per day, QA ≥ 0.75, pooled per country); controls are ERA5 temperature and precipitation and GDP (Eurostat/World Bank), with country and calendar-month fixed effects and standard errors clustered by country. NDVI (CGLS) is a secondary outcome. Additional checks: placebo date, 23-quarter event study, GDP exclusion, log outcome, treatment-date shifts, an EU-specific trend, a post-hoc baseline split, a synthetic control, Moran's I, and a set of identification checks (year-month fixed effects, EU-specific seasonality, wind/boundary-layer and COVID-19 controls, wild cluster bootstrap and randomization inference).

## The Finding

NO₂ fell more in the EU-27 than in the comparison group, by about 5% of the EU's pre-treatment level, and the decline is concentrated in the 14 more polluted member states. But the design cannot attribute this to the Climate Law: nothing changes in the first two years after the law and the whole decline appears from July 2023 (−2.18e-6, p = 0.008), every alternative cutoff date is just as significant, and a steady EU-specific trend absorbs the treatment-date effect (p = 0.243). The estimate itself is sturdy: it holds with year-month fixed effects and EU-specific seasonality (−1.34e-6, p = 0.016; wild cluster bootstrap p = 0.018), with wind, boundary-layer and COVID-19 stringency controls, and when the COVID-19 or energy-crisis months are dropped — though not under randomization inference (p = 0.16) or without the GDP control (p = 0.074). A pixel-level check then shows where the estimate comes from: the decline grows with how polluted each 0.1° pixel was, and comparing pixels with the same starting level cuts the estimate to −0.21e-6 (p = 0.341). The pattern is regional, not institutional: polluted pixels lost 15–25% in north-western Europe, including the non-EU United Kingdom and Switzerland, and 0–6% in south-eastern Europe, including EU members Romania, Bulgaria, Croatia and Greece as well as Serbia and Bosnia and Herzegovina. Within either region the EU border makes no difference. The country-level estimate is also fragile: it weakens without the winter months (−0.81e-6, p = 0.11), with countries weighted by area (p = 0.11) and with log GDP (p = 0.21). The evidence fits a decline in the polluted areas of north-western Europe, not an effect of EU membership or of the law.

| Metric | NO2 (Primary, Pooled) | NO2 (Higher-Baseline, post-hoc) | NDVI (Secondary) |
|---|---|---|---|
| DiD Coefficient | -1.52e-6 (log: -4.2%) | -2.85e-6 (log: -6.4%) | -0.0194 |
| P-value (cluster-robust) | 0.013 (log: 0.034) | 0.002 (log: 0.006) | 0.005 |
| 95% Confidence Interval | [-2.73e-6, -3.16e-7] | — | [-0.0330, -0.0058] |
| With EU-specific trend | +8.7e-7, p = 0.243 | — | — |

The NDVI result is an exploratory association, not evidence that the Climate Law changed vegetation health: land-use change, drought stress and agricultural policy are not controlled for.

## Validation & Robustness Checklist

- ✓ Cluster-robust standard errors, clustered by country (Bertrand, Duflo & Mullainathan, 2004)
- ✓ External comparison group — 9 non-EU countries (some share EU climate instruments: EU ETS for Norway/Iceland, linked Swiss ETS, Western Balkans Green Agenda)
- ✓ Placebo test — exposed the flawed initial single-cohort design
- ✓ 23-quarter event study — 7 of 9 pre-treatment quarters significant with a common seasonal cycle; with an EU-specific seasonal cycle and 12-month blocks the pre-treatment blocks are not significant (joint p = 0.292)
- ✓ Year-month fixed effects + EU-specific seasonality — −1.34e-6 (p = 0.016); unchanged by wind speed, boundary-layer height and COVID-19 stringency controls
- ✓ 12-month blocks — no effect Jul 2021–Jun 2023 (p = 0.98, 0.44); decline only from Jul 2023 (−2.18e-6, p = 0.008)
- ✓ Few-cluster inference — wild cluster bootstrap p = 0.018; randomization inference p = 0.16; stable when any one comparison country is dropped
- ✓ Pixel-level check (0.1° grid, 51,072 pixels) — decline grows with pre-treatment level; matched on that level the estimate is −0.21e-6 (p = 0.341)
- ✓ Regional contrasts — EU border makes no difference inside the north-west (p = 0.44) or the south-east (p = 0.48); north-west vs south-east EU members differ (−1.43e-6, p = 0.016)
- ✓ Stress tests — without Nov–Feb −0.81e-6 (p = 0.11); area-weighted −0.96e-6 (p = 0.11); log GDP −0.94e-6 (p = 0.21); randomization inference on the t-statistic p = 0.046
- ✓ COVID-19 window and energy-crisis months excluded — estimate remains (−2.25e-6, p = 0.011; −2.08e-6, p = 0.005)
- ✓ TROPOMI processor versions checked — reprocessed v2.4.0 to July 2022, operational v2.4–2.7 after; no version change at the treatment date
- ✓ Treatment date ±6/±12 months — every date significant (p = 0.004 to 0.028): no break specific to the law's date
- ✓ EU-specific trend — treatment term no longer significant (p = 0.243); trend −7.9e-7 per year (p = 0.016)
- ✓ GDP excluded (−1.49e-6, p = 0.053); log outcome (−4.2%, p = 0.034); baseline split (decline only in higher-baseline group)
- ✓ Synthetic control (9 donors, intercept-adjusted) — gap −8.1e-7, rank 5 of 10 among placebo countries
- ✓ Moran's I — raw NO₂ clustered (I = 0.578, p = 0.001); DiD residuals clustered in 59 of 72 months (median I = 0.347), so p-values are likely too small
- ✓ All of the above reported, including the results that limit the headline

## Honest Limitation

The headline coefficient is statistically significant, but that is not the same as a Climate Law effect: the checks above show the timing does not line up with the law. This version also corrects an earlier data problem. NO₂ "monthly" values had been single end-of-month snapshots (Sentinel Hub clips Sentinel-5P requests to the last 24 hours of the interval); they are now true monthly means, and every number changed — the earlier pooled null (p = 0.101) is superseded. Remaining limits: a country-level estimate that largely reflects where polluted areas are and that depends on winter retrievals, country weighting and the form of the GDP control, significance that depends on the GDP control and is not confirmed by randomization inference, nine comparison clusters, spatially correlated residuals, a comparison group that differs structurally from the EU-27, and Malta represented by only three 0.1° pixels.

## Global Transferability

The NO₂ acquisition step was run on India's national boundary (2019–2024) with the same request builder, evalscript and QA threshold as the EU study. The test records how many months returned data and how the values compare with the EU-27 distribution. Result: all 72 months returned data; India's monthly national mean ranged from 2.27 × 10⁻⁵ to 4.16 × 10⁻⁵ mol/m² (median 3.32 × 10⁻⁵), with no negative months, and all 72 values fall inside the 5th–95th percentile range of EU-27 country-months (1.34 × 10⁻⁵ to 6.34 × 10⁻⁵ mol/m²). It shows the data pipeline runs outside Europe; transferring the causal design would need its own comparison group.

---

**GitHub:** github.com/sakshimaske303-commits/GPIE | **Live Dashboard:** f5cf6fijj9gm564r6aapt6.streamlit.app | **Zenodo DOI:** 10.5281/zenodo.21756661

Sakshi D. Maske — Independent Geospatial Researcher
