// UkomboziniWomen Daily Report Form Handler with Offline Support

document.addEventListener('DOMContentLoaded', function() {
    // Initialize offline functionality
    initOfflineFeatures();
    
    // Setup form handlers
    setupFormHandlers();
    
    // Setup group entry and calculations
    setupGroupEntryHandler();
    setupCalculations();
    
    // Check for pending forms
    checkPendingForms();
});

// Initialize offline features
function initOfflineFeatures() {
    // Add offline status indicator to nav
    addOfflineIndicator();
    
    // Add event listeners for online/offline events
    window.addEventListener('online', handleOnlineStatusChange);
    window.addEventListener('offline', handleOnlineStatusChange);
    
    // Initialize notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    // Update status indicator initially
    handleOnlineStatusChange();
}

// Add offline status indicator to the UI
function addOfflineIndicator() {
    const navbar = document.querySelector('.navbar-nav');
    if (!navbar) return;
    
    const indicator = document.createElement('li');
    indicator.className = 'nav-item ms-2';
    indicator.innerHTML = `
        <div id="offline-indicator" class="online" title="You are online">
            <i class="fas fa-wifi"></i>
        </div>
    `;
    
    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        #offline-indicator {
            padding: 8px;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
        }
        #offline-indicator.online {
            background-color: #28a745;
            color: white;
        }
        #offline-indicator.offline {
            background-color: #dc3545;
            color: white;
        }
        .pending-forms-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            background-color: #fd7e14;
            color: white;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            font-size: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #offline-toast {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        }
    `;
    
    document.head.appendChild(style);
    navbar.appendChild(indicator);
}

// Handle online/offline status change
function handleOnlineStatusChange() {
    if (window.offlineStorage) {
        window.offlineStorage.updateOnlineStatus();
    }
    
    const isOnline = navigator.onLine;
    
    // Show toast notification
    showConnectivityToast(isOnline);
    
    // If coming back online, try to sync
    if (isOnline && window.offlineStorage) {
        window.offlineStorage.syncPendingForms().then(synced => {
            if (synced) {
                showSyncToast(true);
            }
        });
    }
}

// Show toast notification for connectivity change
function showConnectivityToast(isOnline) {
    // Remove any existing toast
    const existingToast = document.getElementById('offline-toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create new toast
    const toast = document.createElement('div');
    toast.id = 'offline-toast';
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="toast-header ${isOnline ? 'bg-success' : 'bg-danger'} text-white">
            <i class="fas ${isOnline ? 'fa-wifi' : 'fa-exclamation-triangle'} me-2"></i>
            <strong class="me-auto">${isOnline ? 'Online' : 'Offline'}</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${isOnline ? 
                'You are back online. Your data will be synced automatically.' : 
                'You are offline. Your reports will be saved locally and synced when you reconnect.'}
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Initialize and show the toast
    const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 5000 });
    bsToast.show();
}

// Show sync toast notification
function showSyncToast(success) {
    // Remove any existing toast
    const existingToast = document.getElementById('offline-toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create new toast
    const toast = document.createElement('div');
    toast.id = 'offline-toast';
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="toast-header ${success ? 'bg-success' : 'bg-warning'} text-white">
            <i class="fas ${success ? 'fa-check-circle' : 'fa-exclamation-circle'} me-2"></i>
            <strong class="me-auto">Data Sync</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${success ? 
                'Your offline data has been successfully synchronized.' : 
                'Some data could not be synchronized. Please try again later.'}
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Initialize and show the toast
    const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 5000 });
    bsToast.show();
}

// Check for pending forms in IndexedDB
async function checkPendingForms() {
    if (!window.offlineStorage) return;
    
    const pendingForms = await window.offlineStorage.getPendingForms();
    const indicator = document.getElementById('offline-indicator');
    
    if (pendingForms.length > 0 && indicator) {
        // Remove existing badge if any
        const existingBadge = indicator.querySelector('.pending-forms-badge');
        if (existingBadge) {
            existingBadge.remove();
        }
        
        // Add badge with count
        const badge = document.createElement('span');
        badge.className = 'pending-forms-badge';
        badge.textContent = pendingForms.length;
        indicator.appendChild(badge);
        
        // Add tooltip
        indicator.setAttribute('title', `${pendingForms.length} reports waiting to be synced`);
    }
}

// Setup form submission handler
function setupFormHandlers() {
    const form = document.getElementById('dailyReportForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate form
        if (!form.checkValidity()) {
            e.stopPropagation();
            form.classList.add('was-validated');
            return;
        }
        
        // Serialize form data
        const formData = new FormData(form);
        const formObject = {};
        
        // Convert FormData to object
        for (const [key, value] of formData.entries()) {
            // Handle array fields
            if (key.endsWith('[]')) {
                const cleanKey = key.slice(0, -2);
                if (!formObject[cleanKey]) {
                    formObject[cleanKey] = [];
                }
                formObject[cleanKey].push(value);
            } else {
                formObject[key] = value;
            }
        }
        
        // Check if offline storage is available
        if (window.offlineStorage) {
            // Show processing indicator
            showProcessingIndicator(true);
            
            try {
                // Process form with offline support
                const result = await window.offlineStorage.processFormSubmission(
                    'dailyReportForm', 
                    formObject,
                    form.action
                );
                
                // Hide processing indicator
                showProcessingIndicator(false);
                
                if (result.success) {
                    if (result.offline) {
                        showOfflineSubmissionSuccess();
                    } else {
                        // Success, redirect to success page
                        window.location.href = '/user-management/field-officers/report-success/';
                    }
                } else {
                    showSubmissionError('Could not save your report. Please try again.');
                }
            } catch (error) {
                console.error('Form submission error:', error);
                showProcessingIndicator(false);
                showSubmissionError('An error occurred: ' + error.message);
            }
        } else {
            // Fall back to normal form submission
            form.submit();
        }
    });
    
    // Handle "Generate PDF Report" button
    const pdfButton = document.getElementById('generate-report');
    if (pdfButton) {
        pdfButton.addEventListener('click', function() {
            // Simple HTML to PDF conversion in the browser
            if (window.print) {
                window.print();
            }
        });
    }
}

// Show processing indicator
function showProcessingIndicator(show) {
    let indicator = document.getElementById('processing-indicator');
    
    if (show) {
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'processing-indicator';
            indicator.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center bg-dark bg-opacity-50';
            indicator.style.zIndex = '9999';
            
            indicator.innerHTML = `
                <div class="card p-4">
                    <div class="d-flex flex-column align-items-center">
                        <div class="spinner-border text-primary mb-3" role="status">
                            <span class="visually-hidden">Processing...</span>
                        </div>
                        <div>Processing your report...</div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(indicator);
        } else {
            indicator.style.display = 'flex';
        }
    } else if (indicator) {
        indicator.style.display = 'none';
    }
}

// Show offline submission success message
function showOfflineSubmissionSuccess() {
    const alertBox = document.createElement('div');
    alertBox.className = 'alert alert-warning alert-dismissible fade show mt-3';
    alertBox.setAttribute('role', 'alert');
    
    alertBox.innerHTML = `
        <h4 class="alert-heading"><i class="fas fa-wifi-slash me-2"></i>Report Saved Offline!</h4>
        <p>You are currently offline. Your report has been saved to your device and will be automatically 
        submitted when you reconnect to the internet.</p>
        <hr>
        <p class="mb-0">You can continue using the system and submit more reports if needed.</p>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert before the form
    const form = document.getElementById('dailyReportForm');
    form.parentNode.insertBefore(alertBox, form);
    
    // Reset the form
    form.reset();
    form.classList.remove('was-validated');
    
    // Jump to the top of the page
    window.scrollTo(0, 0);
    
    // Update pending forms count
    setTimeout(() => {
        checkPendingForms();
    }, 500);
}

// Show submission error
function showSubmissionError(message) {
    const alertBox = document.createElement('div');
    alertBox.className = 'alert alert-danger alert-dismissible fade show mt-3';
    alertBox.setAttribute('role', 'alert');
    
    alertBox.innerHTML = `
        <h4 class="alert-heading"><i class="fas fa-exclamation-triangle me-2"></i>Error</h4>
        <p>${message}</p>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert before the form
    const form = document.getElementById('dailyReportForm');
    form.parentNode.insertBefore(alertBox, form);
    
    // Jump to the top of the page
    window.scrollTo(0, 0);
}

// Setup group entry handlers
function setupGroupEntryHandler() {
    const addGroupBtn = document.getElementById('add-group');
    if (!addGroupBtn) return;
    
    // Add group button handler
    addGroupBtn.addEventListener('click', function() {
        const groupEntries = document.getElementById('group-entries');
        const entryTemplate = groupEntries.querySelector('.group-entry');
        
        // Clone the first group entry
        const newEntry = entryTemplate.cloneNode(true);
        
        // Clear all input values in the new entry
        const inputs = newEntry.querySelectorAll('input');
        inputs.forEach(input => {
            input.value = '';
            if (input.type === 'number') {
                input.value = '0';
            }
        });
        
        // Add a remove button
        const actionsRow = document.createElement('div');
        actionsRow.className = 'row mt-3';
        actionsRow.innerHTML = `
            <div class="col-12 text-end">
                <button type="button" class="btn btn-outline-danger btn-sm remove-group">
                    <i class="fas fa-trash me-1"></i>Remove Group
                </button>
            </div>
        `;
        newEntry.appendChild(actionsRow);
        
        // Add a divider
        newEntry.style.borderTop = '2px dashed #ccc';
        newEntry.style.paddingTop = '15px';
        
        // Add the new entry to the DOM
        groupEntries.appendChild(newEntry);
        
        // Add event listener to the remove button
        const removeBtn = newEntry.querySelector('.remove-group');
        removeBtn.addEventListener('click', function() {
            newEntry.remove();
            updateSummary();
        });
        
        // Setup calculations for the new entry
        setupCalculationsForEntry(newEntry);
        
        // Update summary
        updateSummary();
    });
}

// Setup calculations and summary
function setupCalculations() {
    const groupEntries = document.getElementById('group-entries');
    if (!groupEntries) return;
    
    const entries = groupEntries.querySelectorAll('.group-entry');
    entries.forEach(entry => {
        setupCalculationsForEntry(entry);
    });
    
    // Initial summary update
    updateSummary();
}

// Setup calculations for a single group entry
function setupCalculationsForEntry(entry) {
    // Setup savings calculation
    const savingsInputs = entry.querySelectorAll('.savings-input');
    const totalSavings = entry.querySelector('.total-savings');
    
    savingsInputs.forEach(input => {
        input.addEventListener('input', () => {
            calculateTotalSavings(entry);
            calculateTotalMoney(entry);
            updateSummary();
        });
    });
    
    // Setup loan repayment calculation
    const loanRepaid = entry.querySelector('.loan-repaid');
    const totalMoney = entry.querySelector('.total-money');
    
    if (loanRepaid) {
        loanRepaid.addEventListener('input', () => {
            calculateTotalMoney(entry);
            updateSummary();
        });
    }
    
    // Initial calculations
    calculateTotalSavings(entry);
    calculateTotalMoney(entry);
}

// Calculate total savings for a group entry
function calculateTotalSavings(entry) {
    const savingsInputs = entry.querySelectorAll('.savings-input');
    const totalSavings = entry.querySelector('.total-savings');
    
    if (!totalSavings) return;
    
    let total = 0;
    savingsInputs.forEach(input => {
        const value = parseFloat(input.value) || 0;
        total += value;
    });
    
    totalSavings.value = total.toFixed(2);
}

// Calculate total money collected for a group entry
function calculateTotalMoney(entry) {
    const loanRepaid = entry.querySelector('.loan-repaid');
    const totalSavings = entry.querySelector('.total-savings');
    const totalMoney = entry.querySelector('.total-money');
    
    if (!totalMoney || !loanRepaid || !totalSavings) return;
    
    const loanAmount = parseFloat(loanRepaid.value) || 0;
    const savingsAmount = parseFloat(totalSavings.value) || 0;
    
    totalMoney.value = (loanAmount + savingsAmount).toFixed(2);
}

// Update the summary section
function updateSummary() {
    const groupEntries = document.getElementById('group-entries');
    if (!groupEntries) return;
    
    const entries = groupEntries.querySelectorAll('.group-entry');
    const summaryGroups = document.getElementById('summary-groups');
    const summaryAttendees = document.getElementById('summary-attendees');
    const summaryLoans = document.getElementById('summary-loans');
    const summarySavings = document.getElementById('summary-savings');
    const summaryMoney = document.getElementById('summary-money');
    
    let totalGroups = entries.length;
    let totalAttendees = 0;
    let totalLoans = 0;
    let totalSavings = 0;
    let totalMoney = 0;
    
    entries.forEach(entry => {
        // Get attendees
        const attendeesInput = entry.querySelector('input[name="total_attendet[]"]');
        if (attendeesInput) {
            totalAttendees += parseInt(attendeesInput.value) || 0;
        }
        
        // Get loans repaid
        const loanRepaidInput = entry.querySelector('.loan-repaid');
        if (loanRepaidInput) {
            totalLoans += parseFloat(loanRepaidInput.value) || 0;
        }
        
        // Get total savings
        const savingsInput = entry.querySelector('.total-savings');
        if (savingsInput) {
            totalSavings += parseFloat(savingsInput.value) || 0;
        }
        
        // Get total money
        const moneyInput = entry.querySelector('.total-money');
        if (moneyInput) {
            totalMoney += parseFloat(moneyInput.value) || 0;
        }
    });
    
    // Update summary displays
    if (summaryGroups) summaryGroups.textContent = totalGroups;
    if (summaryAttendees) summaryAttendees.textContent = totalAttendees;
    if (summaryLoans) summaryLoans.textContent = `KSh ${totalLoans.toFixed(2)}`;
    if (summarySavings) summarySavings.textContent = `KSh ${totalSavings.toFixed(2)}`;
    if (summaryMoney) summaryMoney.textContent = `KSh ${totalMoney.toFixed(2)}`;
} 