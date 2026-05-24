from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

# Fonction de sécurité pour créer automatiquement le Commandant en ligne
def creation_automatique_administrateur():
    User = get_user_model()
    username = "emanuel"
    email = "apotreemanuelv15@gmail.com"
    mot_de_passe_temporaire = "VondaSIH2026!" # Vous pourrez le changer plus tard
    
    if not User.objects.filter(username=username).exists():
        try:
            User.objects.create_superuser(
                username=username, 
                email=email, 
                password=mot_de_passe_temporaire
            )
            print("🚀 Compte Administrateur 'emanuel' créé avec succès dans Postgres !")
        except IntegrityError:
            pass

# Exécution de la vérification au démarrage
creation_automatique_administrateur()

# Vos routes de navigation d'origine
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pharmacy.urls')), # Route vers votre pharmacie
]