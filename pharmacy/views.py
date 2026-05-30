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
def afficher_facture_gros(request, username=None, vente_id=None):
    """Affiche le reçu officiel d'une vente de gros pour impression sans erreur de type"""
    target_id = vente_id if vente_id else username
    vente = get_object_or_404(Vente, id=target_id)
    
    # 1. Calcul du prix total (génère un type Decimal via les champs du modèle)
    prix_total_cartons = vente.quantite_vendue * (vente.medicament.prix_unitaire * vente.medicament.unites_par_carton)
    
    # 2. Sécurisation mathématique : Conversion du taux float en Decimal
    redevance = prix_total_cartons * Decimal('0.05')
    
    # 3. Addition des deux montants de même type (Decimal)
    montant_total_sih = prix_total_cartons + redevance

    return render(request, "pharmacy/facture_gros.html", {
        "vente": vente,
        "prix_total_cartons": prix_total_cartons,
        "redevance": redevance,
        "montant_total_sih": montant_total_sih
    })

@login_required
def passer_vente_detail(request):
    """Gère la distribution au détail (à l'unité) pour les patients de l'hôpital"""
    medicaments = Medicament.objects.filter(quantite_stock__gt=0)

    if request.method == "POST":
        medicament_id = request.POST.get("medicament")
        quantite_unites = int(request.POST.get("quantite_unites", 0))

        medicament = get_object_or_404(Medicament, id=medicament_id)
        
        # 1. Vérification stricte du stock disponible à l'unité
        if medicament.quantite_stock < quantite_unites:
            messages.error(
                request, 
                f"Alerte Stock ! Il ne reste que {medicament.quantite_stock} unités de {medicament.nom}."
            )
            return redirect("passer_vente_detail")

        try:
            # 2. Déduction unique et sécurisée du stock avant enregistrement
            medicament.quantite_stock -= quantite_unites
            medicament.save()

            # 3. Enregistrement de la vente de type 'DETAIL'
            vente = Vente.objects.create(
                medicament=medicament,
                type_vente='DETAIL',
                quantite_vendue=quantite_unites,
            )
            
            # 4. Redirection forcée immédiate pour vider le formulaire
            return redirect("afficher_facture_detail", vente_id=vente.id)
            
        except Exception as e:
            messages.error(request, f"Erreur système : {str(e)}")
            return redirect("passer_vente_detail")

    return render(request, "pharmacy/vente_detail.html", {
        "medicaments": medicaments
    })

@login_required
def afficher_facture_detail(request, vente_id):
    """Génère le reçu au détail pour le dossier du patient"""
    vente = get_object_or_404(Vente, id=vente_id)
    
    # Calcul au détail : Unités vendues x Prix unitaire de base
    montant_total_unitaire = vente.quantite_vendue * vente.medicament.prix_unitaire

    return render(request, "pharmacy/facture_detail.html", {
        "vente": vente,
        "montant_total_unitaire": montant_total_unitaire
    })

@login_required
def passer_transfert(request):
    """Transfère des cartons de médicaments vers un autre établissement sanitaire"""
    medicaments = Medicament.objects.filter(quantite_stock__gt=0)
    etablissements = Etablissement.objects.all()

    if request.method == "POST":
        medicament_id = request.POST.get("medicament")
        quantite_cartons = int(request.POST.get("quantite_cartons", 0))
        etablissement_id = request.POST.get("etablissement")

        medicament = get_object_or_404(Medicament, id=medicament_id)
        etablissement = get_object_or_404(Etablissement, id=etablissement_id)
        
        unites_demandees = quantite_cartons * medicament.unites_par_carton
        
        # Validation stricte de la capacité logistique
        if medicament.quantite_stock < unites_demandees:
            messages.error(
                request, 
                f"Transfert avorté ! Stock insuffisant pour expédier {quantite_cartons} cartons."
            )
            return redirect("passer_transfert")

        try:
            # Soustraction unique du stock central
            medicament.quantite_stock -= unites_demandees
            medicament.save()

            # Enregistrement du mouvement logistique
            vente = Vente.objects.create(
                medicament=medicament,
                type_vente='GROS',
                quantite_vendue=quantite_cartons,
            )
            
            # Redirection vers la génération du Bon de Transport Officiel
            return redirect("afficher_bon_transfert", vente_id=vente.id, etab_id=etablissement.id)
            
        except Exception as e:
            messages.error(request, f"Échec de l'ordre de transfert : {str(e)}")
            return redirect("passer_transfert")

    return render(request, "pharmacy/transfert.html", {
        "medicaments": medicaments,
        "etablissements": etablissements
    })

@login_required
def afficher_bon_transfert(request, vente_id, etab_id):
    """Génère le Bon de Convoi officiel pour le transport routier"""
    vente = get_object_or_404(Vente, id=vente_id)
    etablissement = get_object_or_404(Etablissement, id=etab_id)
    
    volume_total = vente.quantite_vendue * vente.medicament.unites_par_carton

    return render(request, "pharmacy/bon_transfert.html", {
        "vente": vente,
        "etablissement": etablissement,
        "volume_total": volume_total
    })

@login_required
def rapport_flux(request):
    """Affiche le journal historique de toutes les transactions de stock"""
    mouvements = Vente.objects.all().order_by('-date_vente')
    return render(request, "pharmacy/rapport_flux.html", {
        "mouvements": mouvements
    })