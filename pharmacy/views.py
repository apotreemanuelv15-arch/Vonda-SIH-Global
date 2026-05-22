from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Medicament

# Ce décorateur oblige l'utilisateur à être connecté
@login_required
def inventaire(request):
    """Affiche la liste des médicaments uniquement aux utilisateurs connectés"""
    tous_les_medicaments = Medicament.objects.all()
    return render(request, 'pharmacy/inventaire.html', {
        'medicaments': tous_les_medicaments
    })