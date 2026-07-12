import os
import logging
from datetime import datetime

from date_utils import generate_monthly_ranges
from download_no2 import download_product
from extract_no2 import preprocess_file
from download_utils import remove_file

from config import (
    STUDY_START_YEAR,
    STUDY_START_MONTH,
    STUDY_END_YEAR,
    STUDY_END_MONTH,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
)

# ------------------------------------------
# Logging Setup
# ------------------------------------------

os.makedirs("logs", exist_ok=True)

log_filename = f"logs/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

log = logging.getLogger(__name__)


def process_month(start_date, end_date, year, month):
    """
    Runs the full cycle for a single month:
    download -> preprocess -> delete raw files.
    """
    log.info(f"===== Starting month {year}-{month:02d} =====")

    try:
        downloaded_files = download_product(start_date, end_date)
    except Exception as e:
        log.error(f"Download stage failed for {year}-{month:02d}: {e}")
        return

    if not downloaded_files:
        log.warning(f"No files downloaded for {year}-{month:02d}. Skipping processing.")
        return

    monthly_output_dir = os.path.join(PROCESSED_DATA_DIR, f"{year}", f"{month:02d}")

    success_count = 0
    fail_count = 0

    for filepath in downloaded_files:
        log.info(f"Processing: {os.path.basename(filepath)}")

        result = preprocess_file(filepath, monthly_output_dir)

        if result:
            success_count += 1
            remove_file(filepath)
            log.info(f"Processed and cleaned up: {os.path.basename(filepath)}")
        else:
            fail_count += 1
            log.error(f"Processing FAILED, raw file kept: {os.path.basename(filepath)}")

    log.info(
        f"===== Finished month {year}-{month:02d}: "
        f"{success_count} succeeded, {fail_count} failed ====="
    )


def main():
    log.info("GPIE Pipeline Started")
    log.info(f"Study period: {STUDY_START_YEAR}-{STUDY_START_MONTH:02d} to {STUDY_END_YEAR}-{STUDY_END_MONTH:02d}")

    for start_date, end_date, year, month in generate_monthly_ranges(
        STUDY_START_YEAR, STUDY_START_MONTH, STUDY_END_YEAR, STUDY_END_MONTH
    ):
        process_month(start_date, end_date, year, month)

    log.info("GPIE Pipeline Completed")


if __name__ == "__main__":
    main()