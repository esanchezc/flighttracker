class FlightData:
    def __init__(self, departure_airport, arrival_airport, from_city, to_city, price, local_departure, local_arrival,
                 step_over_city, airline, link):
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.from_city = from_city
        self.to_city = to_city
        self.local_departure = local_departure.split("T")[0]
        self.local_arrival = local_arrival.split("T")[0]
        self.price = price
        self.step_over_city = step_over_city
        self.airline = airline
        self.link = link

    def get_flight_data(self):
        msg = f"${self.price} saliendo de {self.from_city}-{self.departure_airport} " \
              f"hacia {self.to_city}-{self.arrival_airport}"
        if self.step_over_city and self.step_over_city != self.to_city:
            msg = f"{msg} via {self.step_over_city} with {self.airline}"
        msg = f"{msg} del {self.local_departure} al {self.local_arrival} {self.link}"
        return msg
