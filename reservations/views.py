from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings

from .forms import RegistrationForm
from .models import Flight, Destination, Booking
import stripe


def welcome(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin:index')
            else:
                return redirect('user_home')
        else:

            return render(request, 'reservations/welcome.html', {'error': 'Invalid credentials'})
    
    return render(request, 'reservations/welcome.html')

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def home(request):
    flights = Flight.objects.all()
    destinations = Destination.objects.all()
    return render(
        request,
        "reservations/home.html",
        {"flights": flights, "destinations": destinations},
    )


@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, "reservations/profile.html", {"bookings": bookings})


@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    booking = Booking.objects.create(user=request.user, flight=flight)
    return redirect("checkout", booking_id=booking.id)


@login_required
def destination_detail(request, dest_id):
    destination = get_object_or_404(Destination, id=dest_id)
    return render(request, "reservations/destination_detail.html", {"destination": destination})


@login_required
def weather(request, dest_id):
    destination = get_object_or_404(Destination, id=dest_id)
    # TODO: integrate weather API here
    weather_data = {"temp": "25°C", "condition": "Sunny"}
    return JsonResponse(weather_data)


@login_required
def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, "reservations/checkout.html", {"booking": booking})


@login_required
def create_checkout_session(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": booking.flight.destination.name},
                    "unit_amount": int(booking.flight.price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri("/profile/"),
        cancel_url=request.build_absolute_uri("/checkout/{}/".format(booking.id)),
    )

    return JsonResponse({"id": checkout_session.id})
