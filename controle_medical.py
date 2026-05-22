import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pharmacy.models import Consultation

def superviser_consultations():
    aujourd_hui = timezone.now().date()
    consults = Consultation.objects.filter(date_consultation__date=aujourd_hui)

    if not consults.exists():
        print("--- 📭 Aucune consultation à réviser aujourd'hui. ---")
        return

    print(f"\n=== 🩺 SUPERVISION MÉDICALE - {aujourd_hui} ===")
    print(f"Nombre de cas à réviser : {consults.count()}\n")

    for c in consults:
        print(f"--- PATIENT : {c.patient.nom_complet} ---")
        print(f"Médecin traitant : {c.medecin.username}")
        print(f"Diagnostic initial : {c.diagnostic}")
        print(f"Observations actuelles : {c.observations or 'Aucune'}")
        
        reponse = input("\n📝 Ajouter une observation du Médecin Général ? (Laissez vide pour passer) : ")
        
        if reponse.strip():
            # On ajoute l'observation avec la mention du superviseur
            horodatage = timezone.now().strftime("%H:%M")
            nouvelle_obs = f"[{horodatage} - Médecin Général] : {reponse}"
            
            if c.observations:
                c.observations += f"\n{nouvelle_obs}"
            else:
                c.observations = nouvelle_obs
            
            c.save()
            print("✅ Observation enregistrée et gravée dans le dossier.")
        else:
            print("⏩ Passage au cas suivant...")
        print("-" * 40)

    print("\n✅ Session de supervision terminée. N'oubliez pas de régénérer le rapport !")

if __name__ == "__main__":
    superviser_consultations()