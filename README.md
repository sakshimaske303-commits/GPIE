# 🛰️ GPIE — Green Policy Intelligence Engine

**Independently verifying environmental policy claims using satellite data.**

GPIE is a geospatial causal-inference framework that tests whether the European Green Deal's flagship legislation — the **European Climate Law** (effective 30 June 2021) — produced a measurable, statistically distinguishable reduction in NO₂ pollution across the EU-27, using satellite observations rather than self-reported government claims.

Built on a **"Trust, But Verify"** research philosophy: policy claims are treated as hypotheses to be independently tested, not facts to be assumed.

---

## 📄 Project Documentation

| Document | What's Inside |
|---|---|
| 📘 [`Project_Journal.md`](./Project_Journal.md) | Polished project summary — methodology, findings, conclusions (start here) |
| 📗 [`Research_Paper.md`](./Research_Paper.md) | Formal academic paper — literature review, statistical methodology, results, discussion |
| 📙 [`Devlopment_Log.md`](./Devlopment_Log.md) | Full technical development log — every bug, debugging session, and methodology iteration |

---

## 🔗 Live Dashboard

**[View the interactive dashboard →](https://f5cf6fijj9gm564r6aapt6.streamlit.app/)**

---

## 📊 What This Project Does

- Acquires and processes **7 independent datasets** (NO₂, NDVI, climate, GDP, land cover, elevation, policy records) across **30 countries** (EU-27 + a genuine non-EU control group: UK, Norway, Switzerland), 2019–2024
- Builds a rigorous **Difference-in-Differences** causal inference model to isolate the Climate Law's specific effect from broader European pollution trends
- Validates the result through a **placebo test**, a **genuine external control group**, and a **quarterly event-study** robustness check
- Reports an honest, rigorously validated finding — including when that finding is a **statistically non-significant result**
- Presents everything through **7 publication-quality maps** and an **interactive Streamlit dashboard**

## 🔬 Key Finding

No statistically distinguishable EU-specific reduction in NO₂ was detected once genuinely compared against a non-EU control group (coefficient = −1.40 × 10⁻⁶, p = 0.632). This null result was independently confirmed via a 23-quarter event-study analysis. Full methodology, including an initial (later invalidated) positive result and the placebo test that revealed it was unreliable, is documented in the dashboard's Methodology page and in `Project_Journal.md`.

## 🌍 Transferability Validation

GPIE's original design goal was a **globally transferable methodology**, not one limited to the EU-27. To provide direct evidence of this — rather than leaving it as an unverified claim — the project's NO₂ acquisition pipeline was tested standalone on **India** (2019–2024), using the same Sentinel Hub Statistical API infrastructure and evalscript logic built for the EU-27 study, with zero modification to the core acquisition code.

All 6 years acquired successfully, returning physically realistic NO₂ values consistent with the EU-27 dataset's observed range. This confirms the framework's data-acquisition architecture is genuinely portable to other countries and regions — a standalone proof-of-concept, not a comparative analysis. See `test_india_transferability.py`.

---

## 🗂️ Repository Structure

```text
GPIE/
├── dashboard/                  # Streamlit dashboard (8 pages)
├── data/                       # Processed datasets and master merge files
│   └── earth_observation/      # Per-dataset acquisition/processing outputs
├── outputs/
│   └── plots/                  # Final generated maps and charts
├── Project_Journal.md          # Polished project summary and methodology
├── Research_Paper.md           # Formal academic research paper
├── Devlopment_Log.md           # Full technical development log (debugging & iteration history)
├── download_*.py               # Dataset acquisition scripts
├── process_*.py                # Dataset processing scripts
├── *_stats.py                  # Statistical processing utilities
├── causal_inference*.py        # Main, placebo & event-study models
├── map_*.py                    # Map generation scripts
└── country_boundaries.py       # Shared EU-27 + control-group boundary loader
```

## 🛠️ Tech Stack

Python · pandas · geopandas · statsmodels · matplotlib · Plotly · Streamlit · Sentinel Hub API · Copernicus Climate Data Store · Eurostat API · World Bank API

## 📚 Data Sources

| Dataset | Provider |
|---|---|
| NO₂ (Sentinel-5P) | ESA / Copernicus, via Sentinel Hub |
| NDVI (CGLS) | Copernicus Land Monitoring Service |
| Climate (ERA5) | ECMWF / Copernicus Climate Data Store |
| GDP | Eurostat (EU-27), World Bank (control group) |
| Land Cover | ESA WorldCover |
| Elevation | Copernicus DEM GLO-30 |
| Boundaries | Eurostat GISCO (NUTS), GADM |
| Policy Records | EUR-Lex |

## ▶️ Running Locally

```bash
git clone https://github.com/sakshimaske303-commits/GPIE.git
cd GPIE
pip install -r requirements.txt
cd dashboard
streamlit run app.py
```

## 👤 Author

**Sakshi D. Maske**

Independent Geospatial Researcher

---

*This project's full development process — including debugging history, methodology iterations, and every technical decision — is documented in `Devlopment_Log.md` for full transparency and reproducibility.*
