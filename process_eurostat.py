import json
import csv
import os

INPUT_PATH = "data/earth_observation/economy/raw/nama_10r_2gdp_2019_2024.json"
OUTPUT_PATH = "data/earth_observation/economy/final/gdp_by_country_year.csv"


def decode_jsonstat():
    """
    Decodes the JSON-stat 2.0 format into a flat, readable table:
    one row per (country, year) with the GDP value.
    """
    with open(INPUT_PATH, "r") as f:
        data = json.load(f)

    dims = data["dimension"]
    dim_order = data["id"]  # order in which dimensions combine, e.g. ['freq','unit','geo','time']
    sizes = data["size"]    # number of categories in each dimension, in the same order

    # Build ordered label lists for each dimension
    dim_categories = {}
    for dim_name in dim_order:
        category_index = dims[dim_name]["category"]["index"]
        # category_index maps label -> position; invert it to get position -> label
        ordered_labels = sorted(category_index.items(), key=lambda x: x[1])
        dim_categories[dim_name] = [label for label, _ in ordered_labels]

    geo_labels = dim_categories["geo"]
    time_labels = dim_categories["time"]

    values = data["value"]  # dict of {flat_index_str: value}

    results = []

    for flat_index_str, gdp_value in values.items():
        flat_index = int(flat_index_str)

        # Decode the flat index back into per-dimension indices
        remaining = flat_index
        indices = {}
        for dim_name in reversed(dim_order):
            size = sizes[dim_order.index(dim_name)]
            indices[dim_name] = remaining % size
            remaining //= size

        geo_code = geo_labels[indices["geo"]]
        year = time_labels[indices["time"]]

        unit_labels = dim_categories["unit"]
        unit_code = unit_labels[indices["unit"]]

        results.append({
            "geo": geo_code,
            "year": year,
            "unit": unit_code,
            "value": gdp_value,
        })

    return results


def save_csv(results):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["geo", "year", "unit", "value"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Saved {len(results)} records to {OUTPUT_PATH}")


if __name__ == "__main__":
    results = decode_jsonstat()
    save_csv(results)