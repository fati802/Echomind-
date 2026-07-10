"""Re-ingest the pre-extracted events from data/extracted_events.json into a
running backend (POST /api/ingest for each). Use this if you don't want to
re-run the YOLO model yourself -- just replay Person A's already-extracted,
verified events into your own local database.

Usage:
    python scripts/ingest_saved_events.py
"""
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
EVENTS_FILE = ROOT / "data" / "extracted_events.json"
INGEST_URL = "http://localhost:8000/api/ingest"


def main():
    events = json.loads(EVENTS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(events)} events from {EVENTS_FILE}")

    success, failed = 0, 0
    for e in events:
        payload = {k: v for k, v in e.items() if k != "id"}
        try:
            resp = requests.post(INGEST_URL, json=payload, timeout=5)
            resp.raise_for_status()
            success += 1
        except Exception as ex:
            failed += 1
            print(f"  FAILED: {e['object']} @ {e['timestamp']} -- {ex}")

    print(f"Ingested: {success} succeeded, {failed} failed")


if __name__ == "__main__":
    main()
