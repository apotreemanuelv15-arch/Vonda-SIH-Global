import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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

# --- 3. PHARMACIE ET LUTTE CONTRE L'AUTOMÉDICATION (MIS À JOUR GROSSISTE) ---
class Medicament(models.Model):
    # --- CHOIX DE CONDITIONNEMENT GROSSISTE ---
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
    
    # --- GESTION DU STOCK HYBRIDE (Détail vs Gros) ---
    quantite_stock = models.IntegerField(default=0, help_text="Quantité totale disponible en unités de détail")
    conditionnement_achat = models.CharField(max_length=20, choices=TYPE_EMBALLAGE_CHOICES, default=UNITE)
    unites_par_carton = models.IntegerField(default=1, help_text="Combien d'unités individuelles contient un carton d'importation")

    # --- TRAÇABILITÉ IMPORT-EXPORT ---
    pays_origine = models.CharField(max_length=100, default="International", help_text="Pays de fabrication (Inde, France, Chine, etc.)")
    numero_lot_import = models.CharField(max_length=100, blank=True, null=True, help_text="Numéro de lot douanier / international")
    cout_fret_douane = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Frais de transport et douane appliqués à ce lot")

    # --- TARIFICATION DÉGRESSIVE ---
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix de vente standard à l'unité")
    prix_grossiste_carton = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Prix spécial par carton pour les dépôts intégrés")

    # --- AIDE IA ---
    posologie_standard_ia = models.TextField(blank=True, help_text="Guide de posologie suggéré par l'IA")
    contre_indications = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nom} ({self.pays_origine}) - {self.etablissement.nom} (Stock: {self.quantite_stock} u)"

    @property
    def stock_en_cartons(self):
        """Calcule instantanément combien de cartons complets sont disponibles au dépôt"""
        if self.unites_par_carton > 1:
            return self.quantite_stock // self.unites_par_carton
        return 0

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
        # Calculer le besoin réel en unités de détail pour la validation du stock
        unites_demandees = self.quantite_vendue
        if self.type_vente == 'GROS':
            unites_demandees = self.quantite_vendue * self.medicament.unites_par_carton

        if self.medicament.quantite_stock < unites_demandees:
            raise ValidationError(f"Stock insuffisant pour {self.medicament.nom}. Requis : {unites_demandees} u, Disponible : {self.medicament.quantite_stock} u.")

    def save(self, *args, **kwargs):
        self.clean()
        
        # 1. Calcul automatique du prix selon le type de contrat (Détail vs Gros)
        if self.type_vente == 'GROS' and self.medicament.prix_grossiste_carton:
            self.prix_total = self.medicament.prix_grossiste_carton * self.quantite_vendue
            unites_a_deduire = self.quantite_vendue * self.medicament.unites_par_carton
        else:
            # Si Vente au détail ou si le prix de gros n'est pas configuré, calcul standard à l'unité
            if self.type_vente == 'GROS':
                # Sécurité : calcul au tarif unitaire si prix de gros oublié
                self.prix_total = (self.medicament.prix_unitaire * self.medicament.unites_par_carton) * self.quantite_vendue
                unites_a_deduire = self.quantite_vendue * self.medicament.unites_par_carton
            else:
                self.prix_total = self.medicament.prix_unitaire * self.quantite_vendue
                unites_a_deduire = self.quantite_vendue
        
        # 2. Déduction automatique du stock global en unités de détail
        self.medicament.quantite_stock -= unites_a_deduire
        self.medicament.save()
        
        # 3. Sauvegarde de la vente en base de données
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # 4. GÉNÉRATION DE LA TRANSACTION BANCAIRE (Redevance Vonda 5%)
        if is_new:
            taux_redevance = 0.05  # 5% de redevance technologique
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