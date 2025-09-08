const CACHE_NAME = 'drive-in-tokyo-v1';
const CORE_ASSETS = [
  '/',
  '/index.html',
  '/css/styles.css',
  '/js/carousel.js',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
    ))
  );
});

// Stale-while-revalidate for CSS/JS/images
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Only handle GET
  if (req.method !== 'GET') return;

  // Bypass requests for other origins except known CDNs
  const sameOrigin = url.origin === self.location.origin;
  const allowedCdn = url.hostname.includes('cdn.jsdelivr.net') || url.hostname.includes('cdnjs.cloudflare.com');
  if (!sameOrigin && !allowedCdn) return;

  if (req.destination === 'image' || req.destination === 'style' || req.destination === 'script') {
    event.respondWith(
      caches.match(req).then((cached) => {
        const fetchPromise = fetch(req).then((networkRes) => {
          const resClone = networkRes.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone));
          return networkRes;
        }).catch(() => cached);
        return cached || fetchPromise;
      })
    );
  }
});


