import json
from download_nuts import download_nuts_country_boundaries, NUTS_RAW_DIR
import os

# ------------------------------------------
# Official EU-27 member states (ISO2 -> ISO3 mapping)
# Note: Greece uses 'EL' in NUTS/Eurostat, not 'GR'
# ------------------------------------------
EU27_ISO2_TO_ISO3 = {
    "AT": "AUT", "BE": "BEL", "BG": "BGR", "HR": "HRV", "CY": "CYP",
    "CZ": "CZE", "DK": "DNK", "EE": "EST", "FI": "FIN", "FR": "FRA",
    "DE": "DEU", "EL": "GRC", "HU": "HUN", "IE": "IRL", "IT": "ITA",
    "LV": "LVA", "LT": "LTU", "LU": "LUX", "MT": "MLT", "NL": "NLD",
    "PL": "POL", "PT": "PRT", "RO": "ROU", "SK": "SVK", "SI": "SVN",
    "ES": "ESP", "SE": "SWE"
}


def get_eu_country_codes():
    """
    Reads the downloaded NUTS country-level GeoJSON and extracts
    ISO3 country codes for the 27 EU member states only.
    Returns a list of ISO3 codes (e.g. ["DEU", "FRA", "ITA", ...]).
    """
    filepath = os.path.join(NUTS_RAW_DIR, "NUTS_LEVL_0_2024_4326.geojson")

    if not os.path.exists(filepath):
        download_nuts_country_boundaries()

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    found_iso2 = set()

    for feature in data["features"]:
        props = feature["properties"]
        nuts_id = props.get("NUTS_ID")
        if nuts_id:
            found_iso2.add(nuts_id)

    iso3_codes = []
    for iso2, iso3 in EU27_ISO2_TO_ISO3.items():
        if iso2 in found_iso2:
            iso3_codes.append(iso3)
        else:
            print(f"Warning: {iso2} ({iso3}) not found in NUTS data")

    return sorted(iso3_codes)


if __name__ == "__main__":
    codes = get_eu_country_codes()
    print(f"Found {len(codes)} EU-27 country codes:")
    print(codes)