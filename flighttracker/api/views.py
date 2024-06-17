from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from .serializers import FlightAlertSerializer, UserSerializer, CitySerializer
from tracker.models import City, FlightAlert, Route

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        # logout(request)
        return Response(status=status.HTTP_200_OK)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CityList(APIView):
    def get(self, request):
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CityDetail(APIView):
    def get(self, request, pk):
        city = City.objects.get(pk=pk)
        serializer = CitySerializer(city)
        return Response(serializer.data)

    def put(self, request, pk):
        city = City.objects.get(pk=pk)
        serializer = CitySerializer(city, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        city = City.objects.get(pk=pk)
        city.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FlightAlertList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        flight_alerts = FlightAlert.objects.filter(user=request.user)
        serializer = FlightAlertSerializer(flight_alerts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FlightAlertSerializer(data=request.data)
        if serializer.is_valid():
            flight_alert = serializer.save(user=request.user)
            for destination_city in request.data['destination_cities']:
                route, created = Route.objects.get_or_create(departure_city=flight_alert.departure_city, destination_city_id=destination_city)
                flight_alert.routes.add(route)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FlightAlertDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            flight_alert = FlightAlert.objects.get(pk=pk, user=request.user)
            serializer = FlightAlertSerializer(flight_alert)
            return Response(serializer.data)
        except FlightAlert.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            flight_alert = FlightAlert.objects.get(pk=pk, user=request.user)
            serializer = FlightAlertSerializer(flight_alert, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except FlightAlert.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            flight_alert = FlightAlert.objects.get(pk=pk, user=request.user)
            flight_alert.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FlightAlert.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
