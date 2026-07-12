import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from styles import apply_custom_style, PALETTE

apply_custom_style()

st.markdown("<h1 style='text-align: center;'>📈 EXPLORE THE DATA</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; color: #a78bfa; font-weight: 400;'>Interactive Country-Level Time Series</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "master_dataset_control.csv")

EU27_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
}
CONTROL_COUNTRIES = {"UK", "NO", "CH"}

COUNTRY_NAMES = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "HR": "Croatia", "CY": "Cyprus",
    "CZ": "Czechia", "DK": "Denmark", "EE": "Estonia", "FI": "Finland", "FR": "France",
    "DE": "Germany", "EL": "Greece", "HU": "Hungary", "IE": "Ireland", "IT": "Italy",
    "LV": "Latvia", "LT": "Lithuania", "LU": "Luxembourg", "MT": "Malta", "NL": "Netherlands",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania", "SK": "Slovakia", "SI": "Slovenia",
    "ES": "Spain", "SE": "Sweden", "UK": "United Kingdom", "NO": "Norway", "CH": "Switzerland",
}


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))
    df["country_name"] = df["country"].map(COUNTRY_NAMES)
    return df


df = load_data()

# --- Controls ---
col1, col2 = st.columns([2, 1])
with col1:
    all_countries = sorted(df["country_name"].unique())
    default_selection = ["Germany", "France", "United Kingdom", "Norway"]
    selected_names = st.multiselect(
        "Select countries to compare",
        options=all_countries,
        default=[c for c in default_selection if c in all_countries],
    )
with col2:
    variable = st.selectbox(
        "Select variable",
        options=["mean_no2", "mean_ndvi", "avg_temp_c", "gdp_million_eur"],
        format_func=lambda x: {
            "mean_no2": "NO₂ (mol/m²)",
            "mean_ndvi": "NDVI (Vegetation Health)",
            "avg_temp_c": "Temperature (°C)",
            "gdp_million_eur": "GDP (Million EUR)",
        }[x],
    )

name_to_code = {v: k for k, v in COUNTRY_NAMES.items()}
selected_codes = [name_to_code[n] for n in selected_names]

if selected_codes:
    fig = go.Figure()

    color_palette = ["#00d4ff", "#7c3aed", "#00ffa3", "#f472b6", "#fbbf24", "#38bdf8"]

    for i, code in enumerate(selected_codes):
        country_df = df[df["country"] == code].sort_values("time")
        line_style = dict(dash="dot") if code in CONTROL_COUNTRIES else dict()

        fig.add_trace(go.Scatter(
            x=country_df["time"],
            y=country_df[variable],
            mode="lines",
            name=f"{COUNTRY_NAMES[code]}" + (" (control)" if code in CONTROL_COUNTRIES else ""),
            line=dict(color=color_palette[i % len(color_palette)], width=2.5, **line_style),
        ))

    # Treatment date marker
    fig.add_vline(
        x=pd.Timestamp("2021-06-30").timestamp() * 1000,
        line_dash="dash",
        line_color="#f87171",
        annotation_text="European Climate Law",
        annotation_position="top",
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#cbd5e1"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(t=60, b=40, l=40, r=40),
        height=550,
        xaxis_title="Date",
        yaxis_title=variable,
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<p class='caption-text'>Dotted lines indicate control-group (non-EU) countries. "
        "Dashed vertical line marks the European Climate Law's entry into force (30 June 2021).</p>",
        unsafe_allow_html=True,
    )
else:
    st.info("Select at least one country above to view its trend.")

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>GPIE — Green Policy Intelligence Engine</p>",
    unsafe_allow_html=True,
)