import requests

url = "http://127.0.0.1:8000/predict"

data = {
    "store_nbr": 1.0,
    "item_nbr": 96995.0,
    "unit_sales": 7.0,
    "onpromotion": 0.0,
    "day": 1,
    "month": 1,
    "dayofweek": 0,
    "week": 1,
    "family_encoded": 0,
    "city_encoded": 0,
    "state_encoded": 0,
    "type_encoded": 0,
    "is_outlier": 0,
    "is_return": 0,
    "holiday": 0,
    "year": 2017,
    "is_weekend": 0
}

response = requests.post(url, json=data)
print(response.json)