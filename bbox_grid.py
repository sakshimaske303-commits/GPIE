from config import MIN_LON, MIN_LAT, MAX_LON, MAX_LAT


def generate_bbox_grid(min_lon, min_lat, max_lon, max_lat, n_cols, n_rows):
    """
    Splits the given bounding box into an n_cols x n_rows grid.
    Returns a list of [north, east, south, west] boxes,
    in the format required by the CLMS BoundingBox parameter.
    """
    lon_step = (max_lon - min_lon) / n_cols
    lat_step = (max_lat - min_lat) / n_rows

    grid_cells = []

    for row in range(n_rows):
        for col in range(n_cols):
            west = min_lon + col * lon_step
            east = min_lon + (col + 1) * lon_step
            south = min_lat + row * lat_step
            north = min_lat + (row + 1) * lat_step

            grid_cells.append([north, east, south, west])

    return grid_cells


def main():
    grid = generate_bbox_grid(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT, n_cols=5, n_rows=5)
    print(f"Generated {len(grid)} grid cells")
    for i, cell in enumerate(grid):
        print(f"Cell {i}: {cell}")


if __name__ == "__main__":
    main()