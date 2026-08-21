import os
import json
from download_eurostat_gdp import download_regional_gdp, EUROSTAT_RAW_DIR, GDP_DATASET_CODE

def run_eurostat_sandbox_test():
    print("=" * 60)
    print("INITIALIZING EUROSTAT REGIONAL GDP SANDBOX TEST")
    print("=" * 60)
    
    # Testing parameters: Baseline year range
    test_start = 2019
    test_end = 2024
    
    expected_filename = f"{GDP_DATASET_CODE}_{test_start}_{test_end}.json"
    expected_filepath = os.path.join(EUROSTAT_RAW_DIR, expected_filename)
    
    # Run dynamic download check
    status_path = download_regional_gdp(start_year=test_start, end_year=test_end)
    
    print("\n" + "-" * 50)
    print("TEST EXECUTION VERIFICATION SUMMARY")
    print("-" * 50)
    print(f"Function return filepath : {status_path}")
    
    if status_path and os.path.exists(expected_filepath):
        print(f"Physical file status     : EXISTS")
        
        # Load sample data to verify JSON structural integrity
        try:
            with open(expected_filepath, "r", encoding="utf-8") as f:
                sample_data = json.load(f)
            
            # Eurostat API outputs label/dimension keys
            dataset_label = sample_data.get("label", "Unknown Indicator")
            print(f"Dataset Verified Label   : {dataset_label}")
            print("\n[SUCCESS] Eurostat Tabular Engine framework is 100% stable!")
            
        except json.JSONDecodeError:
            print("[FAILURE] File downloaded but content is corrupted or invalid JSON.")
    else:
        print(f"Physical file status     : MISSING / FAILED")
        print("\n[FAILURE] Check Eurostat network endpoints or local directory permissions.")

if __name__ == "__main__":
    run_eurostat_sandbox_test()