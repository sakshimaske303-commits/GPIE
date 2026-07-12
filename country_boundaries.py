import json
from shapely.geometry import shape, mapping, box

NUTS_BOUNDARY_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"

GADM_PATHS = {
    "UK": "data/earth_observation/boundaries/raw/gadm41_GBR_0.json",
    "NO": "data/earth_observation/boundaries/raw/gadm41_NOR_0.json",
    "CH": "data/earth_observation/boundaries/raw/gadm41_CHE_0.json",
}

# Control-group countries use a 2-letter code (consistent with NUTS convention)
# for use throughout the project, even though they're sourced from GADM.
CONTROL_COUNTRIES = ["UK", "NO", "CH"]


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

    # GADM level-0 files contain a single feature covering the whole country
    geom = data["features"][0]["geometry"]
    return shape(geom)


def load_country_geometry(country_code, clip_to_bbox=None):
    """
    Unified loader: tries NUTS first (EU-27 countries), falls back to
    GADM (control-group countries: UK, NO, CH).
    Optionally clips to a bounding box (same pattern used for France's
    overseas-territory fix in the original NDVI/NO2 acquisition).
    """
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

        # Intersection with a bounding box can occasionally produce a
        # GeometryCollection containing degenerate points or lines
        # alongside the actual polygon area (e.g. an island that only
        # touches the box edge). Sentinel Hub only accepts Polygon/
        # MultiPolygon geometry, so extract only the polygonal parts.
        if geom.geom_type == "GeometryCollection":
            from shapely.geometry import MultiPolygon
            polygons = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
            geom = MultiPolygon([p for poly in polygons for p in (poly.geoms if poly.geom_type == "MultiPolygon" else [poly])])

    return mapping(geom)


def get_all_country_codes():
    """Returns EU-27 codes plus the 3 control-group codes, for full acquisition loops."""
    from filter_eu27 import get_eu27_iso2_list
    eu27 = get_eu27_iso2_list()
    return eu27 + CONTROL_COUNTRIES