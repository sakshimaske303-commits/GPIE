# GPIE — Green Policy Intelligence Engine

[![EarthArXiv](https://img.shields.io/badge/EarthArXiv-Preprint-B7410E.svg)](https://eartharxiv.org/repository/view/14824/)

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
| Its fragility | Not significant without November–February (p = 0.11), with countries weighted by area (p = 0.11), with log GDP (p = 0.21), with real GDP per capita in place of nominal GDP (p = 0.072), or under randomization inference on the coefficient (p = 0.17); it appears only from July 2023 |
| RQ1: baseline composition | Under 999 random assignments of the treatment label, the estimate follows the pre-treatment gap between groups (r = −0.81). Comparing EU and comparison pixels in the same pre-treatment class on a 0.1° grid reduces the estimate to −0.21 × 10⁻⁶ (95% CI −0.67 to +0.24) |
| Positive control | When a known 2.5% reduction is added to EU-27 NO₂ from July 2021, the matched pixel model finds it (−0.80 × 10⁻⁶, p = 0.002); with 80% power it detects a uniform reduction of about 3% (0.65 × 10⁻⁶) |
| Ground stations | Against 1,543 EEA background stations the satellite agrees (monthly r = 0.68); the stations give a similar relative EU-27 decline that is not significant (−4.0%, p = 0.12) and no December 2023 drop, which is a retrieval artefact |
| RQ2: where NO₂ fell | Polluted pixels lost about 15–25% in north-western Europe, including the non-EU United Kingdom (−20%) and Switzerland (−18%), and 0–6% in south-eastern Europe, including EU members and Serbia; polluted western Turkey did not decline (−0.3%) |

Most of the country-level estimate reflects that the EU-27 was more polluted to begin with. The data do not require an effect at the EU border, but they cannot rule one out: the matched interval admits a decline of up to half the country-level estimate. The regional pattern depends partly on winter retrievals of uncertain quality, and its cause is not identified.

Further checks reported in the paper:
- **Stable under:** year-month fixed effects, EU-specific seasonality, wind and boundary-layer height, COVID-19 stringency, excluding the COVID-19 or energy-crisis months, leaving out any one comparison country, wild cluster bootstrap (p = 0.018).
- **Not tied to the law's date:** every treatment date shifted by ±6 or ±12 months is also significant, and an EU-specific linear trend removes the treatment term (+0.86 × 10⁻⁶, p = 0.28).
- **Composition at country level:** with each country's pre-treatment level × post in the model the EU term is +0.58 × 10⁻⁶ (p = 0.26); without the Netherlands and Belgium the estimate is −0.73 × 10⁻⁶ (p = 0.054); restricted to countries no more polluted than the United Kingdom it is −0.11 × 10⁻⁶ (p = 0.71).
- **Pixel level:** the matched estimate is flat in 12-month blocks before and after the law (all p ≥ 0.22) and unchanged without the COVID-19 months (−0.23 × 10⁻⁶).
- **Inference:** p-values use a t distribution with clusters − 1 degrees of freedom; residuals are spatially correlated in 59 of 72 months (Moran's I), so the clustered p-values are, if anything, too small.

> **Correction note:** earlier versions of this project reported a pooled null (p = 0.101). Those results were based on NO₂ values that turned out to be single end-of-month snapshots rather than monthly means (Sentinel Hub clips Sentinel-5P requests to the last 24 hours of the interval). The acquisition was rebuilt (`src/s5p_process_daily.py`: one raster per day, pooled into monthly means) and every number was re-estimated. The full history is in the Development Log.

---

## Interactive Maps

Hoverable, zoomable versions of maps and charts, built by `src/build_interactive_maps.py` and embedded in the dashboard's **Interactive Maps** page. The NDVI, GDP, temperature and synthetic-control items are supplementary and are not part of the paper.

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
| Real GDP per capita (PPP, constant 2021 int. $; constant 2015 US$) | World Bank, all 36 countries | Check on the GDP control |
| COVID-19 stringency index | Oxford COVID-19 Government Response Tracker | Control (robustness) |
| Boundaries | Eurostat GISCO NUTS 0 (2024); GADM 4.1 for UK, Norway, Switzerland | Country masks |
| NO₂ at ground stations (verified E1a) | European Environment Agency, via the `airbase` package | Check on the satellite data (station-month means) |

The repository also holds datasets that are **not used in the paper**: CGLS NDVI, ESA WorldCover land cover, Copernicus DEM, WorldPop population and EUR-Lex policy records. They support the dashboard's context pages and the supplementary analyses below (see `Data_Sources.md`).

Contains modified Copernicus Sentinel data (2019–2024) processed by Sentinel Hub, and modified Copernicus Climate Change Service information (2019–2024). GADM boundaries are subject to the GADM licence.

---

## Supplementary Analyses (not in the paper)

These come from earlier stages of the project. They use the baseline model (country and calendar-month fixed effects), not the paper's main model.
- **NDVI.** The same design applied to CGLS NDVI gives −0.0194 (p = 0.008). It is an exploratory association, not evidence that the Climate Law affected vegetation: land-use change, drought and agricultural policy are not controlled for.
- **Synthetic control** (`src/synthetic_control.py`): post-treatment gap −1.45 × 10⁻⁶, ranking 2nd of 10 among in-space placebos.
- **Higher/lower-baseline split** (`src/causal_inference_robustness_checks.py`): the decline is concentrated in the 14 EU members with higher pre-treatment NO₂. The split is defined by the outcome and chosen after seeing the result.
- **Transferability test.** The NO₂ acquisition step was run on India's GADM 4.1 boundary (2019–2024) with the same method (`src/test_india_transferability.py`). All 72 months returned data; the monthly national mean ranged from 2.27 × 10⁻⁵ to 4.16 × 10⁻⁵ mol/m², inside the 5th–95th percentile range of EU-27 country-months. This shows the pipeline runs outside Europe; it is not a causal analysis.

---

## Architecture

All scripts named here are in `src/`.

```text
 SENTINEL-5P TROPOMI L2 NO₂ ──▶ s5p_process_daily.py / download_no2_gridded.py
   (Sentinel Hub Process API,      daily 0.1° rasters, qa ≥ 0.75
    2,192 days)                    │
                                   ├──▶ country monthly means ──┐
                                   └──▶ pixel monthly grid ─────┼──▶ country-level DiD, placebo, inference
 ERA5 · GDP · OxCGRT ──▶ master_merge_control.py ───────────────┤     (causal_inference_identification_checks.py,
 GISCO NUTS 0 · GADM ──▶ country_boundaries.py (masks) ─────────┘      causal_inference_stress_tests.py,
                                                                        causal_inference_additional_checks.py,
                                                                        causal_inference_positive_control.py)
                                                                   ──▶ pixel-level matched DiD
                                                                        (analyse_no2_grid_baseline.py, stress tests)
                                                                   ──▶ figures (plot_*.py, map_*.py) · dashboard
```

---

## Reproducibility

### Quick reproduction

From the repository root:

```bash
pip install -r requirements.txt
python reproduce_paper.py --check   # lists which steps can run and which inputs are missing
python reproduce_paper.py           # re-runs every estimate, table and figure in order (about 30 min)
```

Steps 1, 2 and 11 run from the data in this repository with no download. `src/download_nuts.py` and `src/download_gadm.py` (no account needed) add steps 9 and 10. Steps 3–8 also need the monthly 0.1° NO₂ grid, which `src/download_no2_gridded.py` builds with a free Sentinel Hub account. `python reproduce_paper.py --compare DIR` compares a re-run with an earlier copy of `data/*.json`; on my machine a full re-run gives every number in the paper again.

All scripts are run from the repository root (for example `python src/master_merge_control.py`), because their file paths start at the root.

### Full pipeline

- **Environment**: Python 3.10+. Most dependencies install via `requirements.txt`; `geopandas`/`rasterio`/`GDAL` are easiest installed via `conda` (`conda install -c conda-forge geopandas rasterio gdal`) if the `pip` install fails on your platform.
- **Credentials**: Sentinel Hub (`SH_CLIENT_ID`, `SH_CLIENT_SECRET`) and Copernicus CDS access need free accounts; credentials go in a local `.env` file (never committed). The World Bank and Eurostat APIs need no credentials.
- **Run order for the paper:**
  1. Boundaries: `src/download_nuts.py` and `src/download_gadm.py` (GADM files are not in the repository because the GADM licence does not allow redistribution).
  2. NO₂: `src/download_no2_sentinelhub.py` (daily Process API rasters → country monthly means, `no2_stats_monthly_mean_36.json`) and `src/download_no2_gridded.py` (keeps every daily 0.1° raster and builds `data/earth_observation/no2/gridded/no2_grid_monthly.npz`, about 77 MB, which the pixel-level analysis needs; not in the repository because of its size). `src/check_s5p_processor_versions.py` checks which TROPOMI processor versions the values come from; `src/diagnose_sentinelhub.py` checks which Sentinel Hub endpoints currently work.
  3. Controls: `src/download_era5.py` → `src/unzip_era5.py` → `src/process_era5.py` → `src/era5_regional_stats.py` + `src/era5_regional_stats_control_expansion.py`; `src/download_era5_wind_blh.py` (→ `data/era5_wind_blh_country_monthly.csv`); `src/download_eurostat_gdp.py` → `src/process_eurostat.py` → `src/apply_eu27_filter.py`; `src/download_gdp_control_countries.py` + `src/download_gdp_control_expansion.py`; `src/download_gdp_real.py` (real GDP per capita, for the check); `data/covid/oxcgrt_stringency_national.csv` (Oxford stringency index).
  4. `src/master_merge_control.py` → `data/master_dataset_control.csv`
  5. Models: `src/causal_inference_identification_checks.py` (→ `data/identification_checks.json`), `src/analyse_no2_grid_baseline.py` (→ `data/grid_baseline_checks.json`, Figures 4–5), `src/causal_inference_stress_tests.py` (→ `data/stress_tests.json`, `data/placebo_assignments.csv`, Figures 3 and 6), `src/causal_inference_additional_checks.py` (→ `data/additional_checks.json`), `src/causal_inference_positive_control.py` (→ `data/positive_control.json`, Figure 7), `src/causal_inference_real_gdp.py` (→ `data/real_gdp_checks.json`), `src/validate_eea_stations.py` (EEA stations, after `airbase verified -p NO2 ... -M`; → `data/eea_station_monthly.csv`, `data/eea_validation.json`), `src/spatial_autocorrelation.py`
  6. Figures: `src/map_control_group_highlight.py` (Figure 1), `src/plot_block_event_study.py` (Figure 2); dashboard: `dashboard/app.py`
- **Supplementary and historical scripts** (not used for the paper): `src/causal_inference_final_did.py` and `src/causal_inference_robustness_checks.py` (baseline model), `src/causal_inference_ndvi.py`, `src/causal_inference_event_study.py`, `src/synthetic_control.py`, `src/test_india_transferability.py`; the single-cohort models `archive/superseded_scripts/causal_inference_initial_model.py`, `src/causal_inference_placebo.py`, `archive/superseded_scripts/causal_inference.py`.
- **Superseded scripts kept for the record**: `archive/superseded_scripts/run_pipeline.py`/`archive/superseded_scripts/download_no2.py`/`archive/superseded_scripts/extract_no2.py` (OData + HARP Level-2 test pipeline), `download_*_control_expansion.py` for NO₂/NDVI (single-mosaic acquisition), `archive/superseded_scripts/master_merge.py`, `archive/superseded_scripts/master_merge_control_expanded.py` and `archive/superseded_scripts/causal_inference_expanded_control.py` (these two read `data/master_dataset_control_expanded.csv`, which holds the superseded end-of-month NO₂ values).
- **Audit trail**: every methodology change is logged chronologically in the Development Log.

---

## Repository Structure

```text
GPIE/
├── reproduce_paper.py          # One command: re-runs every estimate, table and figure in the paper
├── src/                        # All pipeline scripts (download, processing, models, figures)
│   ├── download_*.py, process_*.py, *_regional_stats*.py   # Data acquisition and processing
│   ├── s5p_process_daily.py    # NO₂: daily Process API rasters → country monthly means
│   ├── master_merge_control.py # Country × month panel (36 countries × 72 months)
│   ├── causal_inference_*.py   # Country- and pixel-level models
│   ├── analyse_no2_grid_baseline.py, validate_eea_stations.py
│   ├── map_*.py, plot_*.py     # Figures
│   └── config.py, country_boundaries.py   # Shared settings and boundary loader
├── data/                       # Processed datasets, master panel and model outputs (JSON/CSV)
│   └── earth_observation/      # Per-dataset acquisition/processing outputs
├── outputs/
│   ├── plots/                  # Static maps and charts
│   └── interactive/            # Hoverable/zoomable HTML maps (src/build_interactive_maps.py)
├── dashboard/                  # Streamlit dashboard
├── archive/
│   ├── superseded_scripts/     # Earlier pipeline versions, kept for the record, not used by the paper
│   └── ...                     # Dev-time scratch and smoke-test scripts
├── GPIE_Research_Paper.md      # Research paper
├── GPIE_Executive_Summary.md   # Executive summary
├── GPIE_Development_Log.md     # Development log (script names as they were when each entry was written)
├── Data_Sources.md, CITATION.cff, LICENSE, requirements.txt
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
