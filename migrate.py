import os
import sys
import django
from django.core.management import call_command

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def exécuter_migrations_et_créer_commandant():
    print("🛰️ Connexion à Neon Postgres en cours...")
    try:
        # 1. Création des tables
        call_command('migrate', interactive=False)
        print("✅ Toutes les tables ont été créées avec succès dans Postgres !")
        
        # 2. Création de votre profil Administrateur
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = "emanuel"
        email = "apotreemanuelv15@gmail.com"
        password = "VondaSIH2026!"
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"🚀 Administrateur '{username}' créé avec succès !")
        else:
            print(f"ℹ️ L'administrateur '{username}' existe déjà.")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution : {e}")

if __name__ == '__main__':
    exécuter_migrations_et_créer_commandant()