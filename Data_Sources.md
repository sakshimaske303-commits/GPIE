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
Format : NetCDF (.nc)
Spatial Resolution : ~7 km × 3.5 km (recent products)
Temporal Resolution : Daily
Purpose : Monitor atmospheric NO₂ concentration before and after Green Deal implementation.

### DS03

Dataset Name : Sentinel-2 NDVI
Satellite : Sentinel-2
Instrument : MSI (MultiSpectral Instrument)
Parameter : Normalized Difference Vegetation Index (NDVI)
Data Type : Raster
Format : GeoTIFF (.tif)
Spatial Resolution : 10 m
Temporal Resolution : 5 Days
Purpose : Monitor vegetation health and greenness before and after Green Deal implementation.

### DS04

Dataset Name : ESA WorldCover 10 m
Provider : European Space Agency (ESA)
Parameter : Land Cover Classification
Data Type : Raster
Format : GeoTIFF (.tif)
Spatial Resolution : 10 m
Temporal Resolution : Annual
Purpose : Analyze land cover classes and detect changes associated with environmental policies.

### DS05

Dataset Name : Copernicus DEM GLO-30
Provider : Copernicus Programme
Parameter : Digital Elevation Model (Elevation)
Data Type : Raster
Format : GeoTIFF (.tif)
Spatial Resolution : 30 m
Temporal Resolution : Static
Purpose : Derive elevation, slope and terrain characteristics for environmental and policy impact analysis.

### DS06

Dataset Name : ERA5 Climate Reanalysis
Provider : Copernicus Climate Data Store (CDS)
Parameter : Air Temperature and Total Precipitation
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
Purpose : Estimate population exposure and assess the number of people affected by environmental changes.

### DS08

Dataset Name : Eurostat Regional Statistics
Provider : Eurostat
Parameter : GDP and Socio-economic Indicators
Data Type : Tabular
Format : CSV
Spatial Resolution : NUTS Administrative Regions
Temporal Resolution : Annual
Purpose : Evaluate socio-economic trends alongside environmental and policy changes.

### DS09

Dataset Name : NUTS Administrative Boundaries
Provider : Eurostat GISCO
Parameter : NUTS Levels 0, 1, 2 and 3 Administrative Regions
Data Type : Vector
Format : Shapefile (.shp)
Spatial Resolution : Administrative Units
Temporal Resolution : Static (Updated when administrative boundaries change)
Purpose : Spatial joins, regional aggregation and visualization of environmental and socio-economic datasets.