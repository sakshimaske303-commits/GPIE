from auth import get_access_token

token = get_access_token()
print("Token received successfully!")
print(token[:50], "...")