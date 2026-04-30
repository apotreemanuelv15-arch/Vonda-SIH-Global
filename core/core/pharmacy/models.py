from django.db import models

# --- MODULE PHARMACIE ---
class Medicament(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.IntegerField(default=0)
    date_expiration = models.DateField()
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class Vente(models.Model):
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    quantite_vendue = models.IntegerField()
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    date_vente = models.DateTimeField(auto_now_add=True)

# --- MODULE PATIENTS ---
class Patient(models.Model):
    SEXE_CHOICES = [('M', 'Masculin'), ('F', 'Féminin')]
    
    nom_complet = models.CharField(max_length=255)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom_complet
