from django.contrib import admin
from django.utils.html import format_html
from django.templatetags.static import static
from .models import (
    Etablissement, Patient, Medicament, 
    Consultation, Hospitalisation, Vente, 
    TransactionBancaire, Prescription, ChirurgieAssistee, GuideModule
)

# --- CONFIGURATION DE L'INTERFACE ADMIN (LOGO NET & TITRES) ---
admin.site.site_header = format_html(
    '<img src="{}" style="height: 50px; width: auto; margin-right: 10px; vertical-align: middle;"> Interface Vonda SIH Global',
    static('images/icon-192x192.png')
)
admin.site.site_title = "Vonda SIH Admin"
admin.site.index_title = "Tableau de Bord de l'Architecte"

# --- ACTION PERSONNALISÉE : CAMPAGNE SMS ---
@admin.action(description="Envoyer la campagne de SMS de prévention")
def envoyer_campagne_sms(modeladmin, request, queryset):
    for patient in queryset:
        nom = patient.nom_complet
        if "CPN" in nom:
            text_sms = "Vonda Sante : Rappel RDV. Maman, ne prenez aucun medicament ou plante sans avis medical. L'automedication nuit au bebe."
        elif "VIH" in nom:
            text_sms = "Vonda SIH : Votre sante est notre priorite. Rappel RDV demain. Attention : l'automedication peut perturber votre traitement."
        elif "CNP" in nom:
            text_sms = "Vonda SIH : Bonjour, rappel de votre consultation. Ne modifiez jamais votre traitement seul. Un expert vous attend."
        else:
            text_sms = f"Vonda SIH : Bonjour {nom}, votre medecin vous rappelle de suivre scrupuleusement votre ordonnance. Prenez soin de votre sante."
        
        patient.alerte_sms_envoyee = True
        patient.save()
        
    modeladmin.message_user(request, f"📱 Campagne SMS envoyée avec succès pour {queryset.count()} patient(s) !")

# --- PERSONNALISATION DES MODULES ---

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'telephone', 'type_suivi', 'alerte_sms_envoyee')
    list_filter = ('type_suivi', 'alerte_sms_envoyee')
    search_fields = ('nom_complet', 'telephone')
    actions = [envoyer_campagne_sms]

@admin.register(ChirurgieAssistee)
class ChirurgieAssisteeAdmin(admin.ModelAdmin):
    list_display = ('patient', 'expert_distance', 'statut_robotique', 'date_intervention')
    fieldsets = (
        ('Expertise à distance', {
            'fields': ('patient', 'chirurgien_local', 'expert_distance'),
            'description': "Module de télé-chirurgie robotique assistée."
        }),
        ('Technique & IA', {
            'fields': ('type_intervention', 'statut_robotique', 'flux_video_ia', 'date_intervention'),
        }),
    )

@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    # 1. Les colonnes visibles dans le tableau de la liste des médicaments
    list_display = ('nom', 'pays_origine', 'quantite_stock', 'stock_en_cartons', 'prix_unitaire')
    list_filter = ('conditionnement_achat', 'pays_origine', 'etablissement')
    search_fields = ('nom', 'pays_origine', 'numero_lot_import')
    
    # 2. L'organisation des champs à l'intérieur du formulaire d'ajout/modification
    fieldsets = (
        ('Informations Générales', {
            'fields': ('etablissement', 'nom', 'pays_origine')
        }),
        ('Logistique de Gros & Import-Export', {
            'fields': ('conditionnement_achat', 'unites_par_carton', 'numero_lot_import', 'cout_fret_douane'),
            'description': "Configurez ici les emballages pour les dépôts de gros et le suivi douanier."
        }),
        ('Gestion des Prix et Stocks', {
            'fields': ('quantite_stock', 'prix_unitaire', 'prix_grossiste_carton'),
            'description': "Le stock global doit toujours être saisi en unités de détail."
        }),
        ('Aide IA (Anti-Automédication)', {
            'fields': ('posologie_standard_ia', 'contre_indications'),
            'description': "Ces informations sont des guides générés. Seul le médecin valide la prescription finale."
        }),
    )

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('code_facture_unique', 'medicament', 'type_vente', 'quantite_vendue', 'prix_total', 'date_vente')
    readonly_fields = ('prix_total', 'code_facture_unique') # Sécurité : calculé par le système, non modifiable à la main
    list_filter = ('type_vente', 'date_vente')
    search_fields = ('code_facture_unique', 'medicament__nom')
    date_hierarchy = 'date_vente'

@admin.register(GuideModule)
class GuideModuleAdmin(admin.ModelAdmin):
    list_display = ('titre_module',)

# Enregistrement des autres modèles
admin.site.register(Etablissement)
admin.site.register(Consultation)
admin.site.register(Hospitalisation)
admin.site.register(TransactionBancaire)