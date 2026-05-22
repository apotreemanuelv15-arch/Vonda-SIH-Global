from django.urls import path
from . import views

urlpatterns = [
    # Cette ligne lie l'adresse /pharmacy/inventaire/ à votre vue
    path('inventaire/', views.inventaire, name='inventaire'),
]