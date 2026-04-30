from django.shortcuts import render, redirect, get_object_or_404
from .models import Medicament, Vente
from .forms import MedicamentForm

# 1. Liste des médicaments
def liste_medicaments(request):
    tous_les_medicaments = Medicament.objects.all()
    return render(request, 'pharmacy/liste.html', {'medicaments': tous_les_medicaments})

# 2. Ajouter un médicament
def ajouter_medicament(request):
    if request.method == "POST":
        form = MedicamentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_medicaments')
    else:
        form = MedicamentForm()
    return render(request, 'pharmacy/ajouter.html', {'form': form})

# 3. Effectuer une vente (NOUVEAU)
def effectuer_vente(request, pk):
    # On récupère le médicament concerné par son ID (pk)
    medicament = get_object_or_404(Medicament, pk=pk)
    
    if request.method == "POST":
        quantite = int(request.POST.get('quantite'))
        
        # Vérification si le stock est suffisant
        if quantite <= medicament.quantite_stock:
            # Calcul du prix total
            total = medicament.prix * quantite
            
            # Création de la vente
            Vente.objects.create(
                medicament=medicament,
                quantite_vendue=quantite,
                prix_total=total
            )
            
            # MISE À JOUR DU STOCK (L'intelligence du système)
            medicament.quantite_stock -= quantite
            medicament.save()
            
            return redirect('liste_medicaments')
            
    return render(request, 'pharmacy/vente.html', {'medicament': medicament})
