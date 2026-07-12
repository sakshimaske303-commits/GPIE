import os
import cdsapi

ERA5_RAW_DIR = "data/earth_observation/climate/raw"

DATASET = "reanalysis-era5-single-levels-monthly-means"

VARIABLES = ["2m_temperature", "total_precipitation"]

# [North, West, South, East] - matches project's European Bounding Box
AREA = [71.5, -31.5, 27.5, 35.0]

STUDY_START_YEAR = 2019
STUDY_END_YEAR = 2024


def download_era5_year(client, year):
    """
    Downloads monthly-averaged ERA5 temperature and precipitation
    for all 12 months of a given year, for the European bounding box.
    Skips if already downloaded. Returns True on success.
    """
    os.makedirs(ERA5_RAW_DIR, exist_ok=True)
    filename = f"era5_monthly_{year}.nc"
    filepath = os.path.join(ERA5_RAW_DIR, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print(f"Skipping (already exists): {filename}")
        return True

    request = {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": VARIABLES,
        "year": [str(year)],
        "month": [f"{m:02d}" for m in range(1, 13)],
        "time": ["00:00"],
        "area": AREA,
        "data_format": "netcdf",
    }

    print(f"Requesting ERA5 data for {year}... (this may take a while, CDS queues the job)")

    try:
        client.retrieve(DATASET, request, filepath)
        print(f"Downloaded successfully: {filename}")
        return True

    except Exception as e:
        print(f"Error downloading {year}: {e}")
        return False


def main():
    client = cdsapi.Client()

    for year in range(STUDY_START_YEAR, STUDY_END_YEAR + 1):
        download_era5_year(client, year)

    print("\nERA5 download batch complete.")


if __name__ == "__main__":
    main()