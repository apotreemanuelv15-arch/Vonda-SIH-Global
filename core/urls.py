from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView  # Pour rediriger automatiquement

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='inventaire/', permanent=True)), # Si on tape l'adresse brute, hop ! Direction l'inventaire
    path('', include('pharmacy.urls')), 
]