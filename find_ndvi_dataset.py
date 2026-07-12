import requests
from auth_clms import get_clms_access_token

SEARCH_URL = "https://land.copernicus.eu/api/@search"


def find_ndvi_dataset():
    """
    Searches the CLMS catalogue for the NDVI 300m V3 dataset and
    returns its UID and DatasetDownloadInformationID.
    """
    access_token = get_clms_access_token()
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    params = {
        "portal_type": "DataSet",
        "metadata_fields": ["UID", "dataset_full_format", "dataset_download_information"],
        "SearchableText": "NDVI 300m",
        "b_size": 50,
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"Search failed ({response.status_code}): {response.text}")

    data = response.json()

    print(f"Found {data.get('items_total', 0)} matching datasets:\n")

    for item in data.get("items", []):
        print(f"Title: {item.get('title')}")
        print(f"UID: {item.get('UID')}")
        download_info = item.get("dataset_download_information", {}).get("items", [])
        for info in download_info:
            print(f"  -> DownloadInfoID: {info.get('@id')} | format: {info.get('full_format')} | path: {info.get('full_path')}")
        print()


if __name__ == "__main__":
    find_ndvi_dataset()