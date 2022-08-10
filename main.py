import json
import sys

from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager

dm = DataManager()
fs = FlightSearch()
nm = NotificationManager()

continent = "asia"
if len(sys.argv) > 1:
    continent = str(sys.argv[1]).lower()

with open(f"destinations/{continent}.json", "r") as destinations_file:
    destination_data = json.load(destinations_file)
    destinations = destination_data["destinations"]
    text = None
    for destination in destinations.values():
        if not destination.get("iataCode"):
            destination["iataCode"] = fs.get_iata_code(destination["city"])
            destinations[destination["city"]]["iataCode"] = destination["iataCode"]
        new_low_price_flight = None
        for depart_city in destination_data["departure_cities"]:
            flight = fs.search_flight(depart_city, destination["iataCode"], 2)
            if flight:
                if not new_low_price_flight or flight.price < new_low_price_flight.price:
                    new_low_price_flight = flight
        if new_low_price_flight and new_low_price_flight.price < destination['lowestPrice']:
            destinations[destination["city"]]["lowestPrice"] = new_low_price_flight.price
            flight_details = new_low_price_flight.get_flight_data()
            text = f"{text}\n{flight_details}"
            print(flight_details)
if text is not None:
    destination_data["destinations"] = destinations
    with open(f"destinations/{continent}.json", "w+") as destinations_file:
        json.dump(destination_data, destinations_file)
    nm.send_email(text)
else:
    print("No new low prices found :(")

