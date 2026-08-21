# NOTE: used by run_pipeline.py; the project's final NO2 dataset traces to
# download_no2_sentinelhub.py instead — see the note at the top of
# run_pipeline.py.
import requests
import os
import time
from download_utils import (
    is_complete_file,
    remove_file,
)

from auth import get_access_token
from search_products import search_products
from config import (
    DOWNLOAD_URL,
    RAW_DATA_DIR,
)


def download_single_product(product, headers):
    filename = product["Name"]
    filepath = os.path.join(RAW_DATA_DIR, filename)
    expected_size = int(product["ContentLength"])

    if is_complete_file(filepath, expected_size):
        print(f"Skipping (already complete): {filename}")
        return True

    if os.path.exists(filepath):
        remove_file(filepath)

    product_id = product["Id"]
    url = f"{DOWNLOAD_URL}({product_id})/$value"

    max_retries = 3

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=300)

            if response.status_code != 200:
                print(f"Attempt {attempt}: Failed ({response.status_code}) for {filename}")
                time.sleep(5)
                continue

            with open(filepath, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

            if is_complete_file(filepath, expected_size):
                print(f"Downloaded successfully: {filename}")
                return True
            else:
                print(f"Attempt {attempt}: Incomplete download for {filename}, retrying...")
                remove_file(filepath)
                time.sleep(5)

        except Exception as e:
            print(f"Attempt {attempt}: Error downloading {filename}: {e}")
            time.sleep(5)

    print(f"FAILED after {max_retries} attempts: {filename}")
    return False


def download_product(start_date, end_date):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    products = search_products(start_date, end_date)

    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    successful_files = []

    for product in products:
        success = download_single_product(product, headers)
        if success:
            filepath = os.path.join(RAW_DATA_DIR, product["Name"])
            successful_files.append(filepath)

    print(f"Download batch complete: {len(successful_files)}/{len(products)} succeeded")
    return successful_files


def main():
    from config import START_DATE, END_DATE
    download_product(START_DATE, END_DATE)


if __name__ == "__main__":
    main()