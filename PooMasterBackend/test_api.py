"""
Test script to populate the database with sample data
Run this after starting the server to test the system
"""
import requests
from datetime import datetime, timedelta
import random
import time

BASE_URL = "http://localhost:8000"

def log_event(event_type, timestamp=None):
    """Log a bathroom event"""
    data = {"event_type": event_type}
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    response = requests.post(f"{BASE_URL}/api/events", json=data)
    return response.json()

def log_accident(event_type, estimated_time, location, notes):
    """Log an accident"""
    data = {
        "event_type": event_type,
        "estimated_time": estimated_time.isoformat(),
        "location": location,
        "notes": notes
    }
    response = requests.post(f"{BASE_URL}/api/accidents", json=data)
    return response.json()

def get_status():
    """Get current status"""
    response = requests.get(f"{BASE_URL}/api/status")
    return response.json()

def get_analytics(days=7):
    """Get analytics"""
    response = requests.get(f"{BASE_URL}/api/analytics", params={"days": days})
    return response.json()

def populate_sample_data():
    """Populate the database with realistic sample data"""
    print("Populating database with sample data...")
    print("-" * 50)
    
    # Generate events for the last 7 days
    now = datetime.now()
    
    # Pee events - roughly every 4 hours
    current_time = now - timedelta(days=7)
    pee_count = 0
    while current_time < now:
        # Add some randomness (3-5 hours between pees)
        interval = random.uniform(3.0, 5.0)
        current_time += timedelta(hours=interval)
        if current_time < now:
            result = log_event("pee", current_time)
            pee_count += 1
            print(f"✓ Logged pee event at {current_time.strftime('%Y-%m-%d %H:%M')}")
            time.sleep(0.1)  # Small delay to avoid overwhelming the server
    
    print(f"\nTotal pee events: {pee_count}")
    print("-" * 50)
    
    # Poo events - roughly every 12 hours
    current_time = now - timedelta(days=7)
    poo_count = 0
    while current_time < now:
        # Add some randomness (10-14 hours between poos)
        interval = random.uniform(10.0, 14.0)
        current_time += timedelta(hours=interval)
        if current_time < now:
            result = log_event("poo", current_time)
            poo_count += 1
            print(f"✓ Logged poo event at {current_time.strftime('%Y-%m-%d %H:%M')}")
            time.sleep(0.1)
    
    print(f"\nTotal poo events: {poo_count}")
    print("-" * 50)
    
    # Add a couple of accidents
    accident_time1 = now - timedelta(days=3, hours=2)
    log_accident("pee", accident_time1, "Living room carpet", "Found wet spot near the couch")
    print(f"✓ Logged accident at {accident_time1.strftime('%Y-%m-%d %H:%M')}")
    
    accident_time2 = now - timedelta(days=1, hours=8)
    log_accident("pee", accident_time2, "Kitchen floor", "Slipped out during dinner prep")
    print(f"✓ Logged accident at {accident_time2.strftime('%Y-%m-%d %H:%M')}")
    
    print("\n" + "=" * 50)
    print("Sample data loaded successfully!")
    print("=" * 50)

def display_current_status():
    """Display the current system status"""
    print("\n" + "=" * 50)
    print("CURRENT STATUS")
    print("=" * 50)
    
    status = get_status()
    
    print(f"\nPEE Status:")
    print(f"  LED Color: RGB({status['pee']['r']}, {status['pee']['g']}, {status['pee']['b']})")
    print(f"  Time Since Last: {status['pee_time_since']:.1f} hours")
    print(f"  Percentage: {status['pee_percentage']:.1f}%")
    print(f"  Alarm: {'🔴 YES' if status['pee_alarm'] else '✓ No'}")
    
    print(f"\nPOO Status:")
    print(f"  LED Color: RGB({status['poo']['r']}, {status['poo']['g']}, {status['poo']['b']})")
    print(f"  Time Since Last: {status['poo_time_since']:.1f} hours")
    print(f"  Percentage: {status['poo_percentage']:.1f}%")
    print(f"  Alarm: {'🔴 YES' if status['poo_alarm'] else '✓ No'}")

def display_analytics():
    """Display analytics"""
    print("\n" + "=" * 50)
    print("ANALYTICS (Last 7 Days)")
    print("=" * 50)
    
    analytics = get_analytics(7)
    
    print(f"\nPEE:")
    print(f"  Total Events: {analytics['pee']['count']}")
    print(f"  Average Interval: {analytics['pee']['average_interval_hours']:.1f} hours")
    print(f"  Accidents: {analytics['pee']['accidents']}")
    
    print(f"\nPOO:")
    print(f"  Total Events: {analytics['poo']['count']}")
    print(f"  Average Interval: {analytics['poo']['average_interval_hours']:.1f} hours")
    print(f"  Accidents: {analytics['poo']['accidents']}")

def test_new_event():
    """Test logging a new event"""
    print("\n" + "=" * 50)
    print("TESTING NEW EVENT")
    print("=" * 50)
    
    print("\nLogging a new pee event...")
    result = log_event("pee")
    print(f"✓ Event logged with ID: {result['event_id']}")
    print(f"  Timestamp: {result['timestamp']}")
    
    time.sleep(1)
    
    print("\nUpdated status:")
    status = get_status()
    print(f"  Pee time since last: {status['pee_time_since']:.1f} hours")
    print(f"  Pee percentage: {status['pee_percentage']:.1f}%")

if __name__ == "__main__":
    print("=" * 50)
    print("PUPPY BATHROOM TRACKER - TEST SCRIPT")
    print("=" * 50)
    print("\nMake sure the server is running at http://localhost:8000")
    print("\nOptions:")
    print("1. Populate database with sample data")
    print("2. Display current status")
    print("3. Display analytics")
    print("4. Test logging a new event")
    print("5. Run all tests")
    print("0. Exit")
    
    while True:
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "1":
            populate_sample_data()
        elif choice == "2":
            display_current_status()
        elif choice == "3":
            display_analytics()
        elif choice == "4":
            test_new_event()
        elif choice == "5":
            populate_sample_data()
            display_current_status()
            display_analytics()
        elif choice == "0":
            print("\nExiting...")
            break
        else:
            print("Invalid choice. Please enter 0-5.")
