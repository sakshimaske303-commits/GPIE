import zipfile
import os
import glob

RAW_DIR = "data/earth_observation/climate/raw"


def unzip_era5_file(zip_path_disguised_as_nc):
    """
    CDS sometimes returns a zip file even when netcdf format is requested,
    with a .nc extension. This extracts the actual .nc file(s) inside.
    """
    extract_dir = zip_path_disguised_as_nc.replace(".nc", "_extracted")

    if os.path.exists(extract_dir):
        print(f"Already extracted: {os.path.basename(zip_path_disguised_as_nc)}")
        return extract_dir

    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path_disguised_as_nc, "r") as z:
        names = z.namelist()
        z.extractall(extract_dir)

    print(f"Extracted {os.path.basename(zip_path_disguised_as_nc)}: {names}")
    return extract_dir


def main():
    nc_files = glob.glob(os.path.join(RAW_DIR, "era5_monthly_*.nc"))
    print(f"Found {len(nc_files)} files to check.\n")

    for f in nc_files:
        unzip_era5_file(f)


if __name__ == "__main__":
    main()