import os
import xarray as xr
import numpy as np

RAW_EXTRACTED_DIR = "data/earth_observation/climate/raw/era5_monthly_{year}_extracted"
PROCESSED_DIR = "data/earth_observation/climate/processed"


def process_era5_year(year):
    """
    Merges temperature and precipitation files for one year,
    converts units to human-readable form, and saves a combined file.
    """
    extract_dir = RAW_EXTRACTED_DIR.format(year=year)

    temp_file = os.path.join(extract_dir, "data_stream-moda_stepType-avgua.nc")
    precip_file = os.path.join(extract_dir, "data_stream-moda_stepType-avgad.nc")

    if not os.path.exists(temp_file) or not os.path.exists(precip_file):
        print(f"Missing extracted files for {year}, skipping.")
        return None

    ds_temp = xr.open_dataset(temp_file)
    ds_precip = xr.open_dataset(precip_file)

    # Drop CDS internal experiment-version marker, not needed for analysis
    if "expver" in ds_temp.coords:
        ds_temp = ds_temp.drop_vars("expver")
    if "expver" in ds_precip.coords:
        ds_precip = ds_precip.drop_vars("expver")

    # Temperature ("instantaneous") and precipitation ("accumulated") source
    # files carry slightly different internal timestamps for the same
    # calendar month (e.g. 00:00:00 vs 06:00:00). Left uncorrected, combining
    # them creates duplicate time steps (24 per year instead of 12) with
    # each step missing one of the two variables. Force precipitation onto
    # temperature's time index before combining, since both represent the
    # same monthly period.
    ds_precip = ds_precip.assign_coords(valid_time=ds_temp["valid_time"].values)

    # Convert temperature: Kelvin -> Celsius
    temp_celsius = ds_temp["t2m"] - 273.15
    temp_celsius.attrs["units"] = "degrees_C"

    # Convert precipitation: meters -> millimeters
    precip_mm = ds_precip["tp"] * 1000
    precip_mm.attrs["units"] = "mm"

    combined = xr.Dataset({
        "temperature_c": temp_celsius,
        "precipitation_mm": precip_mm,
    })

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    output_path = os.path.join(PROCESSED_DIR, f"era5_processed_{year}.nc")
    combined.to_netcdf(output_path)

    print(f"Processed {year}: saved to {output_path}")
    return output_path


def main():
    for year in range(2019, 2025):
        process_era5_year(year)


if __name__ == "__main__":
    main()