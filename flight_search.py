import requests
from datetime import datetime as dt, timedelta

from pyshorteners.exceptions import ShorteningErrorException
from requests import ReadTimeout

from flight_data import FlightData
import pyshorteners
from dotenv import load_dotenv
import os

class FlightSearch:
    """
    This class provides methods for searching flights using Kiwi API.
    
    Attributes:
        - API_KEY: The API key to access Kiwi API. It's obtained from .env file.
        - BASE_URL: Base URL of Kiwi API.
        - QUERY_LOCATIONS: Endpoint for querying locations in Kiwi API.
        - SEARCH: Endpoint for search flights in Kiwi API.
        - HEADERS: Headers used when making HTTP requests to Kiwi API.
    """

    def __init__(self):
        """
        Initializes a new instance of FlightSearch.

        Loads environment variables from .env file, sets up API key and base URLs.
        """
        load_dotenv()
        self.API_KEY = os.getenv("KIWI_API_KEY")
        self.BASE_URL = "https://tequila-api.kiwi.com"
        self.QUERY_LOCATIONS = "/locations/query"
        self.SEARCH = "/v2/search"
        self.HEADERS = headers = {
            "apikey": self.API_KEY,
        }

    def get_iata_code(self, city):
        """
        Returns IATA code for given city name.

        Args:
            - city (str): Name of the city whose IATA code we want.

        Returns:
            str: IATA code corresponding to given city.
        """
        params = {
            "term": city,
            "location_types": "city"
        }
        response = requests.get(f"{self.BASE_URL}{self.QUERY_LOCATIONS}", params=params, headers=self.HEADERS)
        response.raise_for_status()
        locations = response.json()
        return locations["locations"][0]["code"]

    def search_flight(self, from_city, to_city, max_stopovers=0):
        """
        Searches for cheapest available flights between two cities within next 6 months.

        Args:
            - from_city (str): City where you start your journey.
            - to_city (str): Destination city.
            - max_stopovers (int): Maximum number of stopovers allowed. Defaults to 0.

        Returns:
            - FlightData object if a suitable flight found else None.
        """

        # Check that both 'from_city' and 'to_city' are not empty strings or none
        if not isinstance(from_city, str) or len(from_city.strip()) == 0:
            raise ValueError("Invalid value provided for 'from_city'. Please provide valid string.")

        if not isinstance(to_city, str) or len(to_city.strip()) == 0:
            raise ValueError("Invalid value provided for 'to_city'. Please provide valid string.")
        
        # Ensure max_stopover is an integer greater than equal to zero 
        if not isinstance(max_stopovers, int) or max_stopovers < 0:
            raise ValueError("'max_stopovers' should be a non-negative integer.")

        today = dt.now()
        tomorrow = (today + timedelta(days=7)).strftime("%d/%m/%Y")
        date_in_six_months = (today + timedelta(days=180)).strftime("%d/%m/%Y")

        params = {
                "fly_from": self.get_iata_code(from_city),
                "fly_to": self.get_iata_code(to_city),
                "date_from": tomorrow,
                "date_to": date_in_six_months,
                "nights_in_dst_from": 5,
                "nights_in_dst_to": 20,
                "curr": "USD",
                "max_stopovers": max_stopovers,
                "limit": 1
            }

        response = requests.get(f"{self.BASE_URL}{self.SEARCH}", params=params, headers=self.HEADERS)
        try:
            response.raise_for_status()  
        except Exception as e:
            print(e) 
            return None 

        results = response.json()

        type_tiny = pyshorteners.Shortener()

        if int(results['_results']) > 0:
            result = results['data'][0]

            step_over_city = None
            if max_stopovers > 0:
                step_over_city = result["route"][0]["cityTo"]
                
            link = None
            try:
                link = type_tiny.tinyurl.short(result["deep_link"])
            except ReadTimeout:
                link = result["deep_link"]  

            fecha_salida = result['route'][0]['local_arrival']
            fecha_regreso = result['route'][-1]['local_arrival']

            return FlightData(
                    result["flyFrom"],
                    result["flyTo"],
                    result["cityFrom"], 
                    result["cityTo"], 
                    result["price"], 
                    fecha_salida, 
                    fecha_regreso, 
                    step_over_city, 
                    result["route"][0]["airline"], 
                    link
                )
        else:
            return None  