from django.db import models

class Medicament(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.IntegerField(default=0)
    date_expiration = models.DateField()
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
