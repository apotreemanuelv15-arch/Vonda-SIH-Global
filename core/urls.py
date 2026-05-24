from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pharmacy.urls')),  # Oriente directement vers votre pharmacie en page d'accueil
]