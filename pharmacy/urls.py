from django.urls import path
from . import views

urlpatterns = [
    # Route de l'inventaire général
    path('inventaire/', views.inventaire, name='inventaire'),
    
    # Nouvelle route pour le centre de distribution de gros
    path('vente-gros/', views.passer_vente_gros, name='passer_vente_gros'),
]