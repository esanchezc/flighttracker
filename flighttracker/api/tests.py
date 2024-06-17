from decimal import Decimal
from django.test import TestCase
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import resolve, reverse
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token

from tracker.models import City, FlightAlert, Route
from .views import (
    CityDetail,
    CityList,
    FlightAlertDetail,
    FlightAlertList,
    LoginView,
    LogoutView,
    RegisterView,
)


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            "testuser", "testuser@example.com", "testpassword"
        )

    def test_login_success(self):
        request = self.factory.post(
            "/login/", {"username": "testuser", "password": "testpassword"}
        )
        response = LoginView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)
        self.assertIn("email", response.data)

    def test_login_failure(self):
        request = self.factory.post(
            "/login/", {"username": "testuser", "password": "wrongpassword"}
        )
        response = LoginView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        request = self.factory.post("/login/", {"username": "testuser"})
        response = LoginView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_creation(self):
        request = self.factory.post(
            "/login/", {"username": "testuser", "password": "testpassword"}
        )
        response = LoginView.as_view()(request)
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.data["token"], token.key)


class LogoutViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            "testuser", "testuser@example.com", "testpassword"
        )
        self.token = Token.objects.create(user=self.user)

    def test_logout_success(self):
        request = self.factory.post("/logout/")
        force_authenticate(request, user=self.user)
        response = LogoutView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated(self):
        request = self.factory.post("/logout/")
        response = LogoutView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_token_deleted(self):
        request = self.factory.post(
            "/logout/", HTTP_AUTHORIZATION="Token " + self.token.key
        )
        force_authenticate(request, user=self.user)
        response = LogoutView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=self.user).exists())


class RegisterViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_register_success(self):
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
        }
        request = self.factory.post("/register/", data)
        response = RegisterView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)
        self.assertIn("email", response.data)
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertTrue(Token.objects.filter(user__username="testuser").exists())

    def test_register_failure_missing_fields(self):
        data = {"username": "testuser", "email": "testuser@example.com"}
        request = self.factory.post("/register/", data)
        response = RegisterView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_failure_invalid_email(self):
        data = {
            "username": "testuser",
            "email": "invalid_email",
            "password": "testpassword",
        }
        request = self.factory.post("/register/", data)
        response = RegisterView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_failure_duplicate_username(self):
        User.objects.create_user("testuser", "testuser@example.com", "testpassword")
        data = {
            "username": "testuser",
            "email": "testuser2@example.com",
            "password": "testpassword",
        }
        request = self.factory.post("/register/", data)
        response = RegisterView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)


class CityListTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_get_all_cities(self):
        City.objects.create(name="Test City 1", iata_code="TC1")
        City.objects.create(name="Test City 2", iata_code="TC2")
        request = self.factory.get("/cities/")
        response = CityList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_post_city_success(self):
        data = {"name": "New Test City", "iata_code": "NTC"}
        request = self.factory.post("/cities/", data)
        response = CityList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("name", response.data)
        self.assertIn("iata_code", response.data)
        self.assertTrue(
            City.objects.filter(name="New Test City", iata_code="NTC").exists()
        )

    def test_post_city_failure_missing_fields(self):
        data = {}
        request = self.factory.post("/cities/", data)
        response = CityList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("iata_code", response.data)

    def test_post_city_failure_invalid_data(self):
        data = {"name": "", "iata_code": ""}
        request = self.factory.post("/cities/", data)
        response = CityList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("iata_code", response.data)

    def test_post_city_failure_duplicate_city(self):
        City.objects.create(name="Test City", iata_code="TC")
        data = {"name": "Test City", "iata_code": "TC"}
        request = self.factory.post("/cities/", data)
        response = CityList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("iata_code", response.data)


class CityDetailTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.city = City.objects.create(name="Test City", iata_code="TC")

    def test_get_city(self):
        request = self.factory.get("/cities/{}/".format(self.city.pk))
        response = CityDetail.as_view()(request, pk=self.city.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertIn("iata_code", response.data)

    def test_put_city(self):
        data = {"name": "Updated Test City", "iata_code": "UTC"}
        request = self.factory.put("/cities/{}/".format(self.city.pk), data)
        response = CityDetail.as_view()(request, pk=self.city.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertIn("iata_code", response.data)
        self.city.refresh_from_db()
        self.assertEqual(self.city.name, "Updated Test City")
        self.assertEqual(self.city.iata_code, "UTC")

    def test_put_city_failure_invalid_data(self):
        data = {"name": "", "iata_code": ""}
        request = self.factory.put("/cities/{}/".format(self.city.pk), data)
        response = CityDetail.as_view()(request, pk=self.city.pk)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("iata_code", response.data)

    def test_delete_city(self):
        request = self.factory.delete("/cities/{}/".format(self.city.pk))
        response = CityDetail.as_view()(request, pk=self.city.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(City.objects.filter(pk=self.city.pk).exists())


class RouteTest(TestCase):
    def setUp(self):
        self.city1 = City.objects.create(name="City1", iata_code="C1")
        self.city2 = City.objects.create(name="City2", iata_code="C2")

    def test_create_route(self):
        route = Route.objects.create(
            departure_city=self.city1, destination_city=self.city2, lowest_price=200
        )
        self.assertEqual(route.departure_city, self.city1)
        self.assertEqual(route.destination_city, self.city2)
        self.assertEqual(route.lowest_price, 200)

    def test_update_route(self):
        route = Route.objects.create(
            departure_city=self.city1, destination_city=self.city2, lowest_price=200
        )
        route.lowest_price = 250
        route.save()
        self.assertEqual(route.lowest_price, 250)

    def test_delete_route(self):
        route = Route.objects.create(
            departure_city=self.city1, destination_city=self.city2, lowest_price=200
        )
        route_id = route.id
        route.delete()
        self.assertFalse(Route.objects.filter(id=route_id).exists())


class FlightAlertListTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        self.city1 = City.objects.create(name="City1", iata_code="C1")
        self.city2 = City.objects.create(name="City2", iata_code="C2")

    def tearDown(self):
        City.objects.all().delete()
        User.objects.all().delete()
        Route.objects.all().delete()
        FlightAlert.objects.all().delete()

    def test_post_flight_alert(self):
        request = self.factory.post(
            "/flight-alerts/",
            {
                "departure_city": self.city1.id,
                "destination_cities": [self.city2.id],
            },
        )
        request.user = self.user
        response = FlightAlertList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_flight_alert_failure_invalid_data(self):
        request = self.factory.post(
            "/flight-alerts/",
            {
                "departure_city": self.city1.id,
            },
        )
        request.user = self.user
        response = FlightAlertList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("destination_cities", response.data)


class FlightAlertDetailTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        self.city1 = City.objects.create(name="City1", iata_code="C1")
        self.city2 = City.objects.create(name="City2", iata_code="C2")
        self.flight_alert = FlightAlert.objects.create(
            user=self.user, departure_city=self.city1
        )
        self.flight_alert.destination_cities.add(self.city2)

    def tearDown(self):
        City.objects.all().delete()
        User.objects.all().delete()
        Route.objects.all().delete()
        FlightAlert.objects.all().delete()

    def test_get_flight_alert(self):
        request = self.factory.get("/flight-alerts/{}/".format(self.flight_alert.id))
        request.user = self.user
        response = FlightAlertDetail.as_view()(request, pk=self.flight_alert.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["departure_city"], self.city1.id)
        self.assertEqual(response.data["destination_cities"], [self.city2.id])

    def test_put_flight_alert(self):
        request = self.factory.put(
            "/flight-alerts/{}/".format(self.flight_alert.id),
            {
                "departure_city": self.city1.id,
                "destination_cities": [self.city2.id],
            },
        )
        request.user = self.user
        response = FlightAlertDetail.as_view()(request, pk=self.flight_alert.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flight_alert.refresh_from_db()

    def test_delete_flight_alert(self):
        request = self.factory.delete("/flight-alerts/{}/".format(self.flight_alert.id))
        request.user = self.user
        response = FlightAlertDetail.as_view()(request, pk=self.flight_alert.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FlightAlert.objects.filter(id=self.flight_alert.id).exists())