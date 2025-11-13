from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import sqlite3
import json
from contextlib import contextmanager
import os

app = FastAPI(title="Puppy Bathroom Tracker API", version="1.0.0")

# Enable CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "puppy_tracker.db")


# Pydantic models for API
class EventCreate(BaseModel):
    event_type: str  # "pee" or "poo"
    timestamp: Optional[datetime] = None


class AccidentCreate(BaseModel):
    estimated_time: datetime
    location: str
    notes: Optional[str] = None
    event_type: str  # "pee" or "poo"


class LEDStatus(BaseModel):
    pee: Dict[str, int]  # RGB values
    poo: Dict[str, int]  # RGB values
    pee_alarm: bool
    poo_alarm: bool
    pee_time_since: float  # hours
    poo_time_since: float  # hours
    pee_percentage: float
    poo_percentage: float


# Database context manager
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the database with required tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Accidents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                estimated_time DATETIME NOT NULL,
                location TEXT NOT NULL,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()


def calculate_average_interval(event_type: str, days: int = 7) -> float:
    """Calculate average time between events in hours"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get events from last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        cursor.execute("""
            SELECT timestamp FROM events 
            WHERE event_type = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        """, (event_type, cutoff_date.isoformat()))
        
        events = cursor.fetchall()
        
        if len(events) < 2:
            # Default averages if not enough data
            return 4.0 if event_type == "pee" else 12.0
        
        # Calculate intervals between consecutive events
        intervals = []
        for i in range(1, len(events)):
            prev_time = datetime.fromisoformat(events[i-1]['timestamp'])
            curr_time = datetime.fromisoformat(events[i]['timestamp'])
            interval_hours = (curr_time - prev_time).total_seconds() / 3600
            intervals.append(interval_hours)
        
        # Return average
        return sum(intervals) / len(intervals) if intervals else (4.0 if event_type == "pee" else 12.0)


def get_last_event_time(event_type: str) -> Optional[datetime]:
    """Get the timestamp of the last event of a given type"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp FROM events 
            WHERE event_type = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (event_type,))
        
        result = cursor.fetchone()
        if result:
            return datetime.fromisoformat(result['timestamp'])
        return None


def calculate_led_color(percentage: float) -> Dict[str, int]:
    """
    Calculate RGB color based on percentage of average time elapsed
    0-60%: Green
    60-75%: Green to Yellow transition
    75-90%: Yellow to Red transition
    90%+: Red (will flash on device)
    """
    if percentage < 60:
        # Green
        return {"r": 0, "g": 255, "b": 0}
    elif percentage < 75:
        # Transition from Green to Yellow (60-75%)
        # Green stays at 255, Red increases from 0 to 255
        progress = (percentage - 60) / 15  # 0 to 1
        red = int(255 * progress)
        return {"r": red, "g": 255, "b": 0}
    elif percentage < 90:
        # Transition from Yellow to Red (75-90%)
        # Red stays at 255, Green decreases from 255 to 0
        progress = (percentage - 75) / 15  # 0 to 1
        green = int(255 * (1 - progress))
        return {"r": 255, "g": green, "b": 0}
    else:
        # Red (90%+)
        return {"r": 255, "g": 0, "b": 0}


def get_status_for_type(event_type: str) -> Dict:
    """Get current status for a specific event type"""
    last_event = get_last_event_time(event_type)
    avg_interval = calculate_average_interval(event_type)
    
    if last_event is None:
        # No events yet - show as urgent
        return {
            "color": {"r": 255, "g": 0, "b": 0},
            "alarm": True,
            "time_since": 0.0,
            "percentage": 100.0,
            "average_interval": avg_interval
        }
    
    time_since = (datetime.now() - last_event).total_seconds() / 3600  # hours
    percentage = (time_since / avg_interval) * 100 if avg_interval > 0 else 0
    
    return {
        "color": calculate_led_color(percentage),
        "alarm": percentage >= 90,
        "time_since": round(time_since, 2),
        "percentage": round(percentage, 1),
        "average_interval": round(avg_interval, 2)
    }


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Puppy Bathroom Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "status": "/api/status",
            "log_event": "/api/events",
            "history": "/api/history",
            "analytics": "/api/analytics",
            "accidents": "/api/accidents"
        }
    }


@app.get("/api/status", response_model=LEDStatus)
async def get_status():
    """
    Get current status for both pee and poo with LED colors
    This endpoint is polled by ESP32 devices
    """
    pee_status = get_status_for_type("pee")
    poo_status = get_status_for_type("poo")
    
    return LEDStatus(
        pee=pee_status["color"],
        poo=poo_status["color"],
        pee_alarm=pee_status["alarm"],
        poo_alarm=poo_status["alarm"],
        pee_time_since=pee_status["time_since"],
        poo_time_since=poo_status["time_since"],
        pee_percentage=pee_status["percentage"],
        poo_percentage=poo_status["percentage"]
    )


@app.post("/api/events")
async def log_event(event: EventCreate):
    """
    Log a new bathroom event (pee or poo)
    Called by ESP32 devices or web interface
    """
    if event.event_type not in ["pee", "poo"]:
        raise HTTPException(status_code=400, detail="event_type must be 'pee' or 'poo'")
    
    timestamp = event.timestamp or datetime.now()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO events (event_type, timestamp)
            VALUES (?, ?)
        """, (event.event_type, timestamp.isoformat()))
        conn.commit()
        event_id = cursor.lastrowid
    
    return {
        "success": True,
        "event_id": event_id,
        "event_type": event.event_type,
        "timestamp": timestamp.isoformat()
    }


@app.get("/api/history")
async def get_history(
    event_type: Optional[str] = Query(None, description="Filter by 'pee' or 'poo'"),
    days: int = Query(7, description="Number of days to retrieve"),
    limit: int = Query(100, description="Maximum number of events")
):
    """
    Get event history
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if event_type:
            if event_type not in ["pee", "poo"]:
                raise HTTPException(status_code=400, detail="event_type must be 'pee' or 'poo'")
            
            cursor.execute("""
                SELECT * FROM events 
                WHERE event_type = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (event_type, cutoff_date.isoformat(), limit))
        else:
            cursor.execute("""
                SELECT * FROM events 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (cutoff_date.isoformat(), limit))
        
        events = [dict(row) for row in cursor.fetchall()]
    
    return {"events": events, "count": len(events)}


@app.get("/api/analytics")
async def get_analytics(days: int = Query(7, description="Number of days for analytics")):
    """
    Get analytics including averages, counts, and trends
    """
    pee_status = get_status_for_type("pee")
    poo_status = get_status_for_type("poo")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Count events by type
        cursor.execute("""
            SELECT event_type, COUNT(*) as count
            FROM events
            WHERE timestamp >= ?
            GROUP BY event_type
        """, (cutoff_date.isoformat(),))
        
        counts = {row['event_type']: row['count'] for row in cursor.fetchall()}
        
        # Get accident counts
        cursor.execute("""
            SELECT event_type, COUNT(*) as count
            FROM accidents
            WHERE estimated_time >= ?
            GROUP BY event_type
        """, (cutoff_date.isoformat(),))
        
        accident_counts = {row['event_type']: row['count'] for row in cursor.fetchall()}
    
    return {
        "period_days": days,
        "pee": {
            "count": counts.get("pee", 0),
            "average_interval_hours": pee_status["average_interval"],
            "time_since_last_hours": pee_status["time_since"],
            "current_percentage": pee_status["percentage"],
            "accidents": accident_counts.get("pee", 0)
        },
        "poo": {
            "count": counts.get("poo", 0),
            "average_interval_hours": poo_status["average_interval"],
            "time_since_last_hours": poo_status["time_since"],
            "current_percentage": poo_status["percentage"],
            "accidents": accident_counts.get("poo", 0)
        }
    }


@app.post("/api/accidents")
async def log_accident(accident: AccidentCreate):
    """
    Log an accident with estimated time and location
    """
    if accident.event_type not in ["pee", "poo"]:
        raise HTTPException(status_code=400, detail="event_type must be 'pee' or 'poo'")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO accidents (event_type, estimated_time, location, notes)
            VALUES (?, ?, ?, ?)
        """, (accident.event_type, accident.estimated_time.isoformat(), 
              accident.location, accident.notes))
        conn.commit()
        accident_id = cursor.lastrowid
    
    return {
        "success": True,
        "accident_id": accident_id
    }


@app.get("/api/accidents")
async def get_accidents(days: int = Query(7, description="Number of days to retrieve")):
    """
    Get accident history
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT * FROM accidents 
            WHERE estimated_time >= ?
            ORDER BY estimated_time DESC
        """, (cutoff_date.isoformat(),))
        
        accidents = [dict(row) for row in cursor.fetchall()]
    
    return {"accidents": accidents, "count": len(accidents)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
