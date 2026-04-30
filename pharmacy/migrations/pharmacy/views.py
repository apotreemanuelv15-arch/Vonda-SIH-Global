from django.shortcuts import render, redirect
from .models import Medicament
from .forms import MedicamentForm

# 1. Vue pour afficher la liste des médicaments
def liste_medicaments(request):
    # On récupère tous les médicaments enregistrés
    tous_les_medicaments = Medicament.objects.all()
    
    # On les envoie vers la page 'liste.html'
    return render(request, 'pharmacy/liste.html', {'medicaments': tous_les_medicaments})

# 2. Vue pour ajouter un nouveau médicament
def ajouter_medicament(request):
    # Si l'utilisateur a cliqué sur le bouton "Enregistrer" (méthode POST)
    if request.method == "POST":
        form = MedicamentForm(request.POST)
        if form.is_valid():
            form.save() # On enregistre dans la base de données
            return redirect('liste_medicaments') # On revient à la liste
            
    # Si l'utilisateur arrive juste sur la page (méthode GET)
    else:
        form = MedicamentForm()
        
    # On affiche le formulaire sur la page 'ajouter.html'
    return render(request, 'pharmacy/ajouter.html', {'form': form})
