from datetime import datetime
from dataclasses import dataclass


@dataclass
class FlightData:
    """
    A class to represent flight data.

    Attributes:
        departure_airport (str): The airport from which the flight departs.
        arrival_airport (str): The airport at which the flight arrives.
        from_city (str): The city from which the flight originates.
        to_city (str): The destination city of the flight.
        price (float): The cost of the flight.
        local_departure (str): The date and time when the flight departs in ISO format.
        local_arrival (str): The date and time when the flight arrives in ISO format.
        step_over_city (str): Any intermediate stops during the journey. Can be None if there are no stopovers.
        airline (str): The name of the airline operating this flight.
        link (str): An optional URL linking to more information about the flight.

    Methods:
        __post_init__: Converts the dates into a Python `datetime.date` object after initialization.
        __str__: Returns a formatted string representation of the flight details.
    """

    departure_airport: str
    arrival_airport: str
    from_city: str
    to_city: str
    price: float
    local_departure: str
    local_arrival: str
    step_over_city: str
    airline: str
    link: str

    def __post_init__(self):
        """Converts the dates into a Python `datetime.date` object."""
        self.local_departure = datetime.fromisoformat(
            self.local_departure.replace('Z', '+00:00')
        ).date()
        self.local_arrival = datetime.fromisoformat(
            self.local_arrival.replace('Z', '+00:00')
        ).date()

    def get_flight_data(self):
        """Returns a formatted string representation of the flight details."""
        msg = (
            f"${self.price} saliendo de {self.from_city}-{self.departure_airport} "
            f"hacia {self.to_city}-{self.arrival_airport}"
        )

        # Add any layover cities to the message
        if self.step_over_city and self.step_over_city != self.to_city:
            msg = f"{msg} via {self.step_over_city} with {self.airline}"

        # Format the dates for display
        msg = f"{msg} del {self.local_departure.strftime('%d/%m/%Y')} al {self.local_arrival.strftime('%d/%m/%Y')}"

        # Append an external link if available
        if self.link:
            msg += f" {self.link}"

        return msg
