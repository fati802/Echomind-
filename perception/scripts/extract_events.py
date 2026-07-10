"""Run the fine-tuned YOLO model over each scene's frames, cross-check detections
against the manually authored zone_timeline, collapse repeated frame hits into
discrete events, and POST them to the backend's /api/ingest endpoint.

Usage:
    python scripts/extract_events.py            # dry run, prints events only
    python scripts/extract_events.py --ingest    # also POSTs to the backend
"""
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
from ultralytics import YOLO

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zone_timeline import TIMELINE

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "echomind_yolo_r3" / "weights" / "best.pt"
FRAMES_DIR = ROOT / "data" / "frames"
CONF_THRESHOLD = 0.5
MIN_CONSECUTIVE_HITS = 2  # require 2+ consecutive matching frames to confirm an event
INGEST_URL = "http://localhost:8000/api/ingest"

# Base "demo day" timestamp events are anchored to (scene start times offset from here)
DEMO_BASE_TIME = datetime(2026, 7, 10, 9, 0, 0)
SCENE_START_OFFSETS = {
    "scene1_placement": timedelta(minutes=0),
    "scene2_pickup_move": timedelta(minutes=5),
    "scene3_handoff": timedelta(minutes=12),
    "scene4_filler": timedelta(minutes=20),
}


def parse_frame_timestamp(frame_name: str) -> float:
    # e.g. scene1_placement_f0015_t7.59s.jpg -> 7.59
    part = frame_name.split("_t")[-1]
    return float(part.replace("s.jpg", ""))


def find_timeline_entry(scene_name: str, t: float):
    for entry in TIMELINE.get(scene_name, []):
        if entry["start"] <= t < entry["end"]:
            return entry
    return None


def run_detection(model, frame_path: Path):
    results = model.predict(str(frame_path), conf=CONF_THRESHOLD, verbose=False)
    detected = set()
    confidences = {}
    for r in results:
        for box in r.boxes:
            cls_name = model.names[int(box.cls)]
            conf = float(box.conf)
            detected.add(cls_name)
            confidences[cls_name] = max(confidences.get(cls_name, 0), conf)
    return detected, confidences


def extract_scene_events(model, scene_name: str):
    scene_dir = FRAMES_DIR / scene_name
    if not scene_dir.exists():
        print(f"Skipping missing scene: {scene_name}")
        return []

    frames = sorted(scene_dir.glob("*.jpg"), key=lambda p: parse_frame_timestamp(p.name))

    # For each frame, check if detection matches what the timeline says should be there
    frame_hits = []  # list of (t, entry, confidence, frame_name)
    for frame_path in frames:
        t = parse_frame_timestamp(frame_path.name)
        entry = find_timeline_entry(scene_name, t)
        if entry is None:
            continue
        detected, confidences = run_detection(model, frame_path)
        if entry["object"] in detected:
            frame_hits.append((t, entry, confidences[entry["object"]], frame_path.name))

    # Collapse consecutive hits for the same timeline entry into one discrete event
    events = []
    i = 0
    while i < len(frame_hits):
        t, entry, conf, fname = frame_hits[i]
        run = [(t, conf, fname)]
        j = i + 1
        while j < len(frame_hits) and frame_hits[j][1] is entry:
            run.append((frame_hits[j][0], frame_hits[j][2], frame_hits[j][3]))
            j += 1

        if len(run) >= MIN_CONSECUTIVE_HITS:
            avg_conf = sum(c for _, c, _ in run) / len(run)
            last_t, _, last_fname = run[-1]
            event_time = DEMO_BASE_TIME + SCENE_START_OFFSETS[scene_name] + timedelta(seconds=last_t)
            events.append({
                "object": entry["object"],
                "action": entry["action"],
                "actor": entry["actor"],
                "zone": entry["zone"],
                "timestamp": event_time.isoformat(),
                "confidence": round(avg_conf, 3),
                "source_frame": f"{scene_name}/{last_fname}",
            })
        i = j

    return events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest", action="store_true", help="POST events to the backend")
    args = parser.parse_args()

    model = YOLO(str(MODEL_PATH))

    all_events = []
    for scene_name in TIMELINE.keys():
        events = extract_scene_events(model, scene_name)
        print(f"\n{scene_name}: {len(events)} event(s)")
        for e in events:
            print(f"  {e['timestamp']}  {e['actor']:<10} {e['action']:<12} {e['object']:<14} @ {e['zone']}  (conf={e['confidence']})")
        all_events.extend(events)

    print(f"\nTotal events extracted: {len(all_events)}")

    if args.ingest:
        print(f"\nPosting to {INGEST_URL} ...")
        success, failed = 0, 0
        for e in all_events:
            try:
                resp = requests.post(INGEST_URL, json=e, timeout=5)
                resp.raise_for_status()
                success += 1
            except Exception as ex:
                failed += 1
                print(f"  FAILED: {e['object']} @ {e['timestamp']} -- {ex}")
        print(f"Ingested: {success} succeeded, {failed} failed")
    else:
        print("\nDry run only (no --ingest flag). Nothing was sent to the backend.")


if __name__ == "__main__":
    main()
