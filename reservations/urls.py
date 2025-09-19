from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('flight/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('destination/<int:dest_id>/', views.destination_detail, name='destination_detail'),
    path('weather/<int:dest_id>/', views.weather, name='weather'),
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('create-checkout-session/<int:booking_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('success/<int:booking_id>/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
]