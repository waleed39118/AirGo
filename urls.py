from django.contrib import admin
from django.urls import path, include
from reservations import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome, name='welcome'),
    path('', include('reservations.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]