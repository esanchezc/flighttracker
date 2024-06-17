from datetime import date
from django.db import models
from django.contrib.auth.models import User

class City(models.Model):
    name = models.CharField(max_length=100)
    iata_code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.iata_code})"

class Route(models.Model):
    departure_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='departure_routes')
    destination_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='arrival_routes')
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2, default=9999.99)

class FlightAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    departure_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='departure_city')
    destination_cities = models.ManyToManyField(City, related_name='destination_cities')
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date(date.today().year + 1, 12, 31))
    routes = models.ManyToManyField(Route, related_name='flight_alerts')

    def __str__(self):
        destination_cities_str = ', '.join(city.name for city in self.destination_cities.all())
        return f"{self.user.username} - {self.departure_city.name} to {destination_cities_str}"

class FlightData(models.Model):
    departure_airport = models.CharField(max_length=10)
    arrival_airport = models.CharField(max_length=10)
    from_city = models.CharField(max_length=100)
    to_city = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    local_departure = models.DateField()
    local_arrival = models.DateField()
    step_over_city = models.CharField(max_length=100, null=True, blank=True)
    airline = models.CharField(max_length=100)
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.from_city} to {self.to_city} on {self.local_departure}"

class UserEmail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
