import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pharmacy.models import Patient, Prescription, Vente, Medicament

def servir_patient():
    print("\n--- 💊 PHARMACIE VONDA SIH : SERVICE DES ORDONNANCES ---")
    nom_recherche = input("Nom du patient à servir : ")
    
    # Trouver le patient et sa dernière prescription non servie
    prescriptions = Prescription.objects.filter(
        consultation__patient__nom_complet__icontains=nom_recherche
    ).order_by('-consultation__date_consultation')

    if not prescriptions.exists():
        print("❌ Aucune ordonnance trouvée pour ce patient.")
        return

    print(f"\n📋 Ordonnance trouvée pour : {prescriptions[0].consultation.patient.nom_complet}")
    total_a_payer = 0
    items_a_vendre = []

    for p in prescriptions:
        med = p.medicament
        print(f"- {med.nom} | Posologie : {p.posologie} | Prix : {med.prix_unitaire} $")
        
        # Vérification du stock
        if med.quantite_stock <= 0:
            print(f"   ⚠️ RUPTURE DE STOCK pour {med.nom} !")
            continue
            
        confirmer = input(f"  Servir {med.nom} ? (o/n) : ").lower()
        if confirmer == 'o':
            # On prépare la vente
            items_a_vendre.append((med, 1)) # Ici on assume 1 boîte/unité par défaut
            total_a_payer += med.prix_unitaire

    if not items_a_vendre:
        print("🚫 Aucun médicament servi.")
        return

    print(f"\n💰 TOTAL À PERCEVOIR : {total_a_payer} $")
    valider = input("Confirmer la perception des fonds et la sortie de stock ? (o/n) : ").lower()

    if valider == 'o':
        for med, qte in items_a_vendre:
            # 1. Mise à jour du stock
            med.quantite_stock -= qte
            med.save()

            # 2. Enregistrement de la vente
            Vente.objects.create(
                medicament=med,
                quantite_vendue=qte,
                prix_total=med.prix_unitaire * qte,
                date_vente=timezone.now()
            )
        print(f"✅ Vente enregistrée. Stock mis à jour. Patient servi.")
    else:
        print("❌ Opération annulée.")

if __name__ == "__main__":
    servir_patient()