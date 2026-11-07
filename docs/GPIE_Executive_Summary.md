# GPIE: Green Policy Intelligence Engine

*Membership or Instruments? Satellite NO₂, Baseline Pollution and the European Climate Law*

**Executive Summary** · Sakshi D. Maske · ORCID [0009-0002-5683-5966](https://orcid.org/0009-0002-5683-5966)

---

## Problem

Satellite NO₂ makes it easy to compare pollution in countries that adopted a policy with countries that did not. A common way to do this is a difference-in-differences (DiD) on country averages. How much NO₂ can fall, however, depends on how much there was to begin with, and clean areas have little to lose. If the treated countries start out more polluted, a DiD can mistake that difference for a policy effect.

## Research Question

When treated and comparison countries start from different pollution levels, what does a country-level DiD on satellite NO₂ measure?

- **RQ1:** How much of the country-level estimate comes from the difference in starting NO₂ between the two groups?
- **RQ2:** When EU and comparison areas start at the same level, where did NO₂ fall, and does the pattern follow the EU border?

The test case is the European Climate Law (Regulation (EU) 2021/1119), adopted on 30 June 2021 and in force from 29 July 2021. It applies to all 27 member states from one date and not to their neighbours. It sets climate targets but has no direct mechanism on NO₂, so any estimate that looks like an effect must have another explanation.

## Data and Method

- **Outcome:** Sentinel-5P TROPOMI tropospheric NO₂. One 0.1° map per day for 2,192 days (2019–2024, quality value ≥ 0.75), averaged by month for 36 countries and for every pixel.
- **Groups:** The EU-27 against nine non-EU countries: the United Kingdom, Norway, Switzerland, Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia and Serbia. July 2021 is the first month after the law.
- **Country level:** DiD with country and year-month fixed effects, an EU-specific seasonal cycle, ERA5 weather and GDP controls, and standard errors clustered by country. The model is re-run under about 20 other specifications.
- **Starting-level tests (RQ1):** How each country's starting level interacts with the post period, 999 random reassignments of the EU label, and a pixel-level DiD that compares EU and non-EU pixels with the same starting level.
- **Geography (RQ2):** The change in polluted pixels country by country, including western Turkey and Ukraine outside the sample.

## Findings

| Analysis | Result |
|---|---|
| Country-level DiD | NO₂ fell 1.34 × 10⁻⁶ mol/m² more in the EU-27, 4.3% of its starting level (p = 0.022) |
| How stable it is | Not significant without November–February (p = 0.11), with area weights (p = 0.11), with log GDP (p = 0.21), with real GDP per capita (p = 0.072), or under randomization inference on the coefficient (p = 0.17; p = 0.046 on the t-statistic). The difference appears only from July 2023 |
| Random EU labels | Estimates follow how much more polluted the labelled group was at the start (r = −0.81). The real EU-27 estimate is close to what its starting gap predicts |
| Pixels with the same starting level | −0.21 × 10⁻⁶ (95% CI −0.67 to +0.24). This removes about 84% of the country-level estimate |
| Known reduction added | When a 2.5% reduction is added to EU-27 NO₂ from July 2021, the same model finds it (−0.80 × 10⁻⁶, p = 0.002). It can detect an even reduction of about 3% with 80% power |
| Ground stations | The satellite agrees with 1,543 EEA background stations (monthly r = 0.68). The stations show a similar EU-27 decline that is not significant (−4.0%, p = 0.12). In December 2023 they fall by only 16% in Denmark and 7% in Sweden, where the satellite values turn negative, so most of that drop is a retrieval artefact |
| Where NO₂ fell | Polluted pixels lost about 15–25% in north-western Europe, including the non-EU UK and Switzerland, and 0–6% in south-eastern Europe, including EU members and Serbia. Western Turkey did not decline |

## What It Means

Most of the country-level estimate comes from the EU-27 being more polluted to begin with. The decline followed region more than membership and was largest in the polluted north-west, on both sides of the EU border. The data are consistent with no effect at the border, although a small one cannot be ruled out.

For satellite-based policy evaluation, the study suggests comparing places that start at the same pollution level, reporting results with and without the winter months, and reporting how countries are weighted and how controls enter the model, since here each of these choices alone moves the estimate across the 5% threshold.

## Policy Relevance

The Climate Law sets targets. NO₂ is regulated by other instruments, chiefly vehicle emission standards, the Industrial Emissions Directive and the National Emission reduction Commitments Directive. Environmental policy works through such mixes of instruments (Daugbjerg & Sønderskov, 2012), and EU environmental rules are also adopted by states outside the EU (Knill & Tosun, 2009). The United Kingdom and Switzerland apply the same vehicle standards as the EU, and their polluted areas declined like those of their EU neighbours. A comparison across the membership border therefore compares jurisdictions that share the instruments that matter for NO₂. Explaining why the same standards were followed by larger declines in the north-west than in south-eastern member states, for example through faster fleet renewal in richer countries, needs comparative evidence on how the instruments were implemented, which this study does not have.

## Limitations

Most of the highly polluted comparison pixels are in the United Kingdom, which uses vehicle standards that come from the EU. The study therefore separates EU membership from pollution level, but not EU-origin rules from their absence. The time window for the regional comparison was chosen after seeing the data. Part of the regional difference comes from winter, when there are fewest valid satellite readings. The ground-station check has no data for the United Kingdom, Albania or Montenegro, weather controls are country averages, and there are only nine comparison countries.

## Earlier Versions

Earlier versions reported no effect (p = 0.101). Those results used end-of-month snapshots instead of monthly means. I rebuilt the data from daily maps and re-estimated every number. The Development Log lists each change.

## References

Daugbjerg, C., & Sønderskov, K. M. (2012). Environmental Policy Performance Revisited: Designing Effective Policies for Green Markets. *Political Studies*, 60(2), 399–418. [https://doi.org/10.1111/j.1467-9248.2011.00910.x](https://doi.org/10.1111/j.1467-9248.2011.00910.x)

Knill, C., & Tosun, J. (2009). Hierarchy, networks, or markets: how does the EU shape environmental policy adoptions within and beyond its borders? *Journal of European Public Policy*, 16(6), 873–894. [https://doi.org/10.1080/13501760903088090](https://doi.org/10.1080/13501760903088090)

---

**GitHub:** github.com/sakshimaske303-commits/GPIE | **Live Dashboard:** f5cf6fijj9gm564r6aapt6.streamlit.app

Sakshi D. Maske · Independent Geospatial Researcher
