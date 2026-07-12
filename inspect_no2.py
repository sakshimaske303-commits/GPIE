import harp

filename = r"data/earth_observation/no2/raw/S5P_RPRO_L2__NO2____20190101T064159_20190101T082329_06312_03_020400_20221106T092319.nc"

product = harp.import_product(filename)

print("=" * 50)
print("Variables found in product:")
print("=" * 50)

for variable in product:
    print(variable)