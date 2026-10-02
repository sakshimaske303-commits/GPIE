# DATA SOURCES

### DS01

Dataset Name : EU Green Deal Policy Database (EUR-Lex)
Provider : EUR-Lex
Parameter : European Union Environmental Policies and Legislation
Data Type : Text / Metadata
Format : JSON, CSV
Spatial Resolution : Not Applicable
Temporal Resolution : Updated as New Policies are Published
Purpose : Build a structured policy intelligence database for analysing the relationship between environmental policies and observed geospatial changes.

### DS02

Dataset Name : Sentinel-5P TROPOMI NO₂ Level-2
Satellite : Sentinel-5P
Instrument : TROPOMI
Parameter : Nitrogen Dioxide (NO₂)
Data Type : Raster
Format : Daily GeoTIFF rasters from the Sentinel Hub Process API, reduced locally to per-country daily sums and counts (JSONL log) and monthly means (JSON); the NetCDF/HARP Level-2 route was tested but not used for the final data
Spatial Resolution : 3.5 km × 7 km until 6 August 2019, 3.5 km × 5.5 km afterwards; requested as one 0.1° raster per day via the Sentinel Hub Process API and pooled into country monthly means
Temporal Resolution : Daily overpasses, aggregated to monthly means (QA ≥ 0.75)
Purpose : Primary outcome — tropospheric NO₂ column density before and after the Climate Law date.

### DS03

Dataset Name : Copernicus Global Land Service (CGLS) NDVI
Provider : Copernicus Global Land Service, via Sentinel Hub Statistical API (BYOC collection)
Parameter : Normalized Difference Vegetation Index (NDVI)
Data Type : Zonal Statistics (server-side aggregated)
Format : JSON
Spatial Resolution : 300 m
Temporal Resolution : 10-Daily (Dekadal)
Purpose : Monitor vegetation health and greenness before and after Green Deal implementation.

### DS04

Dataset Name : ESA WorldCover 10 m
Provider : European Space Agency (ESA)
Parameter : Land Cover Classification
Data Type : Raster
Format : GeoTIFF (.tif)
Spatial Resolution : 10 m
Temporal Resolution : Single 2021 map (v200) used; no change detection
Purpose : Descriptive context (dominant land-cover class per EU-27 country); absorbed by country fixed effects, not a model regressor.

### DS05

Dataset Name : Copernicus DEM GLO-30
Provider : Copernicus Programme
Parameter : Digital Elevation Model (Elevation)
Data Type : Raster
Format : GeoTIFF (.tif)
Spatial Resolution : 30 m
Temporal Resolution : Static
Purpose : Descriptive context (mean elevation per EU-27 country); absorbed by country fixed effects, not a model regressor.

### DS06

Dataset Name : ERA5 Climate Reanalysis
Provider : Copernicus Climate Data Store (CDS)
Parameter : Air Temperature and Total Precipitation (model controls); 10 m Wind Speed and Boundary-Layer Height (robustness controls, `download_era5_wind_blh.py`)
Data Type : Raster / NetCDF
Format : NetCDF (.nc)
Spatial Resolution : ~31 km
Temporal Resolution : Hourly (Aggregated to Monthly/Annual)
Purpose : Normalize environmental changes by accounting for climate variability before evaluating policy impacts.

### DS07

Dataset Name : WorldPop Population
Provider : WorldPop
Parameter : Population Distribution
Data Type : Raster
Format : GeoTIFF (.tif)
Spatial Resolution : 100 m
Temporal Resolution : Annual
Purpose : Acquired for 2019–2020 only (later years not available in the version accessed); not used in the model.

### DS08

Dataset Name : Eurostat Regional Statistics
Provider : Eurostat
Parameter : GDP at current market prices (nama_10r_2gdp; country-level NUTS-0 rows, unit MIO_EUR)
Data Type : Tabular
Format : JSON-stat (raw) → CSV
Spatial Resolution : Country (NUTS-0)
Temporal Resolution : Annual (repeated across months in the panel)
Purpose : Time-varying control in the DiD model for the EU-27.

### DS09

Dataset Name : NUTS Administrative Boundaries
Provider : Eurostat GISCO
Parameter : NUTS Level 0 (country) boundaries, 2024, EPSG:4326
Data Type : Vector
Format : GeoJSON
Spatial Resolution : Administrative Units
Temporal Resolution : Static (Updated when administrative boundaries change)
Purpose : Spatial joins, regional aggregation and visualization of environmental and socio-economic datasets.

### DS10

Dataset Name : GADM 4.1 Level-0 Boundaries
Provider : GADM
Parameter : Country boundaries for the United Kingdom, Norway and Switzerland (and India for the transferability test)
Data Type : Vector
Format : GeoJSON
Purpose : Geometry for control countries not covered by the NUTS file used.

### DS11

Dataset Name : World Bank GDP (NY.GDP.MKTP.CD)
Provider : World Bank Open Data API
Parameter : GDP, current US$, converted to EUR with annual average EUR/USD rates
Data Type : Tabular
Format : JSON → CSV
Temporal Resolution : Annual
Purpose : GDP control for the 9 non-EU comparison countries.

### DS12

Dataset Name : Oxford COVID-19 Government Response Tracker (OxCGRT), Stringency Index
Provider : Blavatnik School of Government, University of Oxford (Hale et al., 2021)
Parameter : National stringency index (0-100), averaged to monthly
Data Type : Tabular
Format : CSV (`data/covid/oxcgrt_stringency_national.csv`, four columns taken from OxCGRT_compact_national_v1.csv)
Temporal Resolution : Daily, 2020-2022 (set to 0 outside that window)
Purpose : Robustness control for COVID-19 restrictions. Covers 34 of the 36 study countries (not Montenegro or North Macedonia).

*Counting note: the README groups these sources as 8 (EUR-Lex, NO₂, NDVI, ERA5, GDP [Eurostat + World Bank], land cover, DEM, boundaries [GISCO + GADM]); WorldPop was acquired but not used. The Oxford stringency index (DS12) is used only as a robustness control.*
