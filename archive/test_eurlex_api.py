import requests

url = "https://eur-lex.europa.eu"

response = requests.get(url)

print("Status Code:", response.status_code)
print(response.text[:500])