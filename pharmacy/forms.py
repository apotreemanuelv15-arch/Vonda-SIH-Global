from django import forms
from .models import Medicament

class MedicamentForm(forms.ModelForm):
    class Meta:
        model = Medicament
        fields = ['nom', 'description', 'prix', 'quantite_stock', 'date_expiration']
        widgets = {
            'date_expiration': forms.DateInput(attrs={'type': 'date'}),
        }
