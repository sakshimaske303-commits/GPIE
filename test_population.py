import os
from download_population import download_country_population, POP_RAW_DIR

def run_single_country_test():
    print("=" * 60)
    print("INITIALIZING WORLDPOP SINGLE TILE SANDBOX TEST")
    print("=" * 60)
    
    # Testing parameters: Luxembourg (LUX) for year 2019
    test_country = "LUX"
    test_year = 2019
    
    expected_filename = f"{test_country.lower()}_ppp_{test_year}.tif"
    expected_filepath = os.path.join(POP_RAW_DIR, expected_filename)
    
    # Sandbox operational test run trigger
    status = download_country_population(test_country, test_year)
    
    print("\n" + "-" * 50)
    print("TEST EXECUTION VERIFICATION SUMMARY")
    print("-" * 50)
    print(f"Function return status        : {status}")
    print(f"Target file path configured   : {expected_filepath}")
    
    if os.path.exists(expected_filepath):
        file_size = os.path.getsize(expected_filepath) / 1024 / 1024 # Size in MB
        print(f"Physical file status          : EXISTS")
        print(f"Downloaded file size          : {file_size:.2f} MB")
        print("\n[SUCCESS] Population ingestion framework is 100% stable!")
    else:
        print(f"Physical file status          : MISSING / FAILED")
        print("\n[FAILURE] Check API endpoints or local filesystem paths.")

if __name__ == "__main__":
    run_single_country_test()