from django.urls import path
from . import views

urlpatterns = [
    # Inventaire et Ventes
    path('inventaire/', views.inventaire, name='inventaire'),
    path('vente-gros/', views.passer_vente_gros, name='passer_vente_gros'),
    path('facture-gros/<int:vente_id>/', views.afficher_facture_gros, name='afficher_facture_gros'),
    path('vente-detail/', views.passer_vente_detail, name='passer_vente_detail'),
    path('facture-detail/<int:vente_id>/', views.afficher_facture_detail, name='afficher_facture_detail'),
    
    # Logistique et Transferts
    path('transfert/', views.passer_transfert, name='passer_transfert'),
    path('bon-transfert/<int:vente_id>/<int:etab_id>/', views.afficher_bon_transfert, name='afficher_bon_transfert'),
    path('rapport-flux/', views.rapport_flux, name='rapport-flux'),
    
    # Radar et IA
    path('radar/', views.radar_veille_view, name='radar_veille'),
    path('hologramme-ia/', views.hologramme_ia_view, name='hologramme_ia'),
    path('api/radar-ia/', views.API_recherche_radar_ia, name='api_recherche_radar_ia'),
    
    # Webhooks (WhatsApp/Voix)
    path('whatsapp/webhook/', views.twilio_webhook, name='twilio_webhook'),
    path('voice/webhook/', views.twilio_voice_webhook, name='twilio_voice_webhook'),
    
    # Administration et Export (Point A)
    path('admin-veille/', views.admin_veille_view, name='admin_veille'),
    path('admin-veille/export/', views.export_veille_csv, name='export_veille_csv'),
]
