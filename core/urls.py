from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.http import HttpResponse

# Protection contre le crash automatique des icônes sur les navigateurs
def favicon_view(request):
    return HttpResponse(status=204)  # Réponse propre et silencieuse (No Content)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Interceptions prioritaires pour éviter l'erreur 500 sur Vercel
    path('favicon.ico', favicon_view),
    path('favicon.png', favicon_view),
    
    # Vos configurations d'origine préservées intactes :
    path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('', RedirectView.as_view(url='inventaire/', permanent=True)),
    path('', include('pharmacy.urls')),
]
