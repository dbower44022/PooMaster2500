# Puppy Bathroom Tracker - Web Interface

A responsive web interface for the Puppy Bathroom Tracker system.

## Features

### Dashboard (index.html)
- **Real-time Status Display**: Visual LED indicators showing current status
- **Color-coded LEDs**: 
  - Green (0-60% of average time)
  - Yellow (60-75%)
  - Red (75-90%)
  - Flashing red with alarm (90%+)
- **Separate Tracking**: Independent displays for pee and poo
- **Quick Action Buttons**: Log events with a single click
- **Recent Events**: View last 24 hours of activity
- **Accident Logging**: Form to record accidents with details
- **Auto-refresh**: Updates every 30 seconds automatically

### Admin Panel (admin.html)
- **Comprehensive Analytics**: Detailed statistics for configurable time periods
- **Interactive Charts**: 
  - Event timeline showing daily patterns
  - Average interval comparison
- **Full History**: Filterable table of all events
- **Accident History**: Complete list of accidents with details
- **Flexible Timeframes**: View data from 1 day to 30 days

## Installation

### Prerequisites
- The FastAPI backend server must be running
- A modern web browser (Chrome, Firefox, Safari, Edge)

### Setup

#### Option 1: Direct File Access (Simplest)
1. Open `index.html` directly in your web browser
2. The interface will connect to `http://localhost:8000` by default

#### Option 2: Local Web Server (Recommended)
Using Python's built-in HTTP server:

```bash
cd web
python -m http.server 8080
```

Then open your browser to:
- Dashboard: `http://localhost:8080/index.html`
- Admin: `http://localhost:8080/admin.html`

#### Option 3: Deploy to Web Server
Copy all files to your web server (IIS, Apache, nginx, etc.) and access via your server's URL.

## Configuration

### Change API URL
If your backend is not running on `localhost:8000`, edit the API URL in both JavaScript files:

**In app.js and admin.js:**
```javascript
const API_BASE_URL = 'http://YOUR_SERVER_IP:8000';
```

For example, if your server PC's IP is `192.168.1.100`:
```javascript
const API_BASE_URL = 'http://192.168.1.100:8000';
```

### Update Interval
To change how often the dashboard refreshes (default: 30 seconds):

**In app.js:**
```javascript
const UPDATE_INTERVAL = 30000; // milliseconds (30000 = 30 seconds)
```

## Usage

### Dashboard

1. **View Current Status**
   - LED colors show time elapsed vs. average
   - Numbers show exact hours since last event
   - Percentage shows progress toward alarm threshold

2. **Log Events**
   - Click "Log Pee Event" when puppy pees
   - Click "Log Poo Event" when puppy poops
   - Status updates immediately after logging

3. **Log Accidents**
   - Select type (pee or poo)
   - Enter estimated time
   - Enter location
   - Add optional notes
   - Click "Log Accident"

4. **View Recent Activity**
   - Scroll through last 24 hours of events
   - See timestamp and how long ago

### Admin Panel

1. **Analytics Period**
   - Select timeframe from dropdown (1-30 days)
   - Click refresh to update data

2. **View Statistics**
   - See total event counts
   - Average intervals
   - Current status
   - Accident counts

3. **Analyze Charts**
   - Timeline shows daily event patterns
   - Bar chart compares average intervals

4. **Browse History**
   - Full table of all events in selected period
   - Filter by pee/poo using checkboxes
   - Sort chronologically

5. **Review Accidents**
   - Complete list with timestamps, locations, and notes

## Mobile Access

The interface is fully responsive and works on:
- Desktop computers
- Tablets
- Smartphones

Access from any device on your local network using your server's IP address.

## Troubleshooting

### "Failed to fetch" or Connection Errors

**Problem**: Cannot connect to backend server

**Solutions**:
1. Verify the backend is running: Open `http://localhost:8000/docs` in browser
2. Check the API_BASE_URL in app.js and admin.js
3. If accessing from another device, use the server's IP address instead of localhost
4. Check Windows Firewall is allowing port 8000

### CORS Errors

**Problem**: Cross-Origin Request Blocked errors in browser console

**Solution**: The backend already has CORS enabled. If you still see errors:
1. Make sure you're using the same protocol (both http:// or both https://)
2. Try running the web interface from a local web server instead of opening files directly

### Data Not Updating

**Problem**: Status shows "--" or old data

**Solutions**:
1. Check browser console (F12) for errors
2. Verify backend server is responding: `http://localhost:8000/api/status`
3. Refresh the page (Ctrl+F5 or Cmd+Shift+R)
4. Check browser network tab to see if requests are being made

### Charts Not Displaying

**Problem**: Chart.js not loading in admin panel

**Solutions**:
1. Ensure you have internet connection (Chart.js loads from CDN)
2. Check browser console for Chart.js loading errors
3. Try clearing browser cache

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Files

- `index.html` - Main dashboard page
- `admin.html` - Admin/analytics page
- `style.css` - Shared stylesheet for both pages
- `app.js` - Dashboard JavaScript
- `admin.js` - Admin panel JavaScript
- `README.md` - This file

## Features in Detail

### Auto-Update System
- Dashboard polls server every 30 seconds
- Shows connection status in footer
- Continues updating even if minimized (unless browser throttles)

### Visual Feedback
- LED colors match ESP32 device colors
- Smooth transitions and animations
- Toast notifications for actions
- Loading indicators during data fetch

### Responsive Design
- Adapts to screen size automatically
- Touch-friendly buttons on mobile
- Readable on any device
- Optimized layouts for portrait and landscape

## Integration with Other Components

### ESP32 Devices
Both web interface and ESP32 devices use the same API endpoints, ensuring synchronized data.

### Home Assistant
The web interface can complement Home Assistant dashboards for situations where HA isn't accessible.

## Customization

### Change Colors
Edit color variables in `style.css`:
```css
:root {
    --primary-color: #4CAF50;
    --secondary-color: #2196F3;
    --danger-color: #f44336;
    /* ... etc */
}
```

### Modify Layout
All layouts use CSS Grid and Flexbox, making it easy to adjust spacing and positioning in `style.css`.

### Add Features
JavaScript uses vanilla ES6+ with async/await. Easy to extend with new API calls or UI elements.

## Security Notes

- This interface has no authentication
- Designed for local network use only
- Do not expose to the public internet without adding authentication
- Consider setting up a VPN if you need remote access

## Support

If you encounter issues:
1. Check browser console (F12) for error messages
2. Verify backend server is running and accessible
3. Test API endpoints directly in browser
4. Check network connectivity

## Next Steps

After setting up the web interface:
1. Test all features with sample data
2. Bookmark the dashboard for quick access
3. Set up on mobile devices for convenience
4. Proceed to ESP32 device setup

Enjoy tracking your puppy's bathroom habits! 🐕
