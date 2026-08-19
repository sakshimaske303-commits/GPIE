"""Moran's I diagnostic checking whether cross-border pollution correlation
shows up in the raw data and DiD residuals.
"""

import json
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
from libpysal.weights import KNN
from esda.moran import Moran, Moran_Local
import statsmodels.api as sm

from country_boundaries import load_country_geometry

DATA_PATH = "data/master_dataset_control.csv"
K_NEIGHBORS = 4


def build_country_geodataframe(countries):
    rows = []
    for code in countries:
        geom_geojson = load_country_geometry(code)
        if geom_geojson is None:
            print(f"  no geometry found for {code}, skipping")
            continue
        rows.append({"country": code, "geometry": shape(geom_geojson)})
    return gpd.GeoDataFrame(rows, crs="EPSG:4326")


def moran_on_values(gdf, w, value_col):
    vals = gdf.set_index("country").loc[w.id_order, value_col].values
    mi = Moran(vals, w)
    return mi


def run():
    df = pd.read_csv(DATA_PATH)
    countries = sorted(df["country"].unique())
    print(f"Building geometry for {len(countries)} countries...")
    gdf = build_country_geodataframe(countries)
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].reset_index(drop=True)
    print(f"Geometries loaded: {len(gdf)}")

    # KNN weights on centroids, not contiguity - several countries here are
    # islands or non-contiguous (CY, MT, IE, IS-equivalent gaps) and would
    # end up disconnected under Queen/Rook contiguity. Projected to EPSG:3035
    # (ETRS89-LAEA Europe) first so centroid/distance math isn't done on raw
    # lon/lat degrees.
    gdf_proj = gdf.to_crs("EPSG:3035")
    centroids = gdf_proj.geometry.centroid
    coords = np.column_stack([centroids.x, centroids.y])
    w = KNN.from_array(coords, k=K_NEIGHBORS, ids=list(gdf["country"]))
    w.transform = "r"

    results = {}

    # 1. Cross-sectional level: full-period average NO2 per country
    avg_no2 = df.groupby("country")["mean_no2"].mean().reset_index()
    gdf_no2 = gdf.merge(avg_no2, on="country")
    mi_level = moran_on_values(gdf_no2, w, "mean_no2")
    print(f"\nMoran's I, full-period average NO2 level: I={mi_level.I:.4f}, p={mi_level.p_sim:.4f} "
          f"(999 permutations)")
    results["level_full_period"] = {"I": mi_level.I, "p_sim": mi_level.p_sim, "z_sim": mi_level.z_sim}

    # 2. Pre- vs. post-treatment level, separately
    for label, mask in [("pre_treatment", (df.year < 2021) | ((df.year == 2021) & (df.month <= 6))),
                         ("post_treatment", (df.year > 2021) | ((df.year == 2021) & (df.month > 6)))]:
        avg = df[mask].groupby("country")["mean_no2"].mean().reset_index()
        gdf_period = gdf.merge(avg, on="country")
        mi = moran_on_values(gdf_period, w, "mean_no2")
        print(f"Moran's I, {label} average NO2: I={mi.I:.4f}, p={mi.p_sim:.4f}")
        results[f"level_{label}"] = {"I": mi.I, "p_sim": mi.p_sim, "z_sim": mi.z_sim}

    # 3. DiD residuals - does the model's unexplained variation still cluster
    # spatially, which country-clustered SEs alone wouldn't catch?
    did_df = df.copy()
    did_df["time"] = pd.to_datetime(did_df["year"].astype(str) + "-" + did_df["month"].astype(str).str.zfill(2))
    treatment_date = pd.Timestamp("2021-06-30")
    did_df["post"] = (did_df["time"] > treatment_date).astype(float)
    did_df["did_interaction"] = did_df["treatment_group"] * did_df["post"]
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
    model_df = did_df.dropna(subset=["mean_no2"] + controls).copy()

    country_dummies = pd.get_dummies(model_df["country"], prefix="country", drop_first=True).astype(float)
    month_dummies = pd.get_dummies(model_df["month"], prefix="month", drop_first=True).astype(float)
    X = pd.concat([model_df[["did_interaction", "post"] + controls].astype(float), country_dummies, month_dummies], axis=1)
    X = sm.add_constant(X)
    y = model_df["mean_no2"].astype(float)
    fit = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": model_df["country"]})

    model_df = model_df.copy()
    model_df["residual"] = fit.resid
    avg_resid = model_df.groupby("country")["residual"].mean().reset_index()
    gdf_resid = gdf.merge(avg_resid, on="country")
    mi_resid = moran_on_values(gdf_resid, w, "residual")
    print(f"\nMoran's I, DiD model residuals (country-averaged): I={mi_resid.I:.4f}, p={mi_resid.p_sim:.4f}")
    results["did_residuals"] = {"I": mi_resid.I, "p_sim": mi_resid.p_sim, "z_sim": mi_resid.z_sim}

    # Local Moran's I (LISA) on the full-period level - which specific
    # countries are driving the global clustering result, not just whether
    # clustering exists in aggregate.
    vals = gdf_no2.set_index("country").loc[w.id_order, "mean_no2"].values
    lisa = Moran_Local(vals, w)
    quadrant_labels = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}
    lisa_df = pd.DataFrame({
        "country": w.id_order,
        "local_I": lisa.Is,
        "p_sim": lisa.p_sim,
        "quadrant": [quadrant_labels[q] for q in lisa.q],
        "significant": lisa.p_sim < 0.05,
    })
    lisa_df["cluster"] = np.where(lisa_df["significant"], lisa_df["quadrant"], "Not significant")
    lisa_df.to_csv("data/moran_local_clusters.csv", index=False)
    print(f"\nLocal Moran's I (LISA) clusters:\n{lisa_df[lisa_df['significant']][['country', 'quadrant', 'p_sim']].to_string(index=False)}")
    print("Saved data/moran_local_clusters.csv")

    with open("data/spatial_autocorrelation_summary.json", "w") as f:
        json.dump(results, f, indent=2, default=float)
    print("\nSaved data/spatial_autocorrelation_summary.json")

    gdf_no2 = gdf_no2.merge(lisa_df[["country", "cluster", "local_I", "p_sim"]], on="country")
    gdf_no2.to_file("data/country_no2_for_moran.geojson", driver="GeoJSON")
    print("Saved data/country_no2_for_moran.geojson")


if __name__ == "__main__":
    run()
