# GPIE: Declarations

**What Does a Country-Level Difference-in-Differences on Satellite NO₂ Identify? Baseline Composition, Winter Retrievals and the European Climate Law**

Sakshi D. Maske · Independent Geospatial Researcher · ORCID [0009-0002-5683-5966](https://orcid.org/0009-0002-5683-5966)

Version 1.2.0  
Preprint: EarthArXiv, DOI [10.31223/X5GB87](https://doi.org/10.31223/X5GB87) · Archive: Zenodo, DOI [10.5281/zenodo.21756660](https://doi.org/10.5281/zenodo.21756660) · Code and data: [github.com/sakshimaske303-commits/GPIE](https://github.com/sakshimaske303-commits/GPIE)

## Highlights

- A country-level difference-in-differences finds NO₂ fell 4.3% more in the EU-27 than in nine neighbouring countries after the European Climate Law (p = 0.022), but the gap appears only from July 2023 and is not robust to several reasonable specifications.
- Under random assignment of the treatment label, the estimate follows how much more polluted the labelled group was before treatment (r = −0.81).
- Comparing EU and comparison pixels that started at the same NO₂ level reduces the estimate to −0.21 × 10⁻⁶ mol/m² (95% CI −0.67 to +0.24); the same comparison detects a known 2.5% reduction added to EU-27 NO₂.
- 1,543 EEA ground stations agree with the satellite (monthly r = 0.68) and show that the December 2023 drop is a retrieval artefact.
- Polluted areas lost about 15–25% of their NO₂ in north-western Europe, including the non-EU United Kingdom and Switzerland, and little in south-eastern Europe.

## Author contributions (CRediT)

Sakshi D. Maske: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review and editing, Visualization. This is a single-author study.

## Funding

This research received no external funding. I covered all costs myself.

## Competing interests

I declare no competing interests.

## Ethics

Not applicable. This study did not involve human participants, animals, or personal data of any kind.

## Data availability

All data are from public sources: Sentinel-5P TROPOMI tropospheric NO₂ (daily rasters through the Sentinel Hub Process API), ERA5 reanalysis (Copernicus Climate Change Service), Eurostat and World Bank GDP, the Oxford COVID-19 Government Response Tracker, NUTS and GADM boundaries, and European Environment Agency air-quality station data. The paper contains modified Copernicus Sentinel data (2019–2024), processed by Sentinel Hub, and modified Copernicus Climate Change Service information (2019–2024). GADM boundaries are downloaded by the code and not stored in the repository, because the GADM licence does not allow redistribution.

## Code availability and reproducibility

All code is in the repository. `reproduce_paper.py` re-runs every estimate, table and figure in order, and `--check` lists which steps can run with the files available. Some steps run directly from the data in the repository. The monthly 0.1° NO₂ grid (about 77 MB) and the daily rasters behind it are not stored in the repository and are rebuilt with the included download script, which needs a free Sentinel Hub account; ERA5 needs a free Copernicus account.

## Analysis transparency

The European Climate Law is used as a negative-control case: it has a clear date and border but no plausible dated effect on NO₂, so an estimate that looks like an effect needs another explanation. The period from July 2023, the threshold for polluted pixels and the regional grouping were chosen after seeing the data, so the descriptive regional results and their p-values are not confirmatory. Residuals are spatially correlated, so the clustered p-values are, if anything, too small.

## Corrections and version history

Earlier versions reported a pooled null (p = 0.101). Those results rested on NO₂ values that were single end-of-month snapshots rather than monthly means, because Sentinel Hub clips Sentinel-5P requests to the last 24 hours of the interval. I rebuilt the acquisition as one raster per day pooled into monthly means and re-estimated every number. Before that, my first model attributed the NO₂ decline to the law, but a placebo test on a fake date was just as strong, so I rebuilt the study around an outside comparison group. Every change is recorded in `GPIE_Development_Log.md`.

## Use of AI tools

I used Claude (Anthropic), an AI assistant, at several points in this project. Most of that help was checking: whether the estimates quoted in the paper, executive summary, README and dashboard matched my output tables, from the country-panel difference-in-differences to the pixel comparison on 51,072 matched pixels and the comparison with EEA ground stations. When a script failed or returned something I could not explain, I sometimes used it to help trace the problem in my Python code. I wrote the paper and the other documents myself; I used it to point out sentences that were unclear or too technical, places where something seemed to be missing, and punctuation errors, and I decided what to change. I also used it for the layout of the project pages. It did not download or process the Sentinel-5P data, specify or run any model, or produce the results. The research design, the choice of comparison countries and tests, the decision to report the country-level estimate as not robust once polluted places were compared with equally polluted places, and the interpretation are my own. I checked every suggestion before using it and take full responsibility for the content.

## Licence and citation

The code, documentation and paper are released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0). Citation metadata are in `CITATION.cff`.
