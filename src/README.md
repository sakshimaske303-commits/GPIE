# src/ — what each script does

All scripts sit in this one folder on purpose: many of them import each other by name
(for example `from country_boundaries import ...`), and `reproduce_paper.py` runs them as
`src/<name>.py`. Run every script from the repository root, because their file paths start
there (`python src/master_merge_control.py`).

The groups below are by job. Each script appears once, except `download_nuts.py` and `era5_regional_stats.py`, which also act as modules.

## 1. The paper pipeline (run in this order by `reproduce_paper.py`)

| Step | Script | Writes | Used in the paper |
| --- | --- | --- | --- |
| 1 | `master_merge_control.py` | `data/master_dataset_control.csv` | the country panel, 36 countries x 72 months |
| 2 | `causal_inference_identification_checks.py` | `data/identification_checks.json` | Table 2, Sections 5.1–5.3 |
| 3 | `analyse_no2_grid_baseline.py` | `data/grid_baseline_checks.json` | Tables 3–4, Figures 4–5 |
| 4 | `causal_inference_stress_tests.py` | `data/stress_tests.json`, `data/placebo_assignments.csv` | Figure 3, Table 5, Figure 6 |
| 5 | `causal_inference_additional_checks.py` | `data/additional_checks.json` | Table 4 (blocks, COVID exclusion) |
| 6 | `causal_inference_positive_control.py` | `data/positive_control.json` | Table 6, Figure 7 |
| 7 | `causal_inference_real_gdp.py` | `data/real_gdp_checks.json` | real-GDP rows of Tables 2 and 4 |
| 8 | `validate_eea_stations.py` | `data/eea_station_monthly.csv`, `data/eea_validation.json` | Table 7, Section 5.7 |
| 9 | `spatial_autocorrelation.py` | `data/spatial_autocorrelation_summary.json`, `data/moran_*.csv`, `data/country_no2_for_moran.geojson` | Moran's I, Section 5.1 |
| 10 | `map_control_group_highlight.py` | `outputs/plots/` | Figure 1 |
| 11 | `plot_block_event_study.py` | `outputs/plots/` | Figure 2 |

## 2. Shared modules (imported by other scripts: do not rename or move)

| Module | What it holds | Imported by |
| --- | --- | --- |
| `config.py` | study bounding box and shared settings | 11 scripts |
| `country_boundaries.py` | loads each country's outline (NUTS or GADM), country lists | 13 scripts |
| `s5p_process_daily.py` | daily Sentinel-5P NO₂ requests, masks, monthly pooling | 10 scripts |
| `auth_sentinelhub.py` | Sentinel Hub token from the local `.env` | 6 scripts |
| `auth_clms.py` | Copernicus Land Monitoring Service login | `download_ndvi.py`, `find_ndvi_dataset.py` |
| `sentinelhub_stats.py` | Statistical API helpers for monthly NDVI | `download_ndvi_sentinelhub.py` |
| `get_eu_country_list.py` | EU-27 member list | 3 scripts |
| `filter_eu27.py` | EU-27 ISO2 list | `apply_eu27_filter.py` |
| `download_nuts.py` | also used as a module for the NUTS boundary folder | `get_eu_country_list.py` |
| `era5_regional_stats.py` | also used as a module for country climate means | `era5_regional_stats_control_expansion.py` |

`causal_inference_identification_checks.py` (pipeline step 2) is also imported by five later scripts, and
`analyse_no2_grid_baseline.py` (step 3) by six.

## 3. Data acquisition

| Script | Gets |
| --- | --- |
| `download_no2_sentinelhub.py` | daily NO₂ rasters → country monthly means, 36 countries, 2019–2024 |
| `download_no2_gridded.py` | the same, kept as a monthly 0.1° grid (`no2_grid_monthly.npz`, not in the repository) |
| `download_ndvi_sentinelhub.py` | CGLS 300 m NDVI, monthly means for 36 countries |
| `download_ndvi.py` | NDVI through the CLMS service (earlier route) |
| `download_era5.py`, `unzip_era5.py` | ERA5 monthly climate |
| `download_era5_wind_blh.py` | ERA5 wind speed and boundary-layer height per country |
| `download_eurostat_gdp.py` | Eurostat GDP, EU-27 |
| `download_gdp_control_countries.py`, `download_gdp_control_expansion.py` | World Bank GDP for the comparison countries |
| `download_gdp_real.py` | real GDP per capita, one source for all 36 countries |
| `download_nuts.py`, `download_gadm.py` | country boundaries (GADM is not redistributed, so it is downloaded) |
| `download_dem.py`, `download_worldcover.py`, `download_population.py` | terrain, land cover, population |
| `find_ndvi_dataset.py` | looks up the NDVI dataset id |
| `check_s5p_processor_versions.py` | checks which TROPOMI processor versions the NO₂ values come from |
| `diagnose_sentinelhub.py` | tests which Sentinel Hub requests work, one change at a time |

## 4. Processing

| Script | Does |
| --- | --- |
| `process_era5.py`, `era5_regional_stats.py`, `era5_regional_stats_control_expansion.py` | climate rasters → country monthly means |
| `process_eurostat.py`, `apply_eu27_filter.py` | Eurostat GDP → one clean table |
| `process_dem.py`, `process_landcover.py`, `clip_landcover.py`, `resample_landcover.py`, `landcover_stats.py` | terrain and land-cover summaries per country |
| `process_population.py` | population per country |
| `flatten_no2.py`, `flatten_ndvi.py` | nested JSON results → flat tables |
| `bbox_grid.py` | splits the study box into request tiles |

## 5. Supplementary analyses (not in the paper)

| Script | What it is |
| --- | --- |
| `causal_inference_final_did.py` | the baseline two-group DiD |
| `causal_inference_robustness_checks.py` | early robustness checks on that baseline |
| `causal_inference_ndvi.py` | the same DiD with NDVI as the outcome |
| `causal_inference_event_study.py` | quarterly event study |
| `causal_inference_placebo.py` | single-cohort placebo on the original EU-27 panel |
| `synthetic_control.py` | synthetic control for the EU-27 |
| `test_india_transferability.py` | tries the NO₂ pipeline on India |

## 6. Figures and maps

| Script | Makes |
| --- | --- |
| `map_no2_choropleth.py`, `map_no2_before_after.py`, `map_no2_eu_vs_control_bar.py` | NO₂ maps and bar chart |
| `map_ndvi_choropleth.py`, `map_ndvi_before_after.py`, `map_ndvi_eu_vs_control_bar.py` | NDVI maps and bar chart |
| `map_climate_choropleth.py`, `map_dem_choropleth.py`, `map_gdp_choropleth.py`, `map_land_cover.py` | control-variable maps |
| `map_moran_lisa_clusters.py` | Local Moran's I clusters |
| `plot_event_study.py`, `plot_synthetic_control.py`, `plot_india_trend.py`, `plot_tropomi_example_day.py` | supplementary plots |
| `build_interactive_maps.py` | HTML versions of the maps in `outputs/interactive/` |
| `build_maps_plots_pdf.py` | `GPIE_Maps_and_Plots.pdf` |
