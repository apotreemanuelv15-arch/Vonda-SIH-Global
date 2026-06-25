import urllib.parse
from django.core.management.base import BaseCommand
from pharmacy.models import PharmaciePartenaire

class Command(BaseCommand):
    help = "Génère les liens de prospection automatisés WhatsApp pour le conglomérat (Angola et RDC)"

    def handle(self, *args, **options):
        # On récupère uniquement les pharmacies qui n'ont pas encore accepté le conglomérat
        prospects = PharmaciePartenaire.objects.filter(est_affiliee=False)

        if not prospects.exists():
            self.stdout.write(self.style.SUCCESS("Aucun nouveau prospect à contacter dans la base de données."))
            return

        self.stdout.write(self.style.NOTICE(f"--- Lancement de la génération : {prospects.count()} pharmacies trouvées --- \n"))

        for pharmacie in prospects:
            # Nettoyage rudimentaire du numéro de téléphone (retrait des espaces et des +)
            num_tel = "".join(c for c in pharmacie.telephone_whatsapp if c.isdigit())

            # Personnalisation du message selon le pays cible
            if pharmacie.pays == 'ANGOLA':
                # Message en Portugais pour Luanda
                texte_message = (
                    f"Olá, Gerência da {pharmacie.nom}.\n\n"
                    f"O Sistema *Vonda SIH Global* identificou uma busca ativa de pacientes na zona de {pharmacie.zone_ville}.\n"
                    f"Notámos que os seus stocks ou preços não estão sincronizados no Radar Central de Luanda.\n\n"
                    f"Deseja ativar o seu painel gratuito para receber estes clientes e comparar os seus preços de grosso com as importações do Portugal?\n"
                    f"Clique aqui para validar o seu acesso: http://127.0.0.1:8000/hologramme-ia/"
                )
            else:
                # Message en Français pour Kinshasa
                texte_message = (
                    f"Bonjour, Direction de la {pharmacie.nom}.\n\n"
                    f"Le Système *Vonda SIH Global* a détecté une recherche active de médicaments par des patients dans la commune de {pharmacie.zone_ville}.\n"
                    f"Vos stocks ne sont pas encore synchronisés sur le Radar Central de Kinshasa.\n\n"
                    f"Souhaitez-vous activer votre panneau de gestion gratuit pour capter ces clients et harmoniser vos prix face aux grossistes?\n"
                    f"Cliquez ici pour valider votre accès: http://127.0.0.1:8000/hologramme-ia/"
                )

            # Encodage du texte pour le format URL
            texte_encode = urllib.parse.quote(texte_message)
            
            # Génération du lien d'action WhatsApp
            lien_whatsapp = f"https://wa.me/{num_tel}?text={texte_encode}"

            # Affichage pro dans le terminal
            self.stdout.write(self.style.WARNING(f"📌 [PROSPECT] {pharmacie.nom} ({pharmacie.get_pays_display()})"))
            self.stdout.write(f"📞 WhatsApp: {pharmacie.telephone_whatsapp}")
            self.stdout.write(f"🔗 Lien d'envoi direct:\n{lien_whatsapp}\n")
            self.stdout.write("-" * 50)

        self.stdout.write(self.style.SUCCESS("\nCampagne générée avec succès. Prêt pour l'envoi !"))
