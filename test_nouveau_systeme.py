import os
import django
from django.utils import timezone
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pharmacy.models import Patient, Consultation, Medicament, User

def test_initial():
    # 1. Récupérer l'utilisateur que vous venez de créer
    user_admin = User.objects.get(username='admin')
    
    # 2. Créer un médicament de test
    med, _ = Medicament.objects.get_or_create(
        nom="Paracetamol", 
        defaults={'prix_unitaire': 2, 'quantite_stock': 100, 'seuil_alerte': 10}
    )

    # 3. Créer un patient avec TELEPHONE et SUIVI SPÉCIALISÉ (CPN)
    rdv = date.today() + timedelta(days=1)
    patient, _ = Patient.objects.get_or_create(
        nom_complet="Marie Kalunga",
        defaults={
            'telephone': "+244900000000",
            'type_suivi': 'CPN',
            'tension_arterielle': '12/8',
            'date_prochain_rdv': rdv
        }
    )

    # 4. Créer une consultation avec un diagnostic
    Consultation.objects.create(
        patient=patient,
        medecin=user_admin,
        motif="Suivi de grossesse 3eme mois",
        diagnostic="Evolution normale",
        observations="Rien à signaler, bon état général."
    )

    print(f"✅ Patient '{patient.nom_complet}' enregistré avec succès.")
    print(f"✅ Téléphone : {patient.telephone}")
    print(f"✅ Type de suivi : {patient.get_type_suivi_display()}")
    print(f"✅ Consultation signée par l'utilisateur : {user_admin.username}")

if __name__ == "__main__":
    test_initial()