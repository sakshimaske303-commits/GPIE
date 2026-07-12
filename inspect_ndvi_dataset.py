import json
import requests
from auth_clms import get_clms_access_token

SEARCH_URL = "https://land.copernicus.eu/api/@search"


def inspect_dataset():
    access_token = get_clms_access_token()
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    params = {
        "UID": "68a831a3eb7e4a568d3132ef71161387",
        "metadata_fields": ["dataset_download_information", "dataset_full_format"],
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)
    data = response.json()

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    inspect_dataset()