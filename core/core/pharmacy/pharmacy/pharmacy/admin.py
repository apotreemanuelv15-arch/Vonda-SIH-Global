from django.contrib import admin
from .models import Medicament

@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'quantite_stock', 'date_expiration')
    search_fields = ('nom',)
    list_filter = ('date_expiration',)
