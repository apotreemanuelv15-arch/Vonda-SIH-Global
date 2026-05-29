from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
    # Récupération des médicaments en stock et des établissements
    medicaments = Medicament.objects.filter(quantite_stock__gt=0)
    etablissements = Etablissement.objects.all()

    if request.method == "POST":
        medicament_id = request.POST.get("medicament")
        quantite_cartons = int(request.POST.get("quantite_cartons", 0))
        etablissement_id = request.POST.get("etablissement")

        medicament = get_object_or_404(Medicament, id=medicament_id)
        
        # Calcul des unités individuelles requises
        unites_demandees = quantite_cartons * medicament.unites_par_carton
        
        # Vérification stricte des stocks avant validation
        if medicament.quantite_stock < unites_demandees:
            messages.error(
                request, 
                f"Opération refusée ! Stock insuffisant pour {medicament.nom}. "
                f"Demandé : {quantite_cartons} cartons ({unites_demandees} u), "
                f"Disponible : {medicament.stock_en_cartons} cartons ({medicament.quantite_stock} u)."
            )
            return redirect("passer_vente_gros")

        try:
            # Création de la transaction de gros
            vente = Vente.objects.create(
                medicament=medicament,
                type_vente='GROS',
                quantite_vendue=quantite_cartons,
            )
            
            messages.success(
                request, 
                f"✅ Vente de gros enregistrée ! {quantite_cartons} cartons de {medicament.nom} déstockés. "
                f"Code Facture : {vente.code_facture_unique}."
            )
            return redirect("passer_vente_gros")
            
        except Exception as e:
            messages.error(request, f"Erreur d'exécution du module : {str(e)}")
            return redirect("passer_vente_gros")

    return render(request, "pharmacy/vente_gros.html", {
        "medicaments": medicaments,
        "etablissements": etablissements
    })