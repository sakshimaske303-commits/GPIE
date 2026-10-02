# Control Group Expansion — Run Order

> **Update (post-expansion consolidation):** `master_merge_control.py` was later updated to build
> the full 9-country control panel directly, so `data/master_dataset_control.csv` and
> `data/master_dataset_control_expanded.csv` are now identical files. Step 5's note below ("doesn't
> touch the original master_dataset_control.csv") describes this expansion run as it happened at
> the time, but is no longer an accurate description of the current pipeline —
> `master_dataset_control.csv` now *is* the expanded, 9-country file, and `causal_inference_final_did.py`
> (which reads `master_dataset_control.csv`) and `causal_inference_expanded_control.py` (which reads
> `master_dataset_control_expanded.csv`) now run the identical model on identical data. The rest of
> this document is kept as a historical record of how the expansion was actually run.

Adds Iceland, Albania, Bosnia and Herzegovina, Montenegro, North Macedonia, and Serbia to the control group, and re-fetches Norway's NO2 to fix its 29/72-month gap. 

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

## Notes

- Norway's NO2 was fully re-fetched (not patched) in step 1. The re-fetch did not close its coverage gap, so Norway and Iceland stayed out of the synthetic-control donor pool.

## Superseded (current acquisition path)

The expansion scripts above used Sentinel Hub's default SIMPLE mosaicking, so each "monthly" value was a single most-recent mosaic rather than a monthly mean. The current acquisition fetches all 36 countries in one pass with true monthly means:

```
python download_no2_sentinelhub.py      # -> no2_stats_monthly_mean_36.json
python download_ndvi_sentinelhub.py     # -> ndvi_stats_monthly_mean_36.json
python master_merge_control.py          # uses the *_monthly_mean_36.json files when present
```

The expansion scripts and their outputs are kept only as a historical record.
