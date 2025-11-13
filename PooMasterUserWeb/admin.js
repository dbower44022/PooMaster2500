// Configuration
const API_BASE_URL = 'http://localhost:8000';

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
const daysSelect = document.getElementById('days-select');
const refreshBtn = document.getElementById('refresh-btn');
const historyTable = document.getElementById('history-table');
const accidentHistory = document.getElementById('accident-history');
const lastUpdateEl = document.getElementById('last-update');
const toast = document.getElementById('toast');
const filterPee = document.getElementById('filter-pee');
const filterPoo = document.getElementById('filter-poo');

// Analytics elements
const peeCount = document.getElementById('pee-count');
const peeAvgInterval = document.getElementById('pee-avg-interval');
const peeTimeSince = document.getElementById('pee-time-since');
const peeCurrentPct = document.getElementById('pee-current-pct');
const peeAccidents = document.getElementById('pee-accidents');
const pooCount = document.getElementById('poo-count');
const pooAvgInterval = document.getElementById('poo-avg-interval');
const pooTimeSince = document.getElementById('poo-time-since');
const pooCurrentPct = document.getElementById('poo-current-pct');
const pooAccidents = document.getElementById('poo-accidents');

// Charts
let timelineChart = null;
let intervalChart = null;

// Data cache
let historyData = [];

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
        return true;
        
    } catch (error) {
        console.error('Failed to initialize API:', error);
        showToast(`Failed to connect to API server at ${API_BASE_URL}. Please check that the server is running.`, 'error');
        
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
        loadAllData();
        
        // Event listeners
        refreshBtn.addEventListener('click', loadAllData);
        daysSelect.addEventListener('change', loadAllData);
        filterPee.addEventListener('change', renderHistoryTable);
        filterPoo.addEventListener('change', renderHistoryTable);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', initializeAndStart);

// Load all data
async function loadAllData() {
    const days = parseInt(daysSelect.value);
    
    await Promise.all([
        loadAnalytics(days),
        loadHistory(days),
        loadAccidents(days)
    ]);
    
    lastUpdateEl.textContent = new Date().toLocaleString();
}

// Load analytics
async function loadAnalytics(days) {
    if (!apiConfig.initialized) {
        console.warn('API not initialized, skipping analytics load');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${apiConfig.endpoints.analytics}?days=${days}`);
        if (!response.ok) throw new Error('Failed to fetch analytics');
        
        const analytics = await response.json();
        
        // Update statistics
        peeCount.textContent = analytics.pee.count;
        peeAvgInterval.textContent = `${analytics.pee.average_interval_hours.toFixed(1)} hours`;
        peeTimeSince.textContent = `${analytics.pee.time_since_last_hours.toFixed(1)} hours`;
        peeCurrentPct.textContent = `${analytics.pee.current_percentage.toFixed(0)}%`;
        peeAccidents.textContent = analytics.pee.accidents;
        
        pooCount.textContent = analytics.poo.count;
        pooAvgInterval.textContent = `${analytics.poo.average_interval_hours.toFixed(1)} hours`;
        pooTimeSince.textContent = `${analytics.poo.time_since_last_hours.toFixed(1)} hours`;
        pooCurrentPct.textContent = `${analytics.poo.current_percentage.toFixed(0)}%`;
        pooAccidents.textContent = analytics.poo.accidents;
        
    } catch (error) {
        console.error('Error loading analytics:', error);
        showToast('Failed to load analytics', 'error');
    }
}

// Load full history
async function loadHistory(days) {
    if (!apiConfig.initialized) {
        console.warn('API not initialized, skipping history load');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${apiConfig.endpoints.history}?days=${days}&limit=1000`);
        if (!response.ok) throw new Error('Failed to fetch history');
        
        const data = await response.json();
        historyData = data.events;
        
        renderHistoryTable();
        updateCharts();
        
    } catch (error) {
        console.error('Error loading history:', error);
        historyTable.innerHTML = '<div class="loading">Failed to load history</div>';
    }
}

// Render history table
function renderHistoryTable() {
    if (historyData.length === 0) {
        historyTable.innerHTML = '<div class="loading">No events found</div>';
        return;
    }
    
    // Filter events
    const filteredEvents = historyData.filter(event => {
        if (event.event_type === 'pee' && !filterPee.checked) return false;
        if (event.event_type === 'poo' && !filterPoo.checked) return false;
        return true;
    });
    
    if (filteredEvents.length === 0) {
        historyTable.innerHTML = '<div class="loading">No events match the filter</div>';
        return;
    }
    
    // Create table
    let html = `
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Date & Time</th>
                    <th>Time Ago</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    filteredEvents.forEach(event => {
        const eventDate = new Date(event.timestamp);
        const timeAgo = getTimeAgo(eventDate);
        const icon = event.event_type === 'pee' ? 'ðŸ’§' : 'ðŸ’©';
        
        html += `
            <tr>
                <td>${icon} ${event.event_type.charAt(0).toUpperCase() + event.event_type.slice(1)}</td>
                <td>${eventDate.toLocaleString()}</td>
                <td>${timeAgo}</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    historyTable.innerHTML = html;
}

// Load accidents
async function loadAccidents(days) {
    if (!apiConfig.initialized) {
        console.warn('API not initialized, skipping accidents load');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${apiConfig.endpoints.accidents}?days=${days}`);
        if (!response.ok) throw new Error('Failed to fetch accidents');
        
        const data = await response.json();
        
        if (data.accidents.length === 0) {
            accidentHistory.innerHTML = '<div class="loading">No accidents recorded</div>';
            return;
        }
        
        accidentHistory.innerHTML = '';
        
        data.accidents.forEach(accident => {
            const accidentDate = new Date(accident.estimated_time);
            const icon = accident.event_type === 'pee' ? 'ðŸ’§' : 'ðŸ’©';
            
            const accidentItem = document.createElement('div');
            accidentItem.className = 'accident-item';
            
            accidentItem.innerHTML = `
                <div class="accident-header">
                    <span>${icon} ${accident.event_type.charAt(0).toUpperCase() + accident.event_type.slice(1)} Accident</span>
                    <span>${accidentDate.toLocaleString()}</span>
                </div>
                <div class="accident-details">
                    <strong>Location:</strong> ${accident.location}<br>
                    ${accident.notes ? `<strong>Notes:</strong> ${accident.notes}` : ''}
                </div>
            `;
            
            accidentHistory.appendChild(accidentItem);
        });
        
    } catch (error) {
        console.error('Error loading accidents:', error);
        accidentHistory.innerHTML = '<div class="loading">Failed to load accidents</div>';
    }
}

// Update charts
function updateCharts() {
    updateTimelineChart();
    updateIntervalChart();
}

// Update timeline chart
function updateTimelineChart() {
    const ctx = document.getElementById('timeline-chart');
    
    // Prepare data - count events by day
    const eventsByDay = {};
    
    historyData.forEach(event => {
        const date = new Date(event.timestamp).toLocaleDateString();
        if (!eventsByDay[date]) {
            eventsByDay[date] = { pee: 0, poo: 0 };
        }
        eventsByDay[date][event.event_type]++;
    });
    
    const dates = Object.keys(eventsByDay).sort();
    const peeData = dates.map(date => eventsByDay[date].pee);
    const pooData = dates.map(date => eventsByDay[date].poo);
    
    if (timelineChart) {
        timelineChart.destroy();
    }
    
    timelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'ðŸ’§ Pee Events',
                    data: peeData,
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'ðŸ’© Poo Events',
                    data: pooData,
                    borderColor: 'rgb(245, 87, 108)',
                    backgroundColor: 'rgba(245, 87, 108, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Update interval chart
function updateIntervalChart() {
    const ctx = document.getElementById('interval-chart');
    
    // Calculate intervals
    const peeEvents = historyData.filter(e => e.event_type === 'pee').sort((a, b) => 
        new Date(a.timestamp) - new Date(b.timestamp)
    );
    const pooEvents = historyData.filter(e => e.event_type === 'poo').sort((a, b) => 
        new Date(a.timestamp) - new Date(b.timestamp)
    );
    
    const peeIntervals = [];
    const pooIntervals = [];
    
    for (let i = 1; i < peeEvents.length; i++) {
        const interval = (new Date(peeEvents[i].timestamp) - new Date(peeEvents[i-1].timestamp)) / (1000 * 60 * 60);
        peeIntervals.push(interval);
    }
    
    for (let i = 1; i < pooEvents.length; i++) {
        const interval = (new Date(pooEvents[i].timestamp) - new Date(pooEvents[i-1].timestamp)) / (1000 * 60 * 60);
        pooIntervals.push(interval);
    }
    
    const peeAvg = peeIntervals.length > 0 ? peeIntervals.reduce((a, b) => a + b) / peeIntervals.length : 0;
    const pooAvg = pooIntervals.length > 0 ? pooIntervals.reduce((a, b) => a + b) / pooIntervals.length : 0;
    
    if (intervalChart) {
        intervalChart.destroy();
    }
    
    intervalChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Pee', 'Poo'],
            datasets: [
                {
                    label: 'Average Interval (hours)',
                    data: [peeAvg, pooAvg],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.6)',
                        'rgba(245, 87, 108, 0.6)'
                    ],
                    borderColor: [
                        'rgb(102, 126, 234)',
                        'rgb(245, 87, 108)'
                    ],
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hours'
                    }
                }
            }
        }
    });
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

// Show toast notification
function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
