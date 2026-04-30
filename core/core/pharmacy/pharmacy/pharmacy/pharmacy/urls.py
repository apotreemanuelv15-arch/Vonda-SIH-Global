from django.urls import path
from . import views

urlpatterns = [
    # Cette ligne lie l'adresse 'inventaire/' à votre fonction dans views.py
    path('inventaire/', views.liste_medicaments, name='liste_medicaments'),
]
