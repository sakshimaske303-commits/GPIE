import xarray as xr

files = [
    "data/earth_observation/climate/raw/era5_monthly_2019_extracted/data_stream-moda_stepType-avgua.nc",
    "data/earth_observation/climate/raw/era5_monthly_2019_extracted/data_stream-moda_stepType-avgad.nc",
]

for f in files:
    print(f"\n{'='*60}")
    print(f"FILE: {f}")
    print('='*60)
    ds = xr.open_dataset(f)
    print("Variables:", list(ds.data_vars))
    print(ds)