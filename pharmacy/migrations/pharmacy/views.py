from django.shortcuts import render
from .models import Medicament

def liste_medicaments(request):
    # On récupère tous les médicaments dans la base de données
    tous_les_medicaments = Medicament.objects.all()
    
    # On les envoie à la page HTML (le template)
    return render(request, 'pharmacy/liste.html', {'medicaments': tous_les_medicaments})
