from django.urls import path
from . import views

urlpatterns = [
    # ACCÈS PHARMACIE
    path('inventaire/', views.liste_medicaments, name='liste_medicaments'),
    path('ajouter/', views.ajouter_medicament, name='ajouter_medicament'),
    path('vendre/<int:pk>/', views.effectuer_vente, name='effectuer_vente'),
    path('historique/', views.historique_ventes, name='historique_ventes'),
    
    # ACCÈS PATIENTS
    path('patients/', views.liste_patients, name='liste_patients'),
    path('patients/nouveau/', views.ajouter_patient, name='ajouter_patient'),
]
