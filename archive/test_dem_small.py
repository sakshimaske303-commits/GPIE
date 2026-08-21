from download_dem import download_dem_for_bbox

# Small test area: Netherlands region
download_dem_for_bbox(
    min_lon=3,
    min_lat=50,
    max_lon=7,
    max_lat=54
)