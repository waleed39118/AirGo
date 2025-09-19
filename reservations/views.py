from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.conf import settings
from django.http import JsonResponse
import stripe
import requests

from .models import Destination, Flight, Customer, Booking, TourSpot

def welcome(request):
    return render(request, 'welcome.html')

def home(request):
    flights = Flight.objects.all()
    destinations = Destination.objects.all()
    return render(request, 'home.html', {'flights': flights, 'destinations': destinations})

def search(request):
    search_type = request.GET.get('search_type')
    location = request.GET.get('location') 
    from_id = request.GET.get('from_destination')
    to_id = request.GET.get('to_destination')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    flights = Flight.objects.all()

    if from_id and from_id.isdigit():
        flights = flights.filter(origin_id=int(from_id))
    if to_id and to_id.isdigit():
        flights = flights.filter(destination_id=int(to_id))

    if location:
        flights = flights.filter(
            Q(origin__city_name__icontains=location) |
            Q(destination__city_name__icontains=location)
        )

    if start_date:
        flights = flights.filter(departure_time__gte=start_date)
    if end_date:
        flights = flights.filter(departure_time__lte=end_date)


    if search_type == 'flights':

        pass
    elif search_type == 'destinations':
        destinations = Destination.objects.filter(city_name__icontains=location)
        flights = flights.filter(destination__in=destinations)
    else:
        flights = Flight.objects.none()

    destinations = Destination.objects.all()
    return render(request, 'home.html', {'flights': flights, 'destinations': destinations})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def profile(request):
    return render(request, 'profile.html')

def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        customer, created = Customer.objects.get_or_create(email=email, defaults={'name': name, 'phone': phone})
        booking = Booking.objects.create(customer=customer, flight=flight, status='Pending', paid=False)
        return redirect('checkout', booking_id=booking.id)
    return render(request, 'flight_detail.html', {'flight': flight})

def destination_detail(request, dest_id):
    destination = get_object_or_404(Destination, pk=dest_id)
    tour_spots = TourSpot.objects.filter(destination=destination)
    return render(request, 'tour_spots.html', {'destination': destination, 'tour_spots': tour_spots})

def weather(request, dest_id):
    destination = get_object_or_404(Destination, pk=dest_id)
    api_key = settings.OPENWEATHERMAP_API_KEY
    city = destination.city_name
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_data = {
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon']
        }
    else:
        weather_data = {'temperature': 'N/A', 'description': 'Unavailable', 'icon': ''}
    return render(request, 'weather.html', {'weather': weather_data, 'city': city})

def checkout(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, 'checkout.html', {
        'booking': booking,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY
    })

def create_checkout_session(request, booking_id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    booking = get_object_or_404(Booking, pk=booking_id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': f"Flight {booking.flight.flight_number}"},
                'unit_amount': int(booking.flight.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/success/{booking.id}/'),
        cancel_url=request.build_absolute_uri('/cancel/'),
    )
    return JsonResponse({'id': session.id})

def success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.status = 'Confirmed'
    booking.paid = True
    booking.save()
    return render(request, 'success.html', {'booking': booking})

def cancel(request):
    return render(request, 'cancel.html')