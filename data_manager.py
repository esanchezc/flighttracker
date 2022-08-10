import requests
from user import User


class DataManager:
    def __init__(self):
        self.BASE_URL = "https://api.sheety.co/102369f1e8e69906cd018849bc15350e/flightDeals"
        self.PRICES_ENDPOINT = "/prices"
        self.USERS_ENDPOINT = "/users"
        self.TOKEN = "esanchez_flight_search"
        self.AUTH_HEADERS = {
            "Authorization": f"Bearer {self.TOKEN}"
        }

    def get_prices(self):
        response = requests.get(f"{self.BASE_URL}{self.PRICES_ENDPOINT}", headers=self.AUTH_HEADERS)
        response.raise_for_status()
        return response.json()["prices"]

    def update_iata_code(self, row):
        body = {
            "price": {
                "iataCode": row['iataCode']
            }
        }
        requests.put(f"{self.BASE_URL}{self.PRICES_ENDPOINT}/{row['id']}", headers=self.AUTH_HEADERS, json=body)

    def update_price(self, row, price):
        body = {
            "price": {
                "lowestPrice": price
            }
        }
        requests.put(f"{self.BASE_URL}{self.PRICES_ENDPOINT}/{row['id']}", headers=self.AUTH_HEADERS, json=body)

    def add_user(self, user: User):
        body = {
            "user": {
                "firstName": user.first_name,
                "lastName": user.first_name,
                "email": user.email
            }
        }
        response = requests.post(f"{self.BASE_URL}{self.USERS_ENDPOINT}", headers=self.AUTH_HEADERS, json=body)
        print(response)
