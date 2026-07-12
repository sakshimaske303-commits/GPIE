import os
import json
from download_nuts import download_nuts_country_boundaries, NUTS_RAW_DIR, NUTS_FILENAME

def run_nuts_sandbox_test():
    print("=" * 60)
    print("INITIALIZING NUTS BOUNDARIES VECTOR SANDBOX TEST")
    print("=" * 60)
    
    expected_filepath = os.path.join(NUTS_RAW_DIR, NUTS_FILENAME)
    
    # Run dynamic vector extraction
    status_path = download_nuts_country_boundaries()
    
    print("\n" + "-" * 50)
    print("TEST EXECUTION VERIFICATION SUMMARY")
    print("-" * 50)
    print(f"Function return vector path : {status_path}")
    
    if status_path and os.path.exists(expected_filepath):
        print(f"Physical file status        : EXISTS")
        
        # Verify JSON structure and feature geometry count
        try:
            with open(expected_filepath, "r", encoding="utf-8") as f:
                vector_data = json.load(f)
            
            features_count = len(vector_data.get("features", []))
            print(f"Total Administrative Polygons: {features_count}")
            
            # Extract sample country code property to ensure transparency
            if features_count > 0:
                # Loop through to pull first available NUTS property id 
                sample_feat = vector_data["features"][0]
                sample_country = sample_feat["properties"].get("NUTS_ID", "Unknown")
                print(f"Sample Boundary Identifier   : {sample_country}")
                
            print("\n[SUCCESS] NUTS GISCO Vector Engine framework is 100% stable!")
            
        except json.JSONDecodeError:
            print("[FAILURE] Vector file downloaded but geometry content is corrupted.")
    else:
        print(f"Physical file status        : MISSING / FAILED")
        print("\n[FAILURE] Check GISCO server endpoint or directory access parameters.")

if __name__ == "__main__":
    run_nuts_sandbox_test()