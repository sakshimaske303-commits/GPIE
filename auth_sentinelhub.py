import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

SH_CLIENT_ID = os.getenv("SH_CLIENT_ID")
SH_CLIENT_SECRET = os.getenv("SH_CLIENT_SECRET")


def get_sentinelhub_token():
    """Get a Sentinel Hub access token with the OAuth client credentials flow."""
    if not SH_CLIENT_ID or not SH_CLIENT_SECRET:
        raise ValueError("Missing SH_CLIENT_ID or SH_CLIENT_SECRET in .env file")

    payload = {
        "grant_type": "client_credentials",
        "client_id": SH_CLIENT_ID,
        "client_secret": SH_CLIENT_SECRET,
    }

    response = requests.post(TOKEN_URL, data=payload, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(f"Authentication failed ({response.status_code}): {response.text}")

    return response.json()["access_token"]


if __name__ == "__main__":
    token = get_sentinelhub_token()
    # I print only the length because the token is a live credential.
    print(f"Token received successfully ({len(token)} characters).")