const CACHE = 'manalert-v1';
const FILES = ['./index.html', './manifest.json'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(FILES))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Network first : toujours essayer le réseau, cache en fallback
// Garantit que les mises à jour sont visibles sans vider le cache Safari
self.addEventListener('fetch', e => {
  e.respondWith(
    fetch(e.request, {cache: 'no-cache'})
      .then(r => {
        const rc = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, rc));
        return r;
      })
      .catch(() => caches.match(e.request))
  );
});
