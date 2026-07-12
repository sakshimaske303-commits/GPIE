import os
import time
import requests
from datetime import datetime, timezone
from auth_clms import get_clms_access_token
from get_eu_country_list import get_eu_country_codes

NDVI_RAW_DIR = "data/earth_observation/ndvi/raw"

DATASET_UID = "68a831a3eb7e4a568d3132ef71161387"
DOWNLOAD_INFO_ID = "e4662555-eb53-4e45-a3d2-45f6eb044d85"

REQUEST_URL = "https://land.copernicus.eu/api/@datarequest_post"
STATUS_URL = "https://land.copernicus.eu/api/@datarequest_status_get"

# NUTS uses 2-letter ISO2 codes, not ISO3 - need the mapping back
ISO3_TO_ISO2 = {
    "AUT": "AT", "BEL": "BE", "BGR": "BG", "HRV": "HR", "CYP": "CY",
    "CZE": "CZ", "DNK": "DK", "EST": "EE", "FIN": "FI", "FRA": "FR",
    "DEU": "DE", "GRC": "EL", "HUN": "HU", "IRL": "IE", "ITA": "IT",
    "LVA": "LV", "LTU": "LT", "LUX": "LU", "MLT": "MT", "NLD": "NL",
    "POL": "PL", "PRT": "PT", "ROU": "RO", "SVK": "SK", "SVN": "SI",
    "ESP": "ES", "SWE": "SE"
}


def to_epoch_millis(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def submit_ndvi_request(access_token, year, nuts_code):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    payload = {
        "Datasets": [
            {
                "DatasetID": DATASET_UID,
                "DatasetDownloadInformationID": DOWNLOAD_INFO_ID,
                "OutputFormat": "Geotiff",
                "OutputGCS": "EPSG:4326",
                "NUTS": nuts_code,
                "TemporalFilter": {
                    "StartDate": to_epoch_millis(f"{year}-01-01"),
                    "EndDate": to_epoch_millis(f"{year}-12-31"),
                },
            }
        ]
    }

    response = requests.post(REQUEST_URL, headers=headers, json=payload)

    if response.status_code not in (200, 201):
        raise RuntimeError(f"Request failed ({response.status_code}): {response.text}")

    data = response.json()
    task_id = data["TaskIds"][0]["TaskID"]
    print(f"Submitted request: {nuts_code}, year {year}. Task ID: {task_id}")
    return task_id


def poll_and_download(access_token, task_id, year, nuts_code):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    os.makedirs(NDVI_RAW_DIR, exist_ok=True)
    filepath = os.path.join(NDVI_RAW_DIR, f"ndvi_300m_{year}_{nuts_code}.zip")

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print(f"Skipping (already exists): {os.path.basename(filepath)}")
        return True

    max_wait_minutes = 30
    waited = 0

    while waited < max_wait_minutes:
        response = requests.get(STATUS_URL, headers=headers, params={"TaskID": task_id})

        if response.status_code != 200:
            print(f"Status check failed ({response.status_code}): {response.text}")
            time.sleep(60)
            waited += 1
            continue

        status_data = response.json()
        task_status = status_data.get("Status")
        download_url = status_data.get("DownloadURL")

        print(f"[{nuts_code}, {year}] Status: {task_status}")

        if task_status == "Finished_ok" and download_url:
            file_response = requests.get(download_url, stream=True)
            with open(filepath, "wb") as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Downloaded: {os.path.basename(filepath)}")
            return True

        if task_status in ("Error", "Rejected", "Cancelled"):
            print(f"Task failed for {nuts_code}, {year}: {task_status}")
            print(status_data)
            return False

        time.sleep(60)
        waited += 1

    print(f"Timed out waiting for {nuts_code}, {year}")
    return False


def main():
    access_token = get_clms_access_token()
    iso3_codes = get_eu_country_codes()
    nuts_codes = [ISO3_TO_ISO2[c] for c in iso3_codes if c in ISO3_TO_ISO2]

    for year in range(2019, 2025):
        for nuts_code in nuts_codes:
            task_id = submit_ndvi_request(access_token, year, nuts_code)
            poll_and_download(access_token, task_id, year, nuts_code)


if __name__ == "__main__":
    main()