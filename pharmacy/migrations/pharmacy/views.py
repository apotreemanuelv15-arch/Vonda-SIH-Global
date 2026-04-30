from django.shortcuts import render, redirect, get_object_or_404
from .models import Medicament, Vente, Patient
from .forms import MedicamentForm, PatientForm
from django.db.models import Sum

# --- PARTIE PHARMACIE ---

def liste_medicaments(request):
    tous_les_medicaments = Medicament.objects.all()
    return render(request, 'pharmacy/liste.html', {'medicaments': tous_les_medicaments})

def ajouter_medicament(request):
    if request.method == "POST":
        form = MedicamentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_medicaments')
    else:
        form = MedicamentForm()
    return render(request, 'pharmacy/ajouter.html', {'form': form})

def effectuer_vente(request, pk):
    medicament = get_object_or_404(Medicament, pk=pk)
    if request.method == "POST":
        quantite = int(request.POST.get('quantite'))
        if quantite <= medicament.quantite_stock:
            total = medicament.prix * quantite
            Vente.objects.create(
                medicament=medicament,
                quantite_vendue=quantite,
                prix_total=total
            )
            medicament.quantite_stock -= quantite
            medicament.save()
            return redirect('historique_ventes')
    return render(request, 'pharmacy/vente.html', {'medicament': medicament})

def historique_ventes(request):
    toutes_les_ventes = Vente.objects.all().order_by('-date_vente')
    total_revenus = toutes_les_ventes.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
    return render(request, 'pharmacy/historique.html', {
        'ventes': toutes_les_ventes,
        'total_revenus': total_revenus
    })

# --- PARTIE PATIENTS ---

def liste_patients(request):
    # Récupère tous les patients du plus récent au plus ancien
    tous_les_patients = Patient.objects.all().order_by('-date_enregistrement')
    return render(request, 'pharmacy/liste_patients.html', {'patients': tous_les_patients})

def ajouter_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_patients')
    else:
        form = PatientForm()
    return render(request, 'pharmacy/ajouter_patient.html', {'form': form})
