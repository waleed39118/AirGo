from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("home/", views.home, name="home"),
    path("profile/", views.profile, name="profile"),
    path("book/<int:flight_id>/", views.book_flight, name="book_flight"),
    path("destination/<int:dest_id>/", views.destination_detail, name="destination_detail"),
    path("weather/<int:dest_id>/", views.weather, name="weather"),
    path("checkout/<int:booking_id>/", views.checkout, name="checkout"),
    path("create-checkout-session/<int:booking_id>/", views.create_checkout_session, name="create_checkout_session"),
]

