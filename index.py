import os
import sys
import django

# 1. Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# 2. Forcer l'exécution des migrations au démarrage sur Vercel
from django.core.management import call_command
try:
    print("Vercel Auto-Migration : Démarrage des migrations...")
    call_command('migrate', interactive=False)
    print("Vercel Auto-Migration : Base de données à jour !")
except Exception as e:
    print(f"Vercel Auto-Migration Erreur : {e}", file=sys.stderr)

# 3. Importation de l'application WSGI pour Vercel
from core.wsgi import app

# Cette variable est lue par Vercel pour lancer Django
application = app
