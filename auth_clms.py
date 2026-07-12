import json
import time
import jwt
import requests


def get_clms_access_token(service_key_path="clms_service_key.json"):
    """
    Builds a signed JWT from the CLMS service key and exchanges it
    for a short-lived access token.
    Returns the access token string.
    """
    with open(service_key_path, "r") as f:
        service_key = json.load(f)

    private_key = service_key["private_key"].encode("utf-8")

    claim_set = {
        "iss": service_key["client_id"],
        "sub": service_key["user_id"],
        "aud": service_key["token_uri"],
        "iat": int(time.time()),
        "exp": int(time.time() + 3600),
    }

    grant = jwt.encode(claim_set, private_key, algorithm="RS256")

    response = requests.post(
        service_key["token_uri"],
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": grant,
        },
    )

    if response.status_code != 200:
        raise RuntimeError(f"CLMS auth failed ({response.status_code}): {response.text}")

    return response.json()["access_token"]