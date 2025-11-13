# Puppy Bathroom Tracker - Server Backend

FastAPI-based server for tracking puppy bathroom events with real-time LED status for ESP32 devices.

## Features

- **Event Tracking**: Log pee and poo events with timestamps
- **Smart LED Colors**: Automatic color calculation based on time elapsed vs. average intervals
  - Green (0-60% of average time)
  - Yellow (60-75%)
  - Red (75-90%)
  - Flashing Red with alarm (90%+)
- **Separate Tracking**: Independent timers and averages for pee and poo
- **Analytics**: Calculate rolling averages, view history, and track trends
- **Accident Logging**: Record accidents with estimated time, location, and notes
- **SQLite Database**: Lightweight, file-based storage
- **REST API**: Easy integration with ESP32 devices, web interfaces, and Home Assistant

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:8000`

3. View the interactive API documentation:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### GET /api/status
Get current LED status for both pee and poo. **This is polled by ESP32 devices.**

**Response:**
```json
{
  "pee": {"r": 0, "g": 255, "b": 0},
  "poo": {"r": 255, "g": 128, "b": 0},
  "pee_alarm": false,
  "poo_alarm": false,
  "pee_time_since": 2.5,
  "poo_time_since": 6.8,
  "pee_percentage": 62.5,
  "poo_percentage": 56.7
}
```

### POST /api/events
Log a new bathroom event.

**Request Body:**
```json
{
  "event_type": "pee",
  "timestamp": "2025-11-11T10:30:00"  // Optional, defaults to now
}
```

**Response:**
```json
{
  "success": true,
  "event_id": 123,
  "event_type": "pee",
  "timestamp": "2025-11-11T10:30:00"
}
```

### GET /api/history
Retrieve event history.

**Query Parameters:**
- `event_type`: Filter by "pee" or "poo" (optional)
- `days`: Number of days to retrieve (default: 7)
- `limit`: Maximum number of events (default: 100)

**Example:**
```
GET /api/history?event_type=pee&days=3&limit=50
```

### GET /api/analytics
Get comprehensive analytics including averages, counts, and current status.

**Query Parameters:**
- `days`: Number of days for analytics (default: 7)

**Response:**
```json
{
  "period_days": 7,
  "pee": {
    "count": 42,
    "average_interval_hours": 4.2,
    "time_since_last_hours": 2.5,
    "current_percentage": 59.5,
    "accidents": 2
  },
  "poo": {
    "count": 14,
    "average_interval_hours": 12.0,
    "time_since_last_hours": 6.8,
    "current_percentage": 56.7,
    "accidents": 1
  }
}
```

### POST /api/accidents
Log an accident with details.

**Request Body:**
```json
{
  "event_type": "pee",
  "estimated_time": "2025-11-11T14:20:00",
  "location": "Living room carpet",
  "notes": "Found wet spot near couch"
}
```

### GET /api/accidents
Retrieve accident history.

**Query Parameters:**
- `days`: Number of days to retrieve (default: 7)

## Testing the API

### Using curl (Command Line)

Log a pee event:
```bash
curl -X POST http://localhost:8000/api/events -H "Content-Type: application/json" -d "{\"event_type\": \"pee\"}"
```

Log a poo event:
```bash
curl -X POST http://localhost:8000/api/events -H "Content-Type: application/json" -d "{\"event_type\": \"poo\"}"
```

Get current status:
```bash
curl http://localhost:8000/api/status
```

Get analytics:
```bash
curl http://localhost:8000/api/analytics
```

### Using Python

```python
import requests

# Log an event
response = requests.post("http://localhost:8000/api/events", 
                        json={"event_type": "pee"})
print(response.json())

# Get status
status = requests.get("http://localhost:8000/api/status")
print(status.json())

# Get analytics
analytics = requests.get("http://localhost:8000/api/analytics?days=7")
print(analytics.json())
```

## LED Color Logic

The system calculates LED colors based on the percentage of average time elapsed:

- **0-60%**: Pure Green (0, 255, 0)
- **60-75%**: Green → Yellow transition (Red increases, Green stays 255)
- **75-90%**: Yellow → Red transition (Red stays 255, Green decreases)
- **90%+**: Pure Red (255, 0, 0) + Alarm triggered

## Database

SQLite database (`puppy_tracker.db`) is created automatically in the same directory as `main.py`.

### Tables

**events**
- `id`: Primary key
- `event_type`: "pee" or "poo"
- `timestamp`: When the event occurred
- `created_at`: When the record was created

**accidents**
- `id`: Primary key
- `event_type`: "pee" or "poo"
- `estimated_time`: Estimated time of accident
- `location`: Where the accident occurred
- `notes`: Additional details
- `created_at`: When the record was created

## Running as a Service (Windows)

To run the server automatically on Windows startup, you can:

1. **Using Task Scheduler:**
   - Create a basic task that runs `python main.py` at startup
   - Set the working directory to the puppy_tracker folder

2. **Using NSSM (Non-Sucking Service Manager):**
   - Download NSSM from https://nssm.cc/
   - Install as service: `nssm install PuppyTracker "C:\Python\python.exe" "C:\path\to\puppy_tracker\main.py"`

## Port Configuration

The server runs on port 8000 by default. To change the port, edit the last line of `main.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=YOUR_PORT_HERE)
```

## Next Steps

1. **ESP32 Firmware**: Create the Arduino/PlatformIO code for ESP32 devices
2. **Web Interface**: Build a responsive web dashboard
3. **Home Assistant Integration**: Configure REST sensors and automations

## Troubleshooting

**Database locked error**: Only one instance of the server should be running at a time.

**Port already in use**: Change the port number or stop the conflicting application.

**CORS errors from web interface**: The server is configured to allow all origins. If you need to restrict this, modify the `CORSMiddleware` configuration in `main.py`.
