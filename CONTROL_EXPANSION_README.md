# Control Group Expansion — Run Order

Adds Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, and Serbia to the control group, and re-fetches Norway's NO2 to fix its 29/72-month gap. Runs on my own machine — this sandbox has no network route to Sentinel Hub / World Bank.

## Setup

Drop these 6 files into the GPIE project root (same folder as `config.py`, `auth_sentinelhub.py`, etc.):

- `download_no2_control_expansion.py`
- `download_ndvi_control_expansion.py`
- `download_gdp_control_expansion.py`
- `era5_regional_stats_control_expansion.py`
- `master_merge_control_expanded.py`
- `causal_inference_expanded_control.py`

`.env` already has the Sentinel Hub credentials from the original run — nothing new to configure there.

## Run order

```
python download_no2_control_expansion.py
python download_ndvi_control_expansion.py
python download_gdp_control_expansion.py
python era5_regional_stats_control_expansion.py
python master_merge_control_expanded.py
python causal_inference_expanded_control.py
```

Steps 1–3 hit Sentinel Hub / World Bank, takes a few minutes (7 countries × 6 years each, 1 sec between requests). Step 4 only reads the already-downloaded `era5_processed_{year}.nc` grid files — no network call, just needs those files present locally from the original ERA5 download. Step 5 merges everything into `data/master_dataset_control_expanded.csv` (doesn't touch the original `master_dataset_control.csv`). Step 6 re-runs the DiD model on the expanded panel and prints the new coefficient/p-value/CI.

## What to paste back

The console output of step 6 (coefficient, p-value, 95% CI, N observations, country list) — that's what I need to update the paper, dashboard, and Zenodo description with the expanded-control-group result. If any step errors out, paste that too and I'll fix the script.

## Notes

- If step 4 says a `era5_processed_{year}.nc` file is missing for some year, that year's grid wasn't downloaded in the original run — tell me and I'll write a version that re-downloads just the missing year(s) instead of assuming full coverage.
- Norway's NO2 is fully re-fetched (not patched) in step 1 — cleaner than trying to fill only the missing months.
- I haven't touched `synthetic_control.py` yet — once the expanded panel's causal_inference results come back, I'll widen the SCM donor pool too (now that Norway's NO2 gap should be fixed, it may finally be usable as a donor along with the new countries).
