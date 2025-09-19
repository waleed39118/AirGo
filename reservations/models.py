from django.db import models
from django.contrib.auth.models import User

class Destination(models.Model):
    city_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.city_name}, {self.country}"

class TourSpot(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    temperature = models.CharField(max_length=50)
    weather_forecast = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Flight(models.Model):
    flight_number = models.CharField(max_length=20)
    origin = models.ForeignKey(Destination, related_name='departures', on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, related_name='arrivals', on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.flight_number} from {self.origin.city_name} to {self.destination.city_name}"

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    status_choices = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='Pending')
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.name} - {self.flight.flight_number}"