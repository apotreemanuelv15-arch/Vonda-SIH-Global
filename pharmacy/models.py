import uuid
import os
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from google import genai  # Importation du nouveau moteur IA de Google

# --- 1. STRUCTURE ADMINISTRATIVE ---
class Etablissement(models.Model):
    TYPES = [('HOSPITAL', 'Hôpital'), ('PHARMA', 'Pharmacie Privée'), ('DEPOT', 'Dépôt de Gros')]
    nom = models.CharField(max_length=150)
    type_etablissement = models.CharField(max_length=10, choices=TYPES, default='PHARMA')
    adresse = models.TextField()
    telephone = models.CharField(max_length=50)
    logo_signature = models.ImageField(upload_to='logos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.get_type_etablissement_display()})"

# --- 2. GESTION DES SOINS, MÉDECINS ET IA ---
class Patient(models.Model):
    TYPES_SUIVI = [('GEN', 'Général'), ('CPN', 'Accouchement/CPN'), ('VIH', 'Suivi VIH')]
    nom_complet = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20, blank=True)
    type_suivi = models.CharField(max_length=3, choices=TYPES_SUIVI, default='GEN')
    date_prochain_rdv = models.DateField(null=True, blank=True)
    alerte_sms_envoyee = models.BooleanField(default=False)

    def __str__(self):
        return self.nom_complet

class Consultation(models.Model):
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medecin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    diagnostic = models.TextField()
    analyse_ia_symptomes = models.TextField(blank=True, help_text="Analyse suggérée par l'IA pour aider le médecin")
    date_consultation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation {self.patient.nom_complet} - {self.date_consultation.strftime('%d/%m/%Y')}"

class ChirurgieAssistee(models.Model):
    """Collaboration chirurgicale robotique et IA à distance"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    chirurgien_local = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chirurgies_locales')
    expert_distance = models.CharField(max_length=200) 
    type_intervention = models.CharField(max_length=255)
    statut_robotique = models.CharField(max_length=100, default="Prêt / Connecté")
    flux_video_ia = models.URLField(blank=True, help_text="Lien du flux vidéo assisté par IA")
    date_intervention = models.DateTimeField()

    def __str__(self):
        return f"Chirurgie IA : {self.patient.nom_complet} ({self.type_intervention})"

# --- 3. PHARMACIE ET LUTTE CONTRE L'AUTOMÉDICATION (AUTOMATISATION IA ACTIVE) ---
class Medicament(models.Model):
    UNITE = 'UNITE'
    CARTON = 'CARTON'
    PALETTE = 'PALETTE'
    
    TYPE_EMBALLAGE_CHOICES = [
        (UNITE, 'Unité (Boîte/Flacon)'),
        (CARTON, 'Carton de Gros'),
        (PALETTE, 'Palette Importation'),
    ]

    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    
    quantite_stock = models.IntegerField(default=0, help_text="Quantité totale disponible en unités de détail")
    conditionnement_achat = models.CharField(max_length=20, choices=TYPE_EMBALLAGE_CHOICES, default=UNITE)
    unites_par_carton = models.IntegerField(default=1, help_text="Combien d'unités individuelles contient un carton d'importation")

    pays_origine = models.CharField(max_length=100, default="International", help_text="Pays de fabrication (Inde, France, Chine, etc.)")
    numero_lot_import = models.CharField(max_length=100, blank=True, null=True, help_text="Numéro de lot douanier / international")
    cout_fret_douane = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Frais de transport et douane appliqués à ce lot")

    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix de vente standard à l'unité")
    prix_grossiste_carton = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Prix spécial par carton pour les dépôts intégrés")

    # Champs gérés automatiquement par l'IA
    posologie_standard_ia = models.TextField(blank=True, help_text="Généré automatiquement par l'IA si laissé vide")
    contre_indications = models.TextField(blank=True, help_text="Généré automatiquement par l'IA si laissé vide")

    def __str__(self):
        return f"{self.nom} ({self.pays_origine}) - {self.etablissement.nom} (Stock: {self.quantite_stock} u)"

    @property
    def stock_en_cartons(self):
        if self.unites_par_carton > 1:
            return self.quantite_stock // self.unites_par_carton
        return 0

    def save(self, *args, **kwargs):
        # Déclenchement du Cerveau IA si les champs sont vides et qu'une clé API est disponible
        api_key_gemini = os.environ.get("GEMINI_API_KEY")
        
        if api_key_gemini and (not self.posologie_standard_ia or not self.contre_indications):
            try:
                # Initialisation du client avec le nouveau SDK google-genai
                client = genai.Client(api_key=api_key_gemini)
                
                if not self.posologie_standard_ia:
                    prompt_poso = f"Donne uniquement la posologie médicale standard, très concise (max 2 phrases), pour la molécule ou le médicament suivant : {self.nom}. Ajoute une formule stricte contre l'automédication à la fin."
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_poso)
                    self.posologie_standard_ia = response.text.strip()
                    
                if not self.contre_indications:
                    prompt_contra = f"Donne uniquement la liste des contre-indications majeures (les plus dangereuses), sous forme de puces concises, pour : {self.nom}."
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_contra)
                    self.contre_indications = response.text.strip()
            except Exception as e:
                # Sécurité : Si l'API échoue (réseau, quota), le système enregistre sans bloquer la pharmacie
                if not self.posologie_standard_ia:
                    self.posologie_standard_ia = "Indisponible temporairement (Erreur IA)."
                if not self.contre_indications:
                    self.contre_indications = "Veuillez consulter la notice d'origine."

        super().save(*args, **kwargs)

class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    medicament = models.ForeignKey(Medicament, on_delete=models.PROTECT)
    posologie = models.CharField(max_length=200)
    duree_traitement = models.CharField(max_length=50)

class Vente(models.Model):
    TYPES_VENTE = [('DETAIL', 'Vente au Détail'), ('GROS', 'Vente en Gros (Carton)')]

    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    type_vente = models.CharField(max_length=10, choices=TYPES_VENTE, default='DETAIL')
    quantite_vendue = models.PositiveIntegerField(help_text="Nombre d'unités si Détail, nombre de cartons si Gros")
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    date_vente = models.DateTimeField(auto_now_add=True)
    code_facture_unique = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def clean(self):
        unites_demandees = self.quantite_vendue
        if self.type_vente == 'GROS':
            unites_demandees = self.quantite_vendue * self.medicament.unites_par_carton

        if self.medicament.quantite_stock < unites_demandees:
            raise ValidationError(f"Stock insuffisant pour {self.medicament.nom}. Requis : {unites_demandees} u, Disponible : {self.medicament.quantite_stock} u.")

    def save(self, *args, **kwargs):
        self.clean()
        
        if self.type_vente == 'GROS' and self.medicament.prix_grossiste_carton:
            self.prix_total = self.medicament.prix_grossiste_carton * self.quantite_vendue
            unites_a_deduire = self.quantite_vendue * self.medicament.unites_par_carton
        else:
            if self.type_vente == 'GROS':
                self.prix_total = (self.medicament.prix_unitaire * self.medicament.unites_par_carton) * self.quantite_vendue
                unites_a_deduire = self.quantite_vendue * self.medicament.unites_par_carton
            else:
                self.prix_total = self.medicament.prix_unitaire * self.quantite_vendue
                unites_a_deduire = self.quantite_vendue
        
        self.medicament.quantite_stock -= unites_a_deduire
        self.medicament.save()
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            taux_redevance = 0.05
            montant_redevance = float(self.prix_total) * taux_redevance
            
            TransactionBancaire.objects.create(
                etablissement=self.medicament.etablissement,
                montant_brut=self.prix_total,
                redevance_vonda=montant_redevance,
                source='PHARMA'
            )

    def __str__(self):
        return f"Facture {self.code_facture_unique} - Total: {self.prix_total} Kz"

# --- 4. HOSPITALISATION ET FINANCES ---
class Hospitalisation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_entree = models.DateTimeField()
    date_sortie = models.DateTimeField(null=True, blank=True)
    motif_sejour = models.CharField(max_length=200)
    prix_par_jour = models.DecimalField(max_digits=10, decimal_places=2)
    est_paye = models.BooleanField(default=False)

    @property
    def total_hebergement(self):
        if self.date_sortie:
            jours = (self.date_sortie - self.date_entree).days
            return (jours if jours > 0 else 1) * self.prix_par_jour
        return 0

class TransactionBancaire(models.Model):
    SOURCES = [('PHARMA', 'Pharmacie'), ('HOSPIT', 'Hospitalisation'), ('SMS', 'Service SMS')]
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE)
    montant_brut = models.DecimalField(max_digits=12, decimal_places=2)
    redevance_vonda = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=10, choices=SOURCES, default='PHARMA', null=True, blank=True)
    reference_audit = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    date_transaction = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.reference_audit} - Redevance Vonda: {self.redevance_vonda} Kz"

# --- 5. GUIDE D'AIDE ET DOCUMENTATION ---
class GuideModule(models.Model):
    titre_module = models.CharField(max_length=100)
    instructions = models.TextField()
    video_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.titre_module

# --- 6. CONGLOMÉRAT ET ACQUISITION AUTOMATISÉE INTERNATIONALE ---
class PharmaciePartenaire(models.Model):
    PAYS_CHOICES = [
        ('ANGOLA', 'Angola (Luanda)'),
        ('RDC', 'République Démocratique du Congo (Kinshasa)'),
    ]

    nom = models.CharField(max_length=255, verbose_name="Nom de la Pharmacie")
    pays = models.CharField(max_length=20, choices=PAYS_CHOICES, default='ANGOLA', verbose_name="Pays")
    zone_ville = models.CharField(max_length=100, help_text="Quartier à Luanda ou Commune à Kinshasa (ex: Gombe, Talatona)", verbose_name="Zone / Commune")
    telephone_whatsapp = models.CharField(max_length=50, verbose_name="Numéro WhatsApp (Prospect)")
    est_affiliee = models.BooleanField(default=False, verbose_name="A accepté le conglomérat")
    date_contact = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.zone_ville} ({self.get_pays_display()})"
