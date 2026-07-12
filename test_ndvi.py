from auth_clms import get_clms_access_token
from download_ndvi import submit_ndvi_request, poll_and_download

token = get_clms_access_token()

task_id = submit_ndvi_request(token, 2019, "NL")  # Netherlands - small, quick test
poll_and_download(token, task_id, 2019, "NL")