"""I use Moran's I to check for spatial correlation in the NO2 levels and the DiD residuals."""

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
    np.random.seed(12345)  # fixed seed so my permutation p-values are reproducible
    df = pd.read_csv(DATA_PATH)
    countries = sorted(df["country"].unique())
    print(f"Building geometry for {len(countries)} countries...")
    gdf = build_country_geodataframe(countries)
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].reset_index(drop=True)
    print(f"Geometries loaded: {len(gdf)}")

    # I use KNN on centroids because islands (CY, MT, IE) have no neighbours under contiguity.
    # I project to EPSG:3035 first so distances are in metres, not degrees.
    gdf_proj = gdf.to_crs("EPSG:3035")
    centroids = gdf_proj.geometry.centroid
    coords = np.column_stack([centroids.x, centroids.y])
    w = KNN.from_array(coords, k=K_NEIGHBORS, ids=list(gdf["country"]))
    w.transform = "r"

    results = {}

    # 1. Full-period average NO2 per country
    avg_no2 = df.groupby("country")["mean_no2"].mean().reset_index()
    gdf_no2 = gdf.merge(avg_no2, on="country")
    mi_level = moran_on_values(gdf_no2, w, "mean_no2")
    print(f"\nMoran's I, full-period average NO2 level: I={mi_level.I:.4f}, p={mi_level.p_sim:.4f} "
          f"(999 permutations)")
    results["level_full_period"] = {"I": mi_level.I, "p_sim": mi_level.p_sim, "z_sim": mi_level.z_sim}

    # 2. Pre and post treatment levels, separately
    for label, mask in [("pre_treatment", (df.year < 2021) | ((df.year == 2021) & (df.month <= 6))),
                         ("post_treatment", (df.year > 2021) | ((df.year == 2021) & (df.month > 6)))]:
        avg = df[mask].groupby("country")["mean_no2"].mean().reset_index()
        gdf_period = gdf.merge(avg, on="country")
        mi = moran_on_values(gdf_period, w, "mean_no2")
        print(f"Moran's I, {label} average NO2: I={mi.I:.4f}, p={mi.p_sim:.4f}")
        results[f"level_{label}"] = {"I": mi.I, "p_sim": mi.p_sim, "z_sim": mi.z_sim}

    # 3. DiD residuals. Country fixed effects force each country's mean residual to zero,
    # so I test the residuals month by month and rebuild the weights for each month.
    did_df = df.copy()
    did_df["time"] = pd.to_datetime(did_df["year"].astype(str) + "-" + did_df["month"].astype(str).str.zfill(2))
    # Cutoff 2021-06-30 makes July 2021 my first post-treatment month.
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
    max_country_mean = model_df.groupby("country")["residual"].mean().abs().max()
    print(f"\n(Check) largest |country-mean residual| = {max_country_mean:.2e} "
          f"- ~0 by construction under country fixed effects, hence the per-month test below.")

    centroid_xy = dict(zip(gdf["country"], coords))
    monthly = []
    for t, grp in model_df.groupby("time"):
        grp = grp[grp["country"].isin(centroid_xy)]
        if len(grp) < 10:
            continue
        ids = list(grp["country"])
        w_t = KNN.from_array(np.array([centroid_xy[c] for c in ids]), k=K_NEIGHBORS, ids=ids)
        w_t.transform = "r"
        mi_t = Moran(grp.set_index("country").loc[w_t.id_order, "residual"].values, w_t)
        monthly.append({"time": str(t.date()), "n_countries": len(ids), "I": mi_t.I, "p_sim": mi_t.p_sim})
    monthly_df = pd.DataFrame(monthly)
    monthly_df.to_csv("data/moran_residuals_by_month.csv", index=False)
    n_sig_pos = int(((monthly_df["p_sim"] < 0.05) & (monthly_df["I"] > 0)).sum())
    print(f"\nMoran's I on DiD residuals, month by month ({len(monthly_df)} months): "
          f"median I = {monthly_df['I'].median():.3f}, mean I = {monthly_df['I'].mean():.3f}; "
          f"{n_sig_pos} months significantly positive at p<0.05")
    results["did_residuals_monthly"] = {
        "n_months": int(len(monthly_df)),
        "median_I": float(monthly_df["I"].median()),
        "mean_I": float(monthly_df["I"].mean()),
        "n_months_significant_positive_p05": n_sig_pos,
        "share_months_significant_positive_p05": n_sig_pos / len(monthly_df),
        "max_abs_country_mean_residual": float(max_country_mean),
    }

    # Local Moran's I (LISA) shows which countries drive the global clustering.
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
