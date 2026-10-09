# GPIE — Green Policy Intelligence Engine

[![EarthArXiv](https://img.shields.io/badge/EarthArXiv-Preprint-B7410E.svg)](https://eartharxiv.org/repository/view/14824/) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21756661.svg)](https://doi.org/10.5281/zenodo.21756661)

**What does a country-level difference-in-differences on satellite NO₂ actually identify?**

GPIE uses Sentinel-5P TROPOMI tropospheric NO₂ (2,192 daily rasters, 2019–2024) to test a design that is common in satellite-based policy evaluation: compare the change in pollution in countries that adopted a policy with the change in countries that did not. The case is the European Climate Law (Regulation (EU) 2021/1119; adopted 30 June 2021, in force 29 July 2021; July 2021 is the first post-treatment month), compared across the EU-27 and nine neighbouring non-EU countries. The law is used as a negative-control case: it has a clear date and border but no plausible dated effect on NO₂, so an estimate that looks like an effect needs another explanation.

**Research question.** When treated and comparison countries differ in baseline pollution, what does a country-level DiD on satellite NO₂ identify?
- **RQ1:** how much of the country-level estimate is explained by the difference in pre-treatment NO₂ between the two groups?
- **RQ2:** when EU and comparison areas are compared at the same starting level, where did NO₂ fall, and does the pattern follow the EU border?

---

## Project Documentation

| Document | What's Inside |
|---|---|
| [Research Paper](./GPIE_Research_Paper.md) | The study: question, data, methods, results, limitations |
| [Executive Summary](./GPIE_Executive_Summary.md) | Two-page summary of the paper |
| [Development Log](./GPIE_Development_Log.md) | How the project developed, including every correction |

---

## Live Dashboard

**[View the interactive dashboard →](https://f5cf6fijj9gm564r6aapt6.streamlit.app/)**

---

## Key Findings

| Step | Result |
|---|---|
| Country-level DiD (main model: country and year-month fixed effects, EU-specific seasonality) | NO₂ fell 1.34 × 10⁻⁶ mol/m² more in the EU-27 (4.3% of its pre-treatment level; p = 0.022) |
| Its fragility | Not significant without November–February (p = 0.11), with countries weighted by area (p = 0.11), with log GDP (p = 0.21), or under randomization inference on the coefficient (p = 0.17); it appears only from July 2023 |
| RQ1: baseline composition | Under 999 random assignments of the treatment label, the estimate follows the pre-treatment gap between groups (r = −0.81). Comparing EU and comparison pixels in the same pre-treatment class on a 0.1° grid reduces the estimate to −0.21 × 10⁻⁶ (95% CI −0.67 to +0.24) |
| RQ2: where NO₂ fell | Polluted pixels lost about 15–25% in north-western Europe, including the non-EU United Kingdom (−20%) and Switzerland (−18%), and 0–6% in south-eastern Europe, including EU members and Serbia; polluted western Turkey did not decline (−0.3%) |

Most of the country-level estimate reflects that the EU-27 was more polluted to begin with. The data do not require an effect at the EU border, but they cannot rule one out: the matched interval admits a decline of up to half the country-level estimate. The regional pattern depends partly on winter retrievals of uncertain quality, and its cause is not identified.

Further checks reported in the paper:
- **Stable under:** year-month fixed effects, EU-specific seasonality, wind and boundary-layer height, COVID-19 stringency, excluding the COVID-19 or energy-crisis months, leaving out any one comparison country, wild cluster bootstrap (p = 0.018).
- **Not tied to the law's date:** every treatment date shifted by ±6 or ±12 months is also significant, and an EU-specific linear trend removes the treatment term (+0.86 × 10⁻⁶, p = 0.28).
- **Composition at country level:** with each country's pre-treatment level × post in the model the EU term is +0.58 × 10⁻⁶ (p = 0.26); without the Netherlands and Belgium the estimate is −0.73 × 10⁻⁶ (p = 0.054); restricted to countries no more polluted than the United Kingdom it is −0.11 × 10⁻⁶ (p = 0.71).
- **Pixel level:** the matched estimate is flat in 12-month blocks before and after the law (all p ≥ 0.22) and unchanged without the COVID-19 months (−0.23 × 10⁻⁶).
- **Inference:** p-values use a t distribution with clusters − 1 degrees of freedom; residuals are spatially correlated in 59 of 72 months (Moran's I), so the clustered p-values are, if anything, too small.

> **Correction note:** earlier versions of this project reported a pooled null (p = 0.101). Those results were based on NO₂ values that turned out to be single end-of-month snapshots rather than monthly means (Sentinel Hub clips Sentinel-5P requests to the last 24 hours of the interval). The acquisition was rebuilt (`s5p_process_daily.py`: one raster per day, pooled into monthly means) and every number was re-estimated. The full history is in the Development Log.

---

## Interactive Maps

Hoverable, zoomable versions of maps and charts, built by `build_interactive_maps.py` and embedded in the dashboard's **Interactive Maps** page. The NDVI, GDP, temperature and synthetic-control items are supplementary and are not part of the paper.

| Map | Link |
|---|---|
| Study Design: EU-27 vs. Comparison Group | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/control_group_map.html) |
| NO₂ Concentration | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/no2_map.html) |
| Pixel-Level NO₂ Change Map | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/no2_pixel_change_map.html) |
| NO₂ Change by Starting Pollution Level | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/no2_change_by_baseline.html) |
| Moran's I Spatial Clusters | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/moran_lisa_map.html) |
| Explore Trends by Country | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/explore_trends.html) |
| Quarterly Event Study (baseline model, supplementary) | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/event_study.html) |
| Synthetic Control Gap (supplementary) | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/synthetic_control.html) |
| Vegetation Health (NDVI, supplementary) | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/ndvi_map.html) |
| Temperature (supplementary) | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/climate_map.html) |
| GDP (supplementary) | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/gdp_map.html) |

---

## Data Used in the Paper

| Dataset | Provider | Role |
|---|---|---|
| Tropospheric NO₂ (Sentinel-5P TROPOMI Level-2, qa ≥ 0.75) | ESA / Copernicus, via the Sentinel Hub Process API | Outcome: daily 0.1° rasters → monthly country and pixel means |
| Temperature, precipitation, wind speed, boundary-layer height (ERA5) | ECMWF / Copernicus Climate Data Store | Controls (monthly country means) |
| GDP | Eurostat (EU-27), World Bank (comparison countries) | Control (annual, country) |
| COVID-19 stringency index | Oxford COVID-19 Government Response Tracker | Control (robustness) |
| Boundaries | Eurostat GISCO NUTS 0 (2024); GADM 4.1 for UK, Norway, Switzerland | Country masks |

The repository also holds datasets that are **not used in the paper**: CGLS NDVI, ESA WorldCover land cover, Copernicus DEM, WorldPop population and EUR-Lex policy records. They support the dashboard's context pages and the supplementary analyses below (see `Data_Sources.md`).

Contains modified Copernicus Sentinel data (2019–2024) processed by Sentinel Hub, and modified Copernicus Climate Change Service information (2019–2024). GADM boundaries are subject to the GADM licence.

---

## Supplementary Analyses (not in the paper)

These come from earlier stages of the project. They use the baseline model (country and calendar-month fixed effects), not the paper's main model.
- **NDVI.** The same design applied to CGLS NDVI gives −0.0194 (p = 0.008). It is an exploratory association, not evidence that the Climate Law affected vegetation: land-use change, drought and agricultural policy are not controlled for.
- **Synthetic control** (`synthetic_control.py`): post-treatment gap −1.45 × 10⁻⁶, ranking 2nd of 10 among in-space placebos.
- **Higher/lower-baseline split** (`causal_inference_robustness_checks.py`): the decline is concentrated in the 14 EU members with higher pre-treatment NO₂. The split is defined by the outcome and chosen after seeing the result.
- **Transferability test.** The NO₂ acquisition step was run on India's GADM 4.1 boundary (2019–2024) with the same method (`test_india_transferability.py`). All 72 months returned data; the monthly national mean ranged from 2.27 × 10⁻⁵ to 4.16 × 10⁻⁵ mol/m², inside the 5th–95th percentile range of EU-27 country-months. This shows the pipeline runs outside Europe; it is not a causal analysis.

---

## Architecture

```text
 SENTINEL-5P TROPOMI L2 NO₂ ──▶ s5p_process_daily.py / download_no2_gridded.py
   (Sentinel Hub Process API,      daily 0.1° rasters, qa ≥ 0.75
    2,192 days)                    │
                                   ├──▶ country monthly means ──┐
                                   └──▶ pixel monthly grid ─────┼──▶ country-level DiD, placebo, inference
 ERA5 · GDP · OxCGRT ──▶ master_merge_control.py ───────────────┤     (causal_inference_identification_checks.py,
 GISCO NUTS 0 · GADM ──▶ country_boundaries.py (masks) ─────────┘      causal_inference_stress_tests.py,
                                                                        causal_inference_additional_checks.py)
                                                                   ──▶ pixel-level matched DiD
                                                                        (analyse_no2_grid_baseline.py, stress tests)
                                                                   ──▶ figures (plot_*.py, map_*.py) · dashboard
```

---

## Reproducibility

- **Environment**: Python 3.10+. Most dependencies install via `requirements.txt`; `geopandas`/`rasterio`/`GDAL` are easiest installed via `conda` (`conda install -c conda-forge geopandas rasterio gdal`) if the `pip` install fails on your platform.
- **Credentials**: Sentinel Hub (`SH_CLIENT_ID`, `SH_CLIENT_SECRET`) and Copernicus CDS access need free accounts; credentials go in a local `.env` file (never committed). The World Bank and Eurostat APIs need no credentials.
- **Run order for the paper:**
  1. NO₂: `download_no2_sentinelhub.py` (daily Process API rasters → country monthly means, `no2_stats_monthly_mean_36.json`) and `download_no2_gridded.py` (keeps every daily 0.1° raster and builds `data/earth_observation/no2/gridded/no2_grid_monthly.npz`, about 77 MB, which the pixel-level analysis needs; not in the repository because of its size). `check_s5p_processor_versions.py` checks which TROPOMI processor versions the values come from; `diagnose_sentinelhub.py` checks which Sentinel Hub endpoints currently work.
  2. Controls: `download_era5.py` → `unzip_era5.py` → `process_era5.py` → `era5_regional_stats.py` + `era5_regional_stats_control_expansion.py`; `download_era5_wind_blh.py` (→ `data/era5_wind_blh_country_monthly.csv`); `download_eurostat_gdp.py` → `process_eurostat.py` → `apply_eu27_filter.py`; `download_gdp_control_countries.py` + `download_gdp_control_expansion.py`; `data/covid/oxcgrt_stringency_national.csv` (Oxford stringency index).
  3. `master_merge_control.py` → `data/master_dataset_control.csv`
  4. Models: `causal_inference_identification_checks.py` (→ `data/identification_checks.json`), `analyse_no2_grid_baseline.py` (→ `data/grid_baseline_checks.json`, Figures 4–5), `causal_inference_stress_tests.py` (→ `data/stress_tests.json`, `data/placebo_assignments.csv`, Figures 3 and 6), `causal_inference_additional_checks.py` (→ `data/additional_checks.json`), `spatial_autocorrelation.py`
  5. Figures: `map_control_group_highlight.py` (Figure 1), `plot_block_event_study.py` (Figure 2); dashboard: `dashboard/app.py`
- **Supplementary and historical scripts** (not used for the paper): `causal_inference_final_did.py` and `causal_inference_robustness_checks.py` (baseline model), `causal_inference_ndvi.py`, `causal_inference_event_study.py`, `synthetic_control.py`, `test_india_transferability.py`; the single-cohort models `causal_inference_initial_model.py`, `causal_inference_placebo.py`, `causal_inference.py`.
- **Superseded scripts kept for the record**: `run_pipeline.py`/`download_no2.py`/`extract_no2.py` (OData + HARP Level-2 test pipeline), `download_*_control_expansion.py` for NO₂/NDVI (single-mosaic acquisition), `master_merge.py`, `master_merge_control_expanded.py` and `causal_inference_expanded_control.py` (these two read `data/master_dataset_control_expanded.csv`, which holds the superseded end-of-month NO₂ values).
- **Audit trail**: every methodology change is logged chronologically in the Development Log.

---

## Repository Structure

```text
GPIE/
├── dashboard/                  # Streamlit dashboard
├── data/                       # Processed datasets, master panel and model outputs (JSON/CSV)
│   └── earth_observation/      # Per-dataset acquisition/processing outputs
├── outputs/
│   ├── plots/                  # Static maps and charts
│   └── interactive/            # Hoverable/zoomable HTML maps (build_interactive_maps.py)
├── archive/                    # Dev-time scratch/inspection/smoke-test scripts, not part of the pipeline
├── GPIE_Research_Paper.md      # Research paper
├── GPIE_Executive_Summary.md   # Executive summary
├── GPIE_Development_Log.md     # Development log
├── s5p_process_daily.py        # NO₂: daily Process API rasters → country monthly means
├── download_no2_gridded.py     # NO₂: daily rasters kept as a 0.1° monthly grid
├── analyse_no2_grid_baseline.py
├── causal_inference_*.py       # Country- and pixel-level models
├── map_*.py, plot_*.py         # Figures
└── country_boundaries.py       # Shared EU-27 + comparison-group boundary loader
```

## Tech Stack

Python · NumPy · pandas · statsmodels · rasterio · geopandas · libpysal/esda · matplotlib · Plotly · folium · Streamlit · Sentinel Hub Process API · Copernicus Climate Data Store · Eurostat API · World Bank API

## Running the Dashboard Locally

```bash
git clone https://github.com/sakshimaske303-commits/GPIE.git
cd GPIE
pip install -r requirements.txt
cd dashboard
streamlit run app.py
```

## Author

**Sakshi D. Maske**

Independent Geospatial Researcher

## License

This project is licensed under [CC BY 4.0](./LICENSE) — free to share and adapt, with attribution. See `CITATION.cff` for citation metadata.
