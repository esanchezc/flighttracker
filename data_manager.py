import requests
from user import User


class DataManager:
    """
    This class provides methods to interact with a Sheety API.

    Attributes:
        BASE_URL (str): The base URL of the Sheety API.
        PRICES_ENDPOINT (str): The endpoint for prices in the Sheety API.
        USERS_ENDPOINT (str): The endpoint for users in the Sheety API.
        TOKEN (str): The token used for authentication with the Sheety API.
        AUTH_HEADERS (dict): A dictionary containing the headers needed for authenticated requests.
    """

    def __init__(self):
        self.BASE_URL = (
            "https://api.sheety.co/102369f1e8e69906cd018849bc15350e/flightDeals"
        )
        self.PRICES_ENDPOINT = "/prices"
        self.USERS_ENDPOINT = "/users"
        self.TOKEN = "esanchez_flight_search"
        self.AUTH_HEADERS = {"Authorization": f"Bearer {self.TOKEN}"}

    def get_prices(self) -> dict:
        """
        Fetch all available flight deals from the API.

        Returns:
            dict: All available flight deals as per the response from the API.

        Raises:
            Exception: If there's an error fetching data from the API, this exception will be raised.
        """
        url = f"{self.BASE_URL}{self.PRICES_ENDPOINT}"
        try:
            response = requests.get(url, headers=self.AUTH_headers)
            response.raise_for_status()
            return response.json()["prices"]
        except Exception as e:
            print(f"Error fetching prices: {str(e)}")

    def _update_row(self, row_id, data):
        """
        Update a specific record on the API.

        Args:
            row_id (int): ID of the record that needs updating.
            data (dict): New values to update the existing ones.

        Returns:
            None

        Raises:
            Exception: If there's an issue while making PUT request or parsing JSON.
        """
        url = f"{self.BASE_URL}{self.PRICES_ENDPOINT}/{row_id}"
        body = {"price": data}
        try:
            requests.put(url, headers=self.AUTH.Headers, json=body)
        except Exception as e:
            print(f"Error updating row: {str(e)}")

    def update_iata_code(self, row):
        """
        Updates IATA Code field of given row using internal method `_update_row`.

        Args:
            row (dict): Dictionary representing details about flight deal including 'id' & 'iataCode'.
        """
        # Passing iataCode value directly because it already exists within `row`
        # No need for creating another variable like price which isn't present initially
        self._update_row(row["id"], {"iataCode": row["iataCode"]})

    def update_price(self, row, price):
        """
        Updates Price field of given row using internal method `_update_row`.

        Args:
            row (dict): Dictionary representing details about flight deal including 'id'.
            price (float/int): LowestPrice value to be updated into respective record.
        """
        self._update_row(row["id"], {"lowestPrice": price})

    def add_user(self, user: User):
        """
        Adds new user information onto Users endpoint at provided API.

        Args:
            user (User object): Object created from User Class holding required properties - first_name, last_name, email

        Returns:
            str: Response message indicating successful addition.
        """
        body = {
            "user": {
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
            }
        }
        url = f"{self.BASE_URL}{self.USERS_ENDPOINT}"
        try:
            response = requests.post(url, headers=self.AUTH_HEADERS, json=body)
            print(response.text)
        except Exception as e:
            print(f"Error adding user: {str(e)}")
