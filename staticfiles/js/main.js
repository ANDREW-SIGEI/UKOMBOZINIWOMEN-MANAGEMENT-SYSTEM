// UkomboziniWomen Management System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Auto hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert-auto-dismiss').fadeOut('slow');
    }, 5000);

    // Toggle sidebar on mobile
    $('#sidebarCollapse').on('click', function() {
        $('#sidebar').toggleClass('active');
    });

    // Confirm delete actions
    $('.confirm-delete').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
            return false;
        }
    });

    // Handle offline mode for forms
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        // Register forms for background sync
        const forms = document.querySelectorAll('.offline-enabled-form');
        
        forms.forEach(form => {
            form.addEventListener('submit', event => {
                // If we're offline, store the form data and sync later
                if (!navigator.onLine) {
                    event.preventDefault();
                    
                    const formData = new FormData(form);
                    const formObject = {};
                    
                    formData.forEach((value, key) => {
                        formObject[key] = value;
                    });
                    
                    // Store form data in IndexedDB
                    storeForSync(form.id, formObject).then(() => {
                        showOfflineNotification();
                    });
                }
            });
        });
    }
});

// Function to show offline notification
function showOfflineNotification() {
    const notification = document.createElement('div');
    notification.className = 'alert alert-warning alert-dismissible fade show position-fixed bottom-0 end-0 m-3';
    notification.innerHTML = `
        <strong>You're offline!</strong> Your changes will be saved and synced when you're back online.
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Function to store form data for sync
async function storeForSync(formId, formData) {
    // Open IndexedDB
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ukomboziniDB', 1);
        
        request.onupgradeneeded = function(event) {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('pendingFormData')) {
                db.createObjectStore('pendingFormData', { keyPath: 'id', autoIncrement: true });
            }
        };
        
        request.onsuccess = function(event) {
            const db = event.target.result;
            const transaction = db.transaction(['pendingFormData'], 'readwrite');
            const store = transaction.objectStore('pendingFormData');
            
            const item = {
                formId: formId,
                data: formData,
                timestamp: new Date().getTime()
            };
            
            const storeRequest = store.add(item);
            
            storeRequest.onsuccess = function() {
                resolve();
                // Register for sync if supported
                if ('serviceWorker' in navigator && 'SyncManager' in window) {
                    navigator.serviceWorker.ready.then(registration => {
                        registration.sync.register('sync-forms');
                    });
                }
            };
            
            storeRequest.onerror = function(error) {
                reject(error);
            };
        };
        
        request.onerror = function(error) {
            reject(error);
        };
    });
}

// Check connection status and update UI
function updateOnlineStatus() {
    const statusIndicator = document.getElementById('connection-status');
    if (statusIndicator) {
        if (navigator.onLine) {
            statusIndicator.innerHTML = '<i class="fas fa-wifi text-success"></i> Online';
            statusIndicator.className = 'text-success';
        } else {
            statusIndicator.innerHTML = '<i class="fas fa-exclamation-triangle text-warning"></i> Offline';
            statusIndicator.className = 'text-warning';
        }
    }
}

// Listen for online/offline events
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

// Update status when page loads
window.addEventListener('load', updateOnlineStatus); 