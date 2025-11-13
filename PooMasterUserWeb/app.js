// Configuration
const API_BASE_URL = 'http://localhost:8000';
const UPDATE_INTERVAL = 30000; // 30 seconds

// API Configuration - Discovered dynamically
let apiConfig = {
    initialized: false,
    version: null,
    apiVersion: null,
    endpoints: {
        health: '/health',
        status: '/api/status',
        log_event: '/api/events',
        history: '/api/history',
        analytics: '/api/analytics',
        accidents: '/api/accidents'
    }
};

// Elements
const peeLed = document.getElementById('pee-led');
const pooLed = document.getElementById('poo-led');
const peeTime = document.getElementById('pee-time');
const pooTime = document.getElementById('poo-time');
const peePercentage = document.getElementById('pee-percentage');
const pooPercentage = document.getElementById('poo-percentage');
const peeAlarm = document.getElementById('pee-alarm');
const pooAlarm = document.getElementById('poo-alarm');
const peeAvg = document.getElementById('pee-avg');
const pooAvg = document.getElementById('poo-avg');
const lastUpdate = document.getElementById('last-update');
const connectionStatus = document.getElementById('connection-status');
const btnPee = document.getElementById('btn-pee');
const btnPoo = document.getElementById('btn-poo');
const accidentForm = document.getElementById('accident-form');
const recentEvents = document.getElementById('recent-events');
const toast = document.getElementById('toast');

let updateTimer;
let averageData = { pee: null, poo: null };

// Initialize API Configuration
async function initializeAPI() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (!response.ok) {
            throw new Error(`API returned status ${response.status}`);
        }
        
        const data = await response.json();
        
        // Store discovered configuration
        apiConfig.version = data.version;
        apiConfig.apiVersion = data.api_version;
        apiConfig.endpoints = data.endpoints;
        apiConfig.initialized = true;
        
        console.log(`Connected to Puppy Tracker API v${data.version} (API ${data.api_version})`);
        setConnectionStatus(true);
        return true;
        
    } catch (error) {
        console.error('Failed to initialize API:', error);
        showToast(`Failed to connect to API server at ${API_BASE_URL}. Please check that the server is running.`, 'error');
        setConnectionStatus(false);
        
        // Show error overlay
        showAPIError(error.message);
        return false;
    }
}

// Show API Error Overlay
function showAPIError(errorMessage) {
    const overlay = document.createElement('div');
    overlay.id = 'api-error-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    
    overlay.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; text-align: center;">
            <h2 style="color: #f44336; margin-bottom: 20px;">⚠️ API Connection Error</h2>
            <p style="margin-bottom: 15px;">Cannot connect to the Puppy Tracker API server.</p>
            <p style="color: #666; margin-bottom: 20px;">
                Server URL: <strong>${API_BASE_URL}</strong><br>
                Error: ${errorMessage}
            </p>
            <p style="margin-bottom: 20px;">Please ensure:</p>
            <ul style="text-align: left; margin-bottom: 20px; padding-left: 40px;">
                <li>The backend server is running (python main.py)</li>
                <li>The server URL is correct</li>
                <li>Your firewall allows the connection</li>
            </ul>
            <button id="retry-connection" style="
                padding: 12px 24px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1rem;
            ">Retry Connection</button>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    document.getElementById('retry-connection').addEventListener('click', async () => {
        overlay.remove();
        await initializeAndStart();
    });
}

// Initialize and start the application
async function initializeAndStart() {
    const success = await initializeAPI();
    
    if (success) {
        // Set default accident time to now
        const now = new Date();
        const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
            .toISOString()
            .slice(0, 16);
        document.getElementById('accident-time').value = localDateTime;
        
        // Start updating
        updateStatus();
        updateAnalytics();
        loadRecentEvents();
        
        // Set up periodic updates
        if (updateTimer) {
            clearInterval(updateTimer);
        }
        updateTimer = setInterval(() => {
            updateStatus();
            loadRecentEvents();
        }, UPDATE_INTERVAL);
        
        // Event listeners
        btnPee.addEventListener('click', () => logEvent('pee'));
        btnPoo.addEventListener('click', () => logEvent('poo'));
        accidentForm.addEventListener('submit', handleAccidentSubmit);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', initializeAndStart);

// Fetch current status
async function updateStatus() {
    if (!apiConfig.initialized) {
        console.warn('API not initialized, skipping status update');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${apiConfig.endpoints.status}`);
        if (!response.ok) throw new Error('Failed to fetch status');
        
        const status = await response.json();
        
        // Update Pee Status
        updateLED(peeLed, status.pee);
        peeTime.textContent = status.pee_time_since.toFixed(1);
        peePercentage.textContent = `${status.pee_percentage.toFixed(0)}%`;
        
        if (status.pee_alarm) {
            peeAlarm.classList.remove('hidden');
        } else {
            peeAlarm.classList.add('hidden');
        }
        
        // Update Poo Status
        updateLED(pooLed, status.poo);
        pooTime.textContent = status.poo_time_since.toFixed(1);
        pooPercentage.textContent = `${status.poo_percentage.toFixed(0)}%`;
        
        if (status.poo_alarm) {
            pooAlarm.classList.remove('hidden');
        } else {
            pooAlarm.classList.add('hidden');
        }
        
        // Update timestamp
        lastUpdate.textContent = new Date().toLocaleTimeString();
        setConnectionStatus(true);
        
    } catch (error) {
        console.error('Error updating status:', error);
        setConnectionStatus(false);
    }
}

// Update LED color
function updateLED(element, color) {
    element.style.backgroundColor = `rgb(${color.r}, ${color.g}, ${color.b})`;
}

// Fetch and update analytics
async function updateAnalytics() {
    if (!apiConfig.initialized) {
        console.warn('API not initialized, skipping analytics update');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${apiConfig.endpoints.analytics}?days=7`);
        if (!response.ok) throw new Error('Failed to fetch analytics');
        
        const analytics = await response.json();
        
        averageData.pee = analytics.pee.average_interval_hours;
        averageData.poo = analytics.poo.average_interval_hours;
        
        peeAvg.textContent = `${analytics.pee.average_interval_hours.toFixed(1)} hrs`;
        pooAvg.textContent = `${analytics.poo.average_interval_hours.toFixed(1)} hrs`;
        
    } catch (error) {
        console.error('Error updating analytics:', error);
    }
}

// Log bathroom event
async function logEvent(eventType) {
    if (!apiConfig.initialized) {
        showToast('API not initialized. Please refresh the page.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${apiConfig.endpoints.log_event}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ event_type: eventType })
        });
        
        if (!response.ok) throw new Error('Failed to log event');
        
        const result = await response.json();
        showToast(`${eventType.charAt(0).toUpperCase() + eventType.slice(1)} event logged successfully!`, 'success');
        
        // Immediate update
        updateStatus();
        updateAnalytics();
        loadRecentEvents();
        
    } catch (error) {
        console.error('Error logging event:', error);
        showToast('Failed to log event. Please try again.', 'error');
    }
}

// Handle accident form submission
async function handleAccidentSubmit(e) {
    e.preventDefault();
    
    if (!apiConfig.initialized) {
        showToast('API not initialized. Please refresh the page.', 'error');
        return;
    }
    
    const eventType = document.getElementById('accident-type').value;
    const estimatedTime = document.getElementById('accident-time').value;
    const location = document.getElementById('accident-location').value;
    const notes = document.getElementById('accident-notes').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}${apiConfig.endpoints.accidents}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event_type: eventType,
                estimated_time: estimatedTime,
                location: location,
                notes: notes || null
            })
        });
        
        if (!response.ok) throw new Error('Failed to log accident');
        
        showToast('Accident logged successfully!', 'success');
        
        // Reset form
        accidentForm.reset();
        const now = new Date();
        const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
            .toISOString()
            .slice(0, 16);
        document.getElementById('accident-time').value = localDateTime;
        
    } catch (error) {
        console.error('Error logging accident:', error);
        showToast('Failed to log accident. Please try again.', 'error');
    }
}

// Load recent events (last 24 hours)
async function loadRecentEvents() {
    if (!apiConfig.initialized) {
        console.warn('API not initialized, skipping recent events load');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${apiConfig.endpoints.history}?days=1&limit=20`);
        if (!response.ok) throw new Error('Failed to fetch history');
        
        const data = await response.json();
        
        if (data.events.length === 0) {
            recentEvents.innerHTML = '<div class="loading">No events in the last 24 hours</div>';
            return;
        }
        
        recentEvents.innerHTML = '';
        
        data.events.forEach(event => {
            const eventItem = document.createElement('div');
            eventItem.className = 'event-item';
            
            const eventDate = new Date(event.timestamp);
            const timeAgo = getTimeAgo(eventDate);
            const formattedTime = eventDate.toLocaleString();
            
            eventItem.innerHTML = `
                <span class="event-type">${event.event_type === 'pee' ? 'ðŸ’§' : 'ðŸ’©'}</span>
                <div class="event-info">
                    <div><strong>${event.event_type.charAt(0).toUpperCase() + event.event_type.slice(1)}</strong></div>
                    <div class="event-time">${formattedTime} (${timeAgo})</div>
                </div>
            `;
            
            recentEvents.appendChild(eventItem);
        });
        
    } catch (error) {
        console.error('Error loading recent events:', error);
        recentEvents.innerHTML = '<div class="loading">Failed to load events</div>';
    }
}

// Get time ago string
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'just now';
    
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    
    const days = Math.floor(hours / 24);
    return `${days} day${days !== 1 ? 's' : ''} ago`;
}

// Set connection status
function setConnectionStatus(connected) {
    if (connected) {
        connectionStatus.textContent = 'Connected';
        connectionStatus.classList.remove('disconnected');
    } else {
        connectionStatus.textContent = 'Disconnected';
        connectionStatus.classList.add('disconnected');
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (updateTimer) {
        clearInterval(updateTimer);
    }
});
