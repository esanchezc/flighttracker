from rest_framework import serializers
from django.contrib.auth.models import User
from tracker.models import City, FlightAlert, Route

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'iata_code']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'departure_city', 'destination_city', 'lowest_price']

class FlightAlertSerializer(serializers.ModelSerializer):
    routes = RouteSerializer(many=True, read_only=True)

    class Meta:
        model = FlightAlert
        fields = ['id', 'departure_city', 'destination_cities', 'start_date', 'end_date', 'routes']