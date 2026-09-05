# ==========================================
# GPIE Configuration File
# ==========================================

# ------------------------------------------
# Project Information
# ------------------------------------------

PROJECT_NAME = "Green Policy Intelligence Engine"

DEMONSTRATION_CASE = "European Green Deal"

# ------------------------------------------
# Study Area
# ------------------------------------------

STUDY_AREA = "European Union"

# ------------------------------------------
# Temporal Extent
# ------------------------------------------
# NOTE: these four values (and START_DATE/END_DATE below) are leftover from
# this project's original single-month test run and were never updated to
# match the real study period. They are NOT the actual study window - the
# final analysis covers January 2019 to December 2024. The final NO2
# acquisition script (download_no2_sentinelhub.py) does not read these
# values at all; it loops over `range(2019, 2025)` directly. Kept here only
# because a few of the older, superseded acquisition scripts still import
# them for a one-off test run - do not treat this as the project's live
# configuration for the study period.

STUDY_START_YEAR = 2019
STUDY_START_MONTH = 1

STUDY_END_YEAR = 2019
STUDY_END_MONTH = 1

# Kept for backward compatibility with scripts that import these directly

START_DATE = "2019-01-01T00:00:00.000Z"

END_DATE   = "2019-01-31T23:59:59.999Z"

# ------------------------------------------
# Europe Bounding Box (Catalogue Discovery)
# ------------------------------------------

MIN_LON = -31.5
MIN_LAT = 27.5

MAX_LON = 35.0
MAX_LAT = 71.5

EU_BBOX_WKT = (
    "POLYGON(("
    "-31.5 27.5,"
    "35.0 27.5,"
    "35.0 71.5,"
    "-31.5 71.5,"
    "-31.5 27.5"
    "))"
)

# ------------------------------------------
# Sentinel-5P Product Configuration
# ------------------------------------------

COLLECTION = "SENTINEL-5P"

PRODUCT = "NO2"

PRODUCT_VERSION = "RPRO"

QUALITY_THRESHOLD = 0.75

# ------------------------------------------
# API Configuration
# ------------------------------------------

CATALOG_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

DOWNLOAD_URL = "https://download.dataspace.copernicus.eu/odata/v1/Products"

# ------------------------------------------
# Download Configuration
# ------------------------------------------

TOP = 1000

BATCH_TYPE = "WEEKLY"

# ------------------------------------------
# Folder Structure
# ------------------------------------------

RAW_DATA_DIR = "data/earth_observation/no2/raw"

PROCESSED_DATA_DIR = "data/earth_observation/no2/processed"

FINAL_DATA_DIR = "data/earth_observation/no2/final"