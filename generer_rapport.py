import os
import django
from django.db.models import Sum, F, Count
from django.utils import timezone
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pharmacy.models import Medicament, Vente, Consultation, Patient

def masquer_nom(nom):
    """Transforme 'Marie Kalunga' en 'M. K.' pour l'anonymat"""
    parties = nom.split()
    if len(parties) >= 2:
        return f"{parties[0][0]}. {parties[1][0]}."
    return f"{nom[0]}***"

def creer_rapport_vonda_international(anonyme=True):
    aujourd_hui = timezone.now().date()
    demain = aujourd_hui + timedelta(days=1)
    
    # --- 💰 SECTION FINANCIÈRE ---
    ventes = Vente.objects.filter(date_vente__date=aujourd_hui)
    ca_pharmacie = ventes.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
    
    nb_sms = Patient.objects.filter(date_prochain_rdv=demain).count()
    ca_sms = nb_sms * 0.50
    ca_total = float(ca_pharmacie) + float(ca_sms)

    # --- 🏥 SECTION SANTÉ PUBLIQUE ---
    consults = Consultation.objects.filter(date_consultation__date=aujourd_hui)
    stats_suivi = Patient.objects.values('type_suivi').annotate(total=Count('id'))

    with open("BILAN_VONDA_INTERNATIONAL.txt", "w", encoding="utf-8") as f:
        f.write("======================================================\n")
        f.write(f"       VONDA SIH - RAPPORT D'ACTIVITÉ : {aujourd_hui}\n")
        f.write(f"       MODE : {'ANONYME (SÉCURISÉ)' if anonyme else 'COMPLET'}\n")
        f.write("======================================================\n\n")
        
        f.write(f"💵 REVENUS GÉNÉRÉS : {ca_total} $\n")
        f.write(f"   (Pharmacie: {ca_pharmacie}$ | SMS: {ca_sms}$)\n\n")
        
        f.write("--- 📊 RÉPARTITION DES SOINS ---\n")
        for s in stats_suivi:
            type_nom = dict(Patient.TYPES_SUIVI).get(s['type_suivi'])
            f.write(f"- {type_nom} : {s['total']} patients suivis\n")
        
        f.write("\n--- 📝 LISTE DES ACTES (TRAÇABILITÉ) ---\n")
        if not consults.exists():
            f.write("Aucune activité enregistrée ce jour.\n")
        else:
            for c in consults:
                # Application de la protection des données
                identite = masquer_nom(c.patient.nom_complet) if anonyme else c.patient.nom_complet
                
                f.write(f"[{c.date_consultation.strftime('%H:%M')}] Patient: {identite}\n")
                f.write(f"   Type: {c.patient.get_type_suivi_display()}\n")
                f.write(f"   Diagnostic: {c.diagnostic}\n")
                f.write(f"   Statut: {c.get_statut_final_display()}\n")
                f.write(f"   ----------\n")

    print(f"\n✅ Rapport généré avec succès en mode {'ANONYME' if anonyme else 'PUBLIC'}.")
    print(f"📄 Fichier : BILAN_VONDA_INTERNATIONAL.txt")

if __name__ == "__main__":
    # Changez True en False si vous voulez voir les noms complets pour usage interne
    creer_rapport_vonda_international(anonyme=True)