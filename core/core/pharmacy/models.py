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

class Vente(models.Model):
    # On lie la vente à un médicament précis
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    quantite_vendue = models.IntegerField()
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    date_vente = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vente de {self.quantite_vendue} {self.medicament.nom}"
