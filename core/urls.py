from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.http import HttpResponse

# Vue temporaire pour déclencher le script migrate.py à distance
def declencher_migration_view(request):
    import migrate
    import sys
    from io import StringIO
    
    # Capturer la sortie du script
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    
    migrate.exécuter_migrations_et_créer_commandant()
    
    sys.stdout = old_stdout
    return HttpResponse(f"<pre>{mystdout.getvalue()}</pre>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('deploy-database-vonda/', declencher_migration_view), # URL secrète d'activation
    path('', RedirectView.as_view(url='inventaire/', permanent=True)), 
    path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('', include('pharmacy.urls')), 
]