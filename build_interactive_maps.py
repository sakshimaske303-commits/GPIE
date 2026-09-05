"""
GPIE — interactive folium/plotly versions of the static maps in outputs/plots/.

    python build_interactive_maps.py
"""
import json
import os

import folium
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from shapely.geometry import shape

OUT_DIR = "outputs/interactive"
DATA_PATH = "data/master_dataset_control.csv"

NUTS_PATH = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"
GADM_PATHS = {
    "UK": "data/earth_observation/boundaries/raw/gadm41_GBR_0.json",
    "NO": "data/earth_observation/boundaries/raw/gadm41_NOR_0.json",
    "CH": "data/earth_observation/boundaries/raw/gadm41_CHE_0.json",
}
CONTROL_COUNTRIES_NUTS = {"IS", "AL", "BA", "ME", "MK", "RS"}
EU27_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
}
CONTROL_COUNTRIES = set(GADM_PATHS.keys()) | CONTROL_COUNTRIES_NUTS
ALL_COUNTRIES = EU27_COUNTRIES | CONTROL_COUNTRIES

COUNTRY_NAMES = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "HR": "Croatia", "CY": "Cyprus",
    "CZ": "Czechia", "DK": "Denmark", "EE": "Estonia", "FI": "Finland", "FR": "France",
    "DE": "Germany", "EL": "Greece", "HU": "Hungary", "IE": "Ireland", "IT": "Italy",
    "LV": "Latvia", "LT": "Lithuania", "LU": "Luxembourg", "MT": "Malta", "NL": "Netherlands",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania", "SK": "Slovakia", "SI": "Slovenia",
    "ES": "Spain", "SE": "Sweden", "UK": "United Kingdom", "NO": "Norway", "CH": "Switzerland",
    "IS": "Iceland", "AL": "Albania", "BA": "Bosnia and Herzegovina", "ME": "Montenegro",
    "MK": "North Macedonia", "RS": "Serbia",
}


def load_geometry():
    records = []
    with open(NUTS_PATH, encoding="utf-8") as f:
        nuts_data = json.load(f)
    for feature in nuts_data["features"]:
        nid = feature["properties"].get("NUTS_ID")
        if nid in EU27_COUNTRIES or nid in CONTROL_COUNTRIES_NUTS:
            records.append({"country": nid, "geometry": shape(feature["geometry"])})
    for country_code, path in GADM_PATHS.items():
        with open(path, encoding="utf-8") as f:
            gadm_data = json.load(f)
        geom = shape(gadm_data["features"][0]["geometry"])
        records.append({"country": country_code, "geometry": geom})
    gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")
    gdf["name"] = gdf["country"].map(COUNTRY_NAMES)
    return gdf


def base_map():
    return folium.Map(location=[54, 12], zoom_start=4, tiles="cartodbpositron")


def choropleth(gdf, value_col, legend, fmt, palette, out_name, title):
    m = base_map()
    folium.Choropleth(
        geo_data=gdf.__geo_interface__,
        data=gdf,
        columns=["country", value_col],
        key_on="feature.properties.country",
        fill_color=palette,
        fill_opacity=0.85,
        line_opacity=0.5,
        legend_name=legend,
        nan_fill_color="lightgray",
    ).add_to(m)

    folium.GeoJson(
        gdf,
        style_function=lambda x: {"fillOpacity": 0, "color": "transparent"},
        tooltip=folium.GeoJsonTooltip(
            fields=["name", value_col],
            aliases=["Country:", f"{legend}:"],
            localize=True,
            fmt=fmt,
        ),
    ).add_to(m)

    m.get_root().html.add_child(folium.Element(
        f'<h3 style="text-align:center; font-family:sans-serif;">{title}</h3>'
    ))
    m.save(os.path.join(OUT_DIR, out_name))
    print(f"Saved: {OUT_DIR}/{out_name}")


def build_control_group_map(gdf):
    m = base_map()
    gdf = gdf.copy()
    gdf["group"] = gdf["country"].apply(
        lambda c: "Treatment (EU-27)" if c in EU27_COUNTRIES else "Control (non-EU)"
    )
    for _, row in gdf.iterrows():
        color = "#2c7fb8" if row["group"] == "Treatment (EU-27)" else "#e34a33"
        folium.GeoJson(
            row["geometry"].__geo_interface__,
            style_function=lambda x, c=color: {"fillColor": c, "color": "#1a1a1a", "weight": 1, "fillOpacity": 0.8},
            tooltip=f"{row['name']} — {row['group']}",
        ).add_to(m)
    m.get_root().html.add_child(folium.Element(
        '<h3 style="text-align:center; font-family:sans-serif;">GPIE Study Design: '
        'EU-27 (Treatment) vs. 9-Country Non-EU Control Group</h3>'
    ))
    m.save(os.path.join(OUT_DIR, "control_group_map.html"))
    print(f"Saved: {OUT_DIR}/control_group_map.html")


def build_moran_lisa_map():
    gdf = gpd.read_file("data/country_no2_for_moran.geojson")
    gdf["name"] = gdf["country"].map(COUNTRY_NAMES)
    cluster_colors = {
        "High-High": "#d7191c", "Low-Low": "#2c7fb8",
        "Low-High": "#abd9e9", "High-Low": "#fdae61", "Not significant": "#d9d9d9",
    }
    gdf["cluster_label"] = gdf.apply(
        lambda r: r["cluster"] if r["p_sim"] < 0.05 and pd.notna(r["cluster"]) else "Not significant", axis=1
    )
    m = base_map()
    for _, row in gdf.iterrows():
        color = cluster_colors.get(row["cluster_label"], "#d9d9d9")
        folium.GeoJson(
            row["geometry"].__geo_interface__,
            style_function=lambda x, c=color: {"fillColor": c, "color": "#1a1a1a", "weight": 0.6, "fillOpacity": 0.85},
            tooltip=f"{row['name']}: {row['cluster_label']} (p={row['p_sim']:.3f})",
        ).add_to(m)
    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index:9999; background:white;
                padding:10px 14px; border:1px solid #999; border-radius:6px; font-family:sans-serif; font-size:13px;">
      <b>LISA cluster (p&lt;0.05)</b><br>
      <span style="color:#d7191c;">&#9632;</span> High-High<br>
      <span style="color:#2c7fb8;">&#9632;</span> Low-Low<br>
      <span style="color:#abd9e9;">&#9632;</span> Low-High<br>
      <span style="color:#fdae61;">&#9632;</span> High-Low<br>
      <span style="color:#d9d9d9;">&#9632;</span> Not significant
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    m.get_root().html.add_child(folium.Element(
        '<h3 style="text-align:center; font-family:sans-serif;">Local Moran\'s I: '
        'Where NO2 Levels Cluster Spatially (36 Countries)</h3>'
    ))
    m.save(os.path.join(OUT_DIR, "moran_lisa_map.html"))
    print(f"Saved: {OUT_DIR}/moran_lisa_map.html")


def build_event_study():
    # NOTE (fixed): this used to build its own X matrix without the
    # avg_temp_c / avg_precip_mm / gdp_million_eur controls that
    # causal_inference_event_study.py uses for the canonical event-study
    # result reported in the paper - so this chart could (and did) show a
    # different significance pattern than the paper's own Figure 3. Now
    # matches that script's specification (same controls, same dropna,
    # same cluster-robust SEs) so this interactive chart and the paper stay
    # in sync. If causal_inference_event_study.py's spec changes again,
    # update this function to match.
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))
    df["month_of_year"] = df["month"]
    df["quarter"] = df["time"].dt.to_period("Q").astype(str)

    import statsmodels.api as sm
    d = df.copy()
    controls = ["avg_temp_c", "avg_precip_mm", "gdp_million_eur"]
    d = d.dropna(subset=["mean_no2"] + controls).copy()
    d["eu_x_quarter"] = d["treatment_group"].astype(str) + "_" + d["quarter"]
    quarters = sorted(d["quarter"].unique())
    ref_q = "2021Q2"

    d["post"] = 1
    country_dummies = pd.get_dummies(d["country"], prefix="country", drop_first=True).astype(float)
    quarter_dummies = pd.get_dummies(d["quarter"], prefix="q", drop_first=True).astype(float)
    interaction_cols = {}
    for q in quarters:
        if q == ref_q:
            continue
        interaction_cols[f"eu_x_{q}"] = ((d["treatment_group"] == 1) & (d["quarter"] == q)).astype(float)
    inter_df = pd.DataFrame(interaction_cols)

    X = pd.concat([inter_df, d[controls].astype(float), quarter_dummies, country_dummies], axis=1)
    X = sm.add_constant(X)
    model_df = pd.concat([d[["mean_no2"]], X], axis=1).dropna()
    y = model_df["mean_no2"].astype(float)
    X_fit = model_df.drop(columns=["mean_no2"]).astype(float)

    results = sm.OLS(y, X_fit).fit(cov_type="cluster", cov_kwds={"groups": d.loc[model_df.index, "country"]})

    rows = []
    for q in quarters:
        if q == ref_q:
            rows.append({"quarter": q, "coef": 0.0, "ci_low": 0.0, "ci_high": 0.0, "sig": False})
            continue
        col = f"eu_x_{q}"
        if col not in results.params:
            continue
        coef = results.params[col]
        ci = results.conf_int().loc[col]
        rows.append({"quarter": q, "coef": coef, "ci_low": ci[0], "ci_high": ci[1],
                     "sig": results.pvalues[col] < 0.05})
    plot_df = pd.DataFrame(rows)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=plot_df["quarter"], y=plot_df["coef"], mode="markers+lines",
        marker=dict(color=["#d7191c" if s else "#2c7fb8" for s in plot_df["sig"]], size=9),
        line=dict(color="#888", width=1),
        error_y=dict(type="data", symmetric=False,
                     array=plot_df["ci_high"] - plot_df["coef"],
                     arrayminus=plot_df["coef"] - plot_df["ci_low"]),
        name="EU x Quarter coefficient",
        hovertemplate="%{x}<br>Coefficient: %{y:.2e}<extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    fig.add_vline(x=ref_q, line_dash="dash", line_color="#f87171")
    fig.update_layout(
        title="Event-Study: Quarter-by-Quarter NO2 Effect (Reference: 2021Q2)<br>"
              "<sup>Red = statistically significant (p&lt;0.05). Hover for exact values.</sup>",
        xaxis_title="Quarter", yaxis_title="Coefficient (EU x Quarter, relative to 2021Q2)",
        template="plotly_white", height=550,
    )
    fig.write_html(os.path.join(OUT_DIR, "event_study.html"), include_plotlyjs="cdn")
    print(f"Saved: {OUT_DIR}/event_study.html")


def build_synthetic_control():
    df = pd.read_csv("data/synthetic_control_results.csv")
    df["date"] = pd.to_datetime(df["date"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["eu27_actual"], name="EU-27 (actual)",
                              line=dict(color="#2c7fb8", width=2)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["synthetic_control"], name="Synthetic control (7-donor composite)",
                              line=dict(color="#d7191c", width=2, dash="dash")))
    fig.add_vline(x="2021-06-30", line_dash="dot", line_color="gray")
    fig.update_layout(
        title="Augmented Synthetic Control: EU-27 vs. 7-Country Donor Composite<br>"
              "<sup>Hover for exact monthly values. Dotted line = European Climate Law effective date.</sup>",
        xaxis_title="Date", yaxis_title="Mean NO2 (mol/m²)",
        template="plotly_white", height=550, hovermode="x unified",
    )
    fig.write_html(os.path.join(OUT_DIR, "synthetic_control.html"), include_plotlyjs="cdn")
    print(f"Saved: {OUT_DIR}/synthetic_control.html")


def distinct_colors(n):
    # Evenly spaced hues around the color wheel - every country gets a
    # genuinely different color instead of a handful of colors repeating
    # (which is what happens with a short palette cycled via modulo).
    import colorsys
    colors = []
    for i in range(n):
        h = i / n
        r, g, b = colorsys.hls_to_rgb(h, 0.5, 0.65)
        colors.append("#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255)))
    return colors


def build_explore_trends():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))
    df["country_name"] = df["country"].map(COUNTRY_NAMES)

    fig = go.Figure()
    countries = sorted(df["country_name"].unique())
    default = ["Germany", "France", "United Kingdom", "Norway"]
    palette = distinct_colors(len(countries))

    for i, name in enumerate(countries):
        cdf = df[df["country_name"] == name].sort_values("time")
        fig.add_trace(go.Scatter(
            x=cdf["time"], y=cdf["mean_no2"], name=name, mode="lines",
            line=dict(color=palette[i]),
            visible=True if name in default else "legendonly",
        ))

    fig.add_vline(x="2021-06-30", line_dash="dash", line_color="#f87171")
    fig.update_layout(
        title="Explore NO2 Trends by Country (2019-2024)<br>"
              "<sup>Click legend entries to toggle countries. Dashed line = European Climate Law effective date.</sup>",
        xaxis_title="Date", yaxis_title="Mean NO2 (mol/m²)",
        template="plotly_white", height=600, hovermode="x unified",
    )
    fig.write_html(os.path.join(OUT_DIR, "explore_trends.html"), include_plotlyjs="cdn")
    print(f"Saved: {OUT_DIR}/explore_trends.html")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    gdf = load_geometry()
    df = pd.read_csv(DATA_PATH)
    country_avg = df.groupby("country")[["mean_no2", "mean_ndvi", "avg_temp_c", "gdp_million_eur"]].mean().reset_index()
    gdf = gdf.merge(country_avg, on="country", how="left")

    build_control_group_map(gdf)
    choropleth(gdf, "mean_no2", "Mean NO2 (mol/m²)", ".2e", "YlOrRd",
               "no2_map.html", "NO2 Concentration by Country (2019-2024 Average)")
    choropleth(gdf, "mean_ndvi", "Mean NDVI", ".3f", "YlGn",
               "ndvi_map.html", "Vegetation Health (NDVI) by Country (2019-2024 Average)")
    choropleth(gdf, "avg_temp_c", "Avg Temperature (°C)", ".1f", "YlOrRd",
               "climate_map.html", "Average Temperature by Country (2019-2024)")
    choropleth(gdf, "gdp_million_eur", "GDP (Million EUR)", ",.0f", "PuBu",
               "gdp_map.html", "GDP by Country (2019-2024 Average)")
    build_moran_lisa_map()
    build_event_study()
    build_synthetic_control()
    build_explore_trends()

    print(f"\nAll interactive maps saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()
