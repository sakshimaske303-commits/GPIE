import json
import rasterstats

WORLDCOVER_VRT = "data/earth_observation/land_cover/processed/worldcover_2021_500m.tif"
NUTS_BOUNDARY_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"
OUTPUT_PATH = "data/earth_observation/land_cover/final/landcover_stats_by_country.json"

# WorldCover class codes (from official legend)
CLASS_NAMES = {
    10: "Tree cover", 20: "Shrubland", 30: "Grassland",
    40: "Cropland", 50: "Built-up", 60: "Bare/sparse vegetation",
    70: "Snow and ice", 80: "Permanent water bodies",
    90: "Herbaceous wetland", 95: "Mangroves", 100: "Moss and lichen"
}


def compute_landcover_stats():
    """
    Computes land cover class percentages for each NUTS country region,
    reading directly from the VRT mosaic without materializing a full
    clipped raster (avoids the storage issue of a continent-wide 10m file).
    """
    print("Computing zonal statistics per NUTS region... (this will take a while)")

    stats = rasterstats.zonal_stats(
        NUTS_BOUNDARY_PATH,
        WORLDCOVER_VRT,
        categorical=True,
        geojson_out=True,
    )

    results = []
    for feature in stats:
        props = feature["properties"]
        nuts_id = props.get("NUTS_ID")

        class_counts = {k: v for k, v in props.items() if isinstance(k, int)}
        total_pixels = sum(class_counts.values()) if class_counts else 0

        percentages = {}
        for code, count in class_counts.items():
            class_name = CLASS_NAMES.get(code, f"class_{code}")
            percentages[class_name] = round((count / total_pixels) * 100, 2) if total_pixels else 0

        results.append({"NUTS_ID": nuts_id, "land_cover_percent": percentages})

    import os
    os.makedirs("data/earth_observation/land_cover/final", exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved land cover statistics: {OUTPUT_PATH}")


if __name__ == "__main__":
    compute_landcover_stats()