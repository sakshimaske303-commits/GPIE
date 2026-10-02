# GPIE — Green Policy Intelligence Engine

[![EarthArXiv](https://img.shields.io/badge/EarthArXiv-Preprint-B7410E.svg)](https://eartharxiv.org/repository/view/14824/) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21756661.svg)](https://doi.org/10.5281/zenodo.21756661)

**Independently verifying environmental policy claims using satellite data.**

GPIE is a geospatial causal-inference framework that tests whether the European Green Deal's flagship legislation — the **European Climate Law** (Regulation (EU) 2021/1119; adopted 30 June 2021, in force 29 July 2021; July 2021 is the first post-treatment month) — produced a measurable, statistically distinguishable reduction in NO₂ pollution across the EU-27, using satellite observations rather than self-reported government claims.

Built on a **"Trust, But Verify"** research philosophy: policy claims are treated as hypotheses to be independently tested, not facts to be assumed.

---

## Project Documentation

| Document | What's Inside |
|---|---|
| [Executive Summary](./GPIE_Executive_Summary.pdf) | Short snapshot — question, method, headline finding, robustness checklist, and links (fastest overview) |
| [Research Paper](./GPIE_Research_Paper.md) | Formal academic paper — literature review, statistical methodology, results, discussion |
| [Development Log](./GPIE_Development_Log.md) | Full technical development log — every bug, debugging session, and methodology iteration |

---

## Live Dashboard

**[View the interactive dashboard →](https://f5cf6fijj9gm564r6aapt6.streamlit.app/)**

---

## Interactive Maps

Hoverable, zoomable versions of the main maps and charts (6 maps + 3 charts) — same underlying data as the static figures, built with `folium`/`plotly` instead of `matplotlib`. Also embedded directly in the dashboard's **Interactive Maps** page.

| Map | Link |
|---|---|
| Study Design: Treatment vs. Control | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/control_group_map.html) |
| NO₂ Concentration | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/no2_map.html) |
| Vegetation Health (NDVI) | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/ndvi_map.html) |
| Temperature | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/climate_map.html) |
| GDP | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/gdp_map.html) |
| Moran's I Spatial Clusters | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/moran_lisa_map.html) |
| Event-Study Plot | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/event_study.html) |
| Synthetic Control Gap (intercept-adjusted) | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/synthetic_control.html) |
| Explore Trends by Country | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/explore_trends.html) |

Built by `build_interactive_maps.py`.

---

## What This Project Does

- Compiles **8 data sources** across **36 countries** (EU-27 + a 9-country non-EU comparison group: UK, Norway, Switzerland, Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, Serbia), 2019–2024. The headline model uses NO₂, ERA5 temperature/precipitation, GDP and boundaries; NDVI is a secondary outcome; land cover, elevation, population and the EUR-Lex records are descriptive context only (see `Data_Sources.md`)
- Estimates a two-group **Difference-in-Differences** model to separate any EU-specific change from the shared European NO₂ trend
- Runs a placebo test, quarterly event study, GDP-exclusion, log-outcome, treatment-date and baseline-split checks, a synthetic control and a Moran's I spatial diagnostic, plus identification checks (year-month fixed effects, EU-specific seasonality, wind/boundary-layer and COVID-19 controls, wild cluster bootstrap, randomization inference)
- Reports what the data show (EU-27 NO₂ fell faster than in the comparison group) and what they do not show (a break at the Climate Law's date), including the checks that limit the causal reading
- Presents it through 20 static figures (`GPIE_Maps_and_Plots.pdf`), 9 interactive maps/charts, and a Streamlit dashboard

## Key Finding

Measured with true monthly satellite means, NO₂ fell more in the EU-27 than in the 9-country non-EU comparison group: the pooled DiD estimate is −1.52 × 10⁻⁶ mol/m² (about 4.9% of the EU's pre-treatment mean; p = 0.013, cluster-robust), or −4.2% on the log scale (p = 0.034). The decline is concentrated in the 14 EU countries with higher pre-treatment NO₂ (p = 0.002; log −6.4%, p = 0.006) and absent in the lower-baseline group.

**The design cannot attribute this to the Climate Law:**

- **Composition effect (pixel level):** on a 0.1° grid, NO₂ fell in proportion to each pixel's pre-treatment level (about a quarter of it), equally inside and outside the EU. Comparing EU and comparison pixels with the same starting level cuts the estimate from −1.34 × 10⁻⁶ to −0.21 × 10⁻⁶ (p = 0.341). The country-level estimate mostly reflects that EU countries contain more highly polluted areas (`analyse_no2_grid_baseline.py`).
- **Late onset:** with year-month fixed effects and EU-specific seasonality the estimate is −1.34 × 10⁻⁶ (p = 0.016), but there is no effect in the first two years after the law (Jul 2021–Jun 2023: p = 0.98 and 0.44); the decline appears only from July 2023 (−2.18 × 10⁻⁶, p = 0.008).
- **Event study:** 7 of 9 pre-treatment quarters differ significantly under a common seasonal cycle; this is largely seasonal and disappears once the EU has its own seasonal cycle (joint p = 0.292).
- **Treatment date:** every alternative cutoff (±6 and ±12 months) is also significant, including two dates before the law existed.
- **EU-specific trend:** allowing a steady EU-specific trend removes the treatment-date effect (+8.7 × 10⁻⁷, p = 0.243); the trend itself is significant (−7.9 × 10⁻⁷ per year, p = 0.016).
- **Synthetic control** (9 donors, intercept-adjusted): gap −8.1 × 10⁻⁷, ranking 5th of 10 among placebo countries.
- **Inference:** wild cluster bootstrap p = 0.018, but randomization inference p = 0.16; without the GDP control p = 0.074.
- **Spatial dependence:** DiD residuals are spatially correlated in 59 of 72 months (median Moran's I = 0.347), so the clustered p-values are likely too small.

The estimate is otherwise sturdy: wind speed, boundary-layer height and COVID-19 stringency controls do not move it, dropping the COVID-19 window or the energy-crisis months leaves it in place, and no single comparison country drives it (`causal_inference_identification_checks.py` → `data/identification_checks.json`).

So the evidence points to a decline of NO₂ in polluted areas across Europe, EU and non-EU alike, that emerges about two years after the Climate Law. It is not an effect specific to the EU or to the law's date.

> **Correction note:** earlier versions of this project reported a pooled null (p = 0.101). Those results were based on NO₂ values that turned out to be single end-of-month snapshots rather than monthly means (Sentinel Hub clips Sentinel-5P requests to the last 24 hours of the interval). The acquisition was rebuilt (`s5p_process_daily.py`: one raster per day, pooled into monthly means) and every number was re-estimated.

The dashboard's Methodology page documents the full sequence, including the initial single-cohort result and the placebo test that invalidated it.

The same design applied to the secondary outcome NDVI gives −0.0194 (p = 0.005), a relative decline in the EU-27. It is reported as an exploratory association, not as evidence the Climate Law affected vegetation.

## Transferability Validation

The NO₂ acquisition step was run on **India** (2019–2024) with the same daily Process API method and QA threshold as the EU study (`s5p_process_daily.py`), using India's GADM 4.1 national boundary. `test_india_transferability.py` writes a sanity-check summary (months with data, value range, comparison with the EU-27 distribution) to `data/global_transferability_test/india_no2_sanity_check.json`. Result: all 72 months returned data; India's monthly national mean ranged from 2.27 × 10⁻⁵ to 4.16 × 10⁻⁵ mol/m² (median 3.32 × 10⁻⁵), with no negative months, and all 72 values fall inside the 5th–95th percentile range of EU-27 country-months (1.34 × 10⁻⁵ to 6.34 × 10⁻⁵ mol/m²). This shows the data pipeline runs outside Europe; it is not a causal analysis.

*(An earlier version used a rectangular bounding box, 68–97.5° E / 6–37.5° N, which also covered neighbouring countries and ocean. That output is superseded.)*

---

## Architecture

```text
 DATA SOURCES                    PREPROCESSING                 MODELLING                   PRESENTATION
 ─────────────                   ─────────────                 ─────────                   ────────────
 Sentinel-5P (NO₂)     ┐
 CGLS (NDVI)           │
 ERA5 (Climate)        │         Per-dataset          Country-month        Difference-in-
 Eurostat / World      ├────▶    download_*.py   ─▶    master datasets ─▶  Differences model   ─▶   outputs/plots/
 Bank (GDP)             │        process_*.py          (data/)             (causal_inference*.py)     (maps & charts)
 ESA WorldCover        │         *_stats.py                                Placebo test                    │
 Copernicus DEM        │                                                   Event-study                     ▼
 GISCO / GADM          │                                                   Cluster-robust SEs      Streamlit dashboard
 (boundaries)          │                                                   Robustness checks        (dashboard/app.py)
 EUR-Lex (policy)      ┘                                                                                    │
                                                                                                              ▼
                                                                                                       Research Paper
```

Each stage is a separate script and every number in the paper is produced by a script in this repository. The repository also keeps superseded scripts from earlier stages of the project (marked as such in their headers); the current run order is below.

## Reproducibility

- **Environment**: Python 3.10+. Most dependencies install via `requirements.txt`; `geopandas`/`rasterio`/`GDAL` are easiest installed via `conda` (`conda install -c conda-forge geopandas rasterio gdal`) if the `pip` install fails on your platform.
- **Credentials**: Sentinel Hub (`SH_CLIENT_ID`, `SH_CLIENT_SECRET`) and Copernicus CDS access need free accounts; credentials go in a local `.env` file (never committed). The World Bank and Eurostat APIs need no credentials.
- **Current run order (NO₂/NDVI → models → figures):**
  1. `download_no2_sentinelhub.py` (daily Process API rasters → resumable daily log → `no2_stats_monthly_mean_36.json`), `download_ndvi_sentinelhub.py` (→ `ndvi_stats_monthly_mean_36.json`); `download_no2_gridded.py` keeps every daily 0.1° raster (→ `data/earth_observation/no2/gridded/`, not in the repository because of its size) and `analyse_no2_grid_baseline.py` runs the pixel-level check on it; `diagnose_sentinelhub.py` checks which Sentinel Hub endpoints currently work; `check_s5p_processor_versions.py` checks which TROPOMI processor versions the NO₂ values come from
  2. Climate/GDP inputs: `download_era5.py` → `unzip_era5.py` → `process_era5.py` → `era5_regional_stats.py` + `era5_regional_stats_control_expansion.py`; `download_eurostat_gdp.py` → `process_eurostat.py` → `apply_eu27_filter.py`; `download_gdp_control_countries.py` + `download_gdp_control_expansion.py`; robustness controls: `download_era5_wind_blh.py` (→ `data/era5_wind_blh_country_monthly.csv`), `data/covid/oxcgrt_stringency_national.csv` (Oxford stringency index)
  3. `master_merge_control.py` → `data/master_dataset_control.csv`
  4. `causal_inference_final_did.py`, `causal_inference_ndvi.py`, `causal_inference_event_study.py`, `causal_inference_robustness_checks.py`, `causal_inference_identification_checks.py`, `synthetic_control.py`, `spatial_autocorrelation.py`; historical single-cohort models: `causal_inference_initial_model.py`, `causal_inference_placebo.py`, `causal_inference.py`
  5. Figures: `map_*.py`, `plot_*.py`, `build_interactive_maps.py`, `build_maps_plots_pdf.py`; dashboard: `dashboard/app.py`
- Superseded scripts kept for the record: `run_pipeline.py`/`download_no2.py`/`extract_no2.py` (OData + HARP Level-2 test pipeline), `download_*_control_expansion.py` for NO₂/NDVI (single-mosaic acquisition), `master_merge.py`, `master_merge_control_expanded.py`.
- **Full audit trail**: every fix, bug, and methodology change made after the first working version — including this project's cluster-robust standard error correction and the NDVI re-analysis — is logged chronologically in the Development Log, so any reported number can be traced back to the change that produced it.

---

## Repository Structure

```text
GPIE/
├── dashboard/                  # Streamlit dashboard (11 pages)
├── data/                       # Processed datasets and master merge files
│   └── earth_observation/      # Per-dataset acquisition/processing outputs
├── outputs/
│   ├── plots/                  # Final generated maps and charts
│   └── interactive/            # Hoverable/zoomable HTML maps (build_interactive_maps.py)
├── archive/                    # Dev-time scratch/inspection/smoke-test scripts, not part of the pipeline
├── GPIE_Research_Paper.md      # Formal academic research paper
├── GPIE_Development_Log.md     # Full technical development log (debugging & iteration history)
├── download_*.py               # Dataset acquisition scripts
├── process_*.py                # Dataset processing scripts
├── *_stats.py                  # Statistical processing utilities
├── s5p_process_daily.py        # NO₂: daily Process API rasters → country monthly means
├── sentinelhub_stats.py        # NDVI: Statistical API monthly-mean request builder
├── causal_inference*.py        # Main, placebo & event-study models
├── map_*.py                    # Map generation scripts
└── country_boundaries.py       # Shared EU-27 + control-group boundary loader
```

## Tech Stack

Python · pandas · geopandas · statsmodels · scipy · libpysal/esda · matplotlib · Plotly · folium · Streamlit · Sentinel Hub API · Copernicus Climate Data Store · Eurostat API · World Bank API

## Data Sources

| Dataset | Provider |
|---|---|
| NO₂ (Sentinel-5P) | ESA / Copernicus, via Sentinel Hub |
| NDVI (CGLS) | Copernicus Land Monitoring Service |
| Climate (ERA5) | ECMWF / Copernicus Climate Data Store |
| GDP | Eurostat (EU-27), World Bank (control group) |
| Land Cover | ESA WorldCover |
| Elevation | Copernicus DEM GLO-30 |
| Boundaries | Eurostat GISCO (NUTS), GADM |
| Policy Records | EUR-Lex |

## Running Locally

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

---

*This project's full development process — including debugging history, methodology iterations, and every technical decision — is documented in the Development Log for full transparency and reproducibility.*
