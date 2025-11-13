from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import sqlite3
import json
from contextlib import contextmanager
import os
import logging
from logging.handlers import RotatingFileHandler

# ===== CONFIGURATION LOADER =====
# Priority: 1. Environment variables, 2. config.json, 3. Hardcoded defaults

def load_config_from_json(config_file: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration from JSON file in the executing directory.
    Returns empty dict if file doesn't exist or is invalid.
    """
    config_path = os.path.join(os.path.dirname(__file__), config_file)

    if not os.path.exists(config_path):
        return {}

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load config file {config_path}: {e}")
        return {}


def get_config_value(key: str, default: Any, value_type: type = str) -> Any:
    """
    Get configuration value with priority: env var > config.json > default

    Args:
        key: Configuration key name
        default: Default value if not found in env or config
        value_type: Type to convert the value to (str, int, float, bool)

    Returns:
        Configuration value with proper type
    """
    # 1. Check environment variable first (highest priority)
    env_value = os.getenv(key)
    if env_value is not None:
        try:
            if value_type == bool:
                return env_value.lower() in ('true', '1', 'yes', 'on')
            elif value_type == list:
                return env_value.split(',')
            else:
                return value_type(env_value)
        except (ValueError, TypeError):
            pass

    # 2. Check config.json (medium priority)
    json_config = load_config_from_json()
    if key in json_config:
        try:
            value = json_config[key]
            if value_type == list and isinstance(value, str):
                return value.split(',')
            elif value_type != type(value):
                return value_type(value)
            return value
        except (ValueError, TypeError):
            pass

    # 3. Return default (lowest priority)
    return default


# ===== ENVIRONMENT CONFIGURATION =====
# Configuration priority: Environment variables > config.json > Hardcoded defaults

# Application settings
APP_VERSION = get_config_value("APP_VERSION", "1.0.0", str)
API_VERSION = get_config_value("API_VERSION", "v1", str)
HOST = get_config_value("HOST", "0.0.0.0", str)
PORT = get_config_value("PORT", 8000, int)

# Database configuration
DB_PATH = get_config_value("DB_PATH", os.path.join(os.path.dirname(__file__), "puppy_tracker.db"), str)

# Logging configuration
LOG_LEVEL = get_config_value("LOG_LEVEL", "INFO", str).upper()
LOG_FILE = get_config_value("LOG_FILE", "puppy_tracker.log", str)
LOG_MAX_BYTES = get_config_value("LOG_MAX_BYTES", 10485760, int)  # 10MB default
LOG_BACKUP_COUNT = get_config_value("LOG_BACKUP_COUNT", 5, int)

# CORS configuration
CORS_ORIGINS = get_config_value("CORS_ORIGINS", "*", list)
if isinstance(CORS_ORIGINS, str):
    CORS_ORIGINS = CORS_ORIGINS.split(',')

# Default intervals (in hours) when no data is available
DEFAULT_PEE_INTERVAL = get_config_value("DEFAULT_PEE_INTERVAL", 4.0, float)
DEFAULT_POO_INTERVAL = get_config_value("DEFAULT_POO_INTERVAL", 12.0, float)

# ===== LOGGING SETUP =====
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Rotating file handler
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=LOG_MAX_BYTES,
    backupCount=LOG_BACKUP_COUNT
)
file_handler.setFormatter(log_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Configure root logger
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)

# Log configuration on startup
logger.info(f"Starting Puppy Bathroom Tracker API v{APP_VERSION}")
logger.info(f"Configuration: DB={DB_PATH}, LOG_LEVEL={LOG_LEVEL}, HOST={HOST}, PORT={PORT}")

# ===== FASTAPI APPLICATION =====
app = FastAPI(title="Puppy Bathroom Tracker API", version=APP_VERSION)

# Enable CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    logger.info(f"Initializing database at {DB_PATH}")
    try:
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
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        raise


def calculate_average_interval(event_type: str, days: int = 7) -> float:
    """Calculate average time between events in hours"""
    logger.debug(f"Calculating average interval for {event_type} over {days} days")
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
            # Default averages if not enough data (from environment or hardcoded defaults)
            default_interval = DEFAULT_PEE_INTERVAL if event_type == "pee" else DEFAULT_POO_INTERVAL
            logger.debug(f"Insufficient data for {event_type} ({len(events)} events), using default: {default_interval}h")
            return default_interval

        # Calculate intervals between consecutive events
        intervals = []
        for i in range(1, len(events)):
            prev_time = datetime.fromisoformat(events[i - 1]['timestamp'])
            curr_time = datetime.fromisoformat(events[i]['timestamp'])
            interval_hours = (curr_time - prev_time).total_seconds() / 3600
            intervals.append(interval_hours)

        # Return average (use environment-configured defaults as fallback)
        avg = sum(intervals) / len(intervals) if intervals else (DEFAULT_PEE_INTERVAL if event_type == "pee" else DEFAULT_POO_INTERVAL)
        logger.debug(f"Average interval for {event_type}: {avg:.2f}h (from {len(events)} events)")
        return avg


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
        logger.warning(f"No events found for {event_type}, returning urgent status")
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

    status = {
        "color": calculate_led_color(percentage),
        "alarm": percentage >= 90,
        "time_since": round(time_since, 2),
        "percentage": round(percentage, 1),
        "average_interval": round(avg_interval, 2)
    }

    if status["alarm"]:
        logger.warning(f"{event_type} alarm triggered! Time since last: {status['time_since']}h, percentage: {status['percentage']}%")

    return status


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Application starting up...")
    init_db()
    logger.info("Puppy Bathroom Tracker API is ready")


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Puppy Bathroom Tracker API",
        "version": APP_VERSION,
        "api_version": API_VERSION,
        "endpoints": {
            "health": "/health",
            "status": f"/api/{API_VERSION}/status",
            "log_event": f"/api/{API_VERSION}/events",
            "history": f"/api/{API_VERSION}/history",
            "analytics": f"/api/{API_VERSION}/analytics",
            "accidents": f"/api/{API_VERSION}/accidents"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    Returns the health status of the application and database
    """
    try:
        # Check database connectivity
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            db_healthy = cursor.fetchone() is not None

        logger.info("Health check successful")
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected" if db_healthy else "disconnected",
            "version": APP_VERSION,
            "api_version": API_VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": "disconnected",
            "error": str(e),
            "version": APP_VERSION,
            "api_version": API_VERSION
        }


@app.get("/api/v1/status", response_model=LEDStatus)
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


@app.post("/api/v1/events")
async def log_event(event: EventCreate):
    """
    Log a new bathroom event (pee or poo)
    Called by ESP32 devices or web interface
    """
    logger.info(f"Received event logging request: {event.event_type}")

    if event.event_type not in ["pee", "poo"]:
        logger.error(f"Invalid event_type received: {event.event_type}")
        raise HTTPException(status_code=400, detail="event_type must be 'pee' or 'poo'")

    timestamp = event.timestamp or datetime.now()

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (event_type, timestamp)
                VALUES (?, ?)
            """, (event.event_type, timestamp.isoformat()))
            conn.commit()
            event_id = cursor.lastrowid

        logger.info(f"Event logged successfully: ID={event_id}, type={event.event_type}, timestamp={timestamp.isoformat()}")

        return {
            "success": True,
            "event_id": event_id,
            "event_type": event.event_type,
            "timestamp": timestamp.isoformat()
        }
    except Exception as e:
        logger.error(f"Error logging event: {e}", exc_info=True)
        raise


@app.get("/api/v1/history")
async def get_history(
        event_type: Optional[str] = Query(None, description="Filter by 'pee' or 'poo'"),
        days: int = Query(7, description="Number of days to retrieve"),
        limit: int = Query(100, description="Maximum number of events")
):
    """
    Get event history
    """
    logger.info(f"History request: event_type={event_type}, days={days}, limit={limit}")

    try:
        with get_db() as conn:
            cursor = conn.cursor()

            cutoff_date = datetime.now() - timedelta(days=days)

            if event_type:
                if event_type not in ["pee", "poo"]:
                    logger.error(f"Invalid event_type in history request: {event_type}")
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

        logger.info(f"History retrieved: {len(events)} events")
        return {"events": events, "count": len(events)}
    except Exception as e:
        logger.error(f"Error retrieving history: {e}", exc_info=True)
        raise


@app.get("/api/v1/analytics")
async def get_analytics(days: int = Query(7, description="Number of days for analytics")):
    """
    Get analytics including averages, counts, and trends
    """
    logger.info(f"Analytics request for {days} days")

    try:
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

        logger.info(f"Analytics generated: pee={counts.get('pee', 0)} events, poo={counts.get('poo', 0)} events")

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
    except Exception as e:
        logger.error(f"Error generating analytics: {e}", exc_info=True)
        raise


@app.post("/api/v1/accidents")
async def log_accident(accident: AccidentCreate):
    """
    Log an accident with estimated time and location
    """
    logger.info(f"Received accident logging request: type={accident.event_type}, location={accident.location}")

    if accident.event_type not in ["pee", "poo"]:
        logger.error(f"Invalid event_type in accident: {accident.event_type}")
        raise HTTPException(status_code=400, detail="event_type must be 'pee' or 'poo'")

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO accidents (event_type, estimated_time, location, notes)
                VALUES (?, ?, ?, ?)
            """, (accident.event_type, accident.estimated_time.isoformat(),
                  accident.location, accident.notes))
            conn.commit()
            accident_id = cursor.lastrowid

        logger.info(f"Accident logged: ID={accident_id}, type={accident.event_type}, location={accident.location}")

        return {
            "success": True,
            "accident_id": accident_id
        }
    except Exception as e:
        logger.error(f"Error logging accident: {e}", exc_info=True)
        raise


@app.get("/api/v1/accidents")
async def get_accidents(days: int = Query(7, description="Number of days to retrieve")):
    """
    Get accident history
    """
    logger.info(f"Accident history request for {days} days")

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cutoff_date = datetime.now() - timedelta(days=days)

            cursor.execute("""
                SELECT * FROM accidents
                WHERE estimated_time >= ?
                ORDER BY estimated_time DESC
            """, (cutoff_date.isoformat(),))

            accidents = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Accident history retrieved: {len(accidents)} accidents")
        return {"accidents": accidents, "count": len(accidents)}
    except Exception as e:
        logger.error(f"Error retrieving accident history: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
