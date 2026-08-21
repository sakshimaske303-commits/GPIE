from auth_sentinelhub import get_sentinelhub_token
from download_ndvi_sentinelhub import load_country_geometry, request_ndvi_stats

token = get_sentinelhub_token()
geom = load_country_geometry("FR")
result = request_ndvi_stats(token, "FR", geom, 2019)

import json
print(json.dumps(result, indent=2)[:1500] if result else "Still failed")