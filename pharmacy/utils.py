import feedparser
from dateutil import parser as date_parser
from django.utils import timezone
from .models import ArticleVeille

# Configuration des antennes du Radar (Flux RSS de confiance)
SOURCES_RADAR = {
    'ONU Afrique': 'https://news.un.org/feed/subscribe/fr/news/region/africa/feed/rss.xml',
    'Banque Mondiale': 'https://www.banquemondiale.org/fr/news/rss/all.xml',
}

def actualiser_radar():
    """
    Parcourt les flux officiels, extrait les articles récents 
    et les enregistre en base de données s'ils n'existent pas déjà.
    """
    articles_ajoutes = 0
    
    for nom_source, url_flux in SOURCES_RADAR.items():
        try:
            flux = feedparser.parse(url_flux)
            
            for entree in flux.entries:
                # On évite les doublons en vérifiant si le lien existe déjà
                if not ArticleVeille.objects.filter(lien=entree.link).exists():
                    # Conversion propre de la date du flux en date compatible Django
                    try:
                        date_pub = date_parser.parse(entree.published)
                        # Rendre la date consciente de la timezone si nécessaire
                        if timezone.is_naive(date_pub):
                            date_pub = timezone.make_aware(date_pub)
                    except Exception:
                        date_pub = timezone.now()
                    
                    # Extraction de la description/résumé
                    description = getattr(entree, 'summary', '')
                    # Nettoyage rapide si la description est trop longue
                    if description and len(description) > 500:
                        description = description[:497] + "..."

                    # Création de l'article dans le Radar
                    ArticleVeille.objects.create(
                        titre=entree.title,
                        lien=entree.link,
                        description=description,
                        source=nom_source,
                        date_publication=date_pub
                    )
                    articles_ajoutes += 1
        except Exception as e:
            print(f"Erreur lors de la lecture du flux {nom_source} : {e}")
            continue
            
    return articles_ajoutes
