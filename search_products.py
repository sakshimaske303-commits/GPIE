import requests

from auth import get_access_token

from config import (
    COLLECTION,
    CATALOG_URL,
    START_DATE,
    END_DATE,
    TOP,
    EU_BBOX_WKT
)

def search_products(start_date, end_date):

    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    print("TOP =", TOP)
    params = {
    "$filter": (
    f"Collection/Name eq '{COLLECTION}' "
    f"and ContentDate/Start ge '{start_date}' "
    f"and ContentDate/Start le '{end_date}' "
    f"and contains(Name,'RPRO') "
    f"and contains(Name,'NO2')"
    f" and OData.CSC.Intersects(area=geography'SRID=4326;{EU_BBOX_WKT}')"
),
    "$orderby": "ContentDate/Start asc",
    "$top": TOP
}
    response = requests.get(
        CATALOG_URL,
        headers=headers,
        params=params,
        timeout=30
    )
    print(response.url)
    #print(response.text)

    print("Status Code:", response.status_code)

    data = response.json()
    
    if "value" not in data:
     return []
    print("Total Products Returned :", len(data["value"]))

    for product in data["value"]:
     #print(product["GeoFootprint"])
     print("=" * 60)
     print("Product :", product["Name"])
     print("Date    :", product["ContentDate"]["Start"])
     print("Size    :", product["ContentLength"], "bytes")

    return data["value"]

def main():
    search_products(
        START_DATE,
        END_DATE
    )


if __name__ == "__main__":
    main()