from django.db import models

class Medicament(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.PositiveIntegerField(default=0)
    seuil_alerte = models.PositiveIntegerField(default=5)  # Alerte si stock < 5

    def __str__(self):
        return self.nom

    def est_en_rupture(self):
        return self.quantite_stock <= self.seuil_alerte