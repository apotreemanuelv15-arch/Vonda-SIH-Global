from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views  # Moteur de connexion Django

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Redirection automatique de la racine vers l'inventaire
    path('', RedirectView.as_view(url='inventaire/', permanent=True)), 
    
    # 2. Route officielle que Django réclame pour la connexion (Correction de l'erreur 404)
    path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    
    # 3. Les routes de vos applications métiers
    path('', include('pharmacy.urls')), 
]