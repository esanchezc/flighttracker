import requests
from datetime import datetime as dt, timedelta

from pyshorteners.exceptions import ShorteningErrorException
from requests import ReadTimeout

from flight_data import FlightData
import pyshorteners
from dotenv import load_dotenv
import os

class FlightSearch:
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv("KIWI_API_KEY")
        self.BASE_URL = "https://tequila-api.kiwi.com"
        self.QUERY_LOCATIONS = "/locations/query"
        self.SEARCH = "/v2/search"
        self.HEADERS = headers = {
            "apikey": self.API_KEY,
        }

    def get_iata_code(self, city):
        params = {
            "term": city,
            "location_types": "city"
        }
        response = requests.get(f"{self.BASE_URL}{self.QUERY_LOCATIONS}", params=params, headers=self.HEADERS)
        response.raise_for_status()
        locations = response.json()
        return locations["locations"][0]["code"]

    def search_flight(self, from_city, to_city, max_stopovers=0):
        today = dt.now()
        tomorrow = (today + timedelta(days=7)).strftime("%d/%m/%Y")
        date_in_six_months = (today + timedelta(days=180)).strftime("%d/%m/%Y")
        params = {
            "fly_from": from_city,
            "fly_to": to_city,
            "date_from": tomorrow,
            "date_to": date_in_six_months,
            "nights_in_dst_from": 5,
            "nights_in_dst_to": 20,
            "curr": "USD",
            "max_stopovers": max_stopovers,
            "limit": 1
        }
        response = requests.get(f"{self.BASE_URL}{self.SEARCH}", params=params, headers=self.HEADERS)
        response.raise_for_status()
        results = response.json()
        type_tiny = pyshorteners.Shortener()
        if int(results['_results']) > 0:
            result = results['data'][0]
            step_over_city = None
            if max_stopovers > 0:
                step_over_city = result["route"][0]["cityTo"]
            try:
                link = type_tiny.tinyurl.short(result["deep_link"])
            except ReadTimeout:
                link = result["deep_link"]
            except ShorteningErrorException:
                link = result["deep_link"]
            fecha_salida = result['route'][0]['local_arrival']
            fecha_regreso = result['route'][-1]['local_arrival']
            return FlightData(result["flyFrom"], result["flyTo"], result["cityFrom"], result["cityTo"], result["price"],
                              fecha_salida, fecha_regreso, step_over_city, result["route"][0]["airline"], link)
        else:
            return None
