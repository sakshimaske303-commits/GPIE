import json
from shapely.geometry import shape, mapping, box

NUTS_BOUNDARY_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"

GADM_PATHS = {
    "UK": "data/earth_observation/boundaries/raw/gadm41_GBR_0.json",
    "NO": "data/earth_observation/boundaries/raw/gadm41_NOR_0.json",
    "CH": "data/earth_observation/boundaries/raw/gadm41_CHE_0.json",
}

# I use 2-letter NUTS-style codes for these even though their boundaries come from GADM.
CONTROL_COUNTRIES = ["UK", "NO", "CH"]

# The other six control countries. Their geometry is in the NUTS-0 file, not GADM.
EXPANSION_CONTROL_COUNTRIES = ["IS", "AL", "BA", "ME", "MK", "RS"]


def load_geometry_from_nuts(nuts_id):
    with open(NUTS_BOUNDARY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for feature in data["features"]:
        if feature["properties"].get("NUTS_ID") == nuts_id:
            return shape(feature["geometry"])

    return None


def load_geometry_from_gadm(country_code):
    path = GADM_PATHS.get(country_code)
    if path is None:
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # A GADM level-0 file has one feature for the whole country.
    geom = data["features"][0]["geometry"]
    return shape(geom)


def load_country_geometry(country_code, clip_to_bbox=None):
    """Country geometry from GADM (UK, NO, CH) or NUTS (all others), optionally clipped to a box."""
    if country_code in CONTROL_COUNTRIES:
        geom = load_geometry_from_gadm(country_code)
    else:
        geom = load_geometry_from_nuts(country_code)

    if geom is None:
        return None

    if clip_to_bbox:
        min_lon, min_lat, max_lon, max_lat = clip_to_bbox
        bbox_geom = box(min_lon, min_lat, max_lon, max_lat)
        geom = geom.intersection(bbox_geom)

        # Clipping can leave stray points or lines. Sentinel Hub only accepts polygons,
        # so I keep only the polygon parts.
        if geom.geom_type == "GeometryCollection":
            from shapely.geometry import MultiPolygon
            polygons = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
            geom = MultiPolygon([p for poly in polygons for p in (poly.geoms if poly.geom_type == "MultiPolygon" else [poly])])

    return mapping(geom)


def get_all_country_codes():
    """All 36 study countries: EU-27 plus my 9 control countries."""
    from filter_eu27 import get_eu27_iso2_list
    eu27 = get_eu27_iso2_list()
    return eu27 + CONTROL_COUNTRIES + EXPANSION_CONTROL_COUNTRIES