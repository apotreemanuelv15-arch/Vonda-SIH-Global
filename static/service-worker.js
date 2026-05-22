const CACHE_NAME = 'vonda-sih-cache-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  // Ajoutez ici les chemins vers vos fichiers CSS ou JS principaux
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      // Retourne le fichier du cache, sinon fait une requête réseau
      return response || fetch(event.request);
    })
  );
});