# GPIE configuration

# Project information

PROJECT_NAME = "Green Policy Intelligence Engine"

DEMONSTRATION_CASE = "European Green Deal"

# Study area

STUDY_AREA = "European Union"

# Study window: January 2019 - December 2024 (72 months).
# My Sentinel Hub scripts loop over range(2019, 2025) directly and do not read these.

STUDY_START_YEAR = 2019
STUDY_START_MONTH = 1

STUDY_END_YEAR = 2024
STUDY_END_MONTH = 12

# One-month window. Only my old OData/HARP test pipeline (run_pipeline.py) uses it.
START_DATE = "2019-01-01T00:00:00.000Z"

END_DATE   = "2019-01-31T23:59:59.999Z"

# Europe bounding box

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

# Sentinel-5P product

COLLECTION = "SENTINEL-5P"

PRODUCT = "NO2"

PRODUCT_VERSION = "RPRO"

QUALITY_THRESHOLD = 0.75

# API

CATALOG_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

DOWNLOAD_URL = "https://download.dataspace.copernicus.eu/odata/v1/Products"

# Download

TOP = 1000

BATCH_TYPE = "WEEKLY"

# Folders

RAW_DATA_DIR = "data/earth_observation/no2/raw"

PROCESSED_DATA_DIR = "data/earth_observation/no2/processed"

FINAL_DATA_DIR = "data/earth_observation/no2/final"