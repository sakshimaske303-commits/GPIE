from auth_sentinelhub import get_sentinelhub_token
from download_no2_sentinelhub import load_country_geometry, request_no2_stats

token = get_sentinelhub_token()
geom = load_country_geometry("NL")
result = request_no2_stats(token, "NL", geom, 2019)

import json
print(json.dumps(result, indent=2)[:1500] if result else "Failed")