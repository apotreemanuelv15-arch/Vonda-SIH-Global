import os
from pathlib import Path
import dj_database_url  # Importation essentielle pour Vercel Postgres

# Chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Sécurité (En développement uniquement)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-vonda-sih-key-pour-developpement')
DEBUG = True
ALLOWED_HOSTS = ['*', '.vercel.app', 'vonda-sih-global.vercel.app']
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app', 'https://vonda-sih-global.vercel.app']

# Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pharmacy',  # Votre application principale
    'billing',   # Votre application de facturation
]

# MIDDLEWARE (Ordre ajusté avec WhiteNoise juste après la sécurité)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <--- Ajout crucial pour le CSS en ligne
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Chemin vers vos fichiers HTML
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# --- CONFIGURATION DYNAMIQUE DE LA BASE DE DONNÉES (Préservée !) ---
if 'VERCEL' in os.environ:
    # Moteur de production en ligne (Vercel + Neon Postgres)
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('POSTGRES_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Moteur de développement local (Votre clé Linux Mint)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Internationalisation
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Luanda'  # Aligné sur votre fuseau horaire opérationnel
USE_I18N = True
USE_TZ = True

# --- CONFIGURATION DES FICHIERS STATIQUES (Optimisée pour la production) ---
STATIC_URL = '/static/'

# Dossiers où Django va chercher les images, CSS et JS en développement
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Dossier de collecte pour la production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Moteur de stockage WhiteNoise pour compresser et servir le design sur le Cloud
if 'VERCEL' in os.environ:
    STORAGES = {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

# Configuration par défaut des IDs
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirections après connexion
LOGIN_REDIRECT_URL = 'inventaire'
LOGOUT_REDIRECT_URL = 'login'