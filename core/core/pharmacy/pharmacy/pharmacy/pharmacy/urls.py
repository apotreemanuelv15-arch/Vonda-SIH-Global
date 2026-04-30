from django.urls import path
from . import views

urlpatterns = [
    # Chemin pour la liste : http://.../pharmacy/inventaire/
    path('inventaire/', views.liste_medicaments, name='liste_medicaments'),
    
    # Chemin pour l'ajout : http://.../pharmacy/ajouter/
    path('ajouter/', views.ajouter_medicament, name='ajouter_medicament'),
]
