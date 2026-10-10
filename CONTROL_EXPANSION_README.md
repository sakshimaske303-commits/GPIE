# Control Group Expansion — Run Order

> **Current status:** this document is a historical record of how the control group was expanded from
> three to nine countries. The expansion scripts used Sentinel Hub's single-mosaic acquisition, so
> `data/master_dataset_control_expanded.csv` holds the superseded end-of-month NO₂ values and is **not**
> identical to `data/master_dataset_control.csv`. `causal_inference_expanded_control.py` therefore reproduces
> the superseded pooled estimate, not the current one. The current 36-country panel is built by
> `master_merge_control.py` (see "Superseded" below and the README's run order).
>
> The scripts named below now live in `archive/superseded_scripts/` (NO₂, NDVI, merge and model) and `src/` (GDP and ERA5); the commands keep their original form as a record.

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

- Norway's NO2 was fully re-fetched (not patched) in step 1. The re-fetch did not close its coverage gap at the time. With the later daily acquisition Norway misses only 4 months, and Norway and Iceland are back in the synthetic-control donor pool.

## Superseded (current acquisition path)

The expansion scripts above used Sentinel Hub's default SIMPLE mosaicking, so each "monthly" value was a single most-recent mosaic rather than a monthly mean. The current acquisition fetches all 36 countries in one pass with true monthly means:

```
python download_no2_sentinelhub.py      # -> no2_stats_monthly_mean_36.json
python download_ndvi_sentinelhub.py     # -> ndvi_stats_monthly_mean_36.json
python master_merge_control.py          # uses the *_monthly_mean_36.json files when present
```

The expansion scripts and their outputs are kept only as a historical record.
