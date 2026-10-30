# data/ — what each file is and where it comes from

Three kinds of file sit here: the **panel** the models read, the **results** the models write
(the numbers in the paper come from these), and per-dataset folders in `earth_observation/`.
Files are not moved into sub-folders because the scripts and the dashboard read them at these paths.

## The panel

| File | What it is | Made by | Read by |
| --- | --- | --- | --- |
| `master_dataset_control.csv` | **Current panel:** NO₂, weather and GDP for 36 countries x 72 months (2019–2024) | `src/master_merge_control.py` | every model, the maps, the dashboard |
| `master_dataset.csv` | Original EU-27-only panel from the first version | `archive/superseded_scripts/master_merge.py` | `src/causal_inference_placebo.py`, dashboard "About the Data" page |
| `master_dataset_control_expanded.csv` | **Superseded.** Expanded panel built from end-of-month NO₂ snapshots; do not use for new work | `archive/superseded_scripts/master_merge_control_expanded.py` | `archive/superseded_scripts/causal_inference_expanded_control.py` only |
| `era5_wind_blh_country_monthly.csv` | ERA5 wind speed and boundary-layer height per country and month | `src/download_era5_wind_blh.py` | `src/causal_inference_identification_checks.py` |
| `covid/oxcgrt_stringency_national.csv` | Oxford COVID-19 stringency index, national (see `Data_Sources.md`) | downloaded | `src/causal_inference_identification_checks.py` |
| `eea_station_monthly.csv` | EEA ground-station NO₂, monthly | `src/validate_eea_stations.py` (from the airbase download) | `src/validate_eea_stations.py` |

## Results behind the paper

| File | Made by | In the paper |
| --- | --- | --- |
| `identification_checks.json` | `src/causal_inference_identification_checks.py` | Table 2, Sections 5.1–5.3 |
| `grid_baseline_checks.json` | `src/analyse_no2_grid_baseline.py` | Tables 3–4, Figures 4–5 |
| `stress_tests.json`, `placebo_assignments.csv` | `src/causal_inference_stress_tests.py` | Figure 3, Table 5, Figure 6 |
| `additional_checks.json` | `src/causal_inference_additional_checks.py` | Table 4 |
| `positive_control.json` | `src/causal_inference_positive_control.py` | Table 6, Figure 7 |
| `real_gdp_checks.json` | `src/causal_inference_real_gdp.py` | real-GDP rows of Tables 2 and 4 |
| `eea_validation.json` | `src/validate_eea_stations.py` | Table 7, Section 5.7 |
| `spatial_autocorrelation_summary.json`, `moran_local_clusters.csv`, `moran_residuals_by_month.csv`, `country_no2_for_moran.geojson` | `src/spatial_autocorrelation.py` | Moran's I, Section 5.1 |

## Supplementary results (not in the paper)

| File | Made by |
| --- | --- |
| `robustness_checks.json` | `src/causal_inference_robustness_checks.py` |
| `synthetic_control_results.csv`, `synthetic_control_summary.json` | `src/synthetic_control.py` |
| `s5p_processor_check.json` | `src/check_s5p_processor_versions.py` |
| `global_transferability_test/` | `src/test_india_transferability.py` |
| `policy_database/` | an early list of EU policy documents; no current script reads it |

## earth_observation/

One folder per dataset (`no2`, `ndvi`, `climate`, `economy`, `dem`, `land_cover`, `population`,
`boundaries`). Each keeps its downloaded files in `raw/` and the country-level tables the merge
reads in `final/`. Large raw files and the 0.1° NO₂ grid are not in the repository; `.gitignore`
lists them and `Data_Sources.md` says where each comes from.
