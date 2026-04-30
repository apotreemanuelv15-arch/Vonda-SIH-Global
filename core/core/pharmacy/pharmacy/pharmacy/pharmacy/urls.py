from django.urls import path
from . import views

urlpatterns = [
    path('inventaire/', views.liste_medicaments, name='liste_medicaments'),
    path('ajouter/', views.ajouter_medicament, name='ajouter_medicament'),
    # Route pour vendre un médicament spécifique via son ID
    path('vendre/<int:pk>/', views.effectuer_vente, name='effectuer_vente'),
]
