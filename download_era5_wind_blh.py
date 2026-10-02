"""I download ERA5 monthly wind speed and boundary-layer height and average them per country.
I use them as weather controls because wind and a deep boundary layer dilute NO2."""
import glob
import os
import zipfile

import numpy as np
import pandas as pd
import xarray as xr
from rasterio.features import geometry_mask
from rasterio.transform import from_origin

from country_boundaries import load_country_geometry, get_all_country_codes

RAW_DIR = "data/earth_observation/climate/raw"
RAW_PATH = os.path.join(RAW_DIR, "era5_wind_blh_2019_2024.nc")
OUT_PATH = "data/era5_wind_blh_country_monthly.csv"
DATASET = "reanalysis-era5-single-levels-monthly-means"
AREA = [71.5, -31.5, 27.5, 35.0]   # N, W, S, E - same box as download_era5.py


def download():
    if os.path.exists(RAW_PATH) and os.path.getsize(RAW_PATH) > 0:
        print(f"Already downloaded: {RAW_PATH}")
        return
    import cdsapi
    os.makedirs(RAW_DIR, exist_ok=True)
    request = {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": ["10m_wind_speed", "boundary_layer_height"],
        "year": [str(y) for y in range(2019, 2025)],
        "month": [f"{m:02d}" for m in range(1, 13)],
        "time": ["00:00"],
        "area": AREA,
        "data_format": "netcdf",
        "download_format": "unarchived",
    }
    print("Requesting ERA5 wind speed + boundary-layer height (CDS queues the job, this can take a while)...")
    cdsapi.Client().retrieve(DATASET, request, RAW_PATH)
    print(f"Downloaded: {RAW_PATH}")


def open_dataset():
    """CDS sometimes returns a zip of several .nc files even when I ask it not to."""
    if zipfile.is_zipfile(RAW_PATH):
        ext = RAW_PATH.replace(".nc", "_extracted")
        with zipfile.ZipFile(RAW_PATH) as z:
            z.extractall(ext)
        parts = [xr.open_dataset(p) for p in sorted(glob.glob(os.path.join(ext, "*.nc")))]
        parts = [p.drop_vars([v for v in ("expver", "number") if v in p.coords]) for p in parts]
        return xr.merge(parts, compat="override")
    ds = xr.open_dataset(RAW_PATH)
    return ds.drop_vars([v for v in ("expver", "number") if v in ds.coords])


def pick(ds, candidates):
    for name in candidates:
        if name in ds.data_vars:
            return name
    raise KeyError(f"None of {candidates} in file; found {list(ds.data_vars)}")


def main():
    download()
    ds = open_dataset()
    tdim = "valid_time" if "valid_time" in ds.dims else "time"
    wind, blh = pick(ds, ["si10", "wind10m", "ws10"]), pick(ds, ["blh"])
    lat, lon = ds["latitude"].values, ds["longitude"].values
    if lat[0] < lat[-1]:                       # make sure latitude runs north -> south
        ds = ds.sortby("latitude", ascending=False)
        lat = ds["latitude"].values
    dlat, dlon = abs(lat[1] - lat[0]), abs(lon[1] - lon[0])
    transform = from_origin(lon[0] - dlon / 2, lat[0] + dlat / 2, dlon, dlat)   # cell edges, not centres
    shape = (len(lat), len(lon))

    masks = {}
    for code in get_all_country_codes():
        geom = load_country_geometry(code)
        m = ~geometry_mask([geom], out_shape=shape, transform=transform, all_touched=False)
        if not m.any():                        # very small country (e.g. Malta)
            m = ~geometry_mask([geom], out_shape=shape, transform=transform, all_touched=True)
        masks[code] = m
    print("ERA5 cells per country: " + ", ".join(f"{c}={int(m.sum())}" for c, m in masks.items()))

    rows = []
    times = pd.to_datetime(ds[tdim].values)
    w_all, b_all = ds[wind].values, ds[blh].values
    for i, t in enumerate(times):
        for code, m in masks.items():
            rows.append({"country": code, "year": int(t.year), "month": int(t.month),
                         "wind_speed_ms": float(np.nanmean(w_all[i][m])),
                         "blh_m": float(np.nanmean(b_all[i][m]))})
    out = pd.DataFrame(rows).sort_values(["country", "year", "month"])
    out.to_csv(OUT_PATH, index=False)
    print(f"Saved: {OUT_PATH}  ({len(out)} rows, {out['country'].nunique()} countries)")
    print(out[["wind_speed_ms", "blh_m"]].describe().loc[["min", "50%", "max"]].round(2).to_string())


if __name__ == "__main__":
    main()
