import json
import os

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.path import Path

NUTS_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"
GADM_PATHS = {
    "UK": "data/earth_observation/boundaries/raw/gadm41_GBR_0.json",
    "NO": "data/earth_observation/boundaries/raw/gadm41_NOR_0.json",
    "CH": "data/earth_observation/boundaries/raw/gadm41_CHE_0.json",
}
OUTPUT_PATH = "outputs/plots/control_group_design_map.png"

EU27_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
}
# UK/NO/CH come from separate GADM files; the rest have a NUTS_ID in the boundary geojson.
CONTROL_COUNTRIES_NUTS = {"IS", "AL", "BA", "ME", "MK", "RS"}
CONTROL_COUNTRIES = set(GADM_PATHS.keys()) | CONTROL_COUNTRIES_NUTS
# In the boundary file but not in my country panel. I show them in grey so Kosovo is not a blank hole.
OUTSIDE_PANEL = {"XK", "LI", "TR", "UA"}

BOUNDS = (-25, 34, 35, 72)


def ring_path(rings):
    """One compound path per polygon: outer ring anticlockwise, holes clockwise, so holes stay empty."""
    verts, codes = [], []
    for i, ring in enumerate(rings):
        ring = np.asarray(ring, dtype=float)[:, :2]
        area = 0.5 * np.sum(ring[:-1, 0] * ring[1:, 1] - ring[1:, 0] * ring[:-1, 1])
        if (i == 0 and area < 0) or (i > 0 and area > 0):
            ring = ring[::-1]
        verts.extend(ring.tolist())
        codes.extend([Path.MOVETO] + [Path.LINETO] * (len(ring) - 2) + [Path.CLOSEPOLY])
    return Path(verts, codes)


def geometry_paths(geometry):
    if geometry["type"] == "Polygon":
        return [ring_path(geometry["coordinates"])]
    return [ring_path(polygon) for polygon in geometry["coordinates"]]


def load_geometries():
    geoms = {}
    with open(NUTS_PATH, encoding="utf-8") as f:
        nuts_data = json.load(f)
    for feature in nuts_data["features"]:
        nid = feature["properties"].get("NUTS_ID")
        if nid in EU27_COUNTRIES or nid in CONTROL_COUNTRIES_NUTS or nid in OUTSIDE_PANEL:
            geoms[nid] = feature["geometry"]
    for country_code, path in GADM_PATHS.items():
        with open(path, encoding="utf-8") as f:
            geoms[country_code] = json.load(f)["features"][0]["geometry"]
    return geoms


def draw(ax, geometry, **style):
    for path in geometry_paths(geometry):
        ax.add_patch(mpatches.PathPatch(path, **style))


def make_map():
    os.makedirs("outputs/plots", exist_ok=True)
    geoms = load_geometries()

    fig, ax = plt.subplots(figsize=(13, 12))
    for code in sorted(OUTSIDE_PANEL):
        draw(ax, geoms[code], facecolor="#d9d9d9", edgecolor="#7f7f7f", linewidth=0.5)
    for code in sorted(EU27_COUNTRIES):
        draw(ax, geoms[code], facecolor="#2c7fb8", edgecolor="#1a1a1a", linewidth=0.6, alpha=0.85)
    for code in sorted(CONTROL_COUNTRIES):
        draw(ax, geoms[code], facecolor="#e34a33", edgecolor="#1a1a1a", linewidth=1.8, alpha=0.9)

    ax.annotate("Kosovo", xy=(20.9, 42.6), xytext=(23.6, 44.9), fontsize=10,
                arrowprops=dict(arrowstyle="-", color="#333333", lw=0.8),
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))

    ax.set_xlim(BOUNDS[0], BOUNDS[2])
    ax.set_ylim(BOUNDS[1], BOUNDS[3])
    ax.set_aspect(1 / np.cos(np.deg2rad((BOUNDS[1] + BOUNDS[3]) / 2)))   # as in a plain lon/lat map
    ax.set_axis_off()

    legend_patches = [
        mpatches.Patch(color="#2c7fb8", label="EU-27 (treated)"),
        mpatches.Patch(color="#e34a33", label="Comparison group (9 non-EU countries)"),
        mpatches.Patch(facecolor="#d9d9d9", edgecolor="#7f7f7f", label="Not in the country panel\n(Kosovo, Liechtenstein, Turkey, Ukraine)"),
    ]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=11, frameon=True, framealpha=0.95)

    ax.set_title("Study design: EU-27 and the nine comparison countries", fontsize=13, pad=15)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_map()
