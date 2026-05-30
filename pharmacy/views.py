from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Medicament, Vente, Etablissement

@login_required
def inventaire(request):
    """Affiche la liste des médicaments uniquement aux utilisateurs connectés"""
    tous_les_medicaments = Medicament.objects.all()
    return render(request, 'pharmacy/inventaire.html', {
        'medicaments': tous_les_medicaments
    })

@login_required
def passer_vente_gros(request):
    """Gère la facturation et le déstockage massif par cartons de gros"""
    medicaments = Medicament.objects.filter(quantite_stock__gt=0)
    etablissements = Etablissement.objects.all()

    if request.method == "POST":
        medicament_id = request.POST.get("medicament")
        quantite_cartons = int(request.POST.get("quantite_cartons", 0))
        etablissement_id = request.POST.get("etablissement")

        medicament = get_object_or_404(Medicament, id=medicament_id)
        unites_demandees = quantite_cartons * medicament.unites_par_carton
        
        if medicament.quantite_stock < unites_demandees:
            messages.error(
                request, 
                f"Opération refusée ! Stock insuffisant pour {medicament.nom}."
            )
            return redirect("passer_vente_gros")

        try:
            # Création de la transaction de gros
            vente = Vente.objects.create(
                medicament=medicament,
                type_vente='GROS',
                quantite_vendue=quantite_cartons,
            )
            
            # Redirection directe vers la page de la facture exclusive
            return redirect("afficher_facture_gros", vente_id=vente.id)
            
        except Exception as e:
            messages.error(request, f"Erreur d'exécution du module : {str(e)}")
            return redirect("passer_vente_gros")

    return render(request, "pharmacy/vente_gros.html", {
        "medicaments": medicaments,
        "etablissements": etablissements
    })

@login_required
def afficher_facture_gros(request, vente_id):
    """Affiche le reçu officiel d'une vente de gros pour impression sans erreur de type"""
    vente = get_object_or_404(Vente, id=vente_id)
    
    # 1. Calcul du prix total (génère un type Decimal via les champs du modèle)
    prix_total_cartons = vente.quantite_vendue * (vente.medicament.prix_unitaire * vente.medicament.unites_par_carton)
    
    # 2. Sécurisation mathématique : Conversion du taux float en Decimal
    redevance = prix_total_cartons * Decimal('0.05')
    
    # 3. Addition des deux montants de même type (Decimal)
    montant_total_sih = prix_total_cartons + redevance

    return render(request, "pharmacy/facture_gros.html", {
        "vente": ... if 'vente' in locals() else vente,  # Protection d'existence de variable
        "vente": vente,
        "prix_total_cartons": prix_total_cartons,
        "redevance": redevance,
        "montant_total_sih": montant_total_sih
    })