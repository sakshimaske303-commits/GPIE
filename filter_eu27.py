import pandas as pd
from get_eu_country_list import get_eu_country_codes

# ISO3 -> ISO2 mapping (same as used in NDVI/Population modules)
ISO3_TO_ISO2 = {
    "AUT": "AT", "BEL": "BE", "BGR": "BG", "HRV": "HR", "CYP": "CY",
    "CZE": "CZ", "DNK": "DK", "EST": "EE", "FIN": "FI", "FRA": "FR",
    "DEU": "DE", "GRC": "EL", "HUN": "HU", "IRL": "IE", "ITA": "IT",
    "LVA": "LV", "LTU": "LT", "LUX": "LU", "MLT": "MT", "NLD": "NL",
    "POL": "PL", "PRT": "PT", "ROU": "RO", "SVK": "SK", "SVN": "SI",
    "ESP": "ES", "SWE": "SE"
}


def get_eu27_iso2_list():
    """
    Returns the list of EU-27 country codes in ISO2 (NUTS-0) format,
    the consistent scope used across all project datasets.
    """
    iso3_codes = get_eu_country_codes()
    return [ISO3_TO_ISO2[c] for c in iso3_codes if c in ISO3_TO_ISO2]


if __name__ == "__main__":
    codes = get_eu27_iso2_list()
    print(f"EU-27 ISO2 codes ({len(codes)}):")
    print(codes)