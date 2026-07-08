import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from backend.database import SessionLocal, init_db
from backend.models.event import Event

def seed_events(reset: bool = True):
    # Initialize the database (creates tables if they don't exist)
    init_db()
    
    db = SessionLocal()
    try:
        if reset:
            print("Resetting events table...")
            db.query(Event).delete()
            db.commit()
            
        print("Seeding new events...")
        
        # Base date: today (July 8, 2026)
        today = datetime.now().date()
        base_dt = datetime(today.year, today.month, today.day)
        
        # 19 realistic, synthetic events matching requirements
        events_data = [
            # Morning (06:00 - 12:00)
            {
                "object": "glasses",
                "action": "placed",
                "actor": "patient",
                "zone": "kitchen shelf",
                "timestamp": base_dt + timedelta(hours=8, minutes=15), # 08:15 AM
                "confidence": 0.95
            },
            {
                "object": "medicine box",
                "action": "placed",
                "actor": "caregiver",
                "zone": "kitchen shelf",
                "timestamp": base_dt + timedelta(hours=8, minutes=30), # 08:30 AM
                "confidence": 0.98
            },
            {
                "object": "mug",
                "action": "placed",
                "actor": "patient",
                "zone": "dining table",
                "timestamp": base_dt + timedelta(hours=8, minutes=45), # 08:45 AM
                "confidence": 0.90
            },
            {
                "object": "keys",
                "action": "placed",
                "actor": "patient",
                "zone": "hallway table",
                "timestamp": base_dt + timedelta(hours=9, minutes=15), # 09:15 AM
                "confidence": 0.88
            },
            {
                "object": "remote",
                "action": "placed",
                "actor": "patient",
                "zone": "study table",
                "timestamp": base_dt + timedelta(hours=9, minutes=45), # 09:45 AM
                "confidence": 0.92
            },
            {
                "object": "medicine box",
                "action": "handed_over",
                "actor": "caregiver",
                "zone": "living room",
                "timestamp": base_dt + timedelta(hours=10, minutes=30), # 10:30 AM
                "confidence": 0.97
            },
            {
                "object": "remote",
                "action": "picked_up",
                "actor": "patient",
                "zone": "study table",
                "timestamp": base_dt + timedelta(hours=11, minutes=0), # 11:00 AM
                "confidence": 0.65  # Hedging test (confidence 0.5-0.7)
            },
            
            # Afternoon (12:00 - 17:00)
            {
                "object": "glasses",
                "action": "picked_up",
                "actor": "patient",
                "zone": "kitchen shelf",
                "timestamp": base_dt + timedelta(hours=12, minutes=15), # 12:15 PM
                "confidence": 0.93
            },
            {
                "object": "mug",
                "action": "picked_up",
                "actor": "patient",
                "zone": "dining table",
                "timestamp": base_dt + timedelta(hours=13, minutes=30), # 01:30 PM
                "confidence": 0.89
            },
            {
                "object": "medicine box",
                "action": "handed_over",
                "actor": "caregiver",
                "zone": "kitchen",
                "timestamp": base_dt + timedelta(hours=14, minutes=15), # 02:15 PM
                "confidence": 0.95
            },
            {
                "object": "remote",
                "action": "placed",
                "actor": "patient",
                "zone": "couch",
                "timestamp": base_dt + timedelta(hours=15, minutes=15), # 03:15 PM
                "confidence": 0.60  # Hedging test (confidence 0.5-0.7)
            },
            {
                "object": "glasses",
                "action": "placed",
                "actor": "patient",
                "zone": "dining table",
                "timestamp": base_dt + timedelta(hours=16, minutes=30), # 04:30 PM
                "confidence": 0.91
            },
            
            # Evening (17:00 - 21:00)
            {
                "object": "keys",
                "action": "picked_up",
                "actor": "patient",
                "zone": "hallway table",
                "timestamp": base_dt + timedelta(hours=17, minutes=45), # 05:45 PM
                "confidence": 0.94
            },
            {
                "object": "mug",
                "action": "placed",
                "actor": "patient",
                "zone": "kitchen sink",
                "timestamp": base_dt + timedelta(hours=18, minutes=30), # 06:30 PM
                "confidence": 0.87
            },
            {
                "object": "glasses",
                "action": "picked_up",
                "actor": "caregiver",
                "zone": "dining table",
                "timestamp": base_dt + timedelta(hours=19, minutes=15), # 07:15 PM
                "confidence": 0.55  # Hedging test (confidence 0.5-0.7)
            },
            {
                "object": "remote",
                "action": "picked_up",
                "actor": "patient",
                "zone": "couch",
                "timestamp": base_dt + timedelta(hours=20, minutes=0), # 08:00 PM
                "confidence": 0.90
            },
            
            # Night (21:00 - 06:00 next day)
            {
                "object": "glasses",
                "action": "placed",
                "actor": "patient",
                "zone": "bedside table",
                "timestamp": base_dt + timedelta(hours=21, minutes=30), # 09:30 PM
                "confidence": 0.96
            },
            {
                "object": "medicine box",
                "action": "observed",
                "actor": None,  # Unidentified actor to test None/null fallback
                "zone": "kitchen shelf",
                "timestamp": base_dt + timedelta(hours=22, minutes=15), # 10:15 PM
                "confidence": 0.92
            },
            {
                "object": "keys",
                "action": "placed",
                "actor": "patient",
                "zone": "bedside table",
                "timestamp": base_dt + timedelta(hours=23, minutes=0), # 11:00 PM
                "confidence": 0.86
            }
        ]
        
        for event_dict in events_data:
            event = Event(**event_dict)
            db.add(event)
            
        db.commit()
        print(f"Successfully seeded {len(events_data)} events!")
        
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed EchoMind events database with synthetic demo data.")
    parser.add_argument("--no-reset", action="store_true", help="Do not clear existing events table before seeding.")
    args = parser.parse_args()
    
    seed_events(reset=not args.no_reset)
