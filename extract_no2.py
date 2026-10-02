# run_pipeline.py uses this. My final NO2 data comes from download_no2_sentinelhub.py.
import harp
import os


def preprocess_file(input_filepath, output_dir):
    """Filter one Sentinel-5P NO2 file by QA, bin it to a 0.05 degree grid, save as Level-3.
    Returns the output path, or None."""
    try:
        operations = (
            "tropospheric_NO2_column_number_density_validity>75;"
            "keep(latitude,longitude,tropospheric_NO2_column_number_density);"
            "bin_spatial(1041,-31.5,0.05,1321,27.5,0.05)"
        )

        product = harp.import_product(input_filepath, operations=operations)

        os.makedirs(output_dir, exist_ok=True)

        input_filename = os.path.basename(input_filepath)
        output_filename = input_filename.replace(".nc", "_L3.nc")
        output_filepath = os.path.join(output_dir, output_filename)

        harp.export_product(product, output_filepath)

        return output_filepath

    except Exception as e:
        print(f"Preprocessing failed for {input_filepath}: {e}")
        return None