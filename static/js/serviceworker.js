// UkomboziniWomen Service Worker for Offline Support

const CACHE_NAME = 'ukombozini-cache-v1';
const DYNAMIC_CACHE = 'ukombozini-dynamic-cache-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js',
    'https://code.jquery.com/jquery-3.6.3.min.js',
    '/static/images/icon-160x160.png',
    '/login/',
    '/dashboard/',
    '/offline/',
];

// Install event - cache all static assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
            .then(() => self.skipWaiting()) // Force service worker to activate immediately
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    const cacheWhitelist = [CACHE_NAME, DYNAMIC_CACHE];
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
        .then(() => self.clients.claim()) // Take control of all clients
    );
});

// Fetch event - serve from cache or fetch from network
self.addEventListener('fetch', event => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip cross-origin requests
    if (new URL(event.request.url).origin !== location.origin && 
        !event.request.url.includes('cdn.jsdelivr.net') && 
        !event.request.url.includes('cdnjs.cloudflare.com') &&
        !event.request.url.includes('code.jquery.com')) {
        return;
    }

    // For HTML pages, use network-first strategy
    if (event.request.headers.get('Accept').includes('text/html')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseClone);
                        });
                    return response;
                })
                .catch(() => {
                    return caches.match(event.request)
                        .then(response => {
                            if (response) {
                                return response;
                            }
                            return caches.match('/offline/');
                        });
                })
        );
        return;
    }

    // For other requests, use cache-first strategy
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Cache hit - return response
                if (response) {
                    return response;
                }

                // Clone the request
                const fetchRequest = event.request.clone();

                return fetch(fetchRequest)
                    .then(response => {
                        // Check if valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone the response
                        const responseToCache = response.clone();

                        // Add to dynamic cache
                        caches.open(DYNAMIC_CACHE)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    })
                    .catch(() => {
                        // If the request is for an image, return a fallback image
                        if (event.request.url.match(/\.(jpg|jpeg|png|gif|svg)$/)) {
                            return caches.match('/static/images/offline-image.png');
                        }
                        
                        // Return whatever we have
                        return new Response('Network error occurred');
                    });
            })
    );
});

// Handle background sync for forms
self.addEventListener('sync', event => {
    if (event.tag === 'sync-forms') {
        event.waitUntil(syncForms());
    }
});

// Function to sync form data
async function syncForms() {
    try {
        // Open IndexedDB
        const db = await new Promise((resolve, reject) => {
            const request = indexedDB.open('ukomboziniDB', 1);
            request.onerror = reject;
            request.onsuccess = event => resolve(event.target.result);
        });

        // Get all pending form data
        const transaction = db.transaction(['pendingFormData'], 'readwrite');
        const store = transaction.objectStore('pendingFormData');
        const pendingForms = await new Promise((resolve, reject) => {
            const request = store.getAll();
            request.onerror = reject;
            request.onsuccess = event => resolve(event.target.result);
        });

        // Submit each form
        const results = await Promise.all(pendingForms.map(async formData => {
            try {
                // Determine the URL based on form ID
                const url = formUrlMapping[formData.formId] || '/api/sync-form/';
                
                // Send the data
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify(formData.data),
                });

                if (response.ok) {
                    // If successfully synced, remove from IndexedDB
                    const delRequest = store.delete(formData.id);
                    return new Promise((resolve, reject) => {
                        delRequest.onsuccess = () => resolve(true);
                        delRequest.onerror = reject;
                    });
                }
                return false;
            } catch (error) {
                console.error('Sync error for form:', error);
                return false;
            }
        }));

        // Show notification if synced successfully
        if (results.some(result => result)) {
            showSyncNotification();
        }
    } catch (error) {
        console.error('Sync error:', error);
    }
}

// Mapping of form IDs to API endpoints
const formUrlMapping = {
    'member-form': '/api/members/',
    'group-form': '/api/groups/',
    'loan-form': '/api/loans/',
    'payment-form': '/api/payments/',
    'savings-form': '/api/savings/',
    // Add more mappings as needed
};

// Helper function to get cookie value
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Show notification when data is synced
function showSyncNotification() {
    self.registration.showNotification('UkomboziniWomen System', {
        body: 'Your data has been successfully synced!',
        icon: '/static/images/icon-160x160.png',
    });
} 