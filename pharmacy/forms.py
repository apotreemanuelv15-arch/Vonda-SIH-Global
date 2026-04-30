from django import forms
from .models import Medicament, Patient

class MedicamentForm(forms.ModelForm):
    class Meta:
        model = Medicament
        fields = ['nom', 'description', 'prix', 'quantite_stock', 'date_expiration']
        widgets = {'date_expiration': forms.DateInput(attrs={'type': 'date'})}

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['nom_complet', 'date_naissance', 'sexe', 'adresse', 'telephone']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }
