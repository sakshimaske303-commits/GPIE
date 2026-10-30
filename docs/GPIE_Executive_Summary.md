# GPIE — Green Policy Intelligence Engine

*What Does a Country-Level Difference-in-Differences on Satellite NO₂ Identify?*

**Executive Summary** · Sakshi D. Maske

---

## The Problem

Satellite NO₂ makes it easy to compare pollution in countries that adopted a policy with countries that did not. A common way to do this is a difference-in-differences (DiD) on country averages. But how much NO₂ can fall depends on how much there was to begin with, and clean areas have little to lose. If the treated countries start out more polluted, a DiD can mistake that difference for a policy effect.

## The Question

When treated and comparison countries start from different pollution levels, what does a country-level DiD on satellite NO₂ actually measure?

- **RQ1:** How much of the country-level estimate comes from the difference in starting NO₂ between the two groups?
- **RQ2:** When EU and comparison areas start at the same level, where did NO₂ fall, and does the pattern follow the EU border?

The test case is the European Climate Law (Regulation (EU) 2021/1119), adopted on 30 June 2021 and in force from 29 July 2021. It applies to all 27 member states from one date and not to their neighbours. It sets climate targets but has no direct mechanism on NO₂, so any estimate that looks like an effect must have another explanation.

## Data and Method

- **Outcome:** Sentinel-5P TROPOMI tropospheric NO₂. One 0.1° map per day for 2,192 days (2019–2024, quality value ≥ 0.75), averaged by month for 36 countries and for every pixel.
- **Groups:** The EU-27 against nine non-EU countries: the United Kingdom, Norway, Switzerland, Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia and Serbia. July 2021 is the first month after the law.
- **Country level:** DiD with country and year-month fixed effects, an EU-specific seasonal cycle, ERA5 weather and GDP controls, and standard errors clustered by country. The model is re-run under about 20 other specifications.
- **Starting-level tests (RQ1):** How each country's starting level interacts with the post period, 999 random reassignments of the EU label, and a pixel-level DiD that compares EU and non-EU pixels with the same starting level.
- **Geography (RQ2):** The change in polluted pixels country by country, including western Turkey and Ukraine outside the sample.

## The Findings

| Analysis | Result |
|---|---|
| Country-level DiD | NO₂ fell 1.34 × 10⁻⁶ mol/m² more in the EU-27, 4.3% of its starting level (p = 0.022) |
| How stable it is | Not significant without November–February (p = 0.11), with area weights (p = 0.11), with log GDP (p = 0.21), with real GDP per capita (p = 0.072), or under randomization inference (p = 0.17). The difference appears only from July 2023 |
| Random EU labels | Estimates follow how much more polluted the labelled group was at the start (r = −0.81). The real EU-27 estimate is close to what its starting gap predicts |
| Pixels with the same starting level | −0.21 × 10⁻⁶ (95% CI −0.67 to +0.24). This removes about 84% of the country-level estimate |
| Known reduction added | When a 2.5% reduction is added to EU-27 NO₂ from July 2021, the same model finds it (−0.80 × 10⁻⁶, p = 0.002). It can detect an even reduction of about 3% with 80% power |
| Ground stations | The satellite agrees with 1,543 EEA background stations (monthly r = 0.68). The stations show a similar EU-27 decline that is not significant (−4.0%, p = 0.12). They do not show the December 2023 drop the satellite records in Denmark and Sweden, so that drop is a satellite error |
| Where NO₂ fell | Polluted pixels lost about 15–25% in north-western Europe, including the non-EU UK and Switzerland, and 0–6% in south-eastern Europe, including EU members and Serbia. Western Turkey did not decline |

## What It Means

Most of the country-level estimate comes from the EU-27 being more polluted to begin with. NO₂ fell by region. It fell most in the polluted north-west, on both sides of the EU border. The data do not need an effect at the border to explain the pattern, though they cannot rule one out.

For anyone using satellite data to evaluate policy, three things follow. Compare places that start at the same level. Report results with and without the winter months. Report how countries are weighted and how controls enter the model, because here each of these choices alone moves the estimate across the 5% threshold.

## Limitations

Most of the highly polluted comparison pixels are in the United Kingdom, which uses vehicle standards that come from the EU. So the study separates EU membership from pollution level, but not EU-origin rules from their absence. The time window for the regional comparison was chosen after seeing the data. Part of the regional difference comes from winter, when there are fewest valid satellite readings. The ground-station check has no data for the United Kingdom, weather controls are country averages, and there are only nine comparison countries.

## Earlier Versions

Earlier versions reported no effect (p = 0.101). Those results used end-of-month snapshots instead of monthly means. I rebuilt the data from daily maps and re-estimated every number. The Development Log lists each change.

---

**GitHub:** github.com/sakshimaske303-commits/GPIE | **Live Dashboard:** f5cf6fijj9gm564r6aapt6.streamlit.app

Sakshi D. Maske — Independent Geospatial Researcher
