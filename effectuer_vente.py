import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pharmacy.models import Medicament, Vente

def simuler_vente_avec_historique(nom_med, quantite):
    try:
        med = Medicament.objects.get(nom__icontains=nom_med)
        
        if med.quantite_stock >= quantite:
            # 1. Calcul du prix au moment de la vente
            total = med.prix_unitaire * quantite
            
            # 2. Création de la trace dans l'historique
            Vente.objects.create(
                medicament=med,
                quantite_vendue=quantite,
                prix_total=total
            )
            
            # 3. Mise à jour du stock
            med.quantite_stock -= quantite
            med.save()
            
            print(f"✅ SUCCÈS : {quantite} {med.nom} vendus pour {total} $")
        else:
            print(f"❌ ÉCHEC : Stock insuffisant pour {med.nom}")
            
    except Medicament.DoesNotExist:
        print("❌ ÉCHEC : Médicament non trouvé.")

if __name__ == "__main__":
    # Test : on vend 2 unités de votre premier médicament
    # Remplacez 'Amoxicilline' par un nom qui existe dans votre base
    simuler_vente_avec_historique("Amoxicilline", 240)