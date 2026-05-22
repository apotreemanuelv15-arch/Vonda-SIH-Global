import os
import django
from django.db.models import Sum
from uuid import uuid4

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pharmacy.models import Transaction, Vente

def synchroniser_finances_partagees():
    print("\n--- 🏦 RÉPARTITION BANCAIRE DES REVENUS (VONDA vs HÔPITAL) ---")
    
    # 1. Récupération des ventes pharmacie
    ca_pharma = Vente.objects.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
    
    # 2. APPLICATION DE LA REDEVANCE LOGICIELLE (Maintenance Vonda)
    # Imaginons 5% sur chaque vente pharma pour votre service
    taux_redevance = 0.05
    gain_vonda_pharma = float(ca_pharma) * taux_redevance
    part_hopital_nette = float(ca_pharma) - gain_vonda_pharma

    # 3. Revenus SMS (100% pour vous, car c'est votre infrastructure)
    # Simulation d'un volume de SMS
    ca_sms = 10.50 # Exemple
    
    gain_total_vonda = gain_vonda_pharma + ca_sms

    # 4. GÉNÉRATION DU RAPPORT DE RÉPARTITION (Audit)
    with open("AUDIT_REDEVAN_VONDA.txt", "w", encoding="utf-8") as f:
        f.write("======================================================\n")
        f.write("       RAPPORT DE RÉPARTITION CONTRACTUELLE\n")
        f.write("======================================================\n\n")
        f.write(f"CHIFFRE D'AFFAIRES PHARMACIE : {ca_pharma} $\n")
        f.write(f"------------------------------------------------------\n")
        f.write(f"PART HÔPITAL (95%)           : {part_hopital_nette:.2f} $\n")
        f.write(f"REDEVANCE LOGICIELLE (5%)    : {gain_vonda_pharma:.2f} $\n")
        f.write(f"REVENUS SERVICES SMS         : {ca_sms:.2f} $\n")
        f.write(f"------------------------------------------------------\n")
        f.write(f"👉 TOTAL À REVERSER À VONDA  : {gain_total_vonda:.2f} $\n\n")
        f.write("Note: Ce rapport sert de base légale pour la facturation\n")
        f.write("de maintenance mensuelle.\n")

    print(f"✅ Audit de répartition généré : AUDIT_REDEVAN_VONDA.txt")
    print(f"💰 Votre gain sécurisé sur cette période : {gain_total_vonda:.2f} $")

if __name__ == "__main__":
    synchroniser_finances_partagees()