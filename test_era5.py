from download_era5 import download_era5_year
import cdsapi
client = cdsapi.Client()
download_era5_year(client, 2019)