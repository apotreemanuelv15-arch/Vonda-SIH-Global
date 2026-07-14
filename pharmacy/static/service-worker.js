const CACHE_NAME = 'vonda-sih-cache-v1';

// Fichiers indispensables à mettre en cache immédiatement (App Shell + Pages clés)
const STATIC_ASSETS = [
    '/',
    '/radar/',          // 📡 Le Radar de veille
    '/inventaire/',     // 📦 L'inventaire de la pharmacie
    '/static/manifest.json',
    '/static/images/icon-192x192.png',
];

// 1. Installation : Mise en cache des ressources de base
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('Vonda SIH : Mise en cache de l\'App Shell');
            return cache.addAll(STATIC_ASSETS);
        }).then(() => self.skipWaiting())
    );
});

// 2. Activation : Nettoyage des anciens caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        console.log('Vonda SIH : Nettoyage d\'un ancien cache', key);
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// 3. Interception des requêtes (Fetch)
self.addEventListener('fetch', (event) => {
    const request = event.request;

    // Stratégie pour les pages HTML (Navigation) : Le réseau d'abord, le cache en secours
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    const copy = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, copy);
                    });
                    return response;
                })
                .catch(() => {
                    return caches.match(request);
                })
        );
        return;
    }

    // Stratégie pour les images, polices, fichiers CSS/JS : Cache en premier (rapidité)
    event.respondWith(
        caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
                return cachedResponse;
            }
            return fetch(request).then((response) => {
                if (response.status === 200) {
                    const copy = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, copy);
                    });
                }
                return response;
            });
        })
    );
});
