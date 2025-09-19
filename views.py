from django.shortcuts import render, redirect

def home(request):
    from reservations.models import Flight
    flights = Flight.objects.all()
    return render(request, 'home.html', {'flights': flights})

def about(request):
    return render(request, 'about.html')