from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path("register/", views.RegisterView.as_view()),
    path("cities/", views.CityList.as_view()),
    path("cities/<int:pk>/", views.CityDetail.as_view()),
    path("flight-alerts/", views.FlightAlertList.as_view()),
    path("flight-alerts/<int:pk>/", views.FlightAlertDetail.as_view()),
]
