from map_no2_choropleth import build_geometry_gdf, compute_avg_no2

gdf = build_geometry_gdf()
avg_no2 = compute_avg_no2()

print("Rows in gdf for FI:", len(gdf[gdf["country"] == "FI"]))
print("Rows in avg_no2 for FI:", len(avg_no2[avg_no2["country"] == "FI"]))

merged = gdf.merge(avg_no2, on="country", how="left")
print()
print("Merged row for FI:")
print(merged[merged["country"] == "FI"][["country", "avg_no2"]])
print()
print("Total rows in merged:", len(merged))
print("Duplicate country codes in merged:", merged["country"].duplicated().sum())
print()
print("All countries in merged with their avg_no2:")
print(merged[["country", "avg_no2"]].to_string())