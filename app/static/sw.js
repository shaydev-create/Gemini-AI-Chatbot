// Service Worker para Gemini AI Chatbot PWA
// Versión: 1.0.0

const CACHE_NAME = 'gemini-chatbot-v1.0.0';
const STATIC_CACHE = 'gemini-static-v1.0.0';
const DYNAMIC_CACHE = 'gemini-dynamic-v1.0.0';

// Archivos estáticos para cachear
const STATIC_FILES = [
    '/',
    '/chat',
    '/static/css/style.css',
    '/static/manifest.json',
    '/static/icons/favicon.ico',
    '/static/icons/icon-192x192.svg',
    '/static/images/icon.svg'
];

// URLs dinámicas que se pueden cachear
const DYNAMIC_URLS = [
    '/api/health',
    '/api/metrics'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
    console.log('🔧 Service Worker: Instalando...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('📦 Service Worker: Cacheando archivos estáticos');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('✅ Service Worker: Instalación completada');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('❌ Service Worker: Error en instalación:', error);
            })
    );
});

// Activación del Service Worker
self.addEventListener('activate', event => {
    console.log('🚀 Service Worker: Activando...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        // Eliminar cachés antiguos
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE && 
                            cacheName !== CACHE_NAME) {
                            console.log('🗑️ Service Worker: Eliminando caché antiguo:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ Service Worker: Activación completada');
                return self.clients.claim();
            })
            .catch(error => {
                console.error('❌ Service Worker: Error en activación:', error);
            })
    );
});

// Interceptar peticiones de red
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Solo manejar peticiones del mismo origen
    if (url.origin !== location.origin) {
        return;
    }
    
    // Estrategia Cache First para archivos estáticos
    if (STATIC_FILES.includes(url.pathname) || 
        url.pathname.startsWith('/static/')) {
        
        event.respondWith(
            caches.match(request)
                .then(response => {
                    if (response) {
                        console.log('📦 Service Worker: Sirviendo desde caché:', url.pathname);
                        return response;
                    }
                    
                    return fetch(request)
                        .then(fetchResponse => {
                            const responseClone = fetchResponse.clone();
                            caches.open(STATIC_CACHE)
                                .then(cache => {
                                    cache.put(request, responseClone);
                                });
                            return fetchResponse;
                        });
                })
                .catch(error => {
                    console.error('❌ Service Worker: Error sirviendo archivo estático:', error);
                    // Fallback para páginas principales
                    if (url.pathname === '/' || url.pathname === '/chat') {
                        return caches.match('/');
                    }
                })
        );
    }
    
    // Estrategia Network First para API y contenido dinámico
    else if (url.pathname.startsWith('/api/') || 
             DYNAMIC_URLS.includes(url.pathname)) {
        
        event.respondWith(
            fetch(request)
                .then(response => {
                    // Solo cachear respuestas exitosas y solicitudes GET
                    if (response.status === 200 && request.method === 'GET') {
                        const responseClone = response.clone();
                        caches.open(DYNAMIC_CACHE)
                            .then(cache => {
                                cache.put(request, responseClone);
                            });
                    }
                    return response;
                })
                .catch(error => {
                    console.log('🔄 Service Worker: Red no disponible, buscando en caché:', url.pathname);
                    return caches.match(request);
                })
        );
    }
    
    // Para otras peticiones, usar la red directamente
    else {
        event.respondWith(fetch(request));
    }
});

// Manejar mensajes del cliente
self.addEventListener('message', event => {
    const { data } = event;
    
    switch (data.type) {
        case 'SKIP_WAITING':
            console.log('🔄 Service Worker: Saltando espera...');
            self.skipWaiting();
            break;
            
        case 'GET_VERSION':
            event.ports[0].postMessage({
                type: 'VERSION',
                version: CACHE_NAME
            });
            break;
            
        case 'CLEAR_CACHE':
            console.log('🗑️ Service Worker: Limpiando caché...');
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => caches.delete(cacheName))
                );
            }).then(() => {
                event.ports[0].postMessage({
                    type: 'CACHE_CLEARED',
                    success: true
                });
            });
            break;
            
        default:
            console.log('📨 Service Worker: Mensaje recibido:', data);
    }
});

// Notificar al cliente cuando el Service Worker esté listo
self.addEventListener('activate', event => {
    event.waitUntil(
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'SW_ACTIVATED',
                    version: CACHE_NAME
                });
            });
        })
    );
});

console.log('🔧 Service Worker: Cargado correctamente');