from django.urls import path
from . import views

urlpatterns = [
    # 📦 Route de l'inventaire général
    path('inventaire/', views.inventaire, name='inventaire'),

    # 🏢 Routes pour le centre de distribution de gros
    path('vente-gros/', views.passer_vente_gros, name='passer_vente_gros'),
    path('facture-gros/<int:vente_id>/', views.afficher_facture_gros, name='afficher_facture_gros'),

    # 💊 Routes de la Pharmacie de Jour (Vente au Détail)
    path('vente-detail/', views.passer_vente_detail, name='passer_vente_detail'),
    path('facture-detail/<int:vente_id>/', views.afficher_facture_detail, name='afficher_facture_detail'),

    # 🚚 Routes pour le transfert Inter-Établissements
    path('transfert/', views.passer_transfert, name='passer_transfert'),
    path('bon-transfert/<int:vente_id>/<int:etab_id>/', views.afficher_bon_transfert, name='afficher_bon_transfert'),

    # 📊 Route du Journal de Surveillance de Flux Logistique
    path('rapport-flux/', views.rapport_flux, name='rapport-flux'),

    # 🔮 Interface Graphique de l'Hologramme IA (Web interne)
    path('hologramme-ia/', views.hologramme_ia_view, name='hologramme_ia'),

    # 📡 API d'arrière-plan pour la recherche Radar Topographique
    path('api/radar-ia/', views.API_recherche_radar_ia, name='api_recherche_radar_ia'),

    # 📡 Webhook officiel pour intercepter et répondre aux messages WhatsApp Twilio
    path('whatsapp/webhook/', views.twilio_webhook, name='twilio_webhook'),
    
    # 📞 Webhook officiel pour intercepter et répondre aux Appels Vocaux
    path('voice/webhook/', views.twilio_voice_webhook, name='twilio_voice_webhook'),
]



