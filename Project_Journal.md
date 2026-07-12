# GREEN POLICY INTELLIGENCE SYSTEM (GPIS)

## Project Overview

The Green Policy Intelligence Engine (GPIE) is a global geospatial decision intelligence framework designed to independently evaluate the real-world environmental effectiveness and economic efficiency of environmental policies using Earth Observation, Geographic Information Systems (GIS), remote sensing, spatial data science, and environmental economics.

Conventional policy assessments primarily rely on government-reported statistics, which may be delayed, inconsistent, or collected using different methodologies across countries. GPIE addresses this limitation by integrating independently observed satellite-derived environmental indicators with socioeconomic, economic, and policy datasets to create an objective and reproducible evaluation framework.

Rather than focusing on a single country or policy, the framework is designed as a globally transferable methodology capable of evaluating environmental policies implemented in different geographic, economic, and political contexts.

The European Green Deal will serve as the first demonstration case because of its comprehensive environmental policy framework, high-quality open datasets, and global relevance. However, the methodology is intentionally designed so that it can later be applied to any country or region worldwide.

## Problem Statement

Governments invest billions of dollars annually in environmental and climate policies. Despite these investments, there is currently no unified geospatial framework capable of independently verifying whether implemented policies have produced measurable environmental improvements while simultaneously evaluating their economic efficiency and spatial impacts.

Existing evaluations frequently depend on administrative reports and fragmented datasets, making comparisons across countries and policies difficult. There remains a need for a transparent, reproducible, and satellite-driven framework capable of integrating environmental observations, economic indicators, spatial analysis, and policy information into a single decision-support system.

## Aim

To develop a globally applicable geospatial framework that objectively measures, compares, and visualizes the environmental performance and economic effectiveness of environmental policies using satellite observations, GIS, Python automation, and spatial analytical techniques.

## Objectives

- Develop an automated workflow for collecting policy, environmental, and socioeconomic datasets.
- Integrate multi-source Earth Observation datasets into a unified spatial database.
- Quantify measurable environmental changes associated with environmental policy implementation.
- Compare environmental outcomes across different geographic regions.
- Evaluate the economic effectiveness of environmental interventions using environmental economics indicators.
- Produce reproducible geospatial analyses, thematic maps, and decision-support outputs.
- Build a modular framework that can be reused for evaluating future environmental policies worldwide.

## Research Question

How can Earth Observation, GIS, remote sensing, spatial data science, and environmental economics be integrated into a reproducible geospatial framework capable of objectively evaluating the environmental effectiveness and economic efficiency of environmental policies at regional, national, and global scales?

## Expected Outputs

The completed project will generate:

- A fully automated Python-based geospatial processing workflow.
- A standardized environmental policy evaluation framework.
- Satellite-derived environmental assessment datasets.
- GIS-ready spatial databases.
- Thematic maps and interactive geospatial visualizations.
- Environmental policy performance indicators.
- Economic efficiency assessments.
- Comparative regional analyses.
- A reproducible methodology suitable for adaptation to other countries and policy domains.
- Complete technical documentation and open-source implementation.

## Demonstration Case

European Green Deal

The European Green Deal will be used exclusively as the first implementation and validation case study for demonstrating the capabilities of the Green Policy Intelligence Engine. Following validation, the framework can be extended to evaluate environmental policies implemented anywhere in the world.

-------------------------------------------------------------------------------------------------------------

# GPIE — Module Architecture

# MODULE 1 — Policy Database Acquisition
Automated extraction of European Green Deal policy records from the EU's official legal database (EUR-Lex), capturing policy metadata such as title, type, year, status, and thematic classification. This forms the "policy" half of the project — a structured record of what governments have officially claimed to implement.

# MODULE 2 — Earth Observation & Auxiliary Data Acquisition
Acquisition of independent satellite and auxiliary datasets used to verify policy outcomes: atmospheric nitrogen dioxide concentrations, vegetation health indices, land cover composition, elevation, climate variables, regional economic output, and administrative boundaries. This module supplies the independent, government-unaffiliated evidence against which policy claims are tested.

# MODULE 3 — Preprocessing & Standardization
Converts raw acquired satellite and statistical data into a standardized, analysis-ready form — including quality filtering, spatial aggregation to consistent administrative units, and unit standardization across all datasets, ensuring every dataset can be meaningfully compared on a common geographic and temporal basis.

# MODULE 4 — Temporal Aggregation
Structures time-series data into consistent monthly and annual composites across all datasets, producing the before-and-after temporal structure required to evaluate policy impact over time.

# MODULE 5 — Export & Output Standardization
Converts validated, processed datasets into final, analysis-ready formats with consistent structure and embedded metadata, preparing all data sources for integration into the causal inference stage.

# MODULE 6 — Validation & Quality Control
Performs systematic checks across all datasets — spatial consistency, valid value ranges, completeness, and cross-dataset compatibility — before any data is accepted into the final integrated GPIE database.

# MODULE 7 — Pipeline Orchestration & Execution Management
Coordinates the end-to-end execution lifecycle of the data pipeline, managing acquisition, processing, and error recovery in a structured, fault-tolerant manner across large multi-year, multi-country data acquisition runs.

# MODULE 8 — Causal Inference & Policy Verification
The project's core scientific contribution: applies causal inference methods (Difference-in-Differences and Synthetic Control) to statistically test whether satellite-observed environmental outcomes support or contradict self-reported government policy claims, moving beyond simple before-after comparison to isolate policy-attributable effects.

# MODULE 9 — Economic Efficiency Ranking
Combines causal inference results with policy cost data to rank environmental interventions by cost-effectiveness, addressing the project's economic evaluation objective alongside its environmental verification objective.

# MODULE 10 — Geospatial Output Generation
Produces the project's final geospatial decision-support outputs — thematic maps and regional comparisons in QGIS — translating statistical results into an interpretable spatial "policy effectiveness atlas."

# MODULE 11 — Dashboard & Deployment
Packages the complete project into an interactive, publicly accessible dashboard, with the full codebase and methodology published as an open-source, reproducible deliverable.

-------------------------------------------------------------------------------------------------------------

# Module 1 — Policy Database Construction

## Objective

To construct a structured, machine-readable database of European Green Deal policy records, forming the "policy" half of GPIE's core comparison — what governments have officially claimed to implement — against which independently observed satellite data would later be evaluated.

## Data Source

EUR-Lex, the European Union's official repository of legal and policy documents, was selected as the source. As the authoritative primary source for EU policy records, it ensures the resulting evaluation framework remains traceable to original legal text rather than secondary summaries.

## Methodology

Since EUR-Lex does not provide a structured bulk-export of policy metadata, an automated web-scraping pipeline was built using Python (`requests` and `BeautifulSoup`) to extract policy records directly from search results and individual document pages.

The pipeline extracts, for each policy record:
- Title, document status, and source link
- Policy type (e.g., Regulation, Decision) and publication year, parsed from the document identifier
- A unique policy identifier (CELEX ID) and a concise policy summary
- Full introductory policy text, along with derived length and word-count metadata
- Thematic tags, assigned through rule-based keyword classification of policy content

The resulting dataset was exported in both JSON and CSV formats (`documents.json`, `documents.csv`) to support downstream analysis, visualization, and integration with GIS and analytics tools.

An exploratory data analysis pass — using Pandas for filtering, grouping, and statistical summarization, and Matplotlib for visualization — validated dataset completeness and consistency, examining policy-type distribution, publication trends over time, and document length patterns before proceeding to the satellite data pipeline.

## Software Architecture

The initial scraping script was refactored into a modular, reusable architecture, separating data acquisition, metadata extraction, thematic tagging, export, and analysis into independent functions coordinated through a single execution entry point. This established a maintainable, production-oriented codebase pattern intended to be reused for the satellite data acquisition pipeline in subsequent modules.

## Why This Was Necessary

Without a structured policy-side dataset, satellite data collected in later modules would have no defined policy events — dates, regions, and categories — to be tested against. The metadata fields extracted here (particularly policy year, type, and thematic tags) are what allow policies to later be matched against specific time windows and regions during the causal inference stage. Establishing a modular, fault-tolerant software architecture at this early stage also meant the more complex Earth Observation pipeline could build on a proven structural pattern rather than repeating design decisions later.

## Output

`documents.json` / `documents.csv` — a structured, analysis-ready dataset of European Green Deal policy records with enriched metadata and thematic classification.

-------------------------------------------------------------------------------------------------------------

# Module 2 — Earth Observation & Auxiliary Data Acquisition

## Methodology Overview

This module establishes the complete Earth Observation and auxiliary data foundation for GPIE, providing the independent environmental and economic evidence against which policy claims (Module 1) are evaluated.

Study Area: European Union (27 member states), used as the first demonstration case for a globally transferable methodology.

Temporal Extent: 1 January 2019 – 31 December 2024, a standardized six-year window providing a pre-policy baseline alongside multiple years of Green Deal implementation.

Dataset Inventory: Nine datasets were integrated — Sentinel-5P TROPOMI NO₂, Sentinel-2/CGLS NDVI, ESA WorldCover, Copernicus DEM, ERA5 Climate Reanalysis, WorldPop Population, Eurostat Regional GDP, EU NUTS Administrative Boundaries, and the EUR-Lex Policy Database (Module 1).

All datasets were acquired directly from official data providers to ensure scientific reliability and reproducibility. Dynamic datasets (NO₂, NDVI, ERA5, GDP) were acquired across the full six-year study period; static datasets (DEM, administrative boundaries, land cover) were acquired once. Every acquired dataset was organized under a standardized directory structure (raw/processed/final) and subjected to basic verification (coordinate reference system, spatial extent, resolution, file integrity) before proceeding to processing.

A single coordinate reference system, WGS84 (EPSG:4326), was maintained throughout acquisition and processing for all datasets to eliminate reprojection error and preserve consistency across the project.

------------------------------------------------------------------------------------------------------------

## DS02 — Sentinel-5P NO₂ (Nitrogen Dioxide)

Purpose: NO₂ serves as the project's primary outcome variable — the independent, satellite-observed signal against which government-reported policy effectiveness is tested in the causal inference stage (Module 8).

Methodology: Tropospheric NO₂ column density was acquired via the Sentinel Hub Statistical API, using the `sentinel-5p-l2` collection. Quality control was applied server-side via the `minQa` parameter set to 75 — matching the project's independently-derived, ESA-recommended quality threshold (`qa_value ≥ 0.75`) for tropospheric NO₂ analysis. Each EU-27 country's administrative boundary was used as the query geometry, with monthly aggregation returned directly by the API. Data was acquired for all 27 EU countries across the full 2019–2024 period (162 country-year records).

Output: `no2_stats_by_country_monthly.json`

------------------------------------------------------------------------------------------------------------

## DS03 — NDVI (Vegetation Health Index)

Purpose: NDVI serves as a supporting environmental indicator, providing vegetation-health context alongside the project's primary NO₂ signal.

Methodology: NDVI (2014–present, 300m resolution, 10-daily composite, Version 3) was acquired via the Sentinel Hub Statistical API, using the underlying Copernicus Global Land Service BYOC collection. The digital-number encoding used by the source product was converted to physical NDVI values (range −1 to +1) server-side within the acquisition request itself, using the officially documented scale and offset values, with reserved status-flag values (snow, water, missing data) excluded prior to conversion. Country geometries were intersected with the project's European study extent prior to querying, to exclude non-contiguous overseas territories that would otherwise distort the requested spatial resolution. Data was acquired for all 27 EU countries across 2019–2024 (162 country-year records).

Output: `ndvi_stats_by_country_monthly.json`

-------------------------------------------------------------------------------------------------------------

## DS04 — ESA WorldCover (Land Cover)

Purpose: Land cover composition serves as a control variable in the causal inference stage, accounting for structural land-use differences between regions independent of policy effects.

Methodology: ESA WorldCover 10m (2021, Version 200) tiles covering the European study extent were acquired and mosaicked into a single virtual raster. The mosaic was resampled to 500m resolution using nearest-neighbor resampling — the scientifically appropriate method for categorical class data, where interpolation would produce meaningless intermediate values. Zonal statistics were computed against each EU-27 country boundary, producing the percentage composition of eleven standardized land cover classes (tree cover, cropland, built-up area, water, etc.) per country.

Output: `landcover_stats_by_country.json`

-------------------------------------------------------------------------------------------------------------

## DS05 — Copernicus DEM (Digital Elevation Model)

Purpose: Elevation serves as a control variable, accounting for topographic influence on environmental outcomes independent of policy effects.

Methodology: Copernicus DEM GLO-30 (30m resolution) tiles covering the European study extent are acquired from the public Copernicus AWS data mirror. Upon completion of acquisition, tiles will be mosaicked and resampled to 500m resolution using bilinear resampling — the appropriate method for continuous elevation data — followed by computation of zonal elevation statistics (mean, minimum, maximum, standard deviation) per EU-27 country.

Status: Acquisition in progress; processing pipeline finalized and pending execution upon acquisition completion.

------------------------------------------------------------------------------------------------------------

## DS06 — ERA5 Climate Reanalysis

Purpose: Temperature and precipitation serve as control variables, accounting for weather-driven environmental variation independent of policy effects.

Methodology: Monthly averaged 2m temperature and total precipitation were acquired via the Copernicus Climate Data Store API for the European study extent, 2019–2024. Temperature values were converted from Kelvin to Celsius and precipitation from meters to millimeters. Zonal statistics were computed against each EU-27 country boundary for every month in the study period, producing country-level monthly climate averages.

Output: `era5_stats_by_country_monthly.json`

-------------------------------------------------------------------------------------------------------------

## DS07 — WorldPop Population

**Purpose**: Population density provides demographic context for interpreting environmental outcomes at the regional level.

**Methodology**: Gridded population estimates were acquired per EU-27 country via the WorldPop REST API. Verified data availability was confirmed only for 2019 and 2020 within the accessible dataset version; extending coverage to 2021–2024 would require integration with a separate WorldPop data distribution system not currently implemented.

**Scope Decision**: Given that Population coverage (2 of 6 study years) is substantially incomplete relative to all other datasets in the project (full 2019–2024 coverage), Population has been designated a **supporting/descriptive dataset** rather than a control variable in the core causal inference model (Module 8), to avoid introducing a variable with significant missing-data gaps into the primary statistical analysis.

---

## DS08 — Eurostat Regional GDP

**Purpose**: GDP serves as a control variable, accounting for regional economic conditions independent of policy effects.

**Methodology**: Annual GDP at current market prices was acquired via the Eurostat REST Statistics API for all EU-27 countries, 2019–2024, standardized to a single measurement unit (Million Euro, current prices) to ensure consistency across all records.

**Output**: `gdp_by_country_year.csv`

---

## DS09 — NUTS Administrative Boundaries

**Purpose**: Provides the standardized spatial framework (country-level administrative boundaries) used to aggregate every other dataset in the project to a common geographic unit.

**Methodology**: Country-level (NUTS LEVL_0) boundaries were acquired from the official Eurostat GISCO distribution service, filtered to the 27 official EU member states.

**Output**: `NUTS_LEVL_0_2024_4326.geojson`

---

## Cross-Dataset Consistency Alignment

Following independent acquisition and processing, all datasets were reconciled to a single, consistent EU-27, country-level scope — correcting inconsistencies such as the inclusion of non-EU entities in some datasets and mixed measurement units in others, which were identified through direct cross-dataset compatibility testing. Climate, Land Cover, GDP, and NO₂ are now confirmed mutually consistent and merge-ready; NDVI shares the same acquisition and scope methodology. This alignment step ensures that all datasets can be reliably integrated in the forthcoming causal inference stage (Module 8).