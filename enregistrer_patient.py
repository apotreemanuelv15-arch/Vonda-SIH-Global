import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pharmacy.models import Patient, Consultation
from django.contrib.auth.models import User

def tester_admission():
    # 1. On récupère le compte du "Commandant" (admin)
    admin = User.objects.first() 
    
    # 2. Création d'un patient test
    patient, created = Patient.objects.get_or_create(
        nom_complet="Jean Dupont",
        defaults={'telephone': "+244 900 000 000", 'adresse': "Luanda, Angola"}
    )
    
    # 3. Création de la consultation
    consult = Consultation.objects.create(
        patient=patient,
        medecin=admin,
        motif="Fièvre persistante et maux de tête",
        diagnostic="Suspicion de Paludisme"
    )
    
    print(f"✅ Patient {patient.nom_complet} enregistré.")
    print(f"✅ Consultation signée par le médecin : {admin.username}")

if __name__ == "__main__":
    tester_admission()