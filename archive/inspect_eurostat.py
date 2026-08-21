import json

with open("data/earth_observation/economy/raw/nama_10r_2gdp_2019_2024.json", "r") as f:
    data = json.load(f)

print("Top-level keys:", list(data.keys()))
print("\nDimension keys:", list(data.get("dimension", {}).keys()))
print("\nSample of 'value' (first 5 items):")
items = list(data.get("value", {}).items())[:5]
print(items)