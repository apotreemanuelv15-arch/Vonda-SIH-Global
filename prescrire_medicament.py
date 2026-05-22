import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pharmacy.models import Patient, Consultation, Medicament, Prescription

def ajouter_prescription_terminal():
    print("\n--- ✍️ ZONE DE PRESCRIPTION MÉDICALE (SÉCURISÉE) ---")
    nom_patient = input("Rechercher le patient (Nom complet) : ")
    
    try:
        patient = Patient.objects.get(nom_complet__icontains=nom_patient)
        # On récupère la dernière consultation de ce patient
        consultation = Consultation.objects.filter(patient=patient).latest('date_consultation')
        
        print(f"✅ Consultation trouvée du {consultation.date_consultation.strftime('%d/%m/%Y')}")
        print(f"🩺 Motif : {consultation.motif}")
        
        nom_med = input("\nNom du médicament à prescrire : ")
        medicament = Medicament.objects.get(nom__icontains=nom_med)
        
        posologie = input("Posologie (ex: 1 matin/1 soir) : ")
        duree = input("Durée du traitement (ex: 5 jours) : ")
        
        # Création de la prescription
        Prescription.objects.create(
            consultation=consultation,
            medicament=medicament,
            posologie=posologie,
            duree_traitement=duree
        )
        
        print(f"\n✅ Prescription de {medicament.nom} enregistrée pour le patient.")
        
    except Patient.DoesNotExist:
        print("❌ Patient non trouvé.")
    except Medicament.DoesNotExist:
        print("❌ Médicament non trouvé en stock.")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    ajouter_prescription_terminal()