import os
import django
from datetime import date, timedelta

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from pharmacy.models import Patient

def generer_file_sms():
    # 1. On cible les rendez-vous de demain
    demain = date.today() + timedelta(days=1)
    patients = Patient.objects.filter(date_prochain_rdv=demain)

    if not patients.exists():
        print(f"📭 Aucun rendez-vous prévu pour le {demain}. Pas de rappels à envoyer.")
        return

    # 2. Création du fichier d'envoi (Format compatible avec les passerelles SMS)
    with open("FILE_SMS_ENVOI.txt", "w", encoding="utf-8") as f:
        f.write(f"--- PILE D'ENVOI SMS DU {date.today()} (Pour les RDV du {demain}) ---\n\n")
        
        for p in patients:
            # Personnalisation du message selon le type de suivi
            if p.type_suivi == 'CPN':
                msg = f"VONDA SIH: Mme {p.nom_complet}, rappel de votre consultation prenatale demain. Portez-vous bien."
            elif p.type_suivi == 'VIH':
                msg = f"VONDA SIH: Cher patient, n'oubliez pas votre rendez-vous de suivi demain à l'heure habituelle."
            elif p.type_suivi == 'CHR':
                msg = f"VONDA SIH: M. {p.nom_complet}, rappel pour votre suivi de maladie chronique demain."
            else:
                msg = f"VONDA SIH: Bonjour {p.nom_complet}, nous vous confirmons votre rendez-vous medical pour demain."
            
            # Format d'exportation pour votre service offline (Destinataire | Message | Coût estimé)
            f.write(f"DEST: {p.telephone} | MSG: {msg} | UNIT_PRICE: 0.50$\n")
            
    print(f"✅ Succès : {patients.count()} rappel(s) généré(s) dans 'FILE_SMS_ENVOI.txt'")
    print(f"💰 Revenu potentiel estimé : {patients.count() * 0.5:.2f} $")

if __name__ == "__main__":
    generer_file_sms()