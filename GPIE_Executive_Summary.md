# GPIE — Green Policy Intelligence Engine

*What Does a Country-Level Difference-in-Differences on Satellite NO₂ Identify?*

**Executive Summary** · Sakshi D. Maske

---

## The Problem

Satellite NO₂ makes it easy to compare pollution in countries that adopted a policy with countries that did not, and a difference-in-differences (DiD) on country averages is a common way to do it. But the change in an NO₂ column depends on its level: clean areas have little to lose. If the treated countries start out more polluted than the comparison countries, a DiD in levels can record that difference as a policy effect.

## The Question

When treated and comparison countries differ in baseline pollution, what does a country-level DiD on satellite NO₂ identify?

- **RQ1:** how much of the country-level estimate is explained by the difference in pre-treatment NO₂ between the groups?
- **RQ2:** when EU and comparison areas are compared at the same starting level, where did NO₂ fall, and does the pattern follow the EU border?

The test case is the European Climate Law (Regulation (EU) 2021/1119; adopted 30 June 2021, in force 29 July 2021). It applies to all 27 member states from one date and not to their neighbours, but it sets climate targets and has no direct mechanism on NO₂. It is used deliberately as a negative-control case: an estimate that looks like an effect needs another explanation.

## Data and Method

- **Outcome:** Sentinel-5P TROPOMI tropospheric NO₂, one 0.1° raster per day for 2,192 days (2019–2024, quality value ≥ 0.75), pooled into monthly means for 36 countries and for every pixel.
- **Groups:** the EU-27 against nine non-EU countries (United Kingdom, Norway, Switzerland, Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, Serbia); July 2021 is the first post-treatment month.
- **Country level:** DiD with country and year-month fixed effects, an EU-specific seasonal cycle, ERA5 weather and GDP controls, and standard errors clustered by country, re-estimated under about 20 alternative specifications.
- **Composition tests (RQ1):** the interaction of each country's pre-treatment level with the post period, 999 random assignments of the treatment label, and a pixel-level DiD that compares EU and comparison pixels within the same pre-treatment class.
- **Geography (RQ2):** change in polluted pixels country by country, including western Turkey and Ukraine outside the sample.

## The Findings

| Analysis | Result |
|---|---|
| Country-level DiD | NO₂ fell 1.34 × 10⁻⁶ mol/m² more in the EU-27 (4.3% of its pre-treatment level; p = 0.022) |
| Fragility | Not significant without November–February (p = 0.11), with area weights (p = 0.11), with log GDP (p = 0.21), with real GDP per capita (p = 0.072), or under randomization inference on the coefficient (p = 0.17). The estimate appears only from July 2023 |
| Random assignment of the label | Estimates follow the pre-treatment gap between groups (r = −0.81), and the EU-27 estimate is close to what its gap predicts |
| Pixels matched on pre-treatment level | −0.21 × 10⁻⁶ (95% CI −0.67 to +0.24). Matching removes about 84% of the country-level estimate |
| Positive control | The matched model finds a known 2.5% reduction added to EU-27 NO₂ from July 2021 (−0.80 × 10⁻⁶, p = 0.002). With 80% power it detects a uniform reduction of about 3%, so its near-zero estimate is not due to low power |
| Ground stations | The satellite agrees with 1,543 EEA background stations (monthly r = 0.68). The stations give a similar relative EU-27 decline that is not significant (−4.0%, p = 0.12), and they do not show the December 2023 drop that the satellite records in Denmark and Sweden, so that drop is a retrieval artefact |
| Where NO₂ fell | Polluted pixels lost about 15–25% in north-western Europe, including the non-EU UK and Switzerland, and 0–6% in south-eastern Europe, including EU members and Serbia. Western Turkey did not decline |

## What It Means

Most of the country-level estimate reflects that the EU-27 was more polluted to begin with. The decline in NO₂ was regional, strongest in the polluted north-west on both sides of the EU border, and the data do not require an effect at the border, although they cannot rule one out. For satellite-based policy evaluation, the lesson is to compare units at the same starting level, to report results with and without the winter months, and to report weighting and functional-form choices, since here each of them alone moves the estimate across the 5% threshold.

## Limitations

The highly polluted comparison pixels are mostly in the United Kingdom, which shares EU-derived vehicle standards, so the comparison separates EU membership from pollution level but not EU-origin regulation from its absence. The time window for the regional description was chosen after seeing the data. Part of the regional contrast comes from winter retrievals, when valid observations are fewest. The ground-station check lacks the United Kingdom, weather controls are country means, and inference rests on only nine comparison countries.

## Correction History

Earlier versions reported a pooled null (p = 0.101), based on NO₂ values that turned out to be end-of-month snapshots rather than monthly means. The acquisition was rebuilt from daily rasters and every number was re-estimated. The Development Log records every correction.

---

**GitHub:** github.com/sakshimaske303-commits/GPIE | **Live Dashboard:** f5cf6fijj9gm564r6aapt6.streamlit.app

Sakshi D. Maske — Independent Geospatial Researcher
