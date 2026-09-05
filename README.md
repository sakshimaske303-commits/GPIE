# GPIE — Green Policy Intelligence Engine

[![EarthArXiv](https://img.shields.io/badge/EarthArXiv-Preprint-B7410E.svg)](https://eartharxiv.org/repository/view/14824/) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21756661.svg)](https://doi.org/10.5281/zenodo.21756661)

**Independently verifying environmental policy claims using satellite data.**

GPIE is a geospatial causal-inference framework that tests whether the European Green Deal's flagship legislation — the **European Climate Law** (effective 30 June 2021) — produced a measurable, statistically distinguishable reduction in NO₂ pollution across the EU-27, using satellite observations rather than self-reported government claims.

Built on a **"Trust, But Verify"** research philosophy: policy claims are treated as hypotheses to be independently tested, not facts to be assumed.

---

## Project Documentation

| Document | What's Inside |
|---|---|
| [Executive Summary](./GPIE_Executive_Summary.pdf) | One-page snapshot — question, method, headline finding, robustness checklist, and links (fastest overview) |
| [Research Paper](./GPIE_Research_Paper.md) | Formal academic paper — literature review, statistical methodology, results, discussion |
| [Development Log](./GPIE_Development_Log.md) | Full technical development log — every bug, debugging session, and methodology iteration |

---

## Live Dashboard

**[View the interactive dashboard →](https://f5cf6fijj9gm564r6aapt6.streamlit.app/)**

---

## Interactive Maps

Hoverable, zoomable versions of every map in this project — same underlying data as the static figures, built with `folium`/`plotly` instead of `matplotlib`. Also embedded directly in the dashboard's **Interactive Maps** page.

| Map | Link |
|---|---|
| Study Design: Treatment vs. Control | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/control_group_map.html) |
| NO₂ Concentration | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/no2_map.html) |
| Vegetation Health (NDVI) | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/ndvi_map.html) |
| Temperature | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/climate_map.html) |
| GDP | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/gdp_map.html) |
| Moran's I Spatial Clusters | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/moran_lisa_map.html) |
| Event-Study Plot | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/event_study.html) |
| Synthetic Control Gap | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/synthetic_control.html) |
| Explore Trends by Country | [Open →](https://sakshimaske303-commits.github.io/GPIE/outputs/interactive/explore_trends.html) |

Built by `build_interactive_maps.py`.

---

## What This Project Does

- Stores and analyses **8 independent datasets** across **36 countries** (EU-27 + a deliberately constructed 9-country non-EU control group: UK, Norway, Switzerland, Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, Serbia), 2019–2024
- Conducts a well-developed **Difference-in-Differences** causal inference model to separate the Climate Law's specific effect from the rest of European pollution
- Performs a placebo test, external control-group construction, quarterly event study, baseline-pollution heterogeneity check, augmented synthetic control and Moran's I spatial autocorrelation diagnostic
- Reports an honest, rigorously established finding — a pooled null result that is consistent with a statistically significant, tightly defined, concentrated effect
- Presents all of it through a series of **12 publication-quality maps**, **9 hoverable interactive maps**, and an interactive Streamlit dashboard

## Key Finding

No statistically distinguishable pooled, EU-wide NO₂ reduction was identified at the conventional 5% level when compared to a 9-country non-EU control group (coefficient = −2.22 × 10⁻⁶; p = 0.101; cluster-robust standard errors by country). However, a heterogeneity check reveals a statistically significant reduction concentrated in the fourteen member states with the higher background pollution levels (coefficient = −5.46 × 10⁻⁶, p = 0.003), supported by the event-study analysis (four quarters with a significant reduction, all negative, clustering in Q2/Q3 of 2022–2024). A methodologically distinct approach, the augmented synthetic control (weighted pool of 7 countries), also estimates the near-zero, same-sign *pooled* estimate, and a Moran's I spatial-autocorrelation test confirms that raw NO₂ is strongly spatially clustered as expected for a cross-border pollutant (I = 0.570, p = 0.001), but that the DiD's own residuals are not significantly spatially clustered (I = 0.069, p = 0.135) — the country and month fixed effects capture the bulk of the spatial clustering. The dashboard's Methodology page provides the complete methodology, including the initial, later-invalidated positive result, and the placebo test that revealed it was unreliable.

The same two-group, cluster-robust design was used for the secondary outcome of NDVI (vegetation health); this was previously evaluated only with the original version - now invalidated - of this design, and was used to obtain a coefficient of −0.0145 (p = 0.007), showing a statistically significant relative drop in NDVI in the EU-27 nations compared to the control group. This is reported as an honest, exploratory secondary finding, not as evidence the Climate Law itself affected vegetation health.

## Transferability Validation

GPIE's original design goal was a methodology that would be transferable globally, not just limited regionally to the EU-27. To confirm this, the project's NO₂ acquisition pipeline was tested — using the same Sentinel Hub Statistical API infrastructure and evalscript logic as the EU-27 study, with no modification to the core acquisition logic (a separate script defines India's own geometry and request handling) — on **India** (2019–2024).

All 6 years successfully acquired, with physically realistic NO₂ values in the same range as reported from the EU-27 dataset. This validates that the framework's data-acquisition architecture is portable to another country/region — a standalone proof-of-concept, not a comparative analysis. See `test_india_transferability.py`.

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

Each stage is a separate, independently re-runnable script — there is no hidden manual step between raw acquisition and the final published figures; every number in the paper traces back to a script in this repository.

## Reproducibility

- **Environment**: Python 3.10+. Most dependencies install via `requirements.txt`; `geopandas`/`rasterio`/`GDAL` are easiest installed via `conda` (`conda install -c conda-forge geopandas rasterio gdal`) if the `pip` install fails on your platform.
- **Credentials**: Sentinel Hub, Copernicus CDS, and World Bank API access require free account credentials, stored in a local `.env` file (never committed — see `.env.example` if present, or the acquisition scripts' docstrings for the expected variable names).
- **Run order**: `download_*.py` (per dataset) → `process_*.py` (standardization) → `*_stats.py` (country-month aggregation) → `causal_inference*.py` (models) → `map_*.py` (figures) → `dashboard/app.py` (interactive presentation). Every intermediate output is written to `data/` or `outputs/plots/` so any stage can be re-run independently without repeating earlier stages.
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
├── causal_inference*.py        # Main, placebo & event-study models
├── map_*.py                    # Map generation scripts
└── country_boundaries.py       # Shared EU-27 + control-group boundary loader
```

## Tech Stack

Python · pandas · geopandas · statsmodels · matplotlib · Plotly · Streamlit · Sentinel Hub API · Copernicus Climate Data Store · Eurostat API · World Bank API

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
