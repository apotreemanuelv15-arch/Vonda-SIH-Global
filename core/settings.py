import os
from pathlib import Path
import dj_database_url

# Chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Sécurité (En développement uniquement)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-vonda-sih-key-pour-developpement')

# Passage automatique à False sur Vercel pour éviter les conflits d'environnement
DEBUG = 'VERCEL' not in os.environ

ALLOWED_HOSTS = ['*', '.vercel.app', 'vonda-sih-global.vercel.app', 'localhost', '127.0.0.1']
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

# MIDDLEWARE (WhiteNoise placé juste après la sécurité)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Crucial pour le CSS en production
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
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


# --- CONFIGURATION DYNAMIQUE DE LA BASE DE DONNÉES ---
if 'VERCEL' in os.environ:
    postgres_url = os.environ.get('POSTGRES_URL')
    if postgres_url:
        DATABASES = {
            'default': dj_database_url.config(
                default=postgres_url,
                conn_max_age=600,
                ssl_require=True
            )
        }
    else:
        # Repli sur SQLite dans le dossier temporaire de Vercel
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join('/tmp', 'db.sqlite3'),
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Internationalisation
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Luanda'
USE_I18N = True
USE_TZ = True

# --- CONFIGURATION DES FICHIERS STATIQUES ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuration WhiteNoise optimisée (évite le crash du manifeste manquant)
if 'VERCEL' in os.environ:
    STORAGES = {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirections après connexion
LOGIN_REDIRECT_URL = 'inventaire'
LOGOUT_REDIRECT_URL = 'login'

# --- EN-TÊTE DE SÉCURITÉ POUR LE PROXY SSL DE VERCEL ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
