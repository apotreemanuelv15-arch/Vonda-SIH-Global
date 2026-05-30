from django.urls import path
from . import views

urlpatterns = [
    # Route de l'inventaire général
    path('inventaire/', views.inventaire, name='inventaire'),
    
    # Nouvelle route pour le centre de distribution de gros
    path('vente-gros/', views.passer_vente_gros, name='passer_vente_gros'),
    # Nouvelle ligne pour intercepter l'ID de la facture
    path('facture-gros/<int:vente_id>/', views.afficher_facture_gros, name='afficher_facture_gros'),
    # 📡 NOUVELLES LIGNES DE TRANSMISSION (VENTE AU DÉTAIL) :
    path('vente-detail/', views.passer_vente_detail, name='passer_vente_detail'),
    path('facture-detail/<int:vente_id>/', views.afficher_facture_detail, name='afficher_facture_detail'),
]