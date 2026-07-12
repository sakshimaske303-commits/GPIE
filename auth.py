import requests
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / ".env")

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/"
    "protocol/openid-connect/token"
)

CLIENT_ID = "cdse-public"

USERNAME = os.getenv("CDSE_USERNAME")
PASSWORD = os.getenv("CDSE_PASSWORD")


def get_access_token():
    if not USERNAME or not PASSWORD:
        raise ValueError(
            "Missing credentials. Check .env file has CDSE_USERNAME and CDSE_PASSWORD."
        )

    payload = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
        "client_id": CLIENT_ID,
    }

    response = requests.post(TOKEN_URL, data=payload, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(
            f"Authentication failed ({response.status_code}): {response.text}"
        )

    token_data = response.json()
    return token_data["access_token"]