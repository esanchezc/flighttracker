import json
from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager


class PriceTracker:
    """
    A class to track prices of flights.

    Attributes:
        data_manager (DataManager): An instance of DataManager for managing destination data.
        flight_searcher (FlightSearch): An instance of FlightSearch for searching flights.
        notification_manager (NotificationManager): An instance of NotificationManager for sending notifications.
    """

    def __init__(self):
        self.data_manager = DataManager()
        self.flight_searcher = FlightSearch()
        self.notification_manager = NotificationManager()

    @staticmethod
    def load_data(continent):
        """
        Load destination data from a JSON file.

        Args:
            continent (str): The name of the continent for which to load data.

        Returns:
            dict: The loaded destination data.
        """
        with open(f"destinations/{continent}.json", "r") as destinations_file:
            return json.load(destinations_file)

    def update_iata_codes(self, continent, destination_data):
        """
        Update IATA codes in the destination data if they are missing.

        Args:
            continent (str): The name of the continent for which to update data.
            destination_data (dict): The destination data containing information about cities and their lowest prices.
        """
        for destination in destination_data["destinations"].values():
            if not destination.get("iataCode"):
                iata_code = self.flight_searcher.get_iata_code(destination["city"])
                destination["iataCode"] = iata_code
                destination_data["destinations"][destination["city"]][
                    "iataCode"
                ] = iata_code
        self.save_destination_data(continent, destination_data)

    def find_lowest_prices(self, continent, destination_data):
        """
        Find the lowest price for each city by comparing it with current prices fetched using FlightSearch.

        Args:
            continent (str): The name of the continent for which to check prices.
            destination_data (dict): The destination data containing information about cities and their lowest prices.
        """
        text = None
        for destination in destination_data["destinations"].values():
            new_low_price_flight = None
            for depart_city in destination_data["departure_cities"]:
                flight = self.flight_searcher.search_flight(
                    depart_city, destination["iataCode"], 2
                )
                if flight and (
                    not new_low_price_flight
                    or flight.price < new_low_price_flight.price
                ):
                    new_low_price_flight = flight

            if (
                new_low_price_flight
                and new_low_price_flight.price < destination["lowestPrice"]
            ):
                destination["lowestPrice"] = new_low_price_flight.price
                flight_details = new_low_price_flight.get_flight_data()
                text = f"{text}\n{flight_details}"
                print(flight_details)

        if text is not None:
            self.send_notification(text)

    def reset_lowest_prices(self, continent, price=1500):
        """
        Reset all the lowest prices in the destination data to a given value.

        Args:
            continent (str): The name of the continent for which to reset prices.
            price (int, optional): The new lowest price. Defaults to 1500.
        """
        destination_data = self.load_data(continent)
        for destination in destination_data["destinations"].values():
            destination["lowestPrice"] = price
        self.save_destination_data(continent, destination_data)

    def save_destination_data(self, continent, data):
        """
        Save the updated destination data back into its corresponding JSON file.

        Args:
            continent (str): The name of the continent for which to save data.
            data (dict): The updated destination data.
        """
        with open(f"destinations/{continent}.json", "w+") as destinations_file:
            json.dump(data, destinations_file)

    def send_notification(self, message):
        """
        Send an email notification through NotificationManager.

        Args:
            message (str): The content of the email.
        """
        self.notification_manager.send_email(message)


if __name__ == "__main__":
    tracker = PriceTracker()

    RESET_PRICES = True

    continent = sys.argv[1].lower() if len(sys.argv) > 1 else "asia"

    if RESET_PRICES:
        tracker.reset_lowest_prices(continent)

    destination_data = tracker.load_data(continent)
    tracker.update_iata_codes(continent, destination_data)
    tracker.find_lowest_prices(continent, destination_data)
