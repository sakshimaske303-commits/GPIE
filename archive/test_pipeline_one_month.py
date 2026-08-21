from run_pipeline import process_month
from date_utils import generate_monthly_ranges

# Test with just January 2019
for start_date, end_date, year, month in generate_monthly_ranges(2019, 1, 2019, 1):
    process_month(start_date, end_date, year, month)

print("Single-month test complete. Check the logs/ folder and outputs/data folders.")